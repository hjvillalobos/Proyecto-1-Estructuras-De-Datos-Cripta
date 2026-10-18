import tkinter as tk
import unittest

from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica
from vista.nombre_puntaje import NombrePuntaje


class TestNombrePuntaje(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.vista.cerrar)
        self.vista.root.update()

    def dialogo(self):
        dialogo = NombrePuntaje(self.vista, "Nombre para la tabla de puntajes:")
        self.addCleanup(lambda: dialogo.dialogo.destroy()
                        if not self.vista._cerrada and dialogo.dialogo.winfo_exists() else None)
        return dialogo

    def test_confirmar_nombre_con_enter_no_altera_motor(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        antes = datos.motor.exportar_estado()
        dialogo = self.dialogo()
        def confirmar():
            self.assertTrue(self.vista._en_menu)
            self.vista._enviar("esperar")
            dialogo.nombre.set("  Belén  ")
            dialogo.entrada.focus_force()
            dialogo.entrada.event_generate("<Return>")
        self.vista.root.after(100, confirmar)
        self.assertEqual(dialogo.mostrar(), "Belén")
        self.assertEqual(self.vista._cola, [])
        self.assertFalse(self.vista._en_menu)
        self.assertEqual(datos.motor.exportar_estado(), antes)
        self.assertIsNone(self.vista.root.grab_current())

    def test_cancelar_escape_y_cerrar_devuelven_vacio(self):
        for accion in ("cancelar", "escape", "cerrar", "enter_cancelar"):
            with self.subTest(accion=accion):
                dialogo = self.dialogo()
                dialogo.nombre.set("No registrar este nombre")
                def cancelar():
                    if accion == "cancelar":
                        dialogo.boton_cancelar.invoke()
                    elif accion == "escape":
                        dialogo.entrada.focus_force()
                        dialogo.entrada.event_generate("<Escape>")
                    elif accion == "enter_cancelar":
                        dialogo.boton_cancelar.focus_force()
                        dialogo.boton_cancelar.event_generate("<Return>")
                    else:
                        dialogo.dialogo.tk.call(dialogo.dialogo.protocol("WM_DELETE_WINDOW"))
                self.vista.root.after(100, cancelar)
                self.assertEqual(dialogo.mostrar(), "")
                self.assertIsNone(self.vista.root.grab_current())

    def test_nombre_vacio_conserva_contrato_del_controlador(self):
        dialogo = self.dialogo()
        dialogo.nombre.set("   ")
        self.vista.root.after(100, dialogo.boton_guardar.invoke)
        self.assertEqual(dialogo.mostrar(), "")

    def test_cerrar_aplicacion_durante_dialogo(self):
        dialogo = self.dialogo()
        self.vista.root.after(100, self.vista.cerrar)
        self.assertEqual(dialogo.mostrar(), "")
        self.assertTrue(self.vista._cerrada)

    def test_cancelar_antes_de_que_la_ventana_sea_visible(self):
        dialogo = self.dialogo()
        self.vista.root.after(0, dialogo.cancelar)
        self.assertEqual(dialogo.mostrar(), "")
        self.assertFalse(self.vista._en_menu)
