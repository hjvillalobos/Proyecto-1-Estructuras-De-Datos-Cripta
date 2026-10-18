import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from red.errores import ErrorRed
from red.sesion import SesionDatos


class TestSesionDatos(unittest.TestCase):
    def test_renovar_cierra_recursos_y_crea_presupuesto_independiente(self):
        with tempfile.TemporaryDirectory() as carpeta:
            args = SimpleNamespace(datos_dir=carpeta, offline=".cache/cripta", cache_size=7)
            sesion = SesionDatos(args)
            sesion.abrir()
            sesion.preparar()
            almacen = sesion.almacen
            cliente = sesion.cliente
            precarga = sesion.precarga
            catalogo = sesion.catalogo
            cliente.configurar_presupuesto(9)
            sesion.renovar()
            try:
                self.assertIs(sesion.almacen, almacen)
                self.assertIsNot(sesion.cliente, cliente)
                self.assertIsNot(sesion.precarga, precarga)
                self.assertIsNot(sesion.catalogo, catalogo)
                self.assertEqual(sesion.catalogo.cache.capacidad, 7)
                self.assertEqual(sesion.cliente.solicitudes_realizadas, 0)
            finally:
                sesion.cerrar()

    def test_cliente_se_cierra_aunque_falle_precarga(self):
        args = SimpleNamespace(datos_dir=".cache/cripta")
        sesion = SesionDatos(args)
        sesion.precarga, sesion.cliente = Mock(), Mock()
        sesion.precarga.cerrar.side_effect = ErrorRed("pendiente fallida")
        with self.assertRaises(ErrorRed):
            sesion.cerrar()
        sesion.cliente.cerrar.assert_called_once()

    def test_error_ya_notificado_se_puede_descartar_al_renovar(self):
        args = SimpleNamespace(datos_dir=".cache/cripta")
        sesion = SesionDatos(args)
        sesion.precarga, sesion.cliente = Mock(), Mock()
        sesion.precarga.cerrar.side_effect = ErrorRed("pendiente fallida")
        sesion.cerrar(tolerar_error=True)
        sesion.cliente.cerrar.assert_called_once()
