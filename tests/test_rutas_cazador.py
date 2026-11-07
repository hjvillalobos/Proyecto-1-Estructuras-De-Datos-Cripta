"""T019: FR-008/009/010, NFR-005; T1–T4 y A4 con datos válidos.

Pruebas rojas del núcleo T021 aún ausente; no son decisión de cazador ni
contrato compartido con C. No usan mocks, búsqueda de referencia o skips.
"""

import unittest

from modelo import rutas
from tests.datos_terreno_cazador import crear_salas


class PruebasRutasCazador(unittest.TestCase):
    def comprobar_consulta(self, salas, origen, destino, limite, esperado):
        """Contrato interno propuesto para T021, con índices ya resueltos.

        buscar_ruta(grafo, espacio, frontera, origen, destino, limite) devuelve
        (primer_indice, direccion, costo_paso, costo_total) o None cuando no
        demuestra ruta dentro del límite. None no distingue desconexión de
        agotamiento del límite ni define políticas de datos null de entrada.
        """
        grafo = rutas.GrafoTerreno(salas)
        espacio = rutas.EspacioBusqueda(grafo.ids)
        frontera = rutas.HeapRutas(espacio)
        resultado = rutas.buscar_ruta(
            grafo, espacio, frontera, grafo.indice(origen),
            grafo.indice(destino), limite,
        )
        if esperado is None:
            self.assertIsNone(resultado)
        else:
            primer_id, direccion, costo_paso, costo_total = esperado
            self.assertEqual(resultado, (grafo.indice(primer_id), direccion,
                                         costo_paso, costo_total))

    def salas_con_alternativas(self, puerta_barata_cerrada=False):
        # 90–7–80: dos pasos, 500. 90–3–50–80: tres pasos, 300.
        return crear_salas([90, 7, 3, 50, 80], [
            (0, "E", 1, "O", 250, False),
            (1, "E", 4, "O", 250, False),
            (0, "N", 2, "S", 100, puerta_barata_cerrada),
            (2, "E", 3, "O", 100, False),
            (3, "N", 4, "S", 100, False),
        ])

    def test_t1_sin_ruta_abierta_por_puerta_cerrada(self):
        salas = crear_salas([90, 80], [(0, "E", 1, "O", 50, True)])
        self.comprobar_consulta(salas, 90, 80, 100, None)

    def test_destino_aislado_es_inalcanzable(self):
        salas = crear_salas([90, 7, 80], [(0, "E", 1, "O", 10, False)])
        self.comprobar_consulta(salas, 90, 80, 100, None)

    def test_t2_costo_101_supera_limite_100(self):
        salas = crear_salas([90, 80], [(0, "E", 1, "O", 101, False)])
        self.comprobar_consulta(salas, 90, 80, 100, None)

    def test_t3_tres_pasos_300_superan_dos_pasos_500(self):
        self.comprobar_consulta(self.salas_con_alternativas(), 90, 80, 600,
                                (3, "N", 100, 300))

    def test_a4_costo_igual_al_limite_admite_ruta(self):
        self.comprobar_consulta(self.salas_con_alternativas(), 90, 80, 300,
                                (3, "N", 100, 300))

    def test_puerta_cerrada_excluye_ruta_barata_pero_no_alternativa(self):
        self.comprobar_consulta(self.salas_con_alternativas(True), 90, 80, 500,
                                (7, "E", 250, 500))

    def test_t4_menor_primer_id_pese_a_orden_de_enumeracion(self):
        conexiones = [
            (0, "E", 1, "O", 150, False),
            (1, "E", 3, "O", 150, False),
            (0, "N", 2, "S", 100, False),
            (2, "E", 3, "S", 200, False),
        ]
        for invertir in (False, True):
            with self.subTest(enumeracion_invertida=invertir):
                orden = list(conexiones)
                if invertir:
                    orden.reverse()
                salas = crear_salas([90, 7, 3, 80], orden)
                self.comprobar_consulta(salas, 90, 80, 300,
                                        (3, "N", 100, 300))

    def test_empate_elige_menor_id_aunque_su_primer_arco_cueste_mas(self):
        salas = crear_salas([90, 7, 3, 80], [
            (0, "E", 1, "O", 100, False),
            (1, "E", 3, "O", 200, False),
            (0, "N", 2, "S", 200, False),
            (2, "E", 3, "S", 100, False),
        ])
        self.comprobar_consulta(salas, 90, 80, 300, (3, "N", 200, 300))

    def test_convergencia_propaga_mejora_del_primer_id(self):
        salas = crear_salas([90, 7, 3, 50, 80], [
            (0, "E", 1, "O", 1, False),
            (1, "E", 3, "O", 4, False),
            (0, "N", 2, "S", 4, False),
            (2, "E", 3, "S", 1, False),
            (3, "E", 4, "O", 1, False),
        ])
        self.comprobar_consulta(salas, 90, 80, 6, (3, "N", 4, 6))

    def test_ciclo_positivo_no_desvia_el_camino_minimo(self):
        salas = crear_salas([90, 7, 3, 80], [
            (0, "E", 1, "O", 3, False),
            (1, "N", 2, "S", 2, False),
            (2, "O", 0, "N", 4, False),
            (1, "E", 3, "O", 10, False),
            (2, "E", 3, "S", 1, False),
        ])
        self.comprobar_consulta(salas, 90, 80, 100, (3, "N", 4, 5))


if __name__ == "__main__":
    unittest.main()
