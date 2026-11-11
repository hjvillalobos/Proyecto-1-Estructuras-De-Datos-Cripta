"""Preparación de T032: conexión de prueba, sin mapa en el motor normal."""

from contextlib import contextmanager
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from datos.offline import ClienteOffline
from modelo.conocimiento import (
    AVISTADA, DESCONOCIDA, EXPLORADA, CambioConocimiento, ConocimientoMapa,
    SalaConocible, SalidaConocible,
)
from modelo.errores_historia import CambioHistoriaIncoherente
from modelo.juego import crear_juego
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import crear_paquete


@contextmanager
def partida_lineal():
    with TemporaryDirectory(prefix="cripta-t032-") as carpeta:
        crear_paquete(carpeta, salas=3)
        cliente = ClienteOffline(carpeta, "v1")
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(), cliente.almacen)
        precarga = GestorPrecarga(cliente, catalogo)
        with patch("requests.sessions.Session.request",
                   side_effect=AssertionError("HTTP durante T032")) as http:
            try:
                motor = crear_juego(precarga, "prueba", semilla=42,
                                    version_cripta="v1", version_catalogo="cat1")
                salas = []
                for sala_id in (100, 101, 102):
                    sala = motor.salas[sala_id]
                    salidas = []
                    for direccion, salida in sala.salidas.items():
                        # El esqueleto del fixture solo contiene arcos simples.
                        if tuple(salida) != ("sala",):
                            raise AssertionError("Se esperaba una salida sin puerta ni costo declarado")
                        salidas.append(SalidaConocible(direccion, salida["sala"], 100))
                    salas.append(SalaConocible(sala.id, sala.nombre, tuple(salidas)))
                mapa = ConocimientoMapa(salas, (), motor.jugador.posicion_actual)
                yield motor, mapa, precarga
            finally:
                try:
                    precarga.cerrar()
                finally:
                    cliente.cerrar()
            http.assert_not_called()
            if cliente.solicitudes_realizadas != 0:
                raise AssertionError("El cliente offline registró solicitudes HTTP")


@contextmanager
def conectar_entrada_de_prueba(motor, mapa):
    mover_real = motor.mover
    lotes = []

    def mover_y_observar(direccion, trampas_activadas=None):
        origen = motor.jugador.posicion_actual
        resultado = mover_real(direccion, trampas_activadas)
        destino = motor.jugador.posicion_actual
        if resultado[0] and destino != origen:
            cambios = mapa.entrar(destino)
            if cambios:
                motor.historial.registrar_fallo(lambda: mapa.revertir(cambios))
            lotes.append(cambios)
        return resultado

    with patch.object(motor, "mover", side_effect=mover_y_observar):
        yield lotes


def eventos_vigentes(motor):
    return tuple(sorted((e.tiempo, e.secuencia, e.tipo, id(e), e.en_cola)
                        for e in motor.cola.pendientes()))


