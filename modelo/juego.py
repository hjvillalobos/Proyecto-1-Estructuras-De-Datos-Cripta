# modelo/juego.py

import random
from copy import copy, deepcopy
from red.errores import ErrorCripta
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
        self._puertas_iniciales = [
            (sala.id, direccion, "cerrada" in salida, salida.get("cerrada", False))
            for sala in salas_lista for direccion, salida in sala.salidas.items()
        ]

        self.cola = ColaEventos()
        self.azar = random.Random(semilla)
        self.reloj = 0

        self.enemigos_por_sala = [[] for _ in range(salas_total + 1)]
        self.objetos_en_suelo = [[] for _ in range(salas_total + 1)]
        self.contenido_cargado = [False] * (salas_total + 1)

        self.efectos = GestorEfectos(self)
        self.registro_rastro = RegistroRastro()
        self.registro_rastro.marcar_visita(self.jugador.posicion_actual, 0)
        self.historial = HistorialRetroceso(self.registro_rastro, self.cola)

        self.meta = None
        self.gestor_precarga = None
        self.acciones_jugador = 0
        self.enemigos_derrotados = 0
        self.terminado = False
        self.resultado = None       # "victoria" | "derrota" | None
        self.sala_salida = None     # lo llena crear_juego()
        self.llave_salida = None    # lo llena crear_juego()
        self.meta = None
        self._notificador = None

    def establecer_notificador(self, notificador):
        self._notificador = notificador

    def informar(self, mensaje):
        if self._notificador is not None:
            self._notificador(f"t={self.reloj}  {mensaje}")

    def nombre_actor(self, actor):
        if actor is self.jugador:
            return "Jugador"
        return self._resolver_ficha(actor.tipo_catalogo).nombre + f" [{actor.id_instancia}]"

    # ---------- enemigos ----------

    def activar_enemigos_de_sala(self, id_sala, enemigos_de_la_sala):
        from utilidades.ordenamiento import ordenar
        dormidos = [e for e in enemigos_de_la_sala if e.sala_actual is None and e.vida > 0]
        for enemigo in ordenar(dormidos, clave=lambda e: e.id_instancia):
            self.historial.registrar_atributo(enemigo, "sala_actual")
            enemigo.sala_actual = id_sala
            self._avanzar_actor(enemigo, _COSTO_ATACAR)

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

    def _buscar_enemigo_en_sala_actual(self, id_instancia):
        for enemigo in self.enemigos_por_sala[self.jugador.posicion_actual]:
            if enemigo.id_instancia == id_instancia:
                return enemigo
        return None

    def _tiene_llave(self, llave_id):
        for objeto in self.jugador.inventario:
            if objeto.tipo_catalogo == llave_id and self._resolver_clase(objeto.tipo_catalogo) == "llave":
                return True
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
            self.programar_evento(tiempo_cierre, "cierre_puerta", (sala_actual, direccion))

        return True, None

    def mover(self, direccion):
        puede, error = self.puede_moverse(direccion)
        if not puede:
            return False, error

        salida = self.salas[self.jugador.posicion_actual].salidas[direccion]
        id_destino = salida["sala"]

        if not self.contenido_cargado[id_destino]:
            sala_preparada = self.gestor_precarga.preparar_entrada(id_destino, self._ids_en_uso(id_destino))
            _incorporar_sala_preparada(self, sala_preparada)

        sala_destino = self.salas[id_destino]
        pos_anterior = self.jugador.posicion_actual
        self.historial.registrar_inventario(lambda p=pos_anterior: setattr(self.jugador, "posicion_actual", p))
        self.jugador.posicion_actual = id_destino
        self._sincronizar_referencias()
        self._avanzar_actor(self.jugador, _COSTO_MOVER)
        self.historial.registrar_rastro(id_destino, self.registro_rastro.tiempo_de(id_destino))
        self.registro_rastro.marcar_visita(id_destino, self.reloj)

        self.activar_enemigos_de_sala(id_destino, self.enemigos_por_sala[id_destino])
        try:
            self.gestor_precarga.anticipar(id_destino)
        except ErrorCripta as error:
            self.informar(f"Precarga anticipada no disponible: {error}")

        for trampa in sala_destino.trampas:
            if self.terminado:
                break
            self.efectos.activar_trampa(trampa)

        if (not self.terminado and id_destino == self.sala_salida
                and (salida.get("llave") == self.llave_salida or self._tiene_llave(self.llave_salida))):
            self.historial.registrar_atributo(self, "terminado")
            self.historial.registrar_atributo(self, "resultado")
            self.terminado = True
            self.resultado = "victoria"

        return True, None

    # ---------- combate ----------

    def atacar(self, atacante, defensor):
        dano = calcular_dano(atacante, defensor, self.azar)
        self.historial.registrar_vida(defensor, defensor.vida)
        defensor.vida = max(0, defensor.vida - dano)
        if self._notificador is not None:
            self.informar(f"{self.nombre_actor(atacante)} ataca a {self.nombre_actor(defensor)}: {dano} de dano.")
        if defensor.vida == 0:
            self._matar(defensor)
        self._avanzar_actor(atacante, _COSTO_ATACAR)
        return dano

    def _matar(self, actor):
        if self._notificador is not None:
            self.informar(f"{self.nombre_actor(actor)} muere.")
        if actor.evento_pendiente is not None:
            self.cancelar_evento(actor.evento_pendiente)
            self.historial.registrar_atributo(actor, "evento_pendiente")
            actor.evento_pendiente = None
        self.efectos.cancelar_veneno(actor)

        if actor is self.jugador:
            self.historial.registrar_atributo(self, "terminado")
            self.historial.registrar_atributo(self, "resultado")
            self.terminado = True
            self.resultado = "derrota"
        else:
            self.enemigos_derrotados += 1
            self.historial.registrar_inventario(
                lambda v=self.enemigos_derrotados: setattr(self, "enemigos_derrotados", v - 1)
            )
            self._sincronizar_referencias()
            self._soltar_botin(actor)
            self._sincronizar_referencias()

    def _soltar_botin(self, enemigo):
        ficha = self.gestor_precarga.catalogo.obtener_fichas([enemigo.tipo_catalogo])[0]
        id_sala = enemigo.sala_actual
        if id_sala is None:
            return
        for indice, tipo_objeto in enumerate(ficha.atributos.get("suelta", [])):
            id_objeto = f"botin-{enemigo.id_instancia}-{indice}"
            pergamino = self._resolver_clase(tipo_objeto) == "pergamino_retroceso"
            if pergamino and (any(o.id_instancia == id_objeto for o in self.jugador.inventario)
                              or any(o.id_instancia == id_objeto
                                     for suelo in self.objetos_en_suelo for o in suelo)):
                continue
            obj = ObjetoInstancia(
                id_instancia=id_objeto,
                tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
            )
            self.objetos_en_suelo[id_sala].append(obj)
            if not pergamino:
                self.historial.registrar_inventario(
                    lambda lista=self.objetos_en_suelo[id_sala], o=obj: lista.remove(o)
                )

    def cambiar_velocidad(self, actor, velocidad_nueva):
        evento_viejo = actor.evento_pendiente
        velocidad_anterior = actor.velocidad
        self.historial.registrar_atributo(actor, "velocidad")
        actor.velocidad = velocidad_nueva
        if evento_viejo is None:
            return
        restante = max(1, (evento_viejo.tiempo - self.reloj) * velocidad_anterior // velocidad_nueva)
        nuevo_tiempo = self.reloj + restante
        self.historial.registrar_atributo(actor, "tiempo_siguiente")
        self.historial.registrar_atributo(actor, "evento_pendiente")
        self.cancelar_evento(evento_viejo)
        actor.tiempo_siguiente = nuevo_tiempo
        actor.evento_pendiente = self.programar_evento(nuevo_tiempo, evento_viejo.tipo, actor)

    def programar_evento(self, tiempo, tipo, referencia):
        evento = self.cola.insertar(tiempo, tipo, referencia)
        self.historial.registrar_evento_creado(evento)
        return evento

    def cancelar_evento(self, evento):
        if not evento.cancelado:
            self.historial.registrar_evento_cancelado(evento)
            self.cola.cancelar(evento)

    def _avanzar_actor(self, actor, costo):
        intervalo = calcular_intervalo(costo, actor.velocidad)
        self.historial.registrar_atributo(actor, "tiempo_siguiente")
        self.historial.registrar_atributo(actor, "evento_pendiente")
        actor.tiempo_siguiente = self.reloj + intervalo
        if actor.evento_pendiente is not None:
            self.cancelar_evento(actor.evento_pendiente)
        tipo_evento = "turno_jugador" if actor is self.jugador else "turno_enemigo"
        actor.evento_pendiente = self.programar_evento(actor.tiempo_siguiente, tipo_evento, actor)

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
        return self.jugador.inventario.seleccionar(id_instancia)

    def _ids_en_uso(self, id_sala=None):
        ids = []
        for lista_enemigos in self.enemigos_por_sala:
            for enemigo in lista_enemigos:
                if (enemigo.vida > 0 and enemigo.sala_actual is not None
                        and enemigo.tipo_catalogo not in ids):
                    ids.append(enemigo.tipo_catalogo)
        actual = self.jugador.posicion_actual if id_sala is None else id_sala
        for objeto in self.objetos_en_suelo[actual]:
            if objeto.tipo_catalogo not in ids:
                ids.append(objeto.tipo_catalogo)
        for trampa in self.salas[actual].trampas:
            if trampa.tipo_catalogo not in ids:
                ids.append(trampa.tipo_catalogo)

        for objeto in self.jugador.inventario:
            if objeto.tipo_catalogo not in ids:
                ids.append(objeto.tipo_catalogo)
        return ids

    def _sincronizar_referencias(self):
        if self.gestor_precarga is not None:
            fijar = getattr(self.gestor_precarga.catalogo, "fijar_referencias", None)
            if fijar is not None:
                fijar(self._ids_en_uso())

    # ---------- vista / resumen ----------

    def estado_vista(self):
        from modelo.snapshots import EstadoVista, SalidaVista, EnemigoVista, ItemVista
        from modelo.snapshots import TrampaVista, EventoVista
        from modelo.inventario import descripcion_objeto
        from utilidades.ordenamiento import ordenar

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
                tipo=enemigo.tipo_catalogo, ataque=enemigo.ataque, defensa=enemigo.defensa,
                velocidad=enemigo.velocidad, tiempo_siguiente=enemigo.tiempo_siguiente,
                comportamiento=enemigo.comportamiento,
            ))

        efectos_activos = []
        if self.jugador.veneno is not None:
            efectos_activos.append("veneno")

        jug = self.jugador
        if self.efectos.antorchas_encendidas:
            efectos_activos.append("antorcha")
        velocidad_base = jug.velocidad
        if self.gestor_precarga and self.gestor_precarga.generales:
            jugador_gen = self.gestor_precarga.generales.get("jugador")
            if jugador_gen is not None:
                velocidad_base = jugador_gen.get("velocidad", jug.velocidad)
        if jug.velocidad != velocidad_base:
            efectos_activos.append("velocidad")

                # Objetos presentes en el suelo de la sala actual
        from modelo.snapshots import ItemVista

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
                    detalle=descripcion_objeto(ficha),
                    tipo=objeto.tipo_catalogo,
                )
            )

        # Capacidad y cantidad real del inventario
        inventario_usado = len(jug.inventario.a_lista_guardado())
        inventario_max = jug.inventario.capacidad_max
        trampas = []
        for trampa in sala.trampas:
            ficha = self._resolver_ficha(trampa.tipo_catalogo)
            trampas.append(TrampaVista(trampa.id_instancia, ficha.nombre, trampa.armada,
                                      ficha.atributos.get("daño", 0), tipo=trampa.tipo_catalogo))
        agenda = []
        nombres = (("pulso_veneno", "Pulso de veneno"), ("fin_veneno", "Fin del veneno"),
                   ("apagar_antorcha", "Se apaga la antorcha"),
                   ("restaurar_velocidad", "Termina el efecto de velocidad"))
        for evento in self.cola.pendientes():
            nombre = None
            if evento.tipo == "turno_enemigo" and evento.referencia.sala_actual == sala.id:
                nombre = self.nombre_actor(evento.referencia)
            elif evento.tipo == "rearmar_trampa" and evento.referencia in sala.trampas:
                nombre = "Se rearma una trampa"
            elif evento.tipo == "cierre_puerta" and evento.referencia[0].id == sala.id:
                nombre = "Se cierra la puerta " + evento.referencia[1]
            else:
                for tipo, etiqueta in nombres:
                    if evento.tipo == tipo:
                        if tipo in ("pulso_veneno", "fin_veneno") and evento.referencia is not jug:
                            continue
                        nombre = etiqueta
            if nombre is not None:
                agenda.append((evento, nombre))
        agenda = [EventoVista(e.tiempo, nombre)
                  for e, nombre in ordenar(agenda, clave=lambda par: (par[0].tiempo, par[0].secuencia))[:4]]
        costos = [(nombre, calcular_intervalo(costo, jug.velocidad)) for nombre, costo in (
            ("mover", _COSTO_MOVER), ("atacar", _COSTO_ATACAR), ("esperar", _COSTO_ESPERAR),
            ("usar", _COSTO_USAR_OBJETO), ("equipar", _COSTO_EQUIPAR),
            ("recoger", _COSTO_RECOGER), ("soltar", _COSTO_SOLTAR), ("abrir", _COSTO_ABRIR_PUERTA))]

        return EstadoVista(
            reloj=self.reloj, sala_id=sala.id, sala_nombre=sala.nombre,
            salidas=salidas, enemigos=enemigos_vista,
            objetos_suelo=objetos_vista,
            vida=self.jugador.vida, vida_max=self.jugador.vida_max,
            ataque=self.jugador.ataque, defensa=self.jugador.defensa, velocidad=self.jugador.velocidad,
            inventario_usado=inventario_usado,
            inventario_max=inventario_max,
            efectos=efectos_activos,
            trampas=trampas, agenda=agenda, costos=costos,
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
        if t == "restaurar_velocidad":
            actor, velocidad_base = e.referencia
            return EventoGuardado(e.tiempo, e.secuencia, t, self._id_actor(actor), [velocidad_base])
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
                trampas=[TrampaGuardada(instancia=t.id_instancia, tipo=t.tipo_catalogo,
                                       armada=t.armada) for t in sala.trampas],
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
            if sala is not None:
                for trampa in sala.trampas:
                    if trampa.id_instancia == id_instancia:
                        return trampa
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
            antorcha = ObjetoInstancia(
                id_instancia=eg.objetivo, tipo_catalogo="", ubicacion="efecto", encendida=True)
            self.efectos.antorchas_encendidas.append(antorcha)
            ins(eg.tiempo, eg.secuencia, t, antorcha)
        elif t == "rearmar_trampa":
            trampa = self._trampa_por_id(eg.objetivo)
            if trampa is not None:
                ins(eg.tiempo, eg.secuencia, t, trampa)
        elif t == "cierre_puerta":
            id_sala, direccion = eg.objetivo.split(":")
            ins(eg.tiempo, eg.secuencia, t, (self.salas[int(id_sala)], direccion))
        elif t == "restaurar_velocidad":
            actor = self._actor_por_id(eg.objetivo)
            if actor is not None:
                actor.evento_velocidad = ins(eg.tiempo, eg.secuencia, t, (actor, eg.parametros[0]))

    def validar_estado(self, estado):
        if self.meta is not None:
            for campo in ("cripta_id", "cripta_version", "catalogo_version"):
                if getattr(self.meta, campo) != getattr(estado.meta, campo):
                    raise ValueError(f"Guardado incompatible: {campo} no coincide con la partida.")
        ids = [estado.jugador.sala_id] + estado.jugador.extras[2:] + [s.sala_id for s in estado.salas]
        if len(estado.jugador.extras) < 2 or any(
                type(i) is not int or not 0 <= i < len(self.salas) or self.salas[i] is None
                for i in ids):
            raise ValueError("Guardado incompatible: salas o indicadores invalidos.")

        random.Random().setstate(estado.rng_estado)
        j = estado.jugador
        valores = (estado.reloj, estado.siguiente_secuencia, estado.acciones_jugador,
                   estado.enemigos_derrotados, j.vida, j.ataque, j.defensa, j.tiempo_siguiente)
        if any(type(v) is not int or v < 0 for v in valores) or any(
                type(v) is not int or v < 1 for v in (j.vida_max, j.velocidad)):
            raise ValueError("Guardado invalido: estadisticas o reloj.")
        if j.vida > j.vida_max or len(j.inventario) > self.jugador.inventario.capacidad_max:
            raise ValueError("Guardado invalido: vida o capacidad.")
        if j.extras[0] not in (0, 1) or j.extras[1] not in (0, 1, 2):
            raise ValueError("Guardado invalido: resultado.")
        actores = ["jugador"] + [e.instancia for s in estado.salas for e in s.enemigos]
        trampas = [t.instancia for s in estado.salas for t in s.trampas]
        cantidades = (("turno_jugador", 0), ("turno_enemigo", 0), ("pulso_veneno", 0),
                      ("fin_veneno", 2), ("pulso_regeneracion", 2), ("apagar_antorcha", 0),
                      ("rearmar_trampa", 0), ("cierre_puerta", 0), ("restaurar_velocidad", 1))
        secuencias = []
        for evento in estado.eventos:
            cantidad = next((n for tipo, n in cantidades if tipo == evento.tipo), None)
            if cantidad is None or len(evento.parametros) != cantidad or any(
                    type(p) is not int or p < 1 for p in evento.parametros):
                raise ValueError("Guardado invalido: parametros de evento.")
            if (type(evento.tiempo) is not int or evento.tiempo < estado.reloj
                    or type(evento.secuencia) is not int or not 0 <= evento.secuencia < estado.siguiente_secuencia
                    or evento.secuencia in secuencias):
                raise ValueError("Guardado invalido: tiempo o secuencia de evento.")
            secuencias.append(evento.secuencia)
            if evento.tipo == "cierre_puerta":
                try:
                    sala, direccion = evento.objetivo.split(":")
                    sala = int(sala)
                    valido = 0 <= sala < len(self.salas) and self.salas[sala] is not None and direccion in self.salas[sala].salidas
                except (ValueError, AttributeError):
                    valido = False
            elif evento.tipo == "rearmar_trampa":
                valido = evento.objetivo in trampas
            elif evento.tipo == "apagar_antorcha":
                valido = isinstance(evento.objetivo, str) and bool(evento.objetivo)
            else:
                valido = evento.objetivo in actores
            if not valido:
                raise ValueError("Guardado invalido: objetivo de evento.")

    def restaurar_estado(self, estado):
        self.validar_estado(estado)
        # Construir la carga fuera de la partida viva; el historial sigue usando deltas.
        preparado = copy(self)
        preparado.jugador = deepcopy(self.jugador)
        preparado.salas = deepcopy(self.salas)
        preparado.registro_rastro = deepcopy(self.registro_rastro)
        preparado.azar = random.Random()
        catalogo = self.gestor_precarga.catalogo
        if hasattr(catalogo, "cache"):
            preparado.gestor_precarga = copy(self.gestor_precarga)
            preparado.gestor_precarga.catalogo = copy(catalogo)
            preparado.gestor_precarga.catalogo.cache = deepcopy(catalogo.cache)
        preparado._restaurar_estado_validado(estado)
        if hasattr(catalogo, "cache"):
            catalogo.cache.__dict__.update(preparado.gestor_precarga.catalogo.cache.__dict__)
            for campo in ("aciertos", "fallos", "recuperaciones_disco"):
                setattr(catalogo, campo, getattr(preparado.gestor_precarga.catalogo, campo))
        preparado.gestor_precarga = self.gestor_precarga
        # Conservar las referencias publicas del jugador, salas y puertas.
        for i, sala in enumerate(self.salas):
            if sala is None:
                continue
            nueva = preparado.salas[i]
            for direccion, salida in sala.salidas.items():
                salida.clear()
                salida.update(nueva.salidas[direccion])
            sala.trampas = nueva.trampas
            preparado.salas[i] = sala
        jugador = self.jugador
        jugador.__dict__.update(preparado.jugador.__dict__)
        for evento in preparado.cola.pendientes():
            if evento.referencia is preparado.jugador:
                evento.referencia = jugador
            elif evento.tipo == "restaurar_velocidad" and evento.referencia[0] is preparado.jugador:
                evento.referencia = (jugador, evento.referencia[1])
            elif evento.tipo == "cierre_puerta":
                sala, direccion = evento.referencia
                evento.referencia = (self.salas[sala.id], direccion)
        preparado.jugador = jugador
        self.__dict__.update(preparado.__dict__)
        self.efectos.motor = self

    def _restaurar_estado_validado(self, estado):
        from modelo.tipos import InstanciaEnemigo, ObjetoInstancia, Trampa
        from modelo.inventario import Inventario

        if self.gestor_precarga is not None:
            fijar = getattr(self.gestor_precarga.catalogo, "fijar_referencias", None)
            if fijar is not None:
                fijar([])
        n = len(self.salas)
        self.cola = ColaEventos()
        self.efectos = GestorEfectos(self)
        self.reloj = estado.reloj
        self.meta = estado.meta
        self.azar.setstate(estado.rng_estado)
        self.acciones_jugador = estado.acciones_jugador
        self.enemigos_derrotados = estado.enemigos_derrotados
        self.enemigos_por_sala = [[] for _ in range(n)]
        self.objetos_en_suelo = [[] for _ in range(n)]
        self.contenido_cargado = [False] * n
        for id_sala, direccion, tenia_campo, cerrada in self._puertas_iniciales:
            salida = self.salas[id_sala].salidas[direccion]
            if tenia_campo:
                salida["cerrada"] = cerrada
            else:
                salida.pop("cerrada", None)
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
        j.evento_velocidad = None
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
                sala.trampas.append(Trampa(id_instancia=tg.instancia, tipo_catalogo=tg.tipo, armada=tg.armada))

        # eventos: primero fin_veneno (crea el veneno), después el resto
        for eg in estado.eventos:
            if eg.tipo == "fin_veneno":
                self._restaurar_evento(eg)
        for eg in estado.eventos:
            if eg.tipo != "fin_veneno":
                self._restaurar_evento(eg)
        self.cola.fijar_contador(estado.siguiente_secuencia)

        self.historial = HistorialRetroceso(self.registro_rastro, self.cola)
        self._sincronizar_referencias()

    def ejecutar(self, accion, argumento=None):
        from modelo.snapshots import ResultadoAccion
        from modelo.enemigos import decidir_accion

        if accion == "retroceso":
            pergamino = next((objeto for objeto in self.jugador.inventario
                              if self._resolver_clase(objeto.tipo_catalogo) == "pergamino_retroceso"), None)
            if pergamino is None:
                return ResultadoAccion(ok=False, mensaje="No tenés pergaminos de retroceso")
            reloj_anterior = self.historial.usar_pergamino(
                self.jugador.inventario, pergamino.tipo_catalogo)
            if reloj_anterior is None:
                return ResultadoAccion(ok=False, mensaje="No hay nada que deshacer")
            self.reloj = reloj_anterior
            self._sincronizar_referencias()
            self.informar("Retroceso: se restaura la accion anterior.")
            return ResultadoAccion(ok=True)

        if self.terminado:
            return ResultadoAccion(ok=False, mensaje="La partida ya terminó")

        self.historial.iniciar_turno(self.reloj)
        azar_anterior = self.azar.getstate()
        secuencia_anterior = self.cola.proxima_secuencia()
        self.historial.registrar_cambio(lambda: self.azar.setstate(azar_anterior))
        self.historial.registrar_cambio(lambda: self.cola.fijar_contador(secuencia_anterior))
        inventario = self.jugador.inventario
        for atributo in ("cursor", "arma_equipada", "armadura_equipada"):
            self.historial.registrar_atributo(inventario, atributo)
        sala_origen = self.jugador.posicion_actual

        if accion == "mover":
            ok, error = self.mover(argumento)
        elif accion == "abrir":
            ok, error = self.abrir_puerta(argumento)
        elif accion == "atacar":
            enemigo = self._buscar_enemigo_en_sala_actual(argumento)
            if enemigo is None or enemigo.vida <= 0:
                return self._rechazar_accion("Ese enemigo no está vivo en tu sala")
            self.atacar(self.jugador, enemigo)
            ok, error = True, None
        elif accion == "esperar":
            self._avanzar_actor(self.jugador, _COSTO_ESPERAR)
            ok, error = True, None
        elif accion == "recoger":
            objetos_sala = self.objetos_en_suelo[self.jugador.posicion_actual]
            objeto = next((o for o in objetos_sala if o.id_instancia == argumento), None)
            if objeto is None:
                return self._rechazar_accion("Ese objeto no está en el suelo de esta sala")
            if inventario.esta_lleno():
                return self._rechazar_accion("Inventario lleno")
            reversible = self._resolver_clase(objeto.tipo_catalogo) != "pergamino_retroceso"
            indice = objetos_sala.index(objeto)
            if reversible:
                self.historial.registrar_atributo(objeto, "ubicacion")
                self.historial.registrar_atributo(objeto, "sala")
            nodo = inventario.recoger(objeto)
            objetos_sala.remove(objeto)
            if reversible:
                self.historial.registrar_inventario(lambda n=nodo: inventario.quitar_nodo(n))
                self.historial.registrar_inventario(
                    lambda lista=objetos_sala, i=indice, o=objeto: lista.insert(i, o))
            self._avanzar_actor(self.jugador, _COSTO_RECOGER)
            ok, error = True, None
        elif accion == "soltar":
            if not self._posicionar_cursor_en(argumento):
                return self._rechazar_accion("No tenés ese objeto en el inventario")
            nodo_actual = inventario.cursor
            anterior = nodo_actual.anterior
            objeto = nodo_actual.objeto
            reversible = self._resolver_clase(objeto.tipo_catalogo) != "pergamino_retroceso"
            if reversible:
                self.historial.registrar_atributo(objeto, "ubicacion")
                self.historial.registrar_atributo(objeto, "sala")
            if nodo_actual is inventario.arma_equipada:
                self.historial.registrar_atributo(self.jugador, "ataque")
                self.jugador.ataque -= self._resolver_ficha(objeto.tipo_catalogo).atributos.get("ataque_bonus", 0)
            if nodo_actual is inventario.armadura_equipada:
                self.historial.registrar_atributo(self.jugador, "defensa")
                self.jugador.defensa -= self._resolver_ficha(objeto.tipo_catalogo).atributos.get("defensa_bonus", 0)
            objeto = inventario.soltar_actual()
            objeto.ubicacion = "suelo"
            objeto.sala = self.jugador.posicion_actual
            objetos_sala = self.objetos_en_suelo[self.jugador.posicion_actual]
            objetos_sala.append(objeto)
            if reversible:
                self.historial.registrar_inventario(
                    lambda a=anterior, n=nodo_actual: inventario.reinsertar_nodo(n, a))
                self.historial.registrar_inventario(lambda lista=objetos_sala, o=objeto: lista.remove(o))
            self._avanzar_actor(self.jugador, _COSTO_SOLTAR)
            ok, error = True, None
        elif accion == "equipar":
            if not self._posicionar_cursor_en(argumento):
                return self._rechazar_accion("No tenés ese objeto en el inventario")
            objeto = inventario.objeto_actual()
            ficha = self.gestor_precarga.catalogo.obtener_fichas([objeto.tipo_catalogo])[0]
            if ficha.clase not in ("arma", "armadura"):
                return self._rechazar_accion("Ese objeto no se puede equipar")

            self.historial.registrar_atributo(self.jugador, "ataque")
            self.historial.registrar_atributo(self.jugador, "defensa")
            nodo_actual = inventario.cursor
            anterior = nodo_actual.anterior
            self.historial.registrar_inventario(
                lambda n=nodo_actual, a=anterior: inventario.mover_despues(n, a))
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

            self._avanzar_actor(self.jugador, _COSTO_EQUIPAR)
            ok, error = True, None
        elif accion == "usar":
            if not self._posicionar_cursor_en(argumento):
                return self._rechazar_accion("No tenés ese objeto en el inventario")
            objeto = inventario.objeto_actual()
            ficha = self.gestor_precarga.catalogo.obtener_fichas([objeto.tipo_catalogo])[0]

            if ficha.clase == "pocion" and "cura" in ficha.atributos:
                self.historial.registrar_vida(self.jugador, self.jugador.vida)
                self.jugador.vida = min(self.jugador.vida_max, self.jugador.vida + ficha.atributos["cura"])
            elif ficha.clase == "pocion" and "modificador_velocidad" in ficha.atributos:
                velocidad_base = self.jugador.velocidad
                anterior = self.jugador.evento_velocidad
                if anterior is not None and not anterior.cancelado:
                    velocidad_base = anterior.referencia[1]
                    self.cancelar_evento(anterior)
                duracion = ficha.atributos.get("duracion", 500)
                nueva_velocidad = max(1, int(velocidad_base * ficha.atributos["modificador_velocidad"]))
                self.cambiar_velocidad(self.jugador, nueva_velocidad)
                self.historial.registrar_atributo(self.jugador, "evento_velocidad")
                self.jugador.evento_velocidad = self.programar_evento(
                    self.reloj + duracion,
                    "restaurar_velocidad",
                    (self.jugador, velocidad_base),
                )
            elif ficha.clase == "antidoto":
                self.efectos.cancelar_veneno(self.jugador)
            elif ficha.clase == "antorcha":
                self.efectos.encender_antorcha(objeto, ficha.atributos.get("duracion", 0))
            elif ficha.clase == "pergamino_retroceso":
                self.historial.descartar_turno()
                return self.ejecutar("retroceso")
            else:
                return self._rechazar_accion("Ese objeto no se puede usar")

            nodo_actual = inventario.cursor
            anterior = nodo_actual.anterior
            inventario.quitar_nodo(nodo_actual)
            self.historial.registrar_inventario(
                lambda n=nodo_actual, a=anterior: inventario.reinsertar_nodo(n, a))
            self._avanzar_actor(self.jugador, _COSTO_USAR_OBJETO)
            ok, error = True, None
        else:
            return self._rechazar_accion("Acción desconocida")

        if not ok:
            return self._rechazar_accion(error)

        if self._notificador is not None:
            if accion in ("recoger", "soltar", "equipar", "usar"):
                from modelo.inventario import descripcion_objeto
                ficha_accion = self._resolver_ficha(objeto.tipo_catalogo)
                verbos = (("recoger", "Recoges"), ("soltar", "Sueltas"),
                          ("equipar", "Equipas"), ("usar", "Usas"))
                verbo = next(texto for clave, texto in verbos if clave == accion)
                self.informar(f"{verbo} {ficha_accion.nombre}. {descripcion_objeto(ficha_accion)}")
            elif accion == "mover":
                self.informar(f"Entras en {self.salas[self.jugador.posicion_actual].nombre}.")
            elif accion == "abrir":
                self.informar(f"Abres la puerta {argumento}.")
            elif accion == "esperar":
                self.informar("El jugador espera.")

        self.historial.registrar_rastro(sala_origen, self.registro_rastro.tiempo_de(sala_origen))
        self.registro_rastro.marcar_visita(sala_origen, self.reloj)
        self._sincronizar_referencias()

        while not self.terminado:
            evento = self.ejecutar_ciclo(decidir_accion)
            if evento is None or evento.tipo == "turno_jugador" or self.terminado:
                break

        self._sincronizar_referencias()

        self.historial.registrar_atributo(self, "acciones_jugador")
        self.acciones_jugador += 1
        self.historial.cerrar_turno()
        return ResultadoAccion(ok=True)

    def _rechazar_accion(self, mensaje):
        from modelo.snapshots import ResultadoAccion
        self.historial.descartar_turno()
        return ResultadoAccion(ok=False, mensaje=mensaje)

    def ejecutar_ciclo(self, decidir_accion_enemigo):
        evento = self.cola.extraer_minimo()
        if evento is None:
            return None

        self.historial.registrar_evento_extraido(evento)
        self.reloj = evento.tiempo
        if evento.tipo in ("turno_jugador", "turno_enemigo"):
            actor = evento.referencia
            self.historial.registrar_atributo(actor, "evento_pendiente")
            actor.evento_pendiente = None
            if actor.vida <= 0:
                return evento

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
            self.historial.registrar_atributo(actor, "evento_velocidad")
            actor.evento_velocidad = None
            self.cambiar_velocidad(actor, velocidad_base)
        elif evento.tipo == "turno_jugador":
            pass

        return evento


def crear_juego(gestor_precarga, cripta_id, semilla, notificar=None,
                version_cripta=None, version_catalogo=None):
    from modelo.snapshots import MetaPartida
    from modelo.inventario import Inventario

    gestor_precarga.generales = None
    gestor_precarga.salas = []
    gestor_precarga.contenidos = []
    gestor_precarga.pendiente = None
    gestor_precarga.red_compatible = True
    preparada = gestor_precarga.preparar_cripta(cripta_id, version_cripta, version_catalogo)
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

    # Si la sala ya fue cargada, conservar el estado del motor tal cual.
    # No recrear enemigos derrotados ni objetos ya recogidos.
    if motor.contenido_cargado[id_sala]:
        return

    def ficha_de(id_tipo):
        for ficha in sala_preparada.fichas:
            if ficha.id == id_tipo:
                return ficha
        return None

    ids_enemigos_existentes = {
        e.id_instancia for e in motor.enemigos_por_sala[id_sala]
    }
    enemigos_nuevos = []
    for enemigo_json in contenido.get("enemigos", []):
        if enemigo_json["instancia"] in ids_enemigos_existentes:
            continue
        ficha = ficha_de(enemigo_json["tipo"])
        enemigos_nuevos.append(InstanciaEnemigo(
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
    motor.enemigos_por_sala[id_sala] = enemigos_nuevos + visitantes

    ids_objetos_existentes = {
        o.id_instancia for o in motor.objetos_en_suelo[id_sala]
    }
    objetos_nuevos = []
    for indice, tipo_objeto in enumerate(contenido.get("objetos", [])):
        id_instancia = f"obj-{id_sala}-{indice}"
        if id_instancia in ids_objetos_existentes:
            continue
        objetos_nuevos.append(ObjetoInstancia(
            id_instancia=id_instancia,
            tipo_catalogo=tipo_objeto, ubicacion="suelo", sala=id_sala,
        ))
    existentes = motor.objetos_en_suelo[id_sala]
    motor.objetos_en_suelo[id_sala] = objetos_nuevos + existentes

    trampas_json = contenido.get("trampas", [])
    for trampa_json in trampas_json:
        if not any(t.id_instancia == trampa_json["instancia"] for t in motor.salas[id_sala].trampas):
            motor.salas[id_sala].trampas.append(Trampa(
                id_instancia=trampa_json["instancia"], tipo_catalogo=trampa_json["tipo"]))

    motor.contenido_cargado[id_sala] = True
