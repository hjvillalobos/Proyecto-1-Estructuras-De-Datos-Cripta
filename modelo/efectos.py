class InfoVeneno:
    def __init__(self, dano_por_pulso, intervalo, tiempo_fin):
        self.dano_por_pulso = dano_por_pulso
        self.intervalo = intervalo
        self.tiempo_fin = tiempo_fin
        self.evento_fin = None
        self.evento_pulso = None


class GestorEfectos:
    def __init__(self, motor):
        self.motor = motor

    # ---------- veneno (§2.10) ----------

    def aplicar_veneno(self, actor, dano_por_pulso, duracion=400, intervalo=80):
        self.cancelar_veneno(actor)
        info = InfoVeneno(dano_por_pulso, intervalo, self.motor.reloj + duracion)
        info.evento_fin = self.motor.cola.insertar(info.tiempo_fin, "fin_veneno", actor)
        actor.veneno = info
        self._programar_pulso_veneno(actor)

    def _programar_pulso_veneno(self, actor):
        info = actor.veneno
        if info is None:
            return
        tiempo_pulso = self.motor.reloj + info.intervalo
        if tiempo_pulso >= info.tiempo_fin:
            return
        info.evento_pulso = self.motor.cola.insertar(tiempo_pulso, "pulso_veneno", actor)

    def ejecutar_pulso_veneno(self, actor):
        info = actor.veneno
        if info is None:
            return
        actor.vida = max(0, actor.vida - info.dano_por_pulso)
        if actor.vida == 0:
            self.motor._matar(actor)
            actor.veneno = None
            return
        self._programar_pulso_veneno(actor)

    def ejecutar_fin_veneno(self, actor):
        info = actor.veneno
        if info is not None:
            if info.evento_pulso is not None:
                self.motor.cola.cancelar(info.evento_pulso)
            actor.veneno = None

    def cancelar_veneno(self, actor):
        info = actor.veneno
        if info is None:
            return
        if info.evento_pulso is not None:
            self.motor.cola.cancelar(info.evento_pulso)
        self.motor.cola.cancelar(info.evento_fin)
        actor.veneno = None

    # ---------- regeneración de enemigos (§2.10) ----------

    def aplicar_regeneracion(self, enemigo, cantidad, intervalo=200):
        self.motor.cola.insertar(self.motor.reloj + intervalo, "pulso_regeneracion",
                                  (enemigo, cantidad, intervalo))

    def ejecutar_pulso_regeneracion(self, enemigo, cantidad, intervalo):
        if enemigo.vida <= 0:
            return
        enemigo.vida = min(enemigo.vida_max, enemigo.vida + cantidad)
        self.aplicar_regeneracion(enemigo, cantidad, intervalo)

    # ---------- antorcha ----------

    def encender_antorcha(self, antorcha_objeto, duracion):
        self.motor.cola.insertar(self.motor.reloj + duracion, "apagar_antorcha", antorcha_objeto)

    def ejecutar_apagar_antorcha(self, antorcha_objeto):
        antorcha_objeto.encendida = False

    # ---------- trampas ----------

    def activar_trampa(self, trampa):
        if not trampa.armada:
            return
        ficha = self.motor.gestor_precarga.catalogo.obtener_fichas([trampa.tipo_catalogo])[0]
        dano = ficha.atributos.get("daño", 0)
        rearme = ficha.atributos.get("rearme", 300)

        self.motor.jugador.vida = max(0, self.motor.jugador.vida - dano)
        if self.motor.jugador.vida == 0:
            self.motor._matar(self.motor.jugador)

        if "veneno" in ficha.atributos:
            info_veneno = ficha.atributos["veneno"]
            self.aplicar_veneno(self.motor.jugador, info_veneno.get("dano_por_pulso", 1))

        trampa.armada = False
        self.motor.cola.insertar(self.motor.reloj + rearme, "rearmar_trampa", trampa)

    def ejecutar_rearmar_trampa(self, trampa):
        trampa.armada = True

    # ---------- puertas ----------

    def ejecutar_cierre_puerta(self, sala, direccion):
        salida = sala.salidas.get(direccion)
        if salida is not None:
            self.motor.historial.registrar_puerta(salida, "cerrada", salida.get("cerrada", False))
            salida["cerrada"] = True