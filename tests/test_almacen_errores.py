"""ERR-01: fallos dobles conservan causa, destino y diagnóstico de limpieza."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from datos.almacen import AlmacenLocal
from red.errores import DatosNoDisponibles


class AlmacenErroresTest(unittest.TestCase):
    def test_reemplazo_y_limpieza_fallidos_conservan_error_original(self):
        with tempfile.TemporaryDirectory() as carpeta:
            almacen = AlmacenLocal(carpeta)
            destino = Path(carpeta) / 'criptas.json'
            destino.write_text('{"anterior":true}', encoding='utf-8')
            principal = OSError('fallo de reemplazo')
            with patch('datos.almacen.os.replace', side_effect=principal), \
                    patch.object(Path, 'unlink', side_effect=PermissionError('fallo de limpieza')):
                with self.assertRaisesRegex(DatosNoDisponibles, 'fallo de reemplazo') as captura:
                    almacen.guardar_lista({'nuevo': True})
            self.assertIs(captura.exception.__cause__, principal)
            self.assertIn('fallo de limpieza', '\n'.join(captura.exception.__notes__))
            self.assertEqual(destino.read_text(encoding='utf-8'), '{"anterior":true}')
            self.assertEqual(len(list(Path(carpeta).glob('*.tmp'))), 1)

    def test_json_invalido_conserva_destino_y_limpia_temporal(self):
        with tempfile.TemporaryDirectory() as carpeta:
            almacen = AlmacenLocal(carpeta)
            almacen.guardar_lista({'anterior': True})
            with self.assertRaises(DatosNoDisponibles) as captura:
                almacen.guardar_lista({'numero': float('nan')})
            self.assertIsInstance(captura.exception.__cause__, ValueError)
            self.assertEqual(almacen.leer_lista(), {'anterior': True})
            self.assertEqual(list(Path(carpeta).glob('*.tmp')), [])

    def test_guardado_correcto_reemplaza_sin_temporales(self):
        with tempfile.TemporaryDirectory() as carpeta:
            almacen = AlmacenLocal(carpeta)
            almacen.guardar_lista({'anterior': True})
            almacen.guardar_lista({'nuevo': 'información'})
            self.assertEqual(almacen.leer_lista(), {'nuevo': 'información'})
            self.assertEqual(list(Path(carpeta).glob('*.tmp')), [])
