import random
import unittest
from unittest.mock import patch

from utilidades.bench_resolubilidad import (generar_datos, medir_datos, medir_resolubilidad,
                                           validar_orden, verificar_repetitivo)
from modelo.resolubilidad import (verificar_resolubilidad, DatosVerificacion, SalaVerificacion,
                                  SalidaVerificacion, UbicacionLlave)


class TestBenchResolubilidad(unittest.TestCase):
    def test_FR015_AC19_generadores_y_oraculo(self):
        estado = random.getstate()
        for familia in ('cadena', 'ciclo', 'alternativas'):
            datos = generar_datos(16, 7, familia)
            self.assertEqual(datos, generar_datos(16, 7, familia))
            incremental = verificar_resolubilidad(datos)
            repetitivo = verificar_repetitivo(datos)
            self.assertEqual(incremental.estado, repetitivo.estado)
            self.assertTrue(validar_orden(datos, incremental.orden_llaves))
            self.assertTrue(validar_orden(datos, repetitivo.orden_llaves))
        self.assertEqual(estado, random.getstate())
        self.assertFalse(validar_orden(generar_datos(4, 7), ['K2']))

    def test_FR015_AC19_AC20_tiempos_completos_sin_red(self):
        with patch('requests.sessions.Session.request', side_effect=AssertionError('Red inesperada')):
            mediciones = medir_resolubilidad([8, 16, 32], 10, 7)
        self.assertEqual(len(mediciones), 18)
        for m in mediciones:
            self.assertEqual(len(m.muestras), 10)
            self.assertGreaterEqual(m.maximo_ms, m.promedio_ms)
            self.assertLessEqual(m.minimo_ms, m.promedio_ms)
            self.assertGreater(m.n, 0)
            self.assertGreater(m.metricas.comparaciones_normalizacion, 0)
            for muestra in m.muestras:
                self.assertGreaterEqual(muestra.total_ms, muestra.normalizacion_ms + muestra.recorrido_ms
                                        + muestra.diagnostico_ms + muestra.reporte_ms - 0.000001)
        cadenas = [m for m in mediciones if m.familia == 'cadena']
        self.assertGreater(cadenas[-1].metricas.salas_procesadas, cadenas[-2].metricas.salas_procesadas)
        ciclos = [m for m in mediciones if m.familia == 'ciclo' and m.estrategia == 'incremental']
        for a, b in zip(ciclos, ciclos[1:]):
            self.assertLess(b.metricas.relaciones_diagnostico, 3 * a.metricas.relaciones_diagnostico)


    def test_FR001_FR005_AC04_AC24_oraculo_en_mapas_variados(self):
        for semilla in range(60):
            azar = random.Random(semilla)
            salas = []
            ubicaciones = []
            for i in range(8):
                salidas = []
                for direccion in ('N', 'S', 'E', 'O')[:azar.randrange(5)]:
                    cerrada = azar.choice([False, True])
                    llave = azar.choice(['A', 'B', 'C'])
                    salidas.append(SalidaVerificacion(i, direccion, azar.randrange(8), cerrada, llave))
                salas.append(SalaVerificacion(i, salidas))
                if azar.randrange(2):
                    ubicaciones.append(UbicacionLlave(azar.choice(['A', 'B', 'C']), i))
            datos = DatosVerificacion('variada', 'v1', 0, 7, 'C', salas, ubicaciones)
            with self.subTest(semilla=semilla):
                incremental = verificar_resolubilidad(datos)
                repetitivo = verificar_repetitivo(datos)
                self.assertEqual(incremental.estado, repetitivo.estado)
                self.assertCountEqual(incremental.orden_llaves, repetitivo.orden_llaves)
                self.assertTrue(validar_orden(datos, incremental.orden_llaves))
                self.assertEqual(incremental.evidencia, repetitivo.evidencia)
                self.assertEqual(incremental.ciclos, repetitivo.ciclos)
    def test_FR015_AC20_datos_preparados(self):
        datos = generar_datos(12, 4)
        mediciones = medir_datos(datos, 10)
        self.assertEqual(len(mediciones), 2)
        self.assertTrue(all(m.version == datos.version for m in mediciones))
        with self.assertRaises(ValueError):
            medir_datos(datos, 0)


if __name__ == '__main__':
    unittest.main()
