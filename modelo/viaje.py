"""Control local I5; propone movimientos, nunca ejecuta el motor ni retroceso."""
from dataclasses import dataclass

from modelo.conocimiento_rutas import ConsultaRuta
from modelo.detencion_viaje import HechosPaso, evaluar_detencion


@dataclass(frozen=True, slots=True)
class PasoViaje:
    numero: int
    origen: int
    ruta: ConsultaRuta


@dataclass(frozen=True, slots=True)
class ResultadoPaso:
    posicion: int
    aceptado: bool
    recibio_dano: bool
    hubo_entrada: bool
    enemigos_al_entrar: bool
    terminado: bool

    def __post_init__(self):
        if type(self.posicion) is not int or self.posicion < 0:
            raise ValueError('Posición inválida.')
        for valor in (self.aceptado, self.recibio_dano, self.hubo_entrada,
                      self.enemigos_al_entrar, self.terminado):
            if type(valor) is not bool:
                raise ValueError('Los hechos requieren booleanos explícitos.')
        if self.enemigos_al_entrar and not self.hubo_entrada:
            raise ValueError('Enemigos al entrar requiere una entrada.')


class ControlViaje:
    """Una propuesta pendiente; uso secuencial desde el futuro controlador.

    Actualizar conocimiento antes de recibir resultado o proponer otro paso.
    Cancelar antes de una restauración externa. No mantiene historial del viaje.
    """

    def __init__(self, planificador):
        self._planificador = planificador
        self._estado = 'inactivo'
        self._posicion = None
        self._destino = None
        self._pendiente = None
        self._causas = ()
        self._numero = 0

    @property
    def estado(self):
        return self._estado

    @property
    def posicion(self):
        return self._posicion

    @property
    def destino(self):
        return self._destino

    @property
    def pendiente(self):
        return self._pendiente

    @property
    def causas(self):
        return self._causas

    def iniciar(self, origen, destino):
        if self._pendiente is not None:
            raise ValueError('Debe resolver o cancelar el paso pendiente.')
        consulta = self._planificador.consultar(origen, destino)
        self._posicion, self._destino = origen, destino
        self._resolver_consulta(consulta)
        return consulta

    def _resolver_consulta(self, consulta):
        self._causas = () if consulta.estado == 'paso' else (consulta.estado,)
        self._estado = 'listo' if consulta.estado == 'paso' else 'detenido'

    def proponer(self):
        if self._pendiente is not None:
            raise ValueError('Ya existe un paso pendiente de resultado.')
        if self._estado != 'listo':
            return None
        consulta = self._planificador.consultar(self._posicion, self._destino)
        if consulta.estado != 'paso':
            self._resolver_consulta(consulta)
            return None
        self._numero += 1
        self._pendiente = PasoViaje(self._numero, self._posicion, consulta)
        self._estado = 'pendiente'
        return self._pendiente

    def registrar_resultado(self, numero, resultado):
        paso = self._pendiente
        if type(numero) is not int or paso is None or paso.numero != numero:
            raise ValueError('El resultado no corresponde al paso pendiente.')
        if type(resultado) is not ResultadoPaso:
            raise ValueError('Se requiere ResultadoPaso.')
        posicion = paso.ruta.siguiente if resultado.aceptado else paso.origen
        if resultado.posicion != posicion or resultado.hubo_entrada != resultado.aceptado:
            raise ValueError('Posición o entrada incompatible con el movimiento.')
        decision = evaluar_detencion(HechosPaso(
            resultado.posicion == self._destino, resultado.recibio_dano,
            resultado.hubo_entrada, resultado.enemigos_al_entrar, True, False))
        causas = decision.causas + (('fin_partida',) if resultado.terminado else ())
        self._posicion = resultado.posicion
        self._pendiente = None
        self._causas = causas
        self._estado = 'detenido' if causas else 'listo'
        return causas

    def cancelar(self):
        self._pendiente = None
        self._causas = ('cancelacion',)
        self._estado = 'detenido'
