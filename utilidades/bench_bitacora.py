"""CD-01/02: bitácora real frente a desplazar la lista, sin red ni vista."""
from dataclasses import dataclass
import random
from sys import getsizeof

from utilidades.bitacora import BufferCircular
from utilidades.bench_juego import medir_carga


class ListaDesplazada:
    """Alternativa solo de medición; desplaza referencias al eliminar la primera."""
    __slots__ = ("_datos", "_capacidad")

    def __init__(self, capacidad=20):
        self._datos = []
        self._capacidad = capacidad

    def agregar(self, mensaje):
        self._datos.append(mensaje)
        if len(self._datos) > self._capacidad:
            self._datos.pop(0)

    def ultimos(self):
        return self._datos.copy()

    def vaciar(self):
        self._datos.clear()

    def __len__(self):
        return len(self._datos)


@dataclass(frozen=True, slots=True)
class ResultadoBitacora:
    estrategia: str
    carga: str
    operaciones: int
    muestras_us: tuple[float, ...]
    almacenamiento_max_bytes: int
    capacidad: int = 20

    def imprimir(self):
        muestras = self.muestras_us
        print(f"bitacora/{self.estrategia}/{self.carga}: "
              f"n={self.operaciones} capacidad={self.capacidad} "
              f"promedio={sum(muestras)/len(muestras):.6f} "
              f"min={min(muestras):.6f} max={max(muestras):.6f} us/op "
              f"almacenamiento_max={self.almacenamiento_max_bytes} B")
        print("  Muestras (us/op): " + ", ".join(f"{t:.6f}" for t in muestras))


def _validar_y_medir_almacenamiento(fabrica, mensajes, capacidad):
    """Pasada independiente: no se cronometra ni atribuye cadenas a la estructura."""
    bitacora = fabrica(capacidad)
    maximo = getsizeof(bitacora) + getsizeof(bitacora._datos)
    if bitacora.ultimos() != [] or len(bitacora) != 0:
        raise AssertionError("La bitácora nueva no está vacía.")
    for i, mensaje in enumerate(mensajes, 1):
        bitacora.agregar(mensaje)
        esperado = mensajes[max(0, i - capacidad):i]
        if bitacora.ultimos() != esperado or len(bitacora) != len(esperado):
            raise AssertionError("La bitácora no conserva el sufijo esperado.")
        maximo = max(maximo, getsizeof(bitacora) + getsizeof(bitacora._datos))
    bitacora.vaciar()
    if bitacora.ultimos() != [] or len(bitacora) != 0:
        raise AssertionError("Vaciar no reinició la bitácora.")
    bitacora.agregar(mensajes[0])
    if bitacora.ultimos() != mensajes[:1]:
        raise AssertionError("La bitácora no se reutiliza después de vaciar.")
    return maximo


def medir_bitacora(operaciones, repeticiones, semilla=20261001, capacidad=20):
    """Prepara una carga común, comprueba cada prefijo y mide cuatro alternativas.

    Los bytes son superficiales: instancia más arreglo de referencias, sin cadenas
    compartidas, resultados temporales, entrada ni generador. El máximo se obtiene
    en una pasada separada, fuera de las mediciones de tiempo.
    """
    for valor in (operaciones, repeticiones, capacidad):
        if type(valor) is not int or valor < 1:
            raise ValueError("Operaciones, repeticiones y capacidad deben ser enteros positivos.")
    azar = random.Random(semilla)
    mensajes = [f"mensaje-{i}-{azar.randrange(1 << 32)}" for i in range(operaciones)]
    esperado = mensajes[-capacidad:]
    resultados = []
    for nombre, fabrica in (("circular", BufferCircular), ("desplazada", ListaDesplazada)):
        memoria = _validar_y_medir_almacenamiento(fabrica, mensajes, capacidad)
        for consultar in (False, True):
            carga = "agregar_y_consultar" if consultar else "agregar"

            def preparar():
                bitacora = fabrica(capacidad)
                observado = []

                def ejecutar():
                    if consultar:
                        ultimo = []
                        for mensaje in mensajes:
                            bitacora.agregar(mensaje)
                            ultimo = bitacora.ultimos()
                        observado.append(ultimo)
                    else:
                        for mensaje in mensajes:
                            bitacora.agregar(mensaje)

                def validar():
                    if bitacora.ultimos() != esperado:
                        raise AssertionError("La ejecución medida perdió mensajes.")
                    if consultar and observado != [esperado]:
                        raise AssertionError("La consulta medida no coincide con el sufijo.")
                return ejecutar, validar

            muestra = medir_carga(f"bitacora/{nombre}/{carga}",
                                  operaciones, repeticiones, preparar)
            resultados.append(ResultadoBitacora(nombre, carga, operaciones,
                              tuple(muestra.tiempos_us), memoria, capacidad))
    return resultados
