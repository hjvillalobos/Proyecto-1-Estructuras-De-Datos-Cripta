import tkinter as tk
from tkinter import ttk

from vista.tema import FONDO, PANEL, TEXTO, AMARILLO, VERDE, BORDE, configurar_botones_menu


class SelectorCripta:
    """Seleccion visual local; devuelve un identificador sin acceder al motor."""

    def __init__(self, vista, criptas):
        self.vista = vista
        configurar_botones_menu(vista.root)
        self.criptas = criptas
        self.resultado = None
        self.imagenes = []
        self.dialogo = tk.Toplevel(vista.root)
        self.dialogo.title("CRIPTA - Elige tu cripta")
        self.dialogo.configure(bg=FONDO)
        self.dialogo.transient(vista.root)
        self.dialogo.geometry("960x640")
        self.dialogo.minsize(820, 560)
        self.canvas = tk.Canvas(self.dialogo, bg=FONDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.lista = tk.Listbox(self.dialogo, bg=PANEL, fg=TEXTO,
                               font=("Segoe UI", 15), relief="flat", borderwidth=0,
                               selectbackground=AMARILLO, selectforeground=FONDO,
                               highlightthickness=1, highlightbackground=BORDE,
                               highlightcolor=AMARILLO, exportselection=False,
                               activestyle="none")
        self.lista.place(relx=.41, rely=.29, relwidth=.54, relheight=.26)
        for cripta in criptas:
            self.lista.insert("end", cripta["nombre"])
        if criptas:
            self.lista.selection_set(0)
        self.lista.bind("<<ListboxSelect>>", self.dibujar)
        self.lista.bind("<Double-Button-1>", self.aceptar)
        self.lista.bind("<Return>", self.aceptar)
        self.dialogo.bind("<Escape>", lambda _evento: self.dialogo.destroy())
        self.controles = tk.Frame(self.dialogo, bg=FONDO)
        self.controles.place(relx=.68, rely=.85, anchor="center", width=380, height=48)
        ttk.Button(self.controles, text="Volver", command=self.dialogo.destroy, style="Menu.TButton").pack(
            side="left", fill="both", expand=True, padx=(0, 8))
        ttk.Button(self.controles, text="Jugar", command=self.aceptar,
                   style="Principal.Menu.TButton",
                   state="normal" if criptas else "disabled").pack(
            side="left", fill="both", expand=True)
        self.dialogo.protocol("WM_DELETE_WINDOW", self.dialogo.destroy)
        self.canvas.bind("<Configure>", self.dibujar)

    def aceptar(self, _evento=None):
        seleccion = self.lista.curselection()
        if seleccion:
            self.resultado = self.criptas[seleccion[0]]["id"]
            self.dialogo.destroy()
        return "break"

    def dibujar(self, _evento=None):
        self.canvas.delete("all")
        self.imagenes.clear()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        fondo = self.vista.recursos.fondo(w, h)
        if fondo is not None:
            self.imagenes.append(fondo)
            self.canvas.create_image(0, 0, image=fondo, anchor="nw")
        jugador = self.vista.recursos.imagen("jugador", int(w * .29), int(h * .68))
        if jugador is not None:
            self.imagenes.append(jugador)
            self.canvas.create_image(w * .19, h * .9, image=jugador, anchor="s")
        self.canvas.create_text(w * .68, h * .13, text="ELIGE TU CRIPTA", fill=AMARILLO,
                                font=("Georgia", 26, "bold"))
        self.canvas.create_line(w * .41, h * .21, w * .95, h * .21, fill=AMARILLO)
        seleccion = self.lista.curselection()
        if seleccion:
            cripta = self.criptas[seleccion[0]]
            self.canvas.create_text(w * .51, h * .64, text=str(cripta["salas"]), fill=VERDE,
                                    font=("Georgia", 36, "bold"))
            self.canvas.create_text(w * .51, h * .71, text="SALAS", fill=TEXTO,
                                    font=("Segoe UI", 11))
            self.canvas.create_text(w * .82, h * .64, text=str(cripta["dificultad"]), fill=AMARILLO,
                                    font=("Georgia", 36, "bold"))
            self.canvas.create_text(w * .82, h * .71, text="DIFICULTAD", fill=TEXTO,
                                    font=("Segoe UI", 11))
        else:
            self.canvas.create_text(w * .68, h * .64, text="No hay criptas disponibles.",
                                    fill=TEXTO, font=("Segoe UI", 14))
        self.canvas.create_text(w * .19, h * .96, text="t = 0", fill=TEXTO,
                                font=("Consolas", 14))

    def mostrar(self):
        en_menu = getattr(self.vista, "_en_menu", False)
        self.vista._en_menu = True
        try:
            self.dialogo.grab_set()
            self.lista.focus_set()
            self.vista.root.wait_window(self.dialogo)
            return self.resultado
        finally:
            self.vista._en_menu = en_menu
            self.vista._cola.clear()
            self.imagenes.clear()
