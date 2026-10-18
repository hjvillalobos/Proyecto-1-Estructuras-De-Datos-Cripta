import tkinter as tk
import unittest
from unittest.mock import patch

from datos.puntajes import RegistroPuntaje
from vista.grafica import VistaGrafica
from vista.tabla_puntajes import TablaPuntajesVisual
from vista.tema import PANEL


class TestTablaPuntajesVisual(unittest.TestCase):
    def setUp(self):
        try:
            self.v = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.v.cerrar)
        self.v.root.update()

    def crear(self, registros):
        tabla = TablaPuntajesVisual(self.v, registros)
        self.addCleanup(lambda: tabla.cerrar() if tabla.dialogo.winfo_exists() else None)
        return tabla

    def test_datos_orden_y_colores_sin_modificar_registros(self):
        registros = [RegistroPuntaje("Belena " * 10, "cripta-nueva", "version-nueva", 20, 3, 1500, "victoria"),
                     RegistroPuntaje("Otro", "otra-cripta", "v2", 10, 1, 600, "derrota")]
        originales = [vars(r).copy() for r in registros]
        t = self.crear(registros)
        filas = t.tabla.get_children()
        self.assertEqual(len(filas), 2)
        self.assertEqual(t.tabla.item(filas[0], "values"),
                         ("1", registros[0].nombre, "cripta-nueva", "Victoria", "1500", "20", "3"))
        self.assertEqual(t.tabla.item(filas[1], "tags"), ("derrota",))
        t.tabla.selection_set(filas[1])
        t._seleccionar()
        self.assertIn("v2", t.detalle.get())
        self.assertEqual([vars(r) for r in registros], originales)
        self.assertNotEqual(t.tabla.tag_configure("victoria", "foreground"), "white")

    def test_vacio_oscuro_y_desplazamiento_en_ambos_ejes(self):
        t = self.crear([])
        self.assertEqual(t.vacio.cget("text"), "Sin partidas registradas")
        self.assertEqual(t.vacio.cget("bg"), PANEL)
        self.assertFalse(t.tabla.get_children())
        self.assertTrue(t.tabla.cget("xscrollcommand"))
        self.assertTrue(t.tabla.cget("yscrollcommand"))

    def test_modal_restaura_menu_y_no_encola_comandos(self):
        t = self.crear([])
        self.v._en_menu = False
        def comprobar_y_cerrar():
            self.assertTrue(self.v._en_menu)
            t.dialogo.event_generate("<Escape>")
            if t.dialogo.winfo_exists():
                t.boton_cerrar.invoke()
        self.v.root.after(150, comprobar_y_cerrar)
        t.mostrar()
        self.assertFalse(self.v._en_menu)
        self.assertEqual(self.v._cola, [])
        self.assertFalse(t.dialogo.winfo_exists())

    def test_vista_utiliza_tabla_y_cerrada_no_abre_dialogo(self):
        with patch("vista.tabla_puntajes.TablaPuntajesVisual") as tabla:
            self.v.mostrar_puntajes([])
            tabla.assert_called_once_with(self.v, [])
            tabla.return_value.mostrar.assert_called_once()
            self.v.cerrar()
            self.v.mostrar_puntajes([])
            tabla.assert_called_once()
