import io
import tempfile
import tkinter as tk
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

from controlador.replay import ReproductorReplay
from datos.bitacora_replay import MetaReplay, AccionReplay
from red.errores import ErrorRed
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica


class TestFlujoReplayInicio(unittest.TestCase):
    def test_error_red_en_accion_o_presentacion_detiene_replay(self):
        for metodo in ("ejecutar", "estado_vista", "inventario_vista"):
            datos = base.TestRegresionesJuego()
            datos.setUp()
            vista = Mock()
            vista.mostrar_replay_paso.return_value = True
            with self.subTest(metodo=metodo), \
                    patch("controlador.replay.BitacoraReplay.leer", return_value=(
                        MetaReplay("prueba", "v1", "cat1", 42), [AccionReplay("esperar")])), \
                    patch.object(datos.motor, metodo, side_effect=ErrorRed("conexion perdida")):
                ReproductorReplay(None, None, vista, lambda *a, **k: datos.motor).reproducir("prueba.log")
            vista.mostrar_error.assert_called_once()
            self.assertIn("conexion perdida", vista.mostrar_error.call_args.args[0])
            vista.mostrar_fin.assert_not_called()

    def test_reloj_visible_y_salir_funciona_en_replay_real(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.geometry("1100x760")
            vista.modo_replay()
            vista.root.update()
            self.assertTrue(vista.lbl_tiempo.winfo_ismapped())
            vista._enviar("mover N")
            self.assertEqual(vista._cola, [])
            vista._enviar("salir")
            self.assertTrue(vista._cerrada)
            self.assertTrue(vista._replay_detener)
        finally:
            vista.cerrar()

    def test_inicio_fallido_regresa_menu_y_permite_salir(self):
        import main
        vista = Mock(spec=VistaGrafica)
        vista.mostrar_menu.side_effect = [("jugar", None), ("salir", None)]
        with tempfile.TemporaryDirectory() as carpeta, redirect_stdout(io.StringIO()), \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("modelo.juego.crear_juego", side_effect=ErrorRed("sin datos")):
            resultado = main.main(["--gui", "--offline", ".cache/cripta", "--datos-dir", carpeta,
                                   "--cripta", "cripta-01"])
        self.assertEqual(resultado, 0)
        self.assertEqual(vista.mostrar_menu.call_count, 2)
        vista.mostrar_error_replay.assert_called_once()
        vista.cerrar.assert_called_once()

    def test_reintento_usa_precarga_nueva(self):
        import main
        vista = Mock(spec=VistaGrafica)
        vista.mostrar_menu.side_effect = [("jugar", None), ("jugar", None)]
        datos = base.TestRegresionesJuego()
        datos.setUp()
        controlador = Mock()
        with tempfile.TemporaryDirectory() as carpeta, redirect_stdout(io.StringIO()), \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("modelo.juego.crear_juego", side_effect=[ErrorRed("sin datos"), datos.motor]) as crear, \
                patch("controlador.controlador.ControladorJuego", return_value=controlador):
            resultado = main.main(["--gui", "--offline", ".cache/cripta", "--datos-dir", carpeta,
                                   "--cripta", "cripta-01", "--semilla", "42"])
        self.assertEqual(resultado, 0)
        self.assertIsNot(crear.call_args_list[0].args[0], crear.call_args_list[1].args[0])
        self.assertEqual(crear.call_args_list[1].args[1:], ("cripta-01", 42))
        controlador.iniciar.assert_called_once_with()
