"""DX-01..06: consumidor D con motor A, datos B y mapa/viaje C reales.

Activación offline explícita de la entrega de A. Solo se simula la vista y
se bloquean HTTP/constructores de vista; no se parchean reglas ni resultados.
"""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from controlador.partida_historica import integrar_historia
from controlador.replay_sin_vista import reproducir
from controlador.resumen_historia import consultar, resumir
from datos.guardado_binario import ArchivoGuardado, guardar_estado
from modelo.conocimiento_rutas import PlanificadorConocido
from modelo.juego import crear_juego
from modelo.tipos import ObjetoInstancia
from modelo.viaje import ControlViaje
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from datos.offline import ClienteOffline
from tests.datos_prueba import crear_paquete


class ControladorACRealTest(TestCase):
    @contextmanager
    def partida(self, *, mapa=False, historia=True):
        with TemporaryDirectory(prefix="d-ac-real-") as carpeta:
            raiz = Path(carpeta)
            paquete = raiz / "paquete"
            almacen = crear_paquete(paquete, salas=4)
            almacen.guardar_ficha("cat1", {"id": "pergamino-d", "clase": "pergamino_retroceso",
                                           "nombre": "Pergamino"})
            with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")) as http:
                cliente = ClienteOffline(str(paquete), "v1")
                precarga = GestorPrecarga(cliente, GestorCatalogo(
                    cliente, CacheCatalogoOrdenado(25), cliente.almacen))
                try:
                    motor = crear_juego(precarga, "prueba", semilla=42,
                                        version_cripta="v1", version_catalogo="cat1",
                                        historia_para_pruebas=historia,
                                        conocimiento_para_pruebas=mapa)
                    juego = integrar_historia(motor, 2) if historia else motor
                    vista = Mock()
                    viaje = ControlViaje(PlanificadorConocido(motor._conocimiento)) if mapa else None
                    control = ControladorJuego(juego, vista, str(raiz / "partida.log"),
                                               partida_p2=historia, control_viaje=viaje)
                    control.bitacora_replay.iniciar(motor.meta)
                    yield motor, juego, control, vista, raiz, precarga
                finally:
                    try:
                        precarga.cerrar()
                    finally:
                        cliente.cerrar()
                http.assert_not_called()
                self.assertEqual(cliente.solicitudes_realizadas, 0)

    def acciones(self, control):
        return [a.accion for a in control.bitacora_replay.leer()[1]]

    def test_dx01_consultas_reales_son_puras_y_respetan_frontera(self):
        with self.partida() as (motor, juego, control, vista, _, __):
            vida_inicial = motor.jugador.vida
            control.procesar_comando("mover E")
            vida_100 = motor.jugador.vida
            self.assertLess(vida_100, vida_inicial)
            control.procesar_comando("esperar")
            antes = juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()
            for referencia, vida in (("99", vida_inicial), ("100", vida_100), ("#2", vida_100)):
                with self.subTest(referencia=referencia):
                    control.procesar_comando("historia " + referencia)
                    self.assertEqual(vista.mostrar_info.call_args.args[0],
                                     resumir(consultar(juego.linea_tiempo, referencia)))
                    self.assertEqual(consultar(juego.linea_tiempo, referencia).estado.obtener("jugador")[0], vida)
            self.assertEqual((juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()), antes)
            vista.mostrar_error.assert_not_called()

    def test_dx02_comandos_guardar_cargar_y_continuar_con_historia_real(self):
        with self.partida() as (motor, juego, control, vista, raiz, _):
            control.procesar_comando("mover E")
            guardado = juego.exportar_estado()
            ruta = raiz / "con espacios.bin"
            control.procesar_comando(f'guardar "{ruta}"')
            with ArchivoGuardado(ruta) as archivo:
                self.assertEqual(archivo.version, 4)
            control.procesar_comando("esperar")
            esperado = juego.exportar_estado()
            control.procesar_comando(f'cargar "{ruta}"')
            self.assertEqual(juego.exportar_estado(), guardado)
            control.procesar_comando("esperar")
            self.assertEqual(juego.exportar_estado(), esperado)
            control.procesar_comando("historia #2")
            self.assertIn("Historia t=100", vista.mostrar_info.call_args.args[0])
            self.assertEqual(self.acciones(control), ["mover", "esperar", "cargar", "esperar"])
            vista.mostrar_error.assert_not_called()

    def test_dx02_cargas_invalidas_no_mutan_ni_se_graban(self):
        with self.partida() as (motor, juego, control, vista, raiz, _):
            control.procesar_comando("mover E")
            p1, roto = raiz / "p1.bin", raiz / "roto.bin"
            guardar_estado(motor.exportar_estado(), str(p1))
            guardar_estado(juego.exportar_estado(), str(roto))
            roto.write_bytes(roto.read_bytes()[:-1])
            antes = juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()
            for ruta in (p1, roto):
                with self.subTest(ruta=ruta.name):
                    vista.reset_mock()
                    control.procesar_comando(f'cargar "{ruta}"')
                    vista.mostrar_error.assert_called_once()
                    self.assertEqual((juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()), antes)

    def test_dx02_pergamino_recorta_historia_y_log_permite_nueva_rama(self):
        with self.partida() as (motor, juego, control, vista, _, __):
            motor.jugador.inventario.recoger(ObjetoInstancia("p-d", "pergamino-d", "inventario"))
            control.procesar_comando("mover E")
            control.procesar_comando("esperar")
            control.procesar_comando("retroceso")
            self.assertEqual((motor.reloj, juego.linea_tiempo.cantidad_acciones), (100, 1))
            self.assertEqual(motor.jugador.inventario.contar("pergamino-d"), 0)
            control.procesar_comando("mover O")
            self.assertEqual((motor.reloj, motor.jugador.posicion_actual), (200, 100))
            self.assertEqual(juego.linea_tiempo.consultar_accion(2).estado.obtener("sala")[0], 101)
            self.assertEqual(self.acciones(control), ["mover", "esperar", "retroceso", "mover"])
            vista.mostrar_error.assert_not_called()

    def test_dx03_log_del_controlador_reproduce_carga_sin_archivo_ni_vista(self):
        with self.partida() as (motor, juego, control, vista, raiz, precarga):
            ruta = raiz / "partida.bin"
            control.procesar_comando("mover E")
            control.procesar_comando(f'guardar "{ruta}"')
            control.procesar_comando("esperar")
            control.procesar_comando(f'cargar "{ruta}"')
            control.procesar_comando("mover O")
            ruta.unlink()
            esperados = [(t, resumir(consultar(juego.linea_tiempo, str(t)))) for t in (99, 100, 200)]
            final = resumir(juego.linea_tiempo.consultar_final())
            def fabrica(fuente, cripta_id, semilla, **versiones):
                return crear_juego(fuente, cripta_id, semilla, historia_para_pruebas=True, **versiones)
            with patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                    patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
                for t, esperado in esperados:
                    self.assertEqual(reproducir(control.bitacora_replay.ruta, precarga, fabrica, 2, t), esperado)
                self.assertEqual(reproducir(control.bitacora_replay.ruta, precarga, fabrica, 2, 201),
                                 "El replay terminó antes de t=201.\n" + final)
            vista.mostrar_error.assert_not_called()

    def test_dx04_mapa_del_controlador_refleja_entradas_reales(self):
        with self.partida(mapa=True, historia=False) as (motor, _, control, vista, __, ___):
            control.procesar_comando("mapa")
            self.assertNotIn("103", vista.mostrar_info.call_args.args[0])
            self.assertEqual(motor.jugador.posicion_actual, 100)
            control.procesar_comando("mover E")
            antes = motor.exportar_estado(), control.bitacora_replay.ruta.read_bytes()
            control.procesar_comando("mapa")
            self.assertIn(motor.salas[101].nombre, vista.mostrar_info.call_args.args[0])
            self.assertEqual((motor.exportar_estado(), control.bitacora_replay.ruta.read_bytes()), antes)
            vista.mostrar_error.assert_not_called()

    def test_dx05_cancelar_viaje_real_no_ejecuta_ni_graba_paso(self):
        with self.partida(mapa=True, historia=False) as (motor, _, control, vista, __, ___):
            control.procesar_comando("mover E")
            control.procesar_comando("mover O")
            antes = motor.exportar_estado(), self.acciones(control)
            control.procesar_comando("ir a 101")
            self.assertTrue(control._viaje_activo)
            control.procesar_comando("cancelar")
            control._avanzar_viaje()
            self.assertEqual((motor.exportar_estado(), self.acciones(control)), antes)
            self.assertIsNone(control.control_viaje.pendiente)
            vista.mostrar_error.assert_not_called()

    def test_dx05_sin_hechos_del_motor_se_detiene_despues_del_paso_grabado(self):
        with self.partida(mapa=True, historia=False) as (motor, _, control, vista, __, ___):
            control.procesar_comando("mover E")
            control.procesar_comando("mover O")
            control.procesar_comando("ir a 101")
            with self.assertRaisesRegex(ValueError, "no entrega los hechos"):
                control._avanzar_viaje()
            self.assertIsNone(control.ultimo_resultado_accion.hechos_paso)
            self.assertEqual((motor.jugador.posicion_actual, motor.acciones_jugador), (101, 3))
            self.assertFalse(control._viaje_activo)
            self.assertIsNone(control.control_viaje.pendiente)
            antes = motor.exportar_estado(), control.bitacora_replay.ruta.read_bytes()
            control._avanzar_viaje()
            self.assertEqual((motor.exportar_estado(), control.bitacora_replay.ruta.read_bytes()), antes)
            self.assertEqual(self.acciones(control), ["mover", "mover", "mover"])

    def test_dx06_carga_con_mapa_activo_rechazada_sin_publicacion_parcial(self):
        with self.partida(mapa=True) as (motor, juego, control, vista, raiz, _):
            control.procesar_comando("mover E")
            ruta = raiz / "mapa.bin"
            control.procesar_comando(f'guardar "{ruta}"')
            control.procesar_comando("esperar")
            antes = juego.exportar_estado(), motor.mapa_conocido(), control.bitacora_replay.ruta.read_bytes()
            control.procesar_comando(f'cargar "{ruta}"')
            self.assertIn("no admite el mapa conocido activo", vista.mostrar_error.call_args.args[0])
            self.assertEqual((juego.exportar_estado(), motor.mapa_conocido(), control.bitacora_replay.ruta.read_bytes()), antes)
