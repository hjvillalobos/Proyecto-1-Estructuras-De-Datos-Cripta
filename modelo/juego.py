# modelo/juego.py

import random
from modelo.eventos import ColaEventos
from modelo.efectos import GestorEfectos
from modelo.tipos import Jugador, InstanciaEnemigo
from modelo.rastro import RegistroRastro


# Costos base de cada acción (§2.3)
COSTOS = {
    "mover": 100,
    "atacar": 100,
    "esperar": 100,
    "usar_objeto": 50,
    "equipar": 50,
    "recoger": 25,
    "soltar": 25,
    "abrir_puerta": 50,
}


def calcular_intervalo(costo, velocidad):
    """intervalo = max(1, costo * 100 // velocidad)  (§2.3)"""
    return max(1, costo * 100 // velocidad)


def calcular_dano(atacante, defensor, azar):
    """daño = max(1, ataque + azar.randint(0,4) - defensa)  (§2.6)"""
    return max(1, atacante.ataque + azar.randint(0, 4) - defensor.defensa)


class Motor:
    def __init__(self, jugador, salas, semilla):
        self.jugador = jugador
        self.salas = salas          # dict {id_sala: Sala} — dato general, no es de los prohibidos en §7
        self.cola = ColaEventos()
        self.azar = random.Random(semilla)   # instancia propia, nunca random global (§2.6)
        self.reloj = 0

        # enemigos activos por sala: {id_sala: [InstanciaEnemigo, ...]}
        self.enemigos_por_sala = {}
        # salas ya visitadas al menos una vez por el jugador (para activación, §2.4)
        self.salas_activadas = set()

        # evento pendiente de cada actor, para poder cancelar/reprogramar (§2.3)
        self.evento_pendiente = {}  # {id(actor): Evento}


        self.efectos = GestorEfectos(self)
        self.sala_de_enemigo = {}          # {id(enemigo): id_sala} — C lo necesita, vos lo mantenés
        self.registro_rastro = RegistroRastro()
        self.registro_rastro.marcar_visita(self.jugador.posicion_actual, 0)  # sala inicial, tiempo 0 (§2.9)
    def activar_enemigos_de_sala(self, id_sala, enemigos_de_la_sala):
        """
        Activa (agenda su primera acción) a los enemigos "dormidos" de una sala
        cuando el jugador entra por primera vez a ella (§2.4).
        """
        if id_sala in self.salas_activadas:
            return
        self.salas_activadas.add(id_sala)

        enemigos_ordenados = sorted(enemigos_de_la_sala, key=lambda e: e.id_instancia)
        for enemigo in enemigos_ordenados:
            self.sala_de_enemigo[id(enemigo)] = id_sala
            intervalo = calcular_intervalo(COSTOS["atacar"], enemigo.velocidad)
            enemigo.tiempo_siguiente = self.reloj + intervalo
            evento = self.cola.insertar(enemigo.tiempo_siguiente, "turno_enemigo", enemigo)
            self.evento_pendiente[id(enemigo)] = evento

        self.enemigos_por_sala.setdefault(id_sala, []).extend(enemigos_de_la_sala)

    def puede_moverse(self, direccion):
        sala_actual = self.salas[self.jugador.posicion_actual]
        salida = sala_actual.salidas.get(direccion)
        if salida is None:
            return False, "No hay salida en esa dirección"
        if salida.get("cerrada"):
            return False, "La puerta está cerrada"
        return True, None

    def abrir_puerta(self, direccion):
        sala_actual = self.salas[self.jugador.posicion_actual]
        salida = sala_actual.salidas.get(direccion)
        if salida is None:
            return False, "No hay puerta en esa dirección"
        llave_necesaria = salida.get("llave")
        if llave_necesaria and llave_necesaria not in self.jugador.llaves_obtenidas:
            return False, "No tenés la llave correcta"  # se rechaza, no consume tiempo (Apéndice B)

        salida["cerrada"] = False
        self._avanzar_actor(self.jugador, COSTOS["abrir_puerta"])

        if "cierre_automatico" in salida:
            tiempo_cierre = self.reloj + salida["cierre_automatico"]
            self.cola.insertar(tiempo_cierre, "cierre_puerta", (sala_actual, direccion))

        return True, None

    def mover(self, direccion, contenido_sala_destino_cargado):
        """
        contenido_sala_destino_cargado: True si B ya garantizó que el
        contenido de la sala destino está en memoria (§4.2). El motor NO debe
        confirmar el movimiento si esto es False.
        """
        puede, error = self.puede_moverse(direccion)
        if not puede:
            return False, error
        if not contenido_sala_destino_cargado:
            return False, "Contenido de la sala destino aún no disponible"

        id_destino = self.salas[self.jugador.posicion_actual].salidas[direccion]["sala"]
        sala_destino = self.salas[id_destino]
        self.jugador.posicion_actual = id_destino
        self._avanzar_actor(self.jugador, COSTOS["mover"])
        self.registro_rastro.marcar_visita(id_destino, self.reloj)

        # activar enemigos dormidos de la sala destino, si los hay
        enemigos = self.enemigos_por_sala.get(id_destino, [])
        self.activar_enemigos_de_sala(id_destino, enemigos)

        # activar trampa armada de la sala destino, inmediatamente después
        # de completar el movimiento, antes de procesar el siguiente evento (§2.10)
        trampa = getattr(sala_destino, "trampa", None)
        if trampa is not None:
            self.efectos.activar_trampa(trampa, trampa.dano, trampa.rearme)

        return True, None

    def atacar(self, atacante, defensor):
        dano = calcular_dano(atacante, defensor, self.azar)
        defensor.vida = max(0, defensor.vida - dano)

        if defensor.vida == 0:
            self._matar(defensor)

        self._avanzar_actor(atacante, COSTOS["atacar"])

        return dano

    def _matar(self, actor):
        """Cancela los eventos futuros del actor muerto (§2.6, §4.1)."""
        evento = self.evento_pendiente.get(id(actor))
        if evento is not None:
            self.cola.cancelar(evento)
            del self.evento_pendiente[id(actor)]



    def cambiar_velocidad(self, actor, velocidad_nueva):
        evento_viejo = self.evento_pendiente.get(id(actor))
        velocidad_anterior = actor.velocidad
        actor.velocidad = velocidad_nueva

        if evento_viejo is None:
            return  # no tenía nada pendiente, no hay qué reprogramar

        restante = max(1, (evento_viejo.tiempo - self.reloj) * velocidad_anterior // velocidad_nueva)
        nuevo_tiempo = self.reloj + restante
        nuevo_evento = self.cola.reprogramar(evento_viejo, nuevo_tiempo)
        self.evento_pendiente[id(actor)] = nuevo_evento

    def _avanzar_actor(self, actor, costo):
        intervalo = calcular_intervalo(costo, actor.velocidad)
        actor.tiempo_siguiente = self.reloj + intervalo
        evento_viejo = self.evento_pendiente.get(id(actor))
        if evento_viejo is not None:
            self.cola.cancelar(evento_viejo)
        tipo_evento = "turno_jugador" if actor is self.jugador else "turno_enemigo"
        nuevo = self.cola.insertar(actor.tiempo_siguiente, tipo_evento, actor)
        self.evento_pendiente[id(actor)] = nuevo

    def _ejecutar_turno_enemigo(self, enemigo, decidir_accion_enemigo):
        id_sala = self.sala_de_enemigo[id(enemigo)]
        sala_actual = self.salas[id_sala]
        jugador_en_sala = (self.jugador.posicion_actual == id_sala)

        accion, dato = decidir_accion_enemigo(
            enemigo, sala_actual, jugador_en_sala,
            self.registro_rastro, self.azar, self.reloj
        )

        if accion == "atacar":
            self.atacar(enemigo, self.jugador)
        elif accion == "mover":
            direccion = dato
            nuevo_id = sala_actual.salidas[direccion]["sala"]
            lista_origen = self.enemigos_por_sala.get(id_sala, [])
            if enemigo in lista_origen:
                lista_origen.remove(enemigo)
            self.enemigos_por_sala.setdefault(nuevo_id, []).append(enemigo)
            self.sala_de_enemigo[id(enemigo)] = nuevo_id
            self._avanzar_actor(enemigo, COSTOS["mover"])
        else:  # "esperar"
            self._avanzar_actor(enemigo, COSTOS["esperar"])

    def ejecutar_ciclo(self, decidir_accion_enemigo):
        """
        Saca el evento más próximo y lo ejecuta.
        decidir_accion_enemigo: función que decide la acción de un enemigo
        en su turno (la entrega Persona C en enemigos.py; mientras tanto
        usamos un stub temporal).
        Devuelve el evento ejecutado, o None si la cola quedó vacía.
        """
        evento = self.cola.extraer_minimo()
        if evento is None:
            return None

        self.reloj = evento.tiempo

        if evento.tipo == "turno_enemigo":
            decidir_accion_enemigo(evento.referencia, self)
        elif evento.tipo == "pulso_veneno":
            self.efectos.ejecutar_pulso_veneno(evento.referencia)
        elif evento.tipo == "fin_veneno":
            self.efectos.ejecutar_fin_veneno(evento.referencia)
        elif evento.tipo == "pulso_regeneracion":
            enemigo, cantidad, intervalo = evento.referencia
            self.efectos.ejecutar_pulso_regeneracion(enemigo, cantidad, intervalo)
        elif evento.tipo == "apagar_antorcha":
            self.efectos.ejecutar_apagar_antorcha(evento.referencia)
        elif evento.tipo == "rearmar_trampa":
            self.efectos.ejecutar_rearmar_trampa(evento.referencia)
        elif evento.tipo == "cierre_puerta":
            sala, direccion = evento.referencia
            self.efectos.ejecutar_cierre_puerta(sala, direccion)
        elif evento.tipo == "turno_jugador":
            pass  # el jugador decide su acción vía la vista/controlador, no acá

        return evento