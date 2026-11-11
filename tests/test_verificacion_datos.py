from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from datos.almacen import AlmacenLocal
from datos.offline import ClienteOffline
from main import main
from red.errores import DatosInvalidos, DatosNoDisponibles, ErrorRed
from red.verificacion import preparar_verificacion, verificar_cripta
from tests.datos_prueba import ServidorFalso


class ServidorVerificacion(ServidorFalso):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llaves = {'llaves': [{'id': 'obj_0', 'sala': 100}]}
        self.version_final = None
        self.error_final = False

    def obtener_llaves(self, cripta_id):
        self._contar('llaves')
        return deepcopy(self.llaves)

    def obtener_esqueleto(self, cripta_id, pagina=1):
        datos = super().obtener_esqueleto(cripta_id, pagina)
        for sala in datos['salas']:
            for salida in sala['salidas'].values():
                if salida['sala'] == 100 + self.cantidad - 1:
                    salida['llave'] = 'obj_0'
                    salida['cerrada'] = True
        return datos

    def obtener_version_cripta(self, cripta_id):
        if any(tipo == 'llaves' for tipo, _ in self.llamadas):
            if self.error_final:
                raise ErrorRed('Fallo en la comprobación final.')
            if self.version_final:
                self.version = self.version_final
        return super().obtener_version_cripta(cripta_id)


