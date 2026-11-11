from dataclasses import dataclass, field

from red.errores import DatosInvalidos
from red.validacion import entero, identificador
from utilidades.ordenamiento import ordenar


DIRECCIONES = ('N', 'S', 'E', 'O')
LIMITACION = 'Verificación por alcanzabilidad acumulada; no garantiza una trayectoria única si hay salidas sin regreso.'


@dataclass(slots=True)
class SalidaVerificacion:
    origen: int
    direccion: str
    destino: int
    cerrada: bool | None = None
    llave: str | None = None


@dataclass(slots=True)
class SalaVerificacion:
    id: int
    salidas: list[SalidaVerificacion]


@dataclass(slots=True)
class UbicacionLlave:
    id: str
    sala: int
    enemigo: str | None = None


@dataclass(slots=True)
class DatosVerificacion:
    cripta_id: str
    version: str
    sala_inicial: int
    sala_salida: int
    llave_salida: str
    salas: list[SalaVerificacion]
    ubicaciones: list[UbicacionLlave]


@dataclass(slots=True)
class MetricasVerificacion:
    salas_procesadas: int = 0
    salidas_examinadas: int = 0
    llaves_obtenidas: int = 0
    pendientes_activadas: int = 0
    relaciones_diagnostico: int = 0
    comparaciones_normalizacion: int = field(default=0, compare=False)
    elementos_reporte: int = 0


@dataclass(slots=True)
class LlaveInalcanzable:
    id: str
    ubicaciones: list[UbicacionLlave]
    condicion: int


@dataclass(slots=True)
class Condicion:
    tipo: str
    identificador: int | str
    operacion: str
    valor: bool
    requisitos: list[int]
    base: bool = False
    salida: SalidaVerificacion | None = None


@dataclass(slots=True)
class Ciclo:
    llaves: list[str]
    integrantes: list[int]
    testigo: list[int]
    clasificacion: str
    bloqueos_externos: list[tuple[int, int]]


@dataclass(slots=True)
class ResultadoVerificacion:
    estado: str
    cripta_id: str
    version: str | None = None
    modelo: str = 'alcanzabilidad_acumulada'
    limitacion: str = LIMITACION
    orden_llaves: list[str] = field(default_factory=list)
    llaves_inalcanzables: list[LlaveInalcanzable] = field(default_factory=list)
    frontera: list[SalidaVerificacion] = field(default_factory=list)
    evidencia: list[Condicion] = field(default_factory=list)
    ciclos: list[Ciclo] = field(default_factory=list)
    primeras_ubicaciones: list[UbicacionLlave] = field(default_factory=list)
    primeras_entradas: list[SalidaVerificacion] = field(default_factory=list)
    causa: str = ''
    metricas: MetricasVerificacion = field(default_factory=MetricasVerificacion)


@dataclass(slots=True)
class Paso:
    salida: SalidaVerificacion
    origen: int
    destino: int
    llave: int


@dataclass(slots=True)
class DatosNormalizados:
    datos: DatosVerificacion
    salas: list[SalaVerificacion]
    llaves: list[str]
    pasos: list[Paso]
    salidas_por_sala: list[list[int]]
    llaves_por_sala: list[list[int]]
    ubicaciones_por_llave: list[list[UbicacionLlave]]
    inicial: int
    salida: int
    llave_salida: int
    metricas: MetricasVerificacion
    evidencia_salas: list[int] = field(default_factory=list)
    evidencia_llaves: list[int] = field(default_factory=list)


class _ClaveContada:
    __slots__ = ('valor', 'metricas')

    def __init__(self, valor, metricas):
        self.valor = valor
        self.metricas = metricas

    def __lt__(self, otra):
        self.metricas.comparaciones_normalizacion += 1
        return self.valor < otra.valor


def _ordenar(valores, clave, metricas):
    return ordenar(valores, clave=lambda x: _ClaveContada(clave(x), metricas), algoritmo='fusion')


def _buscar(valores, valor, metricas):
    inferior, superior = 0, len(valores)
    while inferior < superior:
        medio = (inferior + superior) // 2
        metricas.comparaciones_normalizacion += 1
        if valores[medio] < valor:
            inferior = medio + 1
        else:
            superior = medio
    if inferior == len(valores) or valores[inferior] != valor:
        raise DatosInvalidos(f'Identificador inexistente: {valor}')
    return inferior


