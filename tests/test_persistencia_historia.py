"""FR-011/012: persistencia del núcleo; no es el archivo de partida integrado."""
from dataclasses import replace
from pathlib import Path
import random
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from datos.guardado_binario import ErrorGuardado, FormatoIncompatible, GuardadoCorrupto
from datos.historia_binaria import (
    codificar_historia, decodificar_historia, guardar_historia, cargar_historia,
)
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from modelo.snapshots import CambioHistorico, ValorHistorico


def cambio(clave, antes, despues):
    return CambioHistorico(clave, ValorHistorico(True, antes), ValorHistorico(True, despues))


class TestPersistenciaHistoria(unittest.TestCase):
    def crear(self, k=2, n=7):
        h = LineaTiempo(EstadoHistorico((('vida', 20), ('sala', 1))), k)
        for i in range(n):
            h.registrar_accion((i + 1) * 10, (cambio('sala', i + 1, i + 2),))
        return h

    def comparar(self, a, b):
        self.assertEqual(a.exportar(), b.exportar())
        self.assertEqual(a.checkpoint_cada, b.checkpoint_cada)
        self.assertEqual(a.cantidad_puntos_control, b.cantidad_puntos_control)
        for t in range(a.reloj + 1):
            self.assertEqual(a.consultar_t(t).estado.campos(), b.consultar_t(t).estado.campos())
            self.assertLessEqual(b.consultar_t(t).acciones_reconstruidas, b.checkpoint_cada)
        for k in range(1, a.cantidad_acciones + 1):
            self.assertEqual(a.consultar_accion(k).estado.campos(), b.consultar_accion(k).estado.campos())

    def test_exportacion_tipificada_y_reconstruccion_de_controles(self):
        """FR-009/010/011: importa una historia nueva, no estado compartido."""
        for k in (1, 2, 10):
            a = self.crear(k)
            b = LineaTiempo.desde_guardado(a.exportar())
            self.comparar(a, b)
            b.recortar(0)
            self.assertEqual(a.cantidad_acciones, 7)

    def test_ida_vuelta_binaria_y_continuacion(self):
        """FR-011: mismo pasado y mismo estado tras continuar."""
        a = self.crear()
        b = decodificar_historia(codificar_historia(a))
        self.comparar(a, b)
        for h in (a, b):
            h.registrar_accion(90, (cambio('vida', 20, 17),))
        self.comparar(a, b)

    def test_preserva_eventos_y_campos_creados_o_eliminados(self):
        """FR-002/011: reconstruir entre eventos tras cargar."""
        from modelo.snapshots import EventoHistorico
        a = self.crear(n=0)
        a.registrar_accion(10, (
            CambioHistorico('llave', ValorHistorico(False), ValorHistorico(True, None)),), (
            EventoHistorico(5, 1, (cambio('vida', 20, 18),)),
            EventoHistorico(5, 2, (
                CambioHistorico('llave', ValorHistorico(True, None), ValorHistorico(False)),)),))
        self.comparar(a, decodificar_historia(codificar_historia(a)))

    def test_preserva_solo_rama_vigente_y_correcciones(self):
        """FR-007/011: frontera inicial, checkpoint y bloque incompleto."""
        for conservar in (0, 2, 3):
            a = self.crear()
            a.recortar(conservar, (cambio('vida', 20, 19),))
            a.recortar(conservar, (cambio('vida', 19, 18),))
            b = decodificar_historia(codificar_historia(a))
            self.comparar(a, b)
            for h in (a, b):
                h.registrar_accion(h.reloj + 10, (cambio('vida', 18, 17),))
            self.comparar(a, b)
            with self.assertRaises(ValueError):
                b.consultar_t(100)

    def test_conserva_todos_los_tipos_sin_coercion(self):
        """FR-011: nulo, bool, int grande, float, Unicode y tuplas."""
        datos = (None, False, True, -2**140, 2**140, 1.25, 'llave ámbar 🗝', ())
        h = LineaTiempo(EstadoHistorico((('datos', datos),)))
        cargada = decodificar_historia(codificar_historia(h))
        valores = cargada.consultar_t(0).estado.obtener('datos')
        self.assertEqual(valores, datos)
        self.assertEqual(tuple(type(v) for v in valores), tuple(type(v) for v in datos))

    def test_rng_guardado_como_valor_puro_continua_igual(self):
        """NFR-004/FR-011: demuestra preservar getstate, sin capturar motor."""
        azar = random.Random(27)
        inicial = azar.getstate()
        h = LineaTiempo(EstadoHistorico((('azar', inicial),)), 1)
        azar.random()
        h.registrar_accion(10, (cambio('azar', inicial, azar.getstate()),))
        cargada = decodificar_historia(codificar_historia(h))
        otro = random.Random()
        otro.setstate(cargada.consultar_t(10).estado.obtener('azar'))
        self.assertEqual(otro.random(), azar.random())

    def test_dto_incoherente_es_rechazado_sin_alterar_original(self):
        """FR-020: validar K, tiempos y valores anteriores al importar."""
        h = self.crear()
        dto = h.exportar()
        for malo in (replace(dto, checkpoint_cada=0),
                     replace(dto, acciones=(replace(dto.acciones[0], inicio=1),)),
                     replace(dto, acciones=(replace(dto.acciones[0], cambios=(
                         cambio('sala', 99, 2),)),))):
            with self.assertRaises(ValueError):
                LineaTiempo.desde_guardado(malo)
        self.assertEqual(h.exportar(), dto)

    def test_p1_y_version_futura_rechazados_explicita(self):
        """FR-012/H6 parcial: lector del fragmento distingue CRPT."""
        with self.assertRaises(FormatoIncompatible):
            decodificar_historia(b'CRPT' + struct.pack('<H', 3) + b'\0' * 30)
        datos = bytearray(codificar_historia(self.crear()))
        datos[4:6] = struct.pack('<H', 999)
        with self.assertRaises(FormatoIncompatible):
            decodificar_historia(bytes(datos))

    def test_corrupcion_truncamientos_y_sobrantes(self):
        """FR-011/020: el lector no acepta payload incompleto o alterado."""
        datos = codificar_historia(self.crear(n=1))
        for n in range(len(datos)):
            with self.subTest(longitud=n), self.assertRaises(GuardadoCorrupto):
                decodificar_historia(datos[:n])
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(datos + b'basura')
        malo = bytearray(datos)
        malo[-1] ^= 1
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(bytes(malo))

    def empaquetar(self, payload):
        return struct.pack('<4sHQI', b'CRLH', 1, len(payload), zlib.crc32(payload)) + payload

    def test_estructura_invalida_aunque_crc_coincida(self):
        """FR-020: CRC correcto no sustituye validación semántica."""
        datos = codificar_historia(self.crear(n=0))
        payload = bytearray(datos[18:])
        # K es u64 al principio del fragmento.
        payload[:8] = b'\0' * 8
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(self.empaquetar(payload))
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(self.empaquetar(datos[18:] + b'\0'))

    def test_etiquetas_texto_y_reales_invalidos_con_crc_valido(self):
        """FR-020: valores malformados no se admiten aunque el CRC sea válido."""
        base = struct.pack('<QI', 2, 1)  # K y un campo inicial
        campo = struct.pack('<I', 1) + b'x'
        final = struct.pack('<I', 0)  # sin acciones
        for valor in (b'\xff', b'\x04' + struct.pack('<d', float('nan')),
                      b'\x05' + struct.pack('<I', 1) + b'\xff',
                      b'\x03\x02' + struct.pack('<I', 1) + b'\x01'):
            with self.subTest(valor=valor), self.assertRaises(GuardadoCorrupto):
                decodificar_historia(self.empaquetar(base + campo + valor + final))

    def test_no_admite_claves_repetidas_ni_conteos_imposibles(self):
        """FR-020: valida la estructura, no solo límites exteriores."""
        campo = struct.pack('<I', 1) + b'x\x00'
        payload = struct.pack('<QI', 2, 2) + campo + campo + struct.pack('<I', 0)
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(self.empaquetar(payload))
        with self.assertRaises(GuardadoCorrupto):
            decodificar_historia(self.empaquetar(struct.pack('<QI', 2, 2**32 - 1)))

    def test_historia_larga_persistida_conserva_fronteras_y_k(self):
        """FR-010/011: igualdad al recargar 5000 acciones; no mide rendimiento."""
        a = self.crear(k=50, n=5000)
        b = decodificar_historia(codificar_historia(a))
        self.assertEqual(b.exportar(), a.exportar())
        for t in (0, 1, 499, 500, 501, 49999, 50000):
            self.assertEqual(a.consultar_t(t).estado.campos(), b.consultar_t(t).estado.campos())
            self.assertLessEqual(b.consultar_t(t).acciones_reconstruidas, 50)

    def test_limites_de_profundidad_del_formato(self):
        """FR-020: guardar falla sin producir un archivo ilegible."""
        valor = None
        for _ in range(66):
            valor = (valor,)
        h = LineaTiempo(EstadoHistorico((('anidado', valor),)))
        with self.assertRaises(ErrorGuardado):
            codificar_historia(h)

    def test_archivo_guardado_y_cargado(self):
        """FR-011: reemplazo íntegro y determinista."""
        h = self.crear()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / 'historia.bin'
            guardar_historia(h, ruta)
            self.comparar(h, cargar_historia(ruta))
            self.assertEqual(ruta.read_bytes(), codificar_historia(h))
            self.assertEqual(tuple(Path(carpeta).iterdir()), (ruta,))

    def test_reemplazo_fallido_conserva_archivo_anterior_y_limpia_temporal(self):
        """FR-011/020: guardar no destruye el archivo anterior al fallar."""
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / 'historia.bin'
            ruta.write_bytes(b'original')
            with patch('datos.historia_binaria.os.replace', side_effect=OSError('simulado')):
                with self.assertRaises(ErrorGuardado):
                    guardar_historia(self.crear(), ruta)
            self.assertEqual(ruta.read_bytes(), b'original')
            self.assertEqual(tuple(Path(carpeta).iterdir()), (ruta,))

    def test_carga_inexistente_informa_error(self):
        """FR-020: error de archivo presentable al controlador."""
        with tempfile.TemporaryDirectory() as carpeta:
            with self.assertRaises(ErrorGuardado):
                cargar_historia(Path(carpeta) / 'no-existe.bin')


if __name__ == '__main__':
    unittest.main()
