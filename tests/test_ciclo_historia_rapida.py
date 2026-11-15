"""RC-01: igualdad exacta por evento con d43ded2, no solo resumen final."""
from copy import copy
from unittest import TestCase
from unittest.mock import patch
from modelo.partida import MotorPartida
from utilidades.referencia_historia_ciclo import MotorHistoriaAnterior
from tests import test_partida_generada as generada
from tests import test_controlador_ac_real as integrada


class MotorContrastado(MotorPartida):
    def proyeccion_h3(self):
        esperado = MotorHistoriaAnterior.proyeccion_h3(copy(self))
        actual = super().proyeccion_h3()
        if actual != esperado:
            raise AssertionError('Proyección distinta del productor anterior.')
        return actual

    def _cambios_h3(self, antes):
        referencia = copy(self)
        referencia._deltas_conocimiento = list(self._deltas_conocimiento)
        esperado = MotorHistoriaAnterior._cambios_h3(referencia, antes)
        actual = super()._cambios_h3(antes)
        if actual != esperado:
            raise AssertionError('Deltas distintos del productor anterior.')
        return actual


class HistoriaRapidaTest(TestCase):
    def test_orden_reutilizado_no_conserva_valores_obsoletos(self):
        with integrada.ControladorACRealTest.partida(self) as (motor, juego, __, ___, ____, _____):
            self.assertTrue(juego.ejecutar('mover', 'E').ok)
            def comprobar():
                self.assertEqual(motor.proyeccion_h3(), MotorHistoriaAnterior.proyeccion_h3(copy(motor)))
            comprobar()
            with patch('modelo.partida.ordenar', side_effect=AssertionError('Ordenamiento redundante')):
                motor.proyeccion_h3()
            enemigo = motor.enemigos_por_sala[101][0]
            for vida in (1, 0, enemigo.vida_max):
                enemigo.vida = vida
                comprobar()
            enemigo.id_instancia = 'nuevo-id'
            comprobar()
            otro = copy(enemigo)
            otro.id_instancia = 'a-primero'
            motor.enemigos_por_sala[101].append(otro)
            comprobar()
            motor.enemigos_por_sala[101].extraer(enemigo)
            comprobar()
            motor.enemigos_por_sala[101].extraer(otro)
            motor.enemigos_por_sala[101].append(enemigo)  # Igual tamaño, otra identidad.
            comprobar()
            motor.jugador.posicion_actual = 100
            comprobar()
            motor.jugador.posicion_actual = 101
            comprobar()

    def test_partidas_completas_contrastan_cada_evento(self):
        with patch('modelo.partida.MotorPartida', MotorContrastado):
            prueba = generada.PartidaGeneradaTest('test_ganar_guardar_retroceder_cargar_y_replay_en_criptas_nuevas')
            try:
                prueba.test_ganar_guardar_retroceder_cargar_y_replay_en_criptas_nuevas()
            finally:
                prueba.doCleanups()

    def test_carga_reversion_y_fallos_contrastan_cada_evento(self):
        for nombre in ('test_dx02_comandos_guardar_cargar_y_continuar_con_historia_real',
                       'test_dx02_cargas_invalidas_no_mutan_ni_se_graban',
                       'test_dx02_pergamino_recorta_historia_y_log_permite_nueva_rama',
                       'test_mc01_cargar_descarta_descubrimientos_posteriores_y_permite_continuar'):
            with self.subTest(nombre=nombre), patch('modelo.partida.MotorPartida', MotorContrastado):
                prueba = integrada.ControladorACRealTest(nombre)
                try:
                    getattr(prueba, nombre)()
                finally:
                    prueba.doCleanups()
