
import argparse
import platform

from utilidades.bench_cache import ESCENARIOS, comparar
from utilidades.bench_persistencia import medir_recuperacion


def entero_positivo(texto: str) -> int:
    valor = int(texto)
    if valor <= 0:
        raise argparse.ArgumentTypeError("Debe ser un entero mayor que cero.")
    return valor


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capacidades", nargs="+", type=entero_positivo, default=[25, 250, 2500])
    parser.add_argument("--operaciones", type=entero_positivo, default=10000)
    parser.add_argument("--repeticiones", type=entero_positivo, default=5)
    parser.add_argument("--semilla", type=int, default=20261001)
    parser.add_argument("--escenarios", nargs="+", choices=ESCENARIOS, default=ESCENARIOS)
    parser.add_argument("--sin-disco", action="store_true")
    args = parser.parse_args(argv)

    print(f"Python {platform.python_version()} | {platform.platform()}")
    print(f"Operaciones/carga={args.operaciones}, repeticiones={args.repeticiones}, "
          f"semilla={args.semilla}")
    print("Tiempos en us/operacion: promedio [min, max]. Sin red ni vista.")
    print("Las busquedas miden memoria; recuperacion_disco se mide por separado.")
    print("Mismo arreglo ordenado y LRU; cambia solo la busqueda.")
    print("Rotacion indica % busquedas/inserciones; no garantiza % de aciertos.")
    print("capacidad escenario estrategia promedio [min, max] aciertos/fallos/inserciones")
    for capacidad in args.capacidades:
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


if __name__ == "__main__":
    main()