def normalizar(datos):
    if not isinstance(datos, DatosVerificacion):
        raise DatosInvalidos('Se requieren datos completos de verificación.')
    identificador(datos.cripta_id)
    identificador(datos.version)
    identificador(datos.llave_salida)
    entero(datos.sala_inicial, None)
    entero(datos.sala_salida, None)
    if not isinstance(datos.salas, list) or not datos.salas or not isinstance(datos.ubicaciones, list):
        raise DatosInvalidos('Se requieren salas y un listado completo de llaves.')
    metricas = MetricasVerificacion()
    claves = [datos.llave_salida]
    for sala in datos.salas:
        if not isinstance(sala, SalaVerificacion) or not isinstance(sala.salidas, list):
            raise DatosInvalidos('Sala inválida.')
        entero(sala.id, None)
        direcciones = []
        for salida in sala.salidas:
            if not isinstance(salida, SalidaVerificacion):
                raise DatosInvalidos('Salida inválida.')
            entero(salida.origen, None)
            entero(salida.destino, None)
            if salida.origen != sala.id or salida.direccion not in DIRECCIONES or salida.direccion in direcciones:
                raise DatosInvalidos('Origen o dirección de salida inválidos o repetidos.')
            direcciones.append(salida.direccion)
            if salida.cerrada is not None and type(salida.cerrada) is not bool:
                raise DatosInvalidos('El estado de una salida debe ser booleano o nulo.')
            if salida.llave is not None:
                claves.append(identificador(salida.llave))
            if salida.cerrada and salida.llave is None:
                raise DatosInvalidos('Una salida cerrada requiere una llave.')
    for ubicacion in datos.ubicaciones:
        if not isinstance(ubicacion, UbicacionLlave):
            raise DatosInvalidos('Ubicación de llave inválida.')
        claves.append(identificador(ubicacion.id))
        entero(ubicacion.sala, None)
        if ubicacion.enemigo is not None:
            identificador(ubicacion.enemigo)
    salas = _ordenar(datos.salas, lambda s: s.id, metricas)
    ids = [s.id for s in salas]
    if any(ids[i] == ids[i - 1] for i in range(1, len(ids))):
        raise DatosInvalidos('Hay salas duplicadas.')
    inicial = _buscar(ids, datos.sala_inicial, metricas)
    final = _buscar(ids, datos.sala_salida, metricas)
    llaves = []
    for clave in _ordenar(claves, lambda x: x, metricas):
        if not llaves or llaves[-1] != clave:
            llaves.append(clave)
    salidas_por_sala = [[] for _ in salas]
    llaves_por_sala = [[] for _ in salas]
    ubicaciones_por_llave = [[] for _ in llaves]
    pasos = []
    for i, sala in enumerate(salas):
        for salida in _ordenar(sala.salidas, lambda s: DIRECCIONES.index(s.direccion), metricas):
            destino = _buscar(ids, salida.destino, metricas)
            llave = -1 if salida.llave is None else _buscar(llaves, salida.llave, metricas)
            copia = SalidaVerificacion(salida.origen, salida.direccion, salida.destino,
                                       bool(salida.cerrada), salida.llave)
            salidas_por_sala[i].append(len(pasos))
            pasos.append(Paso(copia, i, destino, llave))
    anterior = None
    for u in _ordenar(datos.ubicaciones, lambda x: (x.id, x.sala, x.enemigo or ''), metricas):
        if u == anterior:
            continue
        anterior = u
        sala = _buscar(ids, u.sala, metricas)
        llave = _buscar(llaves, u.id, metricas)
        llaves_por_sala[sala].append(llave)
        ubicaciones_por_llave[llave].append(UbicacionLlave(u.id, u.sala, u.enemigo))
    return DatosNormalizados(datos, salas, llaves, pasos, salidas_por_sala, llaves_por_sala,
                             ubicaciones_por_llave, inicial, final,
                             _buscar(llaves, datos.llave_salida, metricas), metricas)


