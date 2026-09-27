# tests/test_inventario.py

import unittest
from modelo.tipos import ObjetoInstancia, FichaCatalogo
from modelo.inventario import Inventario


def _objeto(id_instancia, tipo_catalogo):
    return ObjetoInstancia(
        id_instancia=id_instancia,
        tipo_catalogo=tipo_catalogo,
        ubicacion="suelo",
        sala=1,
    )


class TestInventario(unittest.TestCase):

    def setUp(self):
        self.inventario = Inventario(capacidad_max=3)

    def test_recoger_hasta_llenar_y_rechazar_el_siguiente(self):
        self.assertIsNotNone(self.inventario.recoger(_objeto("o1", "itm_daga")))
        self.assertIsNotNone(self.inventario.recoger(_objeto("o2", "itm_pocion")))
        self.assertIsNotNone(self.inventario.recoger(_objeto("o3", "itm_llave")))
        self.assertTrue(self.inventario.esta_lleno())

        # Apéndice B: con el inventario lleno, recoger no se ejecuta.
        rechazado = self.inventario.recoger(_objeto("o4", "itm_antorcha"))
        self.assertIsNone(rechazado)
        self.assertEqual(self.inventario.tamaño, 3)

    def test_avanzar_y_retroceder(self):
        self.inventario.recoger(_objeto("o1", "itm_daga"))
        self.inventario.recoger(_objeto("o2", "itm_pocion"))
        self.inventario.recoger(_objeto("o3", "itm_llave"))

        self.assertEqual(self.inventario.objeto_actual().id_instancia, "o1")
        self.inventario.avanzar()
        self.assertEqual(self.inventario.objeto_actual().id_instancia, "o2")
        self.inventario.avanzar()
        self.assertEqual(self.inventario.objeto_actual().id_instancia, "o3")
        # No hay más allá del último: se queda ahí.
        self.inventario.avanzar()
        self.assertEqual(self.inventario.objeto_actual().id_instancia, "o3")

        self.inventario.retroceder()
        self.inventario.retroceder()
        self.assertEqual(self.inventario.objeto_actual().id_instancia, "o1")

    def test_soltar_actual_en_medio_no_depende_de_la_posicion(self):
        self.inventario.recoger(_objeto("o1", "itm_daga"))
        self.inventario.recoger(_objeto("o2", "itm_pocion"))
        self.inventario.recoger(_objeto("o3", "itm_llave"))

        self.inventario.avanzar()  # cursor -> o2
        soltado = self.inventario.soltar_actual()

        self.assertEqual(soltado.id_instancia, "o2")
        self.assertEqual(self.inventario.tamaño, 2)
        # El cursor se reubica en el vecino (o3, el siguiente).
        self.assertEqual(self.inventario.objeto_actual().id_instancia, "o3")

        vista = [o.id_instancia for o in self.inventario._recolectar()]
        self.assertEqual(vista, ["o1", "o3"])

    def test_equipar_actual_mueve_al_frente_y_marca_arma(self):
        self.inventario.recoger(_objeto("o1", "itm_daga"))
        self.inventario.recoger(_objeto("o2", "itm_espada"))

        self.inventario.avanzar()  # cursor -> o2
        self.inventario.equipar_actual("arma")

        vista = [o.id_instancia for o in self.inventario._recolectar()]
        self.assertEqual(vista, ["o2", "o1"])
        self.assertEqual(self.inventario.arma_equipada.objeto.id_instancia, "o2")
        self.assertEqual(self.inventario.arma_equipada_objeto.id_instancia, "o2")
        self.assertIsNone(self.inventario.armadura_equipada_objeto)

    def test_contar_y_quitar_primero_de_tipo(self):
        self.inventario.recoger(_objeto("o1", "itm_pergamino"))
        self.inventario.recoger(_objeto("o2", "itm_pocion"))
        self.inventario.recoger(_objeto("o3", "itm_pergamino"))

        self.assertEqual(self.inventario.contar("itm_pergamino"), 2)

        quitado = self.inventario.quitar_primero_de_tipo("itm_pergamino")
        self.assertEqual(quitado.id_instancia, "o1")
        self.assertEqual(self.inventario.contar("itm_pergamino"), 1)

    def test_vista_ordenada_no_altera_el_orden_real(self):
        fichas = {
            "itm_pesado": FichaCatalogo("itm_pesado", "arma", "Mandoble", {"peso": 9, "valor": 5}),
            "itm_ligero": FichaCatalogo("itm_ligero", "arma", "Daga", {"peso": 1, "valor": 20}),
        }

        self.inventario.recoger(_objeto("o1", "itm_pesado"))
        self.inventario.recoger(_objeto("o2", "itm_ligero"))

        vista_por_peso = self.inventario.vista_ordenada("peso", lambda t: fichas[t])
        self.assertEqual([o.id_instancia for o in vista_por_peso], ["o2", "o1"])

        vista_por_valor = self.inventario.vista_ordenada("valor", lambda t: fichas[t])
        self.assertEqual([o.id_instancia for o in vista_por_valor], ["o1", "o2"])

        # El orden real (de navegación) no cambió con las vistas.
        orden_real = [o.id_instancia for o in self.inventario._recolectar()]
        self.assertEqual(orden_real, ["o1", "o2"])


if __name__ == '__main__':
    unittest.main()