class TestVerificacionDatos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.almacen = AlmacenLocal(self.temporal.name)

    def test_FR010_AC11_descarga_completa_y_verificacion_offline(self):
        cliente = ServidorVerificacion(salas=3)
        carpeta = self.temporal.name
        with patch('red.cliente_api.ClienteApi', return_value=cliente), redirect_stdout(StringIO()):
            self.assertEqual(main(['--descargar-todo', '--datos-dir', carpeta]), 0)
        self.assertEqual(self.almacen.leer_llaves('prueba', 'v1'), cliente.llaves)
        self.assertEqual(sum(tipo == 'llaves' for tipo, _ in cliente.llamadas), 1)
        salida = StringIO()
        with patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP inesperado')), redirect_stdout(salida):
            self.assertEqual(main(['--verificar', 'prueba', '--offline', carpeta]), 0)
        self.assertIn('Orden de llaves: obj_0', salida.getvalue())

    def test_FR010_AC11_vacio_ausente_corrupto(self):
        self.assertIsNone(self.almacen.leer_llaves('prueba', 'v1'))
        self.almacen.guardar_llaves('prueba', 'v1', {'llaves': []})
        self.assertEqual(self.almacen.leer_llaves('prueba', 'v1'), {'llaves': []})
        ruta = self.almacen._cripta('prueba', 'v1') / 'llaves.json'
        ruta.write_text('{', encoding='utf-8')
        with self.assertRaises(DatosInvalidos):
            self.almacen.leer_llaves('prueba', 'v1')

    def test_FR010_AC23_escritura_fallida_preserva_copia(self):
        self.almacen.guardar_llaves('prueba', 'v1', {'llaves': []})
        with patch('datos.almacen.os.replace', side_effect=OSError('fallo')):
            with self.assertRaises(DatosNoDisponibles):
                self.almacen.guardar_llaves('prueba', 'v1', {'llaves': [{'id': 'K', 'sala': 1}]})
        self.assertEqual(self.almacen.leer_llaves('prueba', 'v1'), {'llaves': []})

    def test_FR008_FR014_AC11_AC12_online_offline_y_reuso(self):
        cliente = ServidorVerificacion(salas=103)
        online = verificar_cripta(cliente, self.almacen, 'prueba')
        self.assertEqual(online.estado, 'resoluble')
        self.assertEqual([args for tipo, args in cliente.llamadas if tipo == 'pagina'], [(1,), (2,), (3,)])
        self.assertFalse(any(tipo in ('contenido', 'catalogo', 'version_catalogo') for tipo, _ in cliente.llamadas))
        offline = ClienteOffline(self.temporal.name)
        with patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP inesperado')):
            local = verificar_cripta(offline, self.almacen, 'prueba')
        self.assertEqual(local, online)
        self.assertEqual(offline.solicitudes_realizadas, 0)
        nuevo = ServidorVerificacion(salas=103)
        self.assertEqual(verificar_cripta(nuevo, self.almacen, 'prueba'), online)
        self.assertEqual(nuevo.llamadas, [('version_cripta', ())])

    def test_FR010_AC13_historico_coherente(self):
        esperado = verificar_cripta(ServidorVerificacion(salas=2), self.almacen, 'prueba')
        verificar_cripta(ServidorVerificacion(version='v2', salas=3), self.almacen, 'prueba')
        cliente = ClienteOffline(self.temporal.name, version_cripta='v1')
        self.assertEqual(cliente.obtener_datos_generales('prueba')['version'], 'v1')
        self.assertEqual(len(cliente.obtener_esqueleto('prueba')['salas']), 2)
        self.assertEqual(verificar_cripta(cliente, self.almacen, 'prueba', 'v1'), esperado)
        remoto = ServidorVerificacion(version='v2')
        self.assertEqual(verificar_cripta(remoto, self.almacen, 'prueba', 'v1'), esperado)
        self.assertEqual(remoto.llamadas, [])

    def test_FR008_AC23_lote_rechazado_no_publica(self):
        for fallo in ('version', 'red', 'presupuesto'):
            with self.subTest(fallo=fallo), tempfile.TemporaryDirectory() as carpeta:
                almacen = AlmacenLocal(carpeta)
                previo = verificar_cripta(ServidorVerificacion(salas=2), almacen, 'prueba')
                antes = [(str(p.relative_to(carpeta)), p.read_bytes()) for p in Path(carpeta).rglob('*.json')]
                cliente = ServidorVerificacion(salas=3, version='v2', presupuesto=4 if fallo == 'presupuesto' else 100)
                cliente.version_final = 'v3' if fallo == 'version' else None
                cliente.error_final = fallo == 'red'
                resultado = verificar_cripta(cliente, almacen, 'prueba')
                self.assertEqual(resultado.estado, 'no_completada')
                despues = [(str(p.relative_to(carpeta)), p.read_bytes()) for p in Path(carpeta).rglob('*.json')]
                self.assertEqual(antes, despues)
                self.assertEqual(verificar_cripta(ClienteOffline(carpeta), almacen, 'prueba'), previo)
                self.assertIsNone(almacen.leer_llaves('prueba', 'v2'))

    def test_FR012_AC14_AC18_tres_estados_sin_diagnostico_parcial(self):
        incompleto = verificar_cripta(ClienteOffline(self.temporal.name), self.almacen, 'prueba')
        self.assertEqual(incompleto.estado, 'no_completada')
        self.assertTrue(incompleto.causa)
        self.assertEqual(incompleto.orden_llaves, [])
        self.assertEqual(incompleto.evidencia, [])
        self.assertIsNone(incompleto.version)
        cliente = ServidorVerificacion()
        cliente.llaves = {'llaves': []}
        negativo = verificar_cripta(cliente, self.almacen, 'prueba')
        self.assertEqual(negativo.estado, 'no_resoluble')
        self.assertEqual(negativo.version, 'v1')
        self.assertEqual(negativo.cripta_id, 'prueba')
        self.assertTrue(negativo.limitacion)
        with self.assertRaises(AttributeError):
            preparar_verificacion(object(), self.almacen, 'prueba')

    def test_FR008_AC14_datos_invalidos_no_publican(self):
        cliente = ServidorVerificacion()
        cliente.llaves = {'llaves': [{'id': 'obj_0'}]}
        resultado = verificar_cripta(cliente, self.almacen, 'prueba')
        self.assertEqual(resultado.estado, 'no_completada')
        self.assertIsNone(self.almacen.leer_generales('prueba'))
        self.assertEqual(list(Path(self.temporal.name).rglob('*.json')), [])

    def test_FR008_AC14_json_nulo_no_es_archivo_ausente(self):
        self.almacen.guardar_llaves('prueba', 'v1', {'llaves': []})
        ruta = self.almacen._cripta('prueba', 'v1') / 'llaves.json'
        ruta.write_text('null', encoding='utf-8')
        with self.assertRaises(DatosInvalidos):
            self.almacen.leer_llaves('prueba', 'v1')

    def test_FR008_AC14_paginas_invalidas_y_historico_incompleto(self):
        cliente = ServidorVerificacion(salas=2)
        pagina = cliente.obtener_esqueleto('prueba')
        pagina['salas'][0]['salidas']['E']['sala'] = 999
        with patch.object(cliente, 'obtener_esqueleto', return_value=pagina):
            self.assertEqual(verificar_cripta(cliente, self.almacen, 'prueba').estado, 'no_completada')
        self.assertIsNone(self.almacen.leer_generales('prueba'))
        self.almacen.guardar_generales(ServidorVerificacion(salas=2).obtener_datos_generales('prueba'))
        remoto = ServidorVerificacion(version='v2')
        self.assertEqual(verificar_cripta(remoto, self.almacen, 'prueba', 'v1').estado, 'no_completada')
        self.assertFalse(any(tipo == 'pagina' for tipo, _ in remoto.llamadas))
        local = ClienteOffline(self.temporal.name)
        self.assertEqual(verificar_cripta(local, self.almacen, 'prueba', 'v1').estado, 'no_completada')
        self.assertEqual(local.solicitudes_realizadas, 0)

    def test_FR008_AC14_paginacion_no_acepta_booleanos(self):
        cliente = ServidorVerificacion(salas=2)
        pagina = cliente.obtener_esqueleto('prueba')
        pagina['pagina'] = True
        with patch.object(cliente, 'obtener_esqueleto', return_value=pagina):
            self.assertEqual(verificar_cripta(cliente, self.almacen, 'prueba').estado, 'no_completada')

    def test_FR015_AC20_medicion_offline_separada(self):
        from utilidades.bench_resolubilidad import medir_preparacion_offline
        verificar_cripta(ServidorVerificacion(salas=2), self.almacen, 'prueba')
        with patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP inesperado')):
            medicion = medir_preparacion_offline(self.temporal.name, 'prueba', 'v1', 10)
        self.assertEqual(len(medicion.muestras_ms), 10)
        self.assertEqual(medicion.version, 'v1')
        self.assertEqual(medicion.solicitudes, 0)


if __name__ == '__main__':
    unittest.main()
