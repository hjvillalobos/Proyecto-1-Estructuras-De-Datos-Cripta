class GestorEfectos:
    """
    Aplica y agenda los efectos temporales del juego (§2.10):
    veneno, regeneración, antorcha, trampas y cierre automático de puertas.
    Los efectos viven en la misma cola de eventos del motor, por eso
    este módulo siempre trabaja sobre una instancia de Motor.
    """

    def __init__(self, motor):
        self.motor = motor
        # efectos activos por actor, para poder cancelarlos antes de que
        # expiren (ej: antídoto cancela veneno). Es bookkeeping normal de
        # aplicación, no es la cola de eventos ni una caché de catálogo.
        self.veneno_activo = {}  # {id(actor): {...}}

    # ---------- veneno (§2.10) ----------

    def aplicar_veneno(self, actor, dano_por_pulso, duracion=400, intervalo=80):
        """Daña cada `intervalo` unidades durante `duracion`, salvo que un antídoto lo cancele antes."""
        self.cancelar_veneno(actor)  # no se acumulan dos venenos

        tiempo_fin = self.motor.reloj + duracion
        evento_fin = self.motor.cola.insertar(tiempo_fin, "fin_veneno", actor)

        self.veneno_activo[id(actor)] = {
            "dano_por_pulso": dano_por_pulso,
            "intervalo": intervalo,
            "tiempo_fin": tiempo_fin,
            "evento_fin": evento_fin,
            "evento_pulso": None,
        }
        self._programar_pulso_veneno(actor)

    def _programar_pulso_veneno(self, actor):
        info = self.veneno_activo.get(id(actor))
        if info is None:
            return
        tiempo_pulso = self.motor.reloj + info["intervalo"]
        if tiempo_pulso >= info["tiempo_fin"]:
            return  # el próximo pulso caería después de que el veneno termine
        info["evento_pulso"] = self.motor.cola.insertar(tiempo_pulso, "pulso_veneno", actor)

    def ejecutar_pulso_veneno(self, actor):
        """El bucle principal llama esto al sacar un evento 'pulso_veneno'."""
        info = self.veneno_activo.get(id(actor))
        if info is None:
            return  # ya fue cancelado (ej: por antídoto)
        actor.vida = max(0, actor.vida - info["dano_por_pulso"])
        if actor.vida == 0:
            self.motor._matar(actor)
            del self.veneno_activo[id(actor)]
            return
        self._programar_pulso_veneno(actor)

    def ejecutar_fin_veneno(self, actor):
        """El bucle principal llama esto al sacar un evento 'fin_veneno'."""
        info = self.veneno_activo.get(id(actor))
        if info is not None:
            if info["evento_pulso"] is not None:
                self.motor.cola.cancelar(info["evento_pulso"])
            del self.veneno_activo[id(actor)]

    def cancelar_veneno(self, actor):
        """Usado por un antídoto (§2.7): cancela el veneno antes de que termine."""
        info = self.veneno_activo.get(id(actor))
        if info is None:
            return
        if info["evento_pulso"] is not None:
            self.motor.cola.cancelar(info["evento_pulso"])
        self.motor.cola.cancelar(info["evento_fin"])
        del self.veneno_activo[id(actor)]

    # ---------- regeneración de enemigos (§2.10) ----------

    def aplicar_regeneracion(self, enemigo, cantidad, intervalo=200):
        """Un enemigo con regeneración recupera `cantidad` cada `intervalo`, sin superar vida_max."""
        self.motor.cola.insertar(self.motor.reloj + intervalo, "pulso_regeneracion",
                                  (enemigo, cantidad, intervalo))

    def ejecutar_pulso_regeneracion(self, enemigo, cantidad, intervalo):
        if enemigo.vida <= 0:
            return  # murió, no sigue regenerando
        enemigo.vida = min(enemigo.vida_max, enemigo.vida + cantidad)
        self.aplicar_regeneracion(enemigo, cantidad, intervalo)

    # ---------- antorcha (§2.7, §2.10) ----------

    def encender_antorcha(self, antorcha_objeto, duracion):
        """Al encenderse, programa su apagado después de `duracion`."""
        self.motor.cola.insertar(self.motor.reloj + duracion, "apagar_antorcha", antorcha_objeto)

    def ejecutar_apagar_antorcha(self, antorcha_objeto):
        antorcha_objeto.encendida = False  # el objeto debe tener este campo

    # ---------- trampas (§2.10) ----------

    def activar_trampa(self, trampa, dano, rearme=300):
        """
        Se llama al entrar a una sala con trampa armada: inmediatamente
        después de completar el movimiento, antes del siguiente evento (§2.10).
        """
        if not trampa.armada:
            return  # desarmada: no pasa nada
        self.motor.jugador.vida = max(0, self.motor.jugador.vida - dano)
        if self.motor.jugador.vida == 0:
            self.motor._matar(self.motor.jugador)

        trampa.armada = False
        self.motor.cola.insertar(self.motor.reloj + rearme, "rearmar_trampa", trampa)

    def ejecutar_rearmar_trampa(self, trampa):
        trampa.armada = True

    # ---------- cierre automático de puerta ----------
    # (el AGENDAMIENTO ya está en juego.py -> Motor.abrir_puerta; acá solo
    # va la EJECUCIÓN, que dispara el bucle principal cuando llega el evento)

    def ejecutar_cierre_puerta(self, sala, direccion):
        salida = sala.salidas.get(direccion)
        if salida is not None:
            salida["cerrada"] = True