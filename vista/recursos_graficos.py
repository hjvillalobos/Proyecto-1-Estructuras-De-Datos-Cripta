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
        self._secuencias = []

    def fotogramas_jugador(self, ancho, alto):
        clave = (int(ancho), int(alto))
        for actual, imagenes in self._secuencias:
            if actual == clave:
                return imagenes
        if Image is None:
            return ()
        try:
            with Image.open(self.carpeta / "jugador_acciones.png") as origen:
                hoja = origen.convert("RGBA")
            w, h = hoja.width // 4, hoja.height // 2
            imagenes = []
            for indice in range(8):
                fila, col = divmod(indice, 4)
                cuadro = hoja.crop((col * w, fila * h + int(h * .19),
                                   (col + 1) * w, fila * h + int(h * .88)))
                cuadro.thumbnail(clave, Image.Resampling.LANCZOS)
                imagenes.append(ImageTk.PhotoImage(cuadro, master=self.root))
        except (OSError, ValueError, tk.TclError):
            return ()
        resultado = tuple(imagenes)
        self._secuencias.append((clave, resultado))
        if len(self._secuencias) > 4:
            self._secuencias.pop(0)
        return resultado

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
