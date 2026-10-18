import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controlador.controlador import ControladorJuego
from modelo.snapshots import ItemVista, ResultadoAccion
from vista.grafica import VistaGrafica


class TestEntradaGrafica(unittest.TestCase):
    def setUp(self):
        self.vista = VistaGrafica.__new__(VistaGrafica)
        self.vista.root = Mock()
        self.vista._cola = []
        self.vista._cerrada = False
        self.vista._en_replay = False
        self.vista._refrescar_inv = False
        self.vista._items = []
        self.vista.var_orden = Mock()
        self.vista.var_orden.get.return_value = "orden real"

    def test_clic_recibido_en_update_se_entrega_al_controlador(self):
        self.vista.root.update.side_effect = lambda: self.vista._enviar("recoger obj-1-0")
        comando = self.vista.pedir_comando()
        modelo = Mock()
        modelo.ejecutar.return_value = ResultadoAccion(ok=True)
        controlador = ControladorJuego(modelo, self.vista)
        controlador.bitacora_replay = Mock()
        controlador.procesar_comando(comando)
        modelo.ejecutar.assert_called_once_with("recoger", "obj-1-0")
        controlador.bitacora_replay.registrar_accion.assert_called_once_with("recoger", "obj-1-0")

    def test_comandos_pendientes_conservan_el_orden_entre_refrescos(self):
        self.vista._enviar("recoger obj-1-0")
        self.vista._enviar("equipar obj-1-0")
        self.assertEqual(self.vista.pedir_comando(), "recoger obj-1-0")
        self.assertEqual(self.vista.pedir_comando(), "inv")
        self.assertEqual(self.vista.pedir_comando(), "equipar obj-1-0")

    def test_cierre_durante_update_interrumpe_espera(self):
        self.vista.root.update.side_effect = lambda: setattr(self.vista, "_cerrada", True)
        self.assertIsNone(self.vista.pedir_comando())

    def test_replay_no_acumula_comandos_del_jugador(self):
        self.vista._en_replay = True
        for comando in ("esperar", "recoger obj-1-0", "mover N"):
            self.vista._enviar(comando)
        self.assertEqual(self.vista._cola, [])

    def test_ventana_cerrada_no_acepta_comandos(self):
        self.vista._cerrada = True
        self.vista._enviar("esperar")
        self.assertEqual(self.vista._cola, [])

    def test_accion_de_inventario_usa_id_seleccionado(self):
        self.vista.lista = Mock()
        self.vista.lista.curselection.return_value = (1,)
        self.vista._items = [ItemVista("a", "Daga", "arma", 1, 2),
                             ItemVista("b", "Pocion", "pocion", 1, 2)]
        self.vista._accion_inventario("usar")
        self.assertEqual(self.vista._cola, ["usar b"])

    def test_doble_clic_pergamino_envia_su_uso(self):
        self.vista.lista = Mock()
        self.vista.lista.curselection.return_value = (0,)
        self.vista._items = [ItemVista("p1", "Pergamino", "pergamino_retroceso", 1, 2)]
        self.vista._doble_clic_inventario()
        self.assertEqual(self.vista._cola, ["usar p1"])

    def test_cada_objeto_del_canvas_envia_su_propia_instancia(self):
        self.vista.canvas = Mock()
        estado = SimpleNamespace(sala_id=1, sala_nombre="Entrada", salidas=[], enemigos=[],
                                 objetos_suelo=[ItemVista("o1", "Daga", "arma", 1, 2),
                                                ItemVista("o2", "Pocion", "pocion", 1, 2)],
                                 vida=30, vida_max=30)
        self.vista._dibujar_sala(estado)
        for llamada in self.vista.canvas.tag_bind.call_args_list:
            etiqueta, evento, callback = llamada.args
            if etiqueta.startswith("objeto_") and evento == "<Button-1>":
                callback(None)
        self.assertEqual(self.vista._cola, ["recoger o1", "recoger o2"])

    def test_refresco_conserva_seleccion_por_instancia_aunque_cambie_orden(self):
        self.vista.lista = Mock()
        self.vista.lista.curselection.return_value = (0,)
        a = ItemVista("a", "Daga", "arma", 1, 2)
        b = ItemVista("b", "Pocion", "pocion", 1, 2)
        self.vista._items = [a, b]
        self.vista.mostrar_inventario([b, a], orden="nombre")
        self.vista.lista.selection_set.assert_called_once_with(1)
