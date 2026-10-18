from pathlib import Path
import tkinter as tk
from vista.cache_visual import CacheVisual
from vista.composiciones import ComposicionesPreparadas, clave_equipo
from vista.tema import PANEL, TEXTO, BORDE

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
        self._acciones = []
        self._fondo = None
        self._hoja_jugador = None
        self._fondo_sala = None
        self._objetos_ilustrados = None
        self._chaleco = None
        self._jugadores_vestidos = []
        self._daga = None
        self._bebidas = []
        self._pose_beber = None
        self._puno = None
        self._antorcha = None
        self._jugador_original = None
        self._fondo_original = None
        self._cuadros_preparados = None
        self._cache_visual = CacheVisual(self.carpeta)
        self._preparadas = ComposicionesPreparadas(self.carpeta)
        self._neutras = []
        self._ausentes = []

    def imagen_entidad(self, nombre, ancho, alto):
        imagen = self.imagen(nombre, ancho, alto)
        return imagen if imagen is not None else self.imagen_neutra(ancho, alto)

    def imagen_neutra(self, ancho, alto):
        """Signo neutro nativo, compartido por tamano; no necesita PNG ni Pillow."""
        tamano = max(8, min(96, int(ancho), int(alto)))
        factor = max(1, tamano // 16)
        clave = factor if tamano >= 16 else 0
        for actual, imagen in self._neutras:
            if actual == clave:
                return imagen
        signo = ("01110", "10001", "00001", "00010", "00100", "00000", "00100")
        filas = []
        for y in range(16):
            colores = []
            for x in range(16):
                color = BORDE if x in (0, 15) or y in (0, 15) else PANEL
                if 3 <= x < 13 and 1 <= y < 15 and signo[(y-1)//2][(x-3)//2] == "1":
                    color = TEXTO
                colores.append(color)
            filas.append("{" + " ".join(colores) + "}")
        original = tk.PhotoImage(master=self.root, width=16, height=16)
        original.put(" ".join(filas))
        imagen = original.zoom(factor) if clave else original.subsample(2)
        self._neutras.append((clave, imagen))
        return imagen

    def _recordar_ausente(self, nombre):
        if nombre not in self._ausentes:
            self._ausentes.append(nombre)
            if len(self._ausentes) > 64:
                self._ausentes.pop(0)

    def _original_jugador(self):
        if self._jugador_original is None:
            with Image.open(self.carpeta / "jugador.png") as origen:
                self._jugador_original = origen.convert("RGBA")
        return self._jugador_original.copy()

    def _original_fondo(self):
        if self._fondo_original is None:
            ruta = self.carpeta / "fondo_cripta_ilustrado.png"
            ilustrado = ruta.is_file()
            with Image.open(ruta if ilustrado else self.carpeta / "fondo_ladrillos.png") as origen:
                self._fondo_original = (origen.convert("RGB"), ilustrado)
        return self._fondo_original

    def _antorcha_jugador(self):
        if Image is None:
            return None
        if self._antorcha is None:
            try:
                self._antorcha = self._objeto_ilustrado("itm_antorcha")
                if self._antorcha is None:
                    with Image.open(self.carpeta / "itm_antorcha.png") as origen:
                        self._antorcha = origen.convert("RGBA")
                from PIL import ImageDraw, ImageChops
                mascara = self._antorcha.getchannel("A").point(lambda a: 255 if a >= 16 else 0)
                y = int(mascara.height * .70)
                fila = [x for x in range(mascara.width) if mascara.getpixel((x, y))]
                if fila:
                    ImageDraw.floodfill(mascara, (fila[len(fila) // 2], y), 128)
                    componente = mascara.point(lambda a: 255 if a == 128 else 0)
                    self._antorcha.putalpha(ImageChops.multiply(self._antorcha.getchannel("A"), componente))
            except (OSError, ValueError):
                return None
        return self._antorcha

    def _puno_jugador(self):
        if Image is None:
            return None
        if self._puno is None:
            try:
                if self._hoja_jugador is None:
                    with Image.open(self.carpeta / "jugador_acciones.png") as origen:
                        self._hoja_jugador = origen.convert("RGBA")
                hoja = self._hoja_jugador
                self._puno = hoja.crop((int(hoja.width * 299 / 1536), int(hoja.height * 224 / 1024),
                                       int(hoja.width * 339 / 1536), int(hoja.height * 267 / 1024)))
            except (OSError, ValueError):
                return None
        return self._puno

    def _arma_jugador(self, tipo):
        if Image is None or tipo != "itm_daga_oxidada":
            return None
        if self._daga is None:
            try:
                self._daga = self._objeto_ilustrado(tipo)
                if self._daga is None:
                    with Image.open(self.carpeta / (tipo + ".png")) as origen:
                        self._daga = origen.convert("RGBA")
            except (OSError, ValueError):
                return None
        return self._daga

    def jugador_armado(self, ancho, alto, arma, armadura=None, antorcha=False):
        if Image is None or (arma != "itm_daga_oxidada" and not antorcha):
            return None
        clave = (int(ancho), int(alto), armadura, arma, bool(antorcha))
        for actual, imagen in self._jugadores_vestidos:
            if actual == clave:
                return imagen
        try:
            cuadro = self._cache_visual.leer(("armado", *clave))
            if cuadro is None:
                cuadro = self._preparadas.leer(("reposo", *clave[:2], *clave_equipo(armadura, arma, antorcha)))
            if cuadro is None:
                cuadro = self._componer_reposo(armadura, arma, antorcha)
                cuadro.thumbnail(clave[:2], Image.Resampling.LANCZOS)
                self._cache_visual.guardar(("armado", *clave), cuadro)
            imagen = ImageTk.PhotoImage(cuadro, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._jugadores_vestidos.append((clave, imagen))
        if len(self._jugadores_vestidos) > 4:
            self._jugadores_vestidos.pop(0)
        return imagen

    def _componer_reposo(self, armadura=None, arma=None, antorcha=False):
        cuadro = self._preparadas.leer(("reposo", *clave_equipo(armadura, arma, antorcha)))
        if cuadro is not None:
            return cuadro
        from vista.equipo_visual import armar_jugador, vestir_jugador, iluminar_jugador
        cuadro = self._original_jugador()
        ropa, daga = self._ropa_jugador(armadura), self._arma_jugador(arma)
        luz = self._antorcha_jugador() if antorcha else None
        puno = self._puno_jugador() if daga is not None or luz is not None else None
        if ropa is not None:
            cuadro = vestir_jugador(cuadro, ropa)
        if daga is not None and puno is not None:
            cuadro = armar_jugador(cuadro, daga, puno)
        if luz is not None and puno is not None:
            cuadro = iluminar_jugador(cuadro, luz, puno)
        return cuadro

    def pose_beber(self, alto, armadura=None, antidoto=False, antorcha=False):
        if Image is None:
            return None
        clave = (int(alto), armadura, bool(antidoto), bool(antorcha))
        for actual, imagen in self._bebidas:
            if actual == clave:
                return imagen
        try:
            cuadro = self._cache_visual.leer(("bebida", *clave))
            if cuadro is None:
                cuadro = self._preparadas.leer(("bebida", int(alto),
                    int(armadura == "itm_coraza_cuero"), int(bool(antidoto)), int(bool(antorcha))))
            if cuadro is None:
                cuadro = self._componer_bebida(armadura, antidoto, antorcha)
                if cuadro is None:
                    return None
                cuadro.thumbnail((290, int(alto)), Image.Resampling.LANCZOS)
                self._cache_visual.guardar(("bebida", *clave), cuadro)
            imagen = ImageTk.PhotoImage(cuadro, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._bebidas.append((clave, imagen))
        if len(self._bebidas) > 4:
            self._bebidas.pop(0)
        return imagen

    def _componer_bebida(self, armadura=None, antidoto=False, antorcha=False):
        preparado = self._preparadas.leer(("bebida_original", int(armadura == "itm_coraza_cuero"),
                                           int(bool(antidoto)), int(bool(antorcha))))
        if preparado is not None:
            return preparado
        try:
            if self._pose_beber is None:
                with Image.open(self.carpeta / "jugador_beber.png") as origen:
                    hoja = origen.convert("RGBA")
                # Solo la celda central conserva el mismo brazo de reposo.
                celda = hoja.width // 3
                margen = int(celda * .035)
                cuadro = hoja.crop((celda + margen, 0, celda * 2 - margen, hoja.height))
                limite = cuadro.getchannel("A").point(lambda a: 255 if a >= 32 else 0).getbbox()
                if limite is None:
                    return None
                self._pose_beber = cuadro.crop(limite)
            cuadro = self._pose_beber.copy()
            if antidoto:
                from PIL import ImageChops
                zona = (int(cuadro.width * .635), int(cuadro.height * .10),
                        int(cuadro.width * .72), int(cuadro.height * .145))
                botella = cuadro.crop(zona)
                h, s, _ = botella.convert("HSV").split()
                mascara = ImageChops.multiply(h.point(lambda v: 255 if v < 20 or v > 240 else 0),
                                             s.point(lambda v: 255 if v > 100 else 0))
                tinte = ImageOps.colorize(botella.convert("L"), "#103c3b", "#7be0cf").convert("RGBA")
                tinte.putalpha(botella.getchannel("A"))
                botella.paste(tinte, (0, 0), mascara)
                cuadro.paste(botella, zona)
            ropa = self._ropa_jugador(armadura)
            if ropa is not None:
                from vista.equipo_visual import vestir_jugador
                cuadro = vestir_jugador(cuadro, ropa)
            if antorcha:
                luz, puno = self._antorcha_jugador(), self._puno_jugador()
                if luz is not None and puno is not None:
                    from vista.equipo_visual import iluminar_jugador
                    cuadro = iluminar_jugador(cuadro, luz, puno, "beber")
            return cuadro
        except (OSError, ValueError, tk.TclError):
            return None

    def fondo_sala(self, ancho, alto):
        """Escenario pintado; conserva el fondo previo como respaldo local."""
        clave = (max(1, int(ancho)), max(1, int(alto)))
        if self._fondo_sala is not None and self._fondo_sala[0] == clave:
            return self._fondo_sala[1]
        if Image is None:
            return None
        try:
            fondo = self._cache_visual.leer(("fondo_sala", *clave))
            if fondo is None:
                fondo, ilustrado = self._original_fondo()
                if not ilustrado:
                    fondo = fondo.crop((int(fondo.width * .34), 0, fondo.width, fondo.height))
                corte = int(fondo.height * (.58 if ilustrado else .78))
                pared = int(clave[1] * .50)
                composicion = Image.new("RGB", clave)
                composicion.paste(fondo.crop((0, 0, fondo.width, corte)).resize(
                    (clave[0], max(1, pared)), Image.Resampling.LANCZOS), (0, 0))
                composicion.paste(fondo.crop((0, corte, fondo.width, fondo.height)).resize(
                    (clave[0], max(1, clave[1] - pared)), Image.Resampling.LANCZOS), (0, pared))
                fondo = composicion
                if not ilustrado:
                    fondo = ImageEnhance.Brightness(fondo).enhance(1.18)
                    fondo = Image.blend(fondo, Image.new("RGB", clave, "#c58b50"), .16)
                self._cache_visual.guardar(("fondo_sala", *clave), fondo)
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
            fondo = self._cache_visual.leer(("fondo_menu", *clave))
            if fondo is None:
                original, _ = self._original_fondo()
                fondo = ImageOps.fit(original, clave, method=Image.Resampling.LANCZOS)
                self._cache_visual.guardar(("fondo_menu", *clave), fondo)
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
        if Image is None or armadura != "itm_coraza_cuero":
            return None
        clave = (int(ancho), int(alto), armadura)
        for actual, imagen in self._jugadores_vestidos:
            if actual == clave:
                return imagen
        try:
            cuadro = self._cache_visual.leer(("vestido", *clave))
            if cuadro is None:
                cuadro = self._preparadas.leer(("reposo", *clave[:2], *clave_equipo(armadura, None, False)))
            if cuadro is None:
                ropa = self._ropa_jugador(armadura)
                if ropa is None:
                    return None
                cuadro = self._componer_reposo(armadura)
                cuadro.thumbnail(clave[:2], Image.Resampling.LANCZOS)
                self._cache_visual.guardar(("vestido", *clave), cuadro)
            imagen = ImageTk.PhotoImage(cuadro, master=self.root)
        except (OSError, ValueError, tk.TclError):
            return None
        self._jugadores_vestidos.append((clave, imagen))
        if len(self._jugadores_vestidos) > 4:
            self._jugadores_vestidos.pop(0)
        return imagen

    def fotogramas_jugador(self, ancho, alto, invertir=False, armadura=None, arma=None, antorcha=False):
        tamano = (int(ancho), int(alto))
        clave = (*tamano, bool(invertir), armadura, arma, bool(antorcha))
        for actual, imagenes in self._secuencias:
            if actual == clave:
                return imagenes
        if Image is None:
            return ()
        try:
            hoja_guardada = self._cache_visual.leer(("secuencia", *clave))
            if hoja_guardada is None:
                hoja_guardada = self._preparadas.leer(("secuencia", *tamano, int(bool(invertir)),
                                                     *clave_equipo(armadura, arma, antorcha)))
            if hoja_guardada is not None and hoja_guardada.width % 8 == 0:
                resultado = self._fotos_desde_hoja(hoja_guardada)
                self._secuencias.append((clave, resultado))
                if len(self._secuencias) > 4:
                    self._secuencias.pop(0)
                return resultado
            # Ambas orientaciones comparten las mismas composiciones, no los objetos Tk.
            composicion = (armadura, arma, bool(antorcha))
            preparados = self._cuadros_preparados
            if preparados is None or preparados[0] != composicion:
                cuadros = self._componer_fotogramas(armadura, arma, antorcha)
                self._cuadros_preparados = (composicion, cuadros)
            else:
                cuadros = preparados[1]
            imagenes = []
            hoja_guardada = None
            for indice, original in enumerate(cuadros):
                cuadro = original.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if invertir else original.copy()
                cuadro.thumbnail(tamano, Image.Resampling.LANCZOS)
                limite = cuadro.getchannel("A").point(lambda a: 255 if a >= 32 else 0).getbbox()
                if limite is not None and limite[3] < cuadro.height:
                    alineado = Image.new("RGBA", cuadro.size)
                    alineado.paste(cuadro, (0, cuadro.height - limite[3]))
                    cuadro = alineado
                if hoja_guardada is None:
                    hoja_guardada = Image.new("RGBA", (cuadro.width * 8, cuadro.height))
                hoja_guardada.paste(cuadro, (indice * cuadro.width, 0))
            self._cache_visual.guardar(("secuencia", *clave), hoja_guardada)
            imagenes = self._fotos_desde_hoja(hoja_guardada)
        except (OSError, ValueError, tk.TclError):
            return ()
        resultado = tuple(imagenes)
        self._secuencias.append((clave, resultado))
        if len(self._secuencias) > 4:
            self._secuencias.pop(0)
        return resultado

    def _fotos_desde_hoja(self, hoja, indices=range(8)):
        w, h = hoja.width // 8, hoja.height
        return tuple(ImageTk.PhotoImage(hoja.crop((i*w, 0, (i+1)*w, h)), master=self.root) for i in indices)

    def fotogramas_accion(self, accion, ancho, alto, invertir=False, armadura=None, arma=None, antorcha=False):
        indices = {"correr": (0, 1, 2, 3), "atacar": (4, 5), "caer": (6, 7)}[accion]
        clave = (int(ancho), int(alto), bool(invertir), armadura, arma, bool(antorcha))
        for actual, cuadros in self._secuencias:
            if actual == clave:
                return tuple(cuadros[i] for i in indices)
        for actual, cuadros in self._acciones:
            if actual == (accion, *clave):
                return cuadros
        if Image is None:
            return ()
        try:
            hoja = self._cache_visual.leer(("secuencia", *clave))
            if hoja is None:
                hoja = self._preparadas.leer(("secuencia", int(ancho), int(alto), int(bool(invertir)),
                                             *clave_equipo(armadura, arma, antorcha)))
            if hoja is None:
                todos = self.fotogramas_jugador(ancho, alto, invertir, armadura, arma, antorcha)
                return tuple(todos[i] for i in indices) if len(todos) == 8 else ()
            cuadros = self._fotos_desde_hoja(hoja, indices)
        except (OSError, ValueError, tk.TclError):
            return ()
        self._acciones.append(((accion, *clave), cuadros))
        if len(self._acciones) > 8:
            self._acciones.pop(0)
        return cuadros

    def _componer_fotogramas(self, armadura, arma, antorcha):
        preparada = self._preparadas.leer(("acciones", *clave_equipo(armadura, arma, antorcha)))
        if preparada is not None and preparada.width % 8 == 0:
            w, h = preparada.width // 8, preparada.height
            return tuple(preparada.crop((i*w, 0, (i+1)*w, h)) for i in range(8))
        if self._hoja_jugador is None:
            with Image.open(self.carpeta / "jugador_acciones.png") as origen:
                self._hoja_jugador = origen.convert("RGBA")
        hoja = self._hoja_jugador
        w, h = hoja.width // 4, hoja.height // 2
        cuadros = []
        ropa = self._ropa_jugador(armadura)
        daga = self._arma_jugador(arma)
        luz = self._antorcha_jugador() if antorcha else None
        puno = self._puno_jugador() if daga is not None or luz is not None else None
        for indice in range(8):
            fila, col = divmod(indice, 4)
            cuadro = hoja.crop((col * w, fila * h + int(h * .19),
                               (col + 1) * w, fila * h + int(h * .88)))
            if ropa is not None:
                from vista.equipo_visual import vestir_jugador
                cuadro = vestir_jugador(cuadro, ropa, indice)
            if daga is not None and puno is not None:
                from vista.equipo_visual import armar_jugador
                cuadro = armar_jugador(cuadro, daga, puno, indice)
            if luz is not None and puno is not None:
                from vista.equipo_visual import iluminar_jugador
                cuadro = iluminar_jugador(cuadro, luz, puno, indice)
            cuadros.append(cuadro)
        return tuple(cuadros)

    def imagen(self, nombre, ancho, alto):
        if Path(nombre).name != nombre:
            return None
        if nombre in self._ausentes:
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
            self._recordar_ausente(nombre)
            return None
        try:
            if Image is not None:
                archivo = ruta.stat()
                preparada = ("imagen", *clave, archivo.st_size, archivo.st_mtime_ns)
                original = self._cache_visual.leer(preparada)
                if original is None:
                    original = self._objeto_ilustrado(nombre)
                    if original is None and nombre == "jugador":
                        original = self._original_jugador()
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
                    self._cache_visual.guardar(preparada, original)
                imagen = ImageTk.PhotoImage(original, master=self.root)
            else:
                original = tk.PhotoImage(file=str(ruta), master=self.root)
                escala = max(1, (original.width() + ancho - 1) // ancho,
                             (original.height() + alto - 1) // alto)
                imagen = original.subsample(escala)
        except (OSError, tk.TclError):
            self._recordar_ausente(nombre)
            return None
        self._imagenes.append((clave, imagen))
        if len(self._imagenes) > 24:
            self._imagenes.pop(0)
        return imagen