def recorrer(n):
    alcanzada = [False] * len(n.salas)
    obtenida = [False] * len(n.llaves)
    pendientes = [[] for _ in n.llaves]
    cola = [n.inicial]
    alcanzada[n.inicial] = True
    orden = []
    n.evidencia_salas = [-1] * len(n.salas)
    n.evidencia_llaves = [-1] * len(n.llaves)

    def incorporar(p):
        paso = n.pasos[p]
        if not alcanzada[paso.destino]:
            alcanzada[paso.destino] = True
            n.evidencia_salas[paso.destino] = p
            cola.append(paso.destino)

    lectura = 0
    while lectura < len(cola):
        sala = cola[lectura]
        lectura += 1
        n.metricas.salas_procesadas += 1
        for llave in n.llaves_por_sala[sala]:
            if not obtenida[llave]:
                obtenida[llave] = True
                n.evidencia_llaves[llave] = sala
                orden.append(n.llaves[llave])
                n.metricas.llaves_obtenidas += 1
                for p in pendientes[llave]:
                    n.metricas.pendientes_activadas += 1
                    incorporar(p)
                pendientes[llave].clear()
        for p in n.salidas_por_sala[sala]:
            paso = n.pasos[p]
            n.metricas.salidas_examinadas += 1
            if not paso.salida.cerrada or obtenida[paso.llave]:
                incorporar(p)
            else:
                pendientes[paso.llave].append(p)
    return alcanzada, obtenida, orden


def es_victoria(n, alcanzada, obtenida):
    return obtenida[n.llave_salida] and any(
        p.destino == n.salida and p.llave == n.llave_salida and alcanzada[p.origen]
        for p in n.pasos)


def verificar_resolubilidad(datos):
    n = normalizar(datos)
    alcanzada, obtenida, orden = recorrer(n)
    evidencia, ciclos = ([], []) if es_victoria(n, alcanzada, obtenida) else diagnosticar(n, alcanzada, obtenida)
    return construir_resultado(n, alcanzada, obtenida, orden, evidencia, ciclos)


def construir_resultado(n, alcanzada, obtenida, orden, evidencia, ciclos):
    datos = n.datos
    victoria = es_victoria(n, alcanzada, obtenida)
    resultado = ResultadoVerificacion('resoluble' if victoria else 'no_resoluble',
                                      datos.cripta_id, datos.version, orden_llaves=orden,
                                      metricas=n.metricas)
    resultado.primeras_entradas = [n.pasos[p].salida for p in n.evidencia_salas if p >= 0]
    resultado.primeras_ubicaciones = [
        next(u for u in n.ubicaciones_por_llave[k] if u.sala == n.salas[sala].id)
        for k, sala in enumerate(n.evidencia_llaves) if sala >= 0]
    if not victoria:
        resultado.causa = ('No se obtuvo la llave de salida.' if not obtenida[n.llave_salida]
                           else 'No hay una entrada alcanzable a la salida que declare su llave.')
        resultado.llaves_inalcanzables = [
            LlaveInalcanzable(clave, n.ubicaciones_por_llave[i], len(n.salas) + i)
            for i, clave in enumerate(n.llaves) if not obtenida[i]]
        resultado.frontera = [p.salida for p in n.pasos
                              if alcanzada[p.origen] and p.salida.cerrada and not obtenida[p.llave]]
        resultado.evidencia, resultado.ciclos = evidencia, ciclos
    resultado.metricas.elementos_reporte = (
        len(resultado.orden_llaves) + len(resultado.frontera)
        + len(resultado.primeras_entradas) + len(resultado.primeras_ubicaciones)
        + sum(1 + len(x.ubicaciones) for x in resultado.llaves_inalcanzables)
        + sum(1 + len(x.requisitos) for x in resultado.evidencia)
        + sum(len(x.integrantes) + len(x.testigo) + len(x.bloqueos_externos) for x in resultado.ciclos))
    return resultado


