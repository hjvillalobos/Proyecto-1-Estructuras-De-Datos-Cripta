"""Regresiones del registro tras perder y de los pixeles de la antorcha."""
import hashlib
import tempfile
import tkinter as tk
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from controlador.controlador import ControladorJuego
from datos.puntajes import RegistroPuntaje, TablaPuntajes
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica
from vista.nombre_puntaje import NombrePuntaje
from vista.recursos_graficos import Image, ImageTk
from vista.tabla_puntajes import TablaPuntajesVisual


class TestPuntajesApagado(unittest.TestCase):
    def setUp(self):
        try:
            self.v = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.v.cerrar)
        self.v.root.geometry("1100x760")
        self.v.root.update()
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()

    def test_derrota_registra_nombre_y_aparece_despues_del_decimo_puesto(self):
        v, m = self.v, self.datos.motor
        m.jugador.vida = 0
        m.terminado, m.resultado = True, "derrota"
        with tempfile.TemporaryDirectory() as carpeta:
            tabla = TablaPuntajes(str(Path(carpeta) / "puntajes.jsonl"))
            for i in range(12):
                tabla.registrar(RegistroPuntaje(f"Previo {i}", "otra", "v1", 1, 0, i, "victoria"))
            mostrar = NombrePuntaje.mostrar

            def registrar(dialogo):
                def confirmar():
                    dialogo.nombre.set("  Belén prueba  ")
                    dialogo.boton_guardar.invoke()
                v.root.after(100, confirmar)
                return mostrar(dialogo)

            with patch.object(NombrePuntaje, "mostrar", registrar), patch.object(v, "mostrar_fin"):
                c = ControladorJuego(m, v, ruta_replay=str(Path(carpeta) / "replay.jsonl"),
                                     tabla_puntajes=tabla)
                self.assertTrue(c.iniciar())
                c._registrar_puntaje()
            ranking = TablaPuntajes(tabla.ruta).ranking()
            self.assertEqual(len(ranking), 13)
            self.assertEqual(ranking[-1].nombre, "Belén prueba")
            self.assertEqual(ranking[-1].resultado, "derrota")
            self.assertEqual(len(tabla.ranking(limite=10)), 10)
            t = TablaPuntajesVisual(v, ranking)
            try:
                self.assertEqual(len(t.tabla.get_children()), 13)
                self.assertEqual(t.tabla.item("12", "values")[1], "Belén prueba")
            finally:
                t.cerrar()

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_apagado_reemplaza_pixeles_de_reposo_y_todos_los_fotogramas(self):
        v, m = self.v, self.datos.motor
        self.datos._inventario("antorcha")
        self.assertTrue(m.ejecutar("usar", "antorcha").ok)
        for armado in (False, True):
            for accion in (None, "atacar", "mover", "usar", "caer"):
                with self.subTest(armado=armado, accion=accion):
                    v.reiniciar_presentacion()
                    def estado(encendida, muerto=False):
                        return replace(m.estado_vista(), efectos=["antorcha"] if encendida else [],
                            arma_tipo="itm_daga_oxidada" if armado else None,
                            armadura_tipo="itm_coraza_cuero" if armado else None,
                            vida=0 if muerto else 30)
                    apagado = estado(False, muerto=accion == "caer")

                    def dibujar(e):
                        v.preparar_animacion(accion or "esperar")
                        v.mostrar_estado(e, [])
                        a = v.escena.animacion
                        sprite = v.canvas.find_withtag("jugador")[0]
                        fotos = []
                        for paso in (0, 6, 12, 35):
                            a.situar(paso)
                            nombre = v.canvas.itemcget(sprite, "image")
                            imagen = next(i for i in v.escena.imagenes if str(i) == nombre)
                            fotos.append(hashlib.sha256(ImageTk.getimage(imagen).tobytes()).hexdigest())
                        return fotos

                    v.mostrar_estado(replace(apagado, reloj=-1), [])
                    referencia = dibujar(apagado)
                    dibujar(estado(True))
                    self.assertTrue(v.canvas.find_withtag("antorcha_visible"))
                    self.assertEqual(dibujar(apagado), referencia)
                    self.assertFalse(v.canvas.find_withtag("antorcha_visible"))

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_duracion_real_apaga_pixeles_incluso_despues_de_cargar(self):
        v, m = self.v, self.datos.motor
        next(f for f in self.datos.fichas if f.id == "antorcha").atributos["duracion"] = 2000
        self.datos._inventario("antorcha")

        def mostrar():
            v.mostrar_estado(replace(m.estado_vista(), arma_tipo="itm_daga_oxidada",
                                    armadura_tipo="itm_coraza_cuero"), [])
            nombre = v.canvas.itemcget(v.canvas.find_withtag("jugador")[0], "image")
            imagen = next(i for i in v.escena.imagenes if str(i) == nombre)
            return hashlib.sha256(ImageTk.getimage(imagen).tobytes()).hexdigest()

        referencia = mostrar()
        self.assertTrue(m.ejecutar("usar", "antorcha").ok)
        self.assertNotEqual(mostrar(), referencia)
        m.restaurar_estado(m.exportar_estado())
        v.preparar_animacion("cargar")
        self.assertNotEqual(mostrar(), referencia)
        for _ in range(25):
            if "antorcha" not in m.estado_vista().efectos:
                break
            self.assertTrue(m.ejecutar("esperar").ok)
            mostrar()
        self.assertNotIn("antorcha", m.estado_vista().efectos)
        self.assertEqual(mostrar(), referencia)
        self.assertFalse(v.canvas.find_withtag("antorcha_visible"))

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_derrota_apaga_llama_aunque_quede_tiempo_del_efecto(self):
        v, m = self.v, self.datos.motor
        activo = replace(m.estado_vista(), efectos=["antorcha"], arma_tipo="itm_daga_oxidada")
        v.mostrar_estado(activo, [])
        self.assertTrue(v.canvas.find_withtag("antorcha_visible"))
        v.mostrar_estado(replace(activo, vida=0), [])
        self.assertFalse(v.canvas.find_withtag("antorcha_visible"))
        a = v.escena.animacion
        alto = int(min(280, max(350, v.canvas.winfo_height()) - 175) * .70)
        esperados = v.recursos.fotogramas_accion("caer", 290, alto,
            arma="itm_daga_oxidada", antorcha=False)
        self.assertEqual(a.secuencias[0][1], esperados)
        for paso in (0, 6, 18, 50):
            a.situar(paso)
            sprite = v.canvas.find_withtag("jugador")[0]
            indice = 0 if paso < 6 else 1
            self.assertEqual(v.canvas.itemcget(sprite, "image"), str(esperados[indice]))
