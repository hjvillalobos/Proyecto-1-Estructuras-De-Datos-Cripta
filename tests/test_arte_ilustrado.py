import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from vista.recursos_graficos import RecursosGraficos, Image, _RECORTES_OBJETOS
from vista.cache_visual import CacheVisual


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestArteIlustrado(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.recursos = RecursosGraficos(self.root)

    def test_objetos_comparten_hoja_y_conservan_transparencia(self):
        for tipo, _ in _RECORTES_OBJETOS:
            with self.subTest(tipo=tipo):
                cuadro = self.recursos._objeto_ilustrado(tipo)
                self.assertIsNotNone(cuadro)
                self.assertEqual(cuadro.mode, "RGBA")
                self.assertGreater(min(cuadro.size), 32)
                minimo, maximo = cuadro.getchannel("A").getextrema()
                self.assertEqual((minimo, maximo), (0, 255))
                imagen = self.recursos.imagen(tipo, 52, 52)
                self.assertIsNotNone(imagen)
                self.assertLessEqual(max(imagen.width(), imagen.height()), 52)
                self.assertIs(self.recursos.imagen(tipo, 52, 52), imagen)

    def test_guardian_ilustrado_y_jugador_original(self):
        self.recursos._preparadas.habilitada = False  # Comprobar los originales tambien sin composiciones distribuidas.
        with tempfile.TemporaryDirectory() as carpeta:
            self.recursos._cache_visual = CacheVisual(self.recursos.carpeta, carpeta)
            with patch("vista.recursos_graficos.Image.open", wraps=Image.open) as abrir:
                self.assertIsNotNone(self.recursos.imagen("ent_guardian_oseo", 140, 118))
                self.assertIsNotNone(self.recursos.imagen("jugador", 230, 180))
                self.assertEqual(len(self.recursos.fotogramas_jugador(290, 180)), 8)
        nombres = [Path(c.args[0]).name for c in abrir.call_args_list]
        self.assertIn("guardian_ilustrado.png", nombres)
        self.assertIn("jugador.png", nombres)
        self.assertIn("jugador_acciones.png", nombres)

    def test_fondo_ilustrado_en_sala_y_menu_y_respaldo_original(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.recursos._cache_visual = CacheVisual(self.recursos.carpeta, carpeta)
            with patch("vista.recursos_graficos.Image.open", wraps=Image.open) as abrir:
                self.assertIsNotNone(self.recursos.fondo_sala(700, 268))
                self.assertIsNotNone(self.recursos.fondo(1100, 760))
        originales = [Path(c.args[0]) for c in abrir.call_args_list
                      if Path(c.args[0]).parent == self.recursos.carpeta]
        self.assertTrue(originales)
        self.assertTrue(all(ruta.name == "fondo_cripta_ilustrado.png" for ruta in originales))
        import shutil
        with tempfile.TemporaryDirectory() as carpeta:
            for nombre in ("fondo_ladrillos.png", "ent_guardian_oseo.png", "itm_pocion_menor.png"):
                shutil.copyfile(self.recursos.carpeta / nombre, Path(carpeta) / nombre)
            respaldo = RecursosGraficos(self.root, carpeta)
            self.assertIsNotNone(respaldo.fondo_sala(700, 268))
            self.assertIsNotNone(respaldo.fondo(1100, 760))
            self.assertIsNotNone(respaldo.imagen("ent_guardian_oseo", 140, 118))
            self.assertIsNotNone(respaldo.imagen("itm_pocion_menor", 52, 52))
