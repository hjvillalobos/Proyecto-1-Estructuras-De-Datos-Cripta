"""RC-01: ciclos completos pareados con el productor anterior versionado."""
from copy import deepcopy
from statistics import median
from utilidades.bench_parte_dos import medir_integracion, cadena
from utilidades.referencia_historia_ciclo import MotorHistoriaAnterior
from modelo.partida import MotorPartida


def comparar(salas, semilla, ciclos=120, series=5):
    tiempos = [[], []]
    pasos = [[], []]
    for serie in range(series):
        estados = [None, None]
        for i in (0, 1) if serie % 2 == 0 else (1, 0):
            print(f'Serie {serie + 1}, productor {("anterior", "optimizado")[i]}')
            t, p, estados[i] = medir_integracion(deepcopy(salas), semilla, ciclos,
                tipo_motor=(MotorHistoriaAnterior, MotorPartida)[i])
            tiempos[i].extend(t)
            pasos[i].extend(p)
        if estados[0] != estados[1]:
            raise AssertionError('Estado, historia o azar diferentes entre productores.')
    resultados = []
    for nombre, muestras, viaje in zip(('anterior', 'optimizado'), tiempos, pasos):
        print(f'{nombre}: ciclos={len(muestras)} mediana={median(muestras):.3f} ms '
              f'máximo={max(muestras):.3f} ms sobre20={sum(t > 20 for t in muestras)}')
        resultados.append({'productor': nombre, 'ciclos_ms': muestras, 'pasos_ms': viaje,
                           'estados_historia_azar_iguales': True})
    return resultados


def medir(cantidad, semilla, repeticiones, paquete=None, cripta=None):
    if paquete:
        from datos.offline import ClienteOffline
        from red.precarga import validar_pagina_esqueleto
        cliente = ClienteOffline(paquete)
        datos = cliente.obtener_datos_generales(cripta)
        salas = [s for p in range(1, datos['paginas'] + 1)
                 for s in validar_pagina_esqueleto(cliente.obtener_esqueleto(cripta, p), p, datos['paginas'])]
        print(f"Referencia {cripta}@{datos['version']}, {len(salas)} salas, cero HTTP.")
    else:
        salas = cadena(max(3, cantidad), semilla)
        print('Carga sintética; no sustituye la referencia oficial.')
    return comparar(salas, semilla, 120, repeticiones)
