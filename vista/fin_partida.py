"""Pantalla de resultado local: presenta el resumen sin ejecutar acciones."""

import tkinter as tk
from tkinter import ttk
from vista.sonidos import sonorizar_botones

from vista.tema import FONDO, PANEL, TEXTO, TENUE, AMARILLO, ROJO, configurar_botones_menu


class FinPartida:
    def __init__(self, vista, resumen):
        self.vista, self.resumen = vista, resumen
        self.reiniciar = False
        self.panel = tk.Frame(vista.root, bg=FONDO)
        self.panel.place(relwidth=1, relheight=1)
        self.canvas = tk.Canvas(self.panel, bg=FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.imagenes = []
        self.estadisticas_visibles = False
        configurar_botones_menu(vista.root)
        self.controles = tk.Frame(self.panel, bg=FONDO, padx=16, pady=12)
        self.controles.place(relx=.64, rely=.78, anchor="n", width=340)
        self.permite_reinicio = resumen.resultado == "derrota" and not vista._en_replay
        self.botones = []
        if self.permite_reinicio:
            self._boton("Jugar de nuevo", True, "Principal.Menu.TButton")
        self._boton("Cerrar replay" if vista._en_replay else "Terminar", False,
                    "Menu.TButton" if self.permite_reinicio else "Principal.Menu.TButton")
        self.boton_estadisticas = ttk.Button(self.panel, text="Ver estadísticas",
            style="Menu.TButton", command=self.alternar_estadisticas, takefocus=True)
        self.boton_estadisticas.place(relx=.64, rely=.40, anchor="n", width=308)
        self.boton_estadisticas.bind("<Return>", lambda e: self.alternar_estadisticas())
        self.canvas.bind("<Configure>", self.dibujar)
        sonorizar_botones(self.panel, vista.sonidos)

    def alternar_estadisticas(self):
        self.estadisticas_visibles = not self.estadisticas_visibles
        self.boton_estadisticas.configure(text="Ocultar estadísticas" if self.estadisticas_visibles
                                         else "Ver estadísticas")
        self.dibujar()
        return "break"

    def _boton(self, texto, reiniciar, estilo):
        boton = ttk.Button(self.controles, text=texto, style=estilo,
                           command=lambda: self.elegir(reiniciar), takefocus=True)
        boton.pack(fill="x", pady=4)
        boton.bind("<Return>", lambda e: self.elegir(reiniciar))
        self.botones.append(boton)

    def elegir(self, reiniciar=False):
        self.reiniciar = bool(reiniciar and self.permite_reinicio)
        self.panel.destroy()
        return "break"

    def dibujar(self, _evento=None):
        c = self.canvas
        c.delete("all")
        self.imagenes.clear()
        w, h = max(1, c.winfo_width()), max(1, c.winfo_height())
        fondo = self.vista.recursos.fondo(w, h)
        if fondo is not None:
            self.imagenes.append(fondo)
            c.create_image(0, 0, image=fondo, anchor="nw")
        victoria = self.resumen.resultado == "victoria"
        derrota = self.resumen.resultado == "derrota"
        titulo = "Victoria" if victoria else "Derrota" if derrota else "Fin de partida"
        mensaje = ("Has escapado de la cripta." if victoria else
                   "Tu aventura termina aquí." if derrota else "Sesión terminada.")
        color = AMARILLO if victoria else ROJO if derrota else TEXTO
        # Un solo telon de lectura, sobre el mismo escenario del inicio.
        x, margen = w * .64, 210
        self.controles.place_configure(rely=.78 if self.estadisticas_visibles else .51)
        c.create_rectangle(x - margen, h * .15, x + margen,
                           h * (.96 if self.estadisticas_visibles else .74),
                           fill=FONDO, outline="")
        c.create_text(x, h * .23, text=titulo, fill=color, font=("Georgia", 42, "bold"))
        c.create_text(x, h * .32, text=mensaje, fill=TEXTO, font=("Georgia", 16), width=380)
        if self.vista._en_replay:
            c.create_text(x, h * .37, text="Replay finalizado", fill=TENUE, font=("Segoe UI", 11))
        filas = (("Acciones", self.resumen.acciones),
                 ("Enemigos derrotados", self.resumen.derrotados),
                 ("Tiempo virtual", f"{self.resumen.reloj_final} u.t."))
        for i, (nombre, valor) in enumerate(filas if self.estadisticas_visibles else ()):
            y = h * (.50 + i * .08)
            c.create_text(x - 170, y, text=nombre, anchor="w", fill=TENUE, font=("Segoe UI", 12))
            c.create_text(x + 170, y, text=str(valor), anchor="e", fill=TEXTO,
                          font=("Consolas", 17, "bold"))
            c.create_line(x - 170, y + 26, x + 170, y + 26, fill=PANEL)
        imagen = self.vista.recursos.imagen("jugador", int(w * .30), int(h * .62))
        if imagen is not None:
            self.imagenes.append(imagen)
            c.create_image(w * .24, h * .87, image=imagen, anchor="s")

    def mostrar(self):
        v = self.vista
        anterior = getattr(v, "_en_menu", False)
        v._en_menu = True
        v._cola.clear()
        escape = v.root.bind("<Escape>", lambda e: self.elegir(), add="+")
        try:
            v.root.update_idletasks()
            self.botones[0].focus_set()
            v.root.wait_window(self.panel)
            return self.reiniciar
        finally:
            v._en_menu = anterior
            v._cola.clear()
            self.imagenes.clear()
            if not v._cerrada:
                v.root.unbind("<Escape>", escape)
                if self.panel.winfo_exists():
                    self.panel.destroy()
                v.root.focus_set()
