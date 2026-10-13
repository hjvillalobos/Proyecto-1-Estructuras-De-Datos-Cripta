import json

from datos.almacen import AlmacenLocal
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.errores import ErrorCripta
from red.precarga import GestorPrecarga


class SesionDatos:
    """Propietaria de los recursos de datos de un intento de partida."""

    def __init__(self, args):
        self.args = args
        self.almacen = AlmacenLocal(args.datos_dir)
        self.cliente = self.catalogo = self.precarga = None

    def abrir(self):
        if self.args.offline is not None:
            from datos.offline import ClienteOffline
            self.cliente = ClienteOffline(self.args.offline)
        else:
            from red.cliente_api import ClienteApi
            self.cliente = ClienteApi()

    def preparar(self):
        self.catalogo = GestorCatalogo(
            self.cliente, CacheCatalogoOrdenado(self.args.cache_size), self.almacen)
        self.precarga = GestorPrecarga(self.cliente, self.catalogo)

    def renovar(self, tolerar_error=False):
        self.cerrar(tolerar_error=tolerar_error)
        self.cliente = self.catalogo = self.precarga = None
        self.abrir()
        self.preparar()

    def cerrar(self, reportar=False, tolerar_error=False):
        try:
            if self.precarga is not None:
                try:
                    self.precarga.cerrar()
                except ErrorCripta:
                    if not tolerar_error:
                        raise
        finally:
            try:
                if reportar:
                    if self.catalogo is not None:
                        print(json.dumps(self.catalogo.reporte(), indent=2, ensure_ascii=False))
                    elif self.cliente is not None:
                        print(f"Solicitudes de red: {self.cliente.solicitudes_realizadas}")
            finally:
                if self.cliente is not None:
                    self.cliente.cerrar()
