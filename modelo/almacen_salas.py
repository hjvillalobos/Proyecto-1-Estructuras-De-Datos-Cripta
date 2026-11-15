"""RF-02: almacenamiento propio por ID; sin reserva por el mayor ID.

La longitud y la iteración abarcan solo los valores existentes; limite_ids
expone por separado el límite lógico para los guardas heredados.
"""


class TablaPorId:
    def __init__(self, ids, fabrica):
        self.ids = tuple(ids)  # Entrada ordenada y única del grafo validado.
        self.valores = [fabrica() for _ in self.ids]
        # Índice radix propio: ocho niveles como máximo para IDs uint32 del
        # formato binario. Consultar vecinos no depende de la cantidad de salas.
        self._bits = max(4, ((self.ids[-1].bit_length() + 3) // 4) * 4) if self.ids else 4
        self._raiz = [None] * 16
        for posicion, identidad in enumerate(self.ids):
            nodo = self._raiz
            for desplazamiento in range(self._bits - 4, 0, -4):
                digito = (identidad >> desplazamiento) & 15
                if nodo[digito] is None:
                    nodo[digito] = [None] * 16
                nodo = nodo[digito]
            nodo[identidad & 15] = posicion

    def __len__(self):
        return len(self.ids)

    def _indice(self, identidad):
        if type(identidad) is not int or identidad < 0:
            raise IndexError('ID de sala inválido.')
        if identidad.bit_length() > self._bits:
            return -1
        nodo = self._raiz
        for desplazamiento in range(self._bits - 4, 0, -4):
            nodo = nodo[(identidad >> desplazamiento) & 15]
            if nodo is None:
                return -1
        posicion = nodo[identidad & 15]
        return -1 if posicion is None else posicion

    def __getitem__(self, identidad):
        indice = self._indice(identidad)
        return None if indice < 0 else self.valores[indice]

    def __setitem__(self, identidad, valor):
        indice = self._indice(identidad)
        if indice < 0:
            raise IndexError('Sala inexistente.')
        self.valores[indice] = valor

    def __iter__(self):
        return iter(self.valores)


def crear_almacen(ids, fabrica):
    """Denso hasta cuatro posiciones por sala; compacto fuera de ese límite."""
    if ids and ids[-1] + 1 > 4 * len(ids):
        return TablaPorId(ids, fabrica)
    return [fabrica() for _ in range(ids[-1] + 1 if ids else 0)]


def limite_ids(almacen):
    if isinstance(almacen, TablaPorId):
        return almacen.ids[-1] + 1 if almacen.ids else 0
    return len(almacen)
