FONDO = "#101718"
PANEL = "#192324"
SALA = "#25302c"
TEXTO = "#eff3e9"
TENUE = "#b1bdb6"
VERDE = "#75d9b1"
ROJO = "#ff9292"
AMARILLO = "#f0cf88"
AZUL = "#98c9ef"
NARANJA = "#e6ac73"
MORADO = "#d9b4ee"
PIEDRA = "#304039"
BORDE = "#42544d"


def configurar_botones_menu(root):
    from tkinter import ttk
    estilo = ttk.Style(root)
    estilo.configure("Menu.TButton", font=("Segoe UI", 12), padding=(12, 9),
                     background=PIEDRA, foreground=TEXTO, bordercolor=BORDE)
    for nombre in ("Menu.TButton", "Principal.Menu.TButton"):
        estilo.map(nombre,
                   background=[("disabled", PANEL), ("focus", NARANJA), ("!focus", PIEDRA)],
                   foreground=[("disabled", TENUE), ("focus", FONDO), ("!focus", TEXTO)],
                   bordercolor=[("focus", NARANJA), ("!focus", BORDE)])
