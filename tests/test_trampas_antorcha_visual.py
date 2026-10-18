import tempfile
import tkinter as tk
import unittest
from dataclasses import replace
from pathlib import Path

from datos.guardado_binario import guardar_estado, cargar_estado
from modelo.snapshots import TrampaVista
from modelo.tipos import Trampa
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica
from vista.recursos_graficos import Image, ImageTk


class TestActivacionesTrampas(unittest.TestCase):
    def test_informa_activacion_aunque_la_trampa_se_rearme_antes_del_turno(self):
        d = base.TestRegresionesJuego()
        d.setUp()
        m = d.motor
        m.sala_salida = None
        m.salas[1].salidas["E"]["cerrada"] = False
        ficha = next(f for f in d.fichas if f.id == "trampa")
        ficha.atributos["rearme"] = 20
        m.salas[2].trampas = [Trampa("t1", "trampa"), Trampa("t2", "trampa", armada=False)]
        resultado = m.ejecutar("mover", "E")
        self.assertTrue(resultado.ok)
        self.assertEqual(resultado.trampas_activadas, ["t1"])
        self.assertTrue(m.salas[2].trampas[0].armada)
        self.assertEqual(m.jugador.vida, 26)
        self.assertEqual(m.ejecutar("esperar").trampas_activadas, [])
        self.assertEqual(m.ejecutar("mover", "N").trampas_activadas, [])


