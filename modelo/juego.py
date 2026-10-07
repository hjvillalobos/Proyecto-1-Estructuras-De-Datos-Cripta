# modelo/juego.py

import random
from modelo.eventos import ColaEventos
from modelo.efectos import GestorEfectos
from modelo.tipos import Jugador, InstanciaEnemigo, ObjetoInstancia
from modelo.rastro import RegistroRastro
from modelo.historial import HistorialRetroceso


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
        self.historial = HistorialRetroceso(self.registro_rastro)
        self.objetos_en_suelo = {}
        self.acciones_jugador = 0
        self.enemigos_derrotados = 0
        self.terminado = False
        self.resultado = None       # "victoria" | "derrota" | None
        self.sala_salida = None     # lo llena crear_juego()
        self.llave_salida = None    # lo llena crear_juego()
        self.meta = None

    def estado_vista(self):
        from modelo.snapshots import EstadoVista, SalidaVista, EnemigoVista

        sala = self.salas[self.jugador.posicion_actual]

        salidas = [
            SalidaVista(
                direccion=direccion,
                destino=info["sala"],
                cerrada=info.get("cerrada", False),
                llave=info.get("llave"),
            )
            for direccion, info in sala.salidas.items()
        ]

        enemigos_vista = [
            EnemigoVista(
                instancia=enemigo.id_instancia,
                nombre=f"{enemigo.tipo_catalogo} #{indice + 1}",
                vida=enemigo.vida,
                vida_max=enemigo.vida_max,
            )
            for indice, enemigo in enumerate(self.enemigos_por_sala.get(sala.id, []))
            if enemigo.vida > 0
        ]

        return EstadoVista(
            reloj=self.reloj,
            sala_id=sala.id,
            sala_nombre=sala.nombre,
            salidas=salidas,
            enemigos=enemigos_vista,
            objetos_suelo=[],  # pendiente: depende de ObjetoInstancia (C/B)
            vida=self.jugador.vida,
            vida_max=self.jugador.vida_max,
            ataque=self.jugador.ataque,
            defensa=self.jugador.defensa,
            velocidad=self.jugador.velocidad,
            inventario_usado=0,  # pendiente: D lo llena con su inventario real
            inventario_max=0,  # pendiente: viene de los datos generales de la cripta (B)
            efectos=[],  # opcional, para más adelante
        )

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
            objetos_sala = self.objetos_en_suelo.get(self.jugador.posicion_actual, [])
            objeto = next((o for o in objetos_sala if o.id_instancia == argumento), None)
            if objeto is None:
                return ResultadoAccion(ok=False, mensaje="Ese objeto no está en el suelo de esta sala")
            nodo = self.jugador.inventario.recoger(objeto)
            if nodo is None:
                return ResultadoAccion(ok=False, mensaje="Inventario lleno")
            objetos_sala.remove(objeto)
            if objeto.tipo_catalogo != "itm_pergamino_retroceso":  # excepción §2.11
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
            self.objetos_en_suelo.setdefault(self.jugador.posicion_actual, []).append(objeto)
            if objeto.tipo_catalogo != "itm_pergamino_retroceso":  # excepción §2.11
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


    def _buscar_enemigo_en_sala_actual(self, id_instancia):
        for enemigo in self.enemigos_por_sala.get(self.jugador.posicion_actual, []):
            if enemigo.id_instancia == id_instancia:
                return enemigo
        return None
    def _ids_en_uso(self):
        ids = set()
        for enemigos in self.enemigos_por_sala.values():
            for enemigo in enemigos:
                if enemigo.vida > 0:
                    ids.add(enemigo.tipo_catalogo)
        for objetos in self.objetos_en_suelo.values():
            for objeto in objetos:
                ids.add(objeto.tipo_catalogo)

        inventario = self.jugador.inventario
        if inventario is not None and not inventario.esta_vacio():
            anterior = None
            actual = inventario.objeto_actual()
            while actual is not anterior:
                anterior = actual
                actual = inventario.retroceder()
            while actual is not None:
                ids.add(actual.tipo_catalogo)
                siguiente = inventario.avanzar()
                if siguiente is actual:
                    break
                actual = siguiente
        return list(ids)

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

        if id_destino not in self.enemigos_por_sala:
            # contenido de la sala destino aún no existe en memoria: lo pedimos
            # ahora mismo, bloqueando la confirmación del movimiento (§4.2)
            sala_preparada = self.gestor_precarga.preparar_entrada(id_destino, self._ids_en_uso())
            _incorporar_sala_preparada(self, sala_preparada)

        sala_destino = self.salas[id_destino]
        self.jugador.posicion_actual = id_destino
        if id_destino == self.sala_salida and self.llave_salida in self.jugador.llaves_obtenidas:
            self.terminado = True
            self.resultado = "victoria"
        self._avanzar_actor(self.jugador, COSTOS["mover"])
        self.registro_rastro.marcar_visita(id_destino, self.reloj)
        self.historial.registrar_rastro(id_destino, self.registro_rastro.tiempo_de(id_destino))

        enemigos = self.enemigos_por_sala.get(id_destino, [])
        self.activar_enemigos_de_sala(id_destino, enemigos)

        trampa = getattr(sala_destino, "trampa", None)
        if trampa is not None:
            self.efectos.activar_trampa(trampa, trampa.dano, trampa.rearme)

        return True, None

    def atacar(self, atacante, defensor):
        dano = calcular_dano(atacante, defensor, self.azar)
        self.historial.registrar_vida(defensor, defensor.vida)
        defensor.vida = max(0, defensor.vida - dano)
        if defensor.vida == 0:
            self._matar(defensor)
        self._avanzar_actor(atacante, COSTOS["atacar"])
        return dano

    def _matar(self, actor):
        evento = self.evento_pendiente.get(id(actor))
        if evento is not None:
            self.historial.registrar_evento_cancelado(evento)
            self.cola.cancelar(evento)
            del self.evento_pendiente[id(actor)]

        if actor is self.jugador:
            self.terminado = True
            self.resultado = "derrota"
        else:
            self.enemigos_derrotados += 1
            self._soltar_botin(actor)

    def _soltar_botin(self, enemigo):
        ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
        id_sala = self.sala_de_enemigo.get(id(enemigo))
        if id_sala is None:
            return
        objetos_sala = self.objetos_en_suelo.setdefault(id_sala, [])
        for indice, tipo_objeto in enumerate(ficha.atributos.get("suelta", [])):
            objetos_sala.append(ObjetoInstancia(
                id_instancia=f"botin-{enemigo.id_instancia}-{indice}",
                tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
            ))

    def resumen(self):
        from modelo.snapshots import ResumenPartida
        return ResumenPartida(
            terminado=self.terminado,
            resultado=self.resultado,
            acciones=self.acciones_jugador,
            derrotados=self.enemigos_derrotados,
            reloj_final=self.reloj,
        )

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
            self.historial.registrar_evento_cancelado(evento_viejo)
            self.cola.cancelar(evento_viejo)
        tipo_evento = "turno_jugador" if actor is self.jugador else "turno_enemigo"
        nuevo = self.cola.insertar(actor.tiempo_siguiente, tipo_evento, actor)
        self.historial.registrar_evento_creado(nuevo)
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
            pass  # el jugador decide su acción vía la vista/controlador, no acá

        return evento

