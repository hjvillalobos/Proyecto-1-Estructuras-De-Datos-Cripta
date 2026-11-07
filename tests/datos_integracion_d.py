"""Productores simulados para comprobar el alcance de D."""
import random
from types import SimpleNamespace

from modelo.linea_tiempo import EstadoHistorico
from modelo.snapshots import (CambioHistorico, EstadoGuardado, EventoHistorico, JugadorGuardado,
                              MetaPartida, ResultadoAccion, SalaGuardada, ValorHistorico)


def cambio(clave, anterior, nuevo):
    return CambioHistorico(clave, ValorHistorico(anterior is not None, anterior),
                           ValorHistorico(nuevo is not None, nuevo))


class ProductorPrueba:
    """Fixture pequeño de A/C para validar el consumidor sin editar sus módulos."""
    def __init__(self):
        self.meta = MetaPartida("prueba", "v1", "c1", 42)
        self.reloj = 0
        self.acciones_jugador = 0
        self.sala = 1
        self.vida = 20
        self.azar = random.Random(42)
        self.restauraciones = 0

    def estado_historico_inicial(self):
        return EstadoHistorico((
            ("sala", (1, "Entrada")), ("jugador", (20, 20, 5, 3, 100)),
            ("efectos", ()), ("conocimiento", True),
            ("inventario:00", ("p-1", "pergamino", False)), ("mapa:1", "Entrada explorada"),
        ))

    def conectar_historia(self, historia):
        self.historia = historia

    def establecer_notificador(self, notificar):
        pass

    def ejecutar(self, accion, argumento=None):
        if accion == "retroceso":
            self.historia.recortar(0, (cambio("inventario:00", ("p-1", "pergamino", False), None),))
            self.sala, self.vida, self.reloj, self.acciones_jugador = 1, 20, 0, 0
            self.azar.seed(42)
            return ResultadoAccion(True)
        if accion not in ("mover", "esperar"):
            return ResultadoAccion(False, "Acción rechazada por el productor.")
        cambios = ()
        if accion == "mover" and self.sala == 1:
            self.sala = 2
            cambios = (cambio("sala", (1, "Entrada"), (2, "Patio")),
                       cambio("mapa:2", None, "Patio explorado"),
                       cambio("enemigo:e1", None, ("Sabueso", 10, 10, "cazador")))
        fin = self.reloj + 250
        primer_dano = self.azar.randint(1, 2)
        antes = (self.vida, 20, 5, 3, 100)
        medio = (self.vida - primer_dano, 20, 5, 3, 100)
        self.vida -= primer_dano + 2
        eventos = (
            EventoHistorico(fin, self.acciones_jugador * 2, (cambio("jugador", antes, medio),)),
            EventoHistorico(fin, self.acciones_jugador * 2 + 1,
                            (cambio("jugador", medio, (self.vida, 20, 5, 3, 100)),)),
        )
        self.historia.registrar_accion(fin, cambios, eventos)
        self.reloj = fin
        self.acciones_jugador += 1
        return ResultadoAccion(True)

    def exportar_estado(self):
        jugador = JugadorGuardado(self.sala, self.vida, 20, 5, 3, 100, self.reloj)
        return EstadoGuardado(self.meta, self.reloj, self.acciones_jugador * 2,
                              self.acciones_jugador, 0, self.azar.getstate(), jugador,
                              salas=[SalaGuardada(1), SalaGuardada(2)])

    def restaurar_estado_con_historia(self, estado, historia):
        # La preparación y publicación atómica del estado vivo pertenece al productor.
        self.azar.setstate(estado.rng_estado)
        self.sala, self.vida = estado.jugador.sala_id, estado.jugador.vida
        self.reloj, self.acciones_jugador = estado.reloj, estado.acciones_jugador
        self.restauraciones += 1
        self.conectar_historia(historia)


def reporte_prueba(estado="resoluble", version=None):
    return SimpleNamespace(estado=estado, cripta_id="prueba", version=version, causa="datos faltantes",
                           limitacion="Alcanzabilidad acumulada", orden_llaves=["llave"],
                           llaves_inalcanzables=[], frontera=[], evidencia=[], ciclos=[])
