# modelo/juego.py

import random
from modelo.eventos import ColaEventos
from modelo.efectos import GestorEfectos
from modelo.tipos import Jugador, InstanciaEnemigo, ObjetoInstancia
from modelo.rastro import RegistroRastro
from modelo.historial import HistorialRetroceso


_COSTO_MOVER = 100
_COSTO_ATACAR = 100
_COSTO_ESPERAR = 100
_COSTO_USAR_OBJETO = 50
_COSTO_EQUIPAR = 50
_COSTO_RECOGER = 25
_COSTO_SOLTAR = 25
_COSTO_ABRIR_PUERTA = 50


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
        dormidos = [e for e in enemigos_de_la_sala if e.sala_actual is None]
        for enemigo in sorted(dormidos, key=lambda e: e.id_instancia):
            enemigo.sala_actual = id_sala
            intervalo = calcular_intervalo(_COSTO_ATACAR, enemigo.velocidad)
            enemigo.tiempo_siguiente = self.reloj + intervalo
            enemigo.evento_pendiente = self.cola.insertar(enemigo.tiempo_siguiente, "turno_enemigo", enemigo)

            if self.gestor_precarga is not None:
                ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
                if "regeneracion" in ficha.atributos:
                    self.efectos.aplicar_regeneracion(enemigo, ficha.atributos["regeneracion"], 200)

    # ---------- inventario (vistas y fichas) ----------

    def inventario_cursor(self, movimiento):
        return self.jugador.inventario.cursor_vista(
            movimiento,
            self._resolver_ficha,
        )

    def inventario_vista(self, orden=None, descendente=False):
        if orden not in (None, "nombre", "peso", "valor"):
            raise ValueError(f"Orden inválido: {orden}")
        return self.jugador.inventario.vista(
            self._resolver_ficha,
            orden,
            descendente,
        )

    def _equipar_objeto(self, id_instancia):
        inventario = self.jugador.inventario
        if not self._posicionar_cursor_en(id_instancia):
            return False, "No tienes ese objeto."
        objeto = inventario.objeto_actual()
        ficha = self._resolver_ficha(objeto.tipo_catalogo)
        if ficha.clase not in ("arma", "armadura"):
            return False, "Ese objeto no se puede equipar."
        inventario.equipar_actual(ficha.clase)
        return True, None

    def _resolver_ficha(self, tipo_catalogo):
        fichas = self.gestor_precarga.catalogo.obtener_fichas([tipo_catalogo])
        if not fichas:
            raise ValueError(f"No existe la ficha {tipo_catalogo}")
        return fichas[0]

    def _resolver_clase(self, tipo_catalogo):
        return self._resolver_ficha(tipo_catalogo).clase

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
        self._avanzar_actor(self.jugador, _COSTO_ABRIR_PUERTA)

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
        pos_anterior = self.jugador.posicion_actual
        self.historial.registrar_inventario(lambda p=pos_anterior: setattr(self.jugador, "posicion_actual", p))
        self.jugador.posicion_actual = id_destino
        self._avanzar_actor(self.jugador, _COSTO_MOVER)
        self.historial.registrar_rastro(id_destino, self.registro_rastro.tiempo_de(id_destino))
        self.registro_rastro.marcar_visita(id_destino, self.reloj)

        if id_destino == self.sala_salida and self._tiene_llave(self.llave_salida):
            self.terminado = True
            self.resultado = "victoria"

        self.activar_enemigos_de_sala(id_destino, self.enemigos_por_sala[id_destino])
        self.gestor_precarga.anticipar(id_destino)

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
        self._avanzar_actor(atacante, _COSTO_ATACAR)
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
            self.historial.registrar_inventario(
                lambda v=self.enemigos_derrotados: setattr(self, "enemigos_derrotados", v - 1)
            )
            self._soltar_botin(actor)

    def _soltar_botin(self, enemigo):
        ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
        id_sala = enemigo.sala_actual
        if id_sala is None:
            return
        for indice, tipo_objeto in enumerate(ficha.atributos.get("suelta", [])):
            obj = ObjetoInstancia(
                id_instancia=f"botin-{enemigo.id_instancia}-{indice}",
                tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
            )
            self.objetos_en_suelo[id_sala].append(obj)
            self.historial.registrar_inventario(
                lambda lista=self.objetos_en_suelo[id_sala], o=obj: lista.remove(o)
            )

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
            lista_destino = self.enemigos_por_sala[nuevo_id]
            if enemigo in lista_origen:
                lista_origen.remove(enemigo)
            lista_destino.append(enemigo)
            enemigo.sala_actual = nuevo_id
            self.historial.registrar_inventario(
                lambda e=enemigo, lo=lista_origen, ld=lista_destino, s=id_sala: (
                    ld.remove(e), lo.append(e), setattr(e, "sala_actual", s)
                )
            )
            self._avanzar_actor(enemigo, _COSTO_MOVER)
        else:
            self._avanzar_actor(enemigo, _COSTO_ESPERAR)

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
        from modelo.snapshots import EstadoVista, SalidaVista, EnemigoVista, ItemVista

        sala = self.salas[self.jugador.posicion_actual]

        salidas = [
            SalidaVista(direccion=d, destino=info["sala"],
                        cerrada=info.get("cerrada", False), llave=info.get("llave"))
            for d, info in sala.salidas.items()
        ]

        enemigos_vista = []
        for indice, enemigo in enumerate(self.enemigos_por_sala[sala.id]):
            if enemigo.vida <= 0 or enemigo.sala_actual is None:
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

        jug = self.jugador
        ficha_velocidad = None
        inventario = jug.inventario
        if not inventario.esta_vacio():
            anterior = None
            actual = inventario.objeto_actual()
            while actual is not anterior:
                anterior = actual
                actual = inventario.retroceder()
            while actual is not None:
                if actual.tipo_catalogo == "itm_antorcha" and getattr(actual, "encendida", False):
                    efectos_activos.append("antorcha")
                if self.gestor_precarga is not None:
                    ficha = self.gestor_precarga.catalogo.obtener_fichas([actual.tipo_catalogo])[0]
                    if ficha.clase == "pocion" and "modificador_velocidad" in ficha.atributos:
                        ficha_velocidad = ficha
                siguiente = inventario.avanzar()
                if siguiente is actual:
                    break
                actual = siguiente
        velocidad_base = jug.velocidad
        if self.gestor_precarga and self.gestor_precarga.generales:
            jugador_gen = self.gestor_precarga.generales.get("jugador")
            if jugador_gen is not None:
                velocidad_base = jugador_gen.get("velocidad", jug.velocidad)
        if jug.velocidad != velocidad_base:
            efectos_activos.append("velocidad")

        # Objetos presentes en el suelo de la sala actual
        objetos_vista = []
        for objeto in self.objetos_en_suelo[sala.id]:
            ficha = self._resolver_ficha(objeto.tipo_catalogo)
            objetos_vista.append(
                ItemVista(
                    instancia=objeto.id_instancia,
                    nombre=ficha.nombre,
                    clase=ficha.clase,
                    peso=ficha.atributos.get("peso", 0),
                    valor=ficha.atributos.get("valor", 0),
                    equipado=False,
                )
            )

        # Capacidad y cantidad real del inventario
        inventario_usado = len(jug.inventario.a_lista_guardado())
        inventario_max = jug.inventario.capacidad_max

        return EstadoVista(
            reloj=self.reloj, sala_id=sala.id, sala_nombre=sala.nombre,
            salidas=salidas, enemigos=enemigos_vista,
            objetos_suelo=objetos_vista,
            vida=self.jugador.vida, vida_max=self.jugador.vida_max,
            ataque=self.jugador.ataque, defensa=self.jugador.defensa, velocidad=self.jugador.velocidad,
            inventario_usado=inventario_usado,
            inventario_max=inventario_max,
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
    # ---------- guardado: exportar / restaurar (§4.10) ----------
    # JugadorGuardado.extras = [terminado(0/1), resultado(0=nada,1=victoria,2=derrota), *ids de salas con contenido cargado]

    def _id_actor(self, actor):
        return "jugador" if actor is self.jugador else actor.id_instancia

    def _evento_a_guardado(self, e):
        from modelo.snapshots import EventoGuardado
        t = e.tipo
        if t in ("turno_jugador", "turno_enemigo"):
            return EventoGuardado(e.tiempo, e.secuencia, t, self._id_actor(e.referencia), [])
        if t == "pulso_veneno" and e.referencia.veneno is not None:
            return EventoGuardado(e.tiempo, e.secuencia, t, self._id_actor(e.referencia), [])
        if t == "fin_veneno" and e.referencia.veneno is not None:
            v = e.referencia.veneno
            return EventoGuardado(e.tiempo, e.secuencia, t, self._id_actor(e.referencia),
                                  [v.dano_por_pulso, v.intervalo])
        if t == "pulso_regeneracion":
            enemigo, cantidad, intervalo = e.referencia
            return EventoGuardado(e.tiempo, e.secuencia, t, enemigo.id_instancia, [cantidad, intervalo])
        if t == "apagar_antorcha":
            return EventoGuardado(e.tiempo, e.secuencia, t, e.referencia.id_instancia, [])
        if t == "rearmar_trampa":
            return EventoGuardado(e.tiempo, e.secuencia, t, e.referencia.id_instancia, [])
        if t == "cierre_puerta":
            sala, direccion = e.referencia
            return EventoGuardado(e.tiempo, e.secuencia, t, f"{sala.id}:{direccion}", [])
        return None

    def exportar_estado(self):
        from modelo.snapshots import (EstadoGuardado, JugadorGuardado, SalaGuardada, PuertaGuardada,
                                      EnemigoGuardado, ObjetoGuardado, TrampaGuardada)
        j = self.jugador
        codigo = 1 if self.resultado == "victoria" else (2 if self.resultado == "derrota" else 0)
        extras = [1 if self.terminado else 0, codigo]
        for id_sala in range(len(self.salas)):
            if self.contenido_cargado[id_sala]:
                extras.append(id_sala)

        jugador = JugadorGuardado(
            sala_id=j.posicion_actual, vida=j.vida, vida_max=j.vida_max, ataque=j.ataque,
            defensa=j.defensa, velocidad=j.velocidad, tiempo_siguiente=j.tiempo_siguiente,
            inventario=j.inventario.a_lista_guardado(), extras=extras,
        )

        eventos = []
        for e in self.cola.pendientes():
            guardado = self._evento_a_guardado(e)
            if guardado is not None:
                eventos.append(guardado)

        salas = []
        for id_sala in range(len(self.salas)):
            sala = self.salas[id_sala]
            if sala is None:
                continue
            rastro = self.registro_rastro.exportar(id_sala)
            if not (self.contenido_cargado[id_sala] or self.enemigos_por_sala[id_sala]
                    or self.objetos_en_suelo[id_sala] or rastro != -1):
                continue
            salas.append(SalaGuardada(
                sala_id=id_sala, rastro=rastro,
                puertas=[PuertaGuardada(direccion=d, cerrada=bool(info.get("cerrada", False)))
                         for d, info in sala.salidas.items() if "cerrada" in info],
                enemigos=[EnemigoGuardado(instancia=en.id_instancia, tipo=en.tipo_catalogo, vida=en.vida,
                                          activo=en.sala_actual is not None,
                                          tiempo_siguiente=en.tiempo_siguiente)
                          for en in self.enemigos_por_sala[id_sala]],
                objetos_suelo=[ObjetoGuardado(instancia=o.id_instancia, tipo=o.tipo_catalogo)
                               for o in self.objetos_en_suelo[id_sala]],
                trampas=([TrampaGuardada(instancia=sala.trampa.id_instancia,
                                         tipo=sala.trampa.tipo_catalogo, armada=sala.trampa.armada)]
                         if sala.trampa is not None else []),
            ))

        return EstadoGuardado(
            meta=self.meta, reloj=self.reloj, siguiente_secuencia=self.cola.proxima_secuencia(),
            acciones_jugador=self.acciones_jugador, enemigos_derrotados=self.enemigos_derrotados,
            rng_estado=self.azar.getstate(), jugador=jugador, eventos=eventos, salas=salas,
        )

    def _actor_por_id(self, id_actor):
        if id_actor == "jugador":
            return self.jugador
        for lista in self.enemigos_por_sala:
            for enemigo in lista:
                if enemigo.id_instancia == id_actor:
                    return enemigo
        return None

    def _trampa_por_id(self, id_instancia):
        for sala in self.salas:
            if sala is not None and sala.trampa is not None and sala.trampa.id_instancia == id_instancia:
                return sala.trampa
        return None

    def _restaurar_evento(self, eg):
        from modelo.efectos import InfoVeneno
        t = eg.tipo
        ins = self.cola.insertar_con_secuencia
        if t in ("turno_jugador", "turno_enemigo"):
            actor = self._actor_por_id(eg.objetivo)
            if actor is not None:
                actor.evento_pendiente = ins(eg.tiempo, eg.secuencia, t, actor)
        elif t == "fin_veneno":
            actor = self._actor_por_id(eg.objetivo)
            if actor is not None:
                info = InfoVeneno(eg.parametros[0], eg.parametros[1], eg.tiempo)
                info.evento_fin = ins(eg.tiempo, eg.secuencia, t, actor)
                actor.veneno = info
        elif t == "pulso_veneno":
            actor = self._actor_por_id(eg.objetivo)
            if actor is not None and actor.veneno is not None:
                actor.veneno.evento_pulso = ins(eg.tiempo, eg.secuencia, t, actor)
        elif t == "pulso_regeneracion":
            enemigo = self._actor_por_id(eg.objetivo)
            if enemigo is not None:
                ins(eg.tiempo, eg.secuencia, t, (enemigo, eg.parametros[0], eg.parametros[1]))
        elif t == "apagar_antorcha":
            from modelo.tipos import ObjetoInstancia
            ins(eg.tiempo, eg.secuencia, t,
                ObjetoInstancia(id_instancia=eg.objetivo, tipo_catalogo="itm_antorcha", ubicacion="ninguna"))
        elif t == "rearmar_trampa":
            trampa = self._trampa_por_id(eg.objetivo)
            if trampa is not None:
                ins(eg.tiempo, eg.secuencia, t, trampa)
        elif t == "cierre_puerta":
            id_sala, direccion = eg.objetivo.split(":")
            ins(eg.tiempo, eg.secuencia, t, (self.salas[int(id_sala)], direccion))

    def restaurar_estado(self, estado):
        from modelo.tipos import InstanciaEnemigo, ObjetoInstancia, Trampa
        from modelo.inventario import Inventario

        n = len(self.salas)
        self.cola = ColaEventos()
        self.reloj = estado.reloj
        self.meta = estado.meta
        self.azar.setstate(estado.rng_estado)
        self.acciones_jugador = estado.acciones_jugador
        self.enemigos_derrotados = estado.enemigos_derrotados
        self.enemigos_por_sala = [[] for _ in range(n)]
        self.objetos_en_suelo = [[] for _ in range(n)]
        self.contenido_cargado = [False] * n
        for sala in self.salas:
            if sala is not None:
                sala.trampa = None
        for id_sala in range(n):
            self.registro_rastro.importar(id_sala, -1)

        # jugador (se modifica el mismo objeto, otros módulos pueden tener referencia)
        jg = estado.jugador
        j = self.jugador
        j.posicion_actual = jg.sala_id
        j.vida, j.vida_max, j.ataque, j.defensa = jg.vida, jg.vida_max, jg.ataque, jg.defensa
        j.velocidad, j.tiempo_siguiente = jg.velocidad, jg.tiempo_siguiente
        j.veneno = None
        j.evento_pendiente = None
        inventario = Inventario(capacidad_max=j.inventario.capacidad_max)
        inventario.restaurar_desde_guardado(
            jg.inventario,
            lambda tipo: self.gestor_precarga.catalogo.obtener_fichas([tipo])[0].clase)
        j.inventario = inventario

        self.terminado = jg.extras[0] == 1
        codigo = jg.extras[1]
        self.resultado = None if codigo == 0 else ("victoria" if codigo == 1 else "derrota")
        for id_sala in jg.extras[2:]:
            self.contenido_cargado[id_sala] = True

        # salas: rastro, puertas, enemigos, objetos, trampas
        for sg in estado.salas:
            sala = self.salas[sg.sala_id]
            self.registro_rastro.importar(sg.sala_id, sg.rastro)
            for p in sg.puertas:
                if p.direccion in sala.salidas:
                    sala.salidas[p.direccion]["cerrada"] = p.cerrada
            for eg in sg.enemigos:
                ficha = self.gestor_precarga.catalogo.obtener_fichas([eg.tipo])[0]
                a = ficha.atributos
                self.enemigos_por_sala[sg.sala_id].append(InstanciaEnemigo(
                    vida=eg.vida, vida_max=a["vida_max"], ataque=a["ataque"], defensa=a["defensa"],
                    velocidad=a["velocidad"], tiempo_siguiente=eg.tiempo_siguiente,
                    id_instancia=eg.instancia, tipo_catalogo=eg.tipo, comportamiento=a["comportamiento"],
                    sala_actual=sg.sala_id if eg.activo else None))
            for og in sg.objetos_suelo:
                self.objetos_en_suelo[sg.sala_id].append(ObjetoInstancia(
                    id_instancia=og.instancia, tipo_catalogo=og.tipo, ubicacion="suelo", sala=sg.sala_id))
            for tg in sg.trampas:
                sala.trampa = Trampa(id_instancia=tg.instancia, tipo_catalogo=tg.tipo, armada=tg.armada)

        # eventos: primero fin_veneno (crea el veneno), después el resto
        for eg in estado.eventos:
            if eg.tipo == "fin_veneno":
                self._restaurar_evento(eg)
        for eg in estado.eventos:
            if eg.tipo != "fin_veneno":
                self._restaurar_evento(eg)
        self.cola.fijar_contador(estado.siguiente_secuencia)

        self.historial = HistorialRetroceso(self.registro_rastro)

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
            self._avanzar_actor(self.jugador, _COSTO_ESPERAR)
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
            self._avanzar_actor(self.jugador, _COSTO_RECOGER)
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
            self._avanzar_actor(self.jugador, _COSTO_SOLTAR)
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

            ataque_antes = self.jugador.ataque
            defensa_antes = self.jugador.defensa
            self.historial.registrar_inventario(
                lambda a=ataque_antes, d=defensa_antes: (
                    setattr(self.jugador, "ataque", a),
                    setattr(self.jugador, "defensa", d),
                )
            )
            inventario.equipar_actual(ficha.clase)
            if ficha.clase == "arma":
                self.jugador.ataque += ficha.atributos.get("ataque_bonus", 0)
            else:
                self.jugador.defensa += ficha.atributos.get("defensa_bonus", 0)

            self._avanzar_actor(self.jugador, _COSTO_EQUIPAR)
            ok, error = True, None
        elif accion == "usar":
            if not self._posicionar_cursor_en(argumento):
                return ResultadoAccion(ok=False, mensaje="No tenés ese objeto en el inventario")
            inventario = self.jugador.inventario
            objeto = inventario.objeto_actual()
            ficha = self.gestor_precarga.catalogo.obtener_fichas([objeto.tipo_catalogo])[0]

            if ficha.clase == "pocion" and "cura" in ficha.atributos:
                self.historial.registrar_vida(self.jugador, self.jugador.vida)
                self.jugador.vida = min(self.jugador.vida_max, self.jugador.vida + ficha.atributos["cura"])
            elif ficha.clase == "pocion" and "modificador_velocidad" in ficha.atributos:
                velocidad_anterior = self.jugador.velocidad
                velocidad_nueva = int(velocidad_anterior * ficha.atributos["modificador_velocidad"])
                self.historial.registrar_inventario(
                    lambda v=velocidad_anterior: setattr(self.jugador, "velocidad", v)
                )
                self.cambiar_velocidad(self.jugador, velocidad_nueva)
            elif ficha.clase == "antidoto":
                self.efectos.cancelar_veneno(self.jugador)
            elif ficha.clase == "antorcha":
                self.efectos.encender_antorcha(objeto, ficha.atributos.get("duracion", 0))
            else:
                return ResultadoAccion(ok=False, mensaje="Ese objeto no se puede usar")

            inventario.quitar_nodo(inventario.cursor)
            self._avanzar_actor(self.jugador, _COSTO_USAR_OBJETO)
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
        elif evento.tipo == "restaurar_velocidad":
            actor, velocidad_base = evento.referencia
            self.cambiar_velocidad(actor, velocidad_base)
        elif evento.tipo == "turno_jugador":
            pass

        return evento


def crear_juego(gestor_precarga, cripta_id, semilla, notificar=None):
    from modelo.snapshots import MetaPartida
    from modelo.inventario import Inventario

    gestor_precarga.generales = None
    gestor_precarga.salas = []
    gestor_precarga.contenidos = []
    gestor_precarga.pendiente = None
    gestor_precarga.red_compatible = True
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
    visitantes = motor.enemigos_por_sala[id_sala]
    if not motor.contenido_cargado[id_sala]:
        motor.enemigos_por_sala[id_sala] = enemigos_de_la_sala + visitantes

    objetos_de_la_sala = []
    for indice, tipo_objeto in enumerate(contenido.get("objetos", [])):
        objetos_de_la_sala.append(ObjetoInstancia(
            id_instancia=f"obj-{id_sala}-{indice}",
            tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
        ))
    existentes = motor.objetos_en_suelo[id_sala]
    if not motor.contenido_cargado[id_sala]:
        motor.objetos_en_suelo[id_sala] = objetos_de_la_sala + existentes

    trampas_json = contenido.get("trampas", [])
    if trampas_json:
        trampa_json = trampas_json[0]
        motor.salas[id_sala].trampa = Trampa(
            id_instancia=trampa_json["instancia"],
            tipo_catalogo=trampa_json["tipo"],
        )

    motor.contenido_cargado[id_sala] = True