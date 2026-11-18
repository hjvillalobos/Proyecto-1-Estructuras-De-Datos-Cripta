import os
from pathlib import Path


class MusicaPartida:
    def __init__(self, root, mezclador=None):
        self.root = root
        if mezclador is None:
            os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
            from pygame import mixer
            mezclador = mixer
        self.mezclador = mezclador
        self.propio = not mezclador.get_init()
        if self.propio:
            mezclador.init(frequency=22050, size=-16, channels=2, buffer=1024)
        try:
            carpeta = Path(__file__).parent / "recursos" / "sonidos"
            self.pistas = [mezclador.Sound(str(carpeta / ("pasillos_" + nombre + ".wav")))
                           for nombre in ("calma", "tension")]
            self.canales = [mezclador.Channel(0), mezclador.Channel(1)]
        except Exception:
            if self.propio:
                mezclador.quit()
            raise
        self.pendiente = None
        self.activa = False
        self.nivel = 0.0
        self.tension = 0.0
        self.objetivo = 0.0

    def actualizar(self, peligro):
        self.objetivo = float(bool(peligro))
        if not self.activa:
            self.activa = True
            self.nivel = 0.0
            self.tension = self.objetivo
            for canal, pista in zip(self.canales, self.pistas):
                canal.set_volume(0)
                canal.play(pista, loops=-1)
        if self.pendiente is None and (self.nivel < 1 or self.tension != self.objetivo):
            self._mezclar()

    def _mezclar(self):
        self.pendiente = None
        self.nivel = min(1.0, self.nivel + .04)
        diferencia = self.objetivo - self.tension
        self.tension += max(-.04, min(.04, diferencia))
        self.canales[0].set_volume(.6 * self.nivel * (1 - self.tension))
        self.canales[1].set_volume(.6 * self.nivel * self.tension)
        if self.nivel < 1 or self.tension != self.objetivo:
            self.pendiente = self.root.after(50, self._mezclar)

    def detener(self):
        if self.pendiente is not None:
            self.root.after_cancel(self.pendiente)
            self.pendiente = None
        for canal in self.canales:
            canal.stop()
        self.activa = False

    def cerrar(self):
        self.detener()
        self.pistas.clear()
        if self.propio:
            self.mezclador.quit()
