import tkinter as tk
from pathlib import Path
from tkinter import ttk

from datos.guardado_binario import RUTA_GUARDADO_PREDETERMINADA

from vista.tema import FONDO, TEXTO, AMARILLO, VERDE, configurar_botones_menu
from vista.animacion import AnimacionEscena
from vista.sonidos import sonorizar_botones


class MenuInicio:
    """Menu local: solo devuelve una eleccion, sin crear ni avanzar el motor."""

    def __init__(self, vista, replay, puntajes):
        self.vista = vista
        configurar_botones_menu(vista.root)
        self.resultado = None
        self._cargando = False
        self.fin = tk.BooleanVar(master=vista.root, value=False)
        self.panel = tk.Frame(vista.root, bg=FONDO)
        self.panel.place(relwidth=1, relheight=1)
        self.canvas = tk.Canvas(self.panel, bg=FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.animacion = AnimacionEscena(vista.root, self.canvas)
        self.imagenes = []
        self.botones = []
        acciones = (("Jugar", lambda: self.elegir("jugar")), ("Cargar partida", self.cargar),
                    ("Replay", replay), ("Puntajes", puntajes), ("Salir", lambda: self.elegir("salir")))
        self.controles = tk.Frame(self.panel, bg=FONDO)
        self.controles.place(relx=.63, rely=.43, anchor="n", width=280)
        for nombre, comando in acciones:
            boton = ttk.Button(self.controles, text=nombre, command=comando, takefocus=True,
                               style="Principal.Menu.TButton" if nombre == "Jugar" else "Menu.TButton")
            boton.pack(fill="x", pady=5, ipady=5)
            boton.bind("<Up>", lambda e: self.mover(-1))
            boton.bind("<Down>", lambda e: self.mover(1))
            boton.bind("<Return>", lambda e, b=boton: self.activar(b))
            self.botones.append(boton)
        self.canvas.bind("<Configure>", self.dibujar)
        sonorizar_botones(self.panel, vista.sonidos)

    def activar(self, boton):
        boton.invoke()
        return "break"

    def mover(self, avance):
        foco = self.vista.root.focus_get()
        indice = self.botones.index(foco) if foco in self.botones else 0
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
        self.animacion.detener()
        self.canvas.delete("all")
        self.imagenes.clear()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
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
        for nombre, x, ancho, alto, fase in (("jugador", w * .23, 320, int(h * .68), 0),):
            imagen = self.vista.recursos.imagen(nombre, ancho, alto)
            if imagen is not None:
                self.imagenes.append(imagen)
                sprite = self.canvas.create_image(x, h * .82, image=imagen, anchor="s")
                self.animacion.agregar(sprite, fase=fase)
        if self.vista._movimiento_activo:
            self.animacion.iniciar()

    def mostrar(self):
        self.vista._en_menu = True
        self.vista.root.protocol("WM_DELETE_WINDOW", lambda: self.elegir("salir"))
        try:
            self.vista.root.update_idletasks()
            if getattr(self.vista, "sonidos", None) is not None:
                self.vista.sonidos.reproducir("inicio")
            self.botones[0].focus_set()
            self.vista.root.wait_variable(self.fin)
            return self.resultado
        finally:
            self.animacion.detener()
            if (self.resultado is not None and self.resultado[0] in ("jugar", "cargar")
                    and callable(getattr(type(self.vista), "_conservar_inicio", None))):
                self.controles.place_forget()
                self._cargando = True
                self.canvas.itemconfigure("subtitulo", text="Cargando…")
                self.vista._conservar_inicio(self)
            else:
                self.panel.destroy()
            self.vista._en_menu = False
            self.vista._cola.clear()
            self.vista.root.protocol("WM_DELETE_WINDOW", self.vista._al_cerrar)
            self.vista.root.focus_set()
