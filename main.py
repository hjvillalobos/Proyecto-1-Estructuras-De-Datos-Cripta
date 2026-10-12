import argparse
import json
import os
import random
import subprocess
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


def main(argv=None):
    argumentos = sys.argv[1:] if argv is None else list(argv)

    # BENCH
    if "--bench" in argumentos:
        from bench import main as ejecutar_bench

        argumentos.remove("--bench")
        ejecutar_bench(argumentos)
        return 0

    # ARGUMENTOS
    parser = argparse.ArgumentParser(
        description="CRIPTA - Estructuras de Datos II"
    )

    parser.add_argument("--cripta")
    parser.add_argument("--listar", action="store_true")

    parser.add_argument(
        "--offline",
        nargs="?",
        const=".cache/cripta",
        metavar="CARPETA",
    )

    parser.add_argument(
        "--datos-dir",
        default=".cache/cripta",
    )

    parser.add_argument(
        "--cache-size",
        type=entero_positivo,
        default=25,
    )

    parser.add_argument("--version-cripta")
    parser.add_argument("--version-catalogo")

    parser.add_argument(
        "--descargar-todo",
        action="store_true",
    )

    parser.add_argument(
        "--semilla",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--replay",
        metavar="ARCHIVO",
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Jugar en una ventana gráfica (tkinter) en vez de la consola.",
    )

    args = parser.parse_args(argumentos)

    cliente = None
    precarga = None
    catalogo = None

    try:
        # -------------------------------------------------
        # ALMACENAMIENTO
        # -------------------------------------------------

        almacen = AlmacenLocal(args.datos_dir)

        # -------------------------------------------------
        # FUENTE DE DATOS
        # -------------------------------------------------

        if args.offline is not None:
            from datos.offline import ClienteOffline

            cliente = ClienteOffline(args.offline)

        else:
            from red.cliente_api import ClienteApi

            cliente = ClienteApi()

        # -------------------------------------------------
        # LISTAR CRIPTAS
        # -------------------------------------------------

        if (
            args.listar
            or (args.cripta is None and not args.replay and not args.gui)
            or args.descargar_todo
        ):
            listado = cliente.listar_criptas()

            almacen.guardar_lista(listado)

            print(
                json.dumps(
                    listado,
                    indent=2,
                    ensure_ascii=False,
                )
            )

        # Si no se indicó cripta
        if args.cripta is None and not args.replay and not args.gui:
            print(
                "Selecciona una cripta con --cripta ID."
            )
            return 0

        # -------------------------------------------------
        # CATÁLOGO Y PRECARGA
        # -------------------------------------------------

        catalogo = GestorCatalogo(
            cliente,
            CacheCatalogoOrdenado(args.cache_size),
            almacen,
        )

        precarga = GestorPrecarga(
            cliente,
            catalogo,
        )

        # -------------------------------------------------
        # REPLAY
        # -------------------------------------------------

        if args.replay:
            ejecutar_replay(
                args,
                precarga,
                cliente,
            )
            return 0

        # -------------------------------------------------
        # DESCARGAR TODO
        # -------------------------------------------------

        if args.descargar_todo:
            preparada = precarga.preparar_cripta(
                args.cripta,
                args.version_cripta,
                args.version_catalogo,
            )

            precarga.cargar_contenido(
                [
                    sala.id
                    for sala in preparada.salas
                ]
            )

            print(
                f"Respuestas completas guardadas en "
                f"{args.datos_dir}"
            )

            return 0

        # -------------------------------------------------
        # INICIAR JUEGO
        # -------------------------------------------------

        from controlador.controlador import ControladorJuego
        from modelo.juego import crear_juego

        semilla = (
            args.semilla
            if args.semilla is not None
            else random.randint(0, 2**32 - 1)
        )

        if args.gui:
            from vista.grafica import VistaGrafica

            vista = VistaGrafica()
        else:
            from vista.consola import VistaConsola

            vista = VistaConsola()

        try:
            # Con --gui y sin --cripta se elige la cripta en una ventana.
            if args.cripta is None:
                listado = cliente.listar_criptas()
                almacen.guardar_lista(listado)
                lista = (
                    listado["criptas"]
                    if isinstance(listado, dict)
                    else listado
                )
                args.cripta = vista.elegir_cripta(lista)
                if args.cripta is None:
                    return 0

            # IMPORTANTE:
            # No llamamos preparar_cripta() aquí.
            # crear_juego() se encarga de hacerlo.
            juego = crear_juego(
                precarga,
                args.cripta,
                semilla,
            )

            controlador = ControladorJuego(
                modelo=juego,
                vista=vista,
                lanzador_replay=crear_lanzador_replay(args),
            )

            controlador.iniciar()
        finally:
            if args.gui:
                vista.cerrar()

        return 0

    except ErrorCripta as error:
        print(
            f"Error: {error}",
            file=sys.stderr,
        )
        return 1

    except ModuleNotFoundError as error:
        if error.name != "requests":
            raise

        print(
            "Falta requests. "
            "Instálalo con: python -m pip install requests",
            file=sys.stderr,
        )

        return 1

    finally:
        if precarga is not None:
            precarga.cerrar()

        if catalogo is not None:
            print(
                json.dumps(
                    catalogo.reporte(),
                    indent=2,
                    ensure_ascii=False,
                )
            )

        elif cliente is not None:
            print(
                f"Solicitudes de red: "
                f"{cliente.solicitudes_realizadas}"
            )

        if cliente is not None:
            cliente.cerrar()


if __name__ == "__main__":
    raise SystemExit(main())