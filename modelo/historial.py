# modelo/historial.py

HISTORIAL_MAX = 5  # acciones del jugador hacia atrás, como máximo (§2.11, §4.6)


class RegistroTurno:
    """
    Guarda únicamente los deltas necesarios para deshacer todo lo ocurrido
    entre una acción del jugador y la siguiente (§2.11) — nunca una copia
    completa del estado del juego.
    """

    def __init__(self, reloj_anterior: int, registro_rastro, cola=None, referencias=()):
        self.reloj_anterior = reloj_anterior
        self._registro_rastro = registro_rastro
        self._cola = cola
        self.cambios = []
        self.cambios_fallo = []
        self.referencias = list(referencias)

    def registrar_cambio(self, deshacer):
        self.cambios.append(deshacer)
        self.cambios_fallo.append(deshacer)

    def registrar_fallo(self, deshacer):
        self.cambios_fallo.append(deshacer)

    def registrar_atributo(self, objeto, atributo):
        anterior = getattr(objeto, atributo)
        self.registrar_cambio(lambda: setattr(objeto, atributo, anterior))

    def registrar_vida(self, actor, vida_anterior: int):
        self.registrar_cambio(lambda: setattr(actor, "vida", vida_anterior))

    def registrar_rastro(self, sala_id: int, tiempo_anterior):
        rastro = self._registro_rastro
        self.registrar_cambio(
            lambda: rastro.marcar_visita(sala_id, tiempo_anterior))

    def registrar_evento_creado(self, evento):
        self.registrar_cambio(lambda: setattr(evento, "cancelado", True))

    def registrar_evento_cancelado(self, evento):
        cola = self._cola
        def reactivar():
            evento.cancelado = False
            if cola is not None:
                cola.reinsertar(evento)
        self.registrar_cambio(reactivar)

    def registrar_evento_extraido(self, evento):
        cola = self._cola
        if cola is not None:
            self.registrar_cambio(lambda: cola.reinsertar(evento))

    def registrar_inventario(self, deshacer):
        """`deshacer` es una función sin argumentos que revierte
        exactamente una operación de inventario, construida con las
        primitivas de Inventario (insertar_despues/quitar_nodo/
        mover_despues) por quien haga la operación original.

        IMPORTANTE (§2.11): si la operación afecta a un pergamino de
        retroceso (recogerlo o soltarlo), quien llama NO debe registrar un
        `deshacer` para ese cambio puntual — la cantidad de pergaminos
        queda excluida del alcance de la reversión."""
        self.registrar_cambio(deshacer)

    def registrar_puerta(self, salida_dict, campo: str, valor_anterior):
        self.registrar_cambio(lambda: salida_dict.__setitem__(campo, valor_anterior))


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

    def __init__(self, registro_rastro, cola=None):
        self._registro_rastro = registro_rastro
        self._cola = cola
        self._turnos = []           # pila manual, tope HISTORIAL_MAX
        self._turno_actual = None   # RegistroTurno en construcción

    # --- ciclo de vida de un turno ---

    def iniciar_turno(self, reloj_actual: int, referencias=()):
        """Se llama justo antes de ejecutar una acción del jugador."""
        self._turno_actual = RegistroTurno(reloj_actual, self._registro_rastro, self._cola, referencias)

    def descartar_turno(self):
        """Una accion rechazada no deja cambios ni ocupa historial."""
        if self._turno_actual is not None:
            for deshacer in reversed(self._turno_actual.cambios_fallo):
                deshacer()
            self._turno_actual = None

    def registrar_fallo(self, deshacer):
        if self._turno_actual is not None:
            self._turno_actual.registrar_fallo(deshacer)

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

    def registrar_cambio(self, deshacer):
        if self._turno_actual is not None:
            self._turno_actual.registrar_cambio(deshacer)

    def registrar_atributo(self, objeto, atributo):
        if self._turno_actual is not None:
            self._turno_actual.registrar_atributo(objeto, atributo)

    def registrar_evento_extraido(self, evento):
        if self._turno_actual is not None:
            self._turno_actual.registrar_evento_extraido(evento)

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

    def referencias_retroceso(self):
        return list(self._turnos[-1].referencias) if self._turnos else []

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

        # El orden global importa: un evento puede crearse y ejecutarse
        # dentro del mismo intervalo, y un nodo puede cambiar varias veces.
        for deshacer in reversed(turno.cambios):
            deshacer()

        inventario.quitar_primero_de_tipo(tipo_pergamino)
        inventario.normalizar_cursor()

        return turno.reloj_anterior
