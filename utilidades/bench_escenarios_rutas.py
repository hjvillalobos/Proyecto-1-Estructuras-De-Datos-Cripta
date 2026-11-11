"""I9: cargas sintéticas de diagnóstico. No representa una cripta oficial."""
import platform
from random import Random
from time import perf_counter

from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible


def generar(cantidad, semilla, familia):
    if type(cantidad) is not int or cantidad < 3:
        raise ValueError('Se requieren al menos tres salas.')
    if familia not in ('cadena', 'alternativas', 'dirigido'):
        raise ValueError('Familia desconocida.')
    azar = Random(semilla)
    ids = [i * 17 + 10 for i in range(cantidad)]
    salidas = [[] for _ in ids]
    puertas = []

    def arco(a, b, costo, puerta=None):
        salidas[a].append(SalidaConocible(str(b), ids[b], costo, puerta))

    for i in range(cantidad - 1):
        costo = azar.randint(1, 9)
        puertas.append(PuertaConocible(i, ids[i], ids[i + 1]))
        arco(i, i + 1, costo, i)
        if familia != 'dirigido':
            arco(i + 1, i, costo, i)
    if familia != 'cadena':
        for i in range(cantidad - 2):
            costo = azar.randint(1, 9)
            arco(i, i + 2, costo)
            if familia == 'alternativas':
                arco(i + 2, i, costo)
        arco(cantidad - 1, 0, azar.randint(1, 9))
        if familia == 'alternativas':
            arco(0, cantidad - 1, salidas[-1][-1].costo)
    salas = tuple(SalaConocible(id_sala, str(i), tuple(salidas[i]))
                  for i, id_sala in enumerate(ids))
    mapa = ConocimientoMapa(salas, tuple(puertas), ids[0])
    for id_sala in ids:
        mapa.entrar(id_sala)
    for puerta in puertas:
        mapa.observar_puerta(puerta.extremo_a, puerta.id, False)
    # Destino intermedio: el cierre del anillo no trivializa la consulta.
    return mapa, ids[0], ids[cantidad // 2]


def _medir(planificador, origen, destino):
    inicio = perf_counter()
    resultado = planificador.consultar(origen, destino)
    return resultado, (perf_counter() - inicio) * 1000


def _firma(resultado):
    return (resultado.estado, resultado.siguiente, resultado.direccion,
            resultado.costo_paso, resultado.costo_total)


def comparar(anterior, actual, origen, destino, mapa, invertir_orden=False):
    antes = mapa.mapa_conocido()
    revision = mapa.revision
    if invertir_orden:
        nuevo, t_nuevo = _medir(actual, origen, destino)
        previo, t_previo = _medir(anterior, origen, destino)
    else:
        previo, t_previo = _medir(anterior, origen, destino)
        nuevo, t_nuevo = _medir(actual, origen, destino)
    if _firma(previo) != _firma(nuevo):
        raise AssertionError(f'Resultados distintos: {origen} -> {destino}')
    if antes != mapa.mapa_conocido() or revision != mapa.revision:
        raise AssertionError('La consulta modificó el conocimiento.')
    return nuevo, t_previo, t_nuevo


def medir_escenario(cantidad, semilla, familia, muestras=10):
    from modelo.conocimiento_rutas import PlanificadorConocido
    from modelo.conocimiento_rutas_anterior import PlanificadorConocido as Anterior
    if type(muestras) is not int or muestras < 1:
        raise ValueError('Se requiere al menos una muestra.')
    mapa, origen, destino = generar(cantidad, semilla, familia)
    PlanificadorConocido(mapa)  # Importaciones fuera de la preparación medida.
    nombres = ('preparación', 'primera búsqueda', 'pasos sucesivos', 'cierre', 'reversión')
    filas = [(f'{nombre} {version}', []) for nombre in nombres
             for version in ('anterior', 'actual')]
    for i in range(muestras):
        # Alternar el orden evita favorecer siempre al segundo ejecutado.
        clases = ((Anterior, 0), (PlanificadorConocido, 1))
        planes = [None, None]
        for clase, posicion in (reversed(clases) if i % 2 else clases):
            inicio = perf_counter()
            planes[posicion] = clase(mapa)
            filas[posicion][1].append((perf_counter() - inicio) * 1000)
        _, viejo, nuevo = comparar(*planes, origen, destino, mapa, bool(i % 2))
        filas[2][1].append(viejo)
        filas[3][1].append(nuevo)
    anterior, actual = planes
    paso = actual.consultar(origen, destino)
    for i in range(min(30, cantidad)):
        if paso.estado != 'paso' or paso.siguiente == destino:
            break
        origen_paso = paso.siguiente
        paso, viejo, nuevo = comparar(anterior, actual, origen_paso, destino, mapa, bool(i % 2))
        filas[4][1].append(viejo)
        filas[5][1].append(nuevo)
    for i in range(muestras):
        # Puerta inicial de cada carga: cierre y reversión en filas separadas.
        lote = mapa.observar_puerta(origen, 0, True)
        _, viejo, nuevo = comparar(anterior, actual, origen, destino, mapa, bool(i % 2))
        filas[6][1].append(viejo)
        filas[7][1].append(nuevo)
        mapa.revertir(lote)
        _, viejo, nuevo = comparar(anterior, actual, origen, destino, mapa, bool(i % 2))
        filas[8][1].append(viejo)
        filas[9][1].append(nuevo)
    return filas


def main():
    print(f'Python {platform.python_version()}; {platform.platform()}; semilla=927')
    print('C anterior=ad531fd; mapas sintéticos completamente conocidos, puertas inicialmente abiertas.')
    print('Tiempo de consulta sin generación, observación, validación, red ni vista; no certifica PR-001.')
    for cantidad in (300, 1000, 5000):
        for familia in ('cadena', 'alternativas', 'dirigido'):
            mapa, _, _ = generar(cantidad, 927, familia)
            arcos = sum(len(salidas) for salidas in mapa._salidas)
            print(f'{familia}; V={cantidad}; E={arcos}')
            for nombre, tiempos in medir_escenario(cantidad, 927, familia):
                if tiempos:
                    print(f'  {nombre}: n={len(tiempos)}; media={sum(tiempos)/len(tiempos):.3f} ms; '
                          f'máximo={max(tiempos):.3f} ms')
                else:
                    print(f'  {nombre}: sin pasos intermedios; no se mide')


if __name__ == '__main__':
    main()
