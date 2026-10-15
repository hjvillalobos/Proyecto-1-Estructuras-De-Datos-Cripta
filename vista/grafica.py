
import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from vista.recursos_graficos import RecursosGraficos
from vista.escena import EscenaCripta
from vista.transicion_salas import TransicionSalas

from vista.tema import FONDO, PANEL, SALA, TEXTO, TENUE, VERDE, ROJO, AMARILLO, AZUL, NARANJA, MORADO, PIEDRA, BORDE

NOMBRES_DIR = {"N": "Norte", "S": "Sur", "E": "Este", "O": "Oeste"}

AYUDA_GRAFICA = """\
RATÓN
  Clic en una puerta ........ moverte (si está cerrada, intenta abrirla)
  Clic en un enemigo ........ atacarlo
  Clic en un objeto amarillo . recogerlo del suelo
  Doble clic en el inventario  equipar (armas/armaduras) o usar

TECLADO
  W / ↑  norte      S / ↓  sur      D / →  este      A / ←  oeste
  Espacio  esperar        R  usar pergamino de retroceso

BOTONES
  Usar / Equipar / Soltar actúan sobre el objeto seleccionado
  en el inventario. El selector ordena la vista sin cambiar el
  orden real del inventario.

REPLAY
  El botón «Replay» abre un archivo de bitácora (.log) y lo reproduce
  paso a paso en otra ventana, con Pausa, Detener y selector de velocidad.
"""


