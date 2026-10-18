import unittest
import wave
import random
from array import array
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica
from vista.sonidos import Sonidos


class TestSonidos(unittest.TestCase):
    def crear(self):
        reproductor = SimpleNamespace(PlaySound=Mock(), SND_FILENAME=1, SND_ASYNC=2, SND_NODEFAULT=4)
        sonidos = Sonidos(reproductor)
        sonidos.habilitar(True)
        self.addCleanup(sonidos.cerrar)
        return sonidos, reproductor

    def test_efectos_validos_asincronos_y_cacheados(self):
        sonidos, reproductor = self.crear()
        with patch.object(sonidos, "_crear_efecto", wraps=sonidos._crear_efecto) as crear:
            for efecto in ("boton", "inicio", "mover", "abrir", "atacar", "recoger", "equipar", "usar",
                           "soltar", "retroceso", "victoria", "derrota"):
                sonidos.reproducir(efecto)
                ruta, flags = reproductor.PlaySound.call_args.args
                self.assertTrue(flags & reproductor.SND_ASYNC)
                with wave.open(ruta, "rb") as archivo:
                    self.assertEqual(archivo.getnchannels(), 1)
                    self.assertEqual(archivo.getsampwidth(), 2)
                    self.assertEqual(archivo.getframerate(), 22050)
                    self.assertGreater(archivo.getnframes(), 0)
                sonidos.reproducir(efecto)
            self.assertEqual(crear.call_count, 12)

    def test_boton_corto_respeta_silencio(self):
        sonidos, reproductor = self.crear()
        sonidos.reproducir("boton")
        with wave.open(reproductor.PlaySound.call_args.args[0], "rb") as archivo:
            self.assertLess(archivo.getnframes() / archivo.getframerate(), .2)
        sonidos.habilitar(False)
        llamadas = reproductor.PlaySound.call_count
        sonidos.reproducir("boton")
        self.assertEqual(reproductor.PlaySound.call_count, llamadas)

    def test_boton_envuelve_comando_una_vez_y_respeta_deshabilitado(self):
        import tkinter as tk
        from tkinter import ttk
        from vista.sonidos import sonorizar_botones
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(root.destroy)
        root.withdraw()
        sonido, accion = Mock(), Mock()
        boton = ttk.Button(root, text="Jugar", command=accion)
        sonorizar_botones(root, sonido)
        sonorizar_botones(root, sonido)
        boton.invoke()
        sonido.reproducir.assert_called_once_with("boton")
        accion.assert_called_once_with()
        boton.configure(state="disabled")
        boton.invoke()
        self.assertEqual(accion.call_count, 1)
        self.assertEqual(sonido.reproducir.call_count, 1)

    def test_silenciar_detiene_y_no_reproduce_nuevos_efectos(self):
        sonidos, reproductor = self.crear()
        sonidos.reproducir("atacar")
        sonidos.habilitar(False)
        reproductor.PlaySound.assert_called_with(None, 0)
        llamadas = reproductor.PlaySound.call_count
        sonidos.reproducir("mover")
        sonidos.reproducir("inicio")
        self.assertEqual(reproductor.PlaySound.call_count, llamadas)

    def test_menu_reproduce_intro_una_vez_al_mostrarse(self):
        from vista.menu_inicio import MenuInicio
        menu = MenuInicio.__new__(MenuInicio)
        menu.vista = Mock()
        menu.animacion, menu.panel, menu.fin = Mock(), Mock(), Mock()
        menu.botones = [Mock()]
        menu.resultado = ("jugar", None)
        self.assertEqual(menu.mostrar(), ("jugar", None))
        menu.vista.sonidos.reproducir.assert_called_once_with("inicio")
        menu.vista.root.wait_variable.assert_called_once_with(menu.fin)
        menu.animacion.detener.assert_called_once()

    def test_intro_con_ambiente_y_cola_no_usa_azar_global(self):
        sonidos, reproductor = self.crear()
        azar = random.getstate()
        sonidos.reproducir("inicio")
        self.assertEqual(random.getstate(), azar)
        with wave.open(reproductor.PlaySound.call_args.args[0], "rb") as archivo:
            self.assertGreater(archivo.getnframes() / archivo.getframerate(), 5)
            muestras = array("h", archivo.readframes(archivo.getnframes()))
        self.assertGreater(max(muestras), 100)
        self.assertLess(max(abs(v) for v in muestras), 32767)
        self.assertLess(abs(muestras[-1]), 20)

    def test_sin_dispositivo_o_con_error_no_interrumpe_juego(self):
        sonidos = Sonidos(None)
        sonidos.habilitar(True)
        sonidos.reproducir("mover")
        sonidos.cerrar()
        self.assertFalse(sonidos.activo)
        sonidos, reproductor = self.crear()
        reproductor.PlaySound.side_effect = RuntimeError("audio no disponible")
        sonidos.reproducir("mover")
        self.assertFalse(sonidos.activo)

    def test_cerrar_limpia_archivos_y_es_idempotente(self):
        sonidos, reproductor = self.crear()
        sonidos.reproducir("recoger")
        carpeta = Path(sonidos._carpeta.name)
        sonidos.cerrar()
        self.assertFalse(carpeta.exists())
        sonidos.cerrar()
        sonidos.habilitar(True)
        llamadas = reproductor.PlaySound.call_count
        sonidos.reproducir("victoria")
        self.assertEqual(reproductor.PlaySound.call_count, llamadas)

    def test_accion_rechazada_no_suena_y_aceptada_no_altera_motor(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        vista = VistaGrafica.__new__(VistaGrafica)
        vista.sonidos = Mock()
        vista.mostrar_error = Mock()
        controlador = ControladorJuego(datos.motor, vista)
        controlador.bitacora_replay = Mock()
        antes = datos.motor.exportar_estado()
        self.assertFalse(controlador._accion_modelo("mover", "N"))
        vista.sonidos.reproducir.assert_not_called()
        self.assertEqual(datos.motor.exportar_estado(), antes)
        datos.motor.ejecutar("esperar")
        esperado = datos.motor.exportar_estado()
        datos.motor.restaurar_estado(antes)
        self.assertTrue(controlador._accion_modelo("esperar"))
        vista.sonidos.reproducir.assert_called_once_with("esperar")
        self.assertEqual(datos.motor.exportar_estado(), esperado)

    def test_control_silenciar_en_la_vista(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista.sonidos, vista.var_sonido = Mock(), Mock()
        vista.var_sonido.get.return_value = False
        vista._alternar_sonido()
        vista.sonidos.habilitar.assert_called_once_with(False)
