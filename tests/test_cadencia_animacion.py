import unittest
from unittest.mock import Mock, patch

from vista.animacion import AnimacionEscena


class TestCadenciaAnimacion(unittest.TestCase):
    def test_compensa_retrasos_sin_cambiar_los_pasos(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [0, 0]
        a = AnimacionEscena(root, canvas)
        a.agregar(1)
        with patch("vista.animacion.perf_counter", return_value=0) as reloj:
            a.iniciar()
            self.assertEqual(root.after.call_args.args[0], 20)
            reloj.return_value = .030  # Windows despacho el primer callback tarde.
            a._avanzar()
            self.assertEqual(a.paso, 1)
            self.assertEqual(root.after.call_args.args[0], 10)
            reloj.return_value = 1  # Una pausa larga no debe causar una rafaga.
            a._avanzar()
            self.assertEqual(a.paso, 2)
            self.assertEqual(root.after.call_args.args[0], 20)
        a.detener()
        self.assertIsNone(a._siguiente_tic)
        self.assertIsNone(a.pendiente)
