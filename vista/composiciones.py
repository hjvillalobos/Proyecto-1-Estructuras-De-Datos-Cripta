"""Composiciones locales generadas antes de distribuir el juego, sin Tk."""
import hashlib
from pathlib import Path


class ComposicionesPreparadas:
    def __init__(self, recursos):
        self.recursos = Path(recursos)
        self.carpeta = self.recursos / "composiciones"
        self.habilitada = True
        self._firma = None

    def firma(self):
        if self._firma is None:
            huella = hashlib.sha256()
            for nombre in ("jugador", "jugador_acciones", "jugador_beber", "objetos_ilustrados",
                           "itm_coraza_cuero", "itm_daga_oxidada", "itm_antorcha"):
                huella.update(nombre.encode())
                huella.update((self.recursos / (nombre + ".png")).read_bytes())
            pose = self.recursos / "jugador_antorcha.png"
            huella.update(pose.read_bytes() if pose.is_file() else b"sin-pose-antorcha")
            for nombre in ("equipo_visual.py", "recursos_graficos.py", "composiciones.py"):
                huella.update((Path(__file__).parent / nombre).read_bytes().replace(b"\r\n", b"\n"))
            generador = Path(__file__).parent.parent / "utilidades" / "preparar_visuales.py"
            huella.update(generador.read_bytes().replace(b"\r\n", b"\n"))
            self._firma = huella.hexdigest()
        return self._firma

    def _ruta(self, clave):
        return self.carpeta / ("-".join(map(str, clave)) + ".png")

    def leer(self, clave):
        if not self.habilitada:
            return None
        try:
            from PIL import Image
            with Image.open(self._ruta(clave)) as imagen:
                if imagen.info.get("cripta-composicion") != self.firma():
                    return None
                return imagen.convert("RGBA")
        except (OSError, ValueError):
            return None

    def guardar(self, clave, imagen):
        from PIL.PngImagePlugin import PngInfo
        info = PngInfo()
        info.add_text("cripta-composicion", self.firma())
        self.carpeta.mkdir(parents=True, exist_ok=True)
        imagen.save(self._ruta(clave), pnginfo=info, compress_level=6)


def clave_equipo(armadura, arma, antorcha):
    return (int(armadura == "itm_coraza_cuero"), int(arma == "itm_daga_oxidada"), int(bool(antorcha)))
