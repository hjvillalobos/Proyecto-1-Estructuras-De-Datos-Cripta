import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests import test_regresiones_juego as base
from vista.fin_partida import FinPartida
from vista.grafica import VistaGrafica


class TestFinPartida(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.vista.cerrar)
        self.vista.root.geometry("1100x760")
        self.vista.root.update()

    def resumen(self, resultado):
        return SimpleNamespace(resultado=resultado, acciones=62, derrotados=6, reloj_final=4425)

    def pantalla(self, resultado):
        pantalla = FinPartida(self.vista, self.resumen(resultado))
        self.vista.root.update()
        self.addCleanup(lambda: pantalla.panel.destroy() if pantalla.panel.winfo_exists() else None)
        return pantalla

    def test_victoria_y_derrota_cubren_ventana_y_conservan_resumen(self):
        for resultado in ("victoria", "derrota"):
            for geometria in ("1100x760", "1280x850"):
                with self.subTest(resultado=resultado, geometria=geometria):
                    self.vista.root.geometry(geometria)
                    pantalla = self.pantalla(resultado)
                    pantalla.boton_estadisticas.invoke()
                    self.vista.root.update()
                    self.assertEqual(pantalla.panel.winfo_width(), self.vista.root.winfo_width())
                    self.assertEqual(pantalla.panel.winfo_height(), self.vista.root.winfo_height())
                    c = pantalla.canvas
                    textos = [c.itemcget(i, "text") for i in c.find_all() if c.type(i) == "text"]
                    self.assertIn(resultado.capitalize(), textos)
                    for valor in ("62", "6", "4425 u.t."):
                        self.assertIn(valor, textos)
                    for i in c.find_all():
                        if c.type(i) == "text":
                            x1, y1, x2, y2 = c.bbox(i)
                            self.assertGreaterEqual(x1, 0)
                            self.assertLessEqual(x2, c.winfo_width())
                            self.assertGreaterEqual(y1, 0)
                            self.assertLessEqual(y2, c.winfo_height())
                    for boton in pantalla.botones:
                        self.assertTrue(boton.winfo_viewable())
                        self.assertLessEqual(boton.winfo_rooty() + boton.winfo_height(),
                            pantalla.panel.winfo_rooty() + pantalla.panel.winfo_height())
                    pantalla.panel.destroy()

    def test_estadisticas_ocultas_por_defecto_y_desplegables_sin_acciones(self):
        pantalla = self.pantalla("derrota")
        def textos():
            c = pantalla.canvas
            return [c.itemcget(i, "text") for i in c.find_all() if c.type(i) == "text"]
        self.assertFalse(pantalla.estadisticas_visibles)
        self.assertNotIn("Tiempo virtual", textos())
        self.assertEqual(pantalla.boton_estadisticas.cget("text"), "Ver estadísticas")
        y_inicial = pantalla.controles.winfo_y()
        pantalla.boton_estadisticas.invoke()
        self.vista.root.update()
        self.assertIn("4425 u.t.", textos())
        self.assertGreater(pantalla.controles.winfo_y(), y_inicial)
        self.assertEqual(pantalla.boton_estadisticas.cget("text"), "Ocultar estadísticas")
        self.vista.root.geometry("1280x850")
        self.vista.root.update()
        self.assertIn("4425 u.t.", textos())
        pantalla.boton_estadisticas.focus_force()
        pantalla.boton_estadisticas.event_generate("<Return>")
        self.vista.root.update()
        self.assertFalse(pantalla.estadisticas_visibles)
        self.assertNotIn("Tiempo virtual", textos())
        self.assertFalse(pantalla.reiniciar)
        self.assertEqual(self.vista._cola, [])
        self.assertTrue(pantalla.panel.winfo_exists())

    def test_derrota_reinicia_sin_segunda_pregunta_y_sin_avanzar_motor(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        antes = datos.motor.exportar_estado()
        v = self.vista

        def elegir():
            self.assertTrue(v._en_menu)
            v._enviar("esperar")
            panel = next(p for p in v.root.winfo_children() if p.place_info())
            controles = next(h for h in panel.winfo_children() if isinstance(h, tk.Frame))
            controles.winfo_children()[0].invoke()

        v.root.after(100, elegir)
        with patch("vista.grafica.messagebox.askyesno") as pregunta:
            v.mostrar_fin(self.resumen("derrota"))
            self.assertTrue(v.preguntar_reinicio())
            pregunta.assert_not_called()
        self.assertFalse(v._en_menu)
        self.assertEqual(v._cola, [])
        self.assertEqual(datos.motor.exportar_estado(), antes)

    def test_terminar_y_escape_no_reinician(self):
        for escape in (True, False):
            pantalla = self.pantalla("derrota")
            def terminar():
                if escape:
                    self.vista.root.focus_force()
                    self.vista.root.event_generate("<Escape>")
                else:
                    pantalla.botones[-1].invoke()
            self.vista.root.after(100, terminar)
            self.assertFalse(pantalla.mostrar())
            self.assertFalse(pantalla.panel.winfo_exists())
            self.assertEqual(self.vista._cola, [])

    def test_volver_menu_en_victoria_y_derrota(self):
        for resultado in ("victoria", "derrota"):
            pantalla = self.pantalla(resultado)
            boton = next(b for b in pantalla.botones
                         if b.cget("text") == "Volver al menú principal")
            self.vista.root.after(50, boton.invoke)
            self.assertFalse(pantalla.mostrar())
            self.assertTrue(pantalla.volver_menu)
            self.assertFalse(pantalla.reiniciar)
            self.assertEqual(self.vista._cola, [])

    def test_aplicacion_regresa_al_menu_y_permite_otra_partida(self):
        from controlador.aplicacion import ejecutar_juego
        from unittest.mock import Mock
        for resultado in ("victoria", "derrota"):
            with self.subTest(resultado=resultado):
                vista = Mock(spec=VistaGrafica)
                vista.mostrar_menu.side_effect = [("jugar", None), ("jugar", None)]
                vista.preguntar_menu_principal.side_effect = [True, False]
                vista.preguntar_reinicio.return_value = False
                sesion = Mock()
                args = SimpleNamespace(gui=True, semilla=42, cripta="prueba")
                with patch("vista.grafica.VistaGrafica", return_value=vista), \
                        patch("modelo.juego.crear_juego", return_value=SimpleNamespace(resultado=resultado)) as crear, \
                        patch("controlador.controlador.ControladorJuego") as controlador:
                    self.assertEqual(ejecutar_juego(args, sesion, Mock()), 0)
                self.assertEqual(vista.mostrar_menu.call_count, 2)
                self.assertEqual(crear.call_count, 2)
                self.assertEqual(controlador.return_value.iniciar.call_count, 2)
                vista.reiniciar_presentacion.assert_called_once()
                sesion.renovar.assert_called_once_with(tolerar_error=True)
                vista.cerrar.assert_called_once()

    def test_replay_no_ofrece_reinicio(self):
        self.vista._en_replay = True
        pantalla = self.pantalla("derrota")
        self.assertFalse(pantalla.permite_reinicio)
        self.assertEqual([b.cget("text") for b in pantalla.botones], ["Cerrar replay"])
        pantalla.elegir(True)
        self.assertFalse(pantalla.reiniciar)

    def test_cerrar_ventana_durante_resultado(self):
        self.vista.root.after(100, self.vista.cerrar)
        self.vista.mostrar_fin(self.resumen("derrota"))
        self.assertTrue(self.vista._cerrada)
        self.assertFalse(self.vista.preguntar_reinicio())
