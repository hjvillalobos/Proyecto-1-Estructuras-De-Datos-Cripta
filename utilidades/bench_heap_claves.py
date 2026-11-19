"""RF-01: comparación pareada con las comparaciones del heap anterior."""
from time import perf_counter_ns
from statistics import median
from modelo.rutas import GrafoTerreno, EspacioBusqueda, HeapRutas, buscar_ruta


class HeapAnterior(HeapRutas):
    def _clave(self, indice):
        distancia, primero = self.espacio.etiqueta(indice)
        return self._clave_etiqueta(distancia, primero) + (self.espacio.ids[indice],)

    def insertar_o_disminuir(self, indice, distancia, primer_id):
        espacio = self.espacio
        anterior = espacio.etiqueta(indice)
        if anterior is not None and self._clave_etiqueta(*anterior) <= self._clave_etiqueta(distancia, primer_id):
            return False
        posicion = espacio.posicion(indice)
        espacio._registrar(indice, distancia, primer_id)
        if posicion == -1:
            posicion = len(self._nodos)
            self._nodos.append(indice)
            espacio._posiciones[indice] = posicion
        self._subir(posicion)
        return True


def medir(salas, repeticiones=30):
    grafo = GrafoTerreno(salas)
    espacios = [EspacioBusqueda(grafo.ids) for _ in range(2)]
    heaps = [HeapAnterior(espacios[0]), HeapRutas(espacios[1])]
    tiempos = [[], []]
    for repeticion in range(repeticiones):
        # Alternar quién corre primero. Puertas idénticas y varias parejas.
        origen = repeticion % (len(salas) - 1)
        resultados = [None, None]
        for i in (0, 1) if repeticion % 2 == 0 else (1, 0):
            inicio = perf_counter_ns()
            resultados[i] = buscar_ruta(grafo, espacios[i], heaps[i], origen, len(salas) - 1, None)
            tiempos[i].append((perf_counter_ns() - inicio) / 1e6)
        if resultados[0] != resultados[1]:
            raise AssertionError('El heap optimizado cambió la decisión.')
    for nombre, muestras in zip(('anterior', 'claves retenidas'), tiempos):
        print(f'Heap {nombre}: mediana={median(muestras):.4f} ms máximo={max(muestras):.4f} ms muestras={len(muestras)}')
    print(f'Razón medianas anterior/nuevo={median(tiempos[0]) / median(tiempos[1]):.3f}; decisiones iguales.')
    return tiempos
