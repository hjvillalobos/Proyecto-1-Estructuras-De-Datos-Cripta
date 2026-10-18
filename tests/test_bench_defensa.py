import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import bench
from controlador.controlador import ControladorJuego
from datos import guardado_binario as binario
from tests import test_regresiones_juego as base
from utilidades.bench_juego import (
    medir_agenda, medir_inventario, medir_historial, medir_ordenamientos,
    medir_guardado, medir_ciclo, motor_sintetico)
from vista.consola import VistaConsola


class TestRobustezDefensa(unittest.TestCase):
    def test_fin_entrada_e_interrupcion_cierran_controladamente(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as carpeta:
                datos = base.TestRegresionesJuego()
                datos.setUp()
                mensajes = []

                def entrada(_):
                    raise error()
                vista = VistaConsola(entrada=entrada, salida=mensajes.append)
                controlador = ControladorJuego(datos.motor, vista,
                    ruta_replay=str(Path(carpeta) / "partida.log"))
                antes = datos.motor.exportar_estado()
                controlador.iniciar()
                self.assertEqual(antes, datos.motor.exportar_estado())
                self.assertIn("Sesión finalizada.", mensajes)

    def _crear_archivo(self, carpeta):
        motor = motor_sintetico(3, 42)
        motor.contenido_cargado[2] = motor.contenido_cargado[3] = True
        estado = motor.exportar_estado()
        ruta = Path(carpeta) / "partida.bin"
        binario.guardar_estado(estado, str(ruta))
        return ruta, estado

    def _alterar_entrada(self, ruta, transformar):
        with ruta.open("r+b") as archivo:
            cab = binario._ENCABEZADO.unpack(archivo.read(binario._ENCABEZADO.size))
            off = cab[-1]
            archivo.seek(off)
            primera = binario._ENTRADA.unpack(archivo.read(binario._ENTRADA.size))
            segunda = binario._ENTRADA.unpack(archivo.read(binario._ENTRADA.size))
            archivo.seek(off)
            archivo.write(binario._ENTRADA.pack(*transformar(primera, segunda)))

    def test_indice_otro_bloque_valido_se_rechaza_en_ambas_cargas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta, _ = self._crear_archivo(carpeta)
            self._alterar_entrada(ruta, lambda a, b: (a[0], b[1], b[2]))
            with binario.ArchivoGuardado(ruta) as archivo:
                with self.assertRaises(binario.GuardadoCorrupto):
                    archivo.leer_sala(1)
                with self.assertRaises(binario.GuardadoCorrupto):
                    archivo.leer_todo()

    def test_indice_fuera_de_zona_se_rechaza(self):
        for off, longitud in ((0, 10), (10**9, 10), (32, 0)):
            with self.subTest(offset=off), tempfile.TemporaryDirectory() as carpeta:
                ruta, _ = self._crear_archivo(carpeta)
                self._alterar_entrada(ruta, lambda a, b: (a[0], off, longitud))
                with binario.ArchivoGuardado(ruta) as archivo:
                    with self.assertRaises(binario.GuardadoCorrupto):
                        archivo.leer_sala(1)
                    with self.assertRaises(binario.GuardadoCorrupto):
                        archivo.leer_todo()

    def test_indice_repetido_rechazado_en_carga_completa(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta, _ = self._crear_archivo(carpeta)
            self._alterar_entrada(ruta, lambda a, b: (b[0], a[1], a[2]))
            with self.assertRaises(binario.GuardadoCorrupto):
                binario.cargar_estado(ruta)

    def test_sala_directa_no_lee_todo_el_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta, estado = self._crear_archivo(carpeta)
            with binario.ArchivoGuardado(ruta) as archivo:
                with patch.object(archivo, "leer_todo", side_effect=AssertionError("Carga completa")), \
                        patch.object(archivo, "_leer_bloque", wraps=archivo._leer_bloque) as leer:
                    self.assertEqual(archivo.leer_sala(2), estado.salas[1])
                    self.assertIsNone(archivo.leer_sala(999))
                    self.assertEqual(leer.call_count, 1)


class TestBenchDefensa(unittest.TestCase):
    def test_cargas_reales_validan_y_reportan_repeticiones(self):
        for resultado in (medir_agenda(12, 2, 8, 42),
                          medir_inventario(12, 2, 8), medir_historial(12, 2)):
            self.assertEqual(len(resultado.tiempos_us), 2)
            self.assertEqual(resultado.operaciones, 12)
            self.assertTrue(all(t > 0 for t in resultado.tiempos_us))

    def test_ordenamientos_comparan_tres_estrategias_y_cargas(self):
        resultados = medir_ordenamientos(24, 1, [4, 16], 42)
        self.assertEqual(len(resultados), 18)
        for nombre in ("insercion", "fusion", "automatico", "comparacion_costosa", "casi_ordenado"):
            self.assertTrue(any(nombre in r.nombre for r in resultados))

    def test_guardado_compara_mismo_estado_y_acceso_directo(self):
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            resultados = medir_guardado(12, 1, 4, 42)
        self.assertEqual(len(resultados), 5)
        self.assertIn("bytes=", salida.getvalue())
        self.assertTrue(any("json/cargar" in r.nombre for r in resultados))

    def test_ciclo_mide_individualmente_y_reporta_limite(self):
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            resultado = medir_ciclo(4, 2, 8, 42)
        self.assertEqual(resultado.operaciones, 8)
        self.assertEqual(len(resultado.tiempos_us), 8)
        self.assertIn("limite=20000", salida.getvalue())

    def test_cli_todos_los_subsistemas_sin_red_ni_vista(self):
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            bench.main(["--operaciones", "8", "--repeticiones", "1",
                        "--capacidades", "3", "--escenarios", "aciertos",
                        "--tamanos", "4", "--eventos", "8", "--salas", "4"])
        texto = salida.getvalue()
        for nombre in ("binaria", "recuperacion_disco", "agenda/", "inventario/",
                       "historial/", "orden/", "guardado/", "ciclo/"):
            self.assertIn(nombre, texto)

    def test_sin_disco_omite_persistencia_y_opciones_incompletas_rechazadas(self):
        with contextlib.redirect_stdout(io.StringIO()), patch.object(bench, "medir_guardado") as guardar:
            bench.main(["--subsistemas", "guardado", "--sin-disco"])
        guardar.assert_not_called()
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            bench.main(["--paquete", "incompleto"])
