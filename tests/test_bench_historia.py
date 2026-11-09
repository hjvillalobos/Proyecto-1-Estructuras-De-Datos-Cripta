import contextlib
import io
import unittest
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bench import main
from utilidades.bench_historia import medir_historia


class BenchHistoriaTest(unittest.TestCase):
    def test_fr009_fr010_compara_las_mismas_consultas_y_cuenta_controles(self):
        filas = medir_historia(105, 1, 7, campos=8, consultas=12)
        self.assertEqual([fila.k for fila in filas], [10, 50, 100, None])
        self.assertEqual([fila.controles for fila in filas], [11, 3, 2, 1])
        for fila in filas:
            self.assertGreater(fila.memoria, 0)
            self.assertGreater(fila.bytes_guardados, 0)
            self.assertLessEqual(fila.max_acciones, fila.k or 105)

    def test_fr011_bench_compara_binario_v4_y_json_del_mismo_estado(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            main(["--subsistemas", "guardado-historia", "--operaciones", "20",
                  "--salas", "3", "--repeticiones", "1"])
        resultado = salida.getvalue()
        self.assertIn("guardado-historia/binario/cargar", resultado)
        self.assertIn("guardado-historia/json/cargar", resultado)
        self.assertIn("guardado-historia/binario/sala_directa", resultado)

    def test_fr017_bench_delega_mediciones_de_resolubilidad(self):
        fila = SimpleNamespace(familia="cadena", estrategia="incremental", n=50,
                               promedio_ms=2, minimo_ms=1, maximo_ms=3,
                               desviacion_ms=0.5, muestras=[1, 3], estado="resoluble")
        medir = Mock(return_value=[fila])
        salida = io.StringIO()
        with patch.dict(sys.modules, {"utilidades.bench_resolubilidad":
                                     SimpleNamespace(medir_resolubilidad=medir)}), \
                contextlib.redirect_stdout(salida):
            main(["--subsistemas", "resolubilidad", "--tamanos", "4", "8", "16",
                  "--repeticiones", "2", "--semilla", "9"])
        medir.assert_called_once_with([4, 8, 16], 2, 9)
        self.assertIn("Resolubilidad cadena incremental N=50", salida.getvalue())

    def test_nfr001_bench_disponible_por_cli_sin_vista(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            main(["--subsistemas", "historia", "--operaciones", "105",
                  "--repeticiones", "1"])
        self.assertIn("sin controles", salida.getvalue())
        self.assertIn("inversa", salida.getvalue())