class PruebasEntradaConocimientoMotor(unittest.TestCase):
    def test_estado_inicial_y_precarga_no_revelan_salas(self):
        with partida_lineal() as (motor, mapa, precarga):
            self.assertEqual((motor.reloj, motor.jugador.posicion_actual), (0, 100))
            self.assertEqual(mapa.estado_sala(102), DESCONOCIDA)
            inicial = (
                (100, EXPLORADA, motor.salas[100].nombre, (("E", 101, 100, None, False),)),
                (101, AVISTADA, None, ()),
            )
            self.assertEqual(mapa.mapa_conocido(), inicial)
            revision = mapa.revision
            self.assertEqual(precarga.cargar_contenido([102])[0]["sala"], 102)
            self.assertFalse(motor.contenido_cargado[102])
            self.assertEqual(mapa.mapa_conocido(), inicial)
            self.assertEqual(mapa.revision, revision)

    def test_entrada_fisica_explora_destino_y_avista_vecina(self):
        with partida_lineal() as (motor, mapa, _):
            mover_original = motor.mover
            with conectar_entrada_de_prueba(motor, mapa) as lotes:
                self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(motor.mover, mover_original)
            self.assertNotIn("mover", vars(motor))
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (101, 100))
            self.assertEqual(lotes, [(
                CambioConocimiento("sala", 101, AVISTADA, EXPLORADA),
                CambioConocimiento("sala", 102, DESCONOCIDA, AVISTADA),
            )])
            self.assertEqual(mapa.mapa_conocido()[1:], (
                (101, EXPLORADA, motor.salas[101].nombre,
                 (("E", 102, 100, None, False), ("O", 100, 100, None, False))),
                (102, AVISTADA, None, ()),
            ))

    def test_movimiento_rechazado_no_registra_entrada(self):
        with partida_lineal() as (motor, mapa, _):
            previo = mapa.mapa_conocido(), mapa.revision
            with conectar_entrada_de_prueba(motor, mapa) as lotes:
                self.assertFalse(motor.ejecutar("mover", "O").ok)
            self.assertEqual(lotes, [])
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (100, 0))
            self.assertEqual((mapa.mapa_conocido(), mapa.revision), previo)

    def test_revisitar_no_genera_cambios_redundantes(self):
        with partida_lineal() as (motor, mapa, _):
            with conectar_entrada_de_prueba(motor, mapa) as lotes:
                self.assertTrue(motor.ejecutar("mover", "E").ok)
                previo = mapa.mapa_conocido(), mapa.revision
                self.assertTrue(motor.ejecutar("mover", "O").ok)
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (100, 200))
            self.assertEqual(len(lotes), 2)
            self.assertTrue(lotes[0])
            self.assertEqual(lotes[1], ())
            self.assertEqual((mapa.mapa_conocido(), mapa.revision), previo)

    def test_rechazo_h3_revierte_conocimiento_y_turno_del_motor(self):
        with partida_lineal() as (motor, mapa, _):
            previo = mapa.mapa_conocido()
            estado = motor.exportar_estado()
            agenda = eventos_vigentes(motor)
            secuencia = motor.cola.proxima_secuencia()
            rng = motor.azar.getstate()
            mensajes = []
            motor.establecer_notificador(mensajes.append)

            def rechazar(inicio, fin, ordinal, cambios, eventos):
                self.assertEqual((inicio, fin, ordinal), (0, 100, 1))
                self.assertEqual(motor.jugador.posicion_actual, 101)
                self.assertEqual(mapa.estado_sala(101), EXPLORADA)
                self.assertEqual(mapa.estado_sala(102), AVISTADA)
                self.assertEqual(cambios[0][0], "sala")
                self.assertTrue(eventos)
                self.assertNotEqual(eventos_vigentes(motor), agenda)
                self.assertGreater(motor.cola.proxima_secuencia(), secuencia)
                self.assertNotEqual(motor.azar.getstate(), rng)
                self.assertEqual(motor.historial.cantidad_turnos(), 0)
                self.assertEqual(mensajes, [])
                raise CambioHistoriaIncoherente("Rechazo H3 de prueba después de la entrada")

            with conectar_entrada_de_prueba(motor, mapa) as lotes:
                with self.assertRaisesRegex(CambioHistoriaIncoherente, "después de la entrada"):
                    motor.ejecutar("mover", "E", registrar_h3=rechazar)
            self.assertEqual(len(lotes), 1)
            self.assertEqual(mapa.mapa_conocido(), previo)
            self.assertEqual(motor.exportar_estado(), estado)
            self.assertEqual(eventos_vigentes(motor), agenda)
            self.assertEqual(motor.cola.proxima_secuencia(), secuencia)
            self.assertEqual(motor.azar.getstate(), rng)
            self.assertEqual(motor.historial.cantidad_turnos(), 0)
            self.assertEqual(mensajes, [])
