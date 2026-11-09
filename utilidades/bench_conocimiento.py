"""Medición local de I1; futura conexión a --bench coordinada con D.

Carga determinista: cadena sin puertas, IDs dispersos, sin azar/red/vista.
No mide viaje automático ni acredita su presupuesto de 5 ms.
"""
import platform
from time import perf_counter_ns

from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible


def cadena(cantidad):
    salas = []
    for i in range(cantidad):
        salidas = []
        if i:
            salidas.append(SalidaConocible("O", (i - 1) * 1009, 100))
        if i + 1 < cantidad:
            salidas.append(SalidaConocible("E", (i + 1) * 1009, 100))
        salas.append(SalaConocible(i * 1009, "Sala de prueba", tuple(salidas)))
    return tuple(salas)


def medir(cantidad, repeticiones=2000):
    salas = cadena(cantidad)
    inicio = perf_counter_ns()
    mapa = ConocimientoMapa(salas, (), 0)
    preparacion_ms = (perf_counter_ns() - inicio) / 1_000_000
    entrada_ns = inversion_ns = consulta_ns = 0
    for _ in range(repeticiones):
        inicio = perf_counter_ns()
        cambios = mapa.entrar(1009)
        entrada_ns += perf_counter_ns() - inicio
        inicio = perf_counter_ns()
        mapa.revertir(cambios)
        inversion_ns += perf_counter_ns() - inicio
        inicio = perf_counter_ns()
        mapa.estado_sala(1009)
        consulta_ns += perf_counter_ns() - inicio
    return (preparacion_ms, entrada_ns / repeticiones / 1000,
            inversion_ns / repeticiones / 1000, consulta_ns / repeticiones / 1000)


if __name__ == "__main__":
    print(f"Python {platform.python_version()} | {platform.platform()}")
    print("Carga: cadena, IDs separados por 1009, sin azar (semilla no aplica).")
    print("2000 repeticiones; cada entrada procesa dos salidas y produce dos cambios.")
    print("Salas | preparacion ms | entrada media us | inversion media us | consulta media us")
    for cantidad in (100, 1000, 10000):
        resultado = medir(cantidad)
        print(f"{cantidad} | " + " | ".join(f"{valor:.3f}" for valor in resultado))
