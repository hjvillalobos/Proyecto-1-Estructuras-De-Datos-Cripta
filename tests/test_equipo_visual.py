import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from datos.guardado_binario import guardar_estado, cargar_estado
from tests import test_regresiones_juego as base
from vista.animacion import AnimacionEscena
from vista.grafica import VistaGrafica


class TestEquipoVisual(unittest.TestCase):
    def test_snapshot_refleja_equipo_soltar_retroceso_y_carga(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        motor = datos.motor
        for tipo in ("daga", "coraza", "pergamino"):
            datos._inventario(tipo)
        motor.ejecutar("equipar", "daga")
        motor.ejecutar("equipar", "coraza")
        self.assertEqual((motor.estado_vista().arma_tipo, motor.estado_vista().armadura_tipo), ("daga", "coraza"))
        estado = motor.exportar_estado()
        motor.ejecutar("soltar", "daga")
        self.assertIsNone(motor.estado_vista().arma_tipo)
        motor.ejecutar("retroceso")
        self.assertEqual(motor.estado_vista().arma_tipo, "daga")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "equipo.bin")
            guardar_estado(estado, ruta)
            motor.ejecutar("soltar", "coraza")
            motor.restaurar_estado(cargar_estado(ruta))
        self.assertEqual((motor.estado_vista().arma_tipo, motor.estado_vista().armadura_tipo), ("daga", "coraza"))

    def test_anclajes_siguen_actor_y_recogida_desaparece(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [100, 200]
        a = AnimacionEscena(root, canvas)
        a.anclar(2, 1, (10, -20), duracion=45)
        canvas.coords.assert_called_with(2, 110, 180)
        a.anclar(3, 1, (30, -10), ocultar_hasta=45)
        canvas.itemconfig.assert_called_with(3, state="hidden")
        a.paso = 45
        a._actualizar_anclajes()
        canvas.delete.assert_called_with(2)
        canvas.itemconfig.assert_called_with(3, state="normal")
        a.detener()
        self.assertEqual(a.anclajes, [])

    def test_anclaje_cambia_con_pose_y_vuelve_al_reposo(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [100, 200]
        a = AnimacionEscena(root, canvas)
        a.secuencia(1, ["paso1", "paso2"], reposo="quieto")
        a.anclar(2, 1, (10, -20), [(20, -30), (40, -50)])
        canvas.coords.assert_called_with(2, 120, 170)
        a.paso = 3
        a._actualizar_anclajes()
        canvas.coords.assert_called_with(2, 140, 150)
        a.paso = 6
        a._actualizar_anclajes()
        canvas.coords.assert_called_with(2, 110, 180)

    def test_interfaz_equipo_y_recogida_no_alteran_simulacion(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        datos._inventario("daga")
        datos._inventario("coraza")
        datos._suelo("pocion")
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        original = vista.recursos.imagen
        equivalencias = {"daga": "itm_daga_oxidada", "coraza": "itm_coraza_cuero", "pocion": "itm_pocion_menor"}
        try:
            vista.root.withdraw()
            with patch.object(vista.recursos, "imagen", side_effect=lambda n, w, h: original(equivalencias.get(n, n), w, h)):
                datos.motor.ejecutar("equipar", "daga")
                datos.motor.ejecutar("equipar", "coraza")
                vista.mostrar_estado(datos.motor.estado_vista(), [])
                self.assertTrue(vista.canvas.find_withtag("arma_visible"))
                self.assertTrue(vista.canvas.find_withtag("armadura_visible"))
                datos.motor.ejecutar("recoger", "pocion")
                vista.preparar_animacion("recoger")
                vista.mostrar_estado(datos.motor.estado_vista(), [])
                self.assertTrue(vista.canvas.find_withtag("objeto_recogido"))
                antes = datos.motor.exportar_estado()
                vista.root.after(120, vista.root.quit)
                vista.root.mainloop()
                # El limite se prueba por pasos; la carga del equipo no altera el resultado.
                vista.escena.animacion.paso = 45
                vista.escena.animacion._actualizar_anclajes()
                self.assertFalse(vista.canvas.find_withtag("objeto_recogido"))
                arma = vista.canvas.find_withtag("arma_visible")[0]
                self.assertEqual(vista.canvas.itemcget(arma, "state"), "normal")
                self.assertEqual(datos.motor.exportar_estado(), antes)
                self.assertEqual(vista._cola, [])
                vista.var_movimiento.set(False)
                vista._alternar_movimiento()
                self.assertIsNone(vista.escena.animacion)
                self.assertTrue(vista.canvas.find_withtag("armadura_visible"))
                self.assertFalse(vista.canvas.find_withtag("objeto_recogido"))
        finally:
            vista.cerrar()
