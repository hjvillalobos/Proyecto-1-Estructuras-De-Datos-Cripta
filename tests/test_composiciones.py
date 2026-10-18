from itertools import product
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from vista.composiciones import ComposicionesPreparadas
from vista.cache_visual import CacheVisual
from vista.recursos_graficos import RecursosGraficos, Image, ImageTk
from utilidades.preparar_visuales import ALTURAS, reducir_cuadros


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestComposiciones(unittest.TestCase):
    def test_solo_transfiere_poses_necesarias_y_preserva_alpha_y_orden(self):
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        hoja = Image.new("RGBA", (8*12, 10))
        for i in range(8):
            hoja.paste((i*25, 255-i*20, 100, 30+i*25), (i*12, 0, (i+1)*12, 10))
        r = RecursosGraficos(root)
        with patch("vista.recursos_graficos.ImageTk.PhotoImage", wraps=ImageTk.PhotoImage) as subir:
            cuadros = r._fotos_desde_hoja(hoja, (4, 5))
        self.assertEqual(subir.call_count, 2)
        for i, cuadro in zip((4, 5), cuadros):
            self.assertEqual(ImageTk.getimage(cuadro).tobytes(), hoja.crop((i*12, 0, (i+1)*12, 10)).tobytes())

    def test_firma_portable_entre_lf_y_crlf(self):
        recursos = RecursosGraficos(None).carpeta
        leer_original = Path.read_bytes
        def con_crlf(ruta):
            datos = leer_original(ruta)
            return datos.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n") if ruta.suffix == ".py" else datos
        referencia = ComposicionesPreparadas(recursos).firma()
        with patch.object(Path, "read_bytes", con_crlf):
            self.assertEqual(ComposicionesPreparadas(recursos).firma(), referencia)

    def test_cada_accion_carga_solo_sus_poses_y_reutiliza_las_imagenes(self):
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        with tempfile.TemporaryDirectory() as carpeta:
            r = RecursosGraficos(root)
            r._cache_visual = CacheVisual(r.carpeta, carpeta)
            for accion, cantidad in (("atacar", 2), ("correr", 4), ("caer", 2)):
                with patch("vista.recursos_graficos.ImageTk.PhotoImage", wraps=ImageTk.PhotoImage) as subir:
                    primera = r.fotogramas_accion(accion, 290, 196, armadura="itm_coraza_cuero", antorcha=True)
                    segunda = r.fotogramas_accion(accion, 290, 196, armadura="itm_coraza_cuero", antorcha=True)
                self.assertIs(primera, segunda)
                self.assertEqual(len(primera), cantidad)
                self.assertEqual(subir.call_count, cantidad)

    def test_paquete_nativo_conserva_pixeles_en_todas_las_combinaciones(self):
        original = RecursosGraficos(None)
        original._preparadas.habilitada = False
        paquete = ComposicionesPreparadas(original.carpeta)
        for coraza, daga, antorcha in product((0, 1), repeat=3):
            armadura, arma = "itm_coraza_cuero" if coraza else None, "itm_daga_oxidada" if daga else None
            with self.subTest(equipo=(coraza, daga, antorcha)):
                reposo = original._componer_reposo(armadura, arma, antorcha)
                self.assertEqual(paquete.leer(("reposo", coraza, daga, antorcha)).tobytes(), reposo.tobytes())
                cuadros = original._componer_fotogramas(armadura, arma, antorcha)
                preparados = RecursosGraficos(None)._componer_fotogramas(armadura, arma, antorcha)
                self.assertEqual([c.tobytes() for c in cuadros], [c.tobytes() for c in preparados])
                for invertir in (0, 1):
                    referencia = reducir_cuadros(cuadros, (290, 196), invertir)
                    atlas = paquete.leer(("secuencia", 290, 196, invertir, coraza, daga, antorcha))
                    w = atlas.width // 8
                    self.assertEqual([c.tobytes() for c in referencia],
                        [atlas.crop((i*w, 0, (i+1)*w, atlas.height)).tobytes() for i in range(8)])

    def test_todas_las_bebidas_preservan_pixeles(self):
        original = RecursosGraficos(None)
        original._preparadas.habilitada = False
        paquete = ComposicionesPreparadas(original.carpeta)
        for coraza, antidoto, antorcha in product((0, 1), repeat=3):
            cuadro = original._componer_bebida("itm_coraza_cuero" if coraza else None, antidoto, antorcha)
            self.assertEqual(paquete.leer(("bebida_original", coraza, antidoto, antorcha)).tobytes(), cuadro.tobytes())

    def test_firma_distinta_o_png_corrupto_usa_respaldo(self):
        r = RecursosGraficos(None)
        with patch.object(r._preparadas, "firma", return_value="otra-version"):
            self.assertIsNone(r._preparadas.leer(("reposo", 1, 1, 1)))
        with tempfile.TemporaryDirectory() as carpeta:
            r._preparadas.carpeta = Path(carpeta)
            r._preparadas._ruta(("reposo", 1, 1, 1)).write_bytes(b"PNG corrupto")
            self.assertIsNone(r._preparadas.leer(("reposo", 1, 1, 1)))

    def test_tamanos_distribuidos_no_componen_equipo_ni_bebidas(self):
        root = tk.Tk()
        root.withdraw()
        self.addCleanup(root.destroy)
        with tempfile.TemporaryDirectory() as carpeta:
            r = RecursosGraficos(root)
            r._cache_visual = CacheVisual(r.carpeta, carpeta)
            with patch.object(r, "_componer_reposo", side_effect=AssertionError("Compuso reposo")), \
                    patch.object(r, "_componer_fotogramas", side_effect=AssertionError("Compuso animaciones")), \
                    patch.object(r, "_componer_bebida", side_effect=AssertionError("Compuso bebida")):
                for alto in ALTURAS:
                    for coraza, daga, antorcha in product((0, 1), repeat=3):
                        armadura, arma = "itm_coraza_cuero" if coraza else None, "itm_daga_oxidada" if daga else None
                        if daga or antorcha:
                            self.assertIsNotNone(r.jugador_armado(230, alto, arma, armadura, antorcha))
                        elif coraza:
                            self.assertIsNotNone(r.jugador_vestido(230, alto, armadura))
                        for invertir in (False, True):
                            self.assertEqual(len(r.fotogramas_jugador(290, alto, invertir, armadura, arma, antorcha)), 8)
                        for antidoto in (False, True):
                            self.assertIsNotNone(r.pose_beber(alto, armadura, antidoto, antorcha))
                self.assertLessEqual(len(r._secuencias), 4)
                self.assertLessEqual(len(r._jugadores_vestidos), 4)
                self.assertLessEqual(len(r._bebidas), 4)
