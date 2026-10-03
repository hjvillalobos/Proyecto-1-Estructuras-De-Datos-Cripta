from pathlib import Path
import tempfile
from time import perf_counter_ns

from datos.almacen import AlmacenLocal
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo


class OrigenMedicion:
    solicitudes_realizadas = 0
    presupuesto_solicitudes = 0

    def obtener_version_catalogo(self):
        return {"version": "medicion"}

    def obtener_catalogo(self, ids):
        raise AssertionError("La recuperación persistente no debe usar la red.")


def medir_recuperacion(capacidad, operaciones, repeticiones):
    muestras = []
    carpeta = Path(".cache")
    carpeta.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=carpeta) as temporal:
        almacen = AlmacenLocal(temporal)
        claves = [f"ficha_{i}" for i in range(capacidad + 1)]
        for clave in claves:
            almacen.guardar_ficha("medicion", {
                "id": clave, "nombre": clave, "clase": "arma", "peso": 1, "valor": 1
            })
        for _ in range(repeticiones):
            cache = CacheCatalogoOrdenado(capacidad)
            catalogo = GestorCatalogo(OrigenMedicion(), cache, almacen)
            catalogo.obtener_fichas(claves[:capacidad])
            catalogo.obtener_fichas([claves[-1]])
            antes = catalogo.recuperaciones_disco
            inicio = perf_counter_ns()
            for i in range(operaciones):
                catalogo.obtener_fichas([claves[i % len(claves)]])
            muestras.append((perf_counter_ns() - inicio) / operaciones / 1000)
            if catalogo.recuperaciones_disco - antes != operaciones:
                raise AssertionError("No se ejercitó una recuperación por operación.")
            if catalogo.cliente.solicitudes_realizadas:
                raise AssertionError("La carga realizó solicitudes de red.")
    return muestras
