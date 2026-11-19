"""VD-01: elección sobre una proyección, sin referencias al modelo o red."""
import tkinter as tk
from tkinter import ttk
from vista.tema import FONDO, PANEL, TEXTO, TENUE, AMARILLO, ROJO, BORDE, configurar_botones_menu
from vista.sonidos import sonorizar_botones


class DestinoViaje:
    def __init__(self, vista, proyeccion, actual=None):
        self.vista = vista
        self.salas = tuple((r[0], r[2]) for r in proyeccion if r[1] == 2)
        self.resultado = None
        self.dialogo = tk.Toplevel(vista.root)
        self.dialogo.withdraw()
        self.dialogo.title('Viajar a una sala')
        self.dialogo.configure(bg=FONDO)
        self.dialogo.transient(vista.root)
        self.dialogo.resizable(False, False)
        self.dialogo.protocol('WM_DELETE_WINDOW', self.cancelar)
        self.dialogo.bind('<Escape>', self.cancelar)
        self.dialogo.bind('<Return>', self.aceptar)
        configurar_botones_menu(vista.root)
        cabecera = tk.Canvas(self.dialogo, width=570, height=100, bg=FONDO, highlightthickness=0)
        cabecera.pack(fill='x')
        self.fondo = vista.recursos.fondo(570, 100)
        if self.fondo is not None:
            cabecera.create_image(0, 0, image=self.fondo, anchor='nw')
        cabecera.create_rectangle(18, 22, 552, 80, fill=FONDO, outline='')
        cabecera.create_text(285, 51, text='Viajar a una sala', fill=AMARILLO, font=('Georgia', 24))
        cuerpo = tk.Frame(self.dialogo, bg=FONDO, padx=26, pady=18)
        cuerpo.pack(fill='both', expand=True)
        tk.Label(cuerpo, text='Elige un lugar que ya has explorado.', bg=FONDO, fg=TEXTO,
                 font=('Segoe UI', 12)).pack(anchor='w')
        tk.Label(cuerpo, text='El viaje se detiene si aparece peligro o no queda un camino conocido.',
                 bg=FONDO, fg=TENUE, wraplength=510, justify='left', font=('Segoe UI', 10)).pack(anchor='w', pady=(5, 14))
        lista = tk.Frame(cuerpo, bg=PANEL)
        lista.pack(fill='x')
        self.lista = tk.Listbox(lista, height=5, bg=PANEL, fg=TEXTO, selectbackground=AMARILLO,
            selectforeground=FONDO, font=('Segoe UI', 11), exportselection=False,
            relief='flat', highlightthickness=1, highlightbackground=BORDE)
        scroll = ttk.Scrollbar(lista, command=self.lista.yview)
        scroll.pack(side='right', fill='y')
        self.lista.pack(side='left', fill='both', expand=True)
        self.lista.configure(yscrollcommand=scroll.set)
        for identidad, nombre in self.salas:
            self.lista.insert('end', f'Sala {identidad} · {nombre}' + ('  (estás aquí)' if identidad == actual else ''))
        self.lista.bind('<<ListboxSelect>>', self.seleccionar)
        self.detalle = tk.StringVar(master=self.dialogo)
        tk.Label(cuerpo, textvariable=self.detalle, bg=FONDO, fg=TENUE, wraplength=510,
                 justify='left', font=('Segoe UI', 10)).pack(anchor='w', pady=(8, 12))
        tk.Label(cuerpo, text='Número de la sala', bg=FONDO, fg=TEXTO,
                 font=('Segoe UI', 11)).pack(anchor='w')
        self.numero = tk.StringVar(master=self.dialogo)
        self.entrada = tk.Entry(cuerpo, textvariable=self.numero, bg=PANEL, fg=TEXTO,
            insertbackground=AMARILLO, font=('Consolas', 16), relief='flat', highlightthickness=2,
            highlightbackground=BORDE, highlightcolor=AMARILLO)
        self.entrada.pack(fill='x', ipady=8, pady=(5, 0))
        self.error = tk.StringVar(master=self.dialogo)
        tk.Label(cuerpo, textvariable=self.error, bg=FONDO, fg=ROJO, wraplength=510,
                 justify='left', font=('Segoe UI', 10), height=2).pack(fill='x', pady=(5, 8))
        acciones = tk.Frame(cuerpo, bg=FONDO)
        acciones.pack(fill='x')
        self.boton_cancelar = ttk.Button(acciones, text='Cancelar', command=self.cancelar, style='Menu.TButton')
        self.boton_cancelar.pack(side='left', fill='x', expand=True, padx=(0, 12))
        self.boton_cancelar.bind('<Return>', self.cancelar)
        self.boton_viajar = ttk.Button(acciones, text='Viajar', command=self.aceptar, style='Principal.Menu.TButton')
        self.boton_viajar.pack(side='left', fill='x', expand=True)
        if not self.salas:
            self.error.set('Todavía no hay salas exploradas disponibles.')
            self.boton_viajar.configure(state='disabled')
        sonorizar_botones(self.dialogo, vista.sonidos)

    def seleccionar(self, _evento=None):
        indices = self.lista.curselection()
        if indices:
            identidad, nombre = self.salas[indices[0]]
            self.numero.set(str(identidad))
            self.detalle.set(f'Sala {identidad} · {nombre}')
            self.error.set('')

    def aceptar(self, _evento=None):
        texto = self.numero.get().strip()
        if not texto.isascii() or not texto.isdecimal():
            self.error.set('Escribe un número de sala válido o elígelo en la lista.')
            self.entrada.focus_set()
            return 'break'
        # Limitar longitud evita conversiones patológicas sin restringir IDs uint32.
        if len(texto) > 10 or not any(i == int(texto) for i, _ in self.salas):
            self.error.set('Elige una sala explorada de la lista para viajar.')
            return 'break'
        self.resultado = int(texto)
        self.dialogo.destroy()
        return 'break'

    def cancelar(self, _evento=None):
        self.resultado = None
        self.dialogo.destroy()
        return 'break'

    def mostrar(self):
        v = self.vista
        anterior = getattr(v, '_en_menu', False)
        foco = v.root.focus_get()
        v._en_menu = True
        try:
            self.dialogo.update_idletasks()
            x = v.root.winfo_rootx() + max(0, (v.root.winfo_width()-self.dialogo.winfo_reqwidth())//2)
            y = v.root.winfo_rooty() + max(0, (v.root.winfo_height()-self.dialogo.winfo_reqheight())//2)
            self.dialogo.geometry(f'+{x}+{y}')
            self.dialogo.deiconify()
            self.dialogo.grab_set()
            self.entrada.focus_set()
            v.root.wait_window(self.dialogo)
            return self.resultado
        finally:
            v._en_menu = anterior
            if not v._cerrada:
                if self.dialogo.winfo_exists(): self.dialogo.destroy()
                (foco if foco is not None and foco.winfo_exists() else v.root).focus_set()
