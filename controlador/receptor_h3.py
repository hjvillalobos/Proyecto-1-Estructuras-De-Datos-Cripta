from modelo.errores_historia import CambioHistoriaIncoherente, EntradaHistoriaInvalida
from modelo.linea_tiempo import LineaTiempo
from modelo.snapshots import CambioHistorico, EventoHistorico, ValorHistorico


def _tripletas(lote):
    if type(lote) is not tuple or any(type(elemento) is not tuple or len(elemento) != 3 for elemento in lote):
        raise EntradaHistoriaInvalida("El lote H3 debe contener tripletas inmutables.")
    return lote


def _convertir(cambios):
    resultado = []
    for clave, anterior, nuevo in _tripletas(cambios):
        if clave not in ("sala", "jugador"):
            raise EntradaHistoriaInvalida("El receptor H3 solo admite la proyección de sala y jugador.")
        resultado.append(CambioHistorico(clave, ValorHistorico(True, anterior), ValorHistorico(True, nuevo)))
    return tuple(resultado)


class ReceptorH3:
    """Receptor optativo de la proyección acotada de A, sin habilitar una partida histórica completa."""

    def __init__(self, historia):
        if not isinstance(historia, LineaTiempo):
            raise EntradaHistoriaInvalida("El receptor H3 requiere una línea de tiempo de D.")
        self.historia = historia

    def __call__(self, inicio, fin, ordinal, cambios, eventos):
        if type(inicio) is not int or inicio != self.historia.reloj:
            raise CambioHistoriaIncoherente("El inicio del lote H3 no coincide con la frontera histórica.")
        if type(ordinal) is not int or ordinal != self.historia.cantidad_acciones + 1:
            raise CambioHistoriaIncoherente("El ordinal del lote H3 no coincide con la siguiente acción.")
        inmediatos = _convertir(cambios)
        registrados = tuple(EventoHistorico(tiempo, secuencia, _convertir(lote))
                            for tiempo, secuencia, lote in _tripletas(eventos))
        self.historia.registrar_accion(fin, inmediatos, registrados)
