import unittest
import tkinter as tk
from copy import deepcopy
from unittest.mock import Mock

from vista.animacion import AnimacionEscena
from vista.grafica import VistaGrafica
from tests import test_regresiones_juego as base


class TestAnimacion(unittest.TestCase):
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