def diagnosticar(n, alcanzada, obtenida):
    v, k = len(n.salas), len(n.llaves)
    condiciones = [Condicion('sala', s.id, 'OR', alcanzada[i], [], i == n.inicial)
                   for i, s in enumerate(n.salas)]
    condiciones.extend(Condicion('llave', llave, 'OR', obtenida[i], [])
                       for i, llave in enumerate(n.llaves))
    for sala, llaves in enumerate(n.llaves_por_sala):
        for llave in llaves:
            condiciones[v + llave].requisitos.append(sala)
    for i, paso in enumerate(n.pasos):
        requisitos = [paso.origen]
        if paso.salida.cerrada:
            requisitos.append(v + paso.llave)
        habilitada = alcanzada[paso.origen] and (not paso.salida.cerrada or obtenida[paso.llave])
        condiciones.append(Condicion('paso', i, 'AND', habilitada, requisitos, salida=paso.salida))
        condiciones[paso.destino].requisitos.append(v + k + i)
    inversa = [[] for _ in condiciones]
    for i, condicion in enumerate(condiciones):
        for requisito in condicion.requisitos:
            n.metricas.relaciones_diagnostico += 1
            inversa[requisito].append(i)
    componentes, asignada = _componentes(condiciones, inversa, n.metricas)
    estructural = [False] * len(condiciones)
    estructural[n.inicial] = True
    cola = [n.inicial]
    lectura = 0
    while lectura < len(cola):
        sala = cola[lectura]
        lectura += 1
        for llave in n.llaves_por_sala[sala]:
            estructural[v + llave] = True
        for p in n.salidas_por_sala[sala]:
            n.metricas.relaciones_diagnostico += 1
            estructural[v + k + p] = True
            destino = n.pasos[p].destino
            if not estructural[destino]:
                estructural[destino] = True
                cola.append(destino)
    ciclos = []
    predecesor = [-1] * len(condiciones)
    for numero, miembros in enumerate(componentes):
        claves = [i for i in miembros if condiciones[i].tipo == 'llave']
        if not claves or (len(miembros) == 1 and miembros[0] not in condiciones[miembros[0]].requisitos):
            continue
        inicio = min(claves)
        testigo = _testigo(inicio, numero, asignada, condiciones, predecesor, n.metricas)
        externos = []
        autonomo = True
        for i in miembros:
            c = condiciones[i]
            internos = 0
            for r in c.requisitos:
                n.metricas.relaciones_diagnostico += 1
                if asignada[r] == numero:
                    internos += 1
                elif not condiciones[r].valor:
                    externos.append((i, r))
            if c.operacion == 'OR':
                autonomo = autonomo and bool(c.requisitos) and internos == len(c.requisitos)
            else:
                autonomo = autonomo and internos > 0
        if not any(estructural[i] for i in miembros):
            clasificacion = 'ciclo_en_region_desconectada'
        elif autonomo:
            clasificacion = 'bloqueo_circular_autonomo'
        else:
            clasificacion = 'dependencia_circular_con_bloqueos_externos'
        ciclos.append(Ciclo([condiciones[i].identificador for i in claves], miembros,
                            testigo, clasificacion, externos))
    return condiciones, ciclos


def _componentes(condiciones, inversa, metricas):
    vista = [False] * len(condiciones)
    finalizados = []
    for raiz, condicion in enumerate(condiciones):
        if vista[raiz] or condicion.valor:
            continue
        vista[raiz] = True
        pila = [(raiz, 0)]
        while pila:
            nodo, posicion = pila[-1]
            adyacentes = condiciones[nodo].requisitos
            if posicion == len(adyacentes):
                finalizados.append(nodo)
                pila.pop()
                continue
            destino = adyacentes[posicion]
            pila[-1] = (nodo, posicion + 1)
            metricas.relaciones_diagnostico += 1
            if not vista[destino] and not condiciones[destino].valor:
                vista[destino] = True
                pila.append((destino, 0))
    asignada = [-1] * len(condiciones)
    componentes = []
    for raiz in reversed(finalizados):
        if asignada[raiz] != -1:
            continue
        numero = len(componentes)
        miembros = []
        pila = [raiz]
        asignada[raiz] = numero
        while pila:
            nodo = pila.pop()
            miembros.append(nodo)
            for destino in inversa[nodo]:
                metricas.relaciones_diagnostico += 1
                if asignada[destino] == -1 and not condiciones[destino].valor:
                    asignada[destino] = numero
                    pila.append(destino)
        componentes.append(miembros)
    return componentes, asignada


def _testigo(inicio, componente, asignada, condiciones, predecesor, metricas):
    primero = next(r for r in condiciones[inicio].requisitos if asignada[r] == componente)
    if primero == inicio:
        return [inicio, inicio]
    cola = [primero]
    predecesor[primero] = primero
    lectura = 0
    while lectura < len(cola) and predecesor[inicio] == -1:
        nodo = cola[lectura]
        lectura += 1
        for r in condiciones[nodo].requisitos:
            metricas.relaciones_diagnostico += 1
            if asignada[r] == componente and predecesor[r] == -1:
                predecesor[r] = nodo
                cola.append(r)
    camino = [inicio]
    actual = inicio
    while actual != primero:
        actual = predecesor[actual]
        camino.append(actual)
    return [inicio] + list(reversed(camino))
