"""Tabla de solo lectura; conserva el ranking recibido del controlador."""

import tkinter as tk
from tkinter import ttk

from vista.sonidos import sonorizar_botones
from vista.tema import FONDO, PANEL, TEXTO, TENUE, AMARILLO, VERDE, ROJO, BORDE


class TablaPuntajesVisual:
    def __init__(self, vista, registros):
        self.vista = vista
        self.registros = tuple(registros)
        self.dialogo = tk.Toplevel(vista.root)
        self.dialogo.withdraw()
        self.dialogo.title("CRIPTA - Puntajes")
        self.dialogo.configure(bg=FONDO)
        self.dialogo.transient(vista.root)
        self.dialogo.minsize(640, 360)
        self.dialogo.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.dialogo.bind("<Escape>", self.cerrar)

        cabecera = tk.Canvas(self.dialogo, height=112, bg=FONDO, highlightthickness=0)
        cabecera.pack(fill="x")
        self.fondo = vista.recursos.fondo(960, 112)
        if self.fondo is not None:
            cabecera.create_image(0, 0, image=self.fondo, anchor="nw")
        cabecera.create_rectangle(20, 20, 280, 92, fill=FONDO, outline="")
        cabecera.create_text(34, 43, text="Puntajes", anchor="w", fill=AMARILLO,
                             font=("Georgia", 25, "bold"))
        victorias = sum(r.resultado == "victoria" for r in self.registros)
        cabecera.create_text(34, 76, text=f"Partidas: {len(self.registros)}    Victorias: {victorias}",
                             anchor="w", fill=TEXTO, font=("Segoe UI", 11))
        cuerpo = tk.Frame(self.dialogo, bg=FONDO, padx=20, pady=18)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.rowconfigure(0, weight=1)
        cuerpo.columnconfigure(0, weight=1)

        estilo = ttk.Style(vista.root)
        estilo.configure("Puntajes.Treeview", background=PANEL, fieldbackground=PANEL,
                         foreground=TEXTO, rowheight=36, font=("Segoe UI", 11), borderwidth=0)
        estilo.configure("Puntajes.Treeview.Heading", background=BORDE, foreground=AMARILLO,
                         font=("Segoe UI", 10, "bold"), padding=(8, 10), relief="flat")
        estilo.map("Puntajes.Treeview", background=[("selected", "#345345")],
                   foreground=[("selected", TEXTO)])
        estilo.map("Puntajes.Treeview.Heading", background=[("active", BORDE)])
        columnas = (("puesto", "Pos.", 50), ("nombre", "Jugador", 170),
                    ("cripta", "Cripta", 150), ("resultado", "Resultado", 100),
                    ("tiempo", "Tiempo virtual", 130), ("acciones", "Acciones", 85),
                    ("derrotados", "Derrotados", 95))
        self.tabla = ttk.Treeview(cuerpo, columns=[c[0] for c in columnas], show="headings",
                                 selectmode="browse", style="Puntajes.Treeview", height=9)
        for clave, titulo, ancho in columnas:
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, minwidth=ancho,
                              anchor="w" if clave in ("nombre", "cripta") else "center")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(cuerpo, orient="vertical", command=self.tabla.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(cuerpo, orient="horizontal", command=self.tabla.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tabla.tag_configure("victoria", foreground=VERDE)
        self.tabla.tag_configure("derrota", foreground=ROJO)
        self.tabla.tag_configure("abandono", foreground=TENUE)
        for i, r in enumerate(self.registros):
            self.tabla.insert("", "end", iid=str(i), values=(i + 1, r.nombre, r.cripta_id,
                r.resultado.capitalize(), r.tiempo_final, r.acciones, r.derrotados), tags=(r.resultado,))
        self.vacio = None
        if not self.registros:
            self.vacio = tk.Label(self.tabla, text="Sin partidas registradas", bg=PANEL,
                                  fg=TENUE, font=("Georgia", 17))
            self.vacio.place(relx=.5, rely=.5, anchor="center")
        self.detalle = tk.StringVar(master=self.dialogo, value="")
        tk.Label(cuerpo, textvariable=self.detalle, bg=FONDO, fg=TENUE,
                 anchor="w", font=("Segoe UI", 10), wraplength=580).grid(
                     row=2, column=0, sticky="ew", pady=(14, 0))
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar)
        if self.registros:
            self.tabla.selection_set("0")
            self.tabla.focus("0")
            self._seleccionar()
        self.boton_cerrar = ttk.Button(cuerpo, text="Cerrar", command=self.cerrar)
        self.boton_cerrar.grid(row=3, column=0, sticky="e", pady=(16, 0))
        sonorizar_botones(self.dialogo, vista.sonidos)

    def _seleccionar(self, _evento=None):
        seleccion = self.tabla.selection()
        if seleccion:
            r = self.registros[int(seleccion[0])]
            self.detalle.set(f"{r.nombre}  |  Cripta: {r.cripta_id}  |  Version: {r.cripta_version}")

    def cerrar(self, _evento=None):
        self.dialogo.destroy()
        return "break"

    def mostrar(self):
        v = self.vista
        anterior = getattr(v, "_en_menu", False)
        foco = v.root.focus_get()
        v._en_menu = True
        try:
            ancho = min(960, v.root.winfo_screenwidth() - 60)
            alto = min(620, v.root.winfo_screenheight() - 100)
            x = max(0, v.root.winfo_rootx() + (v.root.winfo_width() - ancho) // 2)
            y = max(0, v.root.winfo_rooty() + (v.root.winfo_height() - alto) // 2)
            self.dialogo.geometry(f"{ancho}x{alto}+{x}+{y}")
            self.dialogo.deiconify()
            self.dialogo.wait_visibility()
            self.dialogo.grab_set()
            self.tabla.focus_set()
            v.root.wait_window(self.dialogo)
        except tk.TclError:
            if not v._cerrada:
                raise
        finally:
            v._en_menu = anterior
            self.fondo = None
            if not v._cerrada:
                if self.dialogo.winfo_exists():
                    self.dialogo.destroy()
                if foco is not None and foco.winfo_exists():
                    foco.focus_set()
