"""Adaptador de D para un productor que entregue cambios históricos del motor."""
from dataclasses import replace

from datos.guardado_binario import FormatoIncompatible, GuardadoCorrupto
from datos.historia_binaria import codificar_historia, decodificar_historia
from modelo.linea_tiempo import LineaTiempo


def integrar_historia(motor, checkpoint_cada):
    if callable(getattr(type(motor), "conectar_historia", None)):
        return PartidaHistorica(motor, checkpoint_cada)
    return motor


class PartidaHistorica:
    """Entrega el registro a A y combina su estado vivo con la rama de D."""

    def __init__(self, motor, checkpoint_cada):
        self._motor = motor
        self.linea_tiempo = LineaTiempo(motor.estado_historico_inicial(), checkpoint_cada)
        motor.conectar_historia(self.linea_tiempo)

    def __getattr__(self, nombre):
        return getattr(self._motor, nombre)

    def establecer_notificador(self, notificar):
        self._motor.establecer_notificador(notificar)

    def exportar_estado(self):
        estado = self._motor.exportar_estado()
        if (estado.reloj != self.linea_tiempo.reloj
                or estado.acciones_jugador != self.linea_tiempo.cantidad_acciones):
            raise GuardadoCorrupto("El motor y la historia no coinciden en la frontera de guardado.")
        return replace(estado, historia=codificar_historia(self.linea_tiempo))

    def restaurar_estado(self, estado):
        if estado.historia is None:
            raise FormatoIncompatible("La partida guardada no contiene una historia de Parte II.")
        historia = decodificar_historia(estado.historia)
        if historia.reloj != estado.reloj or historia.cantidad_acciones != estado.acciones_jugador:
            raise GuardadoCorrupto("La historia guardada no coincide con la frontera de la partida.")
        # El productor valida el conocimiento y prepara el estado sin tocar el
        # vivo antes de confirmar juntos la restauración y el nuevo receptor.
        self._motor.restaurar_estado_con_historia(estado, historia)
        self.linea_tiempo = historia
