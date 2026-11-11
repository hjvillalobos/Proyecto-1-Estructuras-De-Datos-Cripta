"""I5 C26–C30: protocolo local, sin simular una integración del motor."""
import unittest

from modelo.conocimiento_rutas import ConsultaRuta
from modelo.viaje import ControlViaje, ResultadoPaso


class PlanificadorPrueba:
    def __init__(self):
        self.respuesta = ConsultaRuta('paso', 20, 'E', 100, 200)
        self.llamadas = []

    def consultar(self, origen, destino):
        self.llamadas.append((origen, destino))
        return self.respuesta


def estado(viaje):
    return viaje.estado, viaje.posicion, viaje.destino, viaje.pendiente, viaje.causas


def resultado(posicion=20, aceptado=True, dano=False, entrada=True, enemigos=False, terminado=False):
    return ResultadoPaso(posicion, aceptado, dano, entrada, enemigos, terminado)


class TestViaje(unittest.TestCase):
    def setUp(self):
        self.plan = PlanificadorPrueba()
        self.viaje = ControlViaje(self.plan)

    def iniciar(self):
        self.viaje.iniciar(10, 30)
        return self.viaje.proponer()

    def test_rechazo_llegada_y_sin_ruta_no_proponen_movimiento(self):
        """C26 / FR-007/012."""
        for razon in ('destino_no_explorado', 'origen_no_explorado', 'sin_ruta', 'llegada'):
            with self.subTest(razon=razon):
                self.plan.respuesta = ConsultaRuta(razon)
                self.viaje.iniciar(10, 30)
                self.assertEqual(self.viaje.causas, (razon,))
                self.assertIsNone(self.viaje.proponer())

    def test_un_paso_pendiente_y_consulta_nueva_al_proponer(self):
        """C26/C27 / FR-009/010."""
        paso = self.iniciar()
        anterior = estado(self.viaje)
        with self.assertRaises(ValueError):
            self.viaje.proponer()
        with self.assertRaises(ValueError):
            self.viaje.iniciar(10, 40)
        self.assertEqual(estado(self.viaje), anterior)
        self.viaje.registrar_resultado(paso.numero, resultado())
        self.assertEqual(self.viaje.estado, 'listo')
        self.plan.respuesta = ConsultaRuta('paso', 30, 'N', 50, 50)
        siguiente = self.viaje.proponer()
        self.assertEqual((siguiente.origen, siguiente.ruta.direccion), (20, 'N'))
        self.assertEqual(self.plan.llamadas, [(10, 30), (10, 30), (20, 30)])
        self.viaje.registrar_resultado(siguiente.numero, resultado(30))
        self.assertEqual(self.viaje.causas, ('llegada',))
        self.assertIsNone(self.viaje.proponer())

    def test_rechazo_de_movimiento_permite_recalcular_sin_reintentar(self):
        """C27 / FR-010/012: observaciones se actualizan fuera de C."""
        paso = self.iniciar()
        self.viaje.registrar_resultado(paso.numero, resultado(10, False, entrada=False))
        self.assertEqual(len(self.plan.llamadas), 2)
        self.plan.respuesta = ConsultaRuta('sin_ruta')
        self.assertIsNone(self.viaje.proponer())
        self.assertEqual(self.viaje.causas, ('sin_ruta',))
        self.assertEqual(self.viaje.posicion, 10)

    def test_dano_enemigos_fin_y_causas_coincidentes(self):
        """C28 / FR-011/018: daño es hecho, no diferencia de vida."""
        for dano, enemigos, terminado, causas in (
                (True, False, False, ('dano',)),
                (False, True, False, ('enemigos',)),
                (False, False, True, ('fin_partida',)),
                (True, True, True, ('dano', 'enemigos', 'fin_partida'))):
            with self.subTest(causas=causas):
                paso = self.iniciar()
                self.viaje.registrar_resultado(paso.numero, resultado(dano=dano, enemigos=enemigos, terminado=terminado))
                self.assertEqual(self.viaje.causas, causas)
                self.assertIsNone(self.viaje.proponer())
        self.viaje.iniciar(10, 20)
        paso = self.viaje.proponer()
        self.viaje.registrar_resultado(paso.numero, resultado(dano=True, enemigos=True))
        self.assertEqual(self.viaje.causas, ('dano', 'enemigos', 'llegada'))

    def test_cancelacion_antes_y_despues_de_paso_no_reanuda(self):
        """C29 / FR-015 local: la reversión externa no activa viaje."""
        self.viaje.iniciar(10, 30)
        self.viaje.cancelar()
        self.viaje.cancelar()
        self.assertIsNone(self.viaje.proponer())
        paso = self.iniciar()
        self.viaje.registrar_resultado(paso.numero, resultado())
        self.viaje.cancelar()
        self.assertEqual(self.viaje.causas, ('cancelacion',))
        self.assertIsNone(self.viaje.proponer())

    def test_resultado_tardio_no_afecta_viaje_nuevo(self):
        """C29/C30 / FR-017: los números no se reciclan."""
        viejo = self.iniciar()
        self.viaje.cancelar()
        with self.assertRaises(ValueError):
            self.viaje.registrar_resultado(viejo.numero, resultado())
        nuevo = self.iniciar()
        anterior = estado(self.viaje)
        self.assertGreater(nuevo.numero, viejo.numero)
        with self.assertRaises(ValueError):
            self.viaje.registrar_resultado(viejo.numero, resultado())
        self.assertEqual(estado(self.viaje), anterior)

    def test_resultados_incoherentes_y_duplicados_no_mutan(self):
        """C30 / FR-009/017: validación antes de cambiar posición/estado."""
        paso = self.iniciar()
        anterior = estado(self.viaje)
        for recibido in (resultado(99), resultado(10, False, entrada=True),
                         resultado(20, True, entrada=False), resultado(99, False, entrada=False), None):
            with self.subTest(recibido=recibido):
                with self.assertRaises(ValueError):
                    self.viaje.registrar_resultado(paso.numero, recibido)
                self.assertEqual(estado(self.viaje), anterior)
        with self.assertRaises(ValueError):
            self.viaje.registrar_resultado(True, resultado())
        self.viaje.registrar_resultado(paso.numero, resultado())
        posterior = estado(self.viaje)
        with self.assertRaises(ValueError):
            self.viaje.registrar_resultado(paso.numero, resultado())
        self.assertEqual(estado(self.viaje), posterior)

    def test_datos_mal_tipados_y_fallo_busqueda_conservan_estado(self):
        """C30: no aceptar enteros como señales booleanas."""
        with self.assertRaises(ValueError):
            resultado(dano=1)
        with self.assertRaises(ValueError):
            resultado(-1)
        with self.assertRaises(ValueError):
            resultado(entrada=False, enemigos=True)
        self.viaje.iniciar(10, 30)
        anterior = estado(self.viaje)
        def fallar(*args):
            raise RuntimeError('Fallo de consulta')
        self.plan.consultar = fallar
        with self.assertRaises(RuntimeError):
            self.viaje.proponer()
        self.assertEqual(estado(self.viaje), anterior)


if __name__ == '__main__':
    unittest.main()
