from vista.tema import FONDO, PANEL, TEXTO, TENUE, VERDE, ROJO, AMARILLO, BORDE
from vista.animacion import AnimacionEscena, PASOS_CARRERA
from vista.equipo_visual import dibujar_equipo
from vista.transicion_salas import punto_puerta
from vista.puerta_visual import PuertaVisual
from vista.trampas_visuales import dibujar_trampas, ActivacionTrampa

ESCALA_JUGADOR = .70


class EscenaCripta:
    """Dibuja la sala a partir de datos de presentacion, sin ejecutar reglas."""

    def __init__(self, vista):
        self.vista = vista
        self.imagenes = []
        self.animacion = None
        self.anterior = None
        self._accion_en_curso = None
        self._entrada_en_curso = (0, 0)
        self._objeto_recogido = None
        self._salir_hacia = None
        self._posicion_relativa = .20
        self._direccion_entrada = None
        self._trampas_activadas = []

    def detener(self):
        if self.animacion is not None:
            self.animacion.detener()

    def _actor(self, identificador, fase=0, entrada=False, golpe=False, **movimiento):
        if self.animacion is not None:
            self.animacion.agregar(identificador, fase, entrada, golpe, **movimiento)

    def _imagen(self, nombre, ancho, alto):
        recursos = getattr(self.vista, "recursos", None)
        imagen = recursos.imagen(nombre, int(ancho), int(alto)) if recursos else None
        if imagen is not None:
            self.imagenes.append(imagen)
        return imagen

    def dibujar(self, estado, salir_hacia=None):
        v, c = self.vista, self.vista.canvas
        self._salir_hacia = salir_hacia
        continuar = (estado == self.anterior and self.animacion is not None
                     and getattr(v, "_accion_visual", None) is None)
        paso_anterior = self.animacion.paso if continuar else 0
        accion_anterior = self._accion_en_curso if continuar else None
        if not continuar:
            self._direccion_entrada = None
            self._objeto_recogido = None
            self._trampas_activadas = list(getattr(v, "_trampas_activadas", ()))
            if getattr(v, "_accion_visual", None) == "recoger" and self.anterior is not None:
                self._objeto_recogido = next((objeto for objeto in self.anterior.objetos_suelo
                    if not any(actual.instancia == objeto.instancia for actual in estado.objetos_suelo)), None)
        self.detener()
        if hasattr(v, "root") and getattr(v, "_movimiento_activo", True):
            self.animacion = AnimacionEscena(v.root, c)
        else:
            self.animacion = None
        self._accion_en_curso = accion_anterior
        self._continuar_movimiento = continuar
        if self.animacion is not None:
            self.animacion.paso = paso_anterior
        self.imagenes.clear()
        c.delete("all")
        ancho, alto = c.winfo_width(), c.winfo_height()
        ancho = max(700, ancho) if isinstance(ancho, int) else v.ANCHO
        alto = max(350, alto) if isinstance(alto, int) else v.ALTO
        c.create_rectangle(0, 0, ancho, alto, fill=FONDO, outline="")
        dibujar_fondo = getattr(getattr(v, "recursos", None), "fondo_sala", None)
        fondo = dibujar_fondo(ancho, alto - 82) if callable(dibujar_fondo) else None
        if fondo is not None:
            self.imagenes.append(fondo)
            c.create_image(0, 0, image=fondo, anchor="nw", tags=("fondo_sala",))
        else:
            c.create_rectangle(0, 58, ancho, alto - 82, fill="#594636", outline="")
            for fila, y in enumerate(range(58, alto - 82, 38)):
                for x in range(-45 if fila % 2 else 0, ancho, 90):
                    c.create_rectangle(x + 2, y + 2, x + 88, min(y + 36, alto - 82),
                                       fill="#756047", outline="#a08866")
        c.create_rectangle(0, 0, ancho, 62, fill=FONDO, outline="")
        if fondo is None:
            self._ambiente(estado.sala_nombre, ancho, c)
        self._puertas(estado, ancho, alto, c)
        origenes = dibujar_trampas(self, estado, ancho)
        self._jugador(estado, alto, c)
        self._enemigos(estado, ancho, alto, c)
        self._objetos(estado, ancho, alto, c)
        if self.animacion is not None:
            jugador = c.find_withtag("jugador")
            if jugador:
                for trampa, origen in origenes:
                    if trampa.instancia in self._trampas_activadas:
                        self.animacion.decorar(ActivacionTrampa(c, origen, jugador[0],
                            int(min(280, alto - 175) * ESCALA_JUGADOR),
                            dardos=trampa.tipo == "trp_dardos", etiqueta="disparo_" + trampa.instancia))
            if (self.anterior is None or any(getattr(self.anterior, atributo, None) != getattr(estado, atributo, None)
                                            for atributo in ("arma_tipo", "armadura_tipo"))
                    or (("antorcha" in getattr(self.anterior, "efectos", ())) != ("antorcha" in estado.efectos))):
                recursos = getattr(v, "recursos", None)
                if recursos is not None:
                    for invertir in (False, True):
                        recursos.fotogramas_jugador(290, int(min(280, alto - 175) * ESCALA_JUGADOR),
                            invertir=invertir, armadura=getattr(estado, "armadura_tipo", None),
                            arma=getattr(estado, "arma_tipo", None), antorcha="antorcha" in estado.efectos)
            if salir_hacia is None:
                self.animacion.situar(paso_anterior)
            self.animacion.iniciar()
        self.anterior = estado
        v._accion_visual = None

    def _ambiente(self, nombre, ancho, c):
        nombre = nombre.lower()
        for x in (80, ancho - 80):
            if "urna" in nombre or "nicho" in nombre:
                c.create_oval(x - 17, 102, x + 17, 145, fill="#78644c", outline="#b7a280")
                c.create_rectangle(x - 13, 97, x + 13, 105, fill="#a08a68", outline="")
            elif "osario" in nombre or "cripta" in nombre:
                c.create_rectangle(x - 18, 98, x + 18, 145, fill="#66533e", outline="#a58a67")
                c.create_oval(x - 9, 109, x + 9, 128, fill="#bcc4a5", outline="")
            else:
                c.create_rectangle(x - 13, 92, x + 13, 148, fill="#66533e", outline="#a58a67")

    def _puertas(self, estado, ancho, alto, c):
        direccion = None
        entrando = self._salir_hacia is None
        if not entrando:
            direccion = next((s.direccion for s in estado.salidas
                              if s.destino == self._salir_hacia), None)
        elif self._accion_jugador(estado) == "correr" and self.anterior is not None:
            previa = next((s.direccion for s in self.anterior.salidas
                           if s.destino == estado.sala_id), None)
            direccion = {"N": "S", "S": "N", "E": "O", "O": "E"}.get(previa)
            self._direccion_entrada = direccion
        elif self._continuar_movimiento:
            direccion = self._direccion_entrada
        if direccion is not None and self.animacion is not None:
            self.animacion.decorar(PuertaVisual(c, punto_puerta(direccion, ancho, alto), entrando))
        # El carril izquierdo queda fuera de las celdas y barras de los enemigos.
        sur_x = 145 if estado.enemigos else ancho / 2
        posiciones = (("N", ancho / 2, 40), ("S", sur_x, alto - 104),
                      ("O", 44, alto / 2), ("E", ancho - 44, alto / 2))
        nombres = (("N", "Norte"), ("S", "Sur"), ("O", "Oeste"), ("E", "Este"))
        for salida in estado.salidas:
            posicion = next((p for p in posiciones if p[0] == salida.direccion), None)
            if posicion is None:
                continue
            _, x, y = posicion
            etiqueta = "puerta_" + salida.direccion
            w, h = (98, 34) if salida.direccion in ("N", "S") else (72, 56)
            verbo = "abrir" if salida.cerrada or getattr(salida, "apertura_pendiente", False) else "mover"
            c.create_rectangle(x - w / 2, y - h / 2, x + w / 2, y + h / 2,
                               fill="#403925" if salida.cerrada else "#20392f",
                               outline=AMARILLO if salida.cerrada else VERDE, width=2, tags=(etiqueta,))
            nombre = next(n for d, n in nombres if d == salida.direccion)
            c.create_text(x, y, text=f"{nombre}\n{verbo.capitalize()} {self.vista._costo(verbo)}",
                          fill=TEXTO, font=("Segoe UI", 9), tags=(etiqueta,))
            self.vista._ligar(etiqueta, f"{verbo} {salida.direccion}")

    def _jugador(self, estado, alto, c):
        ancho = c.winfo_width()
        ancho = max(700, ancho) if isinstance(ancho, int) else self.vista.ANCHO
        anterior = self.anterior
        direccion = next((s.direccion for s in getattr(anterior, "salidas", [])
                          if s.destino == estado.sala_id), "E")
        accion_nueva = self._accion_jugador(estado)
        if accion_nueva == "correr" and anterior is not None and anterior.sala_id != estado.sala_id:
            self._posicion_relativa = {"N": .31, "S": .20, "E": .27, "O": .18}[direccion]
        elif anterior is None or getattr(self.vista, "_accion_visual", None) in ("cargar", "retroceso"):
            self._posicion_relativa = .20
        px = min(ancho * self._posicion_relativa, 210 if len(estado.enemigos) > 4 else 240)
        py = alto - 150
        self.vista._jugador_xy = (px, py)
        sombra = c.create_oval(px - 54, py - 12, px + 54, py + 8, fill="#211a13", outline="")
        altura_jugador = int(min(280, alto - 175) * ESCALA_JUGADOR)
        imagen = self._imagen("jugador", 230, altura_jugador)
        recursos = getattr(self.vista, "recursos", None)
        armadura = getattr(estado, "armadura_tipo", None)
        arma = getattr(estado, "arma_tipo", None)
        antorcha = "antorcha" in getattr(estado, "efectos", ())
        armado = (recursos.jugador_armado(230, altura_jugador, arma, armadura, antorcha=antorcha)
                  if recursos and (arma or antorcha) else None)
        vestido = (armado if armado is not None and armadura == "itm_coraza_cuero" else
                   recursos.jugador_vestido(230, altura_jugador, armadura)) if recursos and armadura else None
        if vestido is not None:
            imagen = vestido
            self.imagenes.append(imagen)
        if armado is not None:
            imagen = armado
            self.imagenes.append(imagen)
        if imagen is not None:
            sprite = c.create_image(px, py, image=imagen, anchor="s", tags=("jugador",))
            if vestido is not None:
                c.addtag_withtag("armadura_visible", sprite)
            arma_integrada = armado is not None and arma == "itm_daga_oxidada"
            if arma_integrada:
                c.addtag_withtag("arma_visible", sprite)
            if armado is not None and antorcha:
                c.addtag_withtag("antorcha_visible", sprite)
            cuadros = ()
            indices = ()
            anterior = self.anterior
            accion = self._accion_jugador(estado)
            if accion is None and self._continuar_movimiento:
                accion = self._accion_en_curso
            self._accion_en_curso = accion
            opuesta = {"N": "S", "S": "N", "E": "O", "O": "E"}[direccion]
            inicio = punto_puerta(opuesta, ancho, alto)
            entrada = (inicio[0] - px, inicio[1] - py)
            if self._continuar_movimiento:
                entrada = self._entrada_en_curso
            self._entrada_en_curso = entrada
            invertir = accion == "correr" and entrada[0] > 0
            if self._salir_hacia is not None:
                salida = next((s for s in estado.salidas if s.destino == self._salir_hacia), None)
                if salida is not None:
                    invertir = punto_puerta(salida.direccion, ancho, alto)[0] < px
            self._actor(sprite, entrada=accion == "correr" and self._salir_hacia is None,
                        golpe=anterior is not None and estado.vida < anterior.vida,
                        desplazamiento=entrada, carrera=accion == "correr", ataque=accion == "atacar")
            if self.animacion is not None:
                if accion == "beber":
                    usado = getattr(self.vista, "_objeto_usado", None)
                    bebida = recursos.pose_beber(altura_jugador, armadura,
                        antidoto=getattr(usado, "clase", "") == "antidoto", antorcha=antorcha)
                    if bebida is not None:
                        self.imagenes.append(bebida)
                        self.animacion.secuencia(sprite, (imagen, bebida, bebida, imagen),
                                                reposo=imagen, pasos_por_cuadro=8, duracion=32)
                elif accion:
                    cuadros = self.vista.recursos.fotogramas_jugador(290, altura_jugador,
                        invertir=invertir, armadura=armadura, arma=arma if arma_integrada else None,
                        antorcha=antorcha)
                    self.imagenes.extend(cuadros)
                    indices = {"correr": (0, 1, 2, 3), "atacar": (4, 5), "caer": (6, 7)}[accion]
                    if len(cuadros) == 8:
                        self.animacion.secuencia(sprite, [cuadros[i] for i in indices],
                                                reposo=imagen, mantener=accion == "caer",
                                                pasos_por_cuadro=2 if accion == "correr" else 6,
                                                duracion=PASOS_CARRERA if accion == "correr" else 18,
                                                repetir=accion == "correr")
                    if accion == "correr":
                        for i in range(4):
                            polvo = c.create_line(px - 35 + i * 10, py + 3,
                                                  px - 29 + i * 10, py + 3,
                                                  fill=TENUE, width=2, tags=("efecto_visual",))
                            self.animacion.particula(polvo, duracion=18 + i * 3,
                                                     desplazamiento=(-16 - i * 4, -5 - i))
                    elif accion == "atacar":
                        golpe = c.create_line(px + 45, py - 100, px + 75, py - 125,
                                              px + 95, py - 105, smooth=True,
                                              fill=AMARILLO, width=3, tags=("efecto_visual",))
                        self.animacion.particula(golpe, duracion=14, desplazamiento=(16, 0))
            elegidos = [cuadros[i] for i in indices] if len(cuadros) == 8 else ()
            dibujar_equipo(self, estado, sprite, imagen, elegidos, accion, self._objeto_recogido,
                            invertir=invertir, armadura_integrada=vestido is not None,
                            arma_integrada=arma_integrada)
        else:
            c.create_oval(px - 22, py - 90, px + 22, py - 46, fill=AMARILLO, outline=TEXTO, tags=("jugador",))
            c.create_polygon(px - 38, py - 42, px + 38, py - 42, px + 25, py, px - 25, py,
                             fill="#537c67", outline=TEXTO, tags=("jugador",))
        etiqueta = c.create_text(px, py + 15, text=f"Jugador  {estado.vida}/{estado.vida_max}",
                      fill=self.vista._color_vida(estado.vida, estado.vida_max), font=("Segoe UI", 11, "bold"))
        if imagen is not None and self.animacion is not None and self._accion_en_curso == "correr":
            self.animacion.anclar(sombra, sprite, (-54, -12, 54, 8))
            self.animacion.anclar(etiqueta, sprite, (0, 15))

    def _accion_jugador(self, estado):
        if estado.vida <= 0:
            return "caer"
        anterior = self.anterior
        accion = getattr(self.vista, "_accion_visual", None)
        if accion in ("cargar", "retroceso"):
            return None
        if self._salir_hacia is not None:
            return "correr"
        if anterior is None or getattr(estado, "reloj", 0) < getattr(anterior, "reloj", 0):
            return None
        if anterior.sala_id != estado.sala_id:
            return "correr"
        if accion == "atacar":
            return "atacar"
        if accion == "usar" and getattr(getattr(self.vista, "_objeto_usado", None), "clase", "") in ("pocion", "antidoto"):
            return "beber"
        return None

    def _enemigos(self, estado, ancho, alto, c):
        v = self.vista
        visibles = estado.enemigos[v._pagina_enemigos * 8:v._pagina_enemigos * 8 + 8]
        columnas = min(4, max(1, len(visibles)))
        celda = (ancho - 390) / columnas
        for i, enemigo in enumerate(visibles):
            fila, col = divmod(i, columnas)
            x = 280 + celda * (col + .5)
            y = 132 + (alto - 350) * .39 + fila * (78 + (alto - 350) * .35) if len(visibles) > 4 else alto - 150
            etiqueta = f"enemigo_{i}"
            altura = min(144, (alto - 140) / 1.6) if len(visibles) <= 4 else min(75, 8 + (alto - 350) * .35)
            rata = getattr(enemigo, "tipo", "") == "ent_rata_gigante"
            if rata:
                altura *= .54
            imagen = self._imagen(getattr(enemigo, "tipo", ""), min(145 if rata else 205, celda - 16), altura)
            sombra = min(celda * .32, imagen.width() * .35 if imagen is not None else altura * .35)
            c.create_oval(x - sombra, y - 6, x + sombra, y + 6, fill="#211a13", outline="", tags=(etiqueta,))
            if imagen is not None:
                sprite = c.create_image(x, y, image=imagen, anchor="s", tags=(etiqueta,))
                previo = next((e for e in self.anterior.enemigos if e.instancia == enemigo.instancia), None) if self.anterior else None
                self._actor(sprite, fase=i * .8, golpe=previo is not None and enemigo.vida < previo.vida)
            else:
                radio = min(30, celda / 3)
                c.create_polygon(x - radio, y - 5, x - radio * .8, y - altura * .8,
                                 x, y - altura, x + radio * .8, y - altura * .8, x + radio, y - 5,
                                 fill="#53675d", outline=ROJO, width=2, tags=(etiqueta,))
                r = min(12, altura * .15)
                c.create_oval(x - r, y - altura * .7 - r, x + r, y - altura * .7 + r,
                              fill="#c4cbb8", outline="", tags=(etiqueta,))
            c.create_text(x, y + 15, text=enemigo.nombre, fill=TEXTO, width=celda - 8,
                          font=("Segoe UI", 10, "bold"), tags=(etiqueta,))
            w = min(130, celda - 18)
            c.create_rectangle(x - w / 2, y + 35, x + w / 2, y + 43, fill=FONDO, outline="", tags=(etiqueta,))
            c.create_rectangle(x - w / 2, y + 35, x - w / 2 + w * max(0, enemigo.vida) / max(1, enemigo.vida_max), y + 43,
                               fill=v._color_vida(enemigo.vida, enemigo.vida_max), outline="", tags=(etiqueta,))
            texto = f"{enemigo.vida}/{enemigo.vida_max}"
            if celda >= 140:
                texto += f"  |  Atacar {v._costo('atacar')}"
            c.create_text(x, y + 57, text=texto,
                          fill=TENUE, font=("Segoe UI", 9), tags=(etiqueta,))
            v._ligar(etiqueta, f"atacar {enemigo.instancia}")
            detalle = (f"{enemigo.nombre} | Ataque {getattr(enemigo, 'ataque', 0)} | "
                       f"Defensa {getattr(enemigo, 'defensa', 0)} | Velocidad {getattr(enemigo, 'velocidad', 100)}"
                       f" | Atacar {v._costo('atacar')} u.t.")
            c.tag_bind(etiqueta, "<Enter>", lambda _e, t=detalle: v.mostrar_info(t), add="+")
        v._dibujar_paginacion("enemigos", len(estado.enemigos), 85, 18)

    def _objetos(self, estado, ancho, alto, c):
        v = self.vista
        objetos = estado.objetos_suelo[v._pagina_objetos * 8:v._pagina_objetos * 8 + 8]
        c.create_line(12, alto - 82, ancho - 12, alto - 82, fill=BORDE)
        if not objetos:
            c.create_text(24, alto - 45, text="Sin objetos en el suelo", fill=TENUE, anchor="w", font=("Segoe UI", 10))
        for i, objeto in enumerate(objetos):
            fila, col = divmod(i, 4)
            w = (ancho - 40) / 4
            x, y = 20 + col * w, alto - 76 + fila * 35
            etiqueta = f"objeto_{i}"
            c.create_rectangle(x + 2, y, x + w - 4, y + 30, fill="#30382a", outline="#77734e", tags=(etiqueta,))
            imagen = self._imagen(getattr(objeto, "tipo", ""), 26, 26)
            margen = 34 if imagen is not None else 8
            if imagen is not None:
                sprite = c.create_image(x + 18, y + 15, image=imagen, tags=(etiqueta,))
                self._actor(sprite, fase=i * .7)
            c.create_text(x + margen + (w - margen - 8) / 2, y + 15,
                          text=objeto.nombre, fill=AMARILLO, width=w - margen - 8,
                          font=("Segoe UI", 10), tags=(etiqueta,))
            v._ligar(etiqueta, f"recoger {objeto.instancia}")
            detalle = f"{objeto.nombre} | {getattr(objeto, 'detalle', '')} | Recoger {v._costo('recoger')} u.t."
            c.tag_bind(etiqueta, "<Enter>", lambda _e, t=detalle: v.mostrar_info(t), add="+")
        v._dibujar_paginacion("objetos", len(estado.objetos_suelo), ancho - 290, 18)
