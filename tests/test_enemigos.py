# tests/test_enemigos.py

import random
import unittest
from modelo.tipos import Sala, InstanciaEnemigo
from modelo.rastro import RegistroRastro
from modelo.enemigos import decidir_accion, ACCION_ATACAR, ACCION_MOVER, ACCION_ESPERAR


def _enemigo(comportamiento):
    return InstanciaEnemigo(
        vida=10, vida_max=10, ataque=3, defensa=1, velocidad=100, tiempo_siguiente=0,
        id_instancia="e-1", tipo_catalogo="ent_prueba", comportamiento=comportamiento,
    )


class TestDecidirAccion(unittest.TestCase):

    def setUp(self):
        self.rastro = RegistroRastro(salas_total=5)
        self.azar = random.Random(42)

    def test_cualquier_comportamiento_ataca_si_comparte_sala(self):
        sala = Sala(id=1, nombre="Cripta", salidas={})
        for comportamiento in ("guardian", "errante", "rastreador"):
            enemigo = _enemigo(comportamiento)
            accion, _dato = decidir_accion(enemigo, sala, True, self.rastro, self.azar, tiempo_actual=0)
            self.assertEqual(accion, ACCION_ATACAR)

    def test_guardian_espera_si_jugador_no_esta(self):
        sala = Sala(id=1, nombre="Cripta", salidas={"N": {"sala": 2}})
        enemigo = _enemigo("guardian")
        accion, _dato = decidir_accion(enemigo, sala, False, self.rastro, self.azar, tiempo_actual=0)
        self.assertEqual(accion, ACCION_ESPERAR)

    def test_errante_espera_sin_salidas(self):
        sala = Sala(id=1, nombre="Cripta", salidas={})
        enemigo = _enemigo("errante")
        accion, _dato = decidir_accion(enemigo, sala, False, self.rastro, self.azar, tiempo_actual=0)
        self.assertEqual(accion, ACCION_ESPERAR)

    def test_errante_ignora_salidas_cerradas(self):
        sala = Sala(id=1, nombre="Cripta", salidas={"N": {"sala": 2, "cerrada": True}})
        enemigo = _enemigo("errante")
        accion, _dato = decidir_accion(enemigo, sala, False, self.rastro, self.azar, tiempo_actual=0)
        self.assertEqual(accion, ACCION_ESPERAR)

    def test_errante_se_mueve_por_una_salida_abierta(self):
        sala = Sala(id=1, nombre="Cripta", salidas={"N": {"sala": 2}})
        enemigo = _enemigo("errante")
        accion, direccion = decidir_accion(enemigo, sala, False, self.rastro, self.azar, tiempo_actual=0)
        self.assertEqual(accion, ACCION_MOVER)
        self.assertEqual(direccion, "N")

    def test_rastreador_sigue_el_rastro_mas_fresco(self):
        sala = Sala(id=1, nombre="Cripta", salidas={"N": {"sala": 2}, "S": {"sala": 3}})
        self.rastro.marcar_visita(2, 50)
        self.rastro.marcar_visita(3, 90)
        enemigo = _enemigo("rastreador")

        accion, direccion = decidir_accion(enemigo, sala, False, self.rastro, self.azar, tiempo_actual=100)
        self.assertEqual(accion, ACCION_MOVER)
        self.assertEqual(direccion, "S")

    def test_rastreador_espera_si_ningun_rastro_es_fresco(self):
        sala = Sala(id=1, nombre="Cripta", salidas={"N": {"sala": 2}})
        self.rastro.marcar_visita(2, 0)
        enemigo = _enemigo("rastreador")

        accion, _dato = decidir_accion(enemigo, sala, False, self.rastro, self.azar, tiempo_actual=1000)
        self.assertEqual(accion, ACCION_ESPERAR)


if __name__ == '__main__':
    unittest.main()
