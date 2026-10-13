import unittest
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch
import tkinter as tk

from controlador.controlador import ControladorJuego
from modelo.snapshots import EnemigoVista, ItemVista
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos


class TestPresentacionModelo(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor

    def test_notificaciones_no_cambian_simulacion_ni_azar(self):
        self.datos.fichas[-1].atributos["velocidad"] = 150
        self.datos._enemigo(velocidad=150)
        estado = deepcopy(self.motor.exportar_estado())
        self.motor.ejecutar("esperar")
        esperado = self.motor.exportar_estado()
        self.motor.restaurar_estado(estado)
        mensajes = []
        self.motor.establecer_notificador(mensajes.append)
        self.motor.ejecutar("esperar")
        self.assertEqual(self.motor.exportar_estado(), esperado)
        self.assertTrue(any("t=66" in m and "ataca a Jugador" in m for m in mensajes))

    def test_agenda_respeta_tiempo_secuencia_y_visibilidad(self):
        primero = self.datos._enemigo()
        segundo = deepcopy(primero)
        segundo.id_instancia = "otro"
        segundo.evento_pendiente = None
        segundo.sala_actual = 2
        self.motor.enemigos_por_sala[2].append(segundo)
        self.motor._avanzar_actor(segundo, 25)
        antes = self.motor.exportar_estado()
        vista = self.motor.estado_vista()
        self.assertEqual(len(vista.agenda), 1)
        self.assertEqual(vista.agenda[0].tiempo, 100)
        self.assertIn(primero.id_instancia, vista.agenda[0].nombre)
        self.assertEqual(self.motor.exportar_estado(), antes)
        self.assertEqual(vista.enemigos[0].tipo, "enemigo")
        self.assertEqual(vista.enemigos[0].velocidad, 100)

    def test_costos_se_ajustan_a_la_velocidad(self):
        self.motor.cambiar_velocidad(self.motor.jugador, 200)
        costos = self.motor.estado_vista().costos
        self.assertIn(("mover", 50), costos)
        self.assertIn(("equipar", 25), costos)
        self.assertIn(("recoger", 12), costos)

    def test_objetos_muestran_sus_efectos_antes_de_usarlos(self):
        self.datos._inventario("coraza")
        self.datos._inventario("velocidad")
        self.datos._suelo("pocion")
        items = self.motor.inventario_vista()
        self.assertIn("Defensa +2", items[0].detalle)
        self.assertIn("Velocidad x2", items[1].detalle)
        self.assertIn("300", items[1].detalle)
        self.assertIn("Cura +8", self.motor.estado_vista().objetos_suelo[0].detalle)
        self.assertEqual(items[0].tipo, "coraza")
        self.assertEqual(self.motor.estado_vista().objetos_suelo[0].tipo, "pocion")

    def test_trampa_aparece_y_su_dano_se_notifica(self):
        from modelo.tipos import Trampa
        self.motor.sala_salida = None
        self.motor.salas[2].trampas.append(Trampa("t", "trampa"))
        self.motor.salas[1].salidas["E"]["cerrada"] = False
        mensajes = []
        self.motor.establecer_notificador(mensajes.append)
        self.motor.ejecutar("mover", "E")
        trampa = self.motor.estado_vista().trampas[0]
        self.assertFalse(trampa.armada)
        self.assertEqual(trampa.dano, 4)
        self.assertTrue(any("Trampa:" in m and "4 de dano" in m for m in mensajes))

    def test_notificaciones_utilizan_buffer_existente_de_20_mensajes(self):
        self.datos._enemigo()
        self.motor.jugador.vida = 10000
        self.motor.jugador.vida_max = 10000
        c = ControladorJuego(self.motor, Mock())
        c.bitacora_replay = Mock()
        for _ in range(20):
            c._accion_modelo("esperar")
        self.assertEqual(len(c.mensajes.ultimos()), 20)
        self.assertTrue(any("ataca" in m for m in c.mensajes.ultimos()))


class TestEscena(unittest.TestCase):
    def test_refresco_de_inventario_no_borra_la_animacion_de_dano(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        v = VistaGrafica.__new__(VistaGrafica)
        v._cerrada = False
        v._estado = None
        v._dibujar_sala = Mock()
        v._actualizar_stats = Mock()
        v._actualizar_log = Mock()
        v._mostrar_detalle = Mock()
        v._animar_vida = Mock()
        v.root = Mock()
        v.mostrar_estado(datos.motor.estado_vista(), [])
        datos.motor.jugador.vida -= 4
        v.mostrar_estado(datos.motor.estado_vista(), [])
        v.mostrar_estado(datos.motor.estado_vista(), [])
        self.assertEqual(v._dibujar_sala.call_count, 2)
        v._animar_vida.assert_called_once_with(-4)

    def test_mismo_tipo_utiliza_la_misma_imagen_y_distinta_accion(self):
        v = VistaGrafica.__new__(VistaGrafica)
        v.canvas, v.recursos, v._ligar = Mock(), Mock(), Mock()
        v.recursos.imagen.return_value = object()
        estado = SimpleNamespace(sala_id=1, sala_nombre="Sala", salidas=[], objetos_suelo=[], vida=30, vida_max=30,
            enemigos=[EnemigoVista("r1", "Rata #1", 12, 12, tipo="tipo-r") ,
                      EnemigoVista("r2", "Rata #2", 12, 12, tipo="tipo-r")])
        v._dibujar_sala(estado)
        llamadas = [c.args for c in v.recursos.imagen.call_args_list if c.args[0] == "tipo-r"]
        self.assertEqual(len(llamadas), 2)
        self.assertEqual(llamadas[0], llamadas[1])
        self.assertIn(("enemigo_0", "atacar r1"), [c.args for c in v._ligar.call_args_list])
        self.assertIn(("enemigo_1", "atacar r2"), [c.args for c in v._ligar.call_args_list])

    def test_doble_clic_accidental_no_encola_dos_ataques(self):
        v = VistaGrafica.__new__(VistaGrafica)
        v._cola, v._cerrada, v._en_replay = [], False, False
        with patch("vista.grafica.time.monotonic", side_effect=[1, 1.1, 1.5]):
            v._clic_accion("atacar r1")
            v._clic_accion("atacar r1")
            v._clic_accion("atacar r1")
        self.assertEqual(v._cola, ["atacar r1", "atacar r1"])


class TestGraficosTk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.vista = VistaGrafica()
            cls.vista.root.withdraw()
        except tk.TclError as error:
            raise unittest.SkipTest(str(error))

    @classmethod
    def tearDownClass(cls):
        cls.vista.cerrar()

    def setUp(self):
        self.vista._cola.clear()
        self.vista.mostrar_inventario([])

    def test_png_del_jugador_y_rata_cargan_con_tamano_acotado(self):
        recursos = RecursosGraficos(self.vista.root)
        for nombre in ("jugador", "ent_rata_gigante", "ent_guardian_oseo",
                       "itm_pocion_menor", "itm_daga_oxidada"):
            imagen = recursos.imagen(nombre, 200, 150)
            self.assertIsNotNone(imagen)
            self.assertLessEqual(imagen.width(), 200)
            self.assertLessEqual(imagen.height(), 150)
            self.assertIs(recursos.imagen(nombre, 200, 150), imagen)
        self.assertIsNone(recursos.imagen("entidad-no-conocida", 200, 150))

    def test_miniatura_del_inventario_se_actualiza_y_se_limpia(self):
        v = self.vista
        for tipo in ("itm_pocion_menor", "itm_daga_oxidada"):
            v.mostrar_inventario([ItemVista("obj", "Objeto", "pocion", 1, 2, tipo=tipo)])
            self.assertIsNotNone(v._imagen_detalle)
            self.assertEqual(str(v.icono_detalle.cget("image")), str(v._imagen_detalle))
        v.mostrar_inventario([ItemVista("otro", "Otro", "llave", 1, 2)])
        self.assertIsNone(v._imagen_detalle)
        self.assertEqual(v.icono_detalle.cget("image"), "")
        v.mostrar_inventario([])
        self.assertIsNone(v._imagen_detalle)

    def test_imagen_del_suelo_conserva_la_accion_de_recoger(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        estado = datos.motor.estado_vista()
        estado.objetos_suelo = [ItemVista("p1", "Pocion", "pocion", 1, 2, tipo="itm_pocion_menor"),
                                ItemVista("d1", "Daga", "arma", 1, 2, tipo="itm_daga_oxidada")]
        v = self.vista
        with patch.object(v, "_ligar") as ligar:
            v._dibujar_sala(estado)
        ligar.assert_any_call("objeto_0", "recoger p1")
        ligar.assert_any_call("objeto_1", "recoger d1")
        for etiqueta in ("objeto_0", "objeto_1"):
            self.assertIn("image", [v.canvas.type(i) for i in v.canvas.find_withtag(etiqueta)])

    def test_fallback_sin_pillow_sigue_mostrando_los_png(self):
        with patch("vista.recursos_graficos.Image", None):
            recursos = RecursosGraficos(self.vista.root)
            imagen = recursos.imagen("jugador", 200, 150)
            self.assertIsNotNone(imagen)
            self.assertLessEqual(imagen.height(), 150)

    def test_acciones_incompatibles_se_deshabilitan(self):
        v = self.vista
        for clase, permitidas in (("llave", ["soltar"]), ("arma", ["equipar", "soltar"]),
                                  ("pocion", ["usar", "soltar"])):
            with self.subTest(clase=clase):
                v.mostrar_inventario([ItemVista("obj", "Objeto", clase, 1, 2, detalle="Efecto del objeto")])
                for verbo, boton in v._botones_inventario:
                    self.assertEqual(str(boton.cget("state")), "normal" if verbo in permitidas else "disabled")
                self.assertIn("Efecto del objeto", v.var_detalle.get())
        self.assertEqual(v._cola, [])

    def test_replay_actualiza_inventario_sin_solicitar_comandos(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        v = self.vista
        with patch.object(v, "_pausa_replay", return_value=0):
            self.assertTrue(v.mostrar_replay_paso(datos.motor.estado_vista(), [], 1, 1,
                inventario=[ItemVista("obj", "Coraza", "armadura", 4, 20, detalle="Defensa +2")]))
        self.assertEqual(v.lista.size(), 1)
        self.assertIn("Defensa +2", v.var_detalle.get())
        self.assertEqual(v._cola, [])


if __name__ == "__main__":
    unittest.main()
