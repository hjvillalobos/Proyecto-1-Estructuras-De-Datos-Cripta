"""T011/T016: A1/A2/T6, FR-001/002/003/004/011; costos verificados.

Movimiento ponderado y demás costos verificados con datos válidos, sin expectedFailure.
"""

import unittest
from random import Random

from modelo.enemigos import decidir_accion
from modelo.juego import calcular_intervalo
from modelo.tipos import ObjetoInstancia
from tests.datos_terreno_cazador import SIN_COSTO_DECLARADO, motor_terreno


class PruebasCostosTerreno(unittest.TestCase):
    def comprobar_movimiento_jugador(self, costo, velocidad, reloj, esperado):
        with motor_terreno(costo, velocidad) as motor:
            if reloj == 20:
                self.assertEqual(velocidad, 1000)
                for _ in range(2):
                    self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual(motor.reloj, reloj)
            vida = motor.jugador.vida
            # Una sola acción local en una frontera de decisión real. Se
            # observa el estado inmediato, antes de procesar su intervalo.
            ok, mensaje = motor.mover("E")
            self.assertTrue(ok, mensaje)
            self.assertEqual(motor.jugador.posicion_actual, 101)
            self.assertEqual(motor.jugador.vida, vida)
            self.assertEqual(motor.reloj, reloj)
            self.assertEqual(motor.jugador.tiempo_siguiente, esperado)
            self.assertEqual(motor.jugador.evento_pendiente.tiempo, esperado)

    def comprobar_movimiento_enemigo(self, comportamiento, costo, velocidad,
                                    reloj, esperado):
        velocidad_jugador = 1000 if reloj == 20 else 100
        with motor_terreno(costo, velocidad_jugador, comportamiento,
                           velocidad) as motor:
            enemigo = motor.enemigos_por_sala[100][0]
            if reloj == 20:
                # Ataca legalmente en t=10 porque aún comparte sala. Queda
                # listo para su primer movimiento en t=20, tras salir el jugador.
                self.assertTrue(motor.ejecutar("esperar").ok)
                self.assertEqual(motor.reloj, 10)
            turno = enemigo.evento_pendiente
            self.assertEqual(turno.tiempo, 20 if reloj == 20 else 100)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            for _ in range(2):
                if not turno.en_cola:
                    break
                self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertFalse(turno.en_cola)
            self.assertFalse(turno.cancelado)
            self.assertEqual(enemigo.sala_actual, 101)
            self.assertGreaterEqual(motor.reloj, turno.tiempo)
            intervalo_esperado = esperado - reloj
            self.assertEqual(enemigo.tiempo_siguiente, turno.tiempo + intervalo_esperado)
            self.assertEqual(enemigo.evento_pendiente.tiempo,
                             turno.tiempo + intervalo_esperado)

    def test_formula_de_intervalo_con_costos_validos(self):
        for costo, velocidad, intervalo in ((100, 100, 100), (250, 100, 250),
                                            (250, 200, 125), (1, 1000, 1)):
            with self.subTest(costo=costo, velocidad=velocidad):
                self.assertEqual(calcular_intervalo(costo, velocidad), intervalo)

    def test_fixture_prepara_datos_y_agenda_antes_de_crear_el_motor(self):
        with motor_terreno(250, 1000, "rastreador", 500, True) as motor:
            self.assertEqual(motor.reloj, 0)
            self.assertEqual(motor.jugador.posicion_actual, 100)
            self.assertEqual(motor.jugador.velocidad, 1000)
            self.assertIsNone(motor.jugador.evento_pendiente)
            enemigo = motor.enemigos_por_sala[100][0]
            self.assertEqual(enemigo.comportamiento, "rastreador")
            self.assertEqual(enemigo.velocidad, 500)
            self.assertEqual(enemigo.evento_pendiente.tiempo, 20)
            precarga = motor.gestor_precarga
            pagina = precarga.almacen.leer_pagina("prueba", "v1", 1)
            for fuente in (motor.salas[100].salidas,
                           precarga._sala(100).salidas,
                           pagina["salas"][0]["salidas"]):
                self.assertEqual(fuente["E"]["costo"], 250)
                self.assertTrue(fuente["E"]["cerrada"])
                self.assertEqual(fuente["E"]["llave"], "obj_0")
            for sala, direccion in ((100, "E"), (101, "O")):
                self.assertIn((sala, direccion, True, True), motor._puertas_iniciales)

    def test_jugador_costo_ausente_100(self):
        self.comprobar_movimiento_jugador(SIN_COSTO_DECLARADO, 100, 0, 100)

    def test_jugador_costo_250(self):
        self.comprobar_movimiento_jugador(250, 100, 0, 250)

    def test_jugador_minimo_uno_en_t20(self):
        self.comprobar_movimiento_jugador(1, 1000, 20, 21)

    def test_errante_costo_ausente_100(self):
        self.comprobar_movimiento_enemigo("errante", SIN_COSTO_DECLARADO, 100, 0, 100)

    def test_rastreador_costo_ausente_100(self):
        self.comprobar_movimiento_enemigo("rastreador", SIN_COSTO_DECLARADO, 100, 0, 100)

    def test_errante_costo_250(self):
        self.comprobar_movimiento_enemigo("errante", 250, 100, 0, 250)

    def test_rastreador_costo_250(self):
        self.comprobar_movimiento_enemigo("rastreador", 250, 100, 0, 250)

    def test_errante_minimo_uno_en_t20(self):
        self.comprobar_movimiento_enemigo("errante", 1, 1000, 20, 21)

    def test_rastreador_minimo_uno_en_t20(self):
        self.comprobar_movimiento_enemigo("rastreador", 1, 1000, 20, 21)

    def test_movimiento_reciproco_costo_250(self):
        with motor_terreno(250) as motor:
            self.assertEqual(motor.salas[100].salidas["E"]["costo"], 250)
            self.assertEqual(motor.salas[101].salidas["O"]["costo"], 250)
            inicio = motor.reloj
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            ida = motor.reloj - inicio
            self.assertEqual(motor.jugador.posicion_actual, 101)
            self.assertIsNone(motor.jugador.evento_pendiente)
            inicio = motor.reloj
            self.assertTrue(motor.ejecutar("mover", "O").ok)
            vuelta = motor.reloj - inicio
            self.assertEqual(motor.jugador.posicion_actual, 100)
            self.assertEqual(motor.acciones_jugador, 2)
            self.assertIsNone(motor.jugador.evento_pendiente)
            self.assertEqual((ida, vuelta), (250, 250))

    def test_demas_acciones_conservan_costos_de_parte_i(self):
        for accion, esperado in (("esperar", 100), ("atacar", 100),
                                  ("usar", 50), ("equipar", 50),
                                  ("abrir", 50), ("recoger", 25), ("soltar", 25)):
            with self.subTest(accion=accion), motor_terreno(
                    250, puerta_inicial_cerrada=accion == "abrir") as motor:
                argumento = None
                if accion == "atacar":
                    argumento = motor.enemigos_por_sala[100][0].id_instancia
                elif accion in ("equipar", "soltar"):
                    objeto = motor.objetos_en_suelo[100][0]
                    motor.objetos_en_suelo[100].remove(objeto)
                    motor.jugador.inventario.recoger(objeto)
                    argumento = objeto.id_instancia
                elif accion == "usar":
                    motor.gestor_precarga.catalogo.retener(["pocion"])
                    objeto = ObjetoInstancia("pocion-sintetica", "pocion", "inventario")
                    motor.jugador.inventario.recoger(objeto)
                    argumento = objeto.id_instancia
                elif accion == "abrir":
                    motor.gestor_precarga.catalogo.retener(["obj_0"])
                    motor.jugador.inventario.recoger(
                        ObjetoInstancia("llave-sintetica", "obj_0", "inventario"))
                    for sala, direccion in ((100, "E"), (101, "O")):
                        self.assertTrue(motor.salas[sala].salidas[direccion]["cerrada"])
                        self.assertIn((sala, direccion, True, True), motor._puertas_iniciales)
                    argumento = "E"
                elif accion == "recoger":
                    argumento = motor.objetos_en_suelo[100][0].id_instancia
                resultado = motor.ejecutar(accion, argumento)
                self.assertTrue(resultado.ok, resultado.mensaje)
                self.assertEqual(motor.jugador.tiempo_siguiente, esperado)
                self.assertEqual(motor.reloj, esperado)

    def test_movimiento_sin_ataques_gratuitos_respeta_agenda_y_empates(self):
        """T016: FR-003/004/006/011/016, A1/A2/A9; P1 §§2.3–2.5.

        Amplía la posición inmediata ya probada con evidencia semántica de
        daño/azar y orden real; no duplica los siete casos de otros costos.
        """
        for costo in (250, 100):
            with self.subTest(costo=costo), motor_terreno(costo) as motor:
                origen = motor.enemigos_por_sala[100][0]
                destino = motor.enemigos_por_sala[101][0]
                inicial_origen = origen.evento_pendiente
                self.assertIsNone(destino.evento_pendiente)
                vida = motor.jugador.vida
                vidas_enemigas = (origen.vida, destino.vida)
                azar_esperado = Random()
                azar_esperado.setstate(motor.azar.getstate())

                # Única acción local al iniciar, sin procesar aún su intervalo.
                self.assertTrue(motor.mover("E")[0])
                jugador = motor.jugador.evento_pendiente
                inicial_destino = destino.evento_pendiente
                self.assertEqual(motor.reloj, 0)
                self.assertEqual(motor.jugador.posicion_actual, 101)
                self.assertEqual(jugador.tiempo, costo)
                self.assertEqual(motor.jugador.vida, vida)
                self.assertEqual(motor.azar.getstate(), azar_esperado.getstate())
                self.assertIs(origen.evento_pendiente, inicial_origen)
                self.assertFalse(inicial_origen.cancelado)
                self.assertEqual(inicial_destino.tiempo, 100)
                self.assertLess(inicial_origen.secuencia, jugador.secuencia)
                self.assertLess(jugador.secuencia, inicial_destino.secuencia)

                cronologia = ((origen, 100), (motor.jugador, 100))
                if costo == 250:
                    cronologia = ((origen, 100), (destino, 100),
                                  (origen, 200), (destino, 200),
                                  (motor.jugador, 250))
                dano = 0
                anterior = None
                for actor, instante in cronologia:
                    evento = motor.ejecutar_ciclo(decidir_accion)
                    self.assertIsNotNone(evento)
                    self.assertIs(evento.referencia, actor)
                    self.assertEqual(evento.tiempo, instante)
                    self.assertEqual(motor.reloj, instante)
                    if anterior is not None and anterior.tiempo == instante:
                        self.assertLess(anterior.secuencia, evento.secuencia)
                    anterior = evento
                    if actor is destino:
                        dano += max(1, destino.ataque + azar_esperado.randint(0, 4)
                                    - motor.jugador.defensa)
                    if actor is motor.jugador:
                        self.assertIs(evento, jugador)
                    else:
                        self.assertEqual(actor.evento_pendiente.tiempo, instante + 100)
                        self.assertGreater(actor.evento_pendiente.secuencia,
                                           evento.secuencia)
                    self.assertEqual(motor.jugador.vida, vida - dano)
                    self.assertEqual(motor.azar.getstate(), azar_esperado.getstate())
                    self.assertEqual((origen.vida, destino.vida), vidas_enemigas)
                    self.assertEqual(motor.jugador.posicion_actual, 101)
                self.assertIsNone(motor.jugador.evento_pendiente)

                if costo == 100:
                    # El turno del jugador ganó el empate. El ataque de
                    # destino sigue pendiente en t=100 y se procesa al esperar
                    # legalmente desde esa decisión, sin recibir un turno gratis.
                    self.assertIs(destino.evento_pendiente, inicial_destino)
                    self.assertTrue(inicial_destino.en_cola)
                    self.assertFalse(inicial_destino.cancelado)
                    dano = max(1, destino.ataque + azar_esperado.randint(0, 4)
                               - motor.jugador.defensa)
                    self.assertTrue(motor.ejecutar("esperar").ok)
                    self.assertEqual(motor.reloj, 200)
                    self.assertEqual(motor.acciones_jugador, 1)
                    self.assertEqual(motor.jugador.vida, vida - dano)
                    self.assertEqual(motor.azar.getstate(), azar_esperado.getstate())
                    self.assertEqual(destino.evento_pendiente.tiempo, 200)
                    self.assertIsNone(motor.jugador.evento_pendiente)


if __name__ == "__main__":
    unittest.main()
