import math
from time import perf_counter

PASOS_CARRERA = 16


class AnimacionEscena:
    """Tiempo visual local: nunca consulta ni modifica la simulacion."""

    def __init__(self, root, canvas):
        self.root, self.canvas = root, canvas
        self.pendiente = None
        self.actores = []
        self.paso = 0
        self.secuencias = []
        self.particulas = []
        self.anclajes = []
        self.trayecto = None
        self._al_llegar = None
        self.decoraciones = []
        self._siguiente_tic = None

    def decorar(self, decoracion):
        self.decoraciones.append(decoracion)
        decoracion.actualizar(self.paso)

    def recorrer(self, actor, destino, pasos=20, al_llegar=None):
        self.trayecto = (actor, tuple(self.canvas.coords(actor)), tuple(destino), pasos)
        self._al_llegar = al_llegar
        self.paso = 0

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
        origen = tuple(self.canvas.coords(identificador))
        self.actores.append((identificador, origen,
                             fase, entrada, golpe, desplazamiento, carrera, ataque))
        if entrada:
            progreso = min(1, self.paso / (PASOS_CARRERA if carrera else 16))
            restante = 1 - progreso if carrera else 1 - progreso * progreso * (3 - 2 * progreso)
            self.canvas.coords(identificador, *[
                valor + desplazamiento[i % 2] * restante for i, valor in enumerate(origen)])

    def particula(self, identificador, duracion=20, desplazamiento=(-20, -8)):
        self.particulas.append((identificador, tuple(self.canvas.coords(identificador)),
                                duracion, desplazamiento))

    def anclar(self, identificador, actor, reposo, cuadros=(), duracion=None, ocultar_hasta=0):
        self.anclajes.append((identificador, actor, reposo, tuple(cuadros), duracion, ocultar_hasta))
        self._actualizar_anclajes()

    def _actualizar_anclajes(self):
        for identificador, actor, reposo, cuadros, duracion, ocultar_hasta in self.anclajes:
            if not self.canvas.type(identificador):
                continue
            if duracion is not None and self.paso >= duracion:
                self.canvas.delete(identificador)
                continue
            self.canvas.itemconfig(identificador, state="hidden" if self.paso < ocultar_hasta else "normal")
            posicion = self.canvas.coords(actor)
            if len(posicion) < 2:
                continue
            desplazamiento = reposo
            secuencia = next((s for s in self.secuencias if s[0] == actor), None)
            if secuencia is not None and cuadros:
                _, fotogramas, _, mantener, velocidad, limite, repetir = secuencia
                fin = limite if limite is not None else len(fotogramas) * velocidad
                if self.paso < fin or mantener:
                    indice = self.paso // velocidad
                    indice = indice % len(cuadros) if repetir else min(indice, len(cuadros) - 1)
                    desplazamiento = cuadros[indice]
            self.canvas.coords(identificador, *[
                posicion[i % 2] + valor for i, valor in enumerate(desplazamiento)])

    def iniciar(self):
        if self.pendiente is None and (self.actores or self.particulas):
            ahora = perf_counter()
            if self._siguiente_tic is None or self._siguiente_tic <= ahora:
                self._siguiente_tic = ahora + .020
            demora = max(1, round((self._siguiente_tic - ahora) * 1000))
            self.pendiente = self.root.after(demora, self._avanzar)

    def situar(self, paso):
        """Restaura el dibujo sin avanzar tiempo ni programar otro callback."""
        self.paso = paso
        self._actualizar_pose()

    def _actualizar_pose(self):
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
            progreso = min(1, self.paso / (PASOS_CARRERA if carrera else 16))
            restante = 1 - progreso if carrera else 1 - progreso * progreso * (3 - 2 * progreso)
            dx = desplazamiento[0] * restante if entrada else 0
            dy = desplazamiento[1] * restante if entrada else 0
            if ataque and self.paso < 18:
                dx += math.sin(math.pi * self.paso / 18) * 24
            if golpe and self.paso < 10:
                dx += math.sin(self.paso * 2) * 5 * (1 - self.paso / 10)
            muerto = any(s[0] == identificador and s[3] for s in self.secuencias)
            if not muerto:
                dy += (math.sin(self.paso * .8) * .75 if carrera and progreso < 1
                       else math.sin(self.paso * .055 + fase) * 1.5)
            posicion = [v + (dx if i % 2 == 0 else dy) for i, v in enumerate(origen)]
            if self.trayecto is not None and self.trayecto[0] == identificador:
                _, inicio, destino, pasos = self.trayecto
                p = min(1, self.paso / pasos)
                avance = p
                posicion = [inicio[i] + (destino[i] - inicio[i]) * avance for i in range(2)]
                if p < 1:
                    posicion[1] += math.sin(self.paso * .8) * .5
            self.canvas.coords(identificador, *posicion)
        self._actualizar_anclajes()
        for decoracion in self.decoraciones:
            decoracion.actualizar(self.paso)

    def _avanzar(self):
        self.pendiente = None
        if self._siguiente_tic is not None:
            self._siguiente_tic += .020
        self.paso += 1
        self._actualizar_pose()
        for identificador, origen, duracion, desplazamiento in self.particulas:
            if self.paso >= duracion:
                self.canvas.delete(identificador)
            elif self.canvas.type(identificador):
                progreso = self.paso / duracion
                self.canvas.coords(identificador, *[
                    v + desplazamiento[i % 2] * progreso for i, v in enumerate(origen)])
        if self.trayecto is not None and self.paso >= self.trayecto[3] and self._al_llegar is not None:
            al_llegar = self._al_llegar
            self._al_llegar = None
            al_llegar()
            return
        self.iniciar()

    def detener(self):
        if self.pendiente is not None:
            self.root.after_cancel(self.pendiente)
            self.pendiente = None
        self._siguiente_tic = None
        for identificador, origen, *_ in self.actores:
            if self.canvas.type(identificador):
                self.canvas.coords(identificador, *origen)
        self.actores.clear()
        self.secuencias.clear()
        for identificador, *_ in self.particulas:
            self.canvas.delete(identificador)
        self.particulas.clear()
        self.anclajes.clear()
        for decoracion in self.decoraciones:
            decoracion.detener()
        self.decoraciones.clear()
        self.trayecto = None
        self._al_llegar = None
        self.paso = 0
