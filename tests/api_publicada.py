"""Proceso aislado de QA: cada fase conserva su UUID y su contador HTTP."""
import json
import sys

from datos.almacen import AlmacenLocal
from red.cliente_api import ClienteApi
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from red.verificacion import preparar_verificacion
from modelo.resolubilidad import verificar_resolubilidad
from modelo.juego import crear_juego
from controlador.partida_historica import integrar_historia


def ejecutar(cripta=None, carpeta=None):
    cliente = ClienteApi()
    precarga = None
    try:
        lista = cliente.listar_criptas()
        if cripta is None:
            return lista
        if not any(c['id'] == cripta for c in lista['criptas']):
            raise AssertionError('La cripta no pertenece al listado publicado.')
        almacen = AlmacenLocal(carpeta)
        datos = preparar_verificacion(cliente, almacen, cripta)
        dictamen = verificar_resolubilidad(datos)
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), almacen)
        precarga = GestorPrecarga(cliente, catalogo)
        motor = crear_juego(precarga, cripta, 20, version_cripta=datos.version, partida_completa=True)
        juego = integrar_historia(motor, 50)
        precarga.cargar_contenido([s.id for s in precarga.salas])
        for _ in range(3):
            if motor.terminado:
                break
            if not juego.ejecutar('esperar').ok:
                raise AssertionError('El motor rechazó una espera válida.')
        precarga.cerrar()
        return {'cripta': cripta, 'version': datos.version, 'dictamen': dictamen.estado,
                **catalogo.reporte()}
    finally:
        if precarga is not None:
            precarga.cerrar()
        cliente.cerrar()


if __name__ == '__main__':
    print(json.dumps(ejecutar(*sys.argv[1:]), ensure_ascii=False))
