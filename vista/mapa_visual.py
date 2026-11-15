"""VI-02/04: cartografía de una proyección conocida, sin acceso al modelo/red."""
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from dataclasses import dataclass
from utilidades.ordenamiento import ordenar
from vista.tema import FONDO, PANEL, TEXTO, TENUE, AMARILLO, VERDE, ROJO, BORDE


@dataclass(frozen=True)
class Cartografia:
    registros: tuple
    posiciones: tuple
    conexiones: tuple  # índices origen/destino y salida recordada


def _indice(ids, valor):
    bajo, alto = 0, len(ids)
    while bajo < alto:
        medio = (bajo + alto) // 2
        if ids[medio] < valor:
            bajo = medio + 1
        else:
            alto = medio
    return bajo if bajo < len(ids) and ids[bajo] == valor else None


def preparar_cartografia(proyeccion, actual=None):
    """Descarta información oculta incluso si el llamador la incluye por error.

    Solo usa la proyección recibida. Orden propio O(V log V); disposición
    O(V+E) tras resolver IDs. No presupone geometría ni arcos recíprocos.
    """
    visibles = []
    for identidad, estado, nombre, salidas in proyeccion:
        if estado == 1:
            visibles.append((identidad, estado, None, ()))
        elif estado == 2:
            visibles.append((identidad, estado, nombre, tuple(salidas)))
    registros = tuple(ordenar(visibles, clave=lambda r: r[0], algoritmo='fusion'))
    ids = tuple(r[0] for r in registros)
    vecinos = [[] for _ in ids]
    conexiones = []
    for i, (_, _, _, salidas) in enumerate(registros):
        for salida in salidas:
            j = _indice(ids, salida[1])
            if j is not None:
                conexiones.append((i, j, salida))
                vecinos[i].append(j)
                if i != j:
                    vecinos[j].append(i)  # Solo disposición, no crea salida.
    posiciones = [None] * len(ids)
    visitados = [False] * len(ids)
    primero = _indice(ids, actual) if type(actual) is int else None
    semillas = ([primero] if primero is not None else []) + list(range(len(ids)))
    y_base = 130
    for semilla in semillas:
        if visitados[semilla]:
            continue
        cola, niveles = [(semilla, 0)], [[]]
        visitados[semilla] = True
        lectura = 0
        while lectura < len(cola):
            i, nivel = cola[lectura]
            lectura += 1
            if len(niveles) <= nivel:
                niveles.append([])
            niveles[nivel].append(i)
            for j in vecinos[i]:
                if not visitados[j]:
                    visitados[j] = True
                    cola.append((j, nivel + 1))
        for nivel in niveles:
            filas = (len(nivel) + 5) // 6
            for k, i in enumerate(nivel):
                columna = k % 6
                ancho = min(6, len(nivel) - (k // 6) * 6)
                posiciones[i] = (370 + (columna - (ancho - 1) / 2) * 155,
                                 y_base + (k // 6) * 112)
            y_base += max(1, filas) * 112
        y_base += 60
    # Trasladar sin distorsión para que grafos anchos no queden fuera del lienzo.
    izquierda = min((p[0] for p in posiciones), default=150)
    dx = max(0, 100 - izquierda)
    posiciones = tuple((x + dx, y) for x, y in posiciones)
    return Cartografia(registros, posiciones, tuple(conexiones))


class VentanaMapa:
    def __init__(self, padre, proyeccion, actual=None, destino=None):
        self.datos = preparar_cartografia(proyeccion, actual)
        self.actual, self.destino = actual, destino
        self.seleccion = next((i for i, r in enumerate(self.datos.registros) if r[0] == actual),
                             0 if self.datos.registros else None)
        self.zoom = 1.0
        self.comando = None
        self.ventana = tk.Toplevel(padre)
        v = self.ventana
        v.title('CRIPTA · Cartografía de la memoria')
        v.configure(bg=FONDO)
        ancho = min(1160, max(880, padre.winfo_screenwidth()-80))
        alto = min(760, max(550, padre.winfo_screenheight()-100))
        x = max(0, (padre.winfo_screenwidth()-ancho)//2)
        y = max(0, (padre.winfo_screenheight()-alto)//2)
        v.geometry(f'{ancho}x{alto}+{x}+{y}')
        v.minsize(880, 550)
        v.transient(padre)
        v.protocol('WM_DELETE_WINDOW', self.cerrar)
        v.bind('<Escape>', lambda _: self.cerrar())
        cabecera = tk.Frame(v, bg=FONDO)
        cabecera.pack(fill='x', padx=24, pady=(18, 12))
        tk.Label(cabecera, text='CARTOGRAFÍA DE LA CRIPTA', font=('Georgia', 21),
                 fg=AMARILLO, bg=FONDO).pack(anchor='w')
        tk.Label(cabecera, text='Lo que tus pasos recuerdan', font=('Segoe UI', 11),
                 fg=TENUE, bg=FONDO).pack(anchor='w', pady=(4, 0))
        cuerpo = tk.Frame(v, bg=FONDO)
        cuerpo.pack(fill='both', expand=True, padx=20)
        panel_lateral = tk.Frame(cuerpo, bg=PANEL, width=278)
        panel_lateral.pack(side='right', fill='y', padx=(14, 0))
        panel_lateral.pack_propagate(False)
        lienzo_lateral = tk.Canvas(panel_lateral, width=260, bg=PANEL, highlightthickness=0)
        scroll_lateral = ttk.Scrollbar(panel_lateral, orient='vertical', command=lienzo_lateral.yview)
        scroll_lateral.pack(side='right', fill='y')
        lienzo_lateral.pack(side='left', fill='both', expand=True)
        lienzo_lateral.configure(yscrollcommand=scroll_lateral.set)
        lateral = tk.Frame(lienzo_lateral, bg=PANEL, padx=16, pady=18)
        lienzo_lateral.create_window((0, 0), window=lateral, width=260, anchor='nw')
        lateral.bind('<Configure>', lambda _: lienzo_lateral.configure(scrollregion=lienzo_lateral.bbox('all')))
        tk.Label(lateral, text='TU MEMORIA', font=('Georgia', 14), fg=AMARILLO, bg=PANEL).pack(anchor='w')
        exploradas = sum(r[1] == 2 for r in self.datos.registros)
        tk.Label(lateral, text=f'{exploradas} explorada{"s" if exploradas != 1 else ""} · {len(self.datos.registros) - exploradas} avistadas',
                 fg=TENUE, bg=PANEL, font=('Segoe UI', 10)).pack(anchor='w', pady=(7, 18))
        self.titulo = tk.Label(lateral, fg=TEXTO, bg=PANEL, font=('Georgia', 16), wraplength=225, justify='left')
        self.titulo.pack(anchor='w')
        self.detalle = tk.Label(lateral, fg=TENUE, bg=PANEL, font=('Segoe UI', 10), wraplength=225, justify='left')
        self.detalle.pack(anchor='w', pady=(10, 16))
        self.boton_viajar = ttk.Button(lateral, text='Viajar a esta sala', command=self.viajar)
        self.boton_viajar.pack(fill='x')
        ttk.Button(lateral, text='Centrar en ti', command=self.centrar).pack(fill='x', pady=7)
        self.leyenda = tk.Label(lateral, text='◉ Tu sala · ◇ Destino\nVerde: explorada · ?: avistada\nNiebla: aún desconocido\n\nPuertas (último recuerdo)\nVerde: abierta · rojo: cerrada\nGris: sin observar\nPueden haber cambiado.',
                                fg=TENUE, bg=PANEL, font=('Segoe UI', 9), justify='left', wraplength=225)
        self.leyenda.pack(anchor='w', pady=(22, 0))
        area = tk.Frame(cuerpo, bg='#10191a', highlightbackground=BORDE, highlightthickness=1)
        area.pack(side='left', fill='both', expand=True)
        self.cuadro = tk.Frame(area, bg=FONDO)
        self.cuadro.pack(fill='both', expand=True)
        self.cuadro.rowconfigure(0, weight=1)
        self.cuadro.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.cuadro, bg='#111c1c', highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        barra_x = ttk.Scrollbar(self.cuadro, orient='horizontal', command=self.canvas.xview)
        barra_y = ttk.Scrollbar(self.cuadro, orient='vertical', command=self.canvas.yview)
        barra_x.grid(row=1, column=0, sticky='ew')
        barra_y.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)
        self.canvas.bind('<ButtonPress-2>', lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind('<B2-Motion>', lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))
        self.canvas.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(-1 if e.delta > 0 else 1, 'units'))
        self.texto = ScrolledText(area, bg=PANEL, fg=TEXTO, insertbackground=TEXTO,
                                  font=('Consolas', 11), wrap='word', relief='flat')
        self._texto_visible = False
        pie = tk.Frame(v, bg=FONDO)
        pie.pack(fill='x', padx=20, pady=14)
        for etiqueta, accion in (('−', lambda: self.ampliar(-.15)), ('+', lambda: self.ampliar(.15)),
                                 ('Ver listado', self.alternar_texto)):
            boton = ttk.Button(pie, text=etiqueta, command=accion)
            boton.pack(side='left', padx=(0, 6))
            if etiqueta == 'Ver listado':
                self.boton_listado = boton
        tk.Label(pie, text='Selecciona una sala · rueda para desplazar', fg=TENUE,
                 bg=FONDO, font=('Segoe UI', 9)).pack(side='left', padx=8)
        ttk.Button(pie, text='Volver a la cripta', command=self.cerrar).pack(side='right')
        self.dibujar()
        self.seleccionar(self.seleccion, redibujar=False)
        v.update_idletasks()
        self.centrar()

    def dibujar(self):
        c, z = self.canvas, self.zoom
        c.delete('all')
        ancho = max(740, max((p[0] for p in self.datos.posiciones), default=400) + 100) * z
        alto = max(500, max((p[1] for p in self.datos.posiciones), default=250) + 130) * z
        # Niebla decorativa fija: no depende de salas ocultas ni del tamaño real.
        tonos = ('#121e1e', '#13201f', '#142221', '#152422', '#162623', '#172724', '#182925', '#192a26')
        for x, y, rx, ry in ((100, 70, 190, 80), (630, 100, 230, 100), (380, 390, 260, 120)):
            for k, tono in enumerate(tonos):
                escala = 1-k*.065
                c.create_oval((x-rx*escala)*z, (y-ry*escala)*z,
                              (x+rx*escala)*z, (y+ry*escala)*z,
                              fill=tono, outline='', tags='niebla')
        c.create_text(ancho-90, 30, text='CONEXIONES', fill=AMARILLO, font=('Georgia', 9))
        for i, j, salida in self.datos.conexiones:
            x, y = self.datos.posiciones[i]
            xx, yy = self.datos.posiciones[j]
            recuerdo = salida[4]
            color = ROJO if recuerdo is True else (VERDE if recuerdo is False else '#738780')
            if i == j:
                c.create_line((x+62)*z, y*z, (x+100)*z, (y-66)*z,
                              (x-100)*z, (y-66)*z, (x-62)*z, y*z,
                              smooth=True, fill=color, arrow='last', tags='conexion')
                if self.seleccion == i:
                    c.create_text(x*z, (y-62)*z, text=f'{salida[0]} · {salida[2]}',
                                  fill=color, font=('Segoe UI', 9), tags='costo')
                continue
            dx, dy = xx-x, yy-y
            distancia = max(1, (dx*dx+dy*dy)**.5)
            corte = min(62/max(1, abs(dx)), 31/max(1, abs(dy)))
            desvio = 4 if i < j else -4
            ox, oy = -dy/distancia*4, dx/distancia*4
            c.create_line((x+corte*dx+ox)*z, (y+corte*dy+oy)*z,
                          (xx-corte*dx+ox)*z, (yy-corte*dy+oy)*z, fill=color,
                          width=1.5, arrow='last', dash=(4, 4) if recuerdo is not False else (), tags='conexion')
            if self.seleccion == i:
                mx, my = (x+xx)/2*z, ((y+yy)/2+desvio)*z
                c.create_rectangle(mx-33, my-10, mx+33, my+10, fill='#111c1c', outline='')
                c.create_text(mx, my, text=f'{salida[0]} · {salida[2]}', fill=color,
                              font=('Segoe UI', 9), tags='costo')
        for i, (identidad, estado, nombre, _) in enumerate(self.datos.registros):
            x, y = (n*z for n in self.datos.posiciones[i])
            w, h = 62*z, 31*z
            tag = f'sala_{i}'
            actual, destino = identidad == self.actual, identidad == self.destino
            borde = AMARILLO if actual else (VERDE if estado == 2 else '#667b75')
            if i == self.seleccion:
                c.create_rectangle(x-w-5, y-h-5, x+w+5, y+h+5, outline='#b7a273', width=1)
            c.create_rectangle(x-w, y-h, x+w, y+h, fill='#293f37' if estado == 2 else '#26302f',
                               outline=borde, width=2 if actual else 1, dash=() if estado == 2 else (3, 3), tags=tag)
            limite = max(6, int(13*min(z, 1)))
            texto = ((str(nombre)[:limite]+'…') if len(str(nombre)) > limite else str(nombre)) if estado == 2 else '?'
            c.create_text(x, y-8*z, text=texto, fill=TEXTO if estado == 2 else TENUE,
                          font=('Georgia', max(9, int(11*z))), tags=tag)
            c.create_text(x, y+12*z, text=f'Sala {identidad}', fill=AMARILLO if actual else TENUE,
                          font=('Segoe UI', max(8, int(9*z))), tags=tag)
            if actual or destino:
                c.create_text(x, y-h-16, text='◉ ESTÁS AQUÍ' if actual else '◇ DESTINO',
                              fill=AMARILLO, font=('Segoe UI', 9, 'bold'), tags=tag)
            c.tag_bind(tag, '<Button-1>', lambda _, indice=i: self.seleccionar(indice))
        if not self.datos.registros:
            c.create_text(370, 220, text='La memoria aún no dibuja caminos.', fill=TENUE, font=('Georgia', 16))
        c.configure(scrollregion=(0, 0, ancho, alto))

    def seleccionar(self, indice, redibujar=True):
        self.seleccion = indice
        if indice is None:
            self.titulo.configure(text='Mapa vacío')
            self.boton_viajar.configure(state='disabled')
            return
        identidad, estado, nombre, salidas = self.datos.registros[indice]
        self.titulo.configure(text=nombre if estado == 2 else 'Sala avistada')
        lineas = [f'Sala {identidad}', 'Explorada' if estado == 2 else 'Aún no has entrado aquí.']
        for direccion, destino, costo, puerta, recuerdo in salidas:
            memoria = 'abierta' if recuerdo is False else ('cerrada' if recuerdo is True else 'sin observar')
            lineas.append(f'\n{direccion} → {destino} · costo {costo}' + (f'\nPuerta {memoria}' if puerta is not None else ''))
        self.detalle.configure(text='\n'.join(lineas))
        self.boton_viajar.configure(state='normal' if estado == 2 and identidad != self.actual else 'disabled')
        if redibujar:
            self.dibujar()

    def centrar(self):
        indice = next((i for i, r in enumerate(self.datos.registros) if r[0] == self.actual), None)
        if indice is None:
            return
        x, y = self.datos.posiciones[indice]
        limites = tuple(float(v) for v in self.canvas.cget('scrollregion').split())
        self.canvas.xview_moveto(max(0, (x*self.zoom-self.canvas.winfo_width()/2)/max(1, limites[2])))
        self.canvas.yview_moveto(max(0, (y*self.zoom-self.canvas.winfo_height()/2)/max(1, limites[3])))

    def ampliar(self, cambio):
        self.zoom = min(1.6, max(.65, self.zoom+cambio))
        self.dibujar()

    def alternar_texto(self):
        self._texto_visible = not self._texto_visible
        self.boton_listado.configure(text='Ver mapa' if self._texto_visible else 'Ver listado')
        if self._texto_visible:
            self.cuadro.pack_forget()
            self.texto.configure(state='normal')
            self.texto.delete('1.0', 'end')
            for identidad, estado, nombre, salidas in self.datos.registros:
                self.texto.insert('end', f'Sala {identidad} · {nombre if estado == 2 else "Avistada (?)"}\n')
                for d, destino, costo, puerta, recuerdo in salidas:
                    memoria = 'abierta' if recuerdo is False else ('cerrada' if recuerdo is True else 'sin observar')
                    self.texto.insert('end', f'  {d} → {destino} | costo {costo}' + (f' | puerta {memoria} (recuerdo)' if puerta is not None else '') + '\n')
                self.texto.insert('end', '\n')
            self.texto.configure(state='disabled')
            self.texto.pack(fill='both', expand=True)
        else:
            self.texto.pack_forget()
            self.cuadro.pack(fill='both', expand=True)

    def viajar(self):
        if self.seleccion is not None:
            identidad, estado, _, __ = self.datos.registros[self.seleccion]
            if estado == 2 and identidad != self.actual:
                self.comando = f'ir a {identidad}'
                self.cerrar()

    def cerrar(self):
        self.ventana.destroy()

    def mostrar(self):
        self.ventana.grab_set()
        self.ventana.wait_window()
        return self.comando
