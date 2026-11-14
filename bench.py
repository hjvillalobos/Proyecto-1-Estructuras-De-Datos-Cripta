
import argparse
import platform

from red.errores import ErrorCripta
from utilidades.bench_cache import ESCENARIOS, comparar
from utilidades.bench_persistencia import medir_recuperacion
from utilidades.bench_juego import (
    medir_agenda, medir_inventario, medir_historial, medir_ordenamientos,
    medir_guardado, medir_ciclo)

SUBSISTEMAS_BASE = ("cache", "agenda", "inventario", "historial", "ordenamiento",
                   "guardado", "ciclo", "historia")
SUBSISTEMAS = SUBSISTEMAS_BASE + ("guardado-historia", "resolubilidad", "parte-dos", "terreno-cazador")


def entero_positivo(texto: str) -> int:
    valor = int(texto)
    if valor <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero mayor que cero.")
    return valor


def _resumen_ms(medicion):
    return (f"{medicion.promedio_ms:.3f} ms [{medicion.minimo_ms:.3f}, "
            f"{medicion.maximo_ms:.3f}] desv. estándar={medicion.desviacion_ms:.3f} ms")


def _imprimir_muestras(muestras):
    print("  Muestras (ms): " + ", ".join(f"{muestra:.3f}" for muestra in muestras))


