from vista.tema import FONDO, PANEL, TEXTO, TENUE, VERDE, ROJO, AMARILLO, BORDE


class EscenaCripta:
    """Dibuja la sala a partir de datos de presentacion, sin ejecutar reglas."""

    def __init__(self, vista):
        self.vista = vista
        self.imagenes = []

    def _imagen(self, nombre, ancho, alto):
        recursos = getattr(self.vista, "recursos", None)
        imagen = recursos.imagen(nombre, int(ancho), int(alto)) if recursos else None
        if imagen is not None:
            self.imagenes.append(imagen)
        return imagen

    def dibujar(self, estado):
        v, c = self.vista, self.vista.canvas
        self.imagenes.clear()
        c.delete("all")
        ancho, alto = c.winfo_width(), c.winfo_height()
        ancho = max(700, ancho) if isinstance(ancho, int) else v.ANCHO
        alto = max(350, alto) if isinstance(alto, int) else v.ALTO
        c.create_rectangle(0, 0, ancho, alto, fill=FONDO, outline="")
        pared = ("#28372f", "#303431", "#293638")[estado.sala_id % 3]
        c.create_polygon(24, 58, ancho - 24, 58, ancho - 56, alto - 92, 56, alto - 92,
                         fill=pared, outline=BORDE, width=2)
        for fila in range(3):
            y = 62 + fila * 23
            c.create_line(25, y, ancho - 25, y, fill="#3e4c42")
            for x in range(40 + (fila % 2) * 35, ancho - 30, 70):
                c.create_line(x, y, x, y + 23, fill="#3e4c42")
        c.create_polygon(70, 130, ancho - 70, 130, ancho - 30, alto - 92, 30, alto - 92,
                         fill="#1c2825", outline="#3a4e40")
        for i in range(1, 6):
            x = 70 + (ancho - 140) * i / 6
            c.create_line(x, 130, ancho / 2 + (x - ancho / 2) * 1.5, alto - 92, fill="#304039")
        for fraccion in (.2, .45, .75):
            y = 130 + (alto - 222) * fraccion
            c.create_line(65, y, ancho - 65, y, fill="#304039")
        self._ambiente(estado.sala_nombre, ancho, c)
        self._puertas(estado, ancho, alto, c)
        trampas = getattr(estado, "trampas", [])
        if trampas:
            texto = "  |  ".join(f"{t.nombre}: {'armada' if t.armada else 'desarmada'} ({t.dano} dano)" for t in trampas)
            c.create_text(ancho / 2, 91, text=texto, width=ancho - 210,
                          fill=ROJO if any(t.armada for t in trampas) else TENUE, font=("Segoe UI", 10))
            color = ROJO if any(t.armada for t in trampas) else TENUE
            c.create_polygon(28, alto - 117, 48, alto - 125, 68, alto - 117, 48, alto - 108,
                             fill="#303e34", outline=color, width=2, tags=("trampa",))
            for x in (37, 47, 57):
                c.create_line(x, alto - 119, x + 5, alto - 113, fill=color, width=2, tags=("trampa",))
        self._jugador(estado, alto, c)
        self._enemigos(estado, ancho, alto, c)
        self._objetos(estado, ancho, alto, c)

    def _ambiente(self, nombre, ancho, c):
        nombre = nombre.lower()
        for x in (80, ancho - 80):
            if "urna" in nombre or "nicho" in nombre:
                c.create_oval(x - 17, 102, x + 17, 145, fill="#59665b", outline="#94a18d")
                c.create_rectangle(x - 13, 97, x + 13, 105, fill="#7b8879", outline="")
            elif "osario" in nombre or "cripta" in nombre:
                c.create_rectangle(x - 18, 98, x + 18, 145, fill="#435449", outline="#6a806d")
                c.create_oval(x - 9, 109, x + 9, 128, fill="#bcc4a5", outline="")
            else:
                c.create_rectangle(x - 13, 92, x + 13, 148, fill="#3a4b41", outline=BORDE)

    def _puertas(self, estado, ancho, alto, c):
        sur_x = 145 if len(estado.enemigos) > 4 else ancho / 2
        posiciones = (("N", ancho / 2, 40), ("S", sur_x, alto - 108),
                      ("O", 44, alto / 2), ("E", ancho - 44, alto / 2))
        nombres = (("N", "Norte"), ("S", "Sur"), ("O", "Oeste"), ("E", "Este"))
        for salida in estado.salidas:
            posicion = next((p for p in posiciones if p[0] == salida.direccion), None)
            if posicion is None:
                continue
            _, x, y = posicion
            etiqueta = "puerta_" + salida.direccion
            w, h = (98, 34) if salida.direccion in ("N", "S") else (72, 56)
            verbo = "abrir" if salida.cerrada else "mover"
            c.create_rectangle(x - w / 2, y - h / 2, x + w / 2, y + h / 2,
                               fill="#403925" if salida.cerrada else "#20392f",
                               outline=AMARILLO if salida.cerrada else VERDE, width=2, tags=(etiqueta,))
            nombre = next(n for d, n in nombres if d == salida.direccion)
            c.create_text(x, y, text=f"{nombre}\n{verbo.capitalize()} {self.vista._costo(verbo)}",
                          fill=TEXTO, font=("Segoe UI", 9), tags=(etiqueta,))
            self.vista._ligar(etiqueta, f"{verbo} {salida.direccion}")

    def _jugador(self, estado, alto, c):
        px, py = 145, alto - 150
        self.vista._jugador_xy = (px, py)
        c.create_oval(px - 68, py - 16, px + 68, py + 10, fill="#0b1512", outline="")
        imagen = self._imagen("jugador", 230, min(280, alto - 175))
        if imagen is not None:
            c.create_image(px, py, image=imagen, anchor="s", tags=("jugador",))
        else:
            c.create_oval(px - 22, py - 90, px + 22, py - 46, fill=AMARILLO, outline=TEXTO, tags=("jugador",))
            c.create_polygon(px - 38, py - 42, px + 38, py - 42, px + 25, py, px - 25, py,
                             fill="#537c67", outline=TEXTO, tags=("jugador",))
        c.create_text(px, py + 15, text=f"Jugador  {estado.vida}/{estado.vida_max}",
                      fill=self.vista._color_vida(estado.vida, estado.vida_max), font=("Segoe UI", 11, "bold"))

    def _enemigos(self, estado, ancho, alto, c):
        v = self.vista
        visibles = estado.enemigos[v._pagina_enemigos * 8:v._pagina_enemigos * 8 + 8]
        columnas = min(4, max(1, len(visibles)))
        celda = (ancho - 390) / columnas
        for i, enemigo in enumerate(visibles):
            fila, col = divmod(i, columnas)
            x = 280 + celda * (col + .5)
            y = 132 + (alto - 350) * .39 + fila * (78 + (alto - 350) * .35) if len(visibles) > 4 else alto / 2 + 10
            etiqueta = f"enemigo_{i}"
            c.create_oval(x - celda * .35, y - 8, x + celda * .35, y + 8, fill="#101a15", outline="", tags=(etiqueta,))
            altura = min(118, (alto - 190) / 2) if len(visibles) <= 4 else min(75, 8 + (alto - 350) * .35)
            imagen = self._imagen(getattr(enemigo, "tipo", ""), min(205, celda - 16), altura)
            if imagen is not None:
                c.create_image(x, y, image=imagen, anchor="s", tags=(etiqueta,))
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
                c.create_image(x + 18, y + 15, image=imagen, tags=(etiqueta,))
            c.create_text(x + margen + (w - margen - 8) / 2, y + 15,
                          text=objeto.nombre, fill=AMARILLO, width=w - margen - 8,
                          font=("Segoe UI", 10), tags=(etiqueta,))
            v._ligar(etiqueta, f"recoger {objeto.instancia}")
            detalle = f"{objeto.nombre} | {getattr(objeto, 'detalle', '')} | Recoger {v._costo('recoger')} u.t."
            c.tag_bind(etiqueta, "<Enter>", lambda _e, t=detalle: v.mostrar_info(t), add="+")
        v._dibujar_paginacion("objetos", len(estado.objetos_suelo), ancho - 290, 18)
