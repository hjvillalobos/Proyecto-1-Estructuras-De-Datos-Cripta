from pathlib import Path
import tkinter as tk

try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    Image = ImageTk = None


class RecursosGraficos:
    """Imagenes locales de la vista, independientes del catalogo y de la red."""

    def __init__(self, root, carpeta=None):
        self.root = root
        self.carpeta = Path(carpeta) if carpeta else Path(__file__).parent / "recursos"
        self._imagenes = []
        self._secuencias = []
        self._fondo = None
        self._hoja_jugador = None

    def fondo(self, ancho, alto):
        """Fondo a sangre, con una sola variante de tamano retenida."""
        clave = (max(1, int(ancho)), max(1, int(alto)))
        if self._fondo is not None and self._fondo[0] == clave:
            return self._fondo[1]
        if Image is None:
            return self.imagen("fondo_ladrillos", *clave)
        try:
            with Image.open(self.carpeta / "fondo_ladrillos.png") as origen:
                fondo = ImageOps.fit(origen.convert("RGB"), clave,
                                     method=Image.Resampling.LANCZOS)
            imagen = ImageTk.PhotoImage(fondo, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._fondo = (clave, imagen)
        return imagen

    def fotogramas_jugador(self, ancho, alto, invertir=False):
        tamano = (int(ancho), int(alto))
        clave = (*tamano, bool(invertir))
        for actual, imagenes in self._secuencias:
            if actual == clave:
                return imagenes
        if Image is None:
            return ()
        try:
            if self._hoja_jugador is None:
                with Image.open(self.carpeta / "jugador_acciones.png") as origen:
                    self._hoja_jugador = origen.convert("RGBA")
            hoja = self._hoja_jugador
            w, h = hoja.width // 4, hoja.height // 2
            imagenes = []
            for indice in range(8):
                fila, col = divmod(indice, 4)
                cuadro = hoja.crop((col * w, fila * h + int(h * .19),
                                   (col + 1) * w, fila * h + int(h * .88)))
                if invertir:
                    cuadro = cuadro.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                cuadro.thumbnail(tamano, Image.Resampling.LANCZOS)
                limite = cuadro.getchannel("A").point(lambda a: 255 if a >= 32 else 0).getbbox()
                if limite is not None and limite[3] < cuadro.height:
                    alineado = Image.new("RGBA", cuadro.size)
                    alineado.paste(cuadro, (0, cuadro.height - limite[3]))
                    cuadro = alineado
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
        ancho, alto = max(1, int(ancho)), max(1, int(alto))
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
