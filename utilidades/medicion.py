
import gc
import time
from dataclasses import dataclass

from utilidades.ordenamiento import ordenar


@dataclass
class Medicion:
    mediana_ms: float
    minimo_ms: float
    repeticiones: int


def medir(fn, repeticiones=5, preparar=None):
    """Ejecuta fn() `repeticiones` veces y devuelve mediana y mínimo en milisegundos.

    preparar : función opcional que se ejecuta ANTES de cada repetición y NO se mide
               (ej. reconstruir la lista que fn va a consumir).
    Se usa la mediana porque un pico aislado (GC, otro proceso) no la distorsiona."""
    tiempos = []
    for _ in range(repeticiones):
        if preparar is not None:
            preparar()
        gc.collect()
        gc.disable()
        try:
            t0 = time.perf_counter()
            fn()
            t1 = time.perf_counter()
        finally:
            gc.enable()
        tiempos.append((t1 - t0) * 1000.0)
    ordenados = ordenar(tiempos)     # usamos nuestro propio ordenamiento, no sorted()
    return Medicion(ordenados[len(ordenados) // 2], ordenados[0], repeticiones)


class Reporte:
    """Imprime secciones y filas alineadas. Mantener el formato simple facilita pegar los
    resultados en el Documento de Decisiones."""

    def __init__(self, salida=print):
        self._salida = salida
        self._anchos = None

    def seccion(self, titulo, columnas=None):
        self._salida("")
        self._salida("=" * 78)
        self._salida(titulo)
        self._salida("=" * 78)
        self._anchos = None
        if columnas:
            self.fila(*columnas)
            self._salida("-" * 78)

    def nota(self, texto):
        self._salida(f"  {texto}")

    def fila(self, *celdas, anchos=None):
        if anchos is not None:
            self._anchos = anchos
        if self._anchos is None:
            self._anchos = [max(12, len(str(c)) + 2) for c in celdas]
        partes = []
        for i, c in enumerate(celdas):
            ancho = self._anchos[i] if i < len(self._anchos) else 12
            partes.append(str(c).ljust(ancho))
        self._salida("".join(partes).rstrip())