class VistaGrafica:
    ANCHO = 900
    ALTO = 500

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚔  CRIPTA  ⚔")
        self.root.configure(bg=FONDO)
        self.root.geometry("1280x850")
        self.root.minsize(1100, 760)
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        self._cola = []                 # comandos pendientes de entregar al controlador
        self._cerrada = False
        self._refrescar_inv = True      # pedir "inv" antes de esperar al jugador
        self._ayuda_omitida = False     # el controlador pide ayuda al arrancar: no abrir ventana
        self._items = []                # ítems del inventario que se ven en la lista
        self._en_replay = False         # True en la ventana que reproduce un replay
        self._replay_pausado = False
        self._replay_detener = False

        self.recursos = RecursosGraficos(self.root)
        self.escena = EscenaCripta(self)
        self.transicion_salas = TransicionSalas(self)
        self._estado = None
        self._animaciones = []
        self._movimiento_activo = True
        self._ultimo_clic = ("", 0)
        self._construir()
        self._atar_teclas()

    # ------------------------------------------------------------------
    # Construcción de la ventana
    # ------------------------------------------------------------------
    def _etiqueta(self, padre, texto=None, variable=None, color=TEXTO, tamano=11, fuente="Segoe UI", **opciones):
        return tk.Label(padre, text=texto, textvariable=variable, bg=FONDO, fg=color,
                        font=(fuente, tamano), anchor="w", **opciones)

    def _construir(self):
        estilo = ttk.Style(self.root)
        estilo.theme_use("clam")
        estilo.configure("TButton", background=PANEL, foreground=TEXTO, bordercolor=BORDE,
                         padding=(10, 8), font=("Segoe UI", 10))
        estilo.map("TButton", background=[("active", "#31433b"), ("disabled", "#182020")],
                   foreground=[("disabled", "#82918a")])
        estilo.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=TEXTO,
                         arrowcolor=TEXTO, bordercolor=BORDE)
        estilo.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXTO)])
        self.root.option_add("*TCombobox*Listbox.background", PANEL)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXTO)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        cabecera = tk.Frame(self.root, bg=FONDO)
        cabecera.grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(14, 8))
        self._etiqueta(cabecera, "CRIPTA", color=AMARILLO, tamano=24, fuente="Georgia").pack(side="left", padx=(0, 30))
        for texto, comando in (("Guardar", "guardar"), ("Cargar", "cargar"), ("Replay", "replay"),
                               ("Puntajes", "puntajes"), ("Ayuda", "ayuda"), ("Salir", "salir")):
            ttk.Button(cabecera, text=texto, command=lambda c=comando: self._enviar(c)).pack(side="left", padx=3)
        izq = tk.Frame(self.root, bg=FONDO)
        izq.grid(row=1, column=0, sticky="nsew", padx=(22, 12), pady=(0, 16))
        der = tk.Frame(self.root, bg=FONDO, width=320)
        der.grid(row=1, column=1, sticky="ns", padx=(8, 22), pady=(0, 16))
        self.var_sala = tk.StringVar()
        self._etiqueta(izq, variable=self.var_sala, tamano=18, fuente="Georgia").pack(fill="x", pady=(0, 10))
        self.canvas = tk.Canvas(izq, width=self.ANCHO, height=350, bg=FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._redimensionar)
        self.var_aviso = tk.StringVar()
        self.lbl_aviso = self._etiqueta(izq, variable=self.var_aviso, color=AMARILLO,
                                        wraplength=700, justify="left", height=2)
        self.lbl_aviso.pack(fill="x", pady=4)
        self.barra_botones = tk.Frame(izq, bg=FONDO)
        self.barra_botones.pack(fill="x", pady=(0, 10))
        self.boton_esperar = ttk.Button(self.barra_botones, text="Esperar", command=lambda: self._enviar("esperar"))
        self.boton_esperar.pack(side="left", padx=(0, 8))
        ttk.Button(self.barra_botones, text="Retroceso", command=lambda: self._enviar("retroceso")).pack(side="left")
        self.var_tiempo = tk.StringVar()
        self.lbl_tiempo = self._etiqueta(izq, variable=self.var_tiempo, color=TENUE, fuente="Consolas")
        self.lbl_tiempo.pack(anchor="e")
        self.barra_replay = tk.Frame(izq, bg=FONDO)
        self.var_movimiento = tk.BooleanVar(value=True)
        ttk.Checkbutton(izq, text="Animaciones", variable=self.var_movimiento,
                        command=self._alternar_movimiento).pack(anchor="e")
        ttk.Button(self.barra_replay, text="Pausa / Continuar", command=self._replay_alternar_pausa).pack(side="left")
        ttk.Button(self.barra_replay, text="Detener", command=self._replay_parar).pack(side="left", padx=8)
        self.var_vel = tk.StringVar(value="normal")
        ttk.Combobox(self.barra_replay, textvariable=self.var_vel, state="readonly", width=9,
                     values=("lento", "normal", "rápido")).pack(side="left")
        self._etiqueta(izq, "Registro de la partida", color=TENUE).pack(fill="x")
        caja_log = tk.Frame(izq, bg=FONDO)
        caja_log.pack(fill="x", pady=(6, 0))
        self.log = tk.Text(caja_log, height=4, bg=PANEL, fg=TEXTO, relief="flat", wrap="word",
                           state="disabled", font=("Segoe UI", 10), padx=12, pady=8)
        self.log.pack(side="left", fill="both", expand=True)
        scroll_log = ttk.Scrollbar(caja_log, command=self.log.yview)
        scroll_log.pack(side="right", fill="y")
        self.log.configure(yscrollcommand=scroll_log.set)
        self._etiqueta(der, "Jugador", tamano=18, fuente="Georgia").pack(fill="x")
        self.barra = tk.Canvas(der, width=320, height=30, bg=FONDO, highlightthickness=0)
        self.barra.pack(pady=(10, 6))
        self.var_stats, self.var_efectos = tk.StringVar(), tk.StringVar()
        self._etiqueta(der, variable=self.var_stats, color=AZUL).pack(fill="x")
        self._etiqueta(der, variable=self.var_efectos, color=MORADO, wraplength=320, height=2).pack(fill="x")
        ttk.Separator(der).pack(fill="x", pady=12)
        self._etiqueta(der, "Proximos sucesos", tamano=14, fuente="Georgia").pack(fill="x")
        self.var_agenda = tk.StringVar()
        self._etiqueta(der, variable=self.var_agenda, color=TENUE, justify="left",
                       wraplength=320, height=4).pack(fill="x", pady=(6, 0))
        ttk.Separator(der).pack(fill="x", pady=12)
        self.var_inv = tk.StringVar()
        self._etiqueta(der, variable=self.var_inv, tamano=14, fuente="Georgia").pack(fill="x")
        caja_lista = tk.Frame(der, bg=FONDO)
        caja_lista.pack(fill="x", pady=(10, 8))
        self.lista = tk.Listbox(caja_lista, width=34, height=5, bg=PANEL, fg=TEXTO,
                               selectbackground="#35584e", selectforeground=TEXTO,
                               activestyle="none", relief="flat", exportselection=False,
                               highlightthickness=1, highlightbackground=BORDE, font=("Segoe UI", 11))
        self.lista.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(caja_lista, command=self.lista.yview)
        scroll.pack(side="right", fill="y")
        self.lista.configure(yscrollcommand=scroll.set)
        self.lista.bind("<Double-Button-1>", self._doble_clic_inventario)
        self.lista.bind("<<ListboxSelect>>", self._seleccionar_inventario)
        self.var_detalle = tk.StringVar(value="Inventario vacio")
        detalle = tk.Frame(der, bg=FONDO)
        detalle.pack(fill="x")
        miniatura = tk.Frame(detalle, bg=FONDO, width=56, height=56)
        miniatura.pack(side="left", padx=(0, 6))
        miniatura.pack_propagate(False)
        self.icono_detalle = tk.Label(miniatura, bg=FONDO)
        self.icono_detalle.pack(fill="both", expand=True)
        self._etiqueta(detalle, variable=self.var_detalle, wraplength=255, justify="left",
                       color=TENUE, height=3).pack(side="left", fill="x", expand=True)
        acciones = tk.Frame(der, bg=FONDO)
        acciones.pack(fill="x", pady=8)
        self._botones_inventario = []
        for verbo in ("usar", "equipar", "soltar"):
            boton = ttk.Button(acciones, text=verbo.capitalize(),
                               command=lambda v=verbo: self._accion_inventario(v))
            boton.pack(side="left", fill="x", expand=True, padx=2)
            self._botones_inventario.append((verbo, boton))
        orden = tk.Frame(der, bg=FONDO)
        orden.pack(fill="x", pady=(5, 0))
        self.var_orden = tk.StringVar(value="orden real")
        self.combo = ttk.Combobox(orden, textvariable=self.var_orden, state="readonly", width=13,
                                  values=("orden real", "peso", "valor", "nombre"))
        self.combo.pack(side="left")
        self.combo.bind("<<ComboboxSelected>>", self._cambio_orden)
        self.var_desc = tk.IntVar(value=0)
        tk.Checkbutton(orden, text="Descendente", variable=self.var_desc, bg=FONDO, fg=TEXTO,
                       selectcolor=PANEL, activebackground=FONDO, activeforeground=TEXTO,
                       command=self._cambio_orden).pack(side="left", padx=8)
        self._mostrar_detalle()

    def _costo(self, verbo):
        estado = getattr(self, "_estado", None)
        for nombre, valor in getattr(estado, "costos", []):
            if nombre == verbo:
                return valor
        return 0

    def _mostrar_detalle(self, _evento=None):
        if not hasattr(self, "var_detalle"):
            return
        item = self._instancia_seleccionada()
        if hasattr(self, "icono_detalle"):
            self._imagen_detalle = self.recursos.imagen(item.tipo, 52, 52) if item else None
            self.icono_detalle.config(image=self._imagen_detalle or "")
        self.var_detalle.set("Inventario vacio" if item is None else
            f"{item.nombre}\n{item.detalle or item.clase.capitalize()}\nPeso {item.peso}  |  Valor {item.valor}")
        for verbo, boton in self._botones_inventario:
            permitido = item is not None and (verbo == "soltar" or
                (verbo == "equipar" and item.clase in ("arma", "armadura")) or
                (verbo == "usar" and item.clase not in ("arma", "armadura", "llave")))
            costo = 0 if item and item.clase == "pergamino_retroceso" and verbo == "usar" else self._costo(verbo)
            boton.config(text=f"{verbo.capitalize()} {costo}", state="normal" if permitido else "disabled")

    def _redimensionar(self, _evento=None):
        if getattr(self, "_estado", None) is not None and not self._cerrada:
            transicion = getattr(self, "transicion_salas", None)
            if transicion is not None and transicion.activa:
                transicion.redibujar()
            else:
                self._dibujar_sala(self._estado)
        if hasattr(self, "lbl_aviso"):
            self.lbl_aviso.config(wraplength=max(400, self.canvas.winfo_width() - 16))

    def _alternar_movimiento(self):
        self._movimiento_activo = self.var_movimiento.get()
        if not self._movimiento_activo:
            self._cancelar_dano()
        if hasattr(self, "escena"):
            self.escena.detener()
        if self._estado is not None:
            self._dibujar_sala(self._estado)

    def preparar_animacion(self, accion):
        self._accion_visual = accion

    def _clic_accion(self, comando):
        if getattr(self, "transicion_salas", None) is not None and self.transicion_salas.activa:
            return
        anterior, instante = getattr(self, "_ultimo_clic", ("", 0))
        ahora = time.monotonic()
        if comando == anterior and ahora - instante < .25:
            return
        self._ultimo_clic = (comando, ahora)
        self._enviar(comando)

    def _atar_teclas(self):
        mapa = (("Up", "mover N"), ("w", "mover N"), ("Down", "mover S"), ("s", "mover S"),
                ("Right", "mover E"), ("d", "mover E"), ("Left", "mover O"), ("a", "mover O"),
                ("space", "esperar"), ("r", "retroceso"))
        for tecla, comando in mapa:
            self.root.bind(f"<{tecla}>",
                           lambda ev, c=comando, t=tecla: self._tecla(c, t))

    def _tecla(self, comando, tecla):
        foco = self.root.focus_get()
        if isinstance(foco, ttk.Combobox):
            return
        if isinstance(foco, tk.Listbox) and tecla in ("Up", "Down"):
            return                      # las flechas recorren la lista, no mueven al jugador
        self._enviar(comando)

    # ------------------------------------------------------------------
    # Entrada
    # ------------------------------------------------------------------
    def _enviar(self, comando):
        if self._cerrada or getattr(self, "_en_menu", False):
            return
        if self._en_replay:
            if comando == "salir":
                self._replay_detener = True
                self.cerrar()
            return
        self._cola.append(comando)

    def mostrar_menu(self, replay, puntajes):
        from vista.menu_inicio import MenuInicio
        return MenuInicio(self, replay, puntajes).mostrar()

    def _actualizar_ui(self):
        try:
            self.root.update()
        except tk.TclError:             # la ventana se cerró
            self._cerrada = True

    def _cmd_inventario(self):
        criterio = self.var_orden.get()
        if criterio == "orden real":
            return "inv"
        return f"inv orden {criterio}" + (" desc" if self.var_desc.get() else "")

    def pedir_comando(self):
        if self._cerrada:
            return None
        if self._refrescar_inv:
            self._refrescar_inv = False
            return self._cmd_inventario()
        self._actualizar_ui()
        while not self._cola and not self._cerrada:
            self._actualizar_ui()
            time.sleep(0.015)
        if self._cerrada:
            return None
        self._refrescar_inv = True
        return self._cola.pop(0)

    def pedir_texto(self, pregunta):
        return (simpledialog.askstring("CRIPTA", pregunta, parent=self.root) or "").strip()

    def elegir_cripta(self, criptas):
        from vista.selector_cripta import SelectorCripta
        return SelectorCripta(self, criptas).mostrar()

    # ------------------------------------------------------------------
    # Inventario (lado derecho)
    # ------------------------------------------------------------------
    def _instancia_seleccionada(self):
        seleccion = self.lista.curselection()
        if not seleccion or seleccion[0] >= len(self._items):
            return None
        return self._items[seleccion[0]]

    def _seleccionar_inventario(self, _evento=None):
        self._mostrar_detalle()
        item = self._instancia_seleccionada()
        if item is not None:
            self._enviar(f"seleccionar {item.instancia}")

    def _accion_inventario(self, verbo):
        item = self._instancia_seleccionada()
        if item is None:
            self.mostrar_error("Selecciona primero un objeto del inventario.")
            return
        self._enviar(f"{verbo} {item.instancia}")
        self.root.focus_set()

    def _doble_clic_inventario(self, _evento=None):
        item = self._instancia_seleccionada()
        if item is None:
            return
        if item.clase in ("arma", "armadura"):
            self._enviar(f"equipar {item.instancia}")
        elif item.clase != "llave":
            self._enviar(f"usar {item.instancia}")

    def _cambio_orden(self, _evento=None):
        self._enviar(self._cmd_inventario())
        self.root.focus_set()

    def mostrar_inventario(self, items, orden=None, cursor=None):
        if self._cerrada:
            return
        previo = self._instancia_seleccionada()
        self._items = list(items)
        self.lista.delete(0, "end")
        reseleccion = None
        for i, it in enumerate(self._items):
            self.lista.insert("end", f"{'[E] ' if it.equipado else '    '}{it.nombre}")
            if it.equipado:
                self.lista.itemconfig(i, foreground=AMARILLO)
            if previo is not None and it.instancia == previo.instancia:
                reseleccion = i
        if reseleccion is None and self._items:
            reseleccion = next((i for i, it in enumerate(self._items) if it.instancia == cursor), 0)
        if reseleccion is not None:
            self.lista.selection_set(reseleccion)
        self._mostrar_detalle()

    def mostrar_item(self, item):
        if item is None:
            self.mostrar_info("El inventario está vacío.")
        else:
            self.mostrar_info(f"Viendo: {item.nombre} ({item.clase}, peso {item.peso}, "
                              f"valor {item.valor})")

    # ------------------------------------------------------------------
    # Salida: sala, estadísticas y mensajes
    # ------------------------------------------------------------------
    def mostrar_estado(self, e, mensajes):
        if self._cerrada:
            return
        anterior = self._estado
        self._estado = e
        if e != anterior or getattr(self, "_accion_visual", None) in ("cargar", "retroceso"):
            recorrido = (anterior is not None and anterior.sala_id != e.sala_id
                         and getattr(self, "_accion_visual", None) == "mover"
                         and self.transicion_salas.mostrar(anterior, e))
            if not recorrido:
                self._dibujar_sala(e)
        self._actualizar_stats(e)
        self._actualizar_log(mensajes)
        self._mostrar_detalle()
        if anterior and e.reloj >= anterior.reloj and e.vida != anterior.vida:
            self._animar_vida(e.vida - anterior.vida)
        self.root.update_idletasks()

    def _ligar(self, etiqueta, comando):
        c = self.canvas
        c.tag_bind(etiqueta, "<Button-1>", lambda _ev, cmd=comando: self._clic_accion(cmd))
        c.tag_bind(etiqueta, "<Enter>", lambda _ev: c.config(cursor="hand2"))
        c.tag_bind(etiqueta, "<Leave>", lambda _ev: c.config(cursor=""))

    @staticmethod
    def _color_vida(vida, vida_max):
        fraccion = vida / max(1, vida_max)
        if fraccion > 0.5:
            return VERDE
        return AMARILLO if fraccion > 0.25 else ROJO

    def _dibujar_sala(self, e, salir_hacia=None):
        transicion = getattr(self, "transicion_salas", None)
        if transicion is not None and salir_hacia is None:
            transicion.cancelar()
        anterior = getattr(self, "_estado_sala", None)
        if anterior is None or anterior.sala_id != e.sala_id:
            self._pagina_enemigos = self._pagina_objetos = 0
        self._estado_sala = e
        self._pagina_enemigos = min(self._pagina_enemigos, max(0, (len(e.enemigos) - 1) // 8))
        self._pagina_objetos = min(self._pagina_objetos, max(0, (len(e.objetos_suelo) - 1) // 8))
        if not hasattr(self, "escena"):
            self.escena = EscenaCripta(self)
        self.escena.dibujar(e, salir_hacia=salir_hacia)

    def _cambiar_pagina(self, tipo, avance):
        if getattr(self, "transicion_salas", None) is not None and self.transicion_salas.activa:
            return
        atributo = f"_pagina_{tipo}"
        setattr(self, atributo, max(0, getattr(self, atributo) + avance))
        self._dibujar_sala(self._estado_sala)

    def _dibujar_paginacion(self, tipo, cantidad, x, y):
        if cantidad <= 8:
            return
        pagina = getattr(self, f"_pagina_{tipo}")
        paginas = (cantidad + 7) // 8
        self.canvas.create_text(x + 105, y, text=f"{tipo.capitalize()} {pagina + 1}/{paginas}",
                                fill=TEXTO, font=("Segoe UI", 9))
        for avance, dx, simbolo in ((-1, 0, "←"), (1, 210, "→")):
            etiqueta = f"pagina_{tipo}_{avance}"
            habilitado = 0 <= pagina + avance < paginas
            self.canvas.create_rectangle(x + dx - 14, y - 13, x + dx + 14, y + 13,
                                         fill=PANEL, outline=BORDE, tags=(etiqueta,))
            self.canvas.create_text(x + dx, y, text=simbolo, fill=TEXTO if habilitado else TENUE,
                                    font=("Segoe UI", 12), tags=(etiqueta,))
            if habilitado:
                self.canvas.tag_bind(etiqueta, "<Button-1>",
                                     lambda _e, t=tipo, a=avance: self._cambiar_pagina(t, a))

    def _actualizar_stats(self, e):
        self.var_sala.set(f"Sala {e.sala_id}  |  {e.sala_nombre}")
        self.var_tiempo.set(f"Tu decision: t={e.reloj}")
        self.var_stats.set(f"Ataque {e.ataque}   Defensa {e.defensa}   Velocidad {e.velocidad}")
        self.var_inv.set(f"Inventario   {e.inventario_usado}/{e.inventario_max}")
        self.var_efectos.set("Efectos: " + (", ".join(e.efectos) if e.efectos else "ninguno"))
        self.var_agenda.set("\n".join(f"t={ev.tiempo}  {ev.nombre}" for ev in e.agenda) or "Sin sucesos pendientes")
        self.boton_esperar.config(text=f"Esperar  {self._costo('esperar')} u.t.")
        b = self.barra
        b.delete("all")
        b.create_rectangle(0, 0, 320, 30, fill=PANEL, outline=BORDE)
        b.create_rectangle(2, 2, 2 + 316 * max(0, e.vida) / max(1, e.vida_max), 28,
                           fill=self._color_vida(e.vida, e.vida_max), outline="")
        b.create_rectangle(99, 5, 221, 25, fill=FONDO, outline="")
        b.create_text(160, 15, text=f"Vida {e.vida} / {e.vida_max}", fill=TEXTO, font=("Segoe UI", 11, "bold"))

    def _animar_vida(self, diferencia):
        self._cancelar_dano()
        if not getattr(self, "_movimiento_activo", True):
            return
        x, y = self._jugador_xy
        texto = self.canvas.create_text(x, y - 145, text=f"{diferencia:+d}",
            fill=ROJO if diferencia < 0 else VERDE, font=("Segoe UI", 25, "bold"), tags=("dano_flotante",))
        for paso in range(1, 7):
            self._animaciones.append(self.root.after(paso * 70, lambda t=texto: self.canvas.move(t, 0, -4)))
        self._animaciones.append(self.root.after(650, lambda: self.canvas.delete(texto)))

    def _cancelar_dano(self):
        for identificador in self._animaciones:
            self.root.after_cancel(identificador)
        self._animaciones.clear()
        self.canvas.delete("dano_flotante")

    def _actualizar_log(self, mensajes):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.tag_configure("dano", foreground=ROJO)
        self.log.tag_configure("bien", foreground=VERDE)
        self.log.tag_configure("normal", foreground=TEXTO)
        for m in mensajes[-20:]:
            ml = m.lower()
            if any(p in ml for p in ("muere", "derrota", "daño", "dano", "veneno", "trampa", "herido")):
                tag = "dano"
            elif any(p in ml for p in ("recoge", "cura", "victoria", "abre", "equipa")):
                tag = "bien"
            else:
                tag = "normal"
            self.log.insert("end", f"▸ {m}\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    # ------------------------------------------------------------------
    # Avisos y ventanas
    # ------------------------------------------------------------------
    def _aviso(self, texto, color):
        if self._cerrada:
            return
        self.var_aviso.set(texto)
        self.lbl_aviso.config(fg=color)

    def mostrar_error(self, texto):
        self._aviso(f"(!) {texto}", ROJO)

    def mostrar_error_replay(self, texto):
        if not self._cerrada:
            messagebox.showerror("Error de replay", texto, parent=self.root)

    def preguntar_reinicio(self):
        return not self._cerrada and messagebox.askyesno(
            "Jugar de nuevo", "Has perdido. ¿Quieres iniciar una partida nueva?", parent=self.root)

    def reiniciar_presentacion(self):
        self._accion_visual = None
        if hasattr(self, "escena"):
            self.escena.detener()
            self.escena.anterior = None
        for identificador in self._animaciones:
            self.root.after_cancel(identificador)
        self._animaciones.clear()
        self._cola.clear()
        self._estado = self._estado_sala = None
        self._pagina_enemigos = self._pagina_objetos = 0
        self._refrescar_inv = True
        self._ultimo_clic = ("", 0)
        self.mostrar_inventario([])
        self._aviso("Nueva partida.", AMARILLO)

    def mostrar_info(self, texto):
        self._aviso(texto, AMARILLO)

    def mostrar_ayuda(self):
        if self._cerrada:
            return
        if not self._ayuda_omitida:                 # llamada automática al iniciar
            self._ayuda_omitida = True
            self._aviso("Clic en una puerta para moverte, en un enemigo para atacar, en un "
                        "objeto amarillo para recogerlo. Botón «Ayuda» para ver los controles.",
                        AMARILLO)
            return
        messagebox.showinfo("Ayuda", AYUDA_GRAFICA, parent=self.root)

    def mostrar_puntajes(self, registros):
        if self._cerrada:
            return
        if not registros:
            texto = "(aún no hay partidas registradas)"
        else:
            texto = "\n".join(
                f"{n:>2}. {r.nombre:<14} {r.resultado:<9} tiempo {r.tiempo_final:<6} "
                f"acciones {r.acciones:<4} derrotados {r.derrotados}"
                for n, r in enumerate(registros, start=1))
        messagebox.showinfo("Tabla de puntajes", texto, parent=self.root)

    def mostrar_fin(self, resumen):
        if self._cerrada:
            return
        if resumen.resultado == "victoria":
            titulo, cabecera = "¡Victoria!", "Has escapado de la cripta."
        elif resumen.resultado == "derrota":
            titulo, cabecera = "Derrota", "Has muerto en la cripta."
        else:
            titulo, cabecera = "Fin", "Sesión terminada."
        messagebox.showinfo(
            titulo,
            f"{cabecera}\n\nAcciones: {resumen.acciones}\n"
            f"Enemigos derrotados: {resumen.derrotados}\n"
            f"Tiempo virtual: {resumen.reloj_final}",
            parent=self.root)

    def mostrar_estadisticas_red(self, est):
        self.mostrar_info(f"Red: {est.solicitudes}/{est.presupuesto} solicitudes | "
                          f"caché: {est.aciertos_cache} aciertos, {est.fallos_cache} fallos")

    # ------------------------------------------------------------------
    # Replay
    # ------------------------------------------------------------------
    def pedir_ruta_replay(self):
        """Abre el selector de archivos. Devuelve la ruta o None si se cancela."""
        ruta = filedialog.askopenfilename(
            parent=self.root, title="Elige un archivo de replay",
            initialdir="datos_generados",
            filetypes=[("Bitácora de partida", "*.log"), ("Todos los archivos", "*.*")])
        return ruta or None

    def modo_replay(self):
        """Esta ventana pasa a reproducir: se ocultan los botones de juego."""
        self._en_replay = True
        self._replay_pausado = False
        self._replay_detener = False
        self.barra_botones.pack_forget()
        self.barra_replay.pack(fill="x")
        self.root.title("REPLAY — CRIPTA")

    def _replay_alternar_pausa(self):
        self._replay_pausado = not self._replay_pausado
        self._aviso("REPLAY en pausa." if self._replay_pausado else "REPLAY continúa.", AZUL)

    def _replay_parar(self):
        self._replay_detener = True

    def _pausa_replay(self):
        velocidad = self.var_vel.get()
        if velocidad == "lento":
            return 1.4
        if velocidad == "rápido":
            return 0.2
        return 0.7

    def mostrar_replay_paso(self, estado, mensajes, paso, total, inventario=None):
        """Dibuja un paso del replay y espera. Devuelve False para detenerlo."""
        if self._cerrada or self._replay_detener:
            return False
        self.mostrar_estado(estado, mensajes)
        if inventario is not None:
            self.mostrar_inventario(inventario)
        self._aviso(f"REPLAY — paso {paso}/{total}", AZUL)
        fin = time.time() + self._pausa_replay()
        while not self._cerrada and not self._replay_detener:
            self._actualizar_ui()
            if not self._replay_pausado and time.time() >= fin:
                break
            time.sleep(0.01)
        return not self._cerrada and not self._replay_detener

    # ------------------------------------------------------------------
    # Cierre
    # ------------------------------------------------------------------
    def _al_cerrar(self):
        self.cerrar()

    def cerrar(self):
        if self._cerrada:
            return
        self._cerrada = True
        if hasattr(self, "escena"):
            self.escena.detener()
        try:
            for identificador in getattr(self, "_animaciones", []):
                self.root.after_cancel(identificador)
            self.root.destroy()
        except tk.TclError:
            pass
