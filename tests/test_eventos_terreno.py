"""T030: orden de eventos, activación y efectos en el motor ordinario offline."""

from dataclasses import replace
import unittest
from unittest.mock import patch

from modelo.juego import crear_juego
from modelo.tipos import ObjetoInstancia
from tests.datos_terreno_cazador import motor_terreno
from tests.test_turno_cazador import partida_cazador


class TestEventosTerreno(unittest.TestCase):
    def test_a8_cierre_efecto_y_cazador_empatados_respetan_la_secuencia(self):
        """FR-006/013/014/015: el cierre afecta la decisión solo si ocurre antes."""
        for cierre_primero in (True, False):
            with self.subTest(cierre_primero=cierre_primero), partida_cazador(350) as (motor, cazador, _):
                origen = motor.salas[100]
                salida = origen.salidas["E"]
                self.assertFalse(salida.get("cerrada", False))

                # Condición inicial: vence la aceleración del jugador en t=100.
                fin = motor.programar_evento(100, "restaurar_velocidad", (motor.jugador, 100))
                motor.jugador.evento_velocidad = fin
                if cierre_primero:
                    cierre = motor.programar_evento(100, "cierre_puerta", (origen, "E"))
                turno_inicial = cazador.evento_pendiente
                motor.cancelar_evento(turno_inicial)
                turno = motor.programar_evento(100, "turno_enemigo", cazador)
                cazador.evento_pendiente = turno
                if not cierre_primero:
                    cierre = motor.programar_evento(100, "cierre_puerta", (origen, "E"))

                for sala, tiempo in ((101, 71), (102, 99)):
                    self.assertTrue(motor.ejecutar("mover", "E").ok)
                    self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (sala, tiempo))

                procesados = []
                ciclo_real = motor.ejecutar_ciclo

                def observar(*args, **kwargs):
                    evento = ciclo_real(*args, **kwargs)
                    if evento is not None:
                        procesados.append(evento)
                    return evento

                azar = motor.azar.getstate()
                with patch.object(motor, "ejecutar_ciclo", side_effect=observar):
                    self.assertTrue(motor.ejecutar("esperar").ok)

                empatados = [e for e in procesados if e.tiempo == 100]
                esperados = [fin, cierre, turno] if cierre_primero else [fin, turno, cierre]
                self.assertEqual([e.secuencia for e in empatados], [e.secuencia for e in esperados])
                for real, esperado in zip(empatados, esperados):
                    self.assertIs(real, esperado)
                    self.assertFalse(real.en_cola)
                self.assertTrue(turno_inicial.cancelado)
                self.assertTrue(salida["cerrada"])
                self.assertEqual((motor.reloj, motor.jugador.velocidad), (194, 100))
                self.assertIsNone(motor.jugador.evento_velocidad)
                self.assertEqual(motor.azar.getstate(), azar)
                siguiente = cazador.evento_pendiente
                self.assertEqual((cazador.sala_actual, siguiente.tiempo),
                                 (100, 200) if cierre_primero else (101, 350))
                self.assertIs(siguiente.referencia, cazador)
                self.assertTrue(siguiente.en_cola)

    def test_a9_entrada_activa_en_orden_de_instancia_con_costo_inicial_fijo(self):
        """FR-015/016: precarga sin activación y entrada con costo 100 por actor."""
        with motor_terreno(costo=250, velocidad=500) as motor:
            self.assertTrue(motor.contenido_cargado[101])
            sala = motor.enemigos_por_sala[101]
            posterior = sala[0]
            anterior = replace(posterior, id_instancia="a-101")
            sala.append(anterior)
            self.assertGreater(posterior.id_instancia, anterior.id_instancia)
            for enemigo in sala:
                self.assertIsNone(enemigo.sala_actual)
                self.assertIsNone(enemigo.evento_pendiente)

            self.assertTrue(motor.ejecutar("mover", "E").ok)

            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (101, 50))
            for enemigo in (anterior, posterior):
                evento = enemigo.evento_pendiente
                self.assertEqual(enemigo.sala_actual, 101)
                self.assertEqual((evento.tipo, evento.tiempo), ("turno_enemigo", 100))
                self.assertIs(evento.referencia, enemigo)
                self.assertTrue(evento.en_cola)
            self.assertLess(anterior.evento_pendiente.secuencia, posterior.evento_pendiente.secuencia)

    def test_a9_entrada_conserva_el_turno_del_enemigo_que_llego_activo(self):
        """FR-015/016: una entrada no reactiva al enemigo que ya se movió."""
        with partida_cazador(350) as (motor, cazador, _):
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual((motor.jugador.posicion_actual, cazador.sala_actual, motor.reloj), (102, 100, 99))
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual((motor.jugador.posicion_actual, cazador.sala_actual, motor.reloj), (102, 101, 127))

            turno = cazador.evento_pendiente
            secuencia = turno.secuencia
            self.assertEqual(turno.tiempo, 350)
            self.assertTrue(motor.ejecutar("mover", "O").ok)

            self.assertEqual((motor.jugador.posicion_actual, cazador.sala_actual, motor.reloj), (101, 101, 155))
            self.assertIs(motor.enemigos_por_sala[101][0], cazador)
            self.assertIs(cazador.evento_pendiente, turno)
            self.assertEqual((turno.tiempo, turno.secuencia, cazador.tiempo_siguiente), (350, secuencia, 350))
            self.assertTrue(turno.en_cola)
            self.assertFalse(turno.cancelado)
            pendientes = [e for e in motor.cola.pendientes()
                          if e.tipo == "turno_enemigo" and e.referencia is cazador]
            self.assertEqual(len(pendientes), 1)
            self.assertIs(pendientes[0], turno)

    def test_a10_cierre_tras_cruce_impide_repetir_la_salida_y_conserva_llave(self):
        """FR-015: abrir y cruzar son acciones distintas; el cierre no desplaza al jugador."""
        def preparar(precarga, *args, **kwargs):
            almacen = precarga.cliente.almacen
            pagina = almacen.leer_pagina("prueba", "v1", 1)
            origen, _, alternativa, _ = pagina["salas"]
            origen["salidas"]["E"]["cierre_automatico"] = 40
            # Regreso por otra salida para volver a probar el mismo descriptor.
            origen["salidas"]["N"] = {"sala": 102, "costo": 100}
            alternativa["salidas"]["S"] = {"sala": 100, "costo": 100}
            almacen.guardar_pagina("prueba", "v1", pagina)
            return crear_juego(precarga, *args, **kwargs)

        with patch("tests.datos_terreno_cazador.crear_juego", new=preparar), \
                motor_terreno(costo=250, velocidad=500, puerta_inicial_cerrada=True) as motor:
            jugador = motor.jugador
            salida = motor.salas[100].salidas["E"]
            llave = ObjetoInstancia("llave-t030", "obj_0", "inventario")
            self.assertIsNotNone(jugador.inventario.recoger(llave))
            self.assertTrue(salida["cerrada"])
            self.assertTrue(motor.ejecutar("abrir", "E").ok)
            self.assertEqual((jugador.posicion_actual, motor.reloj, motor.acciones_jugador), (100, 10, 1))
            self.assertFalse(salida["cerrada"])
            cierre, = (e for e in motor.cola.pendientes() if e.tipo == "cierre_puerta")
            self.assertEqual(cierre.tiempo, 40)

            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual((jugador.posicion_actual, motor.reloj, motor.acciones_jugador), (101, 60, 2))
            self.assertFalse(cierre.en_cola)
            self.assertFalse(cierre.cancelado)
            self.assertTrue(salida["cerrada"])
            self.assertEqual(jugador.inventario.contar("obj_0"), 1)

            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertTrue(motor.ejecutar("mover", "S").ok)
            self.assertEqual(jugador.posicion_actual, 100)
            antes = motor.reloj, motor.acciones_jugador
            self.assertFalse(motor.ejecutar("mover", "E").ok)
            self.assertEqual((motor.reloj, motor.acciones_jugador), antes)
            self.assertEqual(jugador.posicion_actual, 100)
            self.assertEqual(jugador.inventario.contar("obj_0"), 1)

    def test_a11_curacion_y_regeneracion_no_superan_vida_maxima(self):
        """FR-017: los dos mecanismos reales limitan la vida antes de devolver el turno."""
        with motor_terreno() as motor:
            jugador = motor.jugador
            enemigo = motor.enemigos_por_sala[100][0]
            jugador.vida = jugador.vida_max - 1
            enemigo.vida = enemigo.vida_max - 1
            pocion = ObjetoInstancia("p-t030", "pocion", "inventario")
            self.assertIsNotNone(jugador.inventario.recoger(pocion))
            motor.efectos.aplicar_regeneracion(enemigo, 4)
            pulso, = (e for e in motor.cola.pendientes() if e.tipo == "pulso_regeneracion")
            self.assertEqual(pulso.tiempo, 200)
            observados = []
            regenerar = motor.efectos.ejecutar_pulso_regeneracion

            def observar(actor, cantidad, intervalo):
                antes = actor.vida
                regenerar(actor, cantidad, intervalo)
                observados.append((motor.reloj, actor, antes, actor.vida))

            with patch.object(motor.efectos, "ejecutar_pulso_regeneracion", side_effect=observar):
                self.assertTrue(motor.ejecutar("usar", pocion.id_instancia).ok)
                self.assertEqual(motor.reloj, 50)
                self.assertEqual(jugador.vida, jugador.vida_max)
                self.assertEqual(jugador.inventario.contar("pocion"), 0)
                self.assertEqual(observados, [])
                for _ in range(4):
                    self.assertTrue(motor.ejecutar("esperar").ok)

            maximo = enemigo.vida_max
            self.assertEqual(observados, [(200, enemigo, maximo - 1, maximo), (400, enemigo, maximo, maximo)])
            self.assertFalse(pulso.en_cola)
            siguiente, = (e for e in motor.cola.pendientes() if e.tipo == "pulso_regeneracion")
            self.assertEqual(siguiente.tiempo, 600)
            self.assertIs(siguiente.referencia[0], enemigo)
            self.assertEqual(enemigo.vida, enemigo.vida_max)
