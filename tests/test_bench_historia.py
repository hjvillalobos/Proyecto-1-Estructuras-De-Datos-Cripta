import contextlib
import io
from tempfile import TemporaryDirectory
import unittest
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

from bench import main
from datos.almacen import AlmacenLocal
from main import main as main_cli
from red.verificacion import preparar_verificacion
from tests.datos_prueba import crear_paquete
from tests.test_verificacion_datos import ServidorVerificacion
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
        with io.BytesIO() as datos, io.TextIOWrapper(datos, encoding="cp1252") as salida:
            with patch.dict(sys.modules, {"utilidades.bench_resolubilidad":
                                         SimpleNamespace(medir_resolubilidad=medir)}), \
                    contextlib.redirect_stdout(salida):
                main(["--subsistemas", "resolubilidad", "--tamanos", "4", "8", "16",
                      "--semilla", "9"])
            salida.flush()
            resultado = datos.getvalue().decode("cp1252")
        medir.assert_called_once_with([4, 8, 16], 10, 9)
        self.assertIn("Resolubilidad cadena incremental N=50", resultado)
        self.assertIn("desv. estándar=0.500 ms muestras=2", resultado)

    def test_fr017_ac20_bench_mide_paquete_y_separa_lectura_del_analisis(self):
        with TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as salida:
            almacen = AlmacenLocal(tmp)
            preparar_verificacion(ServidorVerificacion(salas=2), almacen, "prueba")
            preparar_verificacion(ServidorVerificacion(salas=3, version="v2"), almacen, "prueba")
            with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")), \
                    patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                    patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
                self.assertEqual(main_cli(["--bench", "--subsistemas", "resolubilidad",
                                            "--paquete", tmp, "--cripta", "prueba",
                                            "--version-cripta", "v1"]), 0)
            resultado = salida.getvalue()
            self.assertIn("Paquete offline: prueba@v1 | salas=2", resultado)
            self.assertIn("Preparación offline (lectura y validación)", resultado)
            self.assertIn("solicitudes=0", resultado)
            self.assertIn("Resolubilidad paquete incremental", resultado)
            self.assertIn("Resolubilidad paquete repetitivo", resultado)
            self.assertEqual(resultado.count("muestras=10"), 3)
            self.assertEqual(resultado.count("Muestras (ms)"), 3)
            self.assertNotIn("Resolubilidad cadena", resultado)

    def test_fr017_ac20_bench_rechaza_paquete_sin_llaves(self):
        with TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()) as salida, \
                contextlib.redirect_stderr(io.StringIO()) as errores:
            crear_paquete(tmp, salas=2, incluir_llaves=False)
            with self.assertRaises(SystemExit) as fallo:
                main_cli(["--bench", "--subsistemas", "resolubilidad", "--paquete", tmp,
                          "--cripta", "prueba"])
            self.assertEqual(fallo.exception.code, 1)
            self.assertIn("Faltan datos locales", errores.getvalue())
            self.assertNotIn("Resolubilidad cadena", salida.getvalue())
            self.assertNotIn("Preparación offline", salida.getvalue())

    def test_fr015_ac19_ac20_cli_paquete_300_salas_con_repeticiones_predeterminadas_y_explicitas(self):
        with TemporaryDirectory() as tmp:
            preparar_verificacion(ServidorVerificacion(salas=300), AlmacenLocal(tmp), "prueba")
            for argumentos in ([], ["--repeticiones", "10"]):
                with self.subTest(argumentos=argumentos), \
                        contextlib.redirect_stdout(io.StringIO()) as salida, \
                        patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")), \
                        patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                        patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
                    self.assertEqual(main_cli(["--bench", "--subsistemas", "resolubilidad",
                                               "--paquete", tmp, "--cripta", "prueba",
                                               *argumentos]), 0)
                resultado = salida.getvalue()
                self.assertIn("repeticiones=10", resultado)
                self.assertIn("Paquete offline: prueba@v1 | salas=300", resultado)
                self.assertIn("solicitudes=0", resultado)
                self.assertIn("Resolubilidad paquete incremental", resultado)
                self.assertIn("Resolubilidad paquete repetitivo", resultado)
                self.assertNotIn("Resolubilidad cadena", resultado)
                self.assertEqual(resultado.count("muestras=10"), 3)
                muestras = [linea for linea in resultado.splitlines() if "Muestras (ms):" in linea]
                self.assertEqual(len(muestras), 3)
                for linea in muestras:
                    self.assertEqual(len(linea.split(":", 1)[1].split(",")), 10)

    def test_nfr001_bench_disponible_por_cli_sin_vista(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            main(["--subsistemas", "historia", "--operaciones", "105",
                  "--repeticiones", "1"])
        self.assertIn("sin controles", salida.getvalue())
        self.assertIn("inversa", salida.getvalue())
