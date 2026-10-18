"""Hojas de paso decorativas: no cambian el estado logico de ninguna puerta."""
from vista.tema import FONDO, BORDE, PIEDRA, TENUE


class PuertaVisual:
    def __init__(self, canvas, posicion, entrando=False):
        self.canvas = canvas
        self.x, self.pie = posicion
        self.alto = min(160, max(100, self.pie - 70))
        self.entrando = entrando
        x, y, h = self.x, self.pie, self.alto
        self.marco = canvas.create_polygon(x - 45, y, x - 45, y - h + 20,
            x - 28, y - h, x + 28, y - h, x + 45, y - h + 20, x + 45, y,
            fill=FONDO, outline=BORDE, width=3, tags=("puerta_visual",))
        self.izquierda = canvas.create_rectangle(x - 40, y - h + 23, x, y - 2,
            fill=PIEDRA, outline=TENUE, tags=("puerta_visual",))
        self.derecha = canvas.create_rectangle(x, y - h + 23, x + 40, y - 2,
            fill=PIEDRA, outline=TENUE, tags=("puerta_visual",))
        self.ids = [self.marco, self.izquierda, self.derecha]

    def actualizar(self, paso):
        if not self.ids:
            return
        if self.entrando and paso >= 12:
            self.detener()
            return
        visible = self.entrando or paso >= 3
        for item in self.ids:
            self.canvas.itemconfig(item, state="normal" if visible else "hidden")
        apertura = (1 - min(1, max(0, (paso - 6) / 4)) if self.entrando
                    else min(1, max(0, (paso - 3) / 4)))
        ancho = 2 + 38 * (1 - apertura)
        x, y, h = self.x, self.pie, self.alto
        self.canvas.coords(self.izquierda, x - 40, y - h + 23, x - 40 + ancho, y - 2)
        self.canvas.coords(self.derecha, x + 40 - ancho, y - h + 23, x + 40, y - 2)

    def detener(self):
        for item in self.ids:
            self.canvas.delete(item)
        self.ids.clear()
