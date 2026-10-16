from pathlib import Path
import tkinter as tk

try:
    from PIL import Image, ImageTk, ImageOps, ImageEnhance
except ImportError:
    Image = ImageTk = None

_RECORTES_OBJETOS = (
    ("itm_pocion_menor", (.59, 0, .76, .405)),
    ("itm_daga_oxidada", (.76, 0, 1, .405)),
    ("itm_coraza_cuero", (0, .405, .27, .72)),
    ("itm_antidoto", (.27, .405, .54, .72)),
    ("itm_antorcha", (.54, .39, .76, .72)),
    ("itm_pergamino_retroceso", (.76, .405, 1, .72)),
    ("itm_llave_bronce", (0, .72, .27, 1)),
    ("itm_llave_negra", (.27, .72, .54, 1)),
    ("trp_dardos", (.54, .72, .76, 1)),
)


class RecursosGraficos:
    """Imagenes locales de la vista, independientes del catalogo y de la red."""

    def __init__(self, root, carpeta=None):
        self.root = root
        self.carpeta = Path(carpeta) if carpeta else Path(__file__).parent / "recursos"
        self._imagenes = []
        self._secuencias = []
        self._fondo = None
        self._hoja_jugador = None
        self._fondo_sala = None
        self._objetos_ilustrados = None
        self._chaleco = None
        self._jugadores_vestidos = []

    def fondo_sala(self, ancho, alto):
        """Escenario pintado; conserva el fondo previo como respaldo local."""
        clave = (max(1, int(ancho)), max(1, int(alto)))
        if self._fondo_sala is not None and self._fondo_sala[0] == clave:
            return self._fondo_sala[1]
        if Image is None:
            return None
        try:
            ilustrado = self.carpeta / "fondo_cripta_ilustrado.png"
            with Image.open(ilustrado if ilustrado.is_file() else self.carpeta / "fondo_ladrillos.png") as origen:
                fondo = origen.convert("RGB")
            if not ilustrado.is_file():
                fondo = fondo.crop((int(fondo.width * .34), 0, fondo.width, fondo.height))
            corte = int(fondo.height * (.58 if ilustrado.is_file() else .78))
            pared = int(clave[1] * .50)
            composicion = Image.new("RGB", clave)
            composicion.paste(fondo.crop((0, 0, fondo.width, corte)).resize(
                (clave[0], max(1, pared)), Image.Resampling.LANCZOS), (0, 0))
            composicion.paste(fondo.crop((0, corte, fondo.width, fondo.height)).resize(
                (clave[0], max(1, clave[1] - pared)), Image.Resampling.LANCZOS), (0, pared))
            fondo = composicion
            if not ilustrado.is_file():
                fondo = ImageEnhance.Brightness(fondo).enhance(1.18)
                fondo = Image.blend(fondo, Image.new("RGB", clave, "#c58b50"), .16)
            imagen = ImageTk.PhotoImage(fondo, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._fondo_sala = (clave, imagen)
        return imagen

    def fondo(self, ancho, alto):
        """Fondo a sangre, con una sola variante de tamano retenida."""
        clave = (max(1, int(ancho)), max(1, int(alto)))
        if self._fondo is not None and self._fondo[0] == clave:
            return self._fondo[1]
        if Image is None:
            return self.imagen("fondo_ladrillos", *clave)
        try:
            ruta = self.carpeta / "fondo_cripta_ilustrado.png"
            with Image.open(ruta if ruta.is_file() else self.carpeta / "fondo_ladrillos.png") as origen:
                fondo = ImageOps.fit(origen.convert("RGB"), clave,
                                     method=Image.Resampling.LANCZOS)
            imagen = ImageTk.PhotoImage(fondo, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._fondo = (clave, imagen)
        return imagen

    def _objeto_ilustrado(self, nombre):
        recorte = next((zona for tipo, zona in _RECORTES_OBJETOS if tipo == nombre), None)
        ruta = self.carpeta / "objetos_ilustrados.png"
        if recorte is None or not ruta.is_file():
            return None
        if self._objetos_ilustrados is None:
            with Image.open(ruta) as origen:
                self._objetos_ilustrados = origen.convert("RGBA")
        hoja = self._objetos_ilustrados
        x1, y1, x2, y2 = recorte
        cuadro = hoja.crop((int(x1 * hoja.width), int(y1 * hoja.height),
                            int(x2 * hoja.width), int(y2 * hoja.height)))
        limite = cuadro.getchannel("A").point(lambda a: 255 if a >= 64 else 0).getbbox()
        return cuadro.crop(limite) if limite else None

    def _ropa_jugador(self, armadura):
        if Image is None or armadura != "itm_coraza_cuero":
            return None
        if self._chaleco is None:
            try:
                with Image.open(self.carpeta / "itm_coraza_cuero.png") as origen:
                    chaleco = origen.convert("RGBA")
                limite = chaleco.getchannel("A").getbbox()
                if limite is None:
                    return None
                self._chaleco = chaleco.crop(limite)
            except (OSError, ValueError):
                return None
        return self._chaleco

    def jugador_vestido(self, ancho, alto, armadura):
        """Variante visual acotada: el PNG del tigre permanece sin modificar."""
        ropa = self._ropa_jugador(armadura)
        if ropa is None:
            return None
        clave = (int(ancho), int(alto), armadura)
        for actual, imagen in self._jugadores_vestidos:
            if actual == clave:
                return imagen
        try:
            from vista.equipo_visual import vestir_jugador
            with Image.open(self.carpeta / "jugador.png") as origen:
                cuadro = vestir_jugador(origen.convert("RGBA"), ropa)
            cuadro.thumbnail(clave[:2], Image.Resampling.LANCZOS)
            imagen = ImageTk.PhotoImage(cuadro, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._jugadores_vestidos.append((clave, imagen))
        if len(self._jugadores_vestidos) > 4:
            self._jugadores_vestidos.pop(0)
        return imagen

    def fotogramas_jugador(self, ancho, alto, invertir=False, armadura=None):
        tamano = (int(ancho), int(alto))
        clave = (*tamano, bool(invertir), armadura)
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
                ropa = self._ropa_jugador(armadura)
                if ropa is not None:
                    from vista.equipo_visual import vestir_jugador
                    cuadro = vestir_jugador(cuadro, ropa, indice)
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
        if nombre == "ent_guardian_oseo" and (self.carpeta / "guardian_ilustrado.png").is_file():
            ruta = self.carpeta / "guardian_ilustrado.png"
        if not ruta.is_file():
            return None
        try:
            if Image is not None:
                original = self._objeto_ilustrado(nombre)
                if original is None:
                    with Image.open(ruta) as origen:
                        original = origen.convert("RGBA")
                if ruta.name == "guardian_ilustrado.png":
                    limite = original.getchannel("A").getbbox()
                    if limite:
                        original = original.crop(limite)
                if nombre == "ent_rata_gigante":
                    original = ImageOps.mirror(original)
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