def crear_juego(gestor_precarga, cripta_id, semilla, notificar=None):
    from modelo.tipos import Jugador
    from modelo.snapshots import MetaPartida
    from modelo.inventario import Inventario

    preparada = gestor_precarga.preparar_cripta(cripta_id)
    generales = preparada.generales
    salas = {sala.id: sala for sala in preparada.salas}

    jug = generales["jugador"]
    jugador = Jugador(
        vida=jug["vida_max"], vida_max=jug["vida_max"],
        ataque=jug["ataque"], defensa=jug["defensa"], velocidad=jug["velocidad"],
        tiempo_siguiente=0,
        inventario=Inventario(capacidad_max=generales["inventario_max"]),
        posicion_actual=generales["sala_inicial"],
        llaves_obtenidas=[],
    )

    motor = Motor(jugador=jugador, salas=salas, semilla=semilla)
    motor.gestor_precarga = gestor_precarga   # lo necesita mover() para cargar salas nuevas (§4.2)
    motor.meta = MetaPartida(
        cripta_id=cripta_id,
        cripta_version=generales.get("version", "desconocida"),
        catalogo_version=preparada.version_catalogo,
        semilla=semilla,
    )
    motor.sala_salida = generales["sala_salida"]
    motor.llave_salida = generales["llave_salida"]

    _incorporar_sala_preparada(motor, preparada.inicial)

    if notificar:
        notificar(f"Cripta '{cripta_id}' cargada: {len(salas)} salas.")

    return motor


def _incorporar_sala_preparada(motor, sala_preparada):
    """Convierte el contenido crudo + fichas de UNA sala en InstanciaEnemigo /
    ObjetoInstancia reales, y los registra en el motor."""
    from modelo.tipos import InstanciaEnemigo, ObjetoInstancia

    id_sala = sala_preparada.sala.id
    fichas_por_id = {f.id: f for f in sala_preparada.fichas}
    contenido = sala_preparada.contenido

    enemigos_de_la_sala = []
    for enemigo_json in contenido.get("enemigos", []):
        ficha = fichas_por_id[enemigo_json["tipo"]]
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