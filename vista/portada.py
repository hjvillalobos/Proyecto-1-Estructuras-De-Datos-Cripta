import time
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk


class Portada:
    def __init__(self, root):
        self.root = root
        self.fin = tk.BooleanVar(master=root, value=False)
        self.iniciar = False
        self.pendiente = None
        self.redimension = None
        self.imagenes = []
        self.fuegos = []
        self.transicion = None
        self.imagen_transicion = None
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Misc.lift(self.canvas)
        self.canvas.bind("<Configure>", self.programar_dibujo)
        self.canvas.bind("<KeyPress>", lambda evento: "break")
        self.canvas.bind("<KeyRelease-Return>", self.entrar)
        self.canvas.bind("<ButtonRelease-1>", self.entrar)
        self.canvas.bind("<Destroy>", self.destruir)
        ruta = Path(__file__).parent / "recursos" / "portada"
        self.originales = []
        for nombre in ["fondo", "texto"] + [f"fuego{i}" for i in range(8)]:
            with Image.open(ruta / (nombre + ".png")) as imagen:
                self.originales.append(imagen.convert("RGBA"))
        self.comienzo = time.monotonic()

    def programar_dibujo(self, evento=None):
        if self.transicion is not None:
            return
        if self.redimension is not None:
            self.root.after_cancel(self.redimension)
        self.redimension = self.root.after(80, self.dibujar)

    def dibujar(self):
        self.redimension = None
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        escala = min(ancho / 640, alto / 360)
        if escala <= 0:
            return
        self.imagenes = [ImageTk.PhotoImage(imagen.resize(
            (max(1, round(imagen.width * escala)), max(1, round(imagen.height * escala))),
            Image.Resampling.NEAREST), master=self.root) for imagen in self.originales]
        x = (ancho - round(640 * escala)) // 2
        y = (alto - round(360 * escala)) // 2
        self.canvas.delete("all")
        self.canvas.create_image(x, y, anchor="nw", image=self.imagenes[0])
        self.fuegos = [self.canvas.create_image(x + round(pos * escala),
            y + round(141 * escala), anchor="nw", image=self.imagenes[2])
            for pos in (45, 415)]
        self.texto = self.canvas.create_image(x, y + round(248 * escala),
            anchor="nw", image=self.imagenes[1])
        if self.pendiente is None:
            self.animar()

    def animar(self):
        transcurrido = time.monotonic() - self.comienzo
        cuadro = int(transcurrido * 8) % 8
        for indice, fuego in enumerate(self.fuegos):
            self.canvas.itemconfigure(fuego, image=self.imagenes[2 + (cuadro + indice * 3) % 8])
        self.canvas.itemconfigure(self.texto, state="normal" if transcurrido % 1.4 < .9 else "hidden")
        self.pendiente = self.root.after(125, self.animar)

    def entrar(self, evento=None):
        if self.transicion is not None:
            return "break"
        self.detener()
        if not self.imagenes:
            self.dibujar()
        self.detener()
        self.transicion = self.originales[0].copy()
        cuadro = int((time.monotonic() - self.comienzo) * 8) % 8
        for indice, x in enumerate((45, 415)):
            self.transicion.alpha_composite(self.originales[2 + (cuadro + indice * 3) % 8], (x, 141))
        if self.canvas.itemcget(self.texto, "state") != "hidden":
            self.transicion.alpha_composite(self.originales[1], (0, 248))
        self.fundir(0)
        return "break"

    def fundir(self, paso):
        if paso == 14:
            self.iniciar = True
            self.fin.set(True)
            self.pendiente = None
            return
        ancho, alto = self.canvas.winfo_width(), self.canvas.winfo_height()
        escala = min(ancho / 640, alto / 360)
        tamano = (max(1, round(640 * escala)), max(1, round(360 * escala)))
        with Image.new("RGBA", (640, 360), "black") as negro:
            with Image.blend(self.transicion, negro, min(1, paso / 12)) as cuadro:
                self.imagen_transicion = ImageTk.PhotoImage(
                    cuadro.resize(tamano, Image.Resampling.NEAREST), master=self.root)
        self.canvas.delete("all")
        self.canvas.create_image(ancho / 2, alto / 2, image=self.imagen_transicion)
        self.pendiente = self.root.after(50, self.fundir, paso + 1)

    def salir(self):
        self.detener()
        self.iniciar = False
        self.fin.set(True)

    def destruir(self, evento):
        if evento.widget is self.canvas:
            self.detener()
            self.fin.set(True)

    def detener(self):
        for identificador in (self.pendiente, self.redimension):
            if identificador is not None:
                self.root.after_cancel(identificador)
        self.pendiente = None
        self.redimension = None

    def mostrar(self):
        anterior = self.root.protocol("WM_DELETE_WINDOW")
        self.root.protocol("WM_DELETE_WINDOW", self.salir)
        try:
            self.root.update_idletasks()
            self.canvas.focus_set()
            self.root.wait_variable(self.fin)
            return self.iniciar
        finally:
            self.detener()
            self.canvas.destroy()
            self.imagenes.clear()
            self.imagen_transicion = None
            if self.transicion is not None:
                self.transicion.close()
            for imagen in self.originales:
                imagen.close()
            self.originales.clear()
            self.root.protocol("WM_DELETE_WINDOW", anterior)
