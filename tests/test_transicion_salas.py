import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from tests import test_regresiones_juego as base
from vista.animacion import AnimacionEscena
from vista.grafica import VistaGrafica


def avanzar(vista, pasos):
    for _ in range(pasos):
        animacion = vista.escena.animacion
        if animacion.pendiente is not None:
            vista.root.after_cancel(animacion.pendiente)
            animacion.pendiente = None
        animacion._avanzar()


class TestTransicionSalas(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.vista.root.withdraw()
        self.addCleanup(self.vista.cerrar)
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()

    def mover(self, direccion):
        motor, vista = self.datos.motor, self.vista
        motor.salas[1].salidas.clear()
        motor.salas[1].salidas[direccion] = {"sala": 2}
        vista.mostrar_estado(motor.estado_vista(), [])
        self.assertTrue(motor.ejecutar("mover", direccion).ok)
        vista.preparar_animacion("mover")
        vista.mostrar_estado(motor.estado_vista(), [])

    def test_corre_hasta_puerta_y_entra_sin_cambiar_simulacion(self):
        self.mover("N")
        vista, motor = self.vista, self.datos.motor
        estado = motor.exportar_estado()
        self.assertTrue(vista.transicion_salas.activa)
        self.assertEqual(vista.escena.anterior.sala_id, 1)
        sprite = next(i for i in vista.canvas.find_withtag("jugador") if vista.canvas.type(i) == "image")
        origen = vista.canvas.coords(sprite)
        avanzar(vista, 9)
        self.assertGreater(vista.canvas.coords(sprite)[0] - origen[0], 100)
        avanzar(vista, 1)
        self.assertFalse(vista.transicion_salas.activa)
        self.assertEqual(vista.escena.anterior.sala_id, 2)
        self.assertEqual(vista.escena._accion_en_curso, "correr")
        avanzar(vista, 16)
        self.assertEqual(vista.escena.animacion.paso, 16)
        actor = vista.escena.animacion.actores[0]
        self.assertAlmostEqual(vista.canvas.coords(actor[0])[0], actor[1][0])
        self.assertEqual(motor.exportar_estado(), estado)
        self.assertEqual(vista._cola, [])

    def test_direcciones_y_movimiento_rechazado(self):
        for direccion in ("N", "S", "E", "O"):
            with self.subTest(direccion=direccion):
                self.datos.setUp()
                self.vista.reiniciar_presentacion()
                self.mover(direccion)
                self.assertTrue(self.vista.transicion_salas.activa)
                avanzar(self.vista, 10)
                self.assertEqual(self.vista.escena.anterior.sala_id, 2)
        self.assertFalse(self.datos.motor.ejecutar("mover", "invalida").ok)
        self.assertFalse(self.vista.transicion_salas.activa)

    def test_puerta_solo_durante_paso_y_se_cierra_al_entrar(self):
        vista, motor = self.vista, self.datos.motor
        vista.mostrar_estado(motor.estado_vista(), [])
        self.assertFalse(vista.canvas.find_withtag("puerta_visual"))
        self.mover("N")
        puerta = vista.escena.animacion.decoraciones[0]
        self.assertEqual(vista.canvas.itemcget(puerta.marco, "state"), "hidden")
        avanzar(vista, 3)
        cerrada = vista.canvas.coords(puerta.izquierda)
        avanzar(vista, 4)
        abierta = vista.canvas.coords(puerta.izquierda)
        self.assertLess(abierta[2] - abierta[0], cerrada[2] - cerrada[0])
        avanzar(vista, 3)
        puerta = vista.escena.animacion.decoraciones[0]
        abierta = vista.canvas.coords(puerta.izquierda)
        estado = motor.exportar_estado()
        avanzar(vista, 10)
        cerrada = vista.canvas.coords(puerta.izquierda)
        self.assertGreater(cerrada[2] - cerrada[0], abierta[2] - abierta[0])
        avanzar(vista, 2)
        self.assertFalse(vista.canvas.find_withtag("puerta_visual"))
        self.assertEqual(motor.exportar_estado(), estado)

    def test_entrada_inicia_en_puerta_sin_destello_y_cancelar_la_limpia(self):
        self.mover("E")
        avanzar(self.vista, 10)
        a = self.vista.escena.animacion
        actor, origen, _, entrada, _, desplazamiento, *_ = next(
            item for item in a.actores if item[3])
        self.assertTrue(entrada)
        self.assertEqual(self.vista.canvas.coords(actor),
                         [origen[i] + desplazamiento[i] for i in range(2)])
        self.assertTrue(self.vista.canvas.find_withtag("puerta_visual"))
        a.detener()
        self.assertFalse(self.vista.canvas.find_withtag("puerta_visual"))

    def test_desactivar_o_cargar_interrumpe_sin_callback_obsoleto(self):
        self.mover("N")
        vieja = self.vista.escena.animacion
        self.vista.var_movimiento.set(False)
        self.vista._alternar_movimiento()
        self.assertIsNone(vieja.pendiente)
        self.assertIsNone(vieja._al_llegar)
        self.assertFalse(self.vista.transicion_salas.activa)
        self.assertEqual(self.vista.escena.anterior.sala_id, 2)
        self.vista.var_movimiento.set(True)
        self.vista._alternar_movimiento()
        self.datos.setUp()
        self.vista.reiniciar_presentacion()
        self.mover("E")
        vieja = self.vista.escena.animacion
        self.vista.preparar_animacion("cargar")
        self.vista.mostrar_estado(self.datos.motor.estado_vista(), [])
        self.assertFalse(self.vista.transicion_salas.activa)
        self.assertIsNone(vieja._al_llegar)
        self.assertIsNone(self.vista.escena._accion_en_curso)

    def test_trayecto_llama_final_una_vez_y_cancelacion_lo_descarta(self):
        root, canvas, final = Mock(), Mock(), Mock()
        canvas.coords.return_value = [10, 20]
        a = AnimacionEscena(root, canvas)
        a.agregar(1)
        a.recorrer(1, (210, 120), pasos=2, al_llegar=final)
        a._avanzar()
        final.assert_not_called()
        a._avanzar()
        final.assert_called_once()
        canvas.coords.assert_called_with(1, 210, 120)
        a.detener()
        self.assertIsNone(a._al_llegar)

    def test_redimensionar_conserva_posicion_pose_y_puerta(self):
        self.mover("N")
        avanzar(self.vista, 5)
        v = self.vista
        def dibujo():
            sprite = next(i for i in v.canvas.find_withtag("jugador") if v.canvas.type(i) == "image")
            puerta = v.escena.animacion.decoraciones[0]
            return (v.canvas.coords(sprite), v.canvas.itemcget(sprite, "image"),
                    v.canvas.coords(puerta.izquierda))
        antes = dibujo()
        v._redimensionar()
        self.assertEqual(dibujo(), antes)
        avanzar(v, 5)
        self.assertEqual(v.escena.anterior.sala_id, 2)
        avanzar(v, 7)
        antes = dibujo()
        v._redimensionar()
        self.assertEqual(dibujo(), antes)

    def test_paginacion_no_cancela_salida_ni_deja_sala_antigua(self):
        for i in range(9):
            self.datos._suelo("pocion", f"p-{i}")
        self.mover("N")
        avanzar(self.vista, 5)
        self.vista._cambiar_pagina("objetos", 1)
        self.assertTrue(self.vista.transicion_salas.activa)
        self.assertEqual(self.vista._pagina_objetos, 0)
        avanzar(self.vista, 5)
        self.assertEqual(self.vista.escena.anterior.sala_id,
                         self.datos.motor.jugador.posicion_actual)

    def test_primera_sala_precarga_ambas_orientaciones(self):
        v = self.vista
        v.mostrar_estado(self.datos.motor.estado_vista(), [])
        alto = int(min(280, max(350, v.canvas.winfo_height()) - 175) * .70)
        self.assertTrue(v.recursos.fotogramas_jugador(290, alto))
        self.assertTrue(v.recursos.fotogramas_jugador(290, alto, invertir=True))
        from vista import recursos_graficos
        if recursos_graficos.Image is None:
            self.skipTest("Pillow no disponible")
        with patch.object(recursos_graficos.Image, "open", wraps=recursos_graficos.Image.open) as abrir:
            self.mover("N")
            avanzar(v, 26)
        self.assertFalse(any("jugador_acciones" in str(c.args[0]) for c in abrir.call_args_list))

    def test_movimientos_rapidos_no_restauran_destino_obsoleto(self):
        self.mover("N")
        vieja = self.vista.escena.animacion
        self.assertTrue(self.datos.motor.ejecutar("mover", "O").ok)
        self.vista.preparar_animacion("mover")
        self.vista.mostrar_estado(self.datos.motor.estado_vista(), [])
        self.assertIsNone(vieja._al_llegar)
        avanzar(self.vista, 26)
        self.assertEqual(self.vista.escena.anterior.sala_id, 1)
