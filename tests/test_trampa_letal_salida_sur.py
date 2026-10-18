import tkinter as tk
import unittest
from dataclasses import replace

from modelo.snapshots import EnemigoVista, SalidaVista
from modelo.tipos import Trampa
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica


class TestTrampaLetal(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor
        self.motor.sala_salida = None
        self.motor.salas[1].salidas["E"]["cerrada"] = False
        self.trampa = Trampa("t1", "trampa")
        self.motor.salas[2].trampas = [self.trampa]
        self.ficha = next(f for f in self.datos.fichas if f.id == "trampa")
        self.ficha.atributos["veneno"] = {"dano_por_pulso": 2}

    def test_trampa_letal_no_aplica_veneno_pero_queda_desarmada(self):
        self.motor.jugador.vida = 1
        self.assertTrue(self.motor.ejecutar("mover", "E").ok)
        self.assertEqual(self.motor.resultado, "derrota")
        self.assertEqual(self.motor.jugador.vida, 0)
        self.assertIsNone(self.motor.jugador.veneno)
        self.assertFalse(self.trampa.armada)
        self.assertEqual([e.tipo for e in self.motor.cola.pendientes()], ["rearmar_trampa"])

    def test_trampa_letal_cancela_veneno_anterior_y_no_lo_reaplica(self):
        self.motor.efectos.aplicar_veneno(self.motor.jugador, 2)
        anteriores = (self.motor.jugador.veneno.evento_pulso, self.motor.jugador.veneno.evento_fin)
        self.motor.jugador.vida = 1
        self.assertTrue(self.motor.ejecutar("mover", "E").ok)
        self.assertIsNone(self.motor.jugador.veneno)
        self.assertTrue(all(e.cancelado for e in anteriores))
        self.assertFalse(any(e.tipo in ("pulso_veneno", "fin_veneno") for e in self.motor.cola.pendientes()))

    def test_trampa_no_letal_conserva_veneno_antidoto_y_rearme(self):
        self.datos._inventario("antidoto")
        self.assertTrue(self.motor.ejecutar("mover", "E").ok)
        self.assertEqual(self.motor.jugador.vida, 24)  # 4 de golpe y un pulso de 2 en t=80.
        self.assertEqual(self.motor.jugador.veneno.intervalo, 80)
        self.assertEqual(self.motor.jugador.veneno.tiempo_fin, 400)
        self.assertTrue(self.motor.ejecutar("usar", "antidoto").ok)
        for _ in range(3):
            self.assertTrue(self.motor.ejecutar("esperar").ok)
        self.assertEqual(self.motor.jugador.vida, 24)
        self.assertIsNone(self.motor.jugador.veneno)
        self.assertTrue(self.trampa.armada)

    def test_muerte_detiene_las_demas_trampas_de_la_sala(self):
        segunda = Trampa("t2", "trampa")
        self.motor.salas[2].trampas.append(segunda)
        self.motor.jugador.vida = 1
        self.assertTrue(self.motor.ejecutar("mover", "E").ok)
        self.assertTrue(segunda.armada)
        self.assertEqual(len(self.motor.cola.pendientes()), 1)
        self.assertIsNone(self.motor.jugador.veneno)


class TestSalidaSurSinSolapamiento(unittest.TestCase):
    def test_sur_no_tapa_enemigos_ni_barras_al_redimensionar(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(vista.cerrar)
        datos = base.TestRegresionesJuego()
        datos.setUp()
        antes = datos.motor.exportar_estado()
        for geometria in ("1100x760", "1280x850", "1600x900"):
            vista.root.geometry(geometria)
            vista.root.update()
            for cantidad in (0, 1, 2, 4, 5, 8, 9):
                with self.subTest(geometria=geometria, enemigos=cantidad):
                    estado = replace(datos.motor.estado_vista(), salidas=[SalidaVista("S", 2, False)],
                        enemigos=[EnemigoVista(str(i), f"Rata gigante #{i + 1}", 12, 12,
                                               tipo="ent_rata_gigante") for i in range(cantidad)])
                    vista.mostrar_estado(estado, [])
                    vista.root.update()
                    c = vista.canvas
                    puerta = c.bbox("puerta_S")
                    self.assertIsNotNone(puerta)
                    for i in range(min(8, cantidad)):
                        enemigo = c.bbox(f"enemigo_{i}")
                        self.assertFalse(puerta[0] < enemigo[2] and puerta[2] > enemigo[0]
                                         and puerta[1] < enemigo[3] and puerta[3] > enemigo[1])
                    self.assertLess(puerta[3], c.winfo_height() - 82)
                    for item in c.find_all():
                        if c.type(item) == "text" and c.itemcget(item, "text").startswith("Jugador  "):
                            self.assertLessEqual(c.bbox(item)[3], puerta[1] - 2)
                    if cantidad:
                        vista._cola.clear()
                        c.event_generate("<Motion>", x=(puerta[0] + puerta[2]) // 2,
                                         y=(puerta[1] + puerta[3]) // 2)
                        c.event_generate("<Button-1>", x=(puerta[0] + puerta[2]) // 2,
                                         y=(puerta[1] + puerta[3]) // 2)
                        vista.root.update()
                        self.assertEqual(vista._cola, ["mover S"])
                        vista._ultimo_clic = ("", 0)
        self.assertEqual(datos.motor.exportar_estado(), antes)
