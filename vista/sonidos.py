"""Efectos breves locales; el dispositivo nunca controla la simulacion."""
import math
import os
from array import array
from pathlib import Path
from tempfile import TemporaryDirectory
import wave

try:
    import winsound
except ImportError:
    winsound = None


_NOTAS = {
    "boton": ((391.995, .045), (523.251, .045)),
    "inicio": ((174.614, .55), (261.626, .45), (207.652, .6), (329.628, .5),
               (0, .3), (311.127, .5), (246.942, .5), (195.998, .55),
               (174.614, .65), (130.813, .8)),
    "mover": ((82, .065), (0, .055), (65, .075)),
    "abrir": ((95, .13), (73, .18), (55, .12)),
    "atacar": ((440, .055), (110, .11)),
    "recoger": ((523.251, .1), (622.254, .16)),
    "equipar": ((196, .07), (294, .12)),
    "usar": ((261.626, .1), (391.995, .17)),
    "soltar": ((147, .07), (73, .09)),
    "retroceso": ((391.995, .12), (293.665, .12), (207.652, .2)),
    "victoria": ((261.626, .18), (311.127, .18), (391.995, .32)),
    "derrota": ((195.998, .25), (155.563, .3), (130.813, .45)),
}


def sonorizar_botones(contenedor, sonidos):
    """Envuelve comandos reales: tambien funciona al activar con el teclado."""
    from tkinter import ttk

    for widget in contenedor.winfo_children():
        if isinstance(widget, ttk.Button) and not getattr(widget, "_sonorizado", False):
            comando = widget.cget("command")
            if comando:
                def activar(boton=widget, original=comando):
                    sonidos.reproducir("boton")
                    return boton.tk.call(*boton.tk.splitlist(original))
                widget.configure(command=activar)
                widget._sonorizado = True
        sonorizar_botones(widget, sonidos)


class Sonidos:
    def __init__(self, reproductor=winsound):
        self.reproductor = reproductor
        self.disponible = reproductor is not None
        self.activo = self.disponible and os.environ.get("CRIPTA_SIN_AUDIO") != "1"
        self._carpeta = None
        self._reprodujo = False
        self._cerrado = False

    def habilitar(self, activo):
        self.activo = bool(activo) and self.disponible and not self._cerrado
        if not self.activo:
            self._detener()

    def reproducir(self, efecto):
        if not self.activo or self._cerrado or efecto not in _NOTAS:
            return
        try:
            if self._carpeta is None:
                self._carpeta = TemporaryDirectory(prefix="cripta-audio-")
            ruta = Path(self._carpeta.name) / (efecto + ".wav")
            if not ruta.exists():
                self._crear_efecto(ruta, _NOTAS[efecto], efecto)
            self.reproductor.PlaySound(str(ruta), self.reproductor.SND_FILENAME
                                       | self.reproductor.SND_ASYNC | self.reproductor.SND_NODEFAULT)
            self._reprodujo = True
        except (OSError, RuntimeError, ValueError):
            self.activo = False
            self._detener()

    @staticmethod
    def _crear_efecto(ruta, notas, efecto=""):
        frecuencia = 22050
        ambiente = efecto in ("inicio", "derrota")
        campana = efecto in ("boton", "inicio", "recoger", "usar", "retroceso", "victoria", "derrota")
        senal = []
        ruido, filtrado = 12345, 0.0
        for tono, duracion in notas:
            total = int(frecuencia * duracion)
            for i in range(total):
                t = i / frecuencia
                envolvente = min(1, i / 220, (total - 1 - i) / 330)
                fase = 2 * math.pi * tono * t
                if campana:
                    valor = (math.sin(fase) * math.exp(-4 * t)
                             + .32 * math.sin(fase * 2.76) * math.exp(-7 * t)
                             + .12 * math.sin(fase * 5.4) * math.exp(-12 * t)) if tono else 0
                else:
                    # Ruido local determinista: nunca usa el azar del modelo.
                    ruido = (1664525 * ruido + 1013904223) & 0xffffffff
                    blanco = ruido / 2147483648 - 1
                    filtrado = .82 * filtrado + .18 * blanco
                    golpe = math.sin(fase * (1 - min(.6, t * 2)))
                    valor = (.6 * golpe + (1.6 if efecto == "atacar" else .8) * filtrado)
                    valor = valor * math.exp(-18 * t) if tono else 0
                if ambiente:
                    tiempo = len(senal) / frecuencia
                    valor *= .45
                    valor += .12 * math.sin(2 * math.pi * 55 * tiempo)
                    valor += .07 * math.sin(2 * math.pi * 82.407 * tiempo + .2 * math.sin(tiempo * 2))
                senal.append(valor * envolvente)
        cola = .08 if efecto == "boton" else .7 if campana else .12
        senal.extend([0.0] * int(frecuencia * cola))
        mezcla = senal.copy()
        if campana:
            for segundos, nivel in ((.17, .23), (.33, .12), (.51, .06)):
                demora = int(segundos * frecuencia)
                for i in range(demora, len(mezcla)):
                    mezcla[i] += senal[i - demora] * nivel
        muestras = array("h", (int(max(-1, min(1, v)) * 10500) for v in mezcla))
        import sys
        if sys.byteorder != "little":
            muestras.byteswap()
        with wave.open(str(ruta), "wb") as archivo:
            archivo.setnchannels(1)
            archivo.setsampwidth(2)
            archivo.setframerate(frecuencia)
            archivo.writeframes(muestras.tobytes())

    def _detener(self):
        if self._reprodujo:
            try:
                self.reproductor.PlaySound(None, 0)
            except (OSError, RuntimeError):
                pass
            self._reprodujo = False

    def cerrar(self):
        self.habilitar(False)
        self._cerrado = True
        if self._carpeta is not None:
            try:
                self._carpeta.cleanup()
            except OSError:
                pass
            self._carpeta = None
