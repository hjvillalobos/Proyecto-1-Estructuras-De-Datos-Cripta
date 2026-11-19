"""Bruma ambiental de geometría fija, independiente de las salas desconocidas."""
from math import cos, sin, tau
from time import monotonic


class NieblaMapa:
    def __init__(self, canvas, animada=True):
        self.canvas = canvas
        self.animada = animada
        self.zoom = 1
        self.capas = []
        self.tarea = None
        self.inicio = monotonic()
        canvas.bind('<Destroy>', self.detener, add='+')

    def dibujar(self, zoom):
        self.zoom = zoom
        self.capas.clear()
        # Muchas capas de contraste bajo suavizan los bordes sin cubrir el mapa.
        fondo, luz = (17, 28, 28), (43, 62, 50)
        for banco, (x, y, rx, ry) in enumerate(((110, 85, 245, 95),
                                                (600, 150, 275, 110),
                                                (360, 395, 310, 105))):
            for capa in range(24):
                fuerza = (capa / 23) ** 1.4
                color = '#%02x%02x%02x' % tuple(round(a + (b-a)*fuerza) for a, b in zip(fondo, luz))
                item = self.canvas.create_polygon(0, 0, 1, 1, 2, 0, fill=color,
                    outline='', smooth=True, splinesteps=16, tags='niebla')
                self.capas.append((item, banco, capa, x, y, rx, ry))
        self.actualizar()
        if self.animada and self.tarea is None:
            self.tarea = self.canvas.after(50, self.paso)

    def actualizar(self):
        tiempo = monotonic() - self.inicio if self.animada else 0
        for item, banco, capa, x, y, rx, ry in self.capas:
            fase = tiempo * .15 + banco * 2.1
            cx = x + 35 * sin(fase)
            cy = y + 14 * cos(fase * .7)
            escala = 1 - capa * .024
            puntos = []
            for i in range(16):
                angulo = tau * i / 16
                ondulacion = 1 + .12 * sin(angulo * 3 + fase) + .06 * cos(angulo * 5 - fase * .6)
                puntos.extend(((cx + cos(angulo)*rx*escala*ondulacion)*self.zoom,
                               (cy + sin(angulo)*ry*escala*ondulacion)*self.zoom))
            self.canvas.coords(item, *puntos)

    def paso(self):
        self.tarea = None
        self.actualizar()
        self.tarea = self.canvas.after(50, self.paso)

    def detener(self, _evento=None):
        if self.tarea is not None:
            self.canvas.after_cancel(self.tarea)
            self.tarea = None
