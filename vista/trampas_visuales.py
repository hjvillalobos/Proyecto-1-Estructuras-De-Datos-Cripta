"""Representacion paginada y disparos locales; nunca ejecuta el efecto de una trampa."""

import math
from vista.tema import ROJO, TENUE, AMARILLO, BORDE


class ActivacionTrampa:
    def __init__(self, canvas, origen, jugador, altura, dardos=True, etiqueta=""):
        self.canvas, self.origen, self.jugador = canvas, origen, jugador
        self.altura, self.dardos = altura, dardos
        tags = ("efecto_trampa", etiqueta)
        x, y = origen
        self.aviso = canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                        outline=AMARILLO, width=2, tags=tags)
        self.proyectiles = [canvas.create_line(x, y, x, y, fill=AMARILLO, width=2,
                                              arrow="last" if dardos else "none", tags=tags) for _ in range(3)]
        self.impacto = canvas.create_line(0, 0, 0, 0, fill=ROJO, width=3, tags=tags)
        self.ids = [self.aviso, *self.proyectiles, self.impacto]

    def actualizar(self, paso):
        if not self.ids:
            return
        if paso >= 32 or not self.canvas.type(self.jugador):
            self.detener()
            return
        x, y = self.canvas.coords(self.jugador)[:2]
        y -= self.altura * .52
        ox, oy = self.origen
        self.canvas.itemconfig(self.aviso, state="normal" if paso < 10 else "hidden")
        for i, item in enumerate(self.proyectiles):
            p = min(1, max(0, (paso - 6 - i * 2) / 10))
            self.canvas.itemconfig(item, state="normal" if 0 < p < 1 else "hidden")
            sx, sy = ox, oy + (i - 1) * 5
            px, py = sx + (x - sx) * p, sy + (y - sy) * p
            if self.dardos:
                largo = max(1, math.hypot(x - sx, y - sy))
                self.canvas.coords(item, px - (x - sx) * 16 / largo,
                                   py - (y - sy) * 16 / largo, px, py)
            else:
                self.canvas.coords(item, px - 4, py - 4, px + 4, py + 4)
        self.canvas.itemconfig(self.impacto, state="normal" if 16 <= paso < 24 else "hidden")
        r = 6 + max(0, paso - 16)
        self.canvas.coords(self.impacto, x - r, y - r, x, y + r, x + r, y - r)

    def detener(self):
        for item in self.ids:
            self.canvas.delete(item)
        self.ids.clear()


def dibujar_trampas(escena, estado, ancho):
    v, c = escena.vista, escena.vista.canvas
    trampas = getattr(estado, "trampas", ())
    if not trampas:
        return []
    pagina = getattr(v, "_pagina_trampas", 0)
    visibles = trampas[pagina * 8:pagina * 8 + 8]
    armadas = sum(t.armada for t in trampas)
    titulo = (f"{trampas[0].nombre}: {'armada' if trampas[0].armada else 'desarmada'}"
              if len(trampas) == 1 else f"{len(trampas)} trampas: {armadas} armadas, {len(trampas) - armadas} desarmadas")
    c.create_text((ancho + 170) / 2, 77, text=titulo, width=ancho - 390,
                  fill=ROJO if armadas else TENUE, font=("Segoe UI", 9))
    c.create_text(24, 77, text="Trampas" if len(trampas) <= 8 else "", anchor="w",
                  fill=TENUE, font=("Segoe UI", 9))
    origenes = []
    celda = (ancho - 390) / max(1, len(visibles))
    for i, trampa in enumerate(visibles):
        x, y = 280 + celda * (i + .5), 102
        etiqueta = "trampa_" + trampa.instancia
        tags = ("trampa", etiqueta)
        imagen = escena._imagen(trampa.tipo, 24, 24, generica=True)
        if imagen is not None:
            c.create_image(x, y, image=imagen, tags=tags)
        else:
            c.create_rectangle(x - 12, y - 8, x + 12, y + 8, fill="#594636", outline=BORDE, tags=tags)
            c.create_line(x - 7, y, x + 7, y, fill=TENUE, width=3, tags=tags)
        c.create_oval(x + 10, y + 7, x + 15, y + 12, fill=ROJO if trampa.armada else TENUE,
                      outline="", tags=tags)
        detalle = f"{trampa.nombre} ({trampa.instancia}): {'armada' if trampa.armada else 'desarmada'} | {trampa.dano} dano"
        c.tag_bind(etiqueta, "<Enter>", lambda e, texto=detalle: v.mostrar_info(texto))
        origenes.append((trampa, (x, y)))
    v._dibujar_paginacion("trampas", len(trampas), 24, 77)
    return origenes
