from pathlib import Path
import tkinter as tk

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None


class RecursosGraficos:
    """Imagenes locales de la vista, independientes del catalogo y de la red."""

    def __init__(self, root, carpeta=None):
        self.root = root
        self.carpeta = Path(carpeta) if carpeta else Path(__file__).parent / "recursos"
        self._imagenes = []

    def imagen(self, nombre, ancho, alto):
        if Path(nombre).name != nombre:
            return None
        clave = (nombre, int(ancho), int(alto))
        for actual, imagen in self._imagenes:
            if actual == clave:
                return imagen
        ruta = self.carpeta / (nombre + ".png")
        if not ruta.is_file():
            return None
        try:
            if Image is not None:
                with Image.open(ruta) as origen:
                    original = origen.convert("RGBA")
                original.thumbnail((ancho, alto), Image.Resampling.LANCZOS)
                imagen = ImageTk.PhotoImage(original, master=self.root)
            else:
                original = tk.PhotoImage(file=str(ruta), master=self.root)
                escala = max(1, (original.width() + ancho - 1) // ancho,
                             (original.height() + alto - 1) // alto)
                imagen = original.subsample(escala)
        except (OSError, tk.TclError):
            return None
        self._imagenes.append((clave, imagen))
        if len(self._imagenes) > 24:
            self._imagenes.pop(0)
        return imagen
