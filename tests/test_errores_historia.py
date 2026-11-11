"""FR-020 y FR-011: contrato público de errores esperados, sin ocultar fallos."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from datos.guardado_binario import ErrorGuardado, FormatoIncompatible, GuardadoCorrupto
from datos.historia_binaria import cargar_historia, guardar_historia, decodificar_historia
from modelo.errores_historia import (
    ErrorHistoria, EntradaHistoriaInvalida, ReferenciaHistoricaInvalida,
    CambioHistoriaIncoherente,
)
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from modelo.snapshots import CambioHistorico, ValorHistorico


class TestErroresHistoria(unittest.TestCase):
    def crear(self):
        return LineaTiempo(EstadoHistorico((('vida', 10),)))

    def test_errores_dominio_conservan_compatibilidad_valueerror(self):
        """FR-020: captura común sin confundir parámetros y referencias."""
        for clase in (EntradaHistoriaInvalida, ReferenciaHistoricaInvalida, CambioHistoriaIncoherente):
            self.assertTrue(issubclass(clase, ErrorHistoria))
            self.assertTrue(issubclass(clase, ValueError))
        with self.assertRaisesRegex(EntradaHistoriaInvalida, 'K'):
            LineaTiempo(EstadoHistorico(), 0)
        with self.assertRaisesRegex(EntradaHistoriaInvalida, 'entero'):
            self.crear().consultar_t('uno')

    def test_referencia_invalida_se_distingue_de_entrada(self):
        """FR-001/003: forma válida pero referencia fuera de la rama."""
        h = self.crear()
        for operacion, texto in ((lambda: h.consultar_t(1), 'futuro'),
                                 (lambda: h.consultar_accion(1), 'no existe'),
                                 (lambda: h.recortar(1), 'inexistente')):
            with self.assertRaisesRegex(ReferenciaHistoricaInvalida, texto):
                operacion()
        self.assertEqual(h.cantidad_acciones, 0)

    def test_cambio_incoherente_no_modifica_la_historia(self):
        """FR-005/020: el consumidor decide cómo reportar inconsistencia."""
        h = self.crear()
        original = h.exportar()
        with self.assertRaisesRegex(CambioHistoriaIncoherente, 'vida'):
            h.registrar_accion(10, (
                CambioHistorico('vida', ValorHistorico(True, 9), ValorHistorico(True, 0)),))
        self.assertEqual(h.exportar(), original)

    def test_claves_invalidas_y_campo_ausente_son_distintos(self):
        """FR-020: un campo ausente conserva KeyError, no significa None."""
        estado = EstadoHistorico()
        for clave in (None, 2, ''):
            with self.assertRaises(EntradaHistoriaInvalida):
                estado.obtener(clave)
        with self.assertRaises(KeyError):
            estado.obtener('vida')

    def test_tipos_no_binarios_y_rutas_invalidas(self):
        """FR-011/020: las funciones públicas no filtran TypeError de pathlib."""
        for datos in (None, 'texto', [1, 2]):
            with self.assertRaisesRegex(ErrorGuardado, 'binarios'):
                decodificar_historia(datos)
        for ruta in (None, 10, 'ruta\0invalida'):
            with self.subTest(ruta=ruta), self.assertRaisesRegex(ErrorGuardado, 'ruta'):
                cargar_historia(ruta)
            with self.subTest(ruta=ruta), self.assertRaisesRegex(ErrorGuardado, 'ruta'):
                guardar_historia(self.crear(), ruta)

    def test_archivo_incompatible_y_danado_conservan_clases(self):
        """FR-012/020: la vista podrá distinguir ambos casos."""
        with self.assertRaises(FormatoIncompatible):
            decodificar_historia(b'CRPT' + b'\0' * 20)
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(b'CRLH')

    def test_fallo_de_permiso_es_error_guardado_con_causa(self):
        """FR-011: no se inicia escritura si no se puede crear temporal."""
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / 'historia.bin'
            with patch('datos.historia_binaria.tempfile.mkstemp', side_effect=PermissionError('denegado')):
                with self.assertRaisesRegex(ErrorGuardado, 'guardar') as captura:
                    guardar_historia(self.crear(), ruta)
            self.assertIsInstance(captura.exception.__cause__, PermissionError)
            self.assertFalse(ruta.exists())

    def test_limpieza_fallida_no_oculta_el_error_principal(self):
        """FR-011/020: conserva destino, causa original y aviso del temporal."""
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / 'historia.bin'
            ruta.write_bytes(b'anterior')
            with patch('datos.historia_binaria.os.replace', side_effect=OSError('fallo principal')):
                with patch('datos.historia_binaria.os.unlink', side_effect=PermissionError('limpieza')):
                    with self.assertRaisesRegex(ErrorGuardado, 'fallo principal') as captura:
                        guardar_historia(self.crear(), ruta)
            self.assertEqual(str(captura.exception.__cause__), 'fallo principal')
            self.assertIn('temporal', captura.exception.__notes__[0])
            self.assertEqual(ruta.read_bytes(), b'anterior')


if __name__ == '__main__':
    unittest.main()
