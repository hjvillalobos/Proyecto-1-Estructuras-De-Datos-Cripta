import io
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import main
from datos.guardado_binario import guardar_estado, cargar_estado
from modelo.snapshots import EventoGuardado
from red.errores import ErrorRed
from red.precarga import GestorPrecarga, CargaPendiente
from red.sesion import SesionDatos
from tests import test_regresiones_juego as base


class TestCuatroFallosRevision(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor

    def test_abrir_abierta_no_consume_tiempo_ni_duplica_cierre(self):
        m = self.motor
        self.datos._inventario("llave")
        self.datos._inventario("pergamino")
        m.salas[1].salidas["E"]["cierre_automatico"] = 150
        self.assertTrue(m.ejecutar("abrir", "E").ok)
        antes = deepcopy(m.exportar_estado())
        historial = m.historial.cantidad_turnos()
        self.assertFalse(m.ejecutar("abrir", "E").ok)
        self.assertEqual(m.exportar_estado(), antes)
        self.assertEqual(m.historial.cantidad_turnos(), historial)
        self.assertTrue(m.ejecutar("retroceso").ok)
        self.assertTrue(m.salas[1].salidas["E"]["cerrada"])
        self.assertFalse(any(e.tipo == "cierre_puerta" for e in m.cola.pendientes()))

    def test_reapertura_despues_del_cierre_tiene_intervalo_completo(self):
        m = self.motor
        self.datos._inventario("llave")
        m.salas[1].salidas["E"]["cierre_automatico"] = 150
        self.assertTrue(m.ejecutar("abrir", "E").ok)
        self.assertFalse(m.ejecutar("abrir", "E").ok)
        self.assertTrue(m.ejecutar("esperar").ok)
        self.assertEqual(m.reloj, 150)
        self.assertTrue(m.salas[1].salidas["E"]["cerrada"])
        self.assertTrue(m.ejecutar("abrir", "E").ok)
        self.assertEqual(m.reloj, 200)
        self.assertFalse(m.salas[1].salidas["E"]["cerrada"])
        self.assertEqual([e.tiempo for e in m.cola.pendientes() if e.tipo == "cierre_puerta"], [300])
        estado = m.exportar_estado()
        m.restaurar_estado(estado)
        self.assertTrue(m.ejecutar("esperar").ok)
        self.assertTrue(m.salas[1].salidas["E"]["cerrada"])

    def test_salida_inicialmente_abierta_aun_exige_apertura_con_llave(self):
        m = self.motor
        m.salas[1].salidas["E"]["cerrada"] = False
        self.assertFalse(m.ejecutar("abrir", "E").ok)
        self.datos._inventario("llave")
        self.assertTrue(m.ejecutar("abrir", "E").ok)
        self.assertFalse(m.ejecutar("abrir", "E").ok)
        self.assertTrue(m.ejecutar("mover", "E").ok)
        self.assertEqual(m.resultado, "victoria")

    def test_guardado_binario_con_turnos_duplicados_se_rechaza_sin_mutar(self):
        self.datos._enemigo()
        for tipo, objetivo in (("turno_enemigo", "enemigo-1"), ("turno_jugador", "jugador")):
            with self.subTest(tipo=tipo), tempfile.TemporaryDirectory() as carpeta:
                antes = deepcopy(self.motor.exportar_estado())
                estado = deepcopy(antes)
                for _ in range(2):
                    estado.eventos.append(EventoGuardado(100, estado.siguiente_secuencia, tipo, objetivo))
                    estado.siguiente_secuencia += 1
                ruta = str(Path(carpeta) / "inconsistente.bin")
                guardar_estado(estado, ruta)
                with self.assertRaisesRegex(ValueError, "turno de actor"):
                    self.motor.restaurar_estado(cargar_estado(ruta))
                self.assertEqual(self.motor.exportar_estado(), antes)

    def test_cierres_duplicados_en_carga_se_rechazan(self):
        estado = self.motor.exportar_estado()
        for _ in range(2):
            estado.eventos.append(EventoGuardado(150, estado.siguiente_secuencia, "cierre_puerta", "1:E"))
            estado.siguiente_secuencia += 1
        with self.assertRaisesRegex(ValueError, "cierre de puerta duplicado"):
            self.motor.restaurar_estado(estado)

    def test_tipo_de_turno_debe_corresponder_al_actor(self):
        estado = self.motor.exportar_estado()
        estado.eventos.append(EventoGuardado(100, estado.siguiente_secuencia, "turno_enemigo", "jugador"))
        estado.siguiente_secuencia += 1
        with self.assertRaisesRegex(ValueError, "turno de actor"):
            self.motor.restaurar_estado(estado)

    def test_versiones_cli_llegan_a_partida_normal(self):
        for gui in (False, True):
            with self.subTest(gui=gui):
                sesion = Mock()
                vista = Mock()
                vista.mostrar_menu.return_value = ("jugar", None)
                args = ["--cripta", "prueba", "--version-cripta", "v1",
                        "--version-catalogo", "cat1", "--semilla", "42"]
                with patch("main.SesionDatos", return_value=sesion), \
                        patch("vista.consola.VistaConsola", return_value=vista), \
                        patch("vista.grafica.VistaGrafica", return_value=vista), \
                        patch("modelo.juego.crear_juego", return_value=Mock(resultado=None)) as crear, \
                        patch("controlador.controlador.ControladorJuego"):
                    self.assertEqual(main.main(args + (["--gui"] if gui else [])), 0)
                crear.assert_called_once_with(sesion.precarga, "prueba", 42,
                                              version_cripta="v1", version_catalogo="cat1")

    def test_error_de_precarga_en_cierre_reportado_sin_excepcion(self):
        sesion = SesionDatos(SimpleNamespace(datos_dir=".cache/cripta"))
        sesion.cliente = Mock()
        sesion.cliente.listar_criptas.return_value = {"criptas": []}
        sesion.almacen, sesion.catalogo = Mock(), Mock()
        sesion.catalogo.reporte.return_value = {"solicitudes_realizadas": 3}
        sesion.precarga = GestorPrecarga(sesion.cliente, sesion.catalogo)
        pendiente = CargaPendiente([1])
        pendiente.hilo = Mock()
        pendiente.error = ErrorRed("precarga pendiente fallida")
        sesion.precarga.pendiente = pendiente
        error = io.StringIO()
        with patch("main.SesionDatos", return_value=sesion), patch.object(sesion, "abrir"), \
                redirect_stdout(io.StringIO()), redirect_stderr(error):
            self.assertEqual(main.main(["--listar"]), 0)
        self.assertIn("precarga pendiente fallida", error.getvalue())
        pendiente.hilo.join.assert_called_once()
        sesion.cliente.cerrar.assert_called_once()

    def test_fallo_de_cierre_no_oculta_error_original(self):
        sesion = Mock()
        sesion.abrir.side_effect = ErrorRed("fallo inicial")
        sesion.cerrar.side_effect = OSError("fallo al cerrar")
        error = io.StringIO()
        with patch("main.SesionDatos", return_value=sesion), redirect_stderr(error):
            self.assertEqual(main.main(["--listar"]), 1)
        self.assertIn("fallo inicial", error.getvalue())
        self.assertIn("fallo al cerrar", error.getvalue())