def _medir_resolubilidad_offline(args):
    from datos.offline import ClienteOffline
    from red.verificacion import preparar_verificacion
    from utilidades.bench_resolubilidad import medir_datos, medir_preparacion_offline

    cliente = ClienteOffline(args.paquete, args.version_cripta)
    datos = preparar_verificacion(cliente, cliente.almacen, args.cripta)
    preparacion = medir_preparacion_offline(
        args.paquete, args.cripta, datos.version, args.repeticiones)
    filas = medir_datos(datos, args.repeticiones, familia="paquete")
    print(f"Paquete offline: {datos.cripta_id}@{datos.version} | salas={len(datos.salas)}")
    print(f"Preparación offline (lectura y validación): {_resumen_ms(preparacion)} "
          f"muestras={len(preparacion.muestras_ms)} "
          f"solicitudes={cliente.solicitudes_realizadas + preparacion.solicitudes}")
    _imprimir_muestras(preparacion.muestras_ms)
    print("Análisis de resolubilidad (normalización, recorrido, diagnóstico y reporte).")
    return filas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capacidades", nargs="+", type=entero_positivo, default=[25, 250, 2500])
    parser.add_argument("--operaciones", type=entero_positivo, default=10000)
    parser.add_argument("--repeticiones", type=entero_positivo,
                        help="Repeticiones por carga (5 por defecto, 10 con resolubilidad).")
    parser.add_argument("--semilla", type=int, default=20261001)
    parser.add_argument("--cambios-historia", type=entero_positivo, default=2,
                        help="Cambios por evento en el benchmark de historia.")
    parser.add_argument("--escenarios", nargs="+", choices=ESCENARIOS, default=ESCENARIOS)
    parser.add_argument("--sin-disco", action="store_true")
    parser.add_argument("--subsistemas", nargs="+", choices=SUBSISTEMAS)
    parser.add_argument("--tamanos", nargs="+", type=entero_positivo, default=[8, 16, 32, 256])
    parser.add_argument("--eventos", type=entero_positivo, default=256)
    parser.add_argument("--salas", type=entero_positivo, default=100)
    parser.add_argument("--paquete", help="Paquete offline para medir ciclo o resolubilidad.")
    parser.add_argument("--cripta", help="ID de la cripta de referencia del paquete.")
    parser.add_argument("--version-cripta", help="Versión local para el benchmark de resolubilidad.")
    args = parser.parse_args(argv)
    if args.subsistemas is None:
        args.subsistemas = SUBSISTEMAS_BASE
    if args.repeticiones is None:
        args.repeticiones = 10 if "resolubilidad" in args.subsistemas else 5
    if bool(args.paquete) != bool(args.cripta):
        parser.error("--paquete y --cripta deben indicarse juntos")
    if args.version_cripta is not None and (not args.paquete or "resolubilidad" not in args.subsistemas):
        parser.error("--version-cripta requiere --subsistemas resolubilidad y un paquete offline")

    print(f"Python {platform.python_version()} | {platform.platform()}")
    print(f"Operaciones/carga={args.operaciones}, repeticiones={args.repeticiones}, "
          f"semilla={args.semilla}")
    print("Tiempos en us/operacion: promedio [min, max]. Sin red ni vista.")
    if "cache" in args.subsistemas:
        print("Las busquedas miden memoria; recuperacion_disco se mide por separado.")
        print("Mismo arreglo ordenado y LRU; cambia solo la busqueda.")
        print("Rotacion indica % busquedas/inserciones; no garantiza % de aciertos.")
        print("capacidad escenario estrategia promedio [min, max] aciertos/fallos/inserciones")
    for capacidad in args.capacidades if "cache" in args.subsistemas else ():
        for escenario in args.escenarios:
            resultados = comparar(capacidad, args.operaciones, args.repeticiones,
                                  args.semilla, escenario)
            for resultado in resultados:
                muestras = resultado.ns_por_operacion
                print(f"{capacidad:5d} {escenario:16s} {resultado.estrategia:7s} "
                      f"{resultado.promedio_us:9.3f} "
                      f"[{min(muestras) / 1000:.3f}, {max(muestras) / 1000:.3f}] "
                      f"{resultado.aciertos}/{resultado.fallos}/{resultado.inserciones}")
            factor = resultados[1].promedio_us / resultados[0].promedio_us
            print(f"  lineal/binaria: {factor:.2f}x (mayor que 1 favorece binaria)", flush=True)
        if not args.sin_disco:
            muestras = medir_recuperacion(capacidad, args.operaciones, args.repeticiones)
            print(f"{capacidad:5d} recuperacion_disco "
                  f"{sum(muestras) / len(muestras):.3f} us/op "
                  f"[{min(muestras):.3f}, {max(muestras):.3f}] red=0", flush=True)

    if "agenda" in args.subsistemas:
        medir_agenda(args.operaciones, args.repeticiones, args.eventos, args.semilla).imprimir()
    if "inventario" in args.subsistemas:
        for tamano in args.tamanos:
            medir_inventario(args.operaciones, args.repeticiones, tamano).imprimir()
    if "historial" in args.subsistemas:
        medir_historial(args.operaciones, args.repeticiones).imprimir()
    if "ordenamiento" in args.subsistemas:
        for resultado in medir_ordenamientos(args.operaciones, args.repeticiones, args.tamanos, args.semilla):
            resultado.imprimir()
    if "guardado" in args.subsistemas and not args.sin_disco:
        for resultado in medir_guardado(args.operaciones, args.repeticiones, args.salas, args.semilla):
            resultado.imprimir()
    if "historia" in args.subsistemas:
        from utilidades.bench_historia import medir_historia

        for fila in medir_historia(args.operaciones, args.repeticiones, args.semilla,
                                  campos=args.salas, cambios_por_evento=args.cambios_historia):
            fila.imprimir()
    if "guardado-historia" in args.subsistemas and not args.sin_disco:
        from utilidades.bench_historia import medir_guardado_historia

        for fila in medir_guardado_historia(args.operaciones, args.repeticiones, args.salas,
                                           args.semilla, args.cambios_historia):
            fila.imprimir()
    if "resolubilidad" in args.subsistemas:
        try:
            from utilidades.bench_resolubilidad import medir_resolubilidad
        except ModuleNotFoundError as error:
            if error.name != "utilidades.bench_resolubilidad":
                raise
            parser.exit(1, "La medición del verificador todavía no está disponible en esta rama.\n")
        try:
            filas = (_medir_resolubilidad_offline(args) if args.paquete
                     else medir_resolubilidad(args.tamanos, args.repeticiones, args.semilla))
        except ErrorCripta as error:
            parser.exit(1, f"Error al medir el paquete {args.paquete}: {error}\n")
        except ValueError as error:
            parser.error(str(error))
        for fila in filas:
            print(f"Resolubilidad {fila.familia} {fila.estrategia} N={fila.n} "
                  f"{_resumen_ms(fila)} muestras={len(fila.muestras)} {fila.estado}")
            if args.paquete:
                _imprimir_muestras(muestra.total_ms for muestra in fila.muestras)
    if "ciclo" in args.subsistemas:
        medir_ciclo(args.operaciones, args.repeticiones, args.eventos, args.semilla,
                    args.paquete, args.cripta)
    if "parte-dos" in args.subsistemas:
        from utilidades.bench_parte_dos import medir
        medir(args.salas, args.semilla, args.repeticiones, args.paquete, args.cripta)
    if "terreno-cazador" in args.subsistemas:
        import json
        from utilidades.bench_terreno_cazador import (
            medir_rutas, medir_localidad, medir_agendas, medir_ciclo_motor)
        resultados = {
            'rutas': [medir_rutas(args.salas, h, limite, inestable, args.semilla, args.repeticiones)
                      for h in (1, min(24, args.salas - 1)) for limite in (100, None)
                      for inestable in (False, True)],
            'localidad': medir_localidad((128, 512, 2048), args.semilla, args.repeticiones),
            'agenda': medir_agendas(24, 96, args.semilla, args.repeticiones),
            'ciclo': medir_ciclo_motor(24, args.semilla, args.repeticiones),
        }
        print(json.dumps(resultados, indent=2))


if __name__ == "__main__":
    main()
