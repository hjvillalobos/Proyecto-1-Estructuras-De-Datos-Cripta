"""T023/T027: evidencia de FR-008/009/010/012 sobre las interfaces integradas."""

import unittest

from modelo.conocimiento_rutas import ConsultaRuta, PlanificadorConocido
from modelo.rutas import ContextoRutasReales
from modelo.tipos import Sala
from tests.test_conocimiento_rutas import crear


class PruebasContratoRutasC(unittest.TestCase):
    def test_llegada_ruta_valida_y_ausencia_en_fuente_filtrada(self):
        mapa = crear((10, 20, 30), (
            (10, 20, 2, None), (20, 30, 2, None), (10, 30, 90, 7),
        ))
        mapa.entrar(30)
        plan = PlanificadorConocido(mapa)

        self.assertEqual(plan.consultar(10, 10), ConsultaRuta("llegada", costo_total=0))
        self.assertEqual(plan.consultar(10, 30), ConsultaRuta("sin_ruta"))

        observacion = mapa.observar_puerta(10, 7, False)
        antes = mapa.mapa_conocido(), mapa.revision
        self.assertEqual(plan.consultar(10, 30), ConsultaRuta("paso", 30, "2", 90, 90))
        self.assertEqual((mapa.mapa_conocido(), mapa.revision), antes)
        mapa.revertir(observacion)
        self.assertEqual(plan.consultar(10, 30), ConsultaRuta("sin_ruta"))

    def test_agotar_limite_no_certifica_distancia_fuera_de_rango(self):
        contexto = ContextoRutasReales([
            Sala(10, "Entrada", {"E": {"sala": 20, "costo": 90}}),
            Sala(20, "Vecina", {"O": {"sala": 10, "costo": 90}}),
            Sala(30, "Aislada", {}),
        ])
        origen, vecino, aislada = map(contexto.grafo.indice, (10, 20, 30))

        self.assertIsNone(contexto.buscar(origen, vecino, 89))
        self.assertIsNone(contexto.buscar(origen, aislada, 89))
        self.assertEqual(contexto.buscar(origen, vecino, 90), (vecino, "E", 90, 90))
        self.assertIsNone(contexto.buscar(origen, aislada, None))
