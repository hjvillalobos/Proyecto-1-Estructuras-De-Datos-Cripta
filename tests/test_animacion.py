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
