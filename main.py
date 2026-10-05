import argparse
import json
import sys

from datos.almacen import AlmacenLocal
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.errores import ErrorCripta
from red.precarga import GestorPrecarga


def entero_positivo(texto):
    valor = int(texto)
    if valor < 1:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo.")
    return valor


def main(argv=None):
    argumentos = sys.argv[1:] if argv is None else list(argv)
    if "--bench" in argumentos:
        from bench import main as ejecutar_bench
        argumentos.remove("--bench")
        ejecutar_bench(argumentos)
        return 0
    parser = argparse.ArgumentParser(description="Carga de datos de CRIPTA: parte B.")
    parser.add_argument("--cripta")
    parser.add_argument("--listar", action="store_true")
    parser.add_argument("--offline", nargs="?", const=".cache/cripta", metavar="CARPETA")
    parser.add_argument("--datos-dir", default=".cache/cripta")
    parser.add_argument("--cache-size", type=entero_positivo, default=25)
    parser.add_argument("--version-cripta")
    parser.add_argument("--version-catalogo")
    parser.add_argument("--descargar-todo", action="store_true")
    args = parser.parse_args(argumentos)
    cliente = None
    precarga = None
    catalogo = None
    try:
        almacen = AlmacenLocal(args.datos_dir)
        if args.offline is not None:
            from datos.offline import ClienteOffline
            cliente = ClienteOffline(args.offline)
        else:
            from red.cliente_api import ClienteApi
            cliente = ClienteApi()
        if args.listar or args.cripta is None or args.descargar_todo:
            listado = cliente.listar_criptas()
            almacen.guardar_lista(listado)
            print(json.dumps(listado, indent=2, ensure_ascii=False))
        if args.cripta is None:
            print("Selecciona una cripta con --cripta ID.")
            return 0
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(args.cache_size), almacen)
        precarga = GestorPrecarga(cliente, catalogo)
        preparada = precarga.preparar_cripta(args.cripta, args.version_cripta, args.version_catalogo)
        print(f"Cripta {args.cripta}, versión {preparada.generales['version']}")
        print(f"Sala inicial: {preparada.inicial.sala.id} - {preparada.inicial.sala.nombre}")
        print(f"Esqueleto: {len(preparada.salas)} salas")
        print("Fichas iniciales: " + ", ".join(ficha.nombre for ficha in preparada.inicial.fichas))
        if args.descargar_todo:
            precarga.cargar_contenido([sala.id for sala in preparada.salas])
            print(f"Respuestas completas guardadas en {args.datos_dir}")
        print("Datos preparados para el motor del juego.")
        return 0
    except ErrorCripta as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except ModuleNotFoundError as error:
        if error.name != "requests":
            raise
        print("Falta requests. Instálalo con: python -m pip install requests", file=sys.stderr)
        return 1
    finally:
        if precarga is not None:
            precarga.cerrar()
        if catalogo is not None:
            print(json.dumps(catalogo.reporte(), indent=2, ensure_ascii=False))
        elif cliente is not None:
            print(f"Solicitudes de red: {cliente.solicitudes_realizadas}")
        if cliente is not None:
            cliente.cerrar()


if __name__ == "__main__":
    raise SystemExit(main())
