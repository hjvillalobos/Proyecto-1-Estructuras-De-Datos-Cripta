"""
Vista gráfica sencilla de CRIPTA con tkinter (viene incluido con Python).

Implementa la MISMA interfaz que VistaConsola (pedir_comando, mostrar_estado,
mostrar_inventario, ...), así que el controlador y el modelo no cambian.

Cómo conversa con el controlador:
  * Cada clic/tecla se convierte en un comando de texto ("mover N",
    "atacar e-201", "recoger obj-1-0", "usar itm-3", "esperar", ...) y se
    entrega al controlador desde pedir_comando().
  * Después de cada comando la vista pide "inv" por su cuenta, para que la
    lista de inventario de la derecha siempre esté al día.
"""

import time
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

FONDO   = "#0d0d14"
PANEL   = "#16161f"
SALA    = "#1e1e2e"
TEXTO   = "#f0f0ff"
TENUE   = "#7070a0"
VERDE   = "#3ddc84"
ROJO    = "#ff4f4f"
AMARILLO= "#ffd166"
AZUL    = "#56b4ff"
NARANJA = "#ff9f43"
MORADO  = "#9b59b6"
PIEDRA  = "#2a2a3d"
BORDE   = "#44446a"

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
"""


class VistaGrafica:
    ANCHO = 760
    ALTO = 440

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚔  CRIPTA  ⚔")
        self.root.configure(bg=FONDO)
        self.root.minsize(1100, 720)
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        self._cola = []                 # comandos pendientes de entregar al controlador
        self._cerrada = False
        self._refrescar_inv = True      # pedir "inv" antes de esperar al jugador
        self._ayuda_omitida = False     # el controlador pide ayuda al arrancar: no abrir ventana
        self._items = []                # ítems del inventario que se ven en la lista

        self._construir()
        self._atar_teclas()

    # ------------------------------------------------------------------
    # Construcción de la ventana
    # ------------------------------------------------------------------
    def _construir(self):
        estilo = ttk.Style(self.root)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("TButton", padding=5)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        izq = tk.Frame(self.root, bg=FONDO)
        izq.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        der = tk.Frame(self.root, bg=FONDO)
        der.grid(row=0, column=1, sticky="ns", padx=(5, 10), pady=10)

        # --- izquierda: sala, aviso, bitácora, botones ---
        self.canvas = tk.Canvas(izq, width=self.ANCHO, height=self.ALTO, bg=FONDO,
                                highlightthickness=0)
        self.canvas.pack()

        self.var_aviso = tk.StringVar(value="")
        self.lbl_aviso = tk.Label(izq, textvariable=self.var_aviso, bg=FONDO, fg=AMARILLO,
                                  anchor="w", justify="left", wraplength=self.ANCHO,
                                  font=("Courier", 9, "bold"))
        self.lbl_aviso.pack(fill="x", pady=(4, 2))

        tk.Label(izq, text="► Mensajes", bg=FONDO, fg=TENUE, anchor="w",
                 font=("Courier", 9)).pack(fill="x")
        self.log = tk.Text(izq, height=9, bg=PANEL, fg=TEXTO, relief="flat", wrap="word",
                           state="disabled", font=("Courier", 9),
                           insertbackground=TEXTO, padx=6, pady=4)
        self.log.pack(fill="both", expand=True, pady=(0, 6))

        botones = tk.Frame(izq, bg=FONDO)
        botones.pack(fill="x")
        acciones = [
            ("Esperar (Espacio)", "esperar"),
            ("Retroceso (R)", "retroceso"),
            ("Guardar", "guardar"),
            ("Cargar", "cargar"),
            ("Puntajes", "puntajes"),
            ("Ayuda", "ayuda"),
            ("Salir", "salir"),
        ]
        for i, (texto, comando) in enumerate(acciones):
            ttk.Button(botones, text=texto,
                       command=lambda c=comando: self._enviar(c)).grid(row=0, column=i, padx=2)

        # --- derecha: estado del jugador e inventario ---
        tk.Label(der, text="⚔  C R I P T A  ⚔", bg=FONDO, fg=AMARILLO,
                 font=("Courier", 16, "bold")).pack(anchor="w", pady=(0, 6))
        tk.Frame(der, bg=BORDE, height=2).pack(fill="x", pady=(0, 6))

        self.var_sala = tk.StringVar()
        self.var_tiempo = tk.StringVar()
        self.var_stats = tk.StringVar()
        self.var_inv = tk.StringVar()
        self.var_efectos = tk.StringVar()
        tk.Label(der, textvariable=self.var_sala, bg=FONDO, fg=TEXTO, anchor="w",
                 wraplength=320, justify="left", font=("Courier", 10, "bold")).pack(fill="x")
        tk.Label(der, textvariable=self.var_tiempo, bg=FONDO, fg=TENUE, anchor="w",
                 wraplength=320, justify="left", font=("Courier", 9)).pack(fill="x")

        self.barra = tk.Canvas(der, width=320, height=26, bg=FONDO, highlightthickness=0)
        self.barra.pack(pady=(8, 4))
        tk.Label(der, textvariable=self.var_stats, bg=FONDO, fg=AZUL, anchor="w",
                 wraplength=320, justify="left", font=("Courier", 9)).pack(fill="x")
        tk.Label(der, textvariable=self.var_efectos, bg=FONDO, fg=MORADO, anchor="w",
                 wraplength=320, justify="left", font=("Courier", 9)).pack(fill="x")

        tk.Frame(der, bg=BORDE, height=2).pack(fill="x", pady=(10, 4))
        tk.Label(der, textvariable=self.var_inv, bg=FONDO, fg=AMARILLO, anchor="w",
                 font=("Courier", 10, "bold")).pack(fill="x", pady=(0, 2))

        self.lista = tk.Listbox(der, width=44, height=14, bg=PANEL, fg=TEXTO,
                                selectbackground=AZUL, selectforeground="black",
                                activestyle="none", relief="flat", exportselection=False,
                                font=("Courier", 9))
        self.lista.pack(fill="x")
        self.lista.bind("<Double-Button-1>", self._doble_clic_inventario)

        orden = tk.Frame(der, bg=FONDO)
        orden.pack(fill="x", pady=6)
        tk.Label(orden, text="Ordenar por:", bg=FONDO, fg=TENUE).pack(side="left")
        self.var_orden = tk.StringVar(value="orden real")
        self.combo = ttk.Combobox(orden, textvariable=self.var_orden, state="readonly", width=11,
                                  values=("orden real", "peso", "valor", "nombre"))
        self.combo.pack(side="left", padx=4)
        self.combo.bind("<<ComboboxSelected>>", self._cambio_orden)
        self.var_desc = tk.IntVar(value=0)
        tk.Checkbutton(orden, text="descendente", variable=self.var_desc, bg=FONDO, fg=TEXTO,
                       selectcolor=PANEL, activebackground=FONDO, activeforeground=TEXTO,
                       command=self._cambio_orden).pack(side="left")

        acc = tk.Frame(der, bg=FONDO)
        acc.pack(fill="x")
        for texto, verbo in (("Usar", "usar"), ("Equipar", "equipar"), ("Soltar", "soltar")):
            ttk.Button(acc, text=texto,
                       command=lambda v=verbo: self._accion_inventario(v)).pack(
                           side="left", expand=True, fill="x", padx=2)

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
        self._cola.append(comando)

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
        self._cola.clear()              # descarta clics hechos mientras el juego procesaba
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
        """Diálogo de selección de cripta. Devuelve el id o None si se cierra."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Elige una cripta")
        dlg.configure(bg=FONDO)
        dlg.transient(self.root)
        tk.Label(dlg, text="Elige una cripta:", bg=FONDO, fg=TEXTO,
                 font=("TkDefaultFont", 12, "bold")).pack(padx=14, pady=(14, 6))
        lb = tk.Listbox(dlg, width=58, height=max(3, min(12, len(criptas))), bg=PANEL, fg=TEXTO,
                        selectbackground=AZUL, selectforeground="black", relief="flat",
                        exportselection=False)
        for c in criptas:
            lb.insert("end", f"{c['id']} — {c['nombre']}  "
                             f"({c['salas']} salas, dificultad {c['dificultad']})")
        lb.pack(padx=14)
        if criptas:
            lb.selection_set(0)
        elegido = []

        def aceptar(_evento=None):
            seleccion = lb.curselection()
            if seleccion:
                elegido.append(criptas[seleccion[0]]["id"])
                dlg.destroy()

        lb.bind("<Double-Button-1>", aceptar)
        ttk.Button(dlg, text="Jugar", command=aceptar).pack(pady=12)
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)
        dlg.grab_set()
        self.root.wait_window(dlg)
        return elegido[0] if elegido else None

    # ------------------------------------------------------------------
    # Inventario (lado derecho)
    # ------------------------------------------------------------------
    def _instancia_seleccionada(self):
        seleccion = self.lista.curselection()
        if not seleccion or seleccion[0] >= len(self._items):
            return None
        return self._items[seleccion[0]]

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
        elif item.clase not in ("llave", "pergamino_retroceso"):
            self._enviar(f"usar {item.instancia}")

    def _cambio_orden(self, _evento=None):
        self._enviar(self._cmd_inventario())
        self.root.focus_set()

    def mostrar_inventario(self, items, orden=None, cursor=None):
        if self._cerrada:
            return
        iconos_clase = {
            "arma": "⚔", "armadura": "🛡", "pocion": "🧪",
            "llave": "🔑", "pergamino_retroceso": "📜", "antorcha": "🕯",
        }
        previo = self._instancia_seleccionada()
        self._items = list(items)
        self.lista.delete(0, "end")
        reseleccion = None
        for i, it in enumerate(self._items):
            marca = "★ " if it.equipado else "  "
            icono = iconos_clase.get(it.clase, "○")
            self.lista.insert("end", f"{marca}{icono} {it.nombre}  [{it.clase} p:{it.peso} v:{it.valor}]")
            if it.equipado:
                self.lista.itemconfig(i, foreground=AMARILLO)
            if previo is not None and it.instancia == previo.instancia:
                reseleccion = i
        if reseleccion is not None:
            self.lista.selection_set(reseleccion)

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
        self._dibujar_sala(e)
        self._actualizar_stats(e)
        self._actualizar_log(mensajes)
        self.root.update_idletasks()

    def _ligar(self, etiqueta, comando):
        c = self.canvas
        c.tag_bind(etiqueta, "<Button-1>", lambda _ev, cmd=comando: self._enviar(cmd))
        c.tag_bind(etiqueta, "<Enter>", lambda _ev: c.config(cursor="hand2"))
        c.tag_bind(etiqueta, "<Leave>", lambda _ev: c.config(cursor=""))

    @staticmethod
    def _color_vida(vida, vida_max):
        fraccion = vida / max(1, vida_max)
        if fraccion > 0.5:
            return VERDE
        return AMARILLO if fraccion > 0.25 else ROJO

    def _dibujar_sala(self, e):
        c = self.canvas
        c.delete("all")
        ancho, alto = self.ANCHO, self.ALTO
        x0, y0, x1, y1 = 90, 75, ancho - 90, alto - 65
        cx, cy = ancho // 2, (y0 + y1) // 2

        # --- fondo con patrón de piedra ---
        for gx in range(0, ancho, 32):
            for gy in range(0, alto, 16):
                offset = 16 if (gy // 16) % 2 else 0
                c.create_rectangle(gx + offset, gy, gx + offset + 30, gy + 14,
                                   fill="#111118", outline="#1a1a26", width=1)

        # --- sala principal ---
        c.create_rectangle(x0 + 4, y0 + 4, x1 + 4, y1 + 4, fill="#0a0a12", outline="")
        c.create_rectangle(x0, y0, x1, y1, fill=SALA, outline=BORDE, width=3)
        # esquinas decorativas
        sz = 12
        for (ex, ey) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            c.create_rectangle(ex - sz//2, ey - sz//2, ex + sz//2, ey + sz//2,
                               fill=BORDE, outline=AMARILLO, width=1)

        # título de sala con fondo
        c.create_rectangle(cx - 140, y0 + 4, cx + 140, y0 + 28,
                           fill="#0d0d1a", outline=BORDE)
        c.create_text(cx, y0 + 16, text=f"⌂  Sala {e.sala_id}: {e.sala_nombre}  ⌂",
                      fill=AMARILLO, font=("Courier", 11, "bold"))

        # --- puertas ---
        geometria = {
            "N": ((cx - 40, y0 - 10, cx + 40, y0 + 10), (cx, y0 - 28, "center")),
            "S": ((cx - 40, y1 - 10, cx + 40, y1 + 10), (cx, y1 + 28, "center")),
            "E": ((x1 - 10, cy - 40, x1 + 10, cy + 40), (x1 + 16, cy, "w")),
            "O": ((x0 - 10, cy - 40, x0 + 10, cy + 40), (x0 - 16, cy, "e")),
        }
        flechas = {"N": "↑", "S": "↓", "E": "→", "O": "←"}
        for s in e.salidas:
            if s.direccion not in geometria:
                continue
            caja, (tx, ty, ancla) = geometria[s.direccion]
            etiqueta = f"puerta_{s.direccion}"
            color_puerta = NARANJA if s.cerrada else VERDE
            icono = "🔒" if s.cerrada else flechas[s.direccion]
            llave = (s.llave or "").replace("itm_", "").replace("_", " ")
            texto = f"{icono} {NOMBRES_DIR[s.direccion]}"
            if s.cerrada and llave:
                texto += f"\n({llave})"
            # sombra
            c.create_rectangle(caja[0]+3, caja[1]+3, caja[2]+3, caja[3]+3,
                               fill="#000000", outline="")
            c.create_rectangle(*caja, fill=color_puerta, outline="white", width=2,
                               tags=(etiqueta,))
            c.create_text(tx, ty, text=texto, fill="white", anchor=ancla,
                          width=80 if s.direccion in ("E", "O") else 220, justify="center",
                          font=("Courier", 8, "bold"), tags=(etiqueta,))
            self._ligar(etiqueta, f"abrir {s.direccion}" if s.cerrada else f"mover {s.direccion}")

        # --- enemigos ---
        iconos_enemigo = ["👺", "💀", "🦴", "🐉", "🦧", "👻"]
        por_fila, ancho_c, alto_c = 4, 116, 70
        visibles = e.enemigos[:2 * por_fila]
        for i, en in enumerate(visibles):
            fila, col = divmod(i, por_fila)
            en_fila = min(por_fila, len(visibles) - fila * por_fila)
            total = en_fila * ancho_c + (en_fila - 1) * 10
            ex = cx - total // 2 + col * (ancho_c + 10)
            ey = y0 + 42 + fila * (alto_c + 8)
            etiqueta = f"enemigo_{i}"
            icono_e = iconos_enemigo[i % len(iconos_enemigo)]
            # sombra
            c.create_rectangle(ex+3, ey+3, ex+ancho_c+3, ey+alto_c+3,
                               fill="#000000", outline="")
            c.create_rectangle(ex, ey, ex + ancho_c, ey + alto_c,
                               fill="#3a1520", outline=ROJO, width=2, tags=(etiqueta,))
            c.create_text(ex + ancho_c // 2, ey + 14, text=icono_e,
                          font=("TkDefaultFont", 14), tags=(etiqueta,))
            c.create_text(ex + ancho_c // 2, ey + 32, text=en.nombre, fill=TEXTO,
                          width=ancho_c - 8, justify="center",
                          font=("Courier", 8, "bold"), tags=(etiqueta,))
            fraccion = max(0, en.vida) / max(1, en.vida_max)
            color_v = self._color_vida(en.vida, en.vida_max)
            c.create_rectangle(ex + 8, ey + 44, ex + ancho_c - 8, ey + 56,
                               fill="#1a1a1a", outline=BORDE, tags=(etiqueta,))
            c.create_rectangle(ex + 8, ey + 44,
                               ex + 8 + int((ancho_c - 16) * fraccion), ey + 56,
                               fill=color_v, outline="", tags=(etiqueta,))
            c.create_text(ex + ancho_c // 2, ey + 63,
                          text=f"♥ {en.vida}/{en.vida_max}",
                          fill=color_v, font=("Courier", 7), tags=(etiqueta,))
            self._ligar(etiqueta, f"atacar {en.instancia}")
        if len(e.enemigos) > len(visibles):
            c.create_text(x1 - 10, y0 + 18, anchor="e", fill=ROJO,
                          text=f"+{len(e.enemigos) - len(visibles)} más",
                          font=("Courier", 8, "bold"))

        # --- objetos del suelo ---
        chip_ancho, chip_alto = 104, 26
        visibles_o = e.objetos_suelo[:8]
        for i, o in enumerate(visibles_o):
            fila, col = divmod(i, 4)
            ix = x0 + 100 + col * (chip_ancho + 6)
            iy = y1 - 68 + fila * (chip_alto + 6)
            etiqueta = f"objeto_{i}"
            nombre = o.nombre if len(o.nombre) <= 15 else o.nombre[:14] + "…"
            c.create_rectangle(ix+2, iy+2, ix+chip_ancho+2, iy+chip_alto+2,
                               fill="#000000", outline="")
            c.create_rectangle(ix, iy, ix + chip_ancho, iy + chip_alto,
                               fill="#3a3010", outline=AMARILLO, width=1, tags=(etiqueta,))
            c.create_text(ix + chip_ancho // 2, iy + chip_alto // 2,
                          text=f"★ {nombre}", fill=AMARILLO,
                          font=("Courier", 8), tags=(etiqueta,))
            self._ligar(etiqueta, f"recoger {o.instancia}")
        if len(e.objetos_suelo) > len(visibles_o):
            c.create_text(x1 - 8, y1 - 8, anchor="se", fill=AMARILLO,
                          text=f"+{len(e.objetos_suelo) - len(visibles_o)} objetos más",
                          font=("Courier", 8))

        # --- el jugador ---
        px, py = x0 + 48, y1 - 48
        c.create_oval(px - 24, py - 24, px + 24, py + 24,
                      fill="#0a2a4a", outline=AZUL, width=3)
        c.create_text(px, py - 4, text="⛔", font=("TkDefaultFont", 16))
        c.create_text(px, py + 18, text=f"♥ {e.vida}/{e.vida_max}",
                      fill=self._color_vida(e.vida, e.vida_max),
                      font=("Courier", 8, "bold"))

    def _actualizar_stats(self, e):
        self.var_sala.set(f"⌂  Sala {e.sala_id} — {e.sala_nombre}")
        self.var_tiempo.set(f"⏱  Tiempo virtual: {e.reloj}")
        self.var_stats.set(f"⚔ Ataque {e.ataque}   🛡 Defensa {e.defensa}   ⚡ Velocidad {e.velocidad}")
        self.var_inv.set(f"🎒  Inventario  {e.inventario_usado}/{e.inventario_max}")
        efectos_txt = ", ".join(e.efectos) if e.efectos else "ninguno"
        self.var_efectos.set(f"✨ Efectos: {efectos_txt}")
        b = self.barra
        b.delete("all")
        fraccion = max(0, e.vida) / max(1, e.vida_max)
        color_v = self._color_vida(e.vida, e.vida_max)
        b.create_rectangle(0, 0, 320, 26, fill="#1a1a1a", outline=BORDE)
        b.create_rectangle(2, 2, 2 + int(316 * fraccion), 24, fill=color_v, outline="")
        b.create_text(160, 13, text=f"♥  Vida  {e.vida} / {e.vida_max}",
                      fill="white", font=("Courier", 10, "bold"))

    def _actualizar_log(self, mensajes):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.tag_configure("dano", foreground=ROJO)
        self.log.tag_configure("bien", foreground=VERDE)
        self.log.tag_configure("normal", foreground=TEXTO)
        for m in mensajes:
            ml = m.lower()
            if any(p in ml for p in ("muere", "derrota", "daño", "veneno", "trampa", "herido")):
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
    # Cierre
    # ------------------------------------------------------------------
    def _al_cerrar(self):
        self.cerrar()

    def cerrar(self):
        if self._cerrada:
            return
        self._cerrada = True
        try:
            self.root.destroy()
        except tk.TclError:
            pass