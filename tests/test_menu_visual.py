import tempfile
import tkinter as tk
import unittest

from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos, Image
from vista.selector_cripta import SelectorCripta
from tests.test_criptas_api import CRIPTAS


class TestMenuVisual(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.vista.root.withdraw()
        self.addCleanup(self.vista.cerrar)

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_fondo_cubre_tamano_solicitado_y_cache_acotada(self):
        recursos = self.vista.recursos
        for ancho, alto in ((1100, 760), (1280, 800), (820, 560)):
            fondo = recursos.fondo(ancho, alto)
            self.assertIsNotNone(fondo)
            self.assertEqual((fondo.width(), fondo.height()), (ancho, alto))
            self.assertIs(recursos.fondo(ancho, alto), fondo)
        self.assertEqual(recursos._fondo[0], (820, 560))

    def test_sin_archivo_fondo_se_conserva_interfaz(self):
        with tempfile.TemporaryDirectory() as carpeta:
            recursos = RecursosGraficos(self.vista.root, carpeta)
            self.assertIsNone(recursos.fondo(820, 560))

    def test_imagen_en_geometria_inicial_no_divide_por_cero(self):
        self.assertIsNotNone(self.vista.recursos.imagen("jugador", 0, 0))

    def test_selector_actualiza_datos_sin_acciones(self):
        selector = SelectorCripta(self.vista, CRIPTAS)
        self.addCleanup(lambda: selector.dialogo.destroy() if selector.dialogo.winfo_exists() else None)
        selector.dialogo.update_idletasks()
        selector.lista.selection_clear(0, "end")
        selector.lista.selection_set(3)
        selector.dibujar()
        textos = [selector.canvas.itemcget(item, "text") for item in selector.canvas.find_all()
                  if selector.canvas.type(item) == "text"]
        self.assertIn("50", textos)
        self.assertIn("4", textos)
        self.assertEqual(self.vista._cola, [])
        self.assertEqual(selector.aceptar(), "break")
        self.assertEqual(selector.resultado, "cripta-04")

    def test_selector_vacio_no_puede_iniciar(self):
        selector = SelectorCripta(self.vista, [])
        selector.dialogo.update_idletasks()
        self.assertIn("disabled", selector.controles.winfo_children()[1].state())
        selector.aceptar()
        self.assertIsNone(selector.resultado)
        selector.dialogo.destroy()
