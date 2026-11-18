import tkinter as tk
from pathlib import Path
from tkinter import ttk

from datos.guardado_binario import RUTA_GUARDADO_PREDETERMINADA

from vista.tema import FONDO, TEXTO, AMARILLO, VERDE, BORDE, configurar_botones_menu
from vista.animacion import AnimacionEscena
from vista.sonidos import sonorizar_botones
from vista.personajes import PERSONAJES, guardar_personaje


class MenuInicio:
    """Menu local: solo devuelve una eleccion, sin crear ni avanzar el motor."""

    def __init__(self, vista, replay, puntajes):
        self.vista = vista
        configurar_botones_menu(vista.root)
        self.resultado = None
        self._cargando = False
        self._precarga_selector = None
        self.fin = tk.BooleanVar(master=vista.root, value=False)
        self.panel = tk.Frame(vista.root, bg=FONDO)
        self.panel.bind("<Destroy>", self._destruir, add="+")
        self.panel.place(x=0, y=0, relwidth=1, relheight=1)
        self.panel.lift()
        self.canvas = tk.Canvas(self.panel, bg=FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.animacion = AnimacionEscena(vista.root, self.canvas)
        self.imagenes = []
        self.botones = []
        self.selector_personaje = tk.Frame(self.panel, bg=FONDO)
        self.selector_personaje.place(relx=.23, rely=.84, anchor="n")
        tk.Label(self.selector_personaje, text="Elige tu personaje", bg=FONDO, fg=TEXTO,
                 font=("Georgia", 14)).pack()
        self.personaje = tk.StringVar(master=vista.root, value=vista.recursos.personaje)
        opciones = tk.Frame(self.selector_personaje, bg=FONDO)
        opciones.pack(pady=4)
        for identidad, nombre in PERSONAJES:
            ttk.Radiobutton(opciones, text=nombre, value=identidad, variable=self.personaje,
                            command=self.cambiar_personaje).pack(side="left", padx=12)
        acciones = (("Jugar", lambda: self.elegir("jugar")), ("Cargar partida", self.cargar),
                    ("Replay", replay), ("Puntajes", puntajes), ("Salir", lambda: self.elegir("salir")))
        self.controles = tk.Frame(self.panel, bg=FONDO)
        self.controles.place(relx=.63, rely=.43, anchor="n", width=280)
        for nombre, comando in acciones:
            boton = ttk.Button(self.controles, text=nombre, command=comando, takefocus=True,
                               style="Menu.TButton")
            boton.pack(fill="x", pady=5, ipady=5)
            boton.bind("<Up>", lambda e: self.mover(-1))
            boton.bind("<Down>", lambda e: self.mover(1))
            boton.bind("<Left>", lambda e: self.mover(-1))
            boton.bind("<Right>", lambda e: self.mover(1))
            boton.bind("<Return>", lambda e, b=boton: self.activar(b))
            boton.bind("<Motion>", lambda e, b=boton: b.focus_set())
            self.botones.append(boton)
        for tecla, avance in (("Up", -1), ("Down", 1), ("Left", -1), ("Right", 1)):
            self.canvas.bind("<" + tecla + ">", lambda e, paso=avance: self.mover(paso))
        self.canvas.bind("<Return>", lambda e: self.activar(self.botones[0]))
        self.canvas.bind("<Configure>", self.dibujar)
        sonorizar_botones(self.panel, vista.sonidos)

    def cambiar_personaje(self):
        if self.personaje.get() == self.vista.recursos.personaje:
            return
        self.vista.recursos.seleccionar_personaje(self.personaje.get())
        guardar_personaje(self.personaje.get())
        self.dibujar()

    def elegir_personaje(self, personaje):
        self.personaje.set(personaje)
        self.cambiar_personaje()

    def activar(self, boton):
        boton.invoke()
        return "break"

    def mover(self, avance):
        foco = self.vista.root.focus_get()
        indice = self.botones.index(foco) if foco in self.botones else (-1 if avance > 0 else 0)
        self.botones[(indice + avance) % len(self.botones)].focus_set()
        return "break"

    def elegir(self, accion, ruta=None):
        self.resultado = (accion, ruta)
        self.fin.set(True)

    def cargar(self):
        if not Path(RUTA_GUARDADO_PREDETERMINADA).is_file():
            self.vista.mostrar_error_replay("Aun no hay una partida guardada para cargar.")
            return
        self.elegir("cargar", RUTA_GUARDADO_PREDETERMINADA)

    def dibujar(self, _evento=None):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            return
        self.animacion.detener()
        self.animacion = AnimacionEscena(self.vista.root, self.canvas)
        self.canvas.delete("all")
        self.imagenes.clear()
        fondo = self.vista.recursos.fondo(w, h)
        if fondo is not None:
            self.imagenes.append(fondo)
            self.canvas.create_image(0, 0, image=fondo, anchor="nw")
        self.canvas.create_text(w * .63 + 2, h * .23 + 3, text="CRIPTA", fill=FONDO,
                                font=("Georgia", 64, "bold"))
        self.canvas.create_text(w * .63, h * .23, text="CRIPTA", fill=AMARILLO, font=("Georgia", 64, "bold"))
        self.canvas.create_text(w * .63, h * .34,
                                text="Cargando…" if self._cargando else "La salida te espera.", fill=TEXTO,
                                font=("Georgia", 18), tags=("subtitulo",))
        self.canvas.create_text(w * .63, h * .87, text="Reloj virtual", fill=TEXTO, font=("Segoe UI", 11))
        self.canvas.create_text(w * .63, h * .92, text="t = 0", fill=VERDE, font=("Consolas", 22, "bold"))
        for fase, (nombre, etiqueta) in enumerate(PERSONAJES):
            x = w * (.13 if fase == 0 else .35)
            ancho, alto = min(280, int(w * .205)), int(h * .64)
            tag = "personaje_" + nombre
            seleccionado = nombre == self.personaje.get()
            self.canvas.create_oval(x - ancho * .34, h * .79, x + ancho * .34, h * .82,
                                    fill=FONDO, outline=AMARILLO if seleccionado else BORDE,
                                    width=3 if seleccionado else 1, tags=(tag,))
            imagen = self.vista.recursos.retrato_personaje(nombre, ancho, alto)
            if imagen is not None:
                self.imagenes.append(imagen)
                sprite = self.canvas.create_image(x, h * .80, image=imagen, anchor="s", tags=(tag,))
                self.animacion.agregar(sprite, fase=fase)
            self.canvas.tag_bind(tag, "<Button-1>", lambda _, p=nombre: self.elegir_personaje(p))
        if self.vista._movimiento_activo:
            self.animacion.iniciar()
        self._cancelar_precarga()
        # Preparar el tamano del selector despues de pintar el menu. Tk y sus
        # PhotoImage permanecen en el hilo principal; no se consulta la API.
        self._precarga_selector = self.vista.root.after(120, self._preparar_selector)

    def _destruir(self, evento):
        if evento.widget is self.panel:
            self._cancelar_precarga()
            self.animacion.detener()

    def _cancelar_precarga(self):
        if self._precarga_selector is not None:
            try:
                self.vista.root.after_cancel(self._precarga_selector)
            except tk.TclError:
                pass
            self._precarga_selector = None

    def _preparar_selector(self):
        self._precarga_selector = None
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w > 1 and h > 1:
            self.vista.recursos.imagen("jugador", int(w * .29), int(h * .68))

    def mostrar(self, reproducir_inicio=True):
        self.vista._en_menu = True
        self.vista.root.protocol("WM_DELETE_WINDOW", lambda: self.elegir("salir"))
        try:
            self.vista.root.update_idletasks()
            self.dibujar()
            self.vista.root.update_idletasks()
            if reproducir_inicio and getattr(self.vista, "sonidos", None) is not None:
                self.vista.sonidos.reproducir("inicio")
            self.canvas.focus_set()
            self.vista.root.wait_variable(self.fin)
            return self.resultado
        finally:
            self._cancelar_precarga()
            self.animacion.detener()
            if (self.resultado is not None and self.resultado[0] in ("jugar", "cargar")
                    and callable(getattr(type(self.vista), "_conservar_inicio", None))):
                self.controles.place_forget()
                self.selector_personaje.place_forget()
                self._cargando = True
                self.canvas.itemconfigure("subtitulo", text="Cargando…")
                self.vista._conservar_inicio(self)
            else:
                self.panel.destroy()
            self.vista._en_menu = False
            self.vista._cola.clear()
            self.vista.root.protocol("WM_DELETE_WINDOW", self.vista._al_cerrar)
            self.vista.root.focus_set()
