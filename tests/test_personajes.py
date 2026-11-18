"""Seleccion cosmetica, aislamiento y cobertura real del paquete de la tigresa."""
from itertools import product
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from vista.cache_visual import CacheVisual
from vista.composiciones import ComposicionesPreparadas
from vista.grafica import VistaGrafica
from vista.menu_inicio import MenuInicio
from vista.personajes import leer_personaje, guardar_personaje
from vista.recursos_graficos import RecursosGraficos, Image, ImageTk
from utilidades.preparar_visuales import ALTURAS


class TestPreferenciaPersonaje(unittest.TestCase):
    def test_preferencia_local_validada_y_tolerante_a_archivo_ajeno(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "preferencia.json"
            self.assertEqual(leer_personaje(ruta), "jugador")
            for personaje in ("tigresa", "jugador"):
                guardar_personaje(personaje, ruta)
                self.assertEqual(leer_personaje(ruta), personaje)
            for datos in ('{', 'null', '[]', '{"personaje": "../otro"}'):
                ruta.write_text(datos, encoding="utf-8")
                self.assertEqual(leer_personaje(ruta), "jugador")
            with self.assertRaises(ValueError):
                guardar_personaje("../otro", ruta)
            self.assertEqual(list(Path(carpeta).glob("*.tmp")), [])

    def test_sin_permisos_conserva_eleccion_en_memoria(self):
        with patch.object(Path, "mkdir", side_effect=PermissionError):
            guardar_personaje("tigresa")


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestPaqueteTigresa(unittest.TestCase):
    def test_las_caches_no_comparten_rutas_ni_firmas(self):
        recursos = RecursosGraficos(None).carpeta
        a, b = (CacheVisual(recursos, personaje=p) for p in ("jugador", "tigresa"))
        self.assertNotEqual(a._ruta(("secuencia", 290, 196)), b._ruta(("secuencia", 290, 196)))
        self.assertNotEqual(a._firma_actual(), b._firma_actual())
        a, b = (ComposicionesPreparadas(recursos, p) for p in ("jugador", "tigresa"))
        self.assertNotEqual(a._ruta(("acciones", 0, 0, 0)), b._ruta(("acciones", 0, 0, 0)))
        self.assertNotEqual(a.firma(), b.firma())

    def test_todas_las_composiciones_coinciden_con_su_respaldo(self):
        r = RecursosGraficos(None, personaje="tigresa")
        paquete = ComposicionesPreparadas(r.carpeta, "tigresa")
        r._preparadas.habilitada = False
        for coraza, daga, antorcha in product((0, 1), repeat=3):
            armadura = "itm_coraza_cuero" if coraza else None
            arma = "itm_daga_oxidada" if daga else None
            equipo = (coraza, daga, antorcha)
            with self.subTest(equipo=equipo):
                reposo = r._componer_reposo(armadura, arma, antorcha)
                self.assertEqual(paquete.leer(("reposo", *equipo)).tobytes(), reposo.tobytes())
                cuadros = r._componer_fotogramas(armadura, arma, antorcha)
                atlas = paquete.leer(("acciones", *equipo))
                w = atlas.width // 8
                self.assertEqual(len(cuadros), 8)
                for i, cuadro in enumerate(cuadros):
                    self.assertEqual(cuadro.tobytes(), atlas.crop((i*w, 0, (i+1)*w, atlas.height)).tobytes())
                for antidoto in (False, True):
                    bebida = r._componer_bebida(armadura, antidoto, antorcha)
                    self.assertEqual(paquete.leer(("bebida_original", coraza, int(antidoto), antorcha)).tobytes(),
                                     bebida.tobytes())

    def test_hojas_con_alpha_y_celdas_compatibles(self):
        r = RecursosGraficos(None, personaje="tigresa")
        for sufijo in ("", "_acciones", "_beber", "_antorcha"):
            with Image.open(r._ruta_personaje(sufijo)) as imagen:
                self.assertEqual(imagen.mode, "RGBA")
                self.assertEqual(imagen.getchannel("A").getextrema()[0], 0)
                self.assertGreater(imagen.getchannel("A").getextrema()[1], 240)
                self.assertIsNotNone(imagen.getchannel("A").getbbox())
                if sufijo == "_acciones":
                    self.assertEqual(imagen.width % 4, 0)
                    self.assertEqual(imagen.height % 2, 0)


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestSelectorYAnimaciones(unittest.TestCase):
    def setUp(self):
        self.vista = VistaGrafica()
        self.vista.root.withdraw()
        self.addCleanup(self.vista.cerrar)

    def test_selector_real_conserva_eleccion_al_reiniciar_y_restaura_original(self):
        v = self.vista
        v.recursos.seleccionar_personaje("jugador")
        original = ImageTk.getimage(v.recursos.imagen("jugador", 230, 196)).tobytes()
        menu = MenuInicio(v, lambda: None, lambda: None)
        with patch("vista.menu_inicio.guardar_personaje") as guardar:
            menu.personaje.set("tigresa")
            menu.cambiar_personaje()
            guardar.assert_called_once_with("tigresa")
        self.assertEqual(v.recursos.personaje, "tigresa")
        self.assertNotEqual(ImageTk.getimage(v.recursos.imagen("jugador", 230, 196)).tobytes(), original)
        v.reiniciar_presentacion()
        self.assertEqual(v.recursos.personaje, "tigresa")
        menu.panel.destroy()
        nuevo = MenuInicio(v, lambda: None, lambda: None)
        self.assertEqual(nuevo.personaje.get(), "tigresa")
        nuevo.panel.destroy()
        v.recursos.seleccionar_personaje("jugador")
        self.assertEqual(ImageTk.getimage(v.recursos.imagen("jugador", 230, 196)).tobytes(), original)

    def test_tamanos_equipo_y_animaciones_no_recomponen_y_cache_acotada(self):
        r = self.vista.recursos
        r.seleccionar_personaje("tigresa")
        with tempfile.TemporaryDirectory() as carpeta:
            r._cache_visual = CacheVisual(r.carpeta, carpeta, personaje="tigresa")
            with patch.object(r, "_componer_reposo", side_effect=AssertionError("Recompuso reposo")), \
                 patch.object(r, "_componer_fotogramas", side_effect=AssertionError("Recompuso acciones")), \
                 patch.object(r, "_componer_bebida", side_effect=AssertionError("Recompuso bebida")):
                for alto in ALTURAS:
                    for coraza, daga, antorcha in product((0, 1), repeat=3):
                        armadura = "itm_coraza_cuero" if coraza else None
                        arma = "itm_daga_oxidada" if daga else None
                        if daga or antorcha:
                            self.assertIsNotNone(r.jugador_armado(230, alto, arma, armadura, antorcha))
                        elif coraza:
                            self.assertIsNotNone(r.jugador_vestido(230, alto, armadura))
                        for invertir in (False, True):
                            for accion, n in (("correr", 4), ("atacar", 2), ("caer", 2)):
                                opciones = dict(invertir=invertir, armadura=armadura, arma=arma, antorcha=antorcha)
                                cuadros = r.fotogramas_accion(accion, 290, alto, **opciones)
                                self.assertEqual(len(cuadros), n)
                                with patch("vista.recursos_graficos.ImageTk.PhotoImage", side_effect=AssertionError("Subio otra vez")):
                                    self.assertIs(r.fotogramas_accion(accion, 290, alto, **opciones), cuadros)
                        for antidoto in (False, True):
                            self.assertIsNotNone(r.pose_beber(alto, armadura, antidoto, antorcha))
            self.assertLessEqual(len(r._acciones), 8)
            self.assertLessEqual(len(r._secuencias), 4)
            self.assertLessEqual(len(r._jugadores_vestidos), 4)
            self.assertLessEqual(len(r._bebidas), 4)
            self.assertLessEqual(len(r._hojas_accion), 2)

    def test_carrera_ataque_y_caida_comparten_decodificacion(self):
        r = self.vista.recursos
        r.seleccionar_personaje("tigresa")
        self.assertEqual(len(r.fotogramas_accion("correr", 290, 196)), 4)
        with patch.object(r._preparadas, "leer", side_effect=AssertionError("Decodifico otra vez")), \
             patch.object(r._cache_visual, "leer", side_effect=AssertionError("Consulto disco otra vez")):
            self.assertEqual(len(r.fotogramas_accion("atacar", 290, 196)), 2)
            self.assertEqual(len(r.fotogramas_accion("caer", 290, 196)), 2)

    def test_cambio_preserva_fondo_y_descarta_todas_las_poses_del_otro(self):
        r = self.vista.recursos
        fondo = r.fondo(1100, 760)
        r.imagen("jugador", 230, 196)
        r.fotogramas_accion("correr", 290, 196)
        r.pose_beber(196)
        siguiente = "tigresa" if r.personaje == "jugador" else "jugador"
        r.seleccionar_personaje(siguiente)
        self.assertIs(r.fondo(1100, 760), fondo)
        self.assertEqual((r._acciones, r._secuencias, r._bebidas, r._jugadores_vestidos, r._hojas_accion),
                         ([], [], [], [], []))
        self.assertIsNone(r._hoja_jugador)
        self.assertIsNone(r._pose_beber)
        with self.assertRaises(ValueError):
            r.seleccionar_personaje("../../otro")
        self.assertEqual(r.personaje, siguiente)

    def test_portada_muestra_ambos_sin_recargar_retratos_al_alternar(self):
        v = self.vista
        v.root.deiconify()
        v.root.geometry("1100x760")
        menu = MenuInicio(v, lambda: None, lambda: None)
        self.addCleanup(lambda: menu.panel.destroy() if menu.panel.winfo_exists() else None)
        v.root.update()
        menu.dibujar()
        for nombre in ("jugador", "tigresa"):
            items = menu.canvas.find_withtag("personaje_" + nombre)
            self.assertEqual(sum(menu.canvas.type(i) == "image" for i in items), 1)
            self.assertEqual(sum(menu.canvas.type(i) == "oval" for i in items), 1)
        retratos = tuple(menu.imagenes[1:])
        with patch("vista.menu_inicio.guardar_personaje"), \
             patch.object(v.recursos, "_original_jugador", side_effect=AssertionError("Recargo retrato")):
            for nombre in ("tigresa", "jugador", "tigresa"):
                menu.elegir_personaje(nombre)
                self.assertEqual(v.recursos.personaje, nombre)
                self.assertEqual(tuple(menu.imagenes[1:]), retratos)
        for item in (menu.selector_personaje, menu.controles):
            self.assertGreaterEqual(item.winfo_y(), 0)
            self.assertLessEqual(item.winfo_y()+item.winfo_height(), menu.panel.winfo_height())
