import tempfile
import io
from contextlib import redirect_stdout
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from vista.grafica import VistaGrafica
from vista.menu_inicio import MenuInicio
from tests import test_regresiones_juego as base


class TestMenuInicio(unittest.TestCase):
    def test_salir_del_menu_no_crea_partida(self):
        import main
        vista = Mock(spec=VistaGrafica)
        vista.mostrar_menu.return_value = ("salir", None)
        with tempfile.TemporaryDirectory() as carpeta, redirect_stdout(io.StringIO()), \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("modelo.juego.crear_juego") as crear:
            self.assertEqual(main.main(["--gui", "--offline", ".cache/cripta", "--datos-dir", carpeta]), 0)
        crear.assert_not_called()
        vista.cerrar.assert_called_once()

    def test_cargar_del_menu_usa_versiones_y_semilla_guardadas(self):
        import main
        datos = base.TestRegresionesJuego()
        datos.setUp()
        estado = datos.motor.exportar_estado()
        vista = Mock(spec=VistaGrafica)
        vista.mostrar_menu.return_value = ("cargar", "base.bin")
        controlador = Mock()
        with tempfile.TemporaryDirectory() as carpeta, redirect_stdout(io.StringIO()), \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("datos.guardado_binario.cargar_estado", return_value=estado), \
                patch("modelo.juego.crear_juego", return_value=datos.motor) as crear, \
                patch("controlador.controlador.ControladorJuego", return_value=controlador):
            self.assertEqual(main.main(["--gui", "--offline", ".cache/cripta", "--datos-dir", carpeta]), 0)
        self.assertEqual(crear.call_args.args[1:], ("prueba", 42))
        self.assertEqual(crear.call_args.kwargs, dict(version_cripta="v1", version_catalogo="cat1"))
        controlador.iniciar.assert_called_once_with(estado_inicial=estado)
        vista.elegir_cripta.assert_not_called()

    def test_carga_inicial_conserva_reloj_y_se_registra_en_replay(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        datos.motor.ejecutar("esperar")
        estado = datos.motor.exportar_estado()
        datos.motor.ejecutar("esperar")
        vista = Mock()
        vista.pedir_comando.return_value = None
        with tempfile.TemporaryDirectory() as carpeta:
            c = ControladorJuego(datos.motor, vista, str(Path(carpeta) / "partida.log"))
            c.iniciar(estado_inicial=estado)
            self.assertEqual(datos.motor.reloj, 100)
            self.assertEqual(c.bitacora_replay.leer()[1][0].accion, "cargar")

    def test_menu_real_flechas_enter_y_cancelacion_de_callbacks(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.geometry("1100x760")
            replay, puntajes = Mock(), Mock()
            menu = MenuInicio(vista, replay, puntajes)
            errores = []

            def interactuar():
                try:
                    vista._enviar("mover N")
                    self.assertEqual(vista._cola, [])
                    menu.botones[2].invoke()
                    menu.botones[3].invoke()
                    menu.botones[0].focus_force()
                    vista.root.update()
                    menu.mover(1)
                    vista.root.update()
                    self.assertIs(vista.root.focus_get(), menu.botones[1])
                except Exception as error:
                    errores.append(error)
                finally:
                    menu.activar(menu.botones[0])

            vista.root.after(100, interactuar)
            self.assertEqual(menu.mostrar(), ("jugar", None))
            if errores:
                raise errores[0]
            replay.assert_called_once()
            puntajes.assert_called_once()
            self.assertIsNone(menu.animacion.pendiente)
            self.assertFalse(vista._en_menu)
            self.assertEqual(vista._cola, [])
        finally:
            vista.cerrar()

    def test_cancelar_selector_no_cierra_menu(self):
        menu = MenuInicio.__new__(MenuInicio)
        menu.vista = Mock()
        menu.elegir = Mock()
        with patch("vista.menu_inicio.filedialog.askopenfilename", return_value=""):
            menu.cargar()
        menu.elegir.assert_not_called()
        with patch("vista.menu_inicio.filedialog.askopenfilename", return_value="partida.bin"):
            menu.cargar()
        menu.elegir.assert_called_once_with("cargar", "partida.bin")
