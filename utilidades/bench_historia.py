"""Comparación de historia sintética con cambios deterministas y sin red."""
from dataclasses import dataclass
from random import Random
from statistics import mean, median
from time import perf_counter_ns
import tracemalloc

from datos.historia_binaria import codificar_historia
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from modelo.snapshots import CambioHistorico, EventoHistorico, ValorHistorico
from utilidades.ordenamiento import ordenar


@dataclass(frozen=True)
class MedicionHistoria:
    k: int | None
    controles: int
    memoria: int
    pico: int
    bytes_guardados: int
    max_acciones: int
    busqueda: tuple
    reconstruccion: tuple
    total: tuple
    inversa: tuple
    recorte: tuple

    def imprimir(self):
        nombre = self.k if self.k is not None else "sin controles"
        print(f"Historia K={nombre} | controles={self.controles} "
              f"memoria={self.memoria} B pico={self.pico} B CRLH={self.bytes_guardados} B "
              f"máx. acciones={self.max_acciones}")
        for etiqueta, muestras in (("búsqueda", self.busqueda),
                                   ("reconstrucción", self.reconstruccion),
                                   ("total", self.total), ("inversa", self.inversa),
                                   ("recorte", self.recorte)):
            p95 = ordenar(muestras)[(95 * len(muestras) + 99) // 100 - 1]
            print(f"  {etiqueta:15s} ms media={mean(muestras)/1e6:.4f} "
                  f"mediana={median(muestras)/1e6:.4f} "
                  f"p95={p95/1e6:.4f} máx={max(muestras)/1e6:.4f} "
                  f">50 ms={sum(m > 50_000_000 for m in muestras)}/{len(muestras)}")


def _carga(acciones, campos, semilla, cambios_por_evento):
    azar = Random(semilla)
    claves = [f"campo:{i:08}" for i in range(campos)]
    valores = [0] * campos
    base = EstadoHistorico(zip(claves, valores))
    registros = []
    for i in range(acciones):
        cambios = []
        for _ in range(cambios_por_evento):
            indice = azar.randrange(campos)
            viejo = valores[indice]
            nuevo = viejo + azar.randint(1, 6)
            cambios.append(CambioHistorico(claves[indice], ValorHistorico(True, viejo),
                                           ValorHistorico(True, nuevo)))
            valores[indice] = nuevo
        registros.append((i * 10 + 10, EventoHistorico(i * 10 + 5, i, tuple(cambios))))
    return base, registros


def _construir(base, registros, k):
    historia = LineaTiempo(base, k)
    for fin, evento in registros:
        historia.registrar_accion(fin, eventos=(evento,))
    return historia


def _reconstruccion_inversa(historia, tiempo, completas):
    estado = historia._actual.copiar()
    for i in range(historia.cantidad_acciones - 1, completas - 1, -1):
        accion = historia._accion(i)
        cambios = accion.cambios if tiempo <= accion.inicio else ()
        for evento in reversed(accion.eventos):
            if evento.tiempo > tiempo:
                for cambio in reversed(evento.cambios):
                    estado.aplicar(CambioHistorico(cambio.clave, cambio.nuevo, cambio.anterior))
        for cambio in reversed(cambios):
            estado.aplicar(CambioHistorico(cambio.clave, cambio.nuevo, cambio.anterior))
    return estado


def medir_guardado_historia(acciones, repeticiones, salas, semilla, cambios_por_evento=2):
    from utilidades.bench_juego import medir_guardado

    base, registros = _carga(acciones, salas, semilla, cambios_por_evento)
    historia = _construir(base, registros, 50)
    return medir_guardado(acciones, repeticiones, salas, semilla, historia=historia)


def medir_historia(acciones, repeticiones, semilla, *, campos=256, consultas=32,
                   cambios_por_evento=2):
    base, registros = _carga(acciones, campos, semilla, cambios_por_evento)
    azar = Random(semilla + 1)
    final = acciones * 10
    tiempos = (0, 1, final // 2, max(0, final - 1), final,
               *[azar.randrange(final + 1) for _ in range(consultas)])
    referencia = _construir(base, registros, acciones + 1)
    esperados = [referencia.consultar_t(t).estado.campos() for t in tiempos]
    filas = []
    for k in (10, 50, 100, None):
        # Los cambios compartidos también cuentan en memoria. Se miden sobre
        # una carga nueva, construida dentro de tracemalloc para cada variante.
        tracemalloc.start()
        try:
            base_medida, registros_medidos = _carga(acciones, campos, semilla, cambios_por_evento)
            historia = _construir(base_medida, registros_medidos, k or acciones + 1)
            del base_medida, registros_medidos
            memoria, pico = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

        for t in tiempos:  # calentamiento
            historia.consultar_t(t)
        busqueda, reconstruccion, total, inversa, recorte = [], [], [], [], []
        max_acciones = 0
        for _ in range(repeticiones):
            for t, esperado in zip(tiempos, esperados):
                inicio = perf_counter_ns()
                completas = historia._buscar_acciones_completas(t)
                busqueda.append(perf_counter_ns() - inicio)
                inicio = perf_counter_ns()
                historia._consultar_desde(t, completas)
                reconstruccion.append(perf_counter_ns() - inicio)
                inicio = perf_counter_ns()
                resultado = historia.consultar_t(t)
                total.append(perf_counter_ns() - inicio)
                inicio = perf_counter_ns()
                alternativa = _reconstruccion_inversa(historia, t, completas)
                inversa.append(perf_counter_ns() - inicio)
                if resultado.estado.campos() != esperado or alternativa.campos() != esperado:
                    raise AssertionError("Las reconstrucciones no coinciden.")
                max_acciones = max(max_acciones, resultado.acciones_reconstruidas)
            for prefijo in (acciones // 4, acciones // 2, max(0, acciones - 5)):
                rama = _construir(base, registros[:prefijo + 5], k or acciones + 1)
                inicio = perf_counter_ns()
                rama.recortar(prefijo)
                recorte.append(perf_counter_ns() - inicio)
                if rama.cantidad_acciones != prefijo:
                    raise AssertionError("El recorte retuvo un sufijo.")
        filas.append(MedicionHistoria(k, historia.cantidad_puntos_control, memoria, pico,
                                     len(codificar_historia(historia)), max_acciones,
                                     tuple(busqueda), tuple(reconstruccion), tuple(total),
                                     tuple(inversa), tuple(recorte)))
    return filas
