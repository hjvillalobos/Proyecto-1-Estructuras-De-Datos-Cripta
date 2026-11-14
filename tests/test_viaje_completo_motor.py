"""I11 C43–C45: viaje real offline; no habilita la aplicación normal."""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from datos.offline import ClienteOffline
from modelo.juego import Motor, crear_juego
from modelo.conocimiento_rutas import PlanificadorConocido
from modelo.viaje import ControlViaje
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import crear_paquete


@unittest.skipUnless(hasattr(Motor, '_resultado_paso'),
                     'Ejecutar utilidades.verificar_viaje_completo con la entrega real de A')
class TestViajeCompletoMotor(unittest.TestCase):
    @contextmanager
    def partida(self, trampa=False):
        with TemporaryDirectory(prefix='c-viaje-real-') as carpeta:
            almacen = crear_paquete(carpeta, salas=5)
            if trampa:
                almacen.guardar_ficha('cat1', {'id': 'trampa-viaje', 'clase': 'trampa',
                    'nombre': 'Trampa de prueba', 'daño': 2, 'rearme': 100})
            for sala in range(100, 105):
                contenido = almacen.leer_contenido('prueba', 'v1', sala)
                contenido['enemigos'] = []
                contenido['objetos'] = []
                contenido['trampas'] = ([{'instancia': 'trampa-102', 'tipo': 'trampa-viaje'}]
                                        if trampa and sala == 102 else [])
                almacen.guardar_contenido('prueba', 'v1', contenido)
            with patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP')) as http:
                cliente = ClienteOffline(carpeta, 'v1')
                precarga = GestorPrecarga(cliente, GestorCatalogo(
                    cliente, CacheCatalogoOrdenado(25), cliente.almacen))
                try:
                    motor = crear_juego(precarga, 'prueba', semilla=927,
                        version_cripta='v1', version_catalogo='cat1', conocimiento_para_pruebas=True)
                    vista = Mock()
                    viaje = ControlViaje(PlanificadorConocido(motor._conocimiento))
                    control = ControladorJuego(motor, vista, str(Path(carpeta) / 'viaje.log'),
                                               control_viaje=viaje)
                    control.bitacora_replay.iniciar(motor.meta)
                    # Conocer el camino por entradas reales, nunca por precarga.
                    for direccion in ('E', 'E', 'E', 'O', 'O', 'O'):
                        control.procesar_comando('mover ' + direccion)
                        self.assertTrue(control.ultimo_resultado_accion.ok)
                    self.assertEqual(motor.jugador.posicion_actual, 100)
                    yield motor, control, vista
                    http.assert_not_called()
                    self.assertEqual(cliente.solicitudes_realizadas, 0)
                finally:
                    precarga.cerrar()
                    cliente.cerrar()

    def acciones(self, control):
        return tuple((a.accion, a.argumento) for a in control.bitacora_replay.leer()[1])

    def estado(self, motor):
        return (motor.reloj, motor.jugador.posicion_actual, motor.jugador.vida,
                motor.acciones_jugador, motor.azar.getstate(), motor._conocimiento.mapa_conocido())

    def test_c43_tres_pasos_coinciden_con_movimientos_manuales(self):
        with self.partida() as (motor, control, vista), self.partida() as (manual, otro, _):
            inicio = motor.reloj
            control.procesar_comando('ir a 103')
            for destino in (101, 102, 103):
                control._avanzar_viaje()
                self.assertEqual(motor.jugador.posicion_actual, destino)
                otro.procesar_comando('mover E')
                self.assertEqual(self.estado(motor), self.estado(manual))
            self.assertEqual(motor.reloj - inicio, 300)
            self.assertEqual(control.control_viaje.causas, ('llegada',))
            self.assertFalse(control._viaje_activo)
            self.assertEqual(self.acciones(control), self.acciones(otro))
            self.assertEqual(len(self.acciones(control)), 9)
            antes = self.estado(motor), control.bitacora_replay.ruta.read_bytes()
            control._avanzar_viaje()
            self.assertEqual((self.estado(motor), control.bitacora_replay.ruta.read_bytes()), antes)
            vista.mostrar_error.assert_not_called()

    def test_c44_cancelar_entre_pasos_no_ejecuta_otro(self):
        with self.partida() as (motor, control, vista):
            control.procesar_comando('ir a 103')
            control._avanzar_viaje()
            self.assertEqual(motor.jugador.posicion_actual, 101)
            control.procesar_comando('cancelar')
            antes = self.estado(motor), control.bitacora_replay.ruta.read_bytes()
            control._avanzar_viaje()
            control._avanzar_viaje()
            self.assertEqual((self.estado(motor), control.bitacora_replay.ruta.read_bytes()), antes)
            self.assertEqual(control.control_viaje.causas, ('cancelacion',))
            self.assertEqual(len(self.acciones(control)), 7)
            vista.mostrar_error.assert_not_called()

    def test_c45_dano_intermedio_detiene_antes_del_tercer_paso(self):
        with self.partida(trampa=True) as (motor, control, vista):
            control.procesar_comando('ir a 103')
            control._avanzar_viaje()
            self.assertTrue(control._viaje_activo)
            vida = motor.jugador.vida
            control._avanzar_viaje()
            self.assertEqual(motor.jugador.posicion_actual, 102)
            self.assertLess(motor.jugador.vida, vida)
            self.assertTrue(control.ultimo_resultado_accion.hechos_paso.recibio_dano)
            self.assertFalse(control.ultimo_resultado_accion.hechos_paso.enemigos_al_entrar)
            self.assertEqual(control.control_viaje.causas, ('dano',))
            antes = self.estado(motor), control.bitacora_replay.ruta.read_bytes()
            control._avanzar_viaje()
            self.assertEqual((self.estado(motor), control.bitacora_replay.ruta.read_bytes()), antes)
            self.assertEqual(len(self.acciones(control)), 8)
            vista.mostrar_error.assert_not_called()
