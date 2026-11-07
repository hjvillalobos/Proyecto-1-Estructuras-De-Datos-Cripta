"""T012: T7, FR-005/006/017; cola, snapshots y ejecución semántica separadas."""

import unittest
from random import Random

from modelo.enemigos import decidir_accion
from modelo.eventos import ColaEventos
from tests.datos_terreno_cazador import motor_terreno


class PruebasVelocidadTerreno(unittest.TestCase):
    def comprobar_reprogramacion(self, motor, actor, anterior, esperado):
        nuevo = actor.evento_pendiente
        self.assertTrue(anterior.cancelado)
        self.assertIsNot(nuevo, anterior)
        self.assertEqual(actor.tiempo_siguiente, esperado)
        self.assertEqual(nuevo.tiempo, esperado)
        self.assertEqual(nuevo.tipo, anterior.tipo)
        self.assertIs(nuevo.referencia, actor)
        self.assertGreater(nuevo.secuencia, anterior.secuencia)
        vigentes = [e for e in motor.cola.pendientes() if e.referencia is actor
                    and e.tipo == anterior.tipo]
        self.assertEqual(vigentes, [nuevo])
        return nuevo

    def situar_snapshot_unitario(self, motor, instante):
        """Preparación artificial de mitad de intervalo, no una acción del juego.

        Solo se usa para aislar la fórmula. No se saltan eventos anteriores
        al instante; no acredita historial ni origen del efecto de velocidad.
        """
        self.assertLessEqual(motor.reloj, instante)
        self.assertTrue(all(e.tiempo > instante for e in motor.cola.pendientes()))
        motor.reloj = instante

    def test_cola_descarta_cancelado_sin_afirmar_acciones_del_motor(self):
        cola = ColaEventos()
        referencia = object()
        anterior = cola.insertar(250, "turno_jugador", referencia)
        nuevo = cola.reprogramar(anterior, 150)
        self.assertTrue(anterior.cancelado)
        self.assertGreater(nuevo.secuencia, anterior.secuencia)
        self.assertIs(cola.extraer_minimo(), nuevo)
        self.assertIsNone(cola.extraer_minimo())

    def test_motor_procesa_un_solo_ataque_tras_reprogramar(self):
        # Estado sintético de un efecto temporal: velocidad base 200, reducción
        # a 100 desde t=0 y fin en t=50. Todo evento pasa por el motor real.
        with motor_terreno(250, velocidad_enemigo=200) as motor:
            enemigo = motor.enemigos_por_sala[100][0]
            motor.cambiar_velocidad(enemigo, 100)
            anterior = enemigo.evento_pendiente
            self.assertEqual(anterior.tiempo, 100)
            fin = motor.programar_evento(50, "restaurar_velocidad", (enemigo, 200))
            enemigo.evento_velocidad = fin
            azar_esperado = Random()
            azar_esperado.setstate(motor.azar.getstate())
            dano = max(1, enemigo.ataque + azar_esperado.randint(0, 4)
                       - motor.jugador.defensa)
            vida = motor.jugador.vida
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual(motor.reloj, 100)
            self.assertEqual(motor.acciones_jugador, 1)
            self.assertEqual(motor.jugador.vida, vida - dano)
            self.assertEqual(motor.azar.getstate(), azar_esperado.getstate())
            self.assertTrue(anterior.cancelado)
            self.assertFalse(anterior.en_cola)
            self.assertEqual(enemigo.velocidad, 200)
            self.assertIsNone(enemigo.evento_velocidad)
            self.assertEqual(enemigo.tiempo_siguiente, 125)
            self.assertEqual([e for e in motor.cola.pendientes()
                              if e.tipo == "turno_enemigo" and e.referencia is enemigo],
                             [enemigo.evento_pendiente])
            self.assertIsNone(motor.jugador.evento_pendiente)

    def test_aceleracion_aislada_t50_reprograma_250_a_150(self):
        for tipo in ("jugador", "enemigo"):
            with self.subTest(actor=tipo), motor_terreno(250) as motor:
                actor = motor.jugador if tipo == "jugador" else motor.enemigos_por_sala[100][0]
                motor._avanzar_actor(actor, 250)
                anterior = actor.evento_pendiente
                self.assertEqual(anterior.tiempo, 250)
                self.situar_snapshot_unitario(motor, 50)
                motor.cambiar_velocidad(actor, 200)
                self.comprobar_reprogramacion(motor, actor, anterior, 150)

    def test_ralentizacion_aislada_t50_reprograma_250_a_450(self):
        with motor_terreno(250) as motor:
            motor._avanzar_actor(motor.jugador, 250)
            anterior = motor.jugador.evento_pendiente
            self.situar_snapshot_unitario(motor, 50)
            motor.cambiar_velocidad(motor.jugador, 50)
            self.comprobar_reprogramacion(motor, motor.jugador, anterior, 450)

    def test_reprogramacion_conserva_intervalo_minimo_uno(self):
        with motor_terreno(1, velocidad=1000) as motor:
            motor._avanzar_actor(motor.jugador, 1)
            anterior = motor.jugador.evento_pendiente
            motor.cambiar_velocidad(motor.jugador, 10000)
            self.comprobar_reprogramacion(motor, motor.jugador, anterior, 1)

    def test_fin_de_efecto_aislado_reprograma_restante_a_225(self):
        with motor_terreno(250) as motor:
            motor._avanzar_actor(motor.jugador, 250)
            inicial = motor.jugador.evento_pendiente
            self.situar_snapshot_unitario(motor, 50)
            motor.cambiar_velocidad(motor.jugador, 200)
            acelerado = motor.jugador.evento_pendiente
            restaurar = motor.programar_evento(75, "restaurar_velocidad", (motor.jugador, 100))
            motor.jugador.evento_velocidad = restaurar
            self.assertIs(motor.ejecutar_ciclo(decidir_accion), restaurar)
            self.assertEqual(motor.reloj, 75)
            self.assertEqual(motor.jugador.velocidad, 100)
            self.assertIsNone(motor.jugador.evento_velocidad)
            self.assertTrue(inicial.cancelado)
            nuevo = self.comprobar_reprogramacion(motor, motor.jugador, acelerado, 225)
            self.assertGreater(nuevo.secuencia, restaurar.secuencia)

    def test_t7_parcial_movimiento_250_y_aceleracion(self):
        """Movimiento real y snapshot unitario posterior; no ciclo completo."""
        with motor_terreno(250) as motor:
            self.assertTrue(motor.mover("E")[0])
            anterior = motor.jugador.evento_pendiente
            self.assertEqual(anterior.tiempo, 250, "Pendiente T013: costo real del movimiento")
            self.situar_snapshot_unitario(motor, 50)
            motor.cambiar_velocidad(motor.jugador, 200)
            self.comprobar_reprogramacion(motor, motor.jugador, anterior, 150)

    def test_t7_parcial_movimiento_250_y_ralentizacion(self):
        with motor_terreno(250) as motor:
            self.assertTrue(motor.mover("E")[0])
            anterior = motor.jugador.evento_pendiente
            self.assertEqual(anterior.tiempo, 250, "Pendiente T013: costo real del movimiento")
            self.situar_snapshot_unitario(motor, 50)
            motor.cambiar_velocidad(motor.jugador, 50)
            self.comprobar_reprogramacion(motor, motor.jugador, anterior, 450)

    def test_t7_parcial_movimiento_aceleracion_y_fin_de_efecto(self):
        with motor_terreno(250) as motor:
            self.assertTrue(motor.mover("E")[0])
            inicial = motor.jugador.evento_pendiente
            self.assertEqual(inicial.tiempo, 250, "Pendiente T013: costo real del movimiento")
            self.situar_snapshot_unitario(motor, 50)
            motor.cambiar_velocidad(motor.jugador, 200)
            acelerado = self.comprobar_reprogramacion(motor, motor.jugador, inicial, 150)
            restaurar = motor.programar_evento(75, "restaurar_velocidad", (motor.jugador, 100))
            motor.jugador.evento_velocidad = restaurar
            self.assertIs(motor.ejecutar_ciclo(decidir_accion), restaurar)
            self.assertEqual(motor.jugador.velocidad, 100)
            self.assertIsNone(motor.jugador.evento_velocidad)
            nuevo = self.comprobar_reprogramacion(motor, motor.jugador, acelerado, 225)
            self.assertGreater(nuevo.secuencia, restaurar.secuencia)

    def comprobar_t7_integrado(self, velocidad_base, velocidad_temporal,
                              pendiente_inicial, siguiente, final):
        """FR-003/005/006/017: efecto temporal válido y agenda real completa.

        El estado inicial representa un efecto ya aplicado en t=0; su fin
        restaura exactamente la velocidad base del fixture. No se inventa
        un evento de aplicación ni se superponen efectos no soportados.
        """
        with motor_terreno(250, velocidad=velocidad_base,
                           velocidad_enemigo=25) as motor:
            jugador = motor.jugador
            self.assertEqual(motor.reloj, 0)
            self.assertIsNone(jugador.evento_pendiente)
            motor.cambiar_velocidad(jugador, velocidad_temporal)
            fin = motor.programar_evento(50, "restaurar_velocidad",
                                        (jugador, velocidad_base))
            jugador.evento_velocidad = fin

            # Una acción local real en la frontera inicial permite observar
            # su pendiente antes de procesar eventos. No se vuelve a llamar
            # a mover ni a ejecutar hasta consumir el nuevo turno del jugador.
            self.assertTrue(motor.mover("E")[0])
            inicial = jugador.evento_pendiente
            self.assertEqual(motor.reloj, 0)
            self.assertEqual(jugador.posicion_actual, 101)
            self.assertEqual(jugador.velocidad, velocidad_temporal)
            self.assertEqual(inicial.tiempo, pendiente_inicial)
            self.assertFalse(inicial.cancelado)

            self.assertIs(motor.ejecutar_ciclo(decidir_accion), fin)
            self.assertEqual(motor.reloj, 50)
            self.assertEqual(jugador.velocidad, velocidad_base)
            self.assertIsNone(jugador.evento_velocidad)
            nuevo = self.comprobar_reprogramacion(motor, jugador, inicial,
                                                  siguiente)
            self.assertGreater(nuevo.secuencia, fin.secuencia)
            self.assertTrue(inicial.en_cola)  # cancelación perezosa real

            procesados = []
            for _ in range(5):
                evento = motor.ejecutar_ciclo(decidir_accion)
                self.assertIsNotNone(evento)
                self.assertIsNot(evento, inicial)
                procesados.append(evento)
                if evento is nuevo:
                    break
            self.assertIs(procesados[-1], nuevo)
            self.assertEqual(motor.reloj, siguiente)
            self.assertEqual(sum(e.tipo == "turno_jugador" for e in procesados), 1)
            self.assertIsNone(jugador.evento_pendiente)

            # Ya llegó su turno: ejecutar una acción observable, comprobando
            # un solo daño y una sola tirada, no solo extracción de eventos.
            enemigo = motor.enemigos_por_sala[101][0]
            vida = enemigo.vida
            azar_esperado = Random()
            azar_esperado.setstate(motor.azar.getstate())
            dano = max(1, jugador.ataque + azar_esperado.randint(0, 4)
                       - enemigo.defensa)
            self.assertGreater(vida, dano)
            reloj_tras_ataque = siguiente + max(1, 100 * 100 // velocidad_base)
            self.assertTrue(motor.ejecutar("atacar", enemigo.id_instancia).ok)
            self.assertEqual(motor.reloj, reloj_tras_ataque)
            self.assertEqual(enemigo.vida, vida - dano)
            self.assertEqual(motor.azar.getstate(), azar_esperado.getstate())
            # mover local no incrementa el contador de ejecutar; las dos
            # acciones siguientes sí se cuentan por su API transaccional.
            self.assertEqual(motor.acciones_jugador, 1)
            self.assertIsNone(jugador.evento_pendiente)

            # Una nueva acción legal atraviesa también el tiempo cancelado.
            # Si reaparece el turno viejo, ejecutar terminaría antes de final.
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual(motor.reloj, final)
            self.assertGreater(motor.reloj, pendiente_inicial)
            self.assertEqual(jugador.posicion_actual, 102)
            self.assertEqual(motor.acciones_jugador, 2)
            self.assertEqual(enemigo.vida, vida - dano)
            self.assertTrue(inicial.cancelado)
            self.assertFalse(inicial.en_cola)
            self.assertIsNone(jugador.evento_pendiente)
            self.assertEqual([e for e in motor.cola.pendientes()
                              if e.tipo == "turno_jugador"], [])

    def test_t7_integrado_aceleracion_por_fin_de_ralentizacion(self):
        """T7: movimiento t=0, pendiente 250, fin t=50, turno t=150."""
        self.comprobar_t7_integrado(200, 100, 250, 150, 325)

    def test_t7_integrado_ralentizacion_por_fin_de_aceleracion(self):
        """T7: movimiento t=0, pendiente 250, fin t=50, turno t=450."""
        self.comprobar_t7_integrado(50, 100, 250, 450, 1150)

    def test_t7_integrado_fin_de_efecto_restaura_velocidad_base(self):
        """T7: movimiento a 200, pendiente 125, fin t=50, turno t=200."""
        self.comprobar_t7_integrado(100, 200, 125, 200, 550)


if __name__ == "__main__":
    unittest.main()
