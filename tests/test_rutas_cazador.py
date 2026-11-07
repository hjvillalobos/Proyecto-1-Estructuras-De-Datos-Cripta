"""T019/T026: FR-008/009/010/014, NFR-005; T1–T4, A4 y A7.

Pruebas del núcleo T021 y contraste exhaustivo en grafos sintéticos pequeños.
"""

import unittest

from modelo import rutas
from tests.datos_terreno_cazador import crear_salas


def referencia_caminos_simples(salas, origen, destino):
    """Enumera caminos abiertos sobre los descriptores originales de sala."""
    visitados = [origen]
    mejor = None

    def recorrer(sala_id, total, primer_paso):
        nonlocal mejor
        if sala_id == destino:
            candidato = (total, *primer_paso)
            if mejor is None or candidato[:2] < mejor[:2]:
                mejor = candidato
            return

        sala = next(sala for sala in salas if sala.id == sala_id)
        for direccion, salida in sala.salidas.items():
            vecino = salida["sala"]
            if salida.get("cerrada", False) or vecino in visitados:
                continue
            costo = salida.get("costo", 100)
            paso = (vecino, direccion, costo) if primer_paso is None else primer_paso
            visitados.append(vecino)
            recorrer(vecino, total + costo, paso)
            visitados.pop()

    recorrer(origen, 0, None)
    if mejor is None:
        return None
    total, primer_id, direccion, costo_paso = mejor
    return primer_id, direccion, costo_paso, total


def conexiones_cuadricula():
    conexiones = []
    for fila in range(3):
        for columna in range(3):
            origen = fila * 3 + columna
            if columna < 2:
                conexiones.append((origen, "E", origen + 1, "O", 1, False))
            if fila < 2:
                conexiones.append((origen, "S", origen + 3, "N", 1, False))
    return conexiones


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

    def test_t026_seis_caminos_optimos_con_enumeraciones_distintas(self):
        ids = [90, 7, 34, 3, 22, 11, 65, 1, 80]
        conexiones = conexiones_cuadricula()
        ordenes = (conexiones, conexiones[::-1], conexiones[1::2] + conexiones[::2])
        for numero, orden in enumerate(ordenes):
            with self.subTest(enumeracion=numero):
                salas = crear_salas(ids, orden)
                # De esquina a esquina hay seis caminos de dos E y dos S.
                esperado = referencia_caminos_simples(salas, 90, 80)
                self.assertEqual(esperado, (3, "S", 1, 4))
                self.comprobar_consulta(salas, 90, 80, 4, esperado)
                self.comprobar_consulta(salas[::-1], 90, 80, 4, esperado)

    def test_t026_grafos_ponderados_con_puertas_cerradas_y_limites(self):
        ids = [90, 7, 34, 3, 22, 11, 65, 1, 80]
        for aislar_esquina in (False, True):
            conexiones = [
                (o, direccion, d, vuelta, 1 + i % 7,
                 i in (2, 8) or (aislar_esquina and (o == 0 or d == 0)))
                for i, (o, direccion, d, vuelta, _, _) in enumerate(conexiones_cuadricula())
            ]
            salas = crear_salas(ids, conexiones)
            for origen in ids:
                for destino in ids:
                    if origen == destino:
                        continue
                    with self.subTest(aislada=aislar_esquina, origen=origen,
                                      destino=destino):
                        esperado = referencia_caminos_simples(salas, origen, destino)
                        if esperado is None:
                            self.comprobar_consulta(salas, origen, destino, 56, None)
                        else:
                            total = esperado[3]
                            self.comprobar_consulta(salas, origen, destino, total, esperado)
                            if total > 1:
                                self.comprobar_consulta(salas, origen, destino, total - 1, None)


if __name__ == "__main__":
    unittest.main()
