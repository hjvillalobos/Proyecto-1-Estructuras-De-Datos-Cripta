import random
from pathlib import Path

from datos.bitacora_replay import RUTA_REPLAY_PREDETERMINADA

from red.errores import ErrorCripta


def ejecutar_juego(args, sesion, lanzador_replay):
    from controlador.controlador import ControladorJuego
    from modelo.juego import crear_juego
    from datos.puntajes import TablaPuntajes

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
        def cargar_datos(funcion, *argumentos, **opciones):
            if args.gui and callable(getattr(type(vista), "ejecutar_tarea", None)):
                return vista.ejecutar_tarea(funcion, *argumentos, **opciones)
            return funcion(*argumentos, **opciones)

        estado_inicial = None
        cripta_solicitada = args.cripta
        if args.gui:
            from datos.guardado_binario import cargar_estado, ErrorGuardado

            def abrir_replay():
                if not Path(RUTA_REPLAY_PREDETERMINADA).is_file():
                    vista.mostrar_error_replay("Aun no hay una partida grabada para reproducir.")
                    return
                try:
                    lanzador_replay(RUTA_REPLAY_PREDETERMINADA)
                except OSError as error:
                    vista.mostrar_error_replay(str(error))

            def ver_puntajes():
                try:
                    vista.mostrar_puntajes(TablaPuntajes("datos_generados/puntajes.jsonl").ranking())
                except OSError as error:
                    vista.mostrar_error_replay(str(error))

            def elegir_inicio():
                nonlocal estado_inicial, semilla
                while True:
                    accion, ruta = vista.mostrar_menu(abrir_replay, ver_puntajes)
                    if accion == "salir":
                        return False
                    estado_inicial = None
                    args.cripta = cripta_solicitada
                    semilla = args.semilla if args.semilla is not None else random.randint(0, 2**32 - 1)
                    if accion == "cargar":
                        try:
                            estado_inicial = cargar_estado(ruta)
                        except (OSError, ErrorGuardado, ValueError) as error:
                            vista.mostrar_error_replay(f"No se pudo cargar: {error}")
                            continue
                        args.cripta = estado_inicial.meta.cripta_id
                        semilla = estado_inicial.meta.semilla
                    return True

            if not elegir_inicio():
                return 0

        # IMPORTANTE:
        # No llamamos preparar_cripta() aquí.
        # crear_juego() se encarga de hacerlo.
        while True:
            try:
                if args.cripta is None:
                    listado = cargar_datos(sesion.cliente.listar_criptas)
                    if args.gui and getattr(vista, "_cerrada", False) is True:
                        return 0
                    sesion.almacen.guardar_lista(listado)
                    lista = listado["criptas"] if isinstance(listado, dict) else listado
                    args.cripta = vista.elegir_cripta(lista)
                    if args.cripta is None:
                        if args.gui and getattr(vista, "_cerrada", False):
                            return 0
                        if args.gui and elegir_inicio():
                            continue
                        return 0
                versiones = (dict(version_cripta=estado_inicial.meta.cripta_version,
                                  version_catalogo=estado_inicial.meta.catalogo_version)
                             if estado_inicial is not None else {
                                 campo: valor for campo, valor in (
                                     ("version_cripta", getattr(args, "version_cripta", None)),
                                     ("version_catalogo", getattr(args, "version_catalogo", None)))
                                 if valor is not None})
                juego = cargar_datos(crear_juego, sesion.precarga, args.cripta, semilla, **versiones)
                if args.gui and getattr(vista, "_cerrada", False) is True:
                    return 0
            except (ErrorCripta, OSError) as error:
                if not args.gui:
                    raise
                vista.mostrar_error_replay(f"No se pudo iniciar la partida: {error}")
                sesion.renovar(tolerar_error=True)
                if not elegir_inicio():
                    return 0
                continue
            controlador = ControladorJuego(
                modelo=juego, vista=vista,
                tabla_puntajes=TablaPuntajes("datos_generados/puntajes.jsonl"),
                lanzador_replay=lanzador_replay,
            )
            if estado_inicial is not None:
                iniciado = controlador.iniciar(estado_inicial=estado_inicial)
                estado_inicial = None
                if iniciado is False:
                    if not args.gui:
                        return 1
                    sesion.renovar(tolerar_error=True)
                    vista.reiniciar_presentacion()
                    if not elegir_inicio():
                        return 0
                    continue
            else:
                controlador.iniciar()
            if args.gui and vista.preguntar_menu_principal() is True:
                vista.reiniciar_presentacion()
                if not elegir_inicio():
                    return 0
                sesion.renovar(tolerar_error=True)
                continue
            if not (args.gui and juego.resultado == "derrota" and vista.preguntar_reinicio()):
                break
            while True:
                try:
                    sesion.renovar(tolerar_error=True)
                    break
                except (ErrorCripta, OSError) as error:
                    vista.mostrar_error_replay(f"No se pudo reiniciar la partida: {error}")
                    if not elegir_inicio():
                        return 0
            semilla = args.semilla if args.semilla is not None else random.randint(0, 2**32 - 1)
            vista.reiniciar_presentacion()
    finally:
        if args.gui:
            vista.cerrar()

    return 0
