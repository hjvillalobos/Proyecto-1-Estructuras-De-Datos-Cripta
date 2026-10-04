import unittest

from utilidades.bench_cache import crear_carga, comparar, ESCENARIOS
from utilidades.bench_persistencia import medir_recuperacion


class TestMedicionesCache(unittest.TestCase):
    def test_recuperacion_desalojadas_sin_red(self):
        muestras = medir_recuperacion(3, 10, 2)
        self.assertEqual(len(muestras), 2)
        self.assertTrue(all(valor > 0 for valor in muestras))

    def test_cargas_reproducibles(self):
        for escenario in ESCENARIOS:
            self.assertEqual(crear_carga(25, 100, escenario, 42),
                             crear_carga(25, 100, escenario, 42))

    def test_mismos_resultados_y_conteos(self):
        for escenario in ESCENARIOS:
            with self.subTest(escenario=escenario):
                binaria, lineal = comparar(25, 100, 2, 42, escenario)
                self.assertEqual((binaria.aciertos, binaria.fallos, binaria.inserciones),
                                 (lineal.aciertos, lineal.fallos, lineal.inserciones))
                self.assertEqual(binaria.aciertos + binaria.fallos + binaria.inserciones, 100)
                self.assertEqual(len(binaria.ns_por_operacion), 2)
                if escenario == "aciertos":
                    self.assertEqual(binaria.aciertos, 100)
                elif escenario == "fallos":
                    self.assertEqual(binaria.fallos, 100)
                elif escenario == "mixta_90_10":
                    self.assertEqual((binaria.aciertos, binaria.fallos), (90, 10))
                else:
                    self.assertEqual(binaria.inserciones, 5 if escenario == "rotacion_95_5" else 50)
