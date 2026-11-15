import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from red.sesion import SesionDatos
from red.errores import DatosNoDisponibles, ErrorCripta
from datos.bitacora_replay import ErrorReplay
from modelo.errores_historia import ErrorHistoria


def entero_positivo(texto):
    valor = int(texto)
    if valor < 1:
        raise argparse.ArgumentTypeError("Debe ser un entero positivo.")
    return valor


def ejecutar_replay(args, gestor_precarga):
    from controlador.replay_sin_vista import reproducir
    from modelo.juego import crear_juego

    from functools import partial
    print(reproducir(args.replay, gestor_precarga, partial(crear_juego, partida_completa=True),
                     args.checkpoint_cada, args.hasta))
    return 0


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

        comando += ["--checkpoint-cada", str(args.checkpoint_cada)]
        resultado = subprocess.run(
            comando, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if resultado.returncode:
            raise OSError(resultado.stderr.strip() or "No se pudo reproducir la partida.")
        return resultado.stdout.strip()

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
    modos = parser.add_mutually_exclusive_group()
    modos.add_argument("--replay", metavar="ARCHIVO")
    modos.add_argument("--verificar", metavar="CRIPTA")
    parser.add_argument("--checkpoint-cada", type=entero_positivo, default=50, metavar="K")
    parser.add_argument("--hasta", type=int, metavar="T")
    parser.add_argument("--forzar", action="store_true")
    parser.add_argument("--gui", action="store_true",
                        help="Jugar en una ventana gráfica (tkinter) en vez de la consola.")
    args = parser.parse_args(argumentos)
    if args.hasta is not None and (args.hasta < 0 or not args.replay):
        parser.error("--hasta requiere --replay y un instante entero no negativo.")
    if (args.replay or args.verificar) and (args.gui or args.cripta is not None
            or args.listar or args.descargar_todo or args.forzar or args.semilla is not None):
        parser.error("--verificar y --replay se ejecutan como modos independientes.")
    if args.forzar and (args.listar or args.descargar_todo or (args.cripta is None and not args.gui)):
        parser.error("--forzar requiere iniciar una partida.")
    # La cache incluida pertenece al proyecto, incluso al lanzar main.py desde
    # otra carpeta. Las carpetas personalizadas siguen relativas al comando.
    for campo in ("offline", "datos_dir"):
        valor = getattr(args, campo)
        if valor is not None:
            ruta = Path(valor)
            if ruta == Path(".cache/cripta"):
                ruta = Path(__file__).resolve().parent / ruta
            setattr(args, campo, str(ruta.resolve()))
    return args


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
        if args.verificar:
            from controlador.verificacion import texto_reporte, verificar

            reporte = verificar(sesion, args.verificar, args.version_cripta)
            print(texto_reporte(reporte))
            return 0 if reporte.estado == "resoluble" else 1
        if args.listar or (args.cripta is None and not args.replay and not args.gui) or args.descargar_todo:
            listado = sesion.cliente.listar_criptas()
            sesion.almacen.guardar_lista(listado)
            print(json.dumps(listado, indent=2, ensure_ascii=False))
        if args.cripta is None and not args.replay and not args.gui and not args.descargar_todo:
            print("Selecciona una cripta con --cripta ID.")
            return 0

        sesion.preparar()
        if args.replay:
            return ejecutar_replay(args, sesion.precarga)
        if args.descargar_todo:
            from red.verificacion import preparar_verificacion

            ids = ([args.cripta] if args.cripta is not None
                   else [cripta["id"] for cripta in listado["criptas"]])
            for indice, cripta_id in enumerate(ids):
                if indice:
                    sesion.renovar()
                origen = sesion.cliente.almacen if args.offline is not None else sesion.almacen
                try:
                    datos = preparar_verificacion(
                        sesion.cliente, origen, cripta_id, args.version_cripta)
                except DatosNoDisponibles as error:
                    if args.offline is None:
                        raise
                    raise DatosNoDisponibles(
                        f"Offline: faltan datos para {cripta_id}. "
                        f"Carpeta consultada: {origen.carpeta}. {error}") from error
                preparada = sesion.precarga.preparar_cripta(
                    cripta_id, datos.version, args.version_catalogo)
                sesion.precarga.cargar_contenido([sala.id for sala in preparada.salas])
                if origen.carpeta != sesion.almacen.carpeta:
                    sesion.almacen.guardar_llaves(
                        cripta_id, datos.version, origen.leer_llaves(cripta_id, datos.version))
                print(f"{cripta_id}: {len(preparada.salas)} salas descargadas")
            print(f"Respuestas completas guardadas en {args.datos_dir}")
            return 0

        from controlador.aplicacion import ejecutar_juego
        return ejecutar_juego(args, sesion, crear_lanzador_replay(args))
    except (ErrorCripta, ErrorReplay, ErrorHistoria, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except ModuleNotFoundError as error:
        if error.name != "requests":
            raise
        print("Falta requests. Instálalo con: python -m pip install requests", file=sys.stderr)
        return 1
    finally:
        try:
            sesion.cerrar(reportar=not (args.verificar or args.replay))
        except (ErrorCripta, OSError) as error:
            print(f"Aviso al cerrar la sesion: {error}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
