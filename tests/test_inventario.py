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

    def test_vista_orden_none_devuelve_itemvista_en_orden_real(self):
        fichas = {
            "itm_a": FichaCatalogo("itm_a", "pocion", "Poción A", {"peso": 1, "valor": 5}),
            "itm_b": FichaCatalogo("itm_b", "pocion", "Poción B", {"peso": 2, "valor": 3}),
        }
        self.inventario.recoger(_objeto("o1", "itm_a"))
        self.inventario.recoger(_objeto("o2", "itm_b"))

        vista = self.inventario.vista(lambda t: fichas[t])
        self.assertEqual([i.instancia for i in vista], ["o1", "o2"])
        self.assertEqual(vista[0].nombre, "Poción A")
        self.assertEqual(vista[0].clase, "pocion")

    def test_vista_ordenada_por_valor_devuelve_itemvista_ordenado(self):
        fichas = {
            "itm_a": FichaCatalogo("itm_a", "pocion", "Poción A", {"peso": 1, "valor": 5}),
            "itm_b": FichaCatalogo("itm_b", "pocion", "Poción B", {"peso": 2, "valor": 3}),
        }
        self.inventario.recoger(_objeto("o1", "itm_a"))
        self.inventario.recoger(_objeto("o2", "itm_b"))

        vista = self.inventario.vista(lambda t: fichas[t], orden="valor")
        self.assertEqual([i.instancia for i in vista], ["o2", "o1"])

    def test_cursor_vista_marca_equipado(self):
        fichas = {"itm_espada": FichaCatalogo("itm_espada", "arma", "Espada", {"peso": 4, "valor": 30, "ataque_bonus": 5})}
        self.inventario.recoger(_objeto("o1", "itm_espada"))
        self.inventario.equipar_actual("arma")

        item = self.inventario.cursor_vista("actual", lambda t: fichas[t])
        self.assertEqual(item.instancia, "o1")
        self.assertTrue(item.equipado)

    def test_cursor_vista_devuelve_none_si_vacio(self):
        self.assertIsNone(self.inventario.cursor_vista("actual", lambda t: None))

    def test_guardado_y_restauracion_preservan_orden_y_equipado(self):
        fichas = {
            "itm_espada": FichaCatalogo("itm_espada", "arma", "Espada", {}),
            "itm_pocion": FichaCatalogo("itm_pocion", "pocion", "Poción", {}),
        }
        self.inventario.recoger(_objeto("o1", "itm_espada"))
        self.inventario.recoger(_objeto("o2", "itm_pocion"))
        self.inventario.equipar_actual("arma")  # o1 pasa al frente y queda equipada

        guardado = self.inventario.a_lista_guardado()
        self.assertEqual([g.instancia for g in guardado], ["o1", "o2"])
        self.assertTrue(guardado[0].equipado)
        self.assertFalse(guardado[1].equipado)

        restaurado = Inventario(capacidad_max=3)
        restaurado.restaurar_desde_guardado(guardado, lambda t: fichas[t].clase)

        self.assertEqual([o.id_instancia for o in restaurado._recolectar()], ["o1", "o2"])
        self.assertEqual(restaurado.arma_equipada_objeto.id_instancia, "o1")


if __name__ == '__main__':
    unittest.main()
