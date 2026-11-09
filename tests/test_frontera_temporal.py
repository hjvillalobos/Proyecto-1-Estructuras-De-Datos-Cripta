"""FR-020/006/014/017: acuerdo A–D, frontera cerrada de ejecutar.

Preparación TDD: ejecutar_ciclo conserva su contrato de un solo evento.
Sin reloj manual, mocks de servicios ni cambios de producción. El contador
se prepara en t=0 para reproducir literalmente secuencias 10 y 11; los
huecos son válidos y no se cambia el orden de ningún evento existente.
"""

import unittest
from random import Random

from modelo.enemigos import decidir_accion
from tests.datos_terreno_cazador import motor_terreno


class PruebasFronteraTemporal(unittest.TestCase):
    def observar(self, motor):
        """Sonda que delega cada llamada real, sin fabricar sus resultados."""
        procesados = []
        ejecutar_real = motor.ejecutar_ciclo

        def registrar(*args, **kwargs):
            evento = ejecutar_real(*args, **kwargs)
            if evento is not None:
                procesados.append(evento)
            return evento

        motor.ejecutar_ciclo = registrar
        return procesados

    def azar_y_dano(self, motor, enemigo):
        esperado = Random()
        esperado.setstate(motor.azar.getstate())
        dano = max(1, enemigo.ataque + esperado.randint(0, 4)
                   - motor.jugador.defensa)
        return esperado, dano

    def test_jugador_10_enemigo_11_recibe_dano_antes_de_decidir(self):
        with motor_terreno(100) as motor:
            motor.cola.fijar_contador(10)
            destino = motor.enemigos_por_sala[101][0]
            vida = motor.jugador.vida
            azar, dano = self.azar_y_dano(motor, destino)
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(motor.reloj, 100)
            self.assertEqual(motor.jugador.vida, vida - dano)
            self.assertEqual([(e.tipo, e.secuencia) for e in eventos
                              if e.secuencia in (10, 11)],
                             [("turno_jugador", 10), ("turno_enemigo", 11)])
            self.assertEqual(motor.azar.getstate(), azar.getstate())
            self.assertEqual(destino.evento_pendiente.tiempo, 200)
            self.assertIsNone(motor.jugador.evento_pendiente)

    def test_enemigo_10_jugador_11_conserva_orden_inverso(self):
        with motor_terreno(100) as motor:
            enemigo = motor.enemigos_por_sala[100][0]
            motor.cola.fijar_contador(10)
            # Snapshot inicial coherente: reemplazo por el mismo turno t=100.
            motor._avanzar_actor(enemigo, 100)
            self.assertEqual(enemigo.evento_pendiente.secuencia, 10)
            vida = motor.jugador.vida
            azar, dano = self.azar_y_dano(motor, enemigo)
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual([(e.tipo, e.secuencia) for e in eventos],
                             [("turno_enemigo", 10), ("turno_jugador", 11)])
            self.assertEqual(motor.jugador.vida, vida - dano)
            self.assertEqual(motor.azar.getstate(), azar.getstate())
            self.assertEqual(motor.reloj, 100)

    def test_ataque_letal_empatado_impide_siguiente_accion(self):
        with motor_terreno(100) as motor:
            # Estado inicial sintético herido, dentro de 1..vida_max.
            motor.jugador.vida = 1
            motor.cola.fijar_contador(10)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertTrue(motor.terminado)
            self.assertEqual(motor.resultado, "derrota")
            self.assertEqual(motor.jugador.vida, 0)
            azar = motor.azar.getstate()
            self.assertFalse(motor.ejecutar("esperar").ok)
            self.assertEqual(motor.azar.getstate(), azar)
            self.assertEqual(motor.acciones_jugador, 1)
            self.assertEqual(motor.reloj, 100)

    def test_evento_t_mas_uno_no_se_procesa_anticipadamente(self):
        with motor_terreno(100) as motor:
            futuro = motor.programar_evento(101, "cierre_puerta",
                                            (motor.salas[100], "E"))
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(motor.reloj, 100)
            self.assertTrue(futuro.en_cola)
            self.assertFalse(motor.salas[100].salidas["E"].get("cerrada", False))
            self.assertTrue(all(e.tiempo <= 100 for e in eventos))

    def test_cancelado_en_t_no_actua_ni_arrastra_el_reloj_a_t_mas_uno(self):
        with motor_terreno(100, velocidad_enemigo=25) as motor:
            cancelado = motor.programar_evento(100, "cierre_puerta",
                                               (motor.salas[100], "E"))
            motor.cancelar_evento(cancelado)
            futuro = motor.programar_evento(101, "cierre_puerta",
                                            (motor.salas[100], "E"))
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertTrue(cancelado.cancelado)
            self.assertNotIn(cancelado, eventos)
            self.assertFalse(motor.salas[100].salidas["E"].get("cerrada", False))
            self.assertTrue(futuro.en_cola)
            self.assertEqual(motor.reloj, 100)

    def test_efecto_en_t_respeta_secuencia_y_reprograma_enemigo(self):
        with motor_terreno(100, velocidad_enemigo=200) as motor:
            enemigo = motor.enemigos_por_sala[100][0]
            # Efecto inicial de ralentización a 100, base 200, fin en t=100.
            motor.cambiar_velocidad(enemigo, 100)
            fin = motor.programar_evento(100, "restaurar_velocidad", (enemigo, 200))
            enemigo.evento_velocidad = fin
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual([e.tipo for e in eventos],
                             ["turno_enemigo", "restaurar_velocidad", "turno_jugador"])
            self.assertEqual(enemigo.velocidad, 200)
            self.assertEqual(enemigo.evento_pendiente.tiempo, 150)
            self.assertIsNone(enemigo.evento_velocidad)
            self.assertTrue(all(a.secuencia < b.secuencia
                                for a, b in zip(eventos, eventos[1:])))

    def test_cancelado_despues_del_turno_no_extrae_el_valido_de_t_mas_uno(self):
        with motor_terreno(100, velocidad_enemigo=200) as motor:
            origen = motor.enemigos_por_sala[100][0]
            destino = motor.enemigos_por_sala[101][0]
            motor.cambiar_velocidad(origen, 25)
            # Destino comienza dormido, ralentizado a 100, con fin en t=100.
            # Mover programa jugador y luego destino en t=100. El efecto,
            # ya agendado, reemplaza el turno de destino por uno en t=101.
            motor.cambiar_velocidad(destino, 100)
            fin = motor.programar_evento(100, "restaurar_velocidad", (destino, 200))
            destino.evento_velocidad = fin
            vida = motor.jugador.vida
            azar = motor.azar.getstate()
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(motor.reloj, 100)
            self.assertEqual([e.tipo for e in eventos],
                             ["restaurar_velocidad", "turno_jugador"])
            self.assertEqual(destino.evento_pendiente.tiempo, 101)
            self.assertGreater(destino.evento_pendiente.secuencia, fin.secuencia + 2)
            self.assertTrue(destino.evento_pendiente.en_cola)
            self.assertEqual(motor.jugador.vida, vida)
            self.assertEqual(motor.azar.getstate(), azar)

    def test_reprogramacion_jugador_define_la_frontera_vigente(self):
        with motor_terreno(100, velocidad=200) as motor:
            motor.cambiar_velocidad(motor.jugador, 100)
            fin = motor.programar_evento(50, "restaurar_velocidad",
                                        (motor.jugador, 200))
            motor.jugador.evento_velocidad = fin
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual(motor.reloj, 75)
            self.assertEqual([e.tipo for e in eventos],
                             ["restaurar_velocidad", "turno_jugador"])
            self.assertGreater(eventos[-1].secuencia, fin.secuencia)
            self.assertIsNone(motor.jugador.evento_pendiente)
            self.assertEqual(motor.enemigos_por_sala[100][0].evento_pendiente.tiempo, 100)

    def test_dos_decisiones_no_duplican_ni_difieren_ataques_empatados(self):
        with motor_terreno(100) as motor:
            destino = motor.enemigos_por_sala[101][0]
            vida = motor.jugador.vida
            azar = Random()
            azar.setstate(motor.azar.getstate())
            dano = sum(max(1, destino.ataque + azar.randint(0, 4)
                           - motor.jugador.defensa) for _ in range(2))
            eventos = self.observar(motor)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual(motor.reloj, 200)
            self.assertEqual(motor.jugador.vida, vida - dano)
            self.assertEqual(motor.azar.getstate(), azar.getstate())
            self.assertEqual([e.tiempo for e in eventos
                              if e.tipo == "turno_enemigo" and e.referencia is destino],
                             [100, 200])
            self.assertEqual(destino.evento_pendiente.tiempo, 300)

    def test_repeticion_conserva_azar_agenda_y_orden_del_lote(self):
        estados = []
        for _ in range(2):
            with motor_terreno(100) as motor:
                eventos = self.observar(motor)
                self.assertTrue(motor.ejecutar("mover", "E").ok)
                estados.append((motor.reloj, motor.jugador.vida,
                                motor.azar.getstate(), motor.cola.proxima_secuencia(),
                                tuple((e.tiempo, e.secuencia, e.tipo) for e in eventos),
                                tuple((e.tiempo, e.secuencia, e.tipo)
                                      for e in motor.cola.pendientes())))
        self.assertEqual(estados[0], estados[1])
        self.assertTrue(all(t > estados[0][0] for t, _, _ in estados[0][-1]))

    def test_ejecutar_ciclo_sigue_procesando_un_solo_evento(self):
        with motor_terreno(100) as motor:
            self.assertTrue(motor.mover("E")[0])
            primero = motor.ejecutar_ciclo(decidir_accion)
            segundo = motor.ejecutar_ciclo(decidir_accion)
            self.assertEqual(primero.tipo, "turno_enemigo")
            self.assertEqual(segundo.tipo, "turno_jugador")
            destino = motor.enemigos_por_sala[101][0]
            self.assertEqual(destino.evento_pendiente.tiempo, 100)
            self.assertTrue(destino.evento_pendiente.en_cola)


if __name__ == "__main__":
    unittest.main()
