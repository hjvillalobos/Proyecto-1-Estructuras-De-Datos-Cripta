# modelo/historial.py

HISTORIAL_MAX = 5  # acciones del jugador hacia atrás, como máximo (§2.11, §4.6)


class RegistroTurno:
    """
    Guarda únicamente los deltas necesarios para deshacer todo lo ocurrido
    entre una acción del jugador y la siguiente (§2.11) — nunca una copia
    completa del estado del juego.
    """

    def __init__(self, reloj_anterior: int):
        self.reloj_anterior = reloj_anterior
        self.cambios_vida = []        # [(actor, vida_anterior), ...]
        self.cambios_rastro = []      # [(sala_id, tiempo_anterior), ...]
        self.eventos_creados = []     # [Evento, ...] -> cancelar al revertir
        self.eventos_cancelados = []  # [Evento, ...] -> reactivar al revertir
        self.cambios_inventario = []  # [callable_sin_argumentos, ...]
        self.cambios_puertas = []     # [(salida_dict, campo, valor_anterior), ...]

    def registrar_vida(self, actor, vida_anterior: int):
        self.cambios_vida.append((actor, vida_anterior))

    def registrar_rastro(self, sala_id: int, tiempo_anterior):
        self.cambios_rastro.append((sala_id, tiempo_anterior))

    def registrar_evento_creado(self, evento):
        self.eventos_creados.append(evento)

    def registrar_evento_cancelado(self, evento):
        self.eventos_cancelados.append(evento)

    def registrar_inventario(self, deshacer):
        """`deshacer` es una función sin argumentos que revierte
        exactamente una operación de inventario, construida con las
        primitivas de Inventario (insertar_despues/quitar_nodo/
        mover_despues) por quien haga la operación original.

        IMPORTANTE (§2.11): si la operación afecta a un pergamino de
        retroceso (recogerlo o soltarlo), quien llama NO debe registrar un
        `deshacer` para ese cambio puntual — la cantidad de pergaminos
        queda excluida del alcance de la reversión."""
        self.cambios_inventario.append(deshacer)

    def registrar_puerta(self, salida_dict, campo: str, valor_anterior):
        self.cambios_puertas.append((salida_dict, campo, valor_anterior))


class HistorialRetroceso:
    """
    Pila de como máximo HISTORIAL_MAX turnos (§4.6), implementada a mano
    sobre una list (permitida como arreglo de bajo nivel, §7): apilar
    agrega al final y, si se supera el límite, se descarta el más viejo
    (índice 0).

    Se construye con una referencia al RegistroRastro del jugador para
    poder revertir directamente los cambios de rastro. Los cambios de vida
    se revierten escribiendo `actor.vida` porque Actor ya expone ese campo
    en el contrato compartido (modelo/tipos.py). El reloj virtual anterior
    se devuelve como dato: quien mantenga el reloj (Persona A, en su motor)
    decide cómo reasignarlo, ya que hoy no hay un objeto "reloj" compartido
    en el contrato.

    Ganchos que debe invocar Persona A mientras ejecuta el intervalo entre
    dos acciones del jugador: registrar_vida, registrar_rastro,
    registrar_evento_creado, registrar_evento_cancelado, registrar_puerta.
    Ganchos que invoca Persona C (inventario.py) al recoger/soltar/equipar:
    registrar_inventario.
    """

    def __init__(self, registro_rastro):
        self._registro_rastro = registro_rastro
        self._turnos = []           # pila manual, tope HISTORIAL_MAX
        self._turno_actual = None   # RegistroTurno en construcción

    # --- ciclo de vida de un turno ---

    def iniciar_turno(self, reloj_actual: int):
        """Se llama justo antes de ejecutar una acción del jugador."""
        self._turno_actual = RegistroTurno(reloj_actual)

    def cerrar_turno(self):
        """Se llama cuando el jugador vuelve a tener una decisión, es
        decir, cuando termina el intervalo que este turno debe poder
        revertir. Empuja el turno a la pila y descarta el más viejo si se
        supera HISTORIAL_MAX."""
        if self._turno_actual is None:
            return
        self._turnos.append(self._turno_actual)
        if len(self._turnos) > HISTORIAL_MAX:
            self._turnos.pop(0)
        self._turno_actual = None

    # --- ganchos de registro durante el intervalo ---

    def registrar_vida(self, actor, vida_anterior: int):
        if self._turno_actual is not None:
            self._turno_actual.registrar_vida(actor, vida_anterior)

    def registrar_rastro(self, sala_id: int, tiempo_anterior):
        if self._turno_actual is not None:
            self._turno_actual.registrar_rastro(sala_id, tiempo_anterior)

    def registrar_evento_creado(self, evento):
        if self._turno_actual is not None:
            self._turno_actual.registrar_evento_creado(evento)

    def registrar_evento_cancelado(self, evento):
        if self._turno_actual is not None:
            self._turno_actual.registrar_evento_cancelado(evento)

    def registrar_inventario(self, deshacer):
        if self._turno_actual is not None:
            self._turno_actual.registrar_inventario(deshacer)

    def registrar_puerta(self, salida_dict, campo: str, valor_anterior):
        if self._turno_actual is not None:
            self._turno_actual.registrar_puerta(salida_dict, campo, valor_anterior)

    # --- pergamino de retroceso (§2.11) ---

    def hay_turno_para_revertir(self) -> bool:
        return len(self._turnos) > 0

    def cantidad_turnos(self) -> int:
        return len(self._turnos)

    def usar_pergamino(self, inventario, tipo_pergamino: str = "itm_pergamino_retroceso"):
        """
        Revierte el turno más reciente. No consume tiempo virtual y no
        abre un nuevo turno de historial (§2.11): por eso este método NO
        llama iniciar_turno/cerrar_turno. El pergamino se descuenta
        DESPUÉS de revertir y sin registrarse como delta, para que la
        propia reversión no lo devuelva (excepción explícita de §2.11).

        Devuelve el `reloj_anterior` del turno revertido (para que quien
        mantenga el reloj virtual lo reasigne), o None si no había ningún
        turno que deshacer.
        """
        if not self._turnos:
            return None

        turno = self._turnos.pop()

        for deshacer in reversed(turno.cambios_inventario):
            deshacer()

        for salida_dict, campo, valor_anterior in reversed(turno.cambios_puertas):
            salida_dict[campo] = valor_anterior

        for evento in turno.eventos_creados:
            evento.cancelado = True
        for evento in turno.eventos_cancelados:
            evento.cancelado = False

        for sala_id, tiempo_anterior in reversed(turno.cambios_rastro):
            self._registro_rastro.marcar_visita(sala_id, tiempo_anterior)

        for actor, vida_anterior in reversed(turno.cambios_vida):
            actor.vida = vida_anterior

        inventario.quitar_primero_de_tipo(tipo_pergamino)

        return turno.reloj_anterior
