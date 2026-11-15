"""Campo inverso propio, invalidado por objetivo y estado de puertas."""
from types import SimpleNamespace
from modelo.rutas import EspacioBusqueda, HeapRutas, ArcoTerreno, buscar_ruta

class RutasCompartidas:
    """Alternativa experimental: campo inverso completo por época/objetivo."""
    def __init__(self, grafo):
        self.grafo = grafo
        filas = [[] for _ in grafo.ids]
        for fila in grafo.adyacencias:
            for a in fila:
                filas[a.destino].append(ArcoTerreno(a.destino, a.origen, a.direccion, a.costo, a.puerta))
        self.inverso = SimpleNamespace(ids=grafo.ids, adyacencias=filas)
        self.espacio = EspacioBusqueda(grafo.ids)
        self.heap = HeapRutas(self.espacio)
        self.clave = None

    def buscar(self, origen, destino, rango, epoca):
        if self.clave != (destino, epoca):
            buscar_ruta(self.inverso, self.espacio, self.heap, destino, -1, None)
            self.clave = (destino, epoca)
        etiqueta = self.espacio.etiqueta(origen)
        if etiqueta is None or (rango is not None and etiqueta[0] > rango):
            return None
        elegida = None
        for a in self.grafo.adyacencias[origen]:
            restante = self.espacio.etiqueta(a.destino)
            if not a.puerta.get('cerrada', False) and restante is not None and a.costo + restante[0] == etiqueta[0]:
                if elegida is None or self.grafo.ids[a.destino] < self.grafo.ids[elegida.destino]:
                    elegida = a
        if elegida is None:
            return None
        return elegida.destino, elegida.direccion, elegida.costo, etiqueta[0]

