# tests/test_historial.py

import unittest
from types import SimpleNamespace
from modelo.rastro import RegistroRastro
from modelo.historial import HistorialRetroceso, HISTORIAL_MAX
from modelo.inventario import Inventario
from modelo.tipos import ObjetoInstancia


def _objeto(id_instancia, tipo_catalogo):
    return ObjetoInstancia(id_instancia=id_instancia, tipo_catalogo=tipo_catalogo, ubicacion="inventario")


class TestHistorialRetroceso(unittest.TestCase):

    def setUp(self):
        self.rastro = RegistroRastro(salas_total=5)
        self.historial = HistorialRetroceso(self.rastro)

    def test_pila_respeta_el_tope_de_historial_max(self):
        for i in range(HISTORIAL_MAX + 3):
            self.historial.iniciar_turno(reloj_actual=i * 100)
            self.historial.cerrar_turno()
        self.assertEqual(self.historial.cantidad_turnos(), HISTORIAL_MAX)

    def test_cerrar_turno_sin_iniciar_no_hace_nada(self):
        self.historial.cerrar_turno()
        self.assertEqual(self.historial.cantidad_turnos(), 0)

    def test_usar_pergamino_sin_turnos_devuelve_none(self):
        inventario = Inventario(capacidad_max=5)
        self.assertIsNone(self.historial.usar_pergamino(inventario, "itm_pergamino"))

    def test_revertir_restaura_vida_y_reloj(self):
        jugador = SimpleNamespace(vida=5)
        rata = SimpleNamespace(vida=0)

        self.historial.iniciar_turno(reloj_actual=100)
        self.historial.registrar_vida(jugador, vida_anterior=9)
        self.historial.registrar_vida(rata, vida_anterior=12)
        self.historial.cerrar_turno()

        inventario = Inventario(capacidad_max=5)
        reloj_anterior = self.historial.usar_pergamino(inventario, "itm_pergamino")

        self.assertEqual(reloj_anterior, 100)
        self.assertEqual(jugador.vida, 9)
        self.assertEqual(rata.vida, 12)

    def test_revertir_restaura_rastro(self):
        self.rastro.marcar_visita(2, 500)

        self.historial.iniciar_turno(reloj_actual=100)
        self.historial.registrar_rastro(2, tiempo_anterior=None)  # antes no tenía rastro
        self.historial.cerrar_turno()

        inventario = Inventario(capacidad_max=5)
        self.historial.usar_pergamino(inventario, "itm_pergamino")

        self.assertIsNone(self.rastro.tiempo_de(2))

    def test_revertir_reactiva_eventos_cancelados_y_cancela_los_creados(self):
        evento_creado = SimpleNamespace(cancelado=False)
        evento_cancelado = SimpleNamespace(cancelado=True)

        self.historial.iniciar_turno(reloj_actual=100)
        self.historial.registrar_evento_creado(evento_creado)
        self.historial.registrar_evento_cancelado(evento_cancelado)
        self.historial.cerrar_turno()

        inventario = Inventario(capacidad_max=5)
        self.historial.usar_pergamino(inventario, "itm_pergamino")

        self.assertTrue(evento_creado.cancelado)
        self.assertFalse(evento_cancelado.cancelado)

    def test_revertir_deshace_cambios_de_inventario_en_orden_inverso(self):
        inventario = Inventario(capacidad_max=5)
        orden_de_reversion = []

        self.historial.iniciar_turno(reloj_actual=100)
        self.historial.registrar_inventario(lambda: orden_de_reversion.append("primero"))
        self.historial.registrar_inventario(lambda: orden_de_reversion.append("segundo"))
        self.historial.cerrar_turno()

        self.historial.usar_pergamino(inventario, "itm_pergamino")

        self.assertEqual(orden_de_reversion, ["segundo", "primero"])

    def test_usar_pergamino_descuenta_uno_y_no_registra_ese_descuento(self):
        inventario = Inventario(capacidad_max=5)
        inventario.recoger(_objeto("p1", "itm_pergamino"))
        inventario.recoger(_objeto("p2", "itm_pergamino"))

        self.historial.iniciar_turno(reloj_actual=100)
        self.historial.registrar_vida(SimpleNamespace(vida=1), vida_anterior=1)
        self.historial.cerrar_turno()

        self.historial.usar_pergamino(inventario, "itm_pergamino")

        # Apéndice B: la cantidad de pergaminos nunca se restaura; solo se
        # descuenta el usado. Aquí no había ningún cambio de pergaminos
        # dentro del turno revertido, así que debe quedar 1 (2 - 1 usado).
        self.assertEqual(inventario.contar("itm_pergamino"), 1)

    def test_pergamino_recogido_durante_el_intervalo_no_se_devuelve_al_revertir(self):
        # Apéndice B: si dentro del intervalo revertido el jugador recogió
        # un pergamino, la reversión NO debe deshacer esa recolección: quien
        # registra los deltas simplemente no debe registrar un `deshacer`
        # para operaciones de inventario sobre pergaminos.
        inventario = Inventario(capacidad_max=5)

        self.historial.iniciar_turno(reloj_actual=100)
        inventario.recoger(_objeto("p1", "itm_pergamino"))  # no se registra un delta a propósito
        self.historial.cerrar_turno()

        self.historial.usar_pergamino(inventario, "itm_pergamino")

        # Se descontó el que se usó; el que se recogió durante el turno
        # revertido permanece (no se deshizo su recolección).
        self.assertEqual(inventario.contar("itm_pergamino"), 0)


if __name__ == '__main__':
    unittest.main()
