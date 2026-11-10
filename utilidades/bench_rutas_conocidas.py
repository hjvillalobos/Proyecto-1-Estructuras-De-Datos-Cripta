"""Diagnóstico sintético de I4; no certifica PR-001 ni reemplaza --bench."""
import platform
from time import perf_counter

from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible
from modelo.conocimiento_rutas import PlanificadorConocido


def main():
    print(f'Python {platform.python_version()}; {platform.platform()}; cadena fija, sin azar, red ni vista')
    for cantidad in (100, 1000, 5000):
        salas = []
        for i in range(cantidad):
            salidas = []
            if i > 0:
                salidas.append(SalidaConocible('O', (i - 1) * 7, 100))
            if i + 1 < cantidad:
                salidas.append(SalidaConocible('E', (i + 1) * 7, 100))
            salas.append(SalaConocible(i * 7, str(i), tuple(salidas)))
        mapa = ConocimientoMapa(tuple(salas), (), 0)
        for sala in salas:
            mapa.entrar(sala.id)
        inicio = perf_counter()
        planificador = PlanificadorConocido(mapa)
        preparacion = (perf_counter() - inicio) * 1000
        destino = salas[-1].id
        planificador.consultar(0, destino)
        total, maximo = 0., 0.
        for _ in range(30):
            inicio = perf_counter()
            paso = planificador.consultar(0, destino)
            duracion = (perf_counter() - inicio) * 1000
            total += duracion
            maximo = max(maximo, duracion)
            assert paso.costo_total == (cantidad - 1) * 100
        print(f'V={cantidad}; E={2 * (cantidad - 1)}; preparación adaptador={preparacion:.3f} ms; '
              f'30 consultas media={total / 30:.3f} ms; máximo={maximo:.3f} ms')


if __name__ == '__main__':
    main()
