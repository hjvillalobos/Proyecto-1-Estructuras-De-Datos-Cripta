import tkinter as tk
import unittest
from dataclasses import replace
from unittest.mock import Mock

from controlador.controlador import ControladorJuego
from modelo.snapshots import EnemigoVista
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica
from vista.recursos_graficos import Image, ImageTk


@unittest.skipIf(Image is None, "Pillow no disponible")
class TestGestosIntegrados(unittest.TestCase):
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

    def test_el_puno_sustituye_las_garras_abiertas_no_solo_superpone_el_arma(self):
        from vista.equipo_visual import armar_jugador
        r = self.vista.recursos
        with Image.open(r.carpeta / "jugador.png") as origen:
            original = origen.convert("RGBA")
        antes = original.tobytes()
        daga = r._arma_jugador("itm_daga_oxidada")
        # Sin hoja visible: una mera superposicion dejaria todas las garras intactas.
        daga = Image.new("RGBA", daga.size)
        cerrado = armar_jugador(original, daga, r._puno_jugador())
        zona = tuple(int(v * (original.width if i % 2 == 0 else original.height))
                     for i, v in enumerate((.79, .615, .86, .655)))
        alfa_antes = sum(original.crop(zona).getchannel("A").tobytes())
        alfa_despues = sum(cerrado.crop(zona).getchannel("A").tobytes())
        self.assertGreater(alfa_antes, 0)
        self.assertLess(alfa_despues, alfa_antes * .75)
        self.assertEqual(original.tobytes(), antes)
        self.assertIs(r._puno_jugador(), r._puno_jugador())

    def test_recoger_objeto_no_devuelve_la_daga_a_la_mano_abierta(self):
        self.datos._suelo("pocion")
        v, motor = self.vista, self.datos.motor
        inicial = motor.estado_vista()
        antes = replace(inicial, arma_tipo="itm_daga_oxidada",
                        objetos_suelo=[replace(o, tipo="itm_pocion_menor") for o in inicial.objetos_suelo])
        v.mostrar_estado(antes, [])
        self.assertTrue(motor.ejecutar("recoger", "pocion").ok)
        v.preparar_animacion("recoger")
        v.mostrar_estado(replace(motor.estado_vista(), arma_tipo="itm_daga_oxidada"), [])
        self.assertEqual(v.canvas.find_withtag("arma_visible"), v.canvas.find_withtag("jugador"))
        self.assertTrue(v.canvas.find_withtag("objeto_recogido"))
        jugador = v.canvas.find_withtag("jugador")[0]
        v.escena.animacion.situar(45)
        self.assertNotEqual(v.canvas.itemcget(jugador, "state"), "hidden")

    def test_pocion_y_antidoto_animan_solo_la_accion_aceptada(self):
        for tipo in ("pocion", "antidoto"):
            with self.subTest(tipo=tipo):
                v, motor = self.vista, self.datos.motor
                self.datos._inventario(tipo)
                v.mostrar_estado(motor.estado_vista(), [])
                v.mostrar_inventario(motor.inventario_vista())
                controlador = ControladorJuego(motor, v)
                controlador.bitacora_replay = Mock()
                self.assertTrue(controlador._accion_modelo("usar", tipo))
                despues = motor.exportar_estado()
                v.mostrar_estado(motor.estado_vista(), [])
                self.assertEqual(v.escena._accion_en_curso, "beber")
                animacion = v.escena.animacion
                self.assertEqual(len(animacion.secuencias), 1)
                animacion.situar(12)
                self.assertEqual(motor.exportar_estado(), despues)
                animacion.situar(32)
                self.assertEqual(motor.exportar_estado(), despues)
                self.assertFalse(controlador._accion_modelo("usar", tipo))
                self.assertEqual(motor.exportar_estado(), despues)
                v.var_movimiento.set(False)
                v._alternar_movimiento()
                self.assertIsNone(v.escena.animacion)
                v.var_movimiento.set(True)
                v._alternar_movimiento()

    def test_daga_integrada_con_ropa_y_reflejo(self):
        r = self.vista.recursos
        desnudo = r.fotogramas_jugador(290, 196, armadura="itm_coraza_cuero")
        armado = r.fotogramas_jugador(290, 196, armadura="itm_coraza_cuero", arma="itm_daga_oxidada")
        reflejo = r.fotogramas_jugador(290, 196, invertir=True,
                                      armadura="itm_coraza_cuero", arma="itm_daga_oxidada")
        for antes, despues, inverso in zip(desnudo, armado, reflejo):
            antes, despues, inverso = map(ImageTk.getimage, (antes, despues, inverso))
            self.assertNotEqual(antes.tobytes(), despues.tobytes())
            self.assertEqual(despues.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(), inverso.tobytes())
        estado = replace(self.datos.motor.estado_vista(), arma_tipo="itm_daga_oxidada",
                         armadura_tipo="itm_coraza_cuero")
        self.vista.mostrar_estado(estado, [])
        self.assertEqual(self.vista.canvas.find_withtag("arma_visible"),
                         self.vista.canvas.find_withtag("jugador"))

    def test_bebidas_cacheadas_y_color_solo_cambia_el_liquido(self):
        r = self.vista.recursos
        pocion = r.pose_beber(196, "itm_coraza_cuero")
        antidoto = r.pose_beber(196, "itm_coraza_cuero", antidoto=True)
        self.assertIs(r.pose_beber(196, "itm_coraza_cuero"), pocion)
        pocion, antidoto = ImageTk.getimage(pocion), ImageTk.getimage(antidoto)
        self.assertEqual(pocion.size, antidoto.size)
        self.assertNotEqual(pocion.tobytes(), antidoto.tobytes())
        self.assertEqual(pocion.getchannel("A").tobytes(), antidoto.getchannel("A").tobytes())
        self.assertEqual(pocion.crop((0, 40, pocion.width, pocion.height)).tobytes(),
                         antidoto.crop((0, 40, antidoto.width, antidoto.height)).tobytes())
        for alto in (140, 150, 160, 180, 196):
            self.assertIsNotNone(r.pose_beber(alto))
        self.assertLessEqual(len(r._bebidas), 4)

    def test_rata_mas_pequena_que_humanoide_y_ambos_sobre_el_suelo(self):
        v = self.vista
        estado = replace(self.datos.motor.estado_vista(), enemigos=[
            EnemigoVista("r", "Rata gigante", 12, 12, tipo="ent_rata_gigante"),
            EnemigoVista("g", "Guardian oseo", 30, 30, tipo="ent_guardian_oseo")])
        v.mostrar_estado(estado, [])
        actores = [next(i for i in v.canvas.find_withtag(f"enemigo_{n}") if v.canvas.type(i) == "image")
                   for n in (0, 1)]
        alturas = [int(v.root.tk.call("image", "height", v.canvas.itemcget(i, "image"))) for i in actores]
        self.assertLess(alturas[0], alturas[1] * .65)
        for actor in actores:
            self.assertAlmostEqual(v.canvas.coords(actor)[1], v._jugador_xy[1], delta=2)
