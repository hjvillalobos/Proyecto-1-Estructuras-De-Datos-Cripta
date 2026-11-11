"""C40/C41: comprobar el diagnóstico, no certificar tiempos del juego."""
import unittest
from dataclasses import replace

from utilidades.bench_escenarios_rutas import generar, comparar, medir_escenario


class TestEscenariosRutas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import modelo.rutas
            import modelo.conocimiento_rutas_anterior
        except ModuleNotFoundError as error:
            if error.name not in ('modelo.rutas', 'modelo.conocimiento_rutas_anterior'):
                raise
            raise unittest.SkipTest('Ejecutar utilidades.verificar_conocimiento_rutas para comparar revisiones reales.')

    def test_c40_generacion_reproducible(self):
        for familia in ('cadena', 'alternativas', 'dirigido'):
            a, origen, destino = generar(12, 927, familia)
            b, otro_origen, otro_destino = generar(12, 927, familia)
            self.assertEqual((origen, destino), (otro_origen, otro_destino))
            self.assertEqual(a.mapa_conocido(), b.mapa_conocido())
            self.assertEqual(a._salidas, b._salidas)

    def test_c40_c41_todos_los_escenarios_conservan_resultados(self):
        for familia in ('cadena', 'alternativas', 'dirigido'):
            with self.subTest(familia=familia):
                filas = medir_escenario(12, 927, familia, 3)
                self.assertEqual(len(filas), 10)
                self.assertTrue(all(muestras and min(muestras) >= 0
                                    for _, muestras in filas))

    def test_c41_discrepancia_no_se_publica_como_medicion_valida(self):
        from modelo.conocimiento_rutas import PlanificadorConocido
        mapa, origen, destino = generar(8, 927, 'alternativas')
        real = PlanificadorConocido(mapa)

        class Incorrecto:
            def consultar(self, inicio, fin):
                return replace(real.consultar(inicio, fin), costo_total=-1)

        with self.assertRaisesRegex(AssertionError, 'Resultados distintos'):
            comparar(real, Incorrecto(), origen, destino, mapa)


if __name__ == '__main__':
    unittest.main()
