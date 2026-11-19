"""Consulta del pasado sin cambiar el estado de la partida."""
import tkinter as tk
from tkinter import simpledialog, ttk

from vista.tema import FONDO, PANEL, TEXTO, TENUE, AMARILLO, ROJO, BORDE


class ConsultaHistoria(simpledialog.Dialog):
    def __init__(self, padre):
        super().__init__(padre, 'Historia de tu partida')

    def body(self, cuerpo):
        self.configure(bg=FONDO)
        cuerpo.configure(bg=FONDO, padx=22, pady=18)
        tk.Label(cuerpo, text='Historia de tu partida', bg=FONDO, fg=AMARILLO,
                 font=('Georgia', 23)).pack(anchor='w')
        tk.Label(cuerpo, text='Consulta cómo estabas en un momento anterior.',
                 bg=FONDO, fg=TEXTO, font=('Segoe UI', 12)).pack(anchor='w', pady=(10, 5))
        tk.Label(cuerpo, text='Verás la sala, tu vida, el inventario y el mapa que conocías.\n'
                 'Esta consulta no mueve al personaje ni cambia tu partida.',
                 bg=FONDO, fg=TENUE, justify='left', font=('Segoe UI', 10)).pack(anchor='w')
        opciones = tk.Frame(cuerpo, bg=PANEL, padx=14, pady=12)
        opciones.pack(fill='x', pady=(20, 14))
        self.modo = tk.StringVar(self, value='tiempo')
        for etiqueta, valor in (('Por tiempo del reloj', 'tiempo'), ('Por número de acción', 'accion')):
            tk.Radiobutton(opciones, text=etiqueta, value=valor, variable=self.modo,
                           command=self.actualizar, bg=PANEL, fg=TEXTO,
                           selectcolor=FONDO, activebackground=PANEL, activeforeground=AMARILLO,
                           font=('Segoe UI', 11), anchor='w').pack(fill='x')
        self.etiqueta = tk.Label(cuerpo, bg=FONDO, fg=TEXTO, font=('Segoe UI', 11))
        self.etiqueta.pack(anchor='w')
        self.numero = tk.StringVar(self)
        entrada = tk.Entry(cuerpo, textvariable=self.numero, bg=PANEL, fg=TEXTO,
                           insertbackground=AMARILLO, relief='flat', font=('Consolas', 17),
                           highlightthickness=1, highlightbackground=BORDE, highlightcolor=AMARILLO)
        entrada.pack(fill='x', ipady=9, pady=(6, 5))
        self.ejemplo = tk.Label(cuerpo, bg=FONDO, fg=TENUE, font=('Segoe UI', 10))
        self.ejemplo.pack(anchor='w')
        self.error = tk.Label(cuerpo, text='', bg=FONDO, fg=ROJO, font=('Segoe UI', 10))
        self.error.pack(anchor='w', pady=(10, 0))
        self.actualizar()
        return entrada

    def actualizar(self):
        tiempo = self.modo.get() == 'tiempo'
        self.etiqueta.configure(text='Tiempo del reloj que quieres consultar' if tiempo else 'Número de acción que quieres consultar')
        self.ejemplo.configure(text='Ejemplo: 150. Usa las mismas unidades del reloj de la partida.' if tiempo else 'Ejemplo: 3 para consultar el estado justo antes de la tercera acción.')

    def buttonbox(self):
        barra = tk.Frame(self, bg=FONDO, padx=27, pady=18)
        barra.pack(fill='x')
        ttk.Button(barra, text='Cancelar', command=self.cancel).pack(side='left')
        ttk.Button(barra, text='Consultar historia', command=self.ok).pack(side='right')
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.cancel)

    def validate(self):
        texto = self.numero.get().strip()
        if not texto.isascii() or not texto.isdecimal() or len(texto) > 18:
            self.error.configure(text='Escribe un número entero igual o mayor que cero.')
            return False
        if self.modo.get() == 'accion' and int(texto) < 1:
            self.error.configure(text='Las acciones se numeran desde 1.')
            return False
        return True

    def apply(self):
        self.result = ('#' if self.modo.get() == 'accion' else '') + self.numero.get().strip()
