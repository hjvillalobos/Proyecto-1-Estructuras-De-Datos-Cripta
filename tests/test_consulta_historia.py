"""FR-003/005/020: entradas de historia y cancelación sin acciones."""
import unittest
from unittest.mock import Mock, patch

from vista.consulta_historia import ConsultaHistoria
from vista.grafica import VistaGrafica


class ConsultaHistoriaTest(unittest.TestCase):
    def test_rechaza_entradas_invalidas_y_accion_cero(self):
        dialogo = ConsultaHistoria.__new__(ConsultaHistoria)
        dialogo.numero, dialogo.modo, dialogo.error = Mock(), Mock(), Mock()
        for modo in ('tiempo', 'accion'):
            dialogo.modo.get.return_value = modo
            for texto in ('', '-1', '1.5', '#1', 'abc', '١', '9' * 19):
                with self.subTest(modo=modo, texto=texto):
                    dialogo.numero.get.return_value = texto
                    self.assertFalse(dialogo.validate())
            dialogo.numero.get.return_value = '0'
            self.assertEqual(dialogo.validate(), modo == 'tiempo')
            dialogo.numero.get.return_value = ' 3 '
            self.assertTrue(dialogo.validate())
            dialogo.apply()
            self.assertEqual(dialogo.result, '#3' if modo == 'accion' else '3')

    def test_cancelar_no_encola_y_error_restaura_estado_del_dialogo(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista.root, vista._en_menu, vista._cola = Mock(), False, []
        with patch('vista.consulta_historia.ConsultaHistoria') as crear:
            crear.return_value.result = None
            vista._pedir_historia()
            self.assertEqual(vista._cola, [])
            self.assertFalse(vista._en_menu)
            crear.side_effect = RuntimeError('fallo de ventana')
            with self.assertRaises(RuntimeError):
                vista._pedir_historia()
            self.assertFalse(vista._en_menu)
