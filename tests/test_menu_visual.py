import tempfile
import tkinter as tk
import unittest

from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos, Image
from vista.selector_cripta import SelectorCripta
from tests.test_criptas_api import CRIPTAS
from tests import test_regresiones_juego as base


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

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_fondo_sala_calido_tiene_cache_independiente_del_menu(self):
        recursos = self.vista.recursos
        menu = recursos.fondo(1100, 760)
        sala = recursos.fondo_sala(700, 268)
        self.assertIsNotNone(sala)
        self.assertEqual((sala.width(), sala.height()), (700, 268))
        self.assertIs(recursos.fondo_sala(700, 268), sala)
        self.assertIs(recursos.fondo(1100, 760), menu)
        with tempfile.TemporaryDirectory() as carpeta:
            self.assertIsNone(RecursosGraficos(self.vista.root, carpeta).fondo_sala(700, 268))

    def test_jugador_mas_pequeno_y_fondo_no_alteran_motor(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        antes = datos.motor.exportar_estado()
        self.vista.mostrar_estado(datos.motor.estado_vista(), [])
        sprite = next(i for i in self.vista.canvas.find_withtag("jugador")
                      if self.vista.canvas.type(i) == "image")
        nombre = self.vista.canvas.itemcget(sprite, "image")
        alto = max(350, self.vista.canvas.winfo_height())
        self.assertLessEqual(int(self.vista.root.tk.call("image", "height", nombre)),
                             int(min(280, alto - 175) * .70))
        if Image is not None:
            self.assertTrue(self.vista.canvas.find_withtag("fondo_sala"))
        self.assertEqual(datos.motor.exportar_estado(), antes)
        self.assertEqual(self.vista._cola, [])

    def test_sala_amplia_y_controles_visibles_en_dos_tamanos(self):
        vista = self.vista
        datos = base.TestRegresionesJuego()
        datos.setUp()
        for geometria in ("1100x760", "1280x850"):
            with self.subTest(geometria=geometria):
                vista.root.geometry(geometria)
                vista.root.deiconify()
                vista.root.update()
                vista.mostrar_estado(datos.motor.estado_vista(), [])
                vista.root.update()
                self.assertGreaterEqual(vista.canvas.winfo_height(), 390)
                sprite = vista.canvas.find_withtag("jugador")[0]
                caja = vista.canvas.bbox(sprite)
                self.assertLessEqual(caja[3] - caja[1], 196)
                self.assertGreater(caja[1], 62)
                for control in (vista.boton_esperar, vista.lbl_tiempo, vista.log):
                    self.assertTrue(control.winfo_viewable())
                    self.assertLess(control.winfo_rooty() + control.winfo_height(),
                                    vista.root.winfo_rooty() + vista.root.winfo_height() + 1)

    def test_selector_ocupa_la_misma_ventana_y_escape_regresa(self):
        vista = self.vista
        vista.root.geometry("1100x760")
        vista.root.deiconify()
        selector = SelectorCripta(vista, CRIPTAS)
        vista.root.update()
        self.assertIs(selector.panel.master, vista.root)
        self.assertFalse(any(isinstance(h, tk.Toplevel) for h in vista.root.winfo_children()))
        self.assertEqual(selector.panel.winfo_width(), vista.root.winfo_width())
        self.assertEqual(selector.panel.winfo_height(), vista.root.winfo_height())
        self.assertIsNone(vista._estado)
        def volver():
            vista.root.focus_force()
            vista.root.event_generate("<Escape>")
        vista.root.after(100, volver)
        self.assertIsNone(selector.mostrar())
        self.assertFalse(selector.panel.winfo_exists())
        self.assertFalse(vista._en_menu)
        self.assertEqual(vista._cola, [])
