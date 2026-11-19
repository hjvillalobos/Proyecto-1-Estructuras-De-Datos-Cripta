"""Aceptación de alternativas sintéticas T040–T044."""

import unittest
from unittest.mock import patch

from modelo.rutas import ContextoRutasReales
from tests.datos_terreno_cazador import crear_salas
from tests.test_rutas_cazador import conexiones_cuadricula, referencia_caminos_simples
from utilidades import bench_terreno_cazador as bench
from utilidades.bench_terreno_cazador import (
    AgendaIndexada, CacheConsultas, CampoInverso, buscar_individual,
    carga_sintetica, medir_agendas, medir_ciclo_motor, medir_localidad, medir_rutas,
)


class PruebasEvaluacionTerreno(unittest.TestCase):
    def test_cronometro_excluye_preparacion_y_liberacion(self):
        reloj = 0

        def avanzar(costo):
            nonlocal reloj
            reloj += costo

        with patch.object(bench, "perf_counter_ns", side_effect=lambda: reloj):
            medida = bench._medir_preparada(
                lambda: avanzar(100), lambda _: avanzar(7), 2,
                liberar=lambda _: avanzar(200),
            )
        self.assertEqual(medida["min_ns"], 7)
        self.assertEqual(medida["max_ns"], 7)
        self.assertEqual(reloj, 3 * (100 + 7 + 200))

    def test_lotes_excluyen_liberacion_de_todas_las_estrategias(self):
        medir = bench._medir_preparada
        revisados = []

        def comprobar(preparar, operar, repeticiones, *, liberar=None):
            if liberar is not None:
                preparados = preparar()
                operar(preparados)
                campo, cache = preparados
                if campo is not None:
                    self.assertIsNotNone(campo.etiquetas)
                if cache is not None:
                    self.assertTrue(cache.entradas)
                liberar(preparados)
                if campo is not None:
                    self.assertIsNone(campo.etiquetas)
                if cache is not None:
                    self.assertFalse(cache.entradas)
                revisados.append(preparados)
            return medir(preparar, operar, repeticiones, liberar=liberar)

        with patch.object(bench, "_medir_preparada", side_effect=comprobar):
            informe = medir_rutas(8, 3, None, True, 42, 1)
        self.assertEqual(len(revisados), 6)
        for lote in informe["lotes"].values():
            self.assertIn("liberacion_estrategia", lote)
        for nombre in ("cache_1", "cache_4"):
            self.assertEqual(informe["lotes"][nombre]["costos_cache"]["liberacion"]["operaciones"], 1)

    def test_carga_y_mediciones_sinteticas(self):
        self.assertEqual(carga_sintetica(8, 42), carga_sintetica(8, 42))
        informe = medir_rutas(8, 3, None, True, 42, 1)
        self.assertEqual((informe["V"], informe["E"], informe["H"]), (8, 14, 3))
        self.assertGreater(informe["lotes"]["inverso"]["aciertos"], 0)
        self.assertGreater(informe["lotes"]["cache_1"]["invalidaciones"], 0)
        self.assertGreater(informe["lotes"]["cache_4"]["reemplazos"], 0)

    def test_alternativas_con_oraculo_t026(self):
        conexiones = conexiones_cuadricula()
        salas = crear_salas(tuple(range(9)), conexiones)
        contexto = ContextoRutasReales(salas)
        grafo = contexto.grafo
        campo = CampoInverso(grafo)
        for epoca in (0, 1):
            salas[0].salidas["E"]["cerrada"] = bool(epoca)
            for destino in grafo.ids:
                for limite in (1, 4, None):
                    for origen in grafo.ids:
                        if origen == destino:
                            continue
                        esperado = referencia_caminos_simples(salas, origen, destino)
                        if esperado is not None:
                            vecino, direccion, paso, total = esperado
                            esperado = ((grafo.indice(vecino), direccion, paso, total)
                                        if limite is None or total <= limite else None)
                        a, b = grafo.indice(origen), grafo.indice(destino)
                        with self.subTest(epoca=epoca, origen=origen, destino=destino, limite=limite):
                            self.assertEqual(contexto.buscar(a, b, limite), esperado)
                            self.assertEqual(buscar_individual(grafo, a, b, limite), esperado)
                            self.assertEqual(buscar_individual(grafo, a, b, limite, con_heap=True), esperado)
                            self.assertEqual(campo.buscar(a, b, limite, epoca), esperado)

    def test_cache_distingue_rango_reemplazo_e_invalidez(self):
        cache = CacheConsultas(lambda *consulta: consulta, 1, instrumentar=True)
        self.assertEqual(cache.buscar(0, 2, 100, 0), (0, 2, 100))
        cache.buscar(0, 2, 100, 0)
        self.assertEqual(cache.buscar(0, 2, 101, 0), (0, 2, 101))
        cache.buscar(0, 2, 101, 1)
        self.assertEqual((cache.aciertos, cache.fallos, cache.reemplazos, cache.invalidaciones),
                         (1, 3, 1, 1))
        cache.liberar()
        self.assertEqual([cache.costos[fase]["operaciones"] for fase in
                          ("clave", "insercion", "reemplazo", "invalidacion", "liberacion")],
                         [4, 3, 1, 1, 1])
        self.assertFalse(cache.entradas)

    def test_localidad_separa_expansion_de_inicializacion(self):
        menor, mayor = medir_localidad((128, 512), 42, 1)
        self.assertIsNotNone(menor["ruta"])
        self.assertEqual(menor["ruta"], mayor["ruta"])
        self.assertEqual(menor["expandidos"], mayor["expandidos"])
        self.assertEqual((menor["celdas"], mayor["celdas"]), (256, 1024))

    def test_ciclo_completo_compara_agendas_con_cazadores(self):
        agendas = medir_ciclo_motor(24, 20261113, 1)["agendas"]
        actual, candidata = agendas["ColaEventos"], agendas["AgendaIndexada"]
        self.assertGreater(actual["N_fisico_inicial"], candidata["N_fisico_inicial"])
        self.assertEqual((actual["reloj"], candidata["reloj"]), (100, 100))
        self.assertEqual(actual["eventos_procesados"], candidata["eventos_procesados"])
        self.assertGreater(actual["eventos_procesados"], 48)

    def test_agenda_conserva_eventos_y_frontera(self):
        agenda = AgendaIndexada()
        primero = agenda.insertar(5, "turno", "a")
        segundo = agenda.insertar(5, "turno", "b")
        reemplazo = agenda.reprogramar(primero, 5)
        self.assertTrue(primero.cancelado)
        self.assertFalse(primero.en_cola)
        self.assertIsNone(agenda.extraer_minimo(hasta=4))
        self.assertIs(agenda.extraer_minimo(hasta=5), segundo)
        self.assertIs(agenda.extraer_minimo(hasta=5), reemplazo)
        informe = medir_agendas(12, 48, 42, 1)
        self.assertEqual(informe["ColaEventos"]["N_fisico"], 60)
        self.assertEqual(informe["AgendaIndexada"]["N_fisico"], 12)
        self.assertEqual(informe["AgendaIndexada"]["N_valido"], 12)
