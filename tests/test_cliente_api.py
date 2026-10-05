import unittest
from unittest.mock import Mock

import requests

from red.cliente_api import ClienteApi
from red.errores import DatosInvalidos, ErrorRed, PresupuestoAgotado


def respuesta(estado, datos):
    resultado = Mock()
    resultado.status_code = estado
    resultado.json.return_value = datos
    return resultado


class TestClienteApi(unittest.TestCase):
    def setUp(self):
        self.transporte = Mock()
        self.esperar = Mock()
        self.cliente = ClienteApi(transporte=self.transporte, esperar=self.esperar)
        self.transporte.get.return_value = respuesta(200, {"version": "v1"})

    def test_id_compartido_por_ejecucion(self):
        otro = ClienteApi(transporte=Mock())
        self.assertEqual(self.cliente.cliente_id, otro.cliente_id)
        self.cliente.listar_criptas()
        self.cliente.obtener_version_catalogo()
        for llamada in self.transporte.get.call_args_list:
            self.assertEqual(llamada.kwargs["headers"]["X-Cripta-Client-Id"], otro.cliente_id)
            self.assertEqual(llamada.kwargs["timeout"], 10)
            self.assertFalse(llamada.kwargs["allow_redirects"])

    def test_429_espera_segundos_y_cuenta_reintento(self):
        self.transporte.get.side_effect = [
            respuesta(429, {"error": "límite", "reintentar_en": 12}),
            respuesta(200, {"criptas": []})
        ]
        self.assertEqual(self.cliente.listar_criptas(), {"criptas": []})
        self.esperar.assert_called_once_with(12)
        self.assertEqual(self.cliente.solicitudes_realizadas, 2)
        cabeceras = [c.kwargs["headers"] for c in self.transporte.get.call_args_list]
        self.assertEqual(cabeceras[0], cabeceras[1])

    def test_no_espera_ni_reintenta_sin_presupuesto(self):
        self.cliente.configurar_presupuesto(1)
        self.transporte.get.return_value = respuesta(429, {"reintentar_en": 12})
        with self.assertRaises(PresupuestoAgotado):
            self.cliente.listar_criptas()
        self.esperar.assert_not_called()
        self.assertEqual(self.transporte.get.call_count, 1)

    def test_contador_incluye_inicio_y_errores(self):
        self.cliente.listar_criptas()
        self.transporte.get.return_value = respuesta(200, {"presupuesto_solicitudes": 2})
        self.cliente.obtener_datos_generales("prueba")
        with self.assertRaises(PresupuestoAgotado):
            self.cliente.obtener_version_catalogo()
        self.assertEqual(self.cliente.solicitudes_realizadas, 2)

    def test_presupuesto_insuficiente_al_conocerlo(self):
        self.cliente.listar_criptas()
        self.transporte.get.return_value = respuesta(200, {"presupuesto_solicitudes": 1})
        with self.assertRaises(PresupuestoAgotado):
            self.cliente.obtener_datos_generales("prueba")

    def test_errores_tienen_contexto_y_cuentan(self):
        for error in (requests.Timeout("agotado"), requests.ConnectionError("sin conexión")):
            with self.subTest(error=error):
                self.transporte.get.side_effect = error
                antes = self.cliente.solicitudes_realizadas
                with self.assertRaisesRegex(ErrorRed, "GET /criptas"):
                    self.cliente.listar_criptas()
                self.assertEqual(self.cliente.solicitudes_realizadas, antes + 1)

    def test_estado_http_y_json_invalido(self):
        self.transporte.get.return_value = respuesta(404, {"error": "no existe"})
        with self.assertRaisesRegex(ErrorRed, "404.*no existe"):
            self.cliente.listar_criptas()
        mala = respuesta(200, {})
        mala.json.side_effect = ValueError("inválido")
        self.transporte.get.return_value = mala
        with self.assertRaisesRegex(ErrorRed, "JSON inválido"):
            self.cliente.listar_criptas()
        mala.close.assert_called_once()

    def test_429_invalido_y_reintentos_acotados(self):
        for espera in (None, 0, -1, "12"):
            self.transporte.get.return_value = respuesta(429, {"reintentar_en": espera})
            with self.assertRaises(DatosInvalidos):
                self.cliente.listar_criptas()
        self.transporte.get.reset_mock()
        self.transporte.get.return_value = respuesta(429, {"reintentar_en": 1})
        with self.assertRaisesRegex(ErrorRed, "3 reintentos"):
            self.cliente.listar_criptas()
        self.assertEqual(self.transporte.get.call_count, 4)

    def test_limites_de_lote_antes_de_la_red(self):
        for ids in ([], list(range(11)), [1.5], [True]):
            with self.subTest(ids=ids), self.assertRaises(DatosInvalidos):
                self.cliente.obtener_contenido_salas("prueba", ids)
        for ids in ([], [str(i) for i in range(11)], ["a,b"], [""]):
            with self.subTest(ids=ids), self.assertRaises(DatosInvalidos):
                self.cliente.obtener_catalogo(ids)
        self.assertEqual(self.cliente.solicitudes_realizadas, 0)

    def test_rutas_parametros_y_deduplicacion(self):
        self.cliente.obtener_contenido_salas("prueba", [100, 100, 102])
        self.assertEqual(self.transporte.get.call_args.kwargs["params"], {"salas": "100,102"})
        self.cliente.obtener_catalogo(["a", "a", "b"])
        self.assertEqual(self.transporte.get.call_args.kwargs["params"], {"ids": "a,b"})
        self.cliente.obtener_esqueleto("prueba", 2)
        self.assertTrue(self.transporte.get.call_args.args[0].endswith("/criptas/prueba/salas"))
        self.assertEqual(self.transporte.get.call_args.kwargs["params"], {"pagina": 2})
        self.cliente.obtener_version_cripta("prueba")
        self.assertTrue(self.transporte.get.call_args.args[0].endswith("/criptas/prueba/version"))
