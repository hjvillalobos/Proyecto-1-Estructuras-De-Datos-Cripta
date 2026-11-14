"""T029: resolución topológica previa a sincronizar extremos de puertas."""

import unittest

from modelo.rutas import EmparejamientoSalida, EstadoEmparejamiento, GrafoTerreno
from modelo.tipos import Sala


class TestEmparejamientoSalidas(unittest.TestCase):
    def test_retorno_unico_en_ambos_sentidos_sin_modificar_descriptores(self):
        ida = {"sala": 80, "cerrada": True, "llave": "bronce"}
        vuelta = {"sala": 12}
        grafo = GrafoTerreno([Sala(80, "B", {"N": vuelta}), Sala(12, "A", {"E": ida})])

        self.assertEqual(grafo.resolver_retorno(12, "E"),
                         EmparejamientoSalida(EstadoEmparejamiento.EMPAREJADA, (80, "N")))
        self.assertEqual(grafo.resolver_retorno(80, "N"),
                         EmparejamientoSalida(EstadoEmparejamiento.EMPAREJADA, (12, "E")))
        self.assertEqual(ida, {"sala": 80, "cerrada": True, "llave": "bronce"})
        self.assertEqual(vuelta, {"sala": 12})

    def test_salida_sin_retorno_sigue_siendo_transitable(self):
        from modelo.rutas import ContextoRutasReales

        contexto = ContextoRutasReales([Sala(12, "A", {"E": {"sala": 80}}), Sala(80, "B", {})])
        grafo = contexto.grafo
        self.assertEqual(grafo.resolver_retorno(12, "E"),
                         EmparejamientoSalida(EstadoEmparejamiento.SIN_RETORNO))
        self.assertEqual(contexto.buscar(grafo.indice(12), grafo.indice(80), 100),
                         (grafo.indice(80), "E", 100, 100))

    def test_paralelas_no_se_emparejan_por_direccion_llave_o_costo(self):
        origen = Sala(12, "A", {"E": {"sala": 80, "costo": 150, "llave": "bronce"},
                                "N": {"sala": 80, "costo": 200, "llave": "plata"}})
        retornos = {"O": {"sala": 12, "costo": 150, "llave": "bronce"},
                    "S": {"sala": 12, "costo": 200, "llave": "plata"}}
        for direcciones in (("O",), ("O", "S"), ("S", "O")):
            with self.subTest(retornos=direcciones):
                destino = Sala(80, "B", {d: retornos[d] for d in direcciones})
                grafo = GrafoTerreno([origen, destino])
                for sala in (origen, destino):
                    for direccion in sala.salidas:
                        self.assertEqual(grafo.resolver_retorno(sala.id, direccion),
                                         EmparejamientoSalida(EstadoEmparejamiento.AMBIGUA))
