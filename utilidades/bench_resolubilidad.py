from dataclasses import dataclass
from math import log2
from random import Random
from statistics import mean, pstdev
from time import perf_counter

from modelo.resolubilidad import (DatosVerificacion, MetricasVerificacion, SalaVerificacion,
                                  SalidaVerificacion, UbicacionLlave, construir_resultado,
                                  diagnosticar, es_victoria, normalizar, recorrer)


@dataclass(slots=True)
class Muestra:
    total_ms: float
    normalizacion_ms: float
    recorrido_ms: float
    diagnostico_ms: float
    reporte_ms: float


@dataclass(slots=True)
class MedicionResolubilidad:
    cripta_id: str
    version: str
    familia: str
    estrategia: str
    salas: int
    n: int
    muestras: list[Muestra]
    promedio_ms: float
    minimo_ms: float
    maximo_ms: float
    desviacion_ms: float
    metricas: MetricasVerificacion
    trabajo_por_n: float
    comparaciones_por_n_log_n: float
    longitud_max_id: int
    longitud_total_ids: int
    tiempo_por_n_ms: float
    estado: str
    razones_fases: Muestra | None = None
    razon_tiempo_anterior: float | None = None


def generar_datos(tamano, semilla, familia='cadena'):
    if type(tamano) is not int or tamano < 2:
        raise ValueError('El tamaño debe ser un entero de al menos dos salas.')
    if familia not in ('cadena', 'ciclo', 'alternativas'):
        raise ValueError('Familia sintética desconocida.')
    salas, ubicaciones = [], []
    for i in range(tamano):
        salidas = []
        if i + 1 < tamano:
            clave = f'K{i}'
            salidas.append(SalidaVerificacion(i, 'N', i + 1, True, clave))
            ubicaciones.append(UbicacionLlave(clave, i + 1 if familia == 'ciclo' else i))
            if familia == 'alternativas':
                ubicaciones.append(UbicacionLlave(clave, i + 1))
        salas.append(SalaVerificacion(i, salidas))
    azar = Random(semilla)
    azar.shuffle(salas)
    azar.shuffle(ubicaciones)
    return DatosVerificacion(f'sintetica-{familia}', 'sintetica-v1', 0, tamano - 1,
                              f'K{tamano - 2}', salas, ubicaciones)


def _recorrer_repetitivo(n):
    obtenida = [False] * len(n.llaves)
    orden = []
    n.evidencia_salas = [-1] * len(n.salas)
    n.evidencia_llaves = [-1] * len(n.llaves)
    while True:
        alcanzada = [False] * len(n.salas)
        alcanzada[n.inicial] = True
        cola = [n.inicial]
        lectura = 0
        while lectura < len(cola):
            sala = cola[lectura]
            lectura += 1
            n.metricas.salas_procesadas += 1
            for indice in n.salidas_por_sala[sala]:
                paso = n.pasos[indice]
                n.metricas.salidas_examinadas += 1
                if (not paso.salida.cerrada or obtenida[paso.llave]) and not alcanzada[paso.destino]:
                    alcanzada[paso.destino] = True
                    if n.evidencia_salas[paso.destino] == -1 and paso.destino != n.inicial:
                        n.evidencia_salas[paso.destino] = indice
                    cola.append(paso.destino)
        cambio = False
        for sala in cola:
            for llave in n.llaves_por_sala[sala]:
                if not obtenida[llave]:
                    cambio = True
                    obtenida[llave] = True
                    n.evidencia_llaves[llave] = sala
                    orden.append(n.llaves[llave])
                    n.metricas.llaves_obtenidas += 1
        if not cambio:
            return alcanzada, obtenida, orden


def verificar_repetitivo(datos):
    n = normalizar(datos)
    alcanzada, obtenida, orden = _recorrer_repetitivo(n)
    evidencia, ciclos = ([], []) if es_victoria(n, alcanzada, obtenida) else diagnosticar(n, alcanzada, obtenida)
    return construir_resultado(n, alcanzada, obtenida, orden, evidencia, ciclos)


def validar_orden(datos, orden):
    disponibles = []
    for llave in orden:
        if llave in disponibles:
            return False
        alcanzadas = [datos.sala_inicial]
        lectura = 0
        while lectura < len(alcanzadas):
            actual = alcanzadas[lectura]
            lectura += 1
            sala = next(s for s in datos.salas if s.id == actual)
            for salida in sala.salidas:
                if (not salida.cerrada or salida.llave in disponibles) and salida.destino not in alcanzadas:
                    alcanzadas.append(salida.destino)
        if not any(u.id == llave and u.sala in alcanzadas for u in datos.ubicaciones):
            return False
        disponibles.append(llave)
    return True


def _ejecutar_medido(datos, estrategia):
    inicio = perf_counter()
    n = normalizar(datos)
    normalizado = perf_counter()
    alcanzada, obtenida, orden = (recorrer(n) if estrategia == 'incremental' else _recorrer_repetitivo(n))
    recorrido = perf_counter()
    evidencia, ciclos = ([], []) if es_victoria(n, alcanzada, obtenida) else diagnosticar(n, alcanzada, obtenida)
    diagnosticado = perf_counter()
    resultado = construir_resultado(n, alcanzada, obtenida, orden, evidencia, ciclos)
    final = perf_counter()
    muestra = Muestra((final - inicio) * 1000, (normalizado - inicio) * 1000,
                      (recorrido - normalizado) * 1000, (diagnosticado - recorrido) * 1000,
                      (final - diagnosticado) * 1000)
    return resultado, muestra, n


