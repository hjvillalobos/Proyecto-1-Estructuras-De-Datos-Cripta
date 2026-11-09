"""Medición local de I1; futura conexión a --bench coordinada con D.

Carga determinista: cadena sin puertas, IDs dispersos, sin azar/red/vista.
No mide viaje automático ni acredita su presupuesto de 5 ms.
"""
import platform
from time import perf_counter_ns
import tracemalloc

from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible


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


def medir_memoria_y_proyeccion(cantidad, repeticiones=50):
    """Memoria incremental del constructor y tiempos sin tracemalloc activo."""
    salas = []
    puertas = []
    for i in range(cantidad):
        salidas = []
        if i:
            salidas.append(SalidaConocible("O", (i - 1) * 1009, 100, i - 1))
        if i + 1 < cantidad:
            salidas.append(SalidaConocible("E", (i + 1) * 1009, 100, i))
            puertas.append(PuertaConocible(i, i * 1009, (i + 1) * 1009))
        salas.append(SalaConocible(i * 1009, "Sala de prueba", tuple(salidas)))
    # Esqueleto ya creado: no se contabiliza como asignación del componente.
    tracemalloc.start()
    try:
        mapa = ConocimientoMapa(salas, puertas, 0)
        memoria, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    for i in range(cantidad):
        mapa.entrar(i * 1009)
        if i + 1 < cantidad:
            mapa.observar_puerta(i * 1009, i, False)
    inicio = perf_counter_ns()
    for _ in range(2000):
        mapa.recuerdo_puerta(cantidad // 2)
    consulta_us = (perf_counter_ns() - inicio) / 2000 / 1000
    inicio = perf_counter_ns()
    for _ in range(repeticiones):
        mapa.mapa_conocido()
    proyeccion_ms = (perf_counter_ns() - inicio) / repeticiones / 1_000_000
    return memoria / 1024, pico / 1024, consulta_us, proyeccion_ms


if __name__ == "__main__":
    print(f"Python {platform.python_version()} | {platform.platform()}")
    print("Carga: cadena, IDs separados por 1009, sin azar (semilla no aplica).")
    print("2000 repeticiones; cada entrada procesa dos salidas y produce dos cambios.")
    print("Salas | preparacion ms | entrada media us | inversion media us | consulta media us")
    for cantidad in (100, 1000, 10000):
        resultado = medir(cantidad)
        print(f"{cantidad} | " + " | ".join(f"{valor:.3f}" for valor in resultado))
    print("Cadena con puertas; mapa completo conocido. Memoria incremental del constructor.")
    print("Salas | viva KiB | pico KiB | consulta puerta us | proyeccion media ms (50 repeticiones)")
    for cantidad in (100, 1000, 10000):
        resultado = medir_memoria_y_proyeccion(cantidad)
        print(f"{cantidad} | " + " | ".join(f"{valor:.3f}" for valor in resultado))
