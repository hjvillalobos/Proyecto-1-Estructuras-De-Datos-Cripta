"""Datos históricos de una operación local; no muta inventario ni historia."""


def _id(nodo):
    if nodo is None or nodo.objeto is None:
        return None
    identidad = nodo.objeto.id_instancia
    if type(identidad) is not str or not identidad:
        raise ValueError('La instancia requiere un identificador textual.')
    return identidad


def _meta(inv):
    return (inv.capacidad_max, inv.tamaño, _id(inv.cabeza.siguiente), _id(inv.cola.anterior),
            _id(inv.cursor), _id(inv.arma_equipada), _id(inv.armadura_equipada))


def _valor(nodo):
    if not nodo.en_inventario:
        return None
    objeto = nodo.objeto
    return (objeto.tipo_catalogo, objeto.ubicacion, objeto.sala, objeto.encendida,
            _id(nodo.anterior), _id(nodo.siguiente))


def campos_iniciales(inventario):
    """Base O(n), solo al iniciar historia; IDs únicos son precondición."""
    campos = [('inventario_estado', _meta(inventario))]
    nodo = inventario.cabeza.siguiente
    while nodo is not inventario.cola:
        campos.append(('inventario_nodo:' + _id(nodo), _valor(nodo)))
        nodo = nodo.siguiente
    return tuple(campos)


class CapturaInventario:
    """Preparar antes de una operación, terminar después y descartar.

    Objetivo: nodo que se quita/mueve/modifica; por defecto cursor. Recoger
    requiere pasar su nodo devuelto a terminar. No agrupa varias operaciones,
    no admite mutación concurrente ni cambios de identidad. Pertenece a C;
    las claves propuestas aún deben acordarse con D para la presentación.
    """

    def __init__(self, inventario, nodo=None):
        self._inventario = inventario
        self._usada = False
        self._meta = _meta(inventario)
        nodos = []
        for centro in (nodo if nodo is not None else inventario.cursor,
                       inventario.cabeza.siguiente, inventario.cola.anterior):
            if centro is None or centro.objeto is None:
                continue
            for candidato in (centro.anterior, centro, centro.siguiente):
                if (candidato is not None and candidato.objeto is not None
                        and not any(candidato is previo for previo in nodos)):
                    nodos.append(candidato)
        self._nodos = tuple(nodos)
        self._ids = tuple(_id(n) for n in nodos)
        self._antes = tuple(_valor(n) for n in nodos)

    def terminar(self, nuevo=None):
        """Devuelve deltas de D en O(1); no registra una acción ni deshace."""
        from modelo.snapshots import CambioHistorico, ValorHistorico
        if self._usada:
            raise ValueError('La captura ya fue terminada.')
        cambios = []
        def agregar(clave, antes, despues):
            if antes != despues:
                cambios.append(CambioHistorico(clave, ValorHistorico(antes is not None, antes),
                                                ValorHistorico(despues is not None, despues)))
        agregar('inventario_estado', self._meta, _meta(self._inventario))
        for nodo, identidad, antes in zip(self._nodos, self._ids, self._antes):
            if _id(nodo) != identidad:
                raise ValueError('La identidad de un nodo cambió durante la captura.')
            agregar('inventario_nodo:' + identidad, antes, _valor(nodo))
        if nuevo is not None:
            if any(nuevo is n for n in self._nodos):
                raise ValueError('El nodo indicado no es nuevo.')
            if not nuevo.en_inventario or _id(nuevo) in self._ids:
                raise ValueError('El nodo nuevo debe estar insertado y tener identidad propia.')
            agregar('inventario_nodo:' + _id(nuevo), None, _valor(nuevo))
        if self._inventario.tamaño > self._meta[1] and nuevo is None:
            raise ValueError('Debe entregar el nodo devuelto por recoger.')
        if abs(self._inventario.tamaño - self._meta[1]) > 1:
            raise ValueError('La captura admite una sola operación local.')
        self._usada = True
        self._nodos = ()
        self._inventario = None
        return tuple(cambios)
