import argparse
import json
import os
import subprocess
import sys

from red.sesion import SesionDatos
from red.errores import ErrorCripta


def entero_positivo(texto):
    valor = int(texto)
    if valor < 1:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo.")
    return valor


def ejecutar_replay(args, gestor_precarga, cliente):
    """--replay ARCHIVO: reproduce la partida (con --gui, en una ventana)."""
    from controlador.replay import ReproductorReplay
    from modelo.juego import crear_juego

    if args.gui:
        from vista.grafica import VistaGrafica

        vista = VistaGrafica()
    else:
        from vista.consola import VistaConsola

        vista = VistaConsola()

    try:
        ReproductorReplay(
            cliente,
            gestor_precarga,
            vista,
            crear_juego,
        ).reproducir(args.replay)
    finally:
        if args.gui:
            vista.cerrar()


def crear_lanzador_replay(args):
    """
    Función que abre un replay en un proceso aparte, con las mismas opciones
    de datos (--offline, --datos-dir, --cache-size). Así el replay no toca
    la partida en curso ni gasta su presupuesto de solicitudes.
    """

    def lanzar(ruta):
        comando = [sys.executable, os.path.abspath(__file__)]

        if args.offline is not None:
            comando += ["--offline", args.offline]

        comando += [
            "--datos-dir", args.datos_dir,
            "--cache-size", str(args.cache_size),
            "--replay", ruta,
        ]

        if args.gui:
            # Ventana propia; la partida sigue jugable mientras tanto.
            subprocess.Popen(comando + ["--gui"])
        else:
            # Consola: se muestra en línea y se vuelve a la partida.
            subprocess.run(comando)

    return lanzar


def leer_argumentos(argumentos):
    parser = argparse.ArgumentParser(description="CRIPTA - Estructuras de Datos II")
    parser.add_argument("--cripta")
    parser.add_argument("--listar", action="store_true")
    parser.add_argument("--offline", nargs="?", const=".cache/cripta", metavar="CARPETA")
    parser.add_argument("--datos-dir", default=".cache/cripta")
    parser.add_argument("--cache-size", type=entero_positivo, default=25)
    parser.add_argument("--version-cripta")
    parser.add_argument("--version-catalogo")
    parser.add_argument("--descargar-todo", action="store_true")
    parser.add_argument("--semilla", type=int, default=None)
    parser.add_argument("--replay", metavar="ARCHIVO")
    parser.add_argument("--gui", action="store_true",
                        help="Jugar en una ventana gráfica (tkinter) en vez de la consola.")
    return parser.parse_args(argumentos)


def main(argv=None):
    argumentos = sys.argv[1:] if argv is None else list(argv)
    if "--bench" in argumentos:
        from bench import main as ejecutar_bench
        argumentos.remove("--bench")
        ejecutar_bench(argumentos)
        return 0

    args = leer_argumentos(argumentos)
    sesion = SesionDatos(args)
    try:
        sesion.abrir()
        if args.listar or (args.cripta is None and not args.replay and not args.gui) or args.descargar_todo:
            listado = sesion.cliente.listar_criptas()
            sesion.almacen.guardar_lista(listado)
            print(json.dumps(listado, indent=2, ensure_ascii=False))
        if args.cripta is None and not args.replay and not args.gui and not args.descargar_todo:
            print("Selecciona una cripta con --cripta ID.")
            return 0

        sesion.preparar()
        if args.replay:
            ejecutar_replay(args, sesion.precarga, sesion.cliente)
            return 0
        if args.descargar_todo:
            ids = ([args.cripta] if args.cripta is not None
                   else [cripta["id"] for cripta in listado["criptas"]])
            for indice, cripta_id in enumerate(ids):
                if indice:
                    sesion.renovar()
                preparada = sesion.precarga.preparar_cripta(
                    cripta_id, args.version_cripta, args.version_catalogo)
                sesion.precarga.cargar_contenido([sala.id for sala in preparada.salas])
                print(f"{cripta_id}: {len(preparada.salas)} salas descargadas")
            print(f"Respuestas completas guardadas en {args.datos_dir}")
            return 0

        from controlador.aplicacion import ejecutar_juego
        return ejecutar_juego(args, sesion, crear_lanzador_replay(args))
    except ErrorCripta as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except ModuleNotFoundError as error:
        if error.name != "requests":
            raise
        print("Falta requests. Instálalo con: python -m pip install requests", file=sys.stderr)
        return 1
    finally:
        try:
            sesion.cerrar(reportar=True)
        except (ErrorCripta, OSError) as error:
            print(f"Aviso al cerrar la sesion: {error}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
