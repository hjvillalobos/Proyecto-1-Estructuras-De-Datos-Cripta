import math


class AnimacionEscena:
    """Tiempo visual local: nunca consulta ni modifica la simulacion."""

    def __init__(self, root, canvas):
        self.root, self.canvas = root, canvas
        self.pendiente = None
        self.actores = []
        self.paso = 0
        self.secuencias = []

    def secuencia(self, identificador, fotogramas, reposo=None, mantener=False):
        if fotogramas:
            self.secuencias.append((identificador, tuple(fotogramas), reposo, mantener))
            self.canvas.itemconfig(identificador, image=fotogramas[0])

    def agregar(self, identificador, fase=0, entrada=False, golpe=False):
        self.actores.append((identificador, tuple(self.canvas.coords(identificador)), fase, entrada, golpe))

    def iniciar(self):
        if self.pendiente is None and self.actores:
            self.pendiente = self.root.after(40, self._avanzar)

    def _avanzar(self):
        self.pendiente = None
        self.paso += 1
        for identificador, fotogramas, reposo, mantener in self.secuencias:
            indice = self.paso // 3
            imagen = fotogramas[min(indice, len(fotogramas) - 1)] if indice < len(fotogramas) or mantener else reposo
            if imagen is not None and self.canvas.type(identificador):
                self.canvas.itemconfig(identificador, image=imagen)
        for identificador, origen, fase, entrada, golpe in self.actores:
            if not self.canvas.type(identificador):
                continue
            dx = -18 * max(0, 1 - self.paso / 8) if entrada else 0
            if golpe and self.paso < 10:
                dx += math.sin(self.paso * 2) * 5 * (1 - self.paso / 10)
            muerto = any(i == identificador and mantener for i, _, _, mantener in self.secuencias)
            dy = 0 if muerto else math.sin(self.paso * .11 + fase) * 1.5
            posicion = [v + (dx if i % 2 == 0 else dy) for i, v in enumerate(origen)]
            self.canvas.coords(identificador, *posicion)
        self.iniciar()

    def detener(self):
        if self.pendiente is not None:
            self.root.after_cancel(self.pendiente)
            self.pendiente = None
        for identificador, origen, *_ in self.actores:
            if self.canvas.type(identificador):
                self.canvas.coords(identificador, *origen)
        self.actores.clear()
        self.secuencias.clear()
        self.paso = 0
