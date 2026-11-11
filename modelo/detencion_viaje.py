"""Decisión pura de detención; no ejecuta ni mantiene un viaje activo.

002-niebla-viaje FR-018. El adaptador futuro suministra hechos del paso
cerrado. Este módulo no deduce daño comparando vidas ni consulta enemigos.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class HechosPaso:
    llegada: bool
    recibio_dano: bool
    hubo_entrada: bool
    enemigos_al_entrar: bool
    ruta_disponible: bool
    cancelado: bool

    def __post_init__(self):
        for valor in (self.llegada, self.recibio_dano, self.hubo_entrada,
                      self.enemigos_al_entrar, self.ruta_disponible, self.cancelado):
            if type(valor) is not bool:
                raise ValueError("Los hechos del paso deben ser booleanos explícitos.")


@dataclass(frozen=True)
class DecisionDetencion:
    causas: tuple[str, ...]

    @property
    def continuar(self):
        return not self.causas


def evaluar_detencion(hechos: HechosPaso) -> DecisionDetencion:
    """Conserva todas las causas en orden fijo; O(1), sin efectos laterales.

    El controlador deberá mantener cancelado hasta iniciar otro viaje. Esta
    función no programa pasos ni reemplaza las comprobaciones del motor.
    """
    if type(hechos) is not HechosPaso:
        raise ValueError("Se requiere un registro HechosPaso.")
    causas = []
    if hechos.cancelado:
        causas.append("cancelacion")
    if hechos.recibio_dano:
        causas.append("dano")
    if hechos.hubo_entrada and hechos.enemigos_al_entrar:
        causas.append("enemigos")
    if hechos.llegada:
        causas.append("llegada")
    if not hechos.ruta_disponible:
        causas.append("sin_ruta")
    return DecisionDetencion(tuple(causas))
