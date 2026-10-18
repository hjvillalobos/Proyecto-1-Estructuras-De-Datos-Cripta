"""Recorrido entre puertas exclusivamente visual, despues de un movimiento aceptado."""
from dataclasses import replace


def punto_puerta(direccion, ancho, alto):
    base = alto - 150
    return {"N": (ancho / 2, max(215, base - 24)),
            "S": (ancho / 2, alto - 125),
            "E": (ancho - 170, base), "O": (100, base)}[direccion]


class TransicionSalas:
    def __init__(self, vista):
        self.vista = vista
        self.activa = False
        self.origen = self.destino = None

    def cancelar(self):
        self.activa = False
        self.origen = self.destino = None

    def redibujar(self):
        paso = self.vista.escena.animacion.paso
        origen, destino = self.origen, self.destino
        self.activa = False
        if self.mostrar(origen, destino):
            self.vista.escena.animacion.situar(paso)

    def mostrar(self, origen, destino):
        direccion = next((s.direccion for s in origen.salidas if s.destino == destino.sala_id), None)
        if (self.activa or direccion is None or destino.vida <= 0
                or not self.vista._movimiento_activo):
            return False
        self.activa = True
        self.origen, self.destino = origen, destino
        # La sala de salida conserva su geometria, pero los efectos ya avanzaron
        # en el motor: no volver a encender una antorcha que expiro al moverse.
        salida = replace(origen, efectos=list(destino.efectos))
        self.vista._dibujar_sala(salida, salir_hacia=destino.sala_id)
        escena = self.vista.escena
        animacion = escena.animacion
        sprites = [i for i in self.vista.canvas.find_withtag("jugador")
                   if self.vista.canvas.type(i) == "image"]
        if animacion is None or not sprites:
            self.activa = False
            return False
        ancho = max(700, self.vista.canvas.winfo_width())
        alto = max(350, self.vista.canvas.winfo_height())

        def llegar():
            self.cancelar()
            if not self.vista._cerrada:
                self.vista._dibujar_sala(destino)

        animacion.recorrer(sprites[0], punto_puerta(direccion, ancho, alto),
                           pasos=10, al_llegar=llegar)
        return True
