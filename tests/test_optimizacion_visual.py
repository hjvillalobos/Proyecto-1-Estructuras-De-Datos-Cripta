import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from vista.cache_visual import CacheVisual
from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos, Image, ImageTk


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestCacheVisual(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.base = Path(self.temporal.name)
        self.recursos = self.base / "recursos"
        self.recursos.mkdir()
        self.imagen = Image.new("RGBA", (12, 12), (123, 45, 67, 91))
        self.imagen.save(self.recursos / "jugador.png")
        self.cache = CacheVisual(self.recursos, self.base / "preparadas")

    def test_png_conserva_exactamente_los_pixeles_y_sobrevive_a_otra_vista(self):
        self.cache.guardar(("sprite", 196), self.imagen)
        otra = CacheVisual(self.recursos, self.cache.carpeta)
        self.assertEqual(otra.leer(("sprite", 196)).tobytes(), self.imagen.tobytes())

    def test_recurso_modificado_invalida_la_copia_preparada(self):
        self.cache.guardar("sprite", self.imagen)
        Image.new("RGBA", (13, 13), "blue").save(self.recursos / "jugador.png")
        otra = CacheVisual(self.recursos, self.cache.carpeta)
        self.assertIsNone(otra.leer("sprite"))

    def test_cache_danada_o_sin_permiso_no_impide_renderizar(self):
        self.cache.carpeta.mkdir()
        self.cache._ruta("sprite").write_bytes(b"PNG danado")
        self.assertIsNone(self.cache.leer("sprite"))
        with patch("vista.cache_visual.os.replace", side_effect=PermissionError):
            self.cache.guardar("otra", self.imagen)
        self.assertEqual(list(self.cache.carpeta.glob("*.tmp")), [])

    def test_disco_acotado(self):
        self.cache.LIMITE = 3
        for i in range(6):
            self.cache.guardar(("sprite", i), self.imagen)
        self.assertEqual(len(list(self.cache.carpeta.glob("*.png"))), 3)


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestReutilizacionSprites(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.r = RecursosGraficos(self.root)
        self.r._cache_visual = CacheVisual(self.r.carpeta, self.temporal.name)

    def test_fondos_preparados_conservan_pixeles_y_evitan_reescalado(self):
        from PIL import ImageOps
        r = self.r
        original, _ = r._original_fondo()
        menu = r.fondo(720, 480)
        self.assertEqual(ImageTk.getimage(menu).tobytes(),
                         ImageOps.fit(original, (720, 480), method=Image.Resampling.LANCZOS).convert("RGBA").tobytes())
        sala = r.fondo_sala(700, 268)
        corte = int(original.height * .58)
        referencia = Image.new("RGB", (700, 268))
        referencia.paste(original.crop((0, 0, original.width, corte)).resize(
            (700, 134), Image.Resampling.LANCZOS), (0, 0))
        referencia.paste(original.crop((0, corte, original.width, original.height)).resize(
            (700, 134), Image.Resampling.LANCZOS), (0, 134))
        self.assertEqual(ImageTk.getimage(sala).tobytes(), referencia.convert("RGBA").tobytes())
        otra = RecursosGraficos(self.root)
        otra._cache_visual = CacheVisual(otra.carpeta, self.temporal.name)
        with patch.object(otra, "_original_fondo", side_effect=AssertionError("Decodifico fondo")):
            self.assertEqual(ImageTk.getimage(otra.fondo(720, 480)).tobytes(), ImageTk.getimage(menu).tobytes())
            self.assertEqual(ImageTk.getimage(otra.fondo_sala(700, 268)).tobytes(), ImageTk.getimage(sala).tobytes())

    def test_imagen_preparada_admite_id_nuevo_e_invalida_al_cambiar_png(self):
        carpeta = Path(self.temporal.name) / "recursos_nuevos"
        carpeta.mkdir()
        ruta = carpeta / "entidad_nueva.png"
        Image.new("RGBA", (40, 60), (10, 20, 30, 180)).save(ruta)
        r = RecursosGraficos(self.root, carpeta)
        r._cache_visual = CacheVisual(carpeta, Path(self.temporal.name) / "imagenes")
        primera = ImageTk.getimage(r.imagen("entidad_nueva", 20, 30))
        otra = RecursosGraficos(self.root, carpeta)
        otra._cache_visual = CacheVisual(carpeta, r._cache_visual.carpeta)
        with patch.object(otra, "_objeto_ilustrado", side_effect=AssertionError("Proceso PNG")):
            self.assertEqual(ImageTk.getimage(otra.imagen("entidad_nueva", 20, 30)).tobytes(), primera.tobytes())
        Image.new("RGBA", (50, 60), (100, 120, 130, 180)).save(ruta)
        tercera = RecursosGraficos(self.root, carpeta)
        tercera._cache_visual = CacheVisual(carpeta, r._cache_visual.carpeta)
        self.assertNotEqual(ImageTk.getimage(tercera.imagen("entidad_nueva", 20, 30)).tobytes(), primera.tobytes())

    def test_fondo_modificado_invalida_la_cache_visual(self):
        carpeta = Path(self.temporal.name)
        self.r._cache_visual.guardar("fondo", Image.new("RGB", (10, 10)))
        recursos = carpeta / "recursos"
        recursos.mkdir()
        Image.new("RGB", (10, 10), "red").save(recursos / "fondo_cripta_ilustrado.png")
        cache = CacheVisual(recursos, carpeta / "fondos")
        cache.guardar("fondo", Image.new("RGB", (10, 10), "red"))
        Image.new("RGB", (11, 10), "blue").save(recursos / "fondo_cripta_ilustrado.png")
        self.assertIsNone(CacheVisual(recursos, cache.carpeta).leer("fondo"))

    def test_orientaciones_comparten_composicion_y_nueva_vista_no_recompone(self):
        self.r._preparadas.habilitada = False  # Verificar tambien el respaldo sin paquete distribuido.
        opciones = dict(armadura="itm_coraza_cuero", arma="itm_daga_oxidada", antorcha=True)
        with patch.object(self.r, "_componer_fotogramas", wraps=self.r._componer_fotogramas) as componer:
            normales = self.r.fotogramas_jugador(290, 196, **opciones)
            inversos = self.r.fotogramas_jugador(290, 196, invertir=True, **opciones)
        self.assertEqual(componer.call_count, 1)
        otra = RecursosGraficos(self.root)
        otra._cache_visual = CacheVisual(otra.carpeta, self.temporal.name)
        with patch.object(otra, "_componer_fotogramas", side_effect=AssertionError("Recompuso")):
            guardados = otra.fotogramas_jugador(290, 196, **opciones)
        for normal, inverso, guardado in zip(normales, inversos, guardados):
            a, b, c = map(ImageTk.getimage, (normal, inverso, guardado))
            self.assertEqual(a.tobytes(), c.tobytes())
            self.assertEqual(a.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(), b.tobytes())

    def test_reposo_preparado_conserva_pose_de_agarre_y_daga_contraria(self):
        from vista.equipo_visual import armar_jugador, vestir_jugador
        r = self.r
        with Image.open(r.carpeta / "jugador_antorcha.png") as archivo:
            referencia = archivo.convert("RGBA")
        referencia = vestir_jugador(referencia, r._ropa_jugador("itm_coraza_cuero"),
                                    torso=((.48, .25), (.70, .265), (.48, .435)))
        referencia = armar_jugador(referencia, r._arma_jugador("itm_daga_oxidada"),
                                  r._puno_jugador(), mano=(.785, .582), puno_cerrado=True)
        referencia.thumbnail((230, 196), Image.Resampling.LANCZOS)
        actual = r.jugador_armado(230, 196, "itm_daga_oxidada", "itm_coraza_cuero", antorcha=True)
        self.assertEqual(ImageTk.getimage(actual).tobytes(), referencia.tobytes())
        otra = RecursosGraficos(self.root)
        otra._cache_visual = CacheVisual(otra.carpeta, self.temporal.name)
        with patch.object(otra, "_original_jugador_antorcha", side_effect=AssertionError("Recompuso")):
            guardada = otra.jugador_armado(230, 196, "itm_daga_oxidada", "itm_coraza_cuero", antorcha=True)
        self.assertEqual(ImageTk.getimage(guardada).tobytes(), referencia.tobytes())


class TestEsperaNativa(unittest.TestCase):
    def test_evento_nativo_entrega_comando_sin_sleep(self):
        v = VistaGrafica.__new__(VistaGrafica)
        v.root = Mock()
        v._cola, v._cerrada, v._refrescar_inv = [], False, False
        v.root.tk.dooneevent.side_effect = lambda: v._cola.append("esperar")
        with patch("vista.grafica.time.sleep", side_effect=AssertionError("Sondeo")):
            self.assertEqual(v.pedir_comando(), "esperar")
        v.root.tk.dooneevent.assert_called_once_with()

    def test_cierre_en_evento_nativo_no_se_bloquea(self):
        v = VistaGrafica.__new__(VistaGrafica)
        v.root = Mock()
        v._cola, v._cerrada, v._refrescar_inv = [], False, False
        v.root.tk.dooneevent.side_effect = lambda: setattr(v, "_cerrada", True)
        self.assertIsNone(v.pedir_comando())

    def test_equipo_completo_no_prepara_un_chaleco_que_va_a_reemplazar(self):
        from dataclasses import replace
        from tests import test_regresiones_juego as base
        try:
            v = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(v.cerrar)
        v.root.withdraw()
        datos = base.TestRegresionesJuego()
        datos.setUp()
        estado = replace(datos.motor.estado_vista(), arma_tipo="itm_daga_oxidada",
                         armadura_tipo="itm_coraza_cuero", efectos=["antorcha"])
        with patch.object(v.recursos, "jugador_vestido", side_effect=AssertionError("Trabajo duplicado")):
            v.mostrar_estado(estado, [])
        self.assertEqual(v.canvas.find_withtag("armadura_visible"), v.canvas.find_withtag("jugador"))
        self.assertEqual(v.canvas.find_withtag("antorcha_visible"), v.canvas.find_withtag("jugador"))