class TestTrampasAntorchaVisual(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.vista.cerrar)
        self.vista.root.geometry("1100x760")
        self.vista.root.update()
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()

    def test_todas_las_trampas_visibles_animan_y_limpian_sus_efectos(self):
        v, m = self.vista, self.datos.motor
        estado = replace(m.estado_vista(), trampas=[
            TrampaVista("t1", "Dardos", False, 4, tipo="trp_dardos"),
            TrampaVista("t2", "Otra trampa", False, 2, tipo="tipo_desconocido")])
        antes = m.exportar_estado()
        v.preparar_animacion("mover")
        v.preparar_trampas(["t1", "t2"])
        v.mostrar_estado(estado, [])
        self.assertTrue(v.canvas.find_withtag("trampa_t1"))
        self.assertTrue(v.canvas.find_withtag("trampa_t2"))
        self.assertTrue(v.canvas.find_withtag("disparo_t1"))
        self.assertTrue(v.canvas.find_withtag("disparo_t2"))
        a = v.escena.animacion
        a.situar(12)
        lineas = [i for i in v.canvas.find_withtag("efecto_trampa") if v.canvas.type(i) == "line"]
        self.assertTrue(any(v.canvas.itemcget(i, "state") == "normal" for i in lineas))
        posiciones = [v.canvas.coords(i) for i in lineas]
        a.situar(14)
        self.assertNotEqual(posiciones, [v.canvas.coords(i) for i in lineas])
        self.assertEqual(m.exportar_estado(), antes)
        a.situar(32)
        self.assertFalse(v.canvas.find_withtag("efecto_trampa"))
        v._dibujar_sala(estado)
        self.assertFalse(v.canvas.find_withtag("efecto_trampa"))
        v.preparar_animacion("cargar")
        v._dibujar_sala(estado)
        self.assertFalse(v.canvas.find_withtag("efecto_trampa"))

    def test_paginacion_muestra_trampas_independientes_sin_acciones(self):
        v = self.vista
        estado = replace(self.datos.motor.estado_vista(), trampas=[
            TrampaVista(f"t{i}", "Dardos", True, 4, tipo="trp_dardos") for i in range(10)])
        v.mostrar_estado(estado, [])
        self.assertTrue(v.canvas.find_withtag("trampa_t0"))
        self.assertFalse(v.canvas.find_withtag("trampa_t8"))
        v._cambiar_pagina("trampas", 1)
        self.assertFalse(v.canvas.find_withtag("trampa_t0"))
        self.assertTrue(v.canvas.find_withtag("trampa_t8"))
        self.assertTrue(v.canvas.find_withtag("trampa_t9"))
        self.assertEqual(v._cola, [])
        self.assertFalse(v.canvas.find_withtag("efecto_trampa"))

    def test_desactivar_movimiento_elimina_disparos(self):
        v = self.vista
        estado = replace(self.datos.motor.estado_vista(), trampas=[TrampaVista("t", "Dardos", False, 4, tipo="trp_dardos")])
        v.preparar_animacion("mover")
        v.preparar_trampas(["t"])
        v.mostrar_estado(estado, [])
        self.assertTrue(v.canvas.find_withtag("efecto_trampa"))
        v.var_movimiento.set(False)
        v._alternar_movimiento()
        self.assertFalse(v.canvas.find_withtag("efecto_trampa"))
        self.assertIsNone(v.escena.animacion)

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_antorcha_en_mano_se_apaga_carga_y_revierte_segun_el_modelo(self):
        v, m = self.vista, self.datos.motor
        self.datos._inventario("antorcha")
        self.datos._inventario("pergamino")
        self.datos._inventario("pergamino", "p2")
        self.datos._inventario("pergamino", "p3")
        v.mostrar_estado(m.estado_vista(), [])
        self.assertFalse(v.canvas.find_withtag("antorcha_visible"))
        self.assertTrue(m.ejecutar("usar", "antorcha").ok)
        estado = replace(m.estado_vista(), arma_tipo="itm_daga_oxidada")
        v.preparar_animacion("usar", "antorcha")
        v.mostrar_estado(estado, [])
        self.assertEqual(v.canvas.find_withtag("antorcha_visible"), v.canvas.find_withtag("jugador"))
        self.assertEqual(v.canvas.find_withtag("arma_visible"), v.canvas.find_withtag("jugador"))
        despues = m.exportar_estado()
        v.escena.animacion.situar(20)
        self.assertEqual(m.exportar_estado(), despues)
        v.var_movimiento.set(False)
        v._alternar_movimiento()
        self.assertTrue(v.canvas.find_withtag("antorcha_visible"))
        for _ in range(2):
            self.assertTrue(m.ejecutar("esperar").ok)
        v.mostrar_estado(m.estado_vista(), [])
        self.assertFalse(v.canvas.find_withtag("antorcha_visible"))
        for _ in range(3):
            self.assertTrue(m.ejecutar("retroceso").ok)
        v.preparar_animacion("retroceso")
        v.mostrar_estado(m.estado_vista(), [])
        self.assertFalse(v.canvas.find_withtag("antorcha_visible"))
        self.assertEqual(m.jugador.inventario.contar("antorcha"), 1)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "antorcha.bin")
            guardar_estado(despues, ruta)
            m.restaurar_estado(cargar_estado(ruta))
        v.preparar_animacion("cargar")
        v.mostrar_estado(m.estado_vista(), [])
        self.assertTrue(v.canvas.find_withtag("antorcha_visible"))

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_antorcha_conserva_agarre_al_reflejar_los_ocho_cuadros(self):
        r = self.vista.recursos
        cuadros = r.fotogramas_jugador(290, 196, arma="itm_daga_oxidada", antorcha=True)
        inversos = r.fotogramas_jugador(290, 196, invertir=True, arma="itm_daga_oxidada", antorcha=True)
        self.assertEqual(len(cuadros), 8)
        for cuadro, inverso in zip(cuadros, inversos):
            cuadro, inverso = ImageTk.getimage(cuadro), ImageTk.getimage(inverso)
            self.assertEqual(cuadro.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(), inverso.tobytes())

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_puno_antorcha_no_recorta_la_cola_con_un_rectangulo(self):
        from vista.equipo_visual import iluminar_jugador

        personaje = Image.new("RGBA", (1000, 1000), (140, 80, 30, 255))
        transparente = Image.new("RGBA", (20, 20))
        antes = personaje.tobytes()
        resultado = iluminar_jugador(personaje, transparente, transparente)
        self.assertEqual(resultado.getpixel((425, 640)), personaje.getpixel((425, 640)))
        self.assertEqual(resultado.getpixel((335, 645)), personaje.getpixel((335, 645)))
        self.assertEqual(resultado.getpixel((365, 628))[3], 0)
        self.assertEqual(personaje.tobytes(), antes)

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_llama_apunta_fuera_del_antebrazo_sin_desanclar_el_mango(self):
        from PIL import ImageDraw
        from vista.equipo_visual import iluminar_jugador, _MANOS_IZQUIERDAS

        personaje = Image.new("RGBA", (400, 400))
        antorcha = Image.new("RGBA", (100, 200))
        dibujo = ImageDraw.Draw(antorcha)
        dibujo.ellipse((28, 152, 36, 160), fill=(0, 255, 0, 255))
        dibujo.ellipse((65, 10, 85, 30), fill=(255, 0, 0, 255))
        puno = Image.new("RGBA", (20, 20))
        originales = (personaje.tobytes(), antorcha.tobytes(), puno.tobytes())
        for pose in (None, "beber", 4, 5, 6, 7):
            with self.subTest(pose=pose):
                compuesto = iluminar_jugador(personaje, antorcha, puno, pose)
                mango, llama = [], []
                for y in range(compuesto.height):
                    for x in range(compuesto.width):
                        r, g, b, a = compuesto.getpixel((x, y))
                        if a > 100 and g > 200 and r < 30:
                            mango.append((x, y))
                        if a > 100 and r > 200 and g < 30:
                            llama.append((x, y))
                self.assertTrue(mango)
                self.assertTrue(llama)
                mano = ((.38, .57) if pose is None else (.36, .60)
                        if pose == "beber" else _MANOS_IZQUIERDAS[pose])
                mx = sum(x for x, y in mango) / len(mango)
                my = sum(y for x, y in mango) / len(mango)
                self.assertAlmostEqual(mx, mano[0] * 400, delta=3)
                self.assertAlmostEqual(my, mano[1] * 400, delta=3)
                lx = sum(x for x, y in llama) / len(llama)
                if pose in (None, "beber", 4):
                    self.assertLess(lx, mx - 25)
                else:
                    self.assertGreater(lx, mx + 25)
        self.assertEqual(originales, (personaje.tobytes(), antorcha.tobytes(), puno.tobytes()))
