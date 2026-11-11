"""T007: FR-001/008/014, NFR-002/005; soporte de A2/A5/A7/P2."""

import unittest

from modelo.rutas import GrafoTerreno
from tests.datos_terreno_cazador import (
    SIN_COSTO_DECLARADO, crear_cadena, crear_salas,
)


class PruebasGrafoTerreno(unittest.TestCase):
    def test_indices_densos_con_ids_dispersos_y_entrada_desordenada(self):
        salas = crear_salas([9001, 3, 100000000003, 41], [
            (0, "E", 1, "O", 250, False),
            (1, "E", 2, "O", 1, True),
        ])
        grafo = GrafoTerreno(salas)
        self.assertEqual(grafo.ids, [3, 41, 9001, 100000000003])
        self.assertEqual(len(grafo.adyacencias), 4)
        for indice, identificador in enumerate(grafo.ids):
            self.assertEqual(grafo.indice(identificador), indice)
        self.assertEqual([s.id for s in salas], [9001, 3, 100000000003, 41])
        self.assertEqual(grafo.adyacencias[grafo.indice(41)], [])

    def test_resuelve_arcos_costos_simetria_y_referencia_sin_copiar_puerta(self):
        salas = crear_salas([50, 2], [(0, "E", 1, "O", 250, True)])
        grafo = GrafoTerreno(salas)
        origen, destino = grafo.indice(50), grafo.indice(2)
        arco = grafo.adyacencias[origen][0]
        vuelta = grafo.adyacencias[destino][0]
        self.assertEqual((arco.origen, arco.destino, arco.direccion, arco.costo),
                         (origen, destino, "E", 250))
        self.assertEqual((vuelta.destino, vuelta.costo), (origen, 250))
        self.assertIs(arco.puerta, salas[0].salidas["E"])
        self.assertTrue(arco.puerta["cerrada"])
        self.assertIsNot(arco.puerta, vuelta.puerta)

    def test_costo_ausente_100_sin_mutar_descriptor(self):
        salas = crear_salas([8, 1], [
            (0, "N", 1, "S", SIN_COSTO_DECLARADO, False),
        ])
        grafo = GrafoTerreno(salas)
        for vecinos in grafo.adyacencias:
            self.assertEqual(vecinos[0].costo, 100)
            self.assertNotIn("costo", vecinos[0].puerta)

    def test_grafo_vacio_y_sala_aislada(self):
        vacio = GrafoTerreno([])
        self.assertEqual(vacio.ids, [])
        self.assertEqual(vacio.adyacencias, [])
        aislado = GrafoTerreno(crear_salas([13], []))
        self.assertEqual(aislado.ids, [13])
        self.assertEqual(aislado.adyacencias, [[]])

    def test_cadena_reproducible_y_todas_las_conexiones_resueltas(self):
        for cantidad in (2, 17, 128):
            with self.subTest(cantidad=cantidad):
                salas = crear_cadena(cantidad, 20261105)
                copia = crear_cadena(cantidad, 20261105)
                self.assertEqual([(s.id, s.salidas) for s in salas],
                                 [(s.id, s.salidas) for s in copia])
                grafo = GrafoTerreno(salas)
                self.assertEqual(len(grafo.ids), cantidad)
                self.assertEqual(sum(len(v) for v in grafo.adyacencias),
                                 2 * (cantidad - 1))
                for sala in salas:
                    vecinos = grafo.adyacencias[grafo.indice(sala.id)]
                    for arco in vecinos:
                        self.assertGreaterEqual(arco.costo, 1)
                        self.assertEqual(grafo.ids[arco.destino],
                                         sala.salidas[arco.direccion]["sala"])
                        vueltas = grafo.adyacencias[arco.destino]
                        self.assertTrue(any(v.destino == arco.origen and
                                            v.costo == arco.costo for v in vueltas))


if __name__ == "__main__":
    unittest.main()
