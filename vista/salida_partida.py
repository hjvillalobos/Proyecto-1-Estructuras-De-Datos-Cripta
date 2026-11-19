"""UX-01: elección local; no guarda, reinicia ni modifica la simulación."""
import tkinter as tk
from tkinter import ttk
from vista.tema import FONDO, TEXTO, AMARILLO, configurar_botones_menu
from vista.sonidos import sonorizar_botones


class SalidaPartida:
    def __init__(self, vista):
        self.vista = vista
        self.resultado = 'cancelar'
        self.dialogo = tk.Toplevel(vista.root)
        self.dialogo.withdraw()
        self.dialogo.title('CRIPTA · Opciones de partida')
        self.dialogo.configure(bg=FONDO)
        self.dialogo.transient(vista.root)
        self.dialogo.resizable(False, False)
        self.dialogo.protocol('WM_DELETE_WINDOW', self.cancelar)
        self.dialogo.bind('<Escape>', self.cancelar)
        configurar_botones_menu(vista.root)
        cuerpo = tk.Frame(self.dialogo, bg=FONDO, padx=26, pady=24)
        cuerpo.pack(fill='both', expand=True)
        tk.Label(cuerpo, text='¿Qué quieres hacer?', bg=FONDO, fg=AMARILLO,
                 font=('Georgia', 23)).pack(pady=(0, 12))
        tk.Label(cuerpo, text='El progreso sin guardar se perderá al reiniciar o salir.\n'
                 'Tus archivos de guardado se conservan.', bg=FONDO, fg=TEXTO,
                 font=('Segoe UI', 11), justify='left').pack(pady=(0, 18))
        self.botones = {}
        for texto, accion in (('Continuar jugando', 'cancelar'), ('Reiniciar esta cripta', 'reiniciar'),
                              ('Volver al menú principal', 'menu'), ('Cerrar el juego', 'terminar')):
            boton = ttk.Button(cuerpo, text=texto, command=lambda a=accion: self.elegir(a),
                               style='Principal.Menu.TButton' if accion == 'cancelar' else 'Menu.TButton')
            boton.pack(fill='x', pady=4)
            self.botones[accion] = boton
        sonorizar_botones(self.dialogo, vista.sonidos)

    def elegir(self, accion):
        self.resultado = accion
        self.dialogo.destroy()

    def cancelar(self, _evento=None):
        self.elegir('cancelar')
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
            self.botones['cancelar'].focus_set()
            v.root.wait_window(self.dialogo)
            return self.resultado
        finally:
            v._en_menu = anterior
            if not v._cerrada:
                if self.dialogo.winfo_exists():
                    self.dialogo.destroy()
                (foco if foco is not None and foco.winfo_exists() else v.root).focus_set()
