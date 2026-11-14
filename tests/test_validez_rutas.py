"""T029/T033: retornos topológicos y validez de consultas de rutas reales."""

import unittest

from modelo.rutas import ContextoRutasReales, EmparejamientoSalida, EstadoEmparejamiento, GrafoTerreno
from modelo.tipos import Sala
from tests.datos_terreno_cazador import motor_terreno
from tests.test_turno_cazador import partida_cazador


class TestValidezConsultasReales(unittest.TestCase):
    def test_t029_recalcula_con_cierre_apertura_y_cambio_de_objetivo(self):
        """T5/A6: las consultas reutilizadas leen el estado actual de cada arco."""
        este = {"sala": 20, "costo": 100}
        norte = {"sala": 10, "costo": 100, "cerrada": True}
        contexto = ContextoRutasReales([
            Sala(1, "Origen", {"E": este, "N": norte}),
            Sala(10, "Norte", {"E": {"sala": 30, "costo": 100}}),
            Sala(20, "Este", {"N": {"sala": 30, "costo": 100}}),
            Sala(30, "Destino", {}),
        ])
        origen, vecino_norte, vecino_este, objetivo = map(contexto.grafo.indice, (1, 10, 20, 30))

        self.assertEqual(contexto.buscar(origen, objetivo, 200), (vecino_este, "E", 100, 200))
        norte["cerrada"] = False
        self.assertEqual(contexto.buscar(origen, objetivo, 200), (vecino_norte, "N", 100, 200))
        self.assertEqual(contexto.buscar(origen, vecino_este, 200), (vecino_este, "E", 100, 100))
        norte["cerrada"] = True
        self.assertEqual(contexto.buscar(origen, objetivo, 200), (vecino_este, "E", 100, 200))
        este["cerrada"] = True
        self.assertIsNone(contexto.buscar(origen, objetivo, 200))

    def test_t033_cambiar_velocidad_reprograma_sin_alterar_distancias(self):
        with partida_cazador(350) as (motor, cazador, _):
            contexto = motor._rutas_reales
            origen, vecino, objetivo = map(contexto.grafo.indice, (100, 101, 102))
            ruta = (vecino, "E", 250, 350)
            self.assertEqual(contexto.buscar(origen, objetivo, 350), ruta)
            anterior = cazador.evento_pendiente
            self.assertEqual(anterior.tiempo, 100)

            motor.cambiar_velocidad(cazador, 200)

            self.assertTrue(anterior.cancelado)
            nuevo = cazador.evento_pendiente
            self.assertEqual(nuevo.tiempo, 50)
            self.assertGreater(nuevo.secuencia, anterior.secuencia)
            self.assertEqual(contexto.buscar(origen, objetivo, 350), ruta)
            self.assertIsNone(contexto.buscar(origen, objetivo, 349))

    def test_t033_ocupacion_y_muerte_no_bloquean_una_sala_intermedia(self):
        with motor_terreno(100) as motor:
            contexto = motor._rutas_reales
            origen, vecino, objetivo = map(contexto.grafo.indice, (100, 101, 102))
            ruta = (vecino, "E", 100, 200)
            enemigo = motor.enemigos_por_sala[101][0]
            self.assertGreater(enemigo.vida, 0)
            self.assertEqual(contexto.buscar(origen, objetivo, 200), ruta)

            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(motor.jugador.posicion_actual, 101)
            self.assertGreater(enemigo.vida, 0)
            self.assertEqual(contexto.buscar(origen, objetivo, 200), ruta)

            motor.jugador.ataque = enemigo.vida + enemigo.defensa
            self.assertTrue(motor.ejecutar("atacar", enemigo.id_instancia).ok)
            self.assertEqual(enemigo.vida, 0)
            self.assertIsNone(enemigo.evento_pendiente)
            self.assertEqual(contexto.buscar(origen, objetivo, 200), ruta)


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
