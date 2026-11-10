"""Comparación sintética I8; no certifica PR-001 ni reemplaza --bench."""
import platform
from time import perf_counter

from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible
from modelo.conocimiento_rutas import PlanificadorConocido
from modelo.conocimiento_rutas_anterior import PlanificadorConocido as Anterior


def medir(planificador, origen, destino):
    inicio = perf_counter()
    paso = planificador.consultar(origen, destino)
    return paso, (perf_counter() - inicio) * 1000


def firma(paso):
    return (paso.estado, paso.siguiente, paso.direccion, paso.costo_paso, paso.costo_total)


def resumen(nombre, muestras):
    print(f'  {nombre}: media={sum(muestras) / len(muestras):.3f} ms; '
          f'máximo={max(muestras):.3f} ms; n={len(muestras)}')


def main():
    print(f'Python {platform.python_version()}; {platform.platform()}')
    print('Cadena fija, sin azar/red/vista. Referencia C: ad531fd. Tiempos de procesamiento.')
    for cantidad in (100, 1000, 5000):
        salas = []
        medio = cantidad // 2
        for i in range(cantidad):
            salidas = []
            if i > 0:
                salidas.append(SalidaConocible('O', (i - 1) * 7, 100,
                                               1 if i == medio + 1 else None))
            if i + 1 < cantidad:
                salidas.append(SalidaConocible('E', (i + 1) * 7, 100,
                                               1 if i == medio else None))
            salas.append(SalaConocible(i * 7, str(i), tuple(salidas)))
        mapa = ConocimientoMapa(tuple(salas), (PuertaConocible(1, medio * 7, (medio + 1) * 7),), 0)
        for sala in salas:
            mapa.entrar(sala.id)
        mapa.observar_puerta(medio * 7, 1, False)
        destino = salas[-1].id
        print(f'V={cantidad}; E={2 * (cantidad - 1)}')
        PlanificadorConocido(mapa)  # Calentar importación fuera de la medición.
        for clase, nombre in ((Anterior, 'anterior'), (PlanificadorConocido, 'actual')):
            preparacion, primeras = [], []
            for _ in range(10):
                inicio = perf_counter()
                p = clase(mapa)
                preparacion.append((perf_counter() - inicio) * 1000)
                paso, tiempo = medir(p, 0, destino)
                assert paso.costo_total == (cantidad - 1) * 100
                primeras.append(tiempo)
            resumen(nombre + ' preparación', preparacion)
            resumen(nombre + ' primera búsqueda', primeras)
        anterior, actual = Anterior(mapa), PlanificadorConocido(mapa)
        anterior.consultar(0, destino)
        actual.consultar(0, destino)
        for escenario in ('pasos sucesivos', 'puerta cambiante'):
            muestras_antes, muestras_actual = [], []
            for i in range(30):
                origen = (i + 1) * 7
                if escenario == 'puerta cambiante':
                    mapa.observar_puerta(medio * 7, 1, i % 2 == 0)
                antes, t_antes = medir(anterior, origen, destino)
                ahora, t_actual = medir(actual, origen, destino)
                assert firma(antes) == firma(ahora)
                muestras_antes.append(t_antes)
                muestras_actual.append(t_actual)
            resumen('anterior ' + escenario, muestras_antes)
            resumen('actual ' + escenario, muestras_actual)


if __name__ == '__main__':
    main()
