"""Entrada de nombre con la identidad visual del juego, sin acceso al modelo."""

import tkinter as tk
from tkinter import ttk
from vista.sonidos import sonorizar_botones

from vista.tema import FONDO, PANEL, TEXTO, AMARILLO, BORDE, configurar_botones_menu


class NombrePuntaje:
    def __init__(self, vista, pregunta):
        self.vista = vista
        self.resultado = ""
        self.dialogo = tk.Toplevel(vista.root)
        self.dialogo.withdraw()
        self.dialogo.title("CRIPTA - Puntajes")
        self.dialogo.configure(bg=FONDO)
        self.dialogo.resizable(False, False)
        self.dialogo.transient(vista.root)
        self.dialogo.protocol("WM_DELETE_WINDOW", self.cancelar)
        configurar_botones_menu(vista.root)
        cabecera = tk.Canvas(self.dialogo, width=560, height=108, bg=FONDO, highlightthickness=0)
        cabecera.pack(fill="x")
        self.fondo = vista.recursos.fondo(560, 108)
        if self.fondo is not None:
            cabecera.create_image(0, 0, image=self.fondo, anchor="nw")
        cabecera.create_rectangle(20, 25, 540, 82, fill=FONDO, outline="")
        cabecera.create_text(280, 54, text="Tu nombre en la cripta", fill=AMARILLO,
                              font=("Georgia", 24, "bold"))
        cuerpo = tk.Frame(self.dialogo, bg=FONDO, padx=28, pady=20)
        cuerpo.pack(fill="both", expand=True)
        tk.Label(cuerpo, text=pregunta, bg=FONDO, fg=TEXTO, font=("Segoe UI", 12),
                 anchor="w", justify="left", wraplength=504).pack(fill="x", pady=(0, 12))
        self.nombre = tk.StringVar(master=self.dialogo)
        self.entrada = tk.Entry(cuerpo, textvariable=self.nombre, bg=PANEL, fg=TEXTO,
            insertbackground=AMARILLO, selectbackground=AMARILLO, selectforeground=FONDO,
            relief="flat", highlightthickness=2, highlightbackground=BORDE,
            highlightcolor=AMARILLO, font=("Segoe UI", 16))
        self.entrada.pack(fill="x", ipady=9)
        acciones = tk.Frame(cuerpo, bg=FONDO)
        acciones.pack(fill="x", pady=(24, 4))
        self.boton_cancelar = ttk.Button(acciones, text="Cancelar", command=self.cancelar,
                                        style="Menu.TButton")
        self.boton_cancelar.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.boton_cancelar.bind("<Return>", self.cancelar)
        self.boton_guardar = ttk.Button(acciones, text="Registrar puntaje", command=self.aceptar,
                                       style="Principal.Menu.TButton")
        self.boton_guardar.pack(side="left", fill="x", expand=True)
        self.dialogo.bind("<Return>", self.aceptar)
        self.dialogo.bind("<Escape>", self.cancelar)
        sonorizar_botones(self.dialogo, vista.sonidos)

    def aceptar(self, _evento=None):
        self.resultado = self.nombre.get().strip()
        self.dialogo.destroy()
        return "break"

    def cancelar(self, _evento=None):
        self.resultado = ""
        self.dialogo.destroy()
        return "break"

    def mostrar(self):
        v = self.vista
        anterior = getattr(v, "_en_menu", False)
        foco = v.root.focus_get()
        v._en_menu = True
        v._cola.clear()
        try:
            self.dialogo.update_idletasks()
            ancho, alto = self.dialogo.winfo_reqwidth(), self.dialogo.winfo_reqheight()
            x = v.root.winfo_rootx() + (v.root.winfo_width() - ancho) // 2
            y = v.root.winfo_rooty() + (v.root.winfo_height() - alto) // 2
            self.dialogo.geometry(f"+{max(0, x)}+{max(0, y)}")
            self.dialogo.deiconify()
            self.dialogo.wait_visibility()
            self.dialogo.grab_set()
            self.entrada.focus_set()
            v.root.wait_window(self.dialogo)
            return self.resultado
        except tk.TclError:
            if v._cerrada or not self.dialogo.winfo_exists():
                return self.resultado
            raise
        finally:
            v._en_menu = anterior
            v._cola.clear()
            self.fondo = None
            if not v._cerrada:
                if self.dialogo.winfo_exists():
                    self.dialogo.destroy()
                if foco is not None and foco.winfo_exists():
                    foco.focus_set()
                else:
                    v.root.focus_set()
