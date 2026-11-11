"""T032: conocimiento conectado al motor con activación explícita offline."""

from contextlib import contextmanager
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from datos.offline import ClienteOffline
from modelo.conocimiento import AVISTADA, DESCONOCIDA, EXPLORADA
from modelo.errores_historia import CambioHistoriaIncoherente
from modelo.juego import crear_juego
from modelo.tipos import ObjetoInstancia
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import crear_paquete


@contextmanager
def partida_lineal(*, habilitada=True, con_trampa=False):
    with TemporaryDirectory(prefix="cripta-t032-") as carpeta:
        almacen = crear_paquete(carpeta, salas=3)
        almacen.guardar_ficha("cat1", {"id": "pergamino", "clase": "pergamino_retroceso",
                                       "nombre": "Pergamino"})
        if con_trampa:
            almacen.guardar_ficha("cat1", {"id": "trampa-t032", "clase": "trampa",
                                           "nombre": "Trampa", "daño": 1})
            contenido = almacen.leer_contenido("prueba", "v1", 101)
            contenido["trampas"] = [{"instancia": "t-101", "tipo": "trampa-t032"}]
            almacen.guardar_contenido("prueba", "v1", contenido)
        cliente = ClienteOffline(carpeta, "v1")
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(), cliente.almacen)
        precarga = GestorPrecarga(cliente, catalogo)
        with patch("requests.sessions.Session.request",
                   side_effect=AssertionError("HTTP durante T032")) as http:
            try:
                motor = crear_juego(precarga, "prueba", semilla=42,
                                    version_cripta="v1", version_catalogo="cat1",
                                    **({"conocimiento_para_pruebas": True} if habilitada else {}))
                yield motor, motor._conocimiento, precarga
            finally:
                try:
                    precarga.cerrar()
                finally:
                    cliente.cerrar()
            http.assert_not_called()
            if cliente.solicitudes_realizadas != 0:
                raise AssertionError("El cliente offline registró solicitudes HTTP")


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
            self.assertEqual(motor.mapa_conocido(), inicial)
            revision = mapa.revision
            self.assertEqual(precarga.cargar_contenido([102])[0]["sala"], 102)
            self.assertFalse(motor.contenido_cargado[102])
            self.assertEqual(motor.mapa_conocido(), inicial)
            self.assertEqual(mapa.revision, revision)

    def test_entrada_fisica_explora_destino_y_avista_vecina(self):
        with partida_lineal(con_trampa=True) as (motor, mapa, _):
            activar_enemigos = motor.activar_enemigos_de_sala
            activar_trampa = motor.efectos.activar_trampa
            observaciones = []

            def comprobar_entrada(etapa):
                self.assertEqual(motor.jugador.posicion_actual, 101)
                self.assertEqual(mapa.estado_sala(101), EXPLORADA)
                self.assertEqual(mapa.estado_sala(102), AVISTADA)
                observaciones.append(etapa)

            def observar_enemigos(sala_id, enemigos):
                self.assertEqual(sala_id, 101)
                comprobar_entrada("enemigos")
                return activar_enemigos(sala_id, enemigos)

            def observar_trampa(trampa):
                self.assertEqual(trampa.id_instancia, "t-101")
                comprobar_entrada("trampa")
                return activar_trampa(trampa)

            with patch.object(motor, "activar_enemigos_de_sala", side_effect=observar_enemigos), \
                    patch.object(motor.efectos, "activar_trampa", side_effect=observar_trampa):
                self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(observaciones, ["enemigos", "trampa"])
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (101, 100))
            self.assertEqual(motor.mapa_conocido()[1:], (
                (101, EXPLORADA, motor.salas[101].nombre,
                 (("E", 102, 100, None, False), ("O", 100, 100, None, False))),
                (102, AVISTADA, None, ()),
            ))

    def test_movimiento_rechazado_no_registra_entrada(self):
        with partida_lineal() as (motor, mapa, _):
            previo = mapa.mapa_conocido(), mapa.revision
            with patch.object(mapa, "entrar", wraps=mapa.entrar) as entrar:
                self.assertFalse(motor.ejecutar("mover", "O").ok)
            entrar.assert_not_called()
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (100, 0))
            self.assertEqual((mapa.mapa_conocido(), mapa.revision), previo)

    def test_revisitar_no_genera_cambios_redundantes(self):
        with partida_lineal() as (motor, mapa, _):
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            previo = mapa.mapa_conocido(), mapa.revision
            with patch.object(mapa, "entrar", wraps=mapa.entrar) as entrar:
                self.assertTrue(motor.ejecutar("mover", "O").ok)
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (100, 200))
            entrar.assert_called_once_with(100)
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

            with patch.object(mapa, "revertir", wraps=mapa.revertir) as revertir:
                with self.assertRaisesRegex(CambioHistoriaIncoherente, "después de la entrada"):
                    motor.ejecutar("mover", "E", registrar_h3=rechazar)
            revertir.assert_called_once()
            self.assertEqual(mapa.mapa_conocido(), previo)
            self.assertEqual(motor.exportar_estado(), estado)
            self.assertEqual(eventos_vigentes(motor), agenda)
            self.assertEqual(motor.cola.proxima_secuencia(), secuencia)
            self.assertEqual(motor.azar.getstate(), rng)
            self.assertEqual(motor.historial.cantidad_turnos(), 0)
            self.assertEqual(mensajes, [])

    def test_pergamino_revierte_solo_el_ultimo_turno_y_consume_el_objeto(self):
        with partida_lineal() as (motor, mapa, _):
            inventario = motor.jugador.inventario
            self.assertIsNotNone(inventario.recoger(
                ObjetoInstancia("p-t032", "pergamino", "inventario")))
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            previo = motor.mapa_conocido()
            estado = motor.exportar_estado()
            agenda = eventos_vigentes(motor)
            self.assertEqual(mapa.estado_sala(101), EXPLORADA)
            self.assertEqual(mapa.estado_sala(102), AVISTADA)

            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (102, 200))
            self.assertEqual(mapa.estado_sala(102), EXPLORADA)
            self.assertNotEqual(motor.azar.getstate(), estado.rng_estado)

            with patch.object(mapa, "revertir", wraps=mapa.revertir) as revertir:
                self.assertTrue(motor.ejecutar("retroceso").ok)
            revertir.assert_called_once()
            self.assertEqual(motor.mapa_conocido(), previo)
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (101, 100))
            self.assertEqual(eventos_vigentes(motor), agenda)
            self.assertEqual(motor.cola.proxima_secuencia(), estado.siguiente_secuencia)
            self.assertEqual(motor.azar.getstate(), estado.rng_estado)
            self.assertEqual(motor.jugador.vida, estado.jugador.vida)
            self.assertEqual(motor.acciones_jugador, 1)
            self.assertEqual(motor.historial.cantidad_turnos(), 1)
            self.assertEqual(inventario.contar("pergamino"), 0)

    def test_partida_normal_no_expone_mapa_y_conserva_el_movimiento(self):
        with partida_lineal(habilitada=False) as (motor, mapa, _):
            self.assertIsNone(mapa)
            self.assertIsNone(getattr(motor, "mapa_conocido", None))
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (101, 100))
            self.assertIsNone(getattr(motor, "mapa_conocido", None))
