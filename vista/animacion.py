import math


class AnimacionEscena:
    """Tiempo visual local: nunca consulta ni modifica la simulacion."""

    def __init__(self, root, canvas):
        self.root, self.canvas = root, canvas
        self.pendiente = None
        self.actores = []
        self.paso = 0
        self.secuencias = []
        self.particulas = []

    def secuencia(self, identificador, fotogramas, reposo=None, mantener=False,
                  pasos_por_cuadro=3, duracion=None, repetir=False):
        if fotogramas:
            self.secuencias.append((identificador, tuple(fotogramas), reposo, mantener,
                                    pasos_por_cuadro, duracion, repetir))
            fin = duracion if duracion is not None else len(fotogramas) * pasos_por_cuadro
            indice = self.paso // pasos_por_cuadro
            imagen = (fotogramas[indice % len(fotogramas)] if repetir
                      else fotogramas[min(indice, len(fotogramas) - 1)]) if self.paso < fin else (
                          fotogramas[-1] if mantener else reposo)
            if imagen is not None:
                self.canvas.itemconfig(identificador, image=imagen)

    def agregar(self, identificador, fase=0, entrada=False, golpe=False,
                desplazamiento=(-18, 0), carrera=False, ataque=False):
        self.actores.append((identificador, tuple(self.canvas.coords(identificador)),
                             fase, entrada, golpe, desplazamiento, carrera, ataque))

    def particula(self, identificador, duracion=20, desplazamiento=(-20, -8)):
        self.particulas.append((identificador, tuple(self.canvas.coords(identificador)),
                                duracion, desplazamiento))

    def iniciar(self):
        if self.pendiente is None and (self.actores or self.particulas):
            self.pendiente = self.root.after(20, self._avanzar)

    def _avanzar(self):
        self.pendiente = None
        self.paso += 1
        for identificador, fotogramas, reposo, mantener, velocidad, duracion, repetir in self.secuencias:
            indice = self.paso // velocidad
            fin = duracion if duracion is not None else len(fotogramas) * velocidad
            if self.paso < fin:
                imagen = fotogramas[indice % len(fotogramas)] if repetir else fotogramas[min(indice, len(fotogramas) - 1)]
            else:
                imagen = fotogramas[-1] if mantener else reposo
            if imagen is not None and self.canvas.type(identificador):
                self.canvas.itemconfig(identificador, image=imagen)
        for identificador, origen, fase, entrada, golpe, desplazamiento, carrera, ataque in self.actores:
            if not self.canvas.type(identificador):
                continue
            progreso = min(1, self.paso / (32 if carrera else 16))
            restante = 1 - progreso * progreso * (3 - 2 * progreso)
            dx = desplazamiento[0] * restante if entrada else 0
            dy = desplazamiento[1] * restante if entrada else 0
            if ataque and self.paso < 18:
                dx += math.sin(math.pi * self.paso / 18) * 24
            if golpe and self.paso < 10:
                dx += math.sin(self.paso * 2) * 5 * (1 - self.paso / 10)
            muerto = any(s[0] == identificador and s[3] for s in self.secuencias)
            if not muerto:
                dy += (math.sin(self.paso * .8) * 3 * restante if carrera and progreso < 1
                       else math.sin(self.paso * .055 + fase) * 1.5)
            posicion = [v + (dx if i % 2 == 0 else dy) for i, v in enumerate(origen)]
            self.canvas.coords(identificador, *posicion)
        for identificador, origen, duracion, desplazamiento in self.particulas:
            if self.paso >= duracion:
                self.canvas.delete(identificador)
            elif self.canvas.type(identificador):
                progreso = self.paso / duracion
                self.canvas.coords(identificador, *[
                    v + desplazamiento[i % 2] * progreso for i, v in enumerate(origen)])
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
        for identificador, *_ in self.particulas:
            self.canvas.delete(identificador)
        self.particulas.clear()
        self.paso = 0