def medir_datos(datos, repeticiones=10, familia='preparada'):
    if type(repeticiones) is not int or repeticiones < 10:
        raise ValueError('Se requieren al menos diez repeticiones.')
    resultados = []
    controles = [_ejecutar_medido(datos, e)[0] for e in ('incremental', 'repetitivo')]
    if controles[0].estado != controles[1].estado:
        raise AssertionError('Los algoritmos discrepan en el dictamen.')
    for control in controles:
        if not validar_orden(datos, control.orden_llaves):
            raise AssertionError('El algoritmo produjo un orden de llaves inválido.')
    for estrategia in ('incremental', 'repetitivo'):
        control = controles[0 if estrategia == 'incremental' else 1]
        muestras = []
        for _ in range(repeticiones):
            resultado, muestra, n = _ejecutar_medido(datos, estrategia)
            if resultado != control:
                raise AssertionError('El resultado no fue determinista.')
            muestras.append(muestra)
        tiempos = [m.total_ms for m in muestras]
        cantidad = len(n.salas) + len(n.pasos) + len(n.llaves) + len(datos.ubicaciones)
        metricas = resultado.metricas
        trabajo = (metricas.salas_procesadas + metricas.salidas_examinadas + metricas.llaves_obtenidas
                   + metricas.pendientes_activadas + metricas.relaciones_diagnostico + metricas.elementos_reporte)
        max_id = max([len(str(s.id)) for s in n.salas] + [len(k) for k in n.llaves])
        resultados.append(MedicionResolubilidad(datos.cripta_id, datos.version, familia, estrategia,
                           len(n.salas), cantidad, muestras, mean(tiempos), min(tiempos), max(tiempos),
                           pstdev(tiempos), metricas, trabajo / cantidad,
                           metricas.comparaciones_normalizacion / (cantidad * log2(max(2, cantidad))), max_id,
                           sum(len(str(s.id)) for s in n.salas) + sum(len(k) for k in n.llaves),
                           mean(tiempos) / cantidad, resultado.estado))
    if controles[0].estado != controles[1].estado:
        raise AssertionError('Los algoritmos discrepan en el dictamen.')
    return resultados


def medir_resolubilidad(tamanos, repeticiones=10, semilla=0):
    tamanos = list(tamanos)
    if len(tamanos) < 3 or any(type(t) is not int or t < 2 for t in tamanos):
        raise ValueError('Se requieren al menos tres tamaños enteros de dos salas o más.')
    if any(b <= a for a, b in zip(tamanos, tamanos[1:])):
        raise ValueError('Los tamaños deben ser crecientes.')
    resultado = []
    for familia in ('cadena', 'ciclo', 'alternativas'):
        anteriores = None
        for tamano in tamanos:
            mediciones = medir_datos(generar_datos(tamano, semilla, familia), repeticiones, familia)
            if anteriores:
                for actual, anterior in zip(mediciones, anteriores):
                    actual.razon_tiempo_anterior = actual.promedio_ms / anterior.promedio_ms
                    campos = ('total_ms', 'normalizacion_ms', 'recorrido_ms', 'diagnostico_ms', 'reporte_ms')
                    medias_actuales = [mean(getattr(m, campo) for m in actual.muestras) for campo in campos]
                    medias_anteriores = [mean(getattr(m, campo) for m in anterior.muestras) for campo in campos]
                    if all(medias_anteriores):
                        actual.razones_fases = Muestra(*(a / b for a, b in zip(medias_actuales, medias_anteriores)))
            resultado.extend(mediciones)
            anteriores = mediciones
    return resultado


@dataclass(slots=True)
class MedicionPreparacion:
    cripta_id: str
    version: str
    muestras_ms: list[float]
    promedio_ms: float
    minimo_ms: float
    maximo_ms: float
    desviacion_ms: float
    solicitudes: int
    alcance: str = 'Lectura local y validación; sin análisis de resolubilidad ni HTTP.'


def medir_preparacion_offline(carpeta, cripta_id, version_cripta=None, repeticiones=10):
    from datos.offline import ClienteOffline
    from red.verificacion import preparar_verificacion
    if type(repeticiones) is not int or repeticiones < 10:
        raise ValueError('Se requieren al menos diez repeticiones.')
    cliente = ClienteOffline(carpeta, version_cripta)
    muestras = []
    for _ in range(repeticiones):
        inicio = perf_counter()
        datos = preparar_verificacion(cliente, cliente.almacen, cripta_id, version_cripta)
        muestras.append((perf_counter() - inicio) * 1000)
    return MedicionPreparacion(cripta_id, datos.version, muestras, mean(muestras), min(muestras),
                               max(muestras), pstdev(muestras), cliente.solicitudes_realizadas)
