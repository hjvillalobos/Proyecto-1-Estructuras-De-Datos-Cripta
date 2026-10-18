import tkinter as tk
import unittest
from threading import Event
from unittest.mock import Mock, patch

from tests import test_regresiones_juego as base
from tests.test_criptas_api import CRIPTAS
from vista.grafica import VistaGrafica
from vista.menu_inicio import MenuInicio
from vista.selector_cripta import SelectorCripta


class TestTransicionInicio(unittest.TestCase):
    def setUp(self):
        self.v = VistaGrafica()
        self.addCleanup(self.v.cerrar)
        self.v.root.geometry("1100x760")
        self.v.root.update()

    def iniciar(self, accion="jugar"):
        menu = MenuInicio(self.v, Mock(), Mock())
        self.v.root.after(20, lambda: menu.elegir(accion, "partida.bin" if accion == "cargar" else None))
        self.assertEqual(menu.mostrar()[0], accion)
        self.assertIs(self.v._inicio_en_carga, menu)
        self.assertTrue(menu.panel.winfo_exists())
        self.assertFalse(menu.controles.place_info())
        self.assertEqual(menu.canvas.itemcget("subtitulo", "text"), "Cargando…")
        return menu

    def test_jugar_selector_y_carga_lenta_conservan_fondo_hasta_primera_sala(self):
        menu = self.iniciar()
        selector = SelectorCripta(self.v, CRIPTAS)
        self.v.root.after(20, selector.aceptar)
        self.assertEqual(selector.mostrar(), "cripta-01")
        self.assertTrue(menu.panel.winfo_exists())
        liberar = Event()
        observaciones = []
        def durante_carga():
            observaciones.append(menu.panel.winfo_ismapped())
            self.v._enviar("mover N")
            liberar.set()
        self.v.root.after(20, durante_carga)
        self.assertTrue(self.v.ejecutar_tarea(liberar.wait, 2))
        self.assertEqual(observaciones, [1])
        self.assertEqual(self.v._cola, [])
        datos = base.TestRegresionesJuego()
        datos.setUp()
        with patch.object(self.v, "_dibujar_sala", wraps=self.v._dibujar_sala) as dibujar:
            self.v.mostrar_estado(datos.motor.estado_vista(), [])
        dibujar.assert_called_once()
        self.assertIsNone(self.v._inicio_en_carga)
        self.assertFalse(menu.panel.winfo_exists())
        self.assertTrue(self.v.canvas.find_withtag("jugador"))

    def test_cargar_y_reintentar_reemplaza_la_capa_sin_acumularla(self):
        anterior = self.iniciar("cargar")
        nuevo = MenuInicio(self.v, Mock(), Mock())
        self.v.root.after(20, lambda: nuevo.elegir("salir"))
        with patch("vista.menu_inicio.MenuInicio", return_value=nuevo):
            self.assertEqual(self.v.mostrar_menu(Mock(), Mock()), ("salir", None))
        self.assertFalse(anterior.panel.winfo_exists())
        self.assertIsNone(self.v._inicio_en_carga)

    def test_salir_no_conserva_una_capa_de_carga(self):
        menu = MenuInicio(self.v, Mock(), Mock())
        self.v.root.after(20, lambda: menu.elegir("salir"))
        self.assertEqual(menu.mostrar(), ("salir", None))
        self.assertIsNone(self.v._inicio_en_carga)
        self.assertFalse(menu.panel.winfo_exists())
