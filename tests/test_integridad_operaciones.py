import json
import unittest
import tempfile
from copy import deepcopy
from unittest.mock import Mock, mock_open, patch

from controlador.controlador import ControladorJuego
from datos.puntajes import TablaPuntajes
from modelo.snapshots import EventoGuardado, ItemInventarioGuardado
from red.errores import ErrorRed, DatosInvalidos
from tests import test_regresiones_juego as base


class TestIntegridadOperaciones(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor

    def test_precarga_fallida_no_rompe_movimiento_ni_replay(self):
        m = self.motor
        m.sala_salida = None
        m.salas[1].salidas["E"]["cerrada"] = False
        m.gestor_precarga.anticipar = Mock(side_effect=ErrorRed("fallo anticipado"))
        c = ControladorJuego(m, Mock())
        c.bitacora_replay = Mock()
        self.assertTrue(c._accion_modelo("mover", "E"))
        self.assertEqual((m.jugador.posicion_actual, m.reloj, m.acciones_jugador), (2, 100, 1))
        self.assertEqual(m.historial.cantidad_turnos(), 1)
        c.bitacora_replay.registrar_accion.assert_called_once_with("mover", "E")
        self.datos._inventario("pergamino")
        self.assertTrue(m.ejecutar("retroceso").ok)
        self.assertEqual((m.jugador.posicion_actual, m.reloj), (1, 0))

    def test_cargas_invalidas_conservan_partida_e_historial(self):
        m = self.motor
        m.ejecutar("esperar")
        antes = deepcopy(m.exportar_estado())
        rng = deepcopy(antes)
        rng.reloj = 987
        rng.rng_estado = (999, (), None)
        evento = deepcopy(antes)
        evento.eventos.append(EventoGuardado(150, 100, "fin_veneno", "jugador", []))
        objetivo = deepcopy(antes)
        objetivo.eventos.append(EventoGuardado(150, 0, "rearmar_trampa", "inexistente", []))
        velocidad = deepcopy(antes)
        velocidad.jugador.velocidad = 0
        for estado in (rng, evento, objetivo, velocidad):
            with self.subTest(estado=estado), self.assertRaises(ValueError):
                m.restaurar_estado(estado)
            self.assertEqual(m.exportar_estado(), antes)
            self.assertEqual(m.historial.cantidad_turnos(), 1)

    def test_fallo_de_catalogo_durante_carga_no_modifica_partida(self):
        m = self.motor
        m.ejecutar("esperar")
        antes = deepcopy(m.exportar_estado())
        estado = deepcopy(antes)
        estado.jugador.inventario.append(ItemInventarioGuardado("nuevo", "daga", equipado=True))
        with patch.object(m.gestor_precarga.catalogo, "obtener_fichas", side_effect=DatosInvalidos("sin ficha")):
            with self.assertRaises(DatosInvalidos):
                m.restaurar_estado(estado)
        self.assertEqual(m.exportar_estado(), antes)
        self.assertEqual(m.historial.cantidad_turnos(), 1)

    def test_carga_valida_preserva_jugador_y_referencias_de_eventos(self):
        m = self.motor
        self.datos._inventario("velocidad")
        self.assertTrue(m.ejecutar("usar", "velocidad").ok)
        estado = deepcopy(m.exportar_estado())
        jugador = m.jugador
        m.restaurar_estado(estado)
        self.assertIs(m.jugador, jugador)
        self.assertEqual(m.exportar_estado(), estado)
        self.assertIs(m.jugador.evento_velocidad.referencia[0], jugador)
        for _ in range(6):
            m.ejecutar("esperar")
        self.assertEqual(m.jugador.velocidad, 100)

    def test_ranking_descarta_registros_con_tipos_invalidos(self):
        correcto = dict(nombre="Jugador", cripta_id="prueba", cripta_version="v1",
                        acciones=3, derrotados=1, tiempo_final=100, resultado="victoria")
        invalidos = [dict(correcto, tiempo_final="cinco"), dict(correcto, acciones=True),
                     dict(correcto, derrotados=-1), dict(correcto, nombre=[]),
                     dict(correcto, resultado="otro"), dict(correcto, tiempo_final=None)]
        contenido = "\n".join(json.dumps(r) for r in [correcto] + invalidos + [dict(correcto, tiempo_final=50)])
        with patch("os.path.exists", return_value=True), patch("builtins.open", mock_open(read_data=contenido)):
            tabla = TablaPuntajes("ranking.jsonl")
            self.assertEqual([r.tiempo_final for r in tabla.ranking()], [50, 100])

    def test_carga_con_catalogo_real_conserva_cache_y_estado(self):
        from datos.almacen import AlmacenLocal
        from modelo.juego import crear_juego
        from red.cache import CacheCatalogoOrdenado
        from red.catalogo import GestorCatalogo
        from red.precarga import GestorPrecarga
        from tests.datos_prueba import ServidorFalso

        with tempfile.TemporaryDirectory() as carpeta:
            cache = CacheCatalogoOrdenado(25)
            catalogo = GestorCatalogo(ServidorFalso(), cache, AlmacenLocal(carpeta))
            precarga = GestorPrecarga(catalogo.cliente, catalogo)
            try:
                motor = crear_juego(precarga, "prueba", 42)
                estado = deepcopy(motor.exportar_estado())
                motor.restaurar_estado(estado)
                self.assertIs(catalogo.cache, cache)
                self.assertEqual(motor.exportar_estado(), estado)
                referencias = [(n.clave, n.referencias) for n in cache.arreglo]
                invalido = deepcopy(estado)
                invalido.jugador.inventario.append(ItemInventarioGuardado("nuevo", "desconocido", True))
                with patch.object(catalogo, "obtener_fichas", side_effect=DatosInvalidos("sin ficha")):
                    with self.assertRaises(DatosInvalidos):
                        motor.restaurar_estado(invalido)
                self.assertEqual(motor.exportar_estado(), estado)
                self.assertEqual([(n.clave, n.referencias) for n in cache.arreglo], referencias)
            finally:
                precarga.cerrar()
