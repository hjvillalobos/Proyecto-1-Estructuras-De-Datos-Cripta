"""T039 / P2: localidad de FR-008, FR-010, NFR-002 y NFR-005."""

import tracemalloc
import unittest

from modelo.rutas import EspacioBusqueda, GrafoTerreno, HeapRutas, buscar_ruta
from tests.datos_terreno_cazador import crear_salas
from tests.test_rutas_cazador import referencia_caminos_simples


class ArregloObservado(list):
    """Cuenta elementos leídos o escritos sin cambiar sus valores."""

    lecturas = 0
    escrituras = 0

    def __iter__(self):
        for valor in super().__iter__():
            self.lecturas += 1
            yield valor

    def __getitem__(self, indice):
        self.lecturas += self._cantidad(indice)
        return super().__getitem__(indice)

    def __setitem__(self, indice, valor):
        self.escrituras += self._cantidad(indice)
        super().__setitem__(indice, valor)

    def _cantidad(self, indice):
        if isinstance(indice, slice):
            return len(range(*indice.indices(len(self))))
        return 1


class FronteraObservada(HeapRutas):
    def iniciar(self):
        self.extraidos = 0
        self.descartados = 0
        super().iniciar()

    def extraer(self):
        resultado = super().extraer()
        self.extraidos += 1
        return resultado

    def finalizar(self):
        pendientes = len(self)
        super().finalizar()
        self.descartados = pendientes - len(self)


IDS_LOCALES = (90, 7, 3, 80, 50)
CONEXIONES_LOCALES = (
    (0, "E", 1, "O", 1, False),
    (1, "N", 3, "S", 3, False),
    (0, "N", 2, "S", 2, False),
    (2, "E", 3, "O", 2, False),
    (0, "S", 4, "N", 4, False),
)
LIMITE = 4
CAMPOS_AUXILIARES = ("ids", "_marcas", "_distancias", "_primeros",
                    "_posiciones", "_cerrados")


def preparar_mapa(exteriores):
    ids = list(IDS_LOCALES) + [1000 + i for i in range(exteriores)]
    conexiones = list(CONEXIONES_LOCALES)
    # El único enlace al exterior ya cuesta 6 desde el origen.
    conexiones.append((1, "E", len(IDS_LOCALES), "O", 5, False))
    conexiones.extend(
        (i, "E", i + 1, "O", 1, False)
        for i in range(len(IDS_LOCALES), len(ids) - 1)
    )
    grafo = GrafoTerreno(crear_salas(ids, conexiones))
    espacio = EspacioBusqueda(grafo.ids)
    grafo.adyacencias = ArregloObservado(grafo.adyacencias)
    for campo in CAMPOS_AUXILIARES:
        setattr(espacio, campo, ArregloObservado(getattr(espacio, campo)))
    return grafo, espacio, FronteraObservada(espacio)


class PruebasLocalidadRutas(unittest.TestCase):
    def medir_consulta(self, grafo, espacio, frontera, destino):
        origen_indice, destino_indice = grafo.indice(90), grafo.indice(destino)
        auxiliares = tuple(getattr(espacio, campo) for campo in CAMPOS_AUXILIARES)
        observados = (grafo.adyacencias, *auxiliares)
        for arreglo in observados:
            arreglo.lecturas = arreglo.escrituras = 0

        iniciada_aqui = not tracemalloc.is_tracing()
        if iniciada_aqui:
            tracemalloc.start()
        try:
            tracemalloc.reset_peak()
            inicial = tracemalloc.get_traced_memory()[0]
            resultado = buscar_ruta(
                grafo, espacio, frontera, origen_indice, destino_indice, LIMITE,
            )
            pico = tracemalloc.get_traced_memory()[1] - inicial
        finally:
            if iniciada_aqui:
                tracemalloc.stop()

        self.assertEqual(len(frontera), 0)
        self.assertIs(grafo.adyacencias, observados[0])
        for campo, arreglo in zip(CAMPOS_AUXILIARES, auxiliares):
            self.assertIs(getattr(espacio, campo), arreglo)
        if resultado is not None:
            indice, direccion, costo_paso, total = resultado
            resultado = (grafo.ids[indice], direccion, costo_paso, total)
        operaciones = (
            frontera.extraidos, grafo.adyacencias.lecturas,
            sum(arreglo.lecturas for arreglo in auxiliares),
            sum(arreglo.escrituras for arreglo in auxiliares),
            frontera.descartados,
        )
        return resultado, operaciones, pico

    def test_t039_trabajo_local_con_exterior_creciente(self):
        locales = crear_salas(IDS_LOCALES, CONEXIONES_LOCALES)
        esperado = referencia_caminos_simples(locales, 90, 80)
        self.assertEqual(esperado, (3, "N", 2, LIMITE))
        for destino, ruta in ((80, esperado), (1000, None)):
            for exteriores in (1, 64, 8192):
                with self.subTest(destino=destino, exteriores=exteriores):
                    # Preparación y reserva de arreglos fuera de la consulta.
                    grafo, espacio, frontera = preparar_mapa(exteriores)
                    resultado, operaciones, pico = self.medir_consulta(
                        grafo, espacio, frontera, destino,
                    )
                    self.assertEqual(resultado, ruta)
                    extraidos, _, _, _, descartados = operaciones
                    self.assertLessEqual(extraidos, len(IDS_LOCALES))
                    self.assertEqual(descartados, 1 if ruta is not None else 0)
                    if exteriores == 1:
                        trabajo_local, pico_local = operaciones, pico
                    else:
                        self.assertEqual(operaciones, trabajo_local)
                        # Holgura para objetos temporales de Python, menor
                        # que reservar un arreglo proporcional al mapa mayor.
                        self.assertLessEqual(pico, pico_local + 4096)
