"""Parte II §3.4: hechos del movimiento ordinario y consumo de viaje."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from modelo.errores_historia import CambioHistoriaIncoherente
from modelo.tipos import Trampa
from modelo.viaje import ResultadoPaso
from tests.datos_terreno_cazador import motor_terreno
from tests.test_turno_cazador import partida_cazador
from tests import test_viaje_motor


class PruebasHechosPasoMotor(unittest.TestCase):
    def test_controlador_consume_entrada_y_ataque_en_la_frontera(self):
        with motor_terreno() as motor, TemporaryDirectory() as carpeta:
            _, _, viaje = test_viaje_motor.TestViajeMotor().preparar(motor)
            enemigo = motor.enemigos_por_sala[101][0]
            self.assertIsNone(enemigo.sala_actual)
            control = ControladorJuego(motor, Mock(), str(Path(carpeta) / "viaje.log"),
                                       control_viaje=viaje)
            control.bitacora_replay.iniciar(motor.meta)
            control.procesar_comando("ir a 102")
            control._avanzar_viaje()

            self.assertEqual((motor.reloj, motor.acciones_jugador), (100, 1))
            self.assertEqual(control.ultimo_resultado_accion.hechos_paso,
                             ResultadoPaso(101, True, True, True, True, False))
            self.assertEqual(viaje.causas, ("dano", "enemigos"))
            control._avanzar_viaje()
            self.assertEqual(motor.acciones_jugador, 1)

    def test_rechazo_sin_tiempo_y_movimiento_sin_enemigos(self):
        with partida_cazador(350) as (motor, _, _):
            antes = motor.exportar_estado()
            rechazo = motor.ejecutar("mover", "O")
            self.assertFalse(rechazo.ok)
            self.assertEqual(rechazo.hechos_paso, ResultadoPaso(100, False, False, False, False, False))
            self.assertEqual(motor.exportar_estado(), antes)
            paso = motor.ejecutar("mover", "E")
            self.assertEqual(paso.hechos_paso, ResultadoPaso(101, True, False, True, False, False))
            self.assertEqual(motor.reloj, 71)
            self.assertIsNone(motor.ejecutar("esperar").hechos_paso)

    def test_veneno_y_captura_se_descartan_si_falla_el_turno(self):
        with partida_cazador(350) as (motor, _, _):
            motor.efectos.aplicar_veneno(motor.jugador, 2, intervalo=30)
            antes = motor.exportar_estado()
            with patch.object(motor.historial, "cerrar_turno", side_effect=CambioHistoriaIncoherente("fallo")):
                with self.assertRaises(CambioHistoriaIncoherente):
                    motor.ejecutar("mover", "E")
            self.assertEqual(motor.exportar_estado(), antes)
            rechazo = motor.ejecutar("mover", "O")
            self.assertFalse(rechazo.hechos_paso.recibio_dano)
            paso = motor.ejecutar("mover", "E")
            self.assertEqual(paso.hechos_paso, ResultadoPaso(101, True, True, True, False, False))

    def test_dano_no_se_deduce_de_la_vida_final(self):
        with partida_cazador(350) as (motor, _, _):
            vida = motor.jugador.vida
            motor.efectos.aplicar_veneno(motor.jugador, 2, intervalo=50)
            pulso = motor.efectos.ejecutar_pulso_veneno

            def pulso_y_curacion(actor):
                pulso(actor)
                self.assertLess(actor.vida, vida)
                motor.historial.registrar_vida(actor, actor.vida)
                actor.vida = vida

            # Inyecta la recuperación para aislar la captura del daño, sin añadir una acción.
            with patch.object(motor.efectos, "ejecutar_pulso_veneno", side_effect=pulso_y_curacion):
                paso = motor.ejecutar("mover", "E")
            self.assertEqual(motor.jugador.vida, vida)
            self.assertTrue(paso.hechos_paso.recibio_dano)

    def test_trampa_registra_dano_antes_del_siguiente_turno(self):
        with motor_terreno() as motor:
            motor.gestor_precarga.catalogo.almacen.guardar_ficha("cat1", {
                "id": "trampa-paso", "clase": "trampa", "nombre": "Trampa", "daño": 3,
            })
            motor.salas[101].trampas.append(Trampa("t-paso", "trampa-paso"))
            motor.jugador.vida = 1
            paso = motor.ejecutar("mover", "E")
            self.assertEqual(paso.trampas_activadas, ["t-paso"])
            self.assertEqual(paso.hechos_paso, ResultadoPaso(101, True, True, True, True, True))
            self.assertEqual((motor.reloj, motor.jugador.vida, motor.resultado), (0, 0, "derrota"))
