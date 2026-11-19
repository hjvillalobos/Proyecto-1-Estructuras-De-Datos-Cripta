"""CD-01/02: mensajes visibles, almacenamiento acotado y medición sin vista."""
from pathlib import Path
import subprocess
import sys
import unittest

from utilidades.bitacora import BufferCircular
from utilidades.bench_bitacora import ListaDesplazada, medir_bitacora


class TestBenchBitacora(unittest.TestCase):
    def test_cd01_importacion_publica_conserva_la_clase_real(self):
        from vista.bitacora_pantalla import BufferCircular as Publica
        self.assertIs(Publica, BufferCircular)

    def test_cd01_orden_limite_vaciado_y_reutilizacion_con_oraculo(self):
        mensajes = [f"mensaje {i}" for i in range(85)]
        for fabrica in (BufferCircular, ListaDesplazada):
            with self.subTest(estrategia=fabrica.__name__):
                bitacora = fabrica(20)
                self.assertEqual(bitacora.ultimos(), [])
                for i, mensaje in enumerate(mensajes, 1):
                    bitacora.agregar(mensaje)
                    self.assertEqual(bitacora.ultimos(), mensajes[max(0, i - 20):i])
                    self.assertEqual(len(bitacora), min(20, i))
                copia = bitacora.ultimos()
                copia.clear()
                self.assertEqual(bitacora.ultimos(), mensajes[-20:])
                bitacora.vaciar()
                self.assertEqual(bitacora.ultimos(), [])
                self.assertEqual(len(bitacora), 0)
                bitacora.agregar("nuevo")
                self.assertEqual(bitacora.ultimos(), ["nuevo"])

    def test_cd02_muestras_y_almacenamiento_circular_acotados(self):
        corta = medir_bitacora(25, 2, 42)
        larga = medir_bitacora(400, 2, 42)
        for filas in (corta, larga):
            self.assertEqual(len(filas), 4)
            self.assertEqual([(f.estrategia, f.carga) for f in filas],
                [(e, c) for e in ("circular", "desplazada")
                 for c in ("agregar", "agregar_y_consultar")])
            for fila in filas:
                self.assertEqual(len(fila.muestras_us), 2)
                self.assertTrue(all(t > 0 for t in fila.muestras_us))
                self.assertGreater(fila.almacenamiento_max_bytes, 0)
                self.assertEqual(fila.capacidad, 20)
        self.assertEqual(corta[0].almacenamiento_max_bytes,
                         larga[0].almacenamiento_max_bytes)

    def test_cd02_cli_no_importa_vista_ni_hace_http(self):
        raiz = Path(__file__).resolve().parents[1]
        codigo = """
import sys
from unittest.mock import patch
from main import main
with patch('socket.create_connection', side_effect=AssertionError('red')):
    assert main(['--bench', '--subsistemas', 'bitacora', '--operaciones', '45',
                 '--repeticiones', '2', '--semilla', '42']) == 0
assert not any(n == 'vista' or n.startswith('vista.') for n in sys.modules)
assert 'tkinter' not in sys.modules
"""
        proceso = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", codigo],
                                  cwd=raiz, capture_output=True, encoding="utf-8", timeout=30)
        self.assertEqual(proceso.returncode, 0, proceso.stdout + proceso.stderr)
        for etiqueta in ("circular/agregar", "circular/agregar_y_consultar",
                         "desplazada/agregar", "desplazada/agregar_y_consultar"):
            self.assertIn("bitacora/" + etiqueta, proceso.stdout)
        self.assertIn("almacenamiento_max=", proceso.stdout)
        self.assertIn("Muestras (us/op):", proceso.stdout)

    def test_cd02_carga_invalida_no_genera_mediciones(self):
        for operaciones, repeticiones, capacidad in ((0, 1, 20), (10, 0, 20),
                                                     (10, 1, 0), (True, 1, 20)):
            with self.subTest(carga=(operaciones, repeticiones, capacidad)):
                with self.assertRaises(ValueError):
                    medir_bitacora(operaciones, repeticiones, capacidad=capacidad)


if __name__ == "__main__":
    unittest.main()
