"""T009: FR-010/014, NFR-002/005; fundamentos de T4/A7/P2, no cazador."""

from random import Random
import unittest

from modelo.rutas import EspacioBusqueda, HeapRutas


class PruebasHeapRutas(unittest.TestCase):
    def test_descenso_preserva_desempate_con_marca_de_origen(self):
        espacio, heap = self.crear_heap([8, 2, 4, 6, 0])
        for indice, distancia, primero in ((0, 1, 3), (1, 2, 0), (2, 2, None),
                                           (3, 2, None), (4, 3, 0)):
            heap.insertar_o_disminuir(indice, distancia, primero)
        for esperado in ((0, 1, 3), (2, 2, None), (3, 2, None), (1, 2, 0), (4, 3, 0)):
            self.assertEqual(heap.extraer(), esperado)
            self.comprobar_posiciones(espacio, heap)

    def crear_heap(self, ids):
        espacio = EspacioBusqueda(ids)
        heap = HeapRutas(espacio)
        heap.iniciar()
        return espacio, heap

    def comprobar_posiciones(self, espacio, heap):
        for posicion, indice in enumerate(heap._nodos):
            self.assertEqual(espacio.posicion(indice), posicion)

    def test_orden_total_distancia_primer_id_e_id_sala(self):
        espacio, heap = self.crear_heap([70, 10, 40, 2])
        for indice, distancia, primero in ((0, 9, 8), (1, 5, 7),
                                           (2, 5, 3), (3, 5, 3)):
            self.assertTrue(heap.insertar_o_disminuir(indice, distancia, primero))
        self.comprobar_posiciones(espacio, heap)
        self.assertEqual([heap.extraer() for _ in range(4)],
                         [(3, 5, 3), (2, 5, 3), (1, 5, 7), (0, 9, 8)])
        self.assertEqual(len(heap), 0)
        self.assertEqual([espacio.posicion(i) for i in range(4)], [-1] * 4)

    def test_disminucion_lexicografica_sin_duplicar_nodos(self):
        espacio, heap = self.crear_heap([90, 50, 10])
        heap.insertar_o_disminuir(0, 50, 70)
        heap.insertar_o_disminuir(1, 20, 80)
        heap.insertar_o_disminuir(2, 30, 60)
        self.assertTrue(heap.insertar_o_disminuir(0, 20, 3))
        self.assertFalse(heap.insertar_o_disminuir(0, 20, 3))
        self.assertFalse(heap.insertar_o_disminuir(0, 20, 4))
        self.assertFalse(heap.insertar_o_disminuir(0, 21, 1))
        self.assertEqual(len(heap), 3)
        self.comprobar_posiciones(espacio, heap)
        self.assertEqual(heap.extraer(), (0, 20, 3))
        self.assertTrue(heap.insertar_o_disminuir(2, 20, 7))
        self.assertEqual(heap.extraer(), (2, 20, 7))
        self.assertEqual(heap.extraer(), (1, 20, 80))

    def test_marcador_de_origen_no_es_id_inventado(self):
        _, heap = self.crear_heap([100, 1])
        heap.insertar_o_disminuir(0, 0, None)
        heap.insertar_o_disminuir(1, 1, 1)
        self.assertEqual(heap.extraer(), (0, 0, None))
        self.assertEqual(heap.extraer(), (1, 1, 1))

    def test_mejorar_solo_primer_id_reordena_con_distancia_igual(self):
        espacio, heap = self.crear_heap([90, 10, 50])
        heap.insertar_o_disminuir(0, 25, 7)
        heap.insertar_o_disminuir(1, 25, 3)
        heap.insertar_o_disminuir(2, 25, 9)
        self.assertTrue(heap.insertar_o_disminuir(2, 25, 2))
        self.assertEqual(espacio.etiqueta(2), (25, 2))
        self.comprobar_posiciones(espacio, heap)
        self.assertEqual([heap.extraer() for _ in range(3)],
                         [(2, 25, 2), (1, 25, 3), (0, 25, 7)])

    def test_generaciones_inhabilitan_etiquetas_posiciones_y_cierre(self):
        espacio, heap = self.crear_heap([17 + i * 1000003 for i in range(128)])
        heap.insertar_o_disminuir(127, 4, 17)
        heap.extraer()
        espacio.cerrar(127)
        self.assertTrue(espacio.esta_cerrado(127))
        arreglos = (espacio._marcas, espacio._distancias, espacio._primeros,
                    espacio._posiciones, espacio._cerrados)
        anteriores = [list(arreglo) for arreglo in arreglos]
        generacion = espacio.generacion
        heap.iniciar()
        self.assertEqual(espacio.generacion, generacion + 1)
        self.assertIsNone(espacio.etiqueta(127))
        self.assertEqual(espacio.posicion(127), -1)
        self.assertFalse(espacio.esta_cerrado(127))
        actuales = (espacio._marcas, espacio._distancias, espacio._primeros,
                    espacio._posiciones, espacio._cerrados)
        for anterior, actual, contenido in zip(arreglos, actuales, anteriores):
            self.assertIs(anterior, actual)
            self.assertEqual(actual, contenido)
        self.assertTrue(heap.insertar_o_disminuir(127, 200, 50))
        self.assertEqual(heap.extraer(), (127, 200, 50))

    def test_finalizar_frontera_antes_de_iniciar_otra_consulta(self):
        espacio, heap = self.crear_heap([90, 7, 2])
        heap.insertar_o_disminuir(0, 10, 7)
        heap.insertar_o_disminuir(2, 3, 2)
        with self.assertRaises(RuntimeError):
            heap.iniciar()
        heap.finalizar()
        self.assertEqual(len(heap), 0)
        self.assertEqual(espacio.posicion(0), -1)
        self.assertEqual(espacio.posicion(2), -1)
        heap.iniciar()
        self.assertIsNone(espacio.etiqueta(0))
        heap.insertar_o_disminuir(2, 40, 2)
        self.assertEqual(heap.extraer(), (2, 40, 2))

    def test_heap_vacio_y_espacio_sin_etiquetas_iniciales(self):
        espacio, heap = self.crear_heap([5])
        self.assertIsNone(espacio.etiqueta(0))
        self.assertFalse(espacio.esta_cerrado(0))
        with self.assertRaises(IndexError):
            heap.extraer()
        heap.finalizar()
        vacio, frontera = self.crear_heap([])
        self.assertEqual(vacio.ids, [])
        self.assertEqual(len(frontera), 0)

    def test_secuencia_sembrada_contra_referencia_lineal_independiente(self):
        for semilla in (17, 20261105):
            with self.subTest(semilla=semilla):
                azar = Random(semilla)
                ids = [7 + i * 101 for i in range(31, -1, -1)]
                espacio, heap = self.crear_heap(ids)
                mejores = [None] * len(ids)
                pendientes = [False] * len(ids)

                def extraer_referencia():
                    mejor = None
                    for indice, pendiente in enumerate(pendientes):
                        if pendiente and (mejor is None or
                                mejores[indice] + (ids[indice],) <
                                mejores[mejor] + (ids[mejor],)):
                            mejor = indice
                    if mejor is not None:
                        self.assertEqual(heap.extraer(), (mejor,) + mejores[mejor])
                        pendientes[mejor] = False
                        self.assertEqual(espacio.posicion(mejor), -1)

                for paso in range(700):
                    indice = azar.randrange(len(ids))
                    propuesta = (azar.randint(1, 10000), ids[azar.randrange(len(ids))])
                    mejora = mejores[indice] is None or propuesta < mejores[indice]
                    self.assertEqual(heap.insertar_o_disminuir(indice, *propuesta), mejora)
                    if mejora:
                        mejores[indice] = propuesta
                        pendientes[indice] = True
                    if paso % 3 == 0:
                        extraer_referencia()
                    self.assertEqual(len(heap), sum(pendientes))
                    self.comprobar_posiciones(espacio, heap)
                while any(pendientes):
                    extraer_referencia()
                self.assertEqual(len(heap), 0)


if __name__ == "__main__":
    unittest.main()
