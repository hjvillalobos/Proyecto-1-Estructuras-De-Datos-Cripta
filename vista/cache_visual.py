"""Copias PNG regenerables de la presentacion; ajenas al catalogo y al motor."""

import hashlib
import os
from pathlib import Path
import tempfile


class CacheVisual:
    LIMITE = 128

    def __init__(self, recursos, carpeta=None):
        self.recursos = Path(recursos)
        self.carpeta = Path(carpeta) if carpeta else Path(tempfile.gettempdir()) / "cripta-visuales"
        self._firma = None

    def _firma_actual(self):
        if self._firma is None:
            partes = [str(self.recursos.resolve())]
            for nombre in ("jugador", "jugador_antorcha", "jugador_acciones", "jugador_beber", "itm_coraza_cuero",
                           "objetos_ilustrados", "itm_daga_oxidada", "itm_antorcha",
                           "fondo_cripta_ilustrado", "fondo_ladrillos"):
                ruta = self.recursos / (nombre + ".png")
                try:
                    datos = ruta.stat()
                    partes.append((nombre, datos.st_size, datos.st_mtime_ns))
                except OSError:
                    partes.append((nombre, None))
            for nombre in ("cache_visual.py", "recursos_graficos.py", "equipo_visual.py"):
                partes.append((Path(__file__).parent / nombre).read_bytes())
            self._firma = hashlib.sha256(repr(partes).encode("utf-8")).hexdigest()
        return self._firma

    def _ruta(self, clave):
        nombre = hashlib.sha256(repr(clave).encode("utf-8")).hexdigest()
        return self.carpeta / (nombre + ".png")

    def leer(self, clave):
        try:
            from PIL import Image
            with Image.open(self._ruta(clave)) as imagen:
                if imagen.info.get("cripta-firma") != self._firma_actual():
                    return None
                return imagen.convert("RGBA")
        except (OSError, ValueError):
            return None

    def guardar(self, clave, imagen):
        temporal = None
        try:
            from PIL.PngImagePlugin import PngInfo
            info = PngInfo()
            info.add_text("cripta-firma", self._firma_actual())
            self.carpeta.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=self.carpeta, suffix=".tmp", delete=False) as archivo:
                temporal = Path(archivo.name)
            imagen.save(temporal, format="PNG", pnginfo=info, compress_level=1)
            os.replace(temporal, self._ruta(clave))
            with os.scandir(self.carpeta) as entradas:
                archivos = [entrada for entrada in entradas if entrada.name.endswith(".png")]
            while len(archivos) > self.LIMITE:
                antiguo = min(archivos, key=lambda entrada: entrada.stat().st_mtime_ns)
                Path(antiguo.path).unlink()
                archivos.remove(antiguo)
        except (OSError, ValueError):
            pass  # No poder guardar una optimizacion nunca impide jugar.
        finally:
            if temporal is not None:
                try:
                    temporal.unlink(missing_ok=True)
                except OSError:
                    pass
