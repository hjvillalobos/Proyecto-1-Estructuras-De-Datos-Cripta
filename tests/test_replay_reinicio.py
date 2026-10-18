import io
import json
import tempfile
import tkinter as tk
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, mock_open, patch

from datos.bitacora_replay import BitacoraReplay, ReplayCorrupto
from controlador.controlador import ControladorJuego
from controlador.replay import ReproductorReplay
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica


class TestReplayReinicio(unittest.TestCase):
    def test_replay_rechaza_tipos_invalidos(self):
        encabezado = dict(tipo="encabezado", formato=1, cripta_id="x",
                          version_cripta="v1", version_catalogo="v1", semilla=42)
        casos = ["[]", "null", json.dumps(dict(encabezado, semilla="abc")),
                 json.dumps(dict(encabezado, semilla=True)),
                 json.dumps(encabezado) + "\n[]",
                 json.dumps(encabezado) + '\n{"tipo":"accion","accion":"mover","argumento":[]}']
        for contenido in casos:
            with self.subTest(contenido=contenido), patch("pathlib.Path.exists", return_value=True), \
                    patch("pathlib.Path.open", mock_open(read_data=contenido)):
                with self.assertRaises(ReplayCorrupto):
                    BitacoraReplay("prueba.log").leer()

    def test_fallo_de_grabacion_detiene_sesion_sin_mentir_sobre_accion(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        vista = Mock()
        c = ControladorJuego(datos.motor, vista)
        c.bitacora_replay = Mock()
        c.bitacora_replay.registrar_accion.side_effect = OSError("disco lleno")
        self.assertTrue(c._accion_modelo("esperar"))
        self.assertEqual(datos.motor.reloj, 100)
        self.assertFalse(c.ejecutando)
        self.assertFalse(c._grabacion_valida)
        self.assertIn("incompleta", vista.mostrar_error.call_args.args[0])

    def test_fallo_al_iniciar_no_ejecuta_acciones(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        vista = Mock()
        c = ControladorJuego(datos.motor, vista)
        c.bitacora_replay = Mock()
        c.bitacora_replay.iniciar.side_effect = OSError("sin permisos")
        c.iniciar()
        vista.pedir_comando.assert_not_called()
        self.assertFalse(c._grabacion_valida)

    def test_error_de_replay_espera_confirmacion(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista._cerrada, vista.root = False, Mock()
        with patch("vista.grafica.messagebox.showerror") as dialogo, \
                patch("controlador.replay.BitacoraReplay.leer", side_effect=ReplayCorrupto("danado")):
            ReproductorReplay(None, None, vista, Mock()).reproducir("prueba.log")
        dialogo.assert_called_once_with("Error de replay", "danado", parent=vista.root)

    def test_pregunta_de_reinicio_respeta_respuesta(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista._cerrada, vista.root = False, Mock()
        for respuesta in (True, False):
            with patch("vista.grafica.messagebox.askyesno", return_value=respuesta):
                self.assertEqual(vista.preguntar_reinicio(), respuesta)

    def test_reinicio_limpia_la_ventana_real(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.withdraw()
            vista._cola.append("mover N")
            vista._pagina_objetos = 1
            vista._estado = object()
            vista._animaciones.append(vista.root.after(5000, lambda: None))
            vista.reiniciar_presentacion()
            self.assertEqual(vista._cola, [])
            self.assertEqual(vista._animaciones, [])
            self.assertEqual(vista._pagina_objetos, 0)
            self.assertIsNone(vista._estado)
            self.assertEqual(vista.lista.size(), 0)
            self.assertEqual(vista.pedir_comando(), "inv")
        finally:
            vista.cerrar()

    def test_main_reinicia_con_motor_y_precarga_nuevos(self):
        import main
        vista = Mock(spec=VistaGrafica)
        vista.mostrar_menu.return_value = ("jugar", None)
        vista.preguntar_reinicio.return_value = True
        motores = []

        def controlador(**kwargs):
            motor = kwargs["modelo"]
            motores.append(motor)
            self.assertEqual(motor.reloj, 0)
            self.assertEqual(motor.jugador.vida, motor.jugador.vida_max)
            self.assertTrue(motor.jugador.inventario.esta_vacio())
            motor.resultado = "derrota" if len(motores) == 1 else "victoria"
            return Mock()

        with tempfile.TemporaryDirectory() as carpeta, \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("controlador.controlador.ControladorJuego", side_effect=controlador), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(["--gui", "--offline", ".cache/cripta", "--cripta", "cripta-01",
                                        "--datos-dir", carpeta, "--semilla", "42"]), 0)
        self.assertEqual(len(motores), 2)
        self.assertIsNot(motores[0].gestor_precarga, motores[1].gestor_precarga)
        vista.preguntar_reinicio.assert_called_once()
        vista.reiniciar_presentacion.assert_called_once()
        vista.cerrar.assert_called_once()
