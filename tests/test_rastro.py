# tests/test_rastro.py

import unittest
from modelo.rastro import RegistroRastro, RASTRO_FRESCURA_MAX


class TestRegistroRastro(unittest.TestCase):

    def setUp(self):
        self.rastro = RegistroRastro(salas_total=5)

    def test_sala_sin_visitar_no_tiene_rastro(self):
        self.assertIsNone(self.rastro.tiempo_de(3))

    def test_marcar_y_consultar_visita(self):
        self.rastro.marcar_visita(2, 100)
        self.assertEqual(self.rastro.tiempo_de(2), 100)

    def test_es_fresco_justo_antes_del_limite(self):
        self.assertTrue(self.rastro.es_fresco(100, 100 + RASTRO_FRESCURA_MAX - 1))

    def test_es_fresco_en_el_limite_ya_no_sirve(self):
        # "400 unidades o más de antigüedad no sirve" (§2.9)
        self.assertFalse(self.rastro.es_fresco(100, 100 + RASTRO_FRESCURA_MAX))

    def test_capacidad_crece_con_ids_fuera_de_rango_inicial(self):
        self.rastro.marcar_visita(50, 10)
        self.assertEqual(self.rastro.tiempo_de(50), 10)

    def test_sala_mas_fresca_elige_la_mas_reciente(self):
        self.rastro.marcar_visita(1, 100)
        self.rastro.marcar_visita(2, 300)
        mejor = self.rastro.sala_mas_fresca([1, 2], tiempo_actual=350)
        self.assertEqual(mejor, 2)

    def test_sala_mas_fresca_empate_elige_menor_id(self):
        self.rastro.marcar_visita(3, 200)
        self.rastro.marcar_visita(1, 200)
        mejor = self.rastro.sala_mas_fresca([3, 1], tiempo_actual=250)
        self.assertEqual(mejor, 1)

    def test_sala_mas_fresca_ninguna_fresca_devuelve_none(self):
        self.rastro.marcar_visita(1, 0)
        mejor = self.rastro.sala_mas_fresca([1], tiempo_actual=1000)
        self.assertIsNone(mejor)

    def test_sala_mas_fresca_sin_rastro_devuelve_none(self):
        mejor = self.rastro.sala_mas_fresca([1, 2, 3], tiempo_actual=50)
        self.assertIsNone(mejor)


if __name__ == '__main__':
    unittest.main()
