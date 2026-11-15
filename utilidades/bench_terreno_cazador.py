"""Evaluación sintética de rutas. Ejecutar con python -m utilidades.bench_terreno_cazador."""

from argparse import ArgumentParser
import json
import platform
from random import Random
from statistics import median
from time import perf_counter_ns
import tracemalloc
from types import SimpleNamespace

from modelo.rutas import ContextoRutasReales
from modelo.eventos import ColaEventos
from modelo.historial import HistorialRetroceso
from modelo.inventario import Inventario
from modelo.juego import Motor
from modelo.tipos import FichaCatalogo, InstanciaEnemigo, Jugador, Sala
from utilidades.ordenamiento import ordenar


class HeapObsoleto:
    def __init__(self):
        self.datos = []

    def insertar(self, entrada):
        datos = self.datos
        i = len(datos)
        datos.append(entrada)
        while i and entrada < datos[(i - 1) // 2]:
            padre = (i - 1) // 2
            datos[i] = datos[padre]
            i = padre
        datos[i] = entrada

    def extraer(self):
        datos = self.datos
        primero = datos[0]
        ultimo = datos.pop()
        if datos:
            i = 0
            while 2 * i + 1 < len(datos):
                hijo = 2 * i + 1
                if hijo + 1 < len(datos) and datos[hijo + 1] < datos[hijo]:
                    hijo += 1
                if ultimo <= datos[hijo]:
                    break
                datos[i] = datos[hijo]
                i = hijo
            datos[i] = ultimo
        return primero


def _distancias(grafo, origen, limite, *, heap=None, entrantes=None, destino=None):
    arcos = grafo.adyacencias if entrantes is None else entrantes
    etiquetas = [None] * len(grafo.ids)
    visitados = [False] * len(etiquetas)
    etiquetas[origen] = (0, -1)
    if heap is not None:
        heap.insertar((0, -1, origen))
    expandidos = 0
    while True:
        if heap is None:
            menor = None
            for i, etiqueta in enumerate(etiquetas):
                if etiqueta is not None and not visitados[i]:
                    entrada = (*etiqueta, i)
                    if menor is None or entrada < menor:
                        menor = entrada
            if menor is None:
                break
            costo, primero, actual = menor
        else:
            if not heap.datos:
                break
            costo, primero, actual = heap.extraer()
            if etiquetas[actual] != (costo, primero):
                continue
        visitados[actual] = True
        expandidos += 1
        if actual == destino:
            break
        vecinos = ((arco.destino, arco) for arco in arcos[actual]) if entrantes is None else arcos[actual]
        for vecino, arco in vecinos:
            total = costo + arco.costo
            if arco.puerta.get("cerrada", False) or (limite is not None and total > limite):
                continue
            primer_id = grafo.ids[vecino] if actual == origen else primero
            etiqueta = (total, primer_id)
            if etiquetas[vecino] is None or etiqueta < etiquetas[vecino]:
                etiquetas[vecino] = etiqueta
                if heap is not None:
                    heap.insertar((*etiqueta, vecino))
    return etiquetas, expandidos


def buscar_individual(grafo, origen, destino, limite, *, con_heap=False):
    etiquetas, _ = _distancias(grafo, origen, limite, destino=destino,
                               heap=HeapObsoleto() if con_heap else None)
    if etiquetas[destino] is None:
        return None
    total, primer_id = etiquetas[destino]
    candidatos = (a for a in grafo.adyacencias[origen]
                  if grafo.ids[a.destino] == primer_id and not a.puerta.get("cerrada", False))
    arco = min(candidatos, key=lambda a: a.costo)
    return arco.destino, arco.direccion, arco.costo, total


class CampoInverso:
    def __init__(self, grafo):
        self.grafo = grafo
        self.entrantes = [[] for _ in grafo.ids]
        for origen, arcos in enumerate(grafo.adyacencias):
            for arco in arcos:
                self.entrantes[arco.destino].append((origen, arco))
        self.clave = None
        self.etiquetas = None
        self.aciertos = self.reconstrucciones = self.expandidos = 0
        self.celdas_inicializadas = 0

    def buscar(self, origen, destino, limite, epoca):
        clave = (destino, limite, epoca)
        if clave != self.clave:
            self.reconstruir(destino, limite, epoca)
        else:
            self.aciertos += 1
        mejor = None
        for arco in self.grafo.adyacencias[origen]:
            etiqueta = self.etiquetas[arco.destino]
            if etiqueta is None or arco.puerta.get("cerrada", False):
                continue
            total = arco.costo + etiqueta[0]
            if limite is not None and total > limite:
                continue
            prioridad = (total, self.grafo.ids[arco.destino], arco.costo)
            if mejor is None or prioridad < mejor:
                mejor = prioridad
                resultado = (arco.destino, arco.direccion, arco.costo, total)
        return resultado if mejor is not None else None

    def reconstruir(self, destino, limite, epoca):
        self.etiquetas, expandidos = _distancias(
            self.grafo, destino, limite, heap=HeapObsoleto(), entrantes=self.entrantes)
        self.expandidos += expandidos
        self.celdas_inicializadas += 2 * len(self.grafo.ids)
        self.reconstrucciones += 1
        self.clave = (destino, limite, epoca)

    def liberar(self):
        self.etiquetas = None
        self.clave = None
        self.entrantes.clear()


class CacheConsultas:
    """FIFO acotada para comparar reutilización con recálculo."""

    def __init__(self, buscar, capacidad, *, instrumentar=False):
        if capacidad < 0:
            raise ValueError("La capacidad debe ser no negativa.")
        self.consultar = buscar
        self.capacidad = capacidad
        self.entradas = []
        self.epoca = None
        self.aciertos = self.fallos = self.reemplazos = self.invalidaciones = 0
        self.instrumentar = instrumentar
        self.costos = {fase: {"operaciones": 0, "ns": 0} for fase in
                       ("clave", "insercion", "reemplazo", "invalidacion", "liberacion")}

    def _inicio(self):
        return perf_counter_ns() if self.instrumentar else None

    def _registrar(self, fase, inicio):
        if inicio is not None:
            costo = self.costos[fase]
            costo["ns"] += perf_counter_ns() - inicio
            costo["operaciones"] += 1

    def liberar(self):
        if self.entradas:
            inicio = self._inicio()
            self.entradas.clear()
            self._registrar("liberacion", inicio)

    def buscar(self, origen, destino, limite, epoca):
        if self.epoca != epoca:
            if self.entradas:
                inicio = self._inicio()
                self.invalidaciones += len(self.entradas)
                self.entradas.clear()
                self._registrar("invalidacion", inicio)
            self.epoca = epoca
        inicio = self._inicio()
        clave = (origen, destino, limite)
        self._registrar("clave", inicio)
        for anterior, resultado in self.entradas:
            if anterior == clave:
                self.aciertos += 1
                return resultado
        self.fallos += 1
        resultado = self.consultar(*clave)
        if self.capacidad:
            if len(self.entradas) == self.capacidad:
                inicio = self._inicio()
                self.entradas.pop(0)
                self._registrar("reemplazo", inicio)
                self.reemplazos += 1
            inicio = self._inicio()
            self.entradas.append((clave, resultado))
            self._registrar("insercion", inicio)
        return resultado


def carga_sintetica(vertices, semilla):
    if vertices < 3:
        raise ValueError("Se requieren al menos tres salas.")
    azar = Random(semilla)
    salas = [Sala(i, str(i), {}) for i in range(vertices)]
    for i in range(vertices - 1):
        costo = azar.randint(1, 100)
        salas[i].salidas["E"] = {"sala": i + 1, "costo": costo, "cerrada": False}
        salas[i + 1].salidas["O"] = {"sala": i, "costo": costo, "cerrada": False}
    return salas


def _medir(operacion, repeticiones):
    return _medir_preparada(lambda: None, lambda _: operacion(), repeticiones)


def _medir_preparada(preparar, operar, repeticiones, *, liberar=None):
    tiempos = []
    for _ in range(repeticiones):
        estado = preparar()
        try:
            inicio = perf_counter_ns()
            operar(estado)
            tiempos.append(perf_counter_ns() - inicio)
        finally:
            if liberar is not None:
                liberar(estado)
    estado = preparar()
    tracemalloc.start()
    try:
        operar(estado)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
        if liberar is not None:
            liberar(estado)
    return {"min_ns": min(tiempos), "mediana_ns": median(tiempos),
            "max_ns": max(tiempos), "pico_bytes": pico}


def medir_localidad(tamanos, semilla, repeticiones):
    """Mantiene fijos origen, objetivo y entorno dentro del rango."""
    limite = 100
    resultados = []
    for vertices in tamanos:
        if vertices < 104:
            raise ValueError("Se requieren al menos 104 salas para fijar la región.")
        contexto = ContextoRutasReales(carga_sintetica(vertices, semilla))
        campo = CampoInverso(contexto.grafo)
        consulta = (0, 1, limite)
        ruta = contexto.buscar(*consulta)
        if campo.buscar(*consulta, 0) != ruta:
            raise AssertionError("El campo inverso cambió el resultado local.")
        resultados.append({
            "V": vertices, "limite": limite, "ruta": ruta,
            "expandidos": campo.expandidos, "celdas": campo.celdas_inicializadas,
            "preparacion_entrantes": _medir(lambda: CampoInverso(contexto.grafo), repeticiones),
            "reconstruccion": _medir_preparada(
                lambda: CampoInverso(contexto.grafo),
                lambda nuevo: nuevo.reconstruir(consulta[1], limite, 0), repeticiones),
            "consulta_reutilizada": _medir(lambda: campo.buscar(*consulta, 0), repeticiones),
        })
    return resultados


class AgendaIndexada(ColaEventos):
    """Candidato aislado: posición por secuencia y eliminación inmediata."""

    def __init__(self):
        super().__init__()
        self.posiciones = []

    def insertar(self, tiempo, tipo, referencia):
        self.posiciones.append(len(self._datos))
        return super().insertar(tiempo, tipo, referencia)

    def _intercambiar(self, i, j):
        super()._intercambiar(i, j)
        self.posiciones[self._datos[i].secuencia] = i
        self.posiciones[self._datos[j].secuencia] = j

    def _sube(self, i):
        while i and self._es_menor(self._datos[i], self._datos[self._padre(i)]):
            padre = self._padre(i)
            self._intercambiar(i, padre)
            i = padre

    def _baja(self, i):
        while self._hijo_izq(i) < len(self._datos):
            hijo = self._hijo_izq(i)
            derecha = hijo + 1
            if derecha < len(self._datos) and self._es_menor(self._datos[derecha], self._datos[hijo]):
                hijo = derecha
            if not self._es_menor(self._datos[hijo], self._datos[i]):
                break
            self._intercambiar(i, hijo)
            i = hijo

    def _retirar(self, i):
        self._intercambiar(i, len(self._datos) - 1)
        evento = self._datos.pop()
        evento.en_cola = False
        self.posiciones[evento.secuencia] = None
        if i < len(self._datos):
            if i and self._es_menor(self._datos[i], self._datos[self._padre(i)]):
                self._sube(i)
            else:
                self._baja(i)
        return evento

    def cancelar(self, evento):
        evento.cancelado = True
        i = self.posiciones[evento.secuencia]
        if i is not None:
            self._retirar(i)

    def extraer_minimo(self, *, hasta=None):
        if self._datos and (hasta is None or self._datos[0].tiempo <= hasta):
            return self._retirar(0)
        return None


def medir_agendas(cazadores, cambios, semilla, repeticiones):
    if cazadores < 1 or cambios < 0 or repeticiones < 1:
        raise ValueError("Carga de agenda inválida.")
    azar = Random(semilla)
    ajustes = [(azar.randrange(cazadores), azar.randint(25, 200)) for _ in range(cambios)]

    def preparar(tipo):
        agenda = tipo()
        vigentes = [agenda.insertar(100, "turno_enemigo", actor) for actor in range(cazadores)]
        velocidades = [100] * cazadores
        for actor, velocidad in ajustes:
            anterior = vigentes[actor]
            restante = max(1, anterior.tiempo * velocidades[actor] // velocidad)
            vigentes[actor] = agenda.reprogramar(anterior, restante)
            velocidades[actor] = velocidad
        return agenda, vigentes

    def extraer(agenda, vigentes):
        orden = []
        while (evento := agenda.extraer_minimo()) is not None:
            if evento is not vigentes[evento.referencia] or evento.en_cola or evento.cancelado:
                raise AssertionError("La agenda perdió la identidad o el estado de un evento.")
            orden.append((evento.tiempo, evento.secuencia, evento.referencia))
        return orden

    def medir_extraccion(tipo):
        tiempos = []
        for _ in range(repeticiones):
            agenda, _ = preparar(tipo)
            inicio = perf_counter_ns()
            while agenda.extraer_minimo() is not None:
                pass
            tiempos.append(perf_counter_ns() - inicio)
        return {"min_ns": min(tiempos), "mediana_ns": median(tiempos), "max_ns": max(tiempos)}

    base = None
    mediciones = {}
    for tipo in (ColaEventos, AgendaIndexada):
        agenda, vigentes = preparar(tipo)
        fisicos, validos = len(agenda._datos), len(agenda.pendientes())
        orden = extraer(agenda, vigentes)
        if len(orden) != cazadores or (base is not None and orden != base):
            raise AssertionError("Las agendas difieren en el orden de eventos vigentes.")
        base = orden
        mediciones[tipo.__name__] = {
            "N_fisico": fisicos, "N_valido": validos,
            "preparacion_y_reprogramacion": _medir(lambda: preparar(tipo), repeticiones),
            "extraccion": medir_extraccion(tipo),
        }
    return mediciones


def medir_ciclo_motor(cazadores, semilla, repeticiones):
    """Una espera completa con cazadores y expiraciones de velocidad en memoria."""
    if cazadores < 1 or repeticiones < 1:
        raise ValueError("Carga de ciclo inválida.")

    def preparar(tipo):
        salas = carga_sintetica(4, semilla)
        jugador = Jugador(vida=100, vida_max=100, ataque=1, defensa=1,
                          velocidad=100, tiempo_siguiente=0, inventario=Inventario(1),
                          posicion_actual=3, llaves_obtenidas=[])
        motor = Motor(jugador, salas, semilla)
        motor.cola = tipo()
        motor.historial = HistorialRetroceso(motor.registro_rastro, motor.cola)
        ficha = FichaCatalogo("sintetico", "enemigo", "Cazador", {"rango": None})
        motor.gestor_precarga = SimpleNamespace(
            catalogo=SimpleNamespace(ficha_preparada=lambda _: ficha))
        for i in range(cazadores):
            actor = InstanciaEnemigo(id_instancia=str(i), tipo_catalogo=ficha.id,
                                    comportamiento="cazador", sala_actual=0,
                                    vida=10, vida_max=10, ataque=1, defensa=1,
                                    velocidad=100, tiempo_siguiente=0)
            motor.enemigos_por_sala[0].append(actor)
            actor.evento_pendiente = motor.programar_evento(100, "turno_enemigo", actor)
            motor.cambiar_velocidad(actor, 200)
            actor.evento_velocidad = motor.programar_evento(
                25 + i % 10, "restaurar_velocidad", (actor, 100))
        return motor

    def ejecutar(motor):
        if not motor.ejecutar("esperar").ok:
            raise AssertionError("El motor rechazó la espera sintética.")

    def firma(motor):
        pendientes = motor.cola.pendientes()
        for sala in motor.enemigos_por_sala:
            for actor in sala:
                evento = actor.evento_pendiente
                if (not evento.en_cola or evento.referencia is not actor
                        or not any(p is evento for p in pendientes)):
                    raise AssertionError("Referencia de turno inválida.")
        estado = motor.exportar_estado()
        # La exportación enumera el heap físico, cuyo orden interno puede variar.
        estado.eventos[:] = ordenar(estado.eventos, clave=lambda e: (e.tiempo, e.secuencia))
        velocidades = tuple((actor.id_instancia, actor.velocidad)
                            for sala in motor.enemigos_por_sala for actor in sala)
        return estado, velocidades

    resultados = {}
    anterior = None
    for tipo in (ColaEventos, AgendaIndexada):
        motor = preparar(tipo)
        fisicos_iniciales = len(motor.cola._datos)
        traza = []
        ciclo = motor.ejecutar_ciclo

        def registrar(*args, **kwargs):
            evento = ciclo(*args, **kwargs)
            if evento is not None:
                traza.append((evento.tiempo, evento.secuencia, evento.tipo))
            return evento

        motor.ejecutar_ciclo = registrar
        ejecutar(motor)
        actual = firma(motor), traza
        if anterior is not None and actual != anterior:
            raise AssertionError("Las agendas difieren durante el ciclo del motor.")
        anterior = actual
        resultados[tipo.__name__] = {
            **_medir_preparada(lambda: preparar(tipo), ejecutar, repeticiones),
            "reloj": motor.reloj, "eventos_procesados": len(traza),
            "N_fisico_inicial": fisicos_iniciales,
            "N_fisico": len(motor.cola._datos), "N_valido": len(motor.cola.pendientes()),
        }
    return {"H": cazadores, "semilla": semilla, "repeticiones": repeticiones,
            "agendas": resultados}


def medir_rutas(vertices, cazadores, limite, inestable, semilla, repeticiones):
    if not 1 <= cazadores < vertices or repeticiones < 1:
        raise ValueError("Cantidad de cazadores o repeticiones inválida.")
    consultas = [(origen, destino, limite) for destino in (vertices - 1, vertices - 2)
                 for origen in range(cazadores) if origen != destino]
    estrategias = ("indexado", "lineal", "obsoletos", "inverso", "cache_1", "cache_4")

    def preparar():
        return ContextoRutasReales(carga_sintetica(vertices, semilla))

    def preparar_estrategia(contexto, estrategia, *, instrumentar=False):
        campo = CampoInverso(contexto.grafo) if estrategia == "inverso" else None
        cache = (CacheConsultas(contexto.buscar, int(estrategia[-1]), instrumentar=instrumentar)
                 if estrategia.startswith("cache") else None)
        return campo, cache

    def lote(contexto, estrategia, campo, cache):
        puerta = contexto.grafo.adyacencias[0][0].puerta
        resultados = []
        try:
            for epoca in range(3 if inestable else 1):
                puerta["cerrada"] = epoca == 1
                for consulta in consultas[:1] + consultas + consultas:
                    if campo is not None:
                        valor = campo.buscar(*consulta, epoca)
                    elif cache is not None:
                        valor = cache.buscar(*consulta, epoca)
                    elif estrategia == "indexado":
                        valor = contexto.buscar(*consulta)
                    else:
                        valor = buscar_individual(contexto.grafo, *consulta, con_heap=estrategia == "obsoletos")
                    resultados.append(valor)
        finally:
            puerta["cerrada"] = False
        conteos = {}
        if campo is not None:
            conteos = {"aciertos": campo.aciertos, "reconstrucciones": campo.reconstrucciones,
                       "expandidos": campo.expandidos, "arreglos_por_reconstruccion": vertices}
        if cache is not None:
            conteos = {"aciertos": cache.aciertos, "fallos": cache.fallos,
                       "reemplazos": cache.reemplazos, "invalidaciones": cache.invalidaciones}
            if cache.instrumentar:
                conteos["costos_cache"] = cache.costos
        return resultados, conteos

    def liberar_estrategia(preparados):
        for estrategia in preparados:
            if estrategia is not None:
                estrategia.liberar()

    contexto = preparar()
    referencia, _ = lote(contexto, "lineal", None, None)
    mediciones = {}
    for estrategia in estrategias:
        preparados = preparar_estrategia(contexto, estrategia, instrumentar=True)
        valores, conteos = lote(contexto, estrategia, *preparados)
        liberar_estrategia(preparados)
        if valores != referencia:
            raise AssertionError(f"Resultados distintos para {estrategia}.")

        def preparar_liberacion():
            preparados = preparar_estrategia(contexto, estrategia)
            lote(contexto, estrategia, *preparados)
            return preparados

        mediciones[estrategia] = {
            **_medir_preparada(lambda: preparar_estrategia(contexto, estrategia),
                              lambda preparados: lote(contexto, estrategia, *preparados),
                              repeticiones, liberar=liberar_estrategia), **conteos,
            "preparacion_estrategia": _medir(
                lambda: preparar_estrategia(contexto, estrategia), repeticiones),
            # La limpieza interna de cada consulta sigue incluida en su costo.
            "liberacion_estrategia": _medir_preparada(
                preparar_liberacion, liberar_estrategia, repeticiones),
        }
    return {"V": vertices, "E": 2 * (vertices - 1), "H": cazadores, "limite": limite,
            "inestable": inestable, "semilla": semilla, "repeticiones": repeticiones,
            "preparacion_grafo": _medir(preparar, repeticiones), "lotes": mediciones}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", type=int, default=40)
    parser.add_argument("--semilla", type=int, default=20261113)
    parser.add_argument("--repeticiones", type=int, default=3)
    args = parser.parse_args()
    if args.vertices < 3 or args.repeticiones < 1:
        parser.error("Se requieren al menos tres salas y una repetición.")
    resultados = [medir_rutas(args.vertices, h, limite, inestable, args.semilla, args.repeticiones)
                  for h in (1, min(24, args.vertices - 1))
                  for limite in (100, None) for inestable in (False, True)]
    print(json.dumps({"equipo": platform.platform(), "procesador": platform.processor(),
                      "python": platform.python_version(), "rutas": resultados,
                      "localidad": medir_localidad((128, 512, 2048), args.semilla, args.repeticiones),
                      "agenda_sintetica": medir_agendas(24, 96, args.semilla, args.repeticiones),
                      "ciclo_motor": medir_ciclo_motor(24, args.semilla, args.repeticiones)}, indent=2))


if __name__ == "__main__":
    main()
