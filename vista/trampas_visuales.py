"""Representacion paginada y disparos locales; nunca ejecuta el efecto de una trampa."""

import math
from vista.tema import ROJO, TENUE, AMARILLO, BORDE, VERDE, MORADO, PANEL, TEXTO


class ActivacionTrampa:
    def __init__(self, canvas, origen, jugador, altura, dardos=True, etiqueta="", venenosa=False):
        self.canvas, self.origen, self.jugador = canvas, origen, jugador
        self.altura, self.dardos = altura, dardos
        self.venenosa = venenosa
        tags = ("efecto_trampa", etiqueta)
        if venenosa:
            tags += ("efecto_veneno",)
        color = VERDE if venenosa else AMARILLO
        x, y = origen
        self.aviso = canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                        outline=color, width=2, tags=tags)
        self.proyectiles = [canvas.create_line(x, y, x, y, fill=color, width=2,
                                              arrow="last" if dardos or venenosa else "none",
                                              tags=tags) for _ in range(3)]
        self.impacto = canvas.create_line(0, 0, 0, 0, fill=MORADO if venenosa else ROJO,
                                          width=3, tags=tags)
        self.burbujas = [canvas.create_oval(0, 0, 0, 0, outline=VERDE, width=2,
                                           state="hidden", tags=tags) for _ in range(5)] if venenosa else []
        self.ids = [self.aviso, *self.proyectiles, self.impacto, *self.burbujas]

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
            if self.dardos or self.venenosa:
                largo = max(1, math.hypot(x - sx, y - sy))
                self.canvas.coords(item, px - (x - sx) * 16 / largo,
                                   py - (y - sy) * 16 / largo, px, py)
            else:
                self.canvas.coords(item, px - 4, py - 4, px + 4, py + 4)
        self.canvas.itemconfig(self.impacto, state="normal" if 16 <= paso < 24 else "hidden")
        r = 6 + max(0, paso - 16)
        self.canvas.coords(self.impacto, x - r, y - r, x, y + r, x + r, y - r)
        for i, item in enumerate(self.burbujas):
            edad = paso - 14 - i * 2
            self.canvas.itemconfig(item, state="normal" if 0 <= edad < 14 else "hidden")
            bx = x + (i - 2) * (5 + max(0, edad) * .8)
            by = y + 12 - max(0, edad) * 3 - (i % 2) * 8
            radio = 2 + max(0, edad) * .22
            self.canvas.coords(item, bx - radio, by - radio, bx + radio, by + radio)

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
        venenosa = getattr(trampa, "venenosa", False)
        imagen = None if venenosa else escena._imagen(trampa.tipo, 24, 24, generica=True)
        if venenosa:
            # Icono nativo: cualquier ficha venenosa tiene aspecto propio,
            # incluso sin PNG local para su identificador de catalogo.
            color = VERDE if trampa.armada else TENUE
            c.create_rectangle(x - 15, y - 12, x + 15, y + 12, fill=PANEL,
                               outline=MORADO if trampa.armada else BORDE, tags=tags)
            for dx in (-8, 0, 8):
                c.create_line(x + dx - 3, y + 7, x + dx + 3, y - 7,
                              fill=TEXTO if trampa.armada else TENUE, width=2, tags=tags)
                c.create_line(x + dx + 1, y - 3, x + dx + 3, y - 7,
                              fill=color, width=3, tags=tags)
            c.create_text(x, y + 24, text="Veneno", fill=color,
                          font=("Segoe UI", 9, "bold"), tags=tags)
        elif imagen is not None:
            c.create_image(x, y, image=imagen, tags=tags)
        else:
            c.create_rectangle(x - 12, y - 8, x + 12, y + 8, fill="#594636", outline=BORDE, tags=tags)
            c.create_line(x - 7, y, x + 7, y, fill=TENUE, width=3, tags=tags)
        c.create_oval(x + 10, y + 7, x + 15, y + 12, fill=ROJO if trampa.armada else TENUE,
                      outline="", tags=tags)
        detalle = f"{trampa.nombre} ({trampa.instancia}): {'armada' if trampa.armada else 'desarmada'} | {trampa.dano} dano"
        if venenosa:
            detalle += " | Aplica veneno"
        c.tag_bind(etiqueta, "<Enter>", lambda e, texto=detalle: v.mostrar_info(texto))
        origenes.append((trampa, (x, y)))
    v._dibujar_paginacion("trampas", len(trampas), 24, 77)
    return origenes
