from dataclasses import dataclass
import random
from time import perf_counter_ns

from modelo.tipos import FichaCatalogo
from red.cache import CacheCatalogoOrdenado


class CacheCatalogoLineal(CacheCatalogoOrdenado):
    def _posicion(self, clave: str) -> int:
        for indice, nodo in enumerate(self.arreglo):
            if nodo.clave >= clave:
                return indice
        return len(self.arreglo)


@dataclass
class Operacion:
    clave: str
    ficha: FichaCatalogo | None = None


@dataclass
class Resultado:
    capacidad: int
    escenario: str
    estrategia: str
    ns_por_operacion: list[float]
    aciertos: int
    fallos: int
    inserciones: int

    @property
    def promedio_us(self) -> float:
        return sum(self.ns_por_operacion) / len(self.ns_por_operacion) / 1000


ESCENARIOS = (
    "aciertos", "fallos", "mixta_90_10", "rotacion_95_5", "rotacion_50_50"
)


def crear_carga(capacidad: int, cantidad: int, escenario: str, semilla: int):
    if capacidad <= 0 or cantidad <= 0:
        raise ValueError("Capacidad y cantidad deben ser positivas.")
    if escenario not in ESCENARIOS:
        raise ValueError(f"Escenario desconocido: {escenario}")
    azar = random.Random(semilla)
    fichas = [
        FichaCatalogo(f"tipo_{i * 2:08d}", "arma", f"Ficha {i}", {})
        for i in range(capacidad)
    ]
    operaciones = []
    for i in range(cantidad):
        indice = azar.randrange(capacidad)
        insertar = (
            escenario == "rotacion_95_5" and i % 20 == 19
            or escenario == "rotacion_50_50" and i % 2 == 1
        )
        if insertar:
            clave = f"tipo_{indice * 2:08d}_nuevo_{i:08d}"
            operaciones.append(Operacion(clave, FichaCatalogo(clave, "arma", clave, {})))
        elif escenario == "fallos" or (escenario == "mixta_90_10" and i % 10 == 9):
            operaciones.append(Operacion(f"tipo_{indice * 2 + 1:08d}"))
        else:
            operaciones.append(Operacion(fichas[indice].id))
    return fichas, operaciones


def ejecutar_carga(cache, operaciones: list[Operacion]) -> tuple[int, int, int]:
    aciertos = fallos = inserciones = 0
    for operacion in operaciones:
        if operacion.ficha is not None:
            cache.insertar(operacion.clave, operacion.ficha)
            inserciones += 1
        elif cache.buscar(operacion.clave) is None:
            fallos += 1
        else:
            aciertos += 1
    return aciertos, fallos, inserciones


def comparar(capacidad: int, cantidad: int, repeticiones: int, semilla: int,
             escenario: str) -> list[Resultado]:
    if repeticiones <= 0:
        raise ValueError("Las repeticiones deben ser positivas.")
    fichas, operaciones = crear_carga(capacidad, cantidad, escenario, semilla)
    estrategias = (CacheCatalogoOrdenado, CacheCatalogoLineal)
    resultados = [
        Resultado(capacidad, escenario, nombre, [], 0, 0, 0)
        for nombre in ("binaria", "lineal")
    ]
    referencia = None
    for repeticion in range(-1, repeticiones):
        orden = (0, 1) if repeticion % 2 == 0 else (1, 0)
        for indice in orden:
            cache = estrategias[indice](capacidad)
            for ficha in fichas:
                cache.insertar(ficha.id, ficha)
            carga = operaciones[:min(1000, cantidad)] if repeticion == -1 else operaciones
            inicio = perf_counter_ns()
            conteos = ejecutar_carga(cache, carga)
            transcurrido = perf_counter_ns() - inicio
            if repeticion == -1:
                continue
            orden_lru = []
            nodo = cache.cabeza.siguiente
            while nodo is not cache.cola:
                orden_lru.append(nodo.clave)
                nodo = nodo.siguiente
            estado = (conteos, orden_lru)
            if referencia is None:
                referencia = estado
            elif estado != referencia:
                raise AssertionError("Las estrategias produjeron resultados distintos.")
            resultado = resultados[indice]
            resultado.ns_por_operacion.append(transcurrido / cantidad)
            resultado.aciertos, resultado.fallos, resultado.inserciones = conteos
    return resultados
