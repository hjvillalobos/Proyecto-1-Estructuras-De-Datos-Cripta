# modelo/juego.py

import random
from modelo.eventos import ColaEventos
from modelo.efectos import GestorEfectos
from modelo.tipos import Jugador, InstanciaEnemigo, ObjetoInstancia
from modelo.rastro import RegistroRastro
from modelo.historial import HistorialRetroceso


COSTOS = {
    "mover": 100, "atacar": 100, "esperar": 100, "usar_objeto": 50,
    "equipar": 50, "recoger": 25, "soltar": 25, "abrir_puerta": 50,
}


def calcular_intervalo(costo, velocidad):
    return max(1, costo * 100 // velocidad)


def calcular_dano(atacante, defensor, azar):
    return max(1, atacante.ataque + azar.randint(0, 4) - defensor.defensa)


class Motor:
    def __init__(self, jugador, salas_lista, semilla):
        self.jugador = jugador

        salas_total = 0
        for sala in salas_lista:
            if sala.id > salas_total:
                salas_total = sala.id

        self.salas = [None] * (salas_total + 1)
        for sala in salas_lista:
            self.salas[sala.id] = sala

        self.cola = ColaEventos()
        self.azar = random.Random(semilla)
        self.reloj = 0

        self.enemigos_por_sala = [[] for _ in range(salas_total + 1)]
        self.objetos_en_suelo = [[] for _ in range(salas_total + 1)]
        self.contenido_cargado = [False] * (salas_total + 1)
        self.salas_activadas = [False] * (salas_total + 1)

        self.efectos = GestorEfectos(self)
        self.registro_rastro = RegistroRastro()
        self.registro_rastro.marcar_visita(self.jugador.posicion_actual, 0)
        self.historial = HistorialRetroceso(self.registro_rastro)

        self.meta = None
        self.gestor_precarga = None
        self.acciones_jugador = 0
        self.enemigos_derrotados = 0
        self.terminado = False
        self.resultado = None
        self.sala_salida = None
        self.llave_salida = None

    # ---------- enemigos ----------

    def activar_enemigos_de_sala(self, id_sala, enemigos_de_la_sala):
        if self.salas_activadas[id_sala]:
            return
        self.salas_activadas[id_sala] = True

        enemigos_ordenados = sorted(enemigos_de_la_sala, key=lambda e: e.id_instancia)
        for enemigo in enemigos_ordenados:
            enemigo.sala_actual = id_sala
            intervalo = calcular_intervalo(COSTOS["atacar"], enemigo.velocidad)
            enemigo.tiempo_siguiente = self.reloj + intervalo
            enemigo.evento_pendiente = self.cola.insertar(enemigo.tiempo_siguiente, "turno_enemigo", enemigo)

            if self.gestor_precarga is not None:
                ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
                if "regeneracion" in ficha.atributos:
                    self.efectos.aplicar_regeneracion(enemigo, ficha.atributos["regeneracion"], 200)

    def _tiene_llave(self, llave_id):
        inventario = self.jugador.inventario
        if inventario.esta_vacio():
            return False
        anterior = None
        actual = inventario.objeto_actual()
        while actual is not anterior:
            anterior = actual
            actual = inventario.retroceder()
        while actual is not None:
            ficha = self.gestor_precarga.catalogo.obtener_fichas([actual.tipo_catalogo])[0]
            if ficha.clase == "llave" and ficha.atributos.get("abre") == llave_id:
                return True
            siguiente = inventario.avanzar()
            if siguiente is actual:
                break
            actual = siguiente
        return False

    # ---------- movimiento y puertas ----------

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
        if llave_necesaria and not self._tiene_llave(llave_necesaria):
            return False, "No tenés la llave correcta"

        self.historial.registrar_puerta(salida, "cerrada", salida.get("cerrada", False))
        salida["cerrada"] = False
        self._avanzar_actor(self.jugador, COSTOS["abrir_puerta"])

        if "cierre_automatico" in salida:
            tiempo_cierre = self.reloj + salida["cierre_automatico"]
            self.cola.insertar(tiempo_cierre, "cierre_puerta", (sala_actual, direccion))

        return True, None

    def mover(self, direccion):
        puede, error = self.puede_moverse(direccion)
        if not puede:
            return False, error

        id_destino = self.salas[self.jugador.posicion_actual].salidas[direccion]["sala"]

        if not self.contenido_cargado[id_destino]:
            sala_preparada = self.gestor_precarga.preparar_entrada(id_destino, self._ids_en_uso())
            _incorporar_sala_preparada(self, sala_preparada)

        sala_destino = self.salas[id_destino]
        self.jugador.posicion_actual = id_destino
        self._avanzar_actor(self.jugador, COSTOS["mover"])
        self.historial.registrar_rastro(id_destino, self.registro_rastro.tiempo_de(id_destino))
        self.registro_rastro.marcar_visita(id_destino, self.reloj)

        if id_destino == self.sala_salida and self._tiene_llave(self.llave_salida):
            self.terminado = True
            self.resultado = "victoria"

        self.activar_enemigos_de_sala(id_destino, self.enemigos_por_sala[id_destino])

        trampa = sala_destino.trampa
        if trampa is not None:
            self.efectos.activar_trampa(trampa)

        return True, None

    # ---------- combate ----------

    def atacar(self, atacante, defensor):
        dano = calcular_dano(atacante, defensor, self.azar)
        self.historial.registrar_vida(defensor, defensor.vida)
        defensor.vida = max(0, defensor.vida - dano)
        if defensor.vida == 0:
            self._matar(defensor)
        self._avanzar_actor(atacante, COSTOS["atacar"])
        return dano

    def _matar(self, actor):
        if actor.evento_pendiente is not None:
            self.historial.registrar_evento_cancelado(actor.evento_pendiente)
            self.cola.cancelar(actor.evento_pendiente)
            actor.evento_pendiente = None

        if actor is self.jugador:
            self.terminado = True
            self.resultado = "derrota"
        else:
            self.enemigos_derrotados += 1
            self._soltar_botin(actor)

    def _soltar_botin(self, enemigo):
        ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
        id_sala = enemigo.sala_actual
        if id_sala is None:
            return
        for indice, tipo_objeto in enumerate(ficha.atributos.get("suelta", [])):
            self.objetos_en_suelo[id_sala].append(ObjetoInstancia(
                id_instancia=f"botin-{enemigo.id_instancia}-{indice}",
                tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
            ))

    def cambiar_velocidad(self, actor, velocidad_nueva):
        evento_viejo = actor.evento_pendiente
        velocidad_anterior = actor.velocidad
        actor.velocidad = velocidad_nueva
        if evento_viejo is None:
            return
        restante = max(1, (evento_viejo.tiempo - self.reloj) * velocidad_anterior // velocidad_nueva)
        nuevo_tiempo = self.reloj + restante
        self.historial.registrar_evento_cancelado(evento_viejo)
        nuevo_evento = self.cola.reprogramar(evento_viejo, nuevo_tiempo)
        self.historial.registrar_evento_creado(nuevo_evento)
        actor.evento_pendiente = nuevo_evento

    def _avanzar_actor(self, actor, costo):
        intervalo = calcular_intervalo(costo, actor.velocidad)
        actor.tiempo_siguiente = self.reloj + intervalo
        if actor.evento_pendiente is not None:
            self.historial.registrar_evento_cancelado(actor.evento_pendiente)
            self.cola.cancelar(actor.evento_pendiente)
        tipo_evento = "turno_jugador" if actor is self.jugador else "turno_enemigo"
        actor.evento_pendiente = self.cola.insertar(actor.tiempo_siguiente, tipo_evento, actor)
        self.historial.registrar_evento_creado(actor.evento_pendiente)

    def _ejecutar_turno_enemigo(self, enemigo, decidir_accion_enemigo):
        id_sala = enemigo.sala_actual
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
            lista_origen = self.enemigos_por_sala[id_sala]
            if enemigo in lista_origen:
                lista_origen.remove(enemigo)
            self.enemigos_por_sala[nuevo_id].append(enemigo)
            enemigo.sala_actual = nuevo_id
            self._avanzar_actor(enemigo, COSTOS["mover"])
        else:
            self._avanzar_actor(enemigo, COSTOS["esperar"])

    def _buscar_enemigo_en_sala_actual(self, id_instancia):
        for enemigo in self.enemigos_por_sala[self.jugador.posicion_actual]:
            if enemigo.id_instancia == id_instancia:
                return enemigo
        return None

    def _posicionar_cursor_en(self, id_instancia):
        inventario = self.jugador.inventario
        if inventario.esta_vacio():
            return False
        anterior = None
        actual = inventario.objeto_actual()
        while actual is not anterior:
            anterior = actual
            actual = inventario.retroceder()
        while actual is not None:
            if actual.id_instancia == id_instancia:
                return True
            siguiente = inventario.avanzar()
            if siguiente is actual:
                return False
            actual = siguiente
        return False

    def _ids_en_uso(self):
        ids = []
        for lista_enemigos in self.enemigos_por_sala:
            for enemigo in lista_enemigos:
                if enemigo.vida > 0 and enemigo.tipo_catalogo not in ids:
                    ids.append(enemigo.tipo_catalogo)
        for lista_objetos in self.objetos_en_suelo:
            for objeto in lista_objetos:
                if objeto.tipo_catalogo not in ids:
                    ids.append(objeto.tipo_catalogo)

        inventario = self.jugador.inventario
        if not inventario.esta_vacio():
            anterior = None
            actual = inventario.objeto_actual()
            while actual is not anterior:
                anterior = actual
                actual = inventario.retroceder()
            while actual is not None:
                if actual.tipo_catalogo not in ids:
                    ids.append(actual.tipo_catalogo)
                siguiente = inventario.avanzar()
                if siguiente is actual:
                    break
                actual = siguiente
        return ids

    # ---------- vista / resumen ----------

    def estado_vista(self):
        from modelo.snapshots import EstadoVista, SalidaVista, EnemigoVista

        sala = self.salas[self.jugador.posicion_actual]

        salidas = [
            SalidaVista(direccion=d, destino=info["sala"],
                        cerrada=info.get("cerrada", False), llave=info.get("llave"))
            for d, info in sala.salidas.items()
        ]

        enemigos_vista = []
        for indice, enemigo in enumerate(self.enemigos_por_sala[sala.id]):
            if enemigo.vida <= 0:
                continue
            nombre_base = enemigo.tipo_catalogo
            if self.gestor_precarga is not None:
                ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
                nombre_base = ficha.nombre
            enemigos_vista.append(EnemigoVista(
                instancia=enemigo.id_instancia, nombre=f"{nombre_base} #{indice + 1}",
                vida=enemigo.vida, vida_max=enemigo.vida_max,
            ))

        efectos_activos = []
        if self.jugador.veneno is not None:
            efectos_activos.append("veneno")

        return EstadoVista(
            reloj=self.reloj, sala_id=sala.id, sala_nombre=sala.nombre,
            salidas=salidas, enemigos=enemigos_vista,
            objetos_suelo=[],
            vida=self.jugador.vida, vida_max=self.jugador.vida_max,
            ataque=self.jugador.ataque, defensa=self.jugador.defensa, velocidad=self.jugador.velocidad,
            inventario_usado=0, inventario_max=0,
            efectos=efectos_activos,
        )

    def resumen(self):
        from modelo.snapshots import ResumenPartida
        return ResumenPartida(
            terminado=self.terminado, resultado=self.resultado,
            acciones=self.acciones_jugador, derrotados=self.enemigos_derrotados,
            reloj_final=self.reloj,
        )

    # ---------- acciones del jugador ----------

    def ejecutar(self, accion, argumento=None):
        from modelo.snapshots import ResultadoAccion
        from modelo.enemigos import decidir_accion

        if accion == "retroceso":
            if self.jugador.inventario.contar("itm_pergamino_retroceso") == 0:
                return ResultadoAccion(ok=False, mensaje="No tenés pergaminos de retroceso")
            reloj_anterior = self.historial.usar_pergamino(self.jugador.inventario)
            if reloj_anterior is None:
                return ResultadoAccion(ok=False, mensaje="No hay nada que deshacer")
            self.reloj = reloj_anterior
            return ResultadoAccion(ok=True)

        self.historial.iniciar_turno(self.reloj)

        if accion == "mover":
            ok, error = self.mover(argumento)
        elif accion == "abrir":
            ok, error = self.abrir_puerta(argumento)
        elif accion == "atacar":
            enemigo = self._buscar_enemigo_en_sala_actual(argumento)
            if enemigo is None:
                return ResultadoAccion(ok=False, mensaje="Ese enemigo no está en tu sala")
            self.atacar(self.jugador, enemigo)
            ok, error = True, None
        elif accion == "esperar":
            self._avanzar_actor(self.jugador, COSTOS["esperar"])
            ok, error = True, None
        elif accion == "recoger":
            objetos_sala = self.objetos_en_suelo[self.jugador.posicion_actual]
            objeto = next((o for o in objetos_sala if o.id_instancia == argumento), None)
            if objeto is None:
                return ResultadoAccion(ok=False, mensaje="Ese objeto no está en el suelo de esta sala")
            nodo = self.jugador.inventario.recoger(objeto)
            if nodo is None:
                return ResultadoAccion(ok=False, mensaje="Inventario lleno")
            objetos_sala.remove(objeto)
            if objeto.tipo_catalogo != "itm_pergamino_retroceso":
                self.historial.registrar_inventario(lambda n=nodo: self.jugador.inventario.quitar_nodo(n))
            self._avanzar_actor(self.jugador, COSTOS["recoger"])
            ok, error = True, None
        elif accion == "soltar":
            if not self._posicionar_cursor_en(argumento):
                return ResultadoAccion(ok=False, mensaje="No tenés ese objeto en el inventario")
            inventario = self.jugador.inventario
            nodo_actual = inventario.cursor
            anterior = nodo_actual.anterior if nodo_actual.anterior is not inventario.cabeza else None
            objeto = inventario.soltar_actual()
            objeto.ubicacion = "suelo"
            objeto.sala = self.jugador.posicion_actual
            self.objetos_en_suelo[self.jugador.posicion_actual].append(objeto)
            if objeto.tipo_catalogo != "itm_pergamino_retroceso":
                self.historial.registrar_inventario(lambda a=anterior, o=objeto: inventario.insertar_despues(a, o))
            self._avanzar_actor(self.jugador, COSTOS["soltar"])
            ok, error = True, None
        elif accion == "equipar":
            if not self._posicionar_cursor_en(argumento):
                return ResultadoAccion(ok=False, mensaje="No tenés ese objeto en el inventario")
            inventario = self.jugador.inventario
            objeto = inventario.objeto_actual()
            ficha = self.gestor_precarga.catalogo.obtener_fichas([objeto.tipo_catalogo])[0]
            if ficha.clase not in ("arma", "armadura"):
                return ResultadoAccion(ok=False, mensaje="Ese objeto no se puede equipar")

            nodo_anterior = inventario.arma_equipada if ficha.clase == "arma" else inventario.armadura_equipada
            if nodo_anterior is not None:
                ficha_anterior = self.gestor_precarga.catalogo.obtener_fichas([nodo_anterior.objeto.tipo_catalogo])[0]
                if ficha.clase == "arma":
                    self.jugador.ataque -= ficha_anterior.atributos.get("ataque_bonus", 0)
                else:
                    self.jugador.defensa -= ficha_anterior.atributos.get("defensa_bonus", 0)

            inventario.equipar_actual(ficha.clase)
            if ficha.clase == "arma":
                self.jugador.ataque += ficha.atributos.get("ataque_bonus", 0)
            else:
                self.jugador.defensa += ficha.atributos.get("defensa_bonus", 0)

            self._avanzar_actor(self.jugador, COSTOS["equipar"])
            ok, error = True, None
        elif accion == "usar":
            if not self._posicionar_cursor_en(argumento):
                return ResultadoAccion(ok=False, mensaje="No tenés ese objeto en el inventario")
            inventario = self.jugador.inventario
            objeto = inventario.objeto_actual()
            ficha = self.gestor_precarga.catalogo.obtener_fichas([objeto.tipo_catalogo])[0]

            if ficha.clase == "pocion" and "cura" in ficha.atributos:
                self.jugador.vida = min(self.jugador.vida_max, self.jugador.vida + ficha.atributos["cura"])
            elif ficha.clase == "pocion" and "modificador_velocidad" in ficha.atributos:
                return ResultadoAccion(ok=False, mensaje="Poción de velocidad: pendiente")
            elif ficha.clase == "antidoto":
                self.efectos.cancelar_veneno(self.jugador)
            elif ficha.clase == "antorcha":
                self.efectos.encender_antorcha(objeto, ficha.atributos.get("duracion", 0))
            else:
                return ResultadoAccion(ok=False, mensaje="Ese objeto no se puede usar")

            inventario.quitar_nodo(inventario.cursor)
            self._avanzar_actor(self.jugador, COSTOS["usar_objeto"])
            ok, error = True, None
        else:
            return ResultadoAccion(ok=False, mensaje="Acción desconocida")

        if not ok:
            return ResultadoAccion(ok=False, mensaje=error)

        while True:
            evento = self.ejecutar_ciclo(decidir_accion)
            if evento is None or evento.tipo == "turno_jugador" or self.terminado:
                break

        self.acciones_jugador += 1
        self.historial.cerrar_turno()
        return ResultadoAccion(ok=True)

    def ejecutar_ciclo(self, decidir_accion_enemigo):
        evento = self.cola.extraer_minimo()
        if evento is None:
            return None

        self.reloj = evento.tiempo

        if evento.tipo == "turno_enemigo":
            self._ejecutar_turno_enemigo(evento.referencia, decidir_accion_enemigo)
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
            pass

        return evento


def crear_juego(gestor_precarga, cripta_id, semilla, notificar=None):
    from modelo.snapshots import MetaPartida
    from modelo.inventario import Inventario

    preparada = gestor_precarga.preparar_cripta(cripta_id)
    generales = preparada.generales

    jug = generales["jugador"]
    jugador = Jugador(
        vida=jug["vida_max"], vida_max=jug["vida_max"],
        ataque=jug["ataque"], defensa=jug["defensa"], velocidad=jug["velocidad"],
        tiempo_siguiente=0,
        inventario=Inventario(capacidad_max=generales["inventario_max"]),
        posicion_actual=generales["sala_inicial"],
        llaves_obtenidas=[],
    )

    motor = Motor(jugador=jugador, salas_lista=preparada.salas, semilla=semilla)
    motor.gestor_precarga = gestor_precarga
    motor.sala_salida = generales["sala_salida"]
    motor.llave_salida = generales["llave_salida"]
    motor.meta = MetaPartida(
        cripta_id=cripta_id,
        cripta_version=generales.get("version", "desconocida"),
        catalogo_version=preparada.version_catalogo,
        semilla=semilla,
    )

    _incorporar_sala_preparada(motor, preparada.inicial)
    id_inicial = preparada.inicial.sala.id
    motor.activar_enemigos_de_sala(id_inicial, motor.enemigos_por_sala[id_inicial])

    if notificar:
        notificar(f"Cripta '{cripta_id}' cargada: {len(preparada.salas)} salas.")

    return motor


def _incorporar_sala_preparada(motor, sala_preparada):
    from modelo.tipos import InstanciaEnemigo, ObjetoInstancia, Trampa

    id_sala = sala_preparada.sala.id
    contenido = sala_preparada.contenido

    def ficha_de(id_tipo):
        for ficha in sala_preparada.fichas:
            if ficha.id == id_tipo:
                return ficha
        return None

    enemigos_de_la_sala = []
    for enemigo_json in contenido.get("enemigos", []):
        ficha = ficha_de(enemigo_json["tipo"])
        enemigos_de_la_sala.append(InstanciaEnemigo(
            vida=enemigo_json.get("vida", ficha.atributos["vida_max"]),
            vida_max=ficha.atributos["vida_max"],
            ataque=ficha.atributos["ataque"],
            defensa=ficha.atributos["defensa"],
            velocidad=ficha.atributos["velocidad"],
            tiempo_siguiente=0,
            id_instancia=enemigo_json["instancia"],
            tipo_catalogo=enemigo_json["tipo"],
            comportamiento=ficha.atributos["comportamiento"],
        ))
    motor.enemigos_por_sala[id_sala] = enemigos_de_la_sala

    objetos_de_la_sala = []
    for indice, tipo_objeto in enumerate(contenido.get("objetos", [])):
        objetos_de_la_sala.append(ObjetoInstancia(
            id_instancia=f"obj-{id_sala}-{indice}",
            tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
        ))
    motor.objetos_en_suelo[id_sala] = objetos_de_la_sala

    trampas_json = contenido.get("trampas", [])
    if trampas_json:
        trampa_json = trampas_json[0]
        motor.salas[id_sala].trampa = Trampa(
            id_instancia=trampa_json["instancia"],
            tipo_catalogo=trampa_json["tipo"],
        )

    motor.contenido_cargado[id_sala] = True