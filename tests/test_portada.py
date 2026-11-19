import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from vista.portada import Portada
from vista.grafica import VistaGrafica


class TestPortada(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.geometry("960x600")
        self.addCleanup(self.root.destroy)

    def mostrar_portada(self, portada):
        limite = self.root.after(5000, portada.salir)
        try:
            return portada.mostrar()
        finally:
            self.root.after_cancel(limite)

    def test_enter_se_consume_y_libera_recursos(self):
        portada = Portada(self.root)
        recibidos = []
        self.root.bind("<KeyRelease-Return>", lambda evento: recibidos.append(evento))
        def pulsar():
            portada.canvas.focus_force()
            portada.canvas.event_generate("<KeyRelease-Return>")
        self.root.after(200, pulsar)
        self.assertTrue(self.mostrar_portada(portada))
        self.assertEqual(recibidos, [])
        self.assertIsNone(portada.pendiente)
        self.assertIsNone(portada.redimension)
        self.assertEqual(portada.imagenes, [])
        self.assertEqual(portada.originales, [])

    def test_cerrar_devuelve_salir_y_restaura_protocolo(self):
        anterior = self.root.protocol("WM_DELETE_WINDOW")
        portada = Portada(self.root)
        self.root.after(200, portada.salir)
        self.assertFalse(self.mostrar_portada(portada))
        self.assertEqual(self.root.protocol("WM_DELETE_WINDOW"), anterior)
        self.assertIsNone(portada.pendiente)

    def test_clic_izquierdo_inicia_con_transicion(self):
        portada = Portada(self.root)
        self.root.after(200, lambda: portada.canvas.event_generate("<ButtonRelease-1>", x=100, y=100))
        self.assertTrue(self.mostrar_portada(portada))
        self.assertIsNone(portada.pendiente)

    def test_redimension_conserva_proporcion(self):
        portada = Portada(self.root)
        def comprobar():
            self.assertEqual(portada.imagenes[0].width(), 960)
            self.assertEqual(portada.imagenes[0].height(), 540)
            portada.entrar()
        self.root.after(200, comprobar)
        self.assertTrue(self.mostrar_portada(portada))

    def test_cerrar_durante_desvanecimiento_cancela_inicio(self):
        portada = Portada(self.root)
        def comenzar():
            portada.entrar()
            transicion = portada.transicion
            portada.entrar()
            self.assertIs(portada.transicion, transicion)
            self.assertFalse(portada.fin.get())
            self.root.after(100, portada.salir)
        self.root.after(200, comenzar)
        self.assertFalse(self.mostrar_portada(portada))
        self.assertIsNone(portada.pendiente)
        self.assertIsNone(portada.imagen_transicion)

    def test_menu_solo_muestra_portada_una_vez(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista.root = self.root
        vista.sonidos = Mock()
        vista._inicio_en_carga = None
        with patch("vista.portada.Portada") as portada, patch("vista.menu_inicio.MenuInicio") as menu:
            portada.return_value.mostrar.return_value = True
            menu.return_value.mostrar.return_value = ("salir", None)
            self.assertEqual(vista.mostrar_menu(Mock(), Mock()), ("salir", None))
            vista.sonidos.reproducir.assert_called_once_with("inicio")
            menu.return_value.mostrar.assert_called_once_with(reproducir_inicio=False)
            self.assertEqual(vista.mostrar_menu(Mock(), Mock()), ("salir", None))
            menu.return_value.mostrar.assert_called_with(reproducir_inicio=True)
            portada.assert_called_once_with(self.root)
            self.assertEqual(menu.call_count, 2)
