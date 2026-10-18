import io
import tempfile
import tkinter as tk
import unittest
from contextlib import redirect_stdout
from copy import deepcopy
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from red.cache import CacheSinEspacioError
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica


class TestFallosTransaccionales(unittest.TestCase):
    def test_recogida_fallida_revierte_intervalo_y_no_se_graba(self):
        for despues_de_eventos in (False, True):
            d = base.TestRegresionesJuego()
            d.setUp()
            d._suelo("daga")
            d._enemigo(velocidad=1000)
            antes = deepcopy(d.motor.exportar_estado())
            c = ControladorJuego(d.motor, Mock())
            c.bitacora_replay = Mock()
            fallos = [None, CacheSinEspacioError("llena"), None] if despues_de_eventos else [CacheSinEspacioError("llena"), None]
            with self.subTest(despues=despues_de_eventos), \
                    patch.object(d.motor, "_sincronizar_referencias", side_effect=fallos):
                with self.assertRaises(CacheSinEspacioError):
                    c._accion_modelo("recoger", "daga")
            self.assertEqual(d.motor.exportar_estado(), antes)
            self.assertEqual(d.motor.historial.cantidad_turnos(), 0)
            self.assertEqual(c.mensajes.ultimos(), [])
            c.bitacora_replay.registrar_accion.assert_not_called()
            self.assertTrue(d.motor.ejecutar("recoger", "daga").ok)

    def test_pergamino_no_cambia_si_recoger_o_soltar_falla(self):
        for accion in ("recoger", "soltar"):
            d = base.TestRegresionesJuego()
            d.setUp()
            if accion == "recoger":
                d._suelo("pergamino")
            else:
                d._inventario("pergamino")
            antes = deepcopy(d.motor.exportar_estado())
            with self.subTest(accion=accion), patch.object(d.motor, "_sincronizar_referencias",
                                                         side_effect=CacheSinEspacioError("llena")):
                with self.assertRaises(CacheSinEspacioError):
                    d.motor.ejecutar(accion, "pergamino")
            self.assertEqual(d.motor.exportar_estado(), antes)

    def test_carga_rechazada_regresa_menu_sin_pedir_comandos(self):
        import main
        d = base.TestRegresionesJuego()
        d.setUp()
        estado = d.motor.exportar_estado()
        estado.jugador.vida = 99
        vista = Mock(spec=VistaGrafica)
        vista.mostrar_menu.side_effect = [("cargar", "base.bin"), ("salir", None)]
        with tempfile.TemporaryDirectory() as carpeta, redirect_stdout(io.StringIO()), \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("datos.guardado_binario.cargar_estado", return_value=estado), \
                patch("modelo.juego.crear_juego", return_value=d.motor), \
                patch("controlador.controlador.BitacoraReplay"):
            self.assertEqual(main.main(["--gui", "--offline", ".cache/cripta", "--datos-dir", carpeta]), 0)
        self.assertEqual(vista.mostrar_menu.call_count, 2)
        vista.pedir_comando.assert_not_called()
        vista.reiniciar_presentacion.assert_called_once()
        vista.cerrar.assert_called_once()

    def test_desactivar_animaciones_cancela_dano_actual_y_futuro(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.withdraw()
            d = base.TestRegresionesJuego()
            d.setUp()
            vista.mostrar_estado(d.motor.estado_vista(), [])
            d.motor.jugador.vida -= 1
            vista.mostrar_estado(d.motor.estado_vista(), [])
            self.assertTrue(vista._animaciones)
            vista.var_movimiento.set(False)
            vista._alternar_movimiento()
            self.assertEqual(vista._animaciones, [])
            self.assertEqual(vista.canvas.find_withtag("dano_flotante"), ())
            d.motor.jugador.vida -= 1
            vista.mostrar_estado(d.motor.estado_vista(), [])
            self.assertEqual(vista._animaciones, [])
            self.assertEqual(vista.canvas.find_withtag("dano_flotante"), ())
        finally:
            vista.cerrar()
