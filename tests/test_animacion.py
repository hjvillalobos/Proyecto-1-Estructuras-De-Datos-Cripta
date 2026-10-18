import unittest
import tkinter as tk
from copy import deepcopy
from unittest.mock import Mock

from vista.animacion import AnimacionEscena
from vista.escena import EscenaCripta
from vista.recursos_graficos import RecursosGraficos
from types import SimpleNamespace
from unittest.mock import patch
from vista.grafica import VistaGrafica
from tests import test_regresiones_juego as base


class TestAnimacion(unittest.TestCase):
    def test_redibujar_menu_crea_animacion_nueva_y_destruirlo_la_cancela(self):
        from vista.menu_inicio import MenuInicio
        vista = VistaGrafica()
        self.addCleanup(vista.cerrar)
        vista.root.withdraw()
        menu = MenuInicio(vista, Mock(), Mock())
        menu.dibujar()
        anterior = menu.animacion
        menu.dibujar()
        self.assertIsNot(menu.animacion, anterior)
        self.assertTrue(anterior._detenida)
        self.assertIsNone(anterior.pendiente)
        self.assertIsNotNone(menu.animacion.pendiente)
        self.assertFalse(menu.animacion._detenida)
        menu.panel.destroy()
        self.assertIsNone(menu.animacion.pendiente)
        self.assertTrue(menu.animacion._detenida)

    def test_destruir_canvas_con_callback_pendiente_no_produce_error(self):
        root = tk.Tk()
        self.addCleanup(root.destroy)
        root.withdraw()
        canvas = tk.Canvas(root)
        sprite = canvas.create_rectangle(0, 0, 10, 10)
        animacion = AnimacionEscena(root, canvas)
        animacion.agregar(sprite)
        animacion.particula(canvas.create_line(0, 0, 10, 10))
        animacion.decorar(SimpleNamespace(actualizar=Mock(), detener=Mock()))
        animacion.recorrer(sprite, (20, 20), al_llegar=Mock())
        errores = []
        root.report_callback_exception = lambda *error: errores.append(error)
        animacion.iniciar()
        canvas.destroy()
        root.after(60, root.quit)
        root.mainloop()
        self.assertEqual(errores, [])
        self.assertIsNone(animacion.pendiente)
        self.assertEqual(animacion.actores, [])
        self.assertEqual(animacion.particulas, [])
        self.assertEqual(animacion.decoraciones, [])
        self.assertIsNone(animacion._al_llegar)
        animacion.detener()  # Tambien debe poder limpiarse despues del destroy.

    def test_callback_tardio_de_animacion_cancelada_no_toca_canvas(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [20, 30]
        animacion = AnimacionEscena(root, canvas)
        animacion.agregar(1)
        animacion.iniciar()
        animacion.detener()
        root.reset_mock()
        canvas.reset_mock()
        animacion._avanzar()
        animacion.situar(20)
        animacion.iniciar()
        canvas.type.assert_not_called()
        canvas.coords.assert_not_called()
        root.after.assert_not_called()
        self.assertIsNone(animacion.pendiente)
        self.assertEqual(animacion.paso, 0)

    def test_detener_despues_de_destruir_root_es_seguro(self):
        root = tk.Tk()
        root.withdraw()
        canvas = tk.Canvas(root)
        animacion = AnimacionEscena(root, canvas)
        animacion.agregar(canvas.create_rectangle(0, 0, 10, 10))
        animacion.iniciar()
        root.destroy()
        animacion.detener()
        animacion._avanzar()
        self.assertIsNone(animacion.pendiente)
        self.assertEqual(animacion.actores, [])

    def test_carrera_repite_cuadros_y_se_asienta_sin_salto(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [145, 200]
        animacion = AnimacionEscena(root, canvas)
        animacion.agregar(1, entrada=True, desplazamiento=(-65, 0), carrera=True)
        animacion.secuencia(1, ["a", "b", "c", "d"], reposo="quieto",
                            pasos_por_cuadro=2, duracion=16, repetir=True)
        for _ in range(8):
            animacion._avanzar()
        canvas.itemconfig.assert_called_with(1, image="a")
        x_mitad = canvas.coords.call_args.args[1]
        self.assertGreater(x_mitad, 80)
        self.assertLess(x_mitad, 145)
        for _ in range(8):
            animacion._avanzar()
        canvas.itemconfig.assert_called_with(1, image="quieto")
        self.assertEqual(canvas.coords.call_args.args[1], 145)
        animacion.detener()

    def test_efectos_temporales_se_eliminan_al_terminar_o_cancelar(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [20, 30, 28, 30]
        animacion = AnimacionEscena(root, canvas)
        animacion.particula(7, duracion=2)
        animacion.iniciar()
        root.after.assert_called_once_with(20, animacion._avanzar)
        animacion._avanzar()
        self.assertNotEqual(canvas.coords.call_args.args, (7, 20, 30, 28, 30))
        animacion._avanzar()
        canvas.delete.assert_called_with(7)
        animacion.detener()
        self.assertEqual(animacion.particulas, [])
        self.assertIsNone(animacion.pendiente)

    def test_redibujar_preserva_progreso_y_no_modifica_el_motor(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.withdraw()
            inicial = datos.motor.estado_vista()
            vista.mostrar_estado(inicial, [])
            estado = deepcopy(inicial)
            estado.sala_id = 2
            estado.reloj = 100
            vista.preparar_animacion("mover")
            vista.mostrar_estado(estado, [])
            antes = datos.motor.exportar_estado()
            for _ in range(5):
                # Pasos manuales: cancelar el callback anterior evita duplicarlo.
                a = vista.escena.animacion
                vista.root.after_cancel(a.pendiente)
                a.pendiente = None
                a._avanzar()
            vista._redimensionar()
            self.assertEqual(vista.escena.animacion.paso, 5)
            self.assertEqual(vista.escena._accion_en_curso, "correr")
            self.assertEqual(datos.motor.exportar_estado(), antes)
            self.assertEqual(vista._cola, [])
            vista.var_movimiento.set(False)
            vista._alternar_movimiento()
            self.assertIsNone(vista.escena.animacion)
            self.assertEqual(vista.canvas.find_withtag("efecto_visual"), ())
        finally:
            vista.cerrar()

    def test_secuencia_avanza_y_vuelve_a_reposo(self):
        root, canvas = Mock(), Mock()
        animacion = AnimacionEscena(root, canvas)
        animacion.secuencia(1, ["paso1", "paso2"], reposo="quieto")
        canvas.itemconfig.assert_called_with(1, image="paso1")
        for _ in range(3):
            animacion._avanzar()
        canvas.itemconfig.assert_called_with(1, image="paso2")
        for _ in range(3):
            animacion._avanzar()
        canvas.itemconfig.assert_called_with(1, image="quieto")
        animacion.secuencia(2, ["caida", "suelo"], mantener=True)
        animacion._avanzar()
        canvas.itemconfig.assert_called_with(2, image="suelo")
        animacion.detener()
        self.assertEqual(animacion.secuencias, [])

    def test_acciones_visuales_no_confunden_dano_automatico_con_ataque(self):
        vista = SimpleNamespace(_accion_visual=None)
        escena = EscenaCripta(vista)
        escena.anterior = SimpleNamespace(vida=30, sala_id=1, reloj=0)
        estado = SimpleNamespace(vida=30, sala_id=1, reloj=100)
        self.assertIsNone(escena._accion_jugador(estado))
        vista._accion_visual = "atacar"
        self.assertEqual(escena._accion_jugador(estado), "atacar")
        estado.sala_id = 2
        self.assertEqual(escena._accion_jugador(estado), "correr")
        vista._accion_visual = "cargar"
        self.assertIsNone(escena._accion_jugador(estado))
        estado.vida = 0
        self.assertEqual(escena._accion_jugador(estado), "caer")

    def test_hoja_carga_o_utiliza_respaldo_sin_pillow(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            root.withdraw()
            recursos = RecursosGraficos(root)
            cuadros = recursos.fotogramas_jugador(290, 280)
            self.assertEqual(len(cuadros), 8)
            self.assertIs(recursos.fotogramas_jugador(290, 280), cuadros)
            for imagen in cuadros:
                self.assertLessEqual(imagen.width(), 290)
                self.assertLessEqual(imagen.height(), 280)
            with patch("vista.recursos_graficos.Image", None):
                self.assertEqual(recursos.fotogramas_jugador(100, 100), ())
        finally:
            root.destroy()

    def test_un_solo_callback_y_cancelacion_restaura_posicion(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [20, 30]
        animacion = AnimacionEscena(root, canvas)
        animacion.agregar(1, entrada=True, golpe=True)
        animacion.iniciar()
        animacion.iniciar()
        root.after.assert_called_once()
        animacion._avanzar()
        self.assertNotEqual(canvas.coords.call_args.args, (1, 20, 30))
        animacion.detener()
        canvas.coords.assert_called_with(1, 20, 30)
        self.assertEqual(animacion.actores, [])
        self.assertIsNone(animacion.pendiente)

    def test_animacion_real_no_cambia_motor_ni_acciones(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.withdraw()
            estado = deepcopy(datos.motor.exportar_estado())
            vista.mostrar_estado(datos.motor.estado_vista(), [])
            sprite = next(i for i in vista.canvas.find_withtag("jugador") if vista.canvas.type(i) == "image")
            origen = vista.canvas.coords(sprite)
            vista.root.after(180, vista.root.quit)
            vista.root.mainloop()
            self.assertNotEqual(origen, vista.canvas.coords(sprite))
            self.assertEqual(datos.motor.exportar_estado(), estado)
            self.assertEqual(vista._cola, [])
            vista.var_movimiento.set(False)
            vista._alternar_movimiento()
            self.assertIsNone(vista.escena.animacion)
            self.assertEqual(datos.motor.exportar_estado(), estado)
            vista.reiniciar_presentacion()
            self.assertIsNone(vista.escena.anterior)
        finally:
            vista.cerrar()

    def test_flechas_generan_un_comando_por_pulsacion(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista.root = Mock()
        vista.root.focus_get.return_value = None
        vista._cola, vista._cerrada, vista._en_replay = [], False, False
        vista._atar_teclas()
        bindings = {c.args[0]: c.args[1] for c in vista.root.bind.call_args_list}
        for tecla in ("Up", "Down", "Left", "Right"):
            bindings[f"<{tecla}>"](None)
        self.assertEqual(vista._cola, ["mover N", "mover S", "mover O", "mover E"])
