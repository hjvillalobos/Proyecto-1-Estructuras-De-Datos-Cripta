"""C31/C32: ensayo H3 real y acotado; no adaptador de producción."""
import unittest
from importlib.util import find_spec


@unittest.skipUnless(find_spec('modelo.linea_tiempo') and find_spec('tests.datos_terreno_cazador'),
                     'Ejecutar python -m utilidades.verificar_viaje_motor con A y D reales')
class TestViajeMotor(unittest.TestCase):
    def preparar(self, motor):
        from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible
        from modelo.conocimiento_historia import campos_iniciales
        from modelo.conocimiento_rutas import PlanificadorConocido
        from modelo.viaje import ControlViaje
        from modelo.linea_tiempo import EstadoHistorico, LineaTiempo

        # Camino ya explorado: no atribuir exploración a la precarga de A.
        salas = tuple(SalaConocible(i, motor.salas[i].nombre, tuple(
            SalidaConocible(d, s['sala'], s.get('costo', 100))
            for d, s in motor.salas[i].salidas.items())) for i in (100, 101, 102, 103))
        mapa = ConocimientoMapa(salas, (), 100)
        for i in (101, 102, 103):
            mapa.entrar(i)
        historia = LineaTiempo(EstadoHistorico(motor.proyeccion_h3() + campos_iniciales(mapa)), 2)
        viaje = ControlViaje(PlanificadorConocido(mapa))
        viaje.iniciar(100, 102)
        motor.cola.fijar_contador(10)
        return mapa, historia, viaje

    def registrar(self, historia, inicio, fin, ordinal, cambios, eventos, invalidar=False):
        from modelo.snapshots import CambioHistorico, ValorHistorico, EventoHistorico
        self.assertEqual((inicio, ordinal), (historia.reloj, historia.cantidad_acciones + 1))
        if invalidar:
            cambios += (cambios[0],)  # Repetir movimiento con valor anterior ya consumido.
        def convertir(lote):
            return tuple(CambioHistorico(k, ValorHistorico(True, a), ValorHistorico(True, b))
                         for k, a, b in lote)
        historia.registrar_accion(fin, convertir(cambios), tuple(
            EventoHistorico(t, s, convertir(lote)) for t, s, lote in eventos))

    def test_guardian_detiene_tras_eventos_y_conserva_historia(self):
        """C31 / FR-009/011/016 parcial: no ejecutar un segundo movimiento."""
        from tests.datos_terreno_cazador import motor_terreno
        from modelo.viaje import ResultadoPaso
        with motor_terreno() as motor:
            mapa, historia, viaje = self.preparar(motor)
            conocido = mapa.mapa_conocido()
            paso = viaje.proponer()
            self.assertEqual((paso.origen, paso.ruta.siguiente), (100, 101))
            self.assertTrue(any(e.vida > 0 for e in motor.enemigos_por_sala[101]))
            lotes = []
            def registrar(*lote):
                self.assertEqual(motor.historial.cantidad_turnos(), 0)
                self.registrar(historia, *lote)
                lotes.append(lote)
            vida = motor.jugador.vida
            resultado = motor.ejecutar('mover', paso.ruta.direccion, registrar_h3=registrar)
            self.assertTrue(resultado.ok)
            self.assertEqual(len(lotes), 1)
            # Ataque concreto del guardián H3; no detector genérico de daño.
            ataque = next(cambios for tiempo, secuencia, cambios in lotes[0][4]
                          if tiempo == 100 and secuencia == 11)
            cambio_vida = next((antes, despues) for clave, antes, despues in ataque if clave == 'jugador')
            self.assertLess(cambio_vida[1][0], cambio_vida[0][0])
            viaje.registrar_resultado(paso.numero, ResultadoPaso(
                motor.jugador.posicion_actual, resultado.ok, True, True, True, motor.terminado))
            self.assertEqual(viaje.causas, ('dano', 'enemigos'))
            frontera = motor.reloj, motor.acciones_jugador, motor.jugador.vida
            self.assertIsNone(viaje.proponer())
            self.assertEqual((motor.reloj, motor.acciones_jugador, motor.jugador.vida), frontera)
            self.assertEqual(frontera[:2], (100, 1))
            self.assertEqual(historia.consultar_t(99).estado.obtener('jugador')[0], vida)
            self.assertEqual(historia.consultar_t(100).estado.obtener('jugador')[0], motor.jugador.vida)
            self.assertEqual(historia.consultar_t(100).estado.obtener('conocimiento:sala:101'), 2)
            self.assertEqual(mapa.mapa_conocido(), conocido)

    def test_rechazo_historia_revierte_motor_y_cancela_viaje(self):
        """C32 / FR-009/017: la excepción no confirma el paso de C."""
        from tests.datos_terreno_cazador import motor_terreno
        from tests.test_cambios_historicos_motor import estado_motor
        from modelo.errores_historia import ErrorHistoria
        with motor_terreno() as motor:
            mapa, historia, viaje = self.preparar(motor)
            antes = estado_motor(motor), historia.exportar(), mapa.mapa_conocido()
            paso = viaje.proponer()
            def rechazar(*lote):
                self.registrar(historia, *lote, invalidar=True)
            with self.assertRaises(ErrorHistoria):
                try:
                    motor.ejecutar('mover', paso.ruta.direccion, registrar_h3=rechazar)
                except ErrorHistoria:
                    viaje.cancelar()
                    raise
            self.assertEqual((estado_motor(motor), historia.exportar(), mapa.mapa_conocido()), antes)
            self.assertEqual(viaje.causas, ('cancelacion',))
            self.assertIsNone(viaje.proponer())


if __name__ == '__main__':
    unittest.main()
