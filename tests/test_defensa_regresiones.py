import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from controlador.aplicacion import ejecutar_juego
from controlador.controlador import ControladorJuego
from red.errores import ErrorRed
from tests import test_regresiones_juego as base


class TestDefensaRegresiones(unittest.TestCase):
    def test_retroceso_fallido_conserva_estado_historial_y_pergamino(self):
        for accion in ("retroceso", "usar"):
            datos = base.TestRegresionesJuego()
            datos.setUp()
            datos._inventario("pergamino")
            self.assertTrue(datos.motor.ejecutar("esperar").ok)
            antes = datos.motor.exportar_estado()
            cantidad = datos.motor.historial.cantidad_turnos()
            controlador = ControladorJuego(datos.motor, Mock())
            controlador.bitacora_replay = Mock()
            with self.subTest(accion=accion), patch.object(
                    datos.motor, "_sincronizar_referencias", side_effect=OSError("disco inaccesible")):
                with self.assertRaises(OSError):
                    controlador._accion_modelo(accion, "pergamino" if accion == "usar" else None)
            self.assertEqual(datos.motor.exportar_estado(), antes)
            self.assertEqual(datos.motor.historial.cantidad_turnos(), cantidad)
            controlador.bitacora_replay.registrar_accion.assert_not_called()
            self.assertTrue(datos.motor.ejecutar(accion, "pergamino" if accion == "usar" else None).ok)
            self.assertEqual(datos.motor.reloj, 0)
            self.assertEqual(datos.motor.jugador.tiempo_siguiente, 0)
            self.assertEqual(datos.motor.jugador.inventario.tamaño, 0)

    def test_retroceso_prepara_fichas_consumidas_antes_de_mutar(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        datos._inventario("pergamino")
        datos._inventario("pocion")
        datos.motor.jugador.vida = 10
        datos.motor.ejecutar("usar", "pocion")
        fijar = Mock()
        datos.motor.gestor_precarga.catalogo.fijar_referencias = fijar
        self.assertTrue(datos.motor.ejecutar("retroceso").ok)
        self.assertIn("pocion", fijar.call_args.args[0])
        self.assertEqual(fijar.call_count, 1)
        self.assertEqual(datos.motor.jugador.vida, 10)
        self.assertEqual([o.tipo_catalogo for o in datos.motor.jugador.inventario], ["pocion"])

    def test_rutas_con_espacios_comillas_y_barras_windows(self):
        controlador = ControladorJuego(Mock(), Mock())
        rutas = ("datos_generados/mi partida.bin", r"C:\Users\Belén\New project\partida.bin")
        for verbo, metodo in (("guardar", "_guardar"), ("cargar", "_cargar"), ("replay", "_replay")):
            for ruta in rutas:
                for comilla in ("", '"', "'"):
                    with self.subTest(verbo=verbo, ruta=ruta, comilla=comilla), \
                            patch.object(controlador, metodo) as llamado:
                        controlador.procesar_comando(f"{verbo} {comilla}{ruta}{comilla}")
                        llamado.assert_called_once_with([ruta] if verbo == "replay" else ruta)

    def test_guardar_y_cargar_archivo_real_con_espacios(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        with tempfile.TemporaryDirectory() as carpeta:
            controlador = ControladorJuego(datos.motor, Mock(), str(Path(carpeta) / "replay.log"))
            controlador.bitacora_replay.iniciar(datos.motor.meta)
            ruta = str(Path(carpeta) / "mi partida.bin")
            estado = datos.motor.exportar_estado()
            controlador.procesar_comando(f'guardar "{ruta}"')
            self.assertTrue(Path(ruta).is_file())
            datos.motor.ejecutar("esperar")
            controlador.procesar_comando(f'cargar "{ruta}"')
            self.assertEqual(datos.motor.exportar_estado(), estado)

    def test_reinicio_error_persistente_permite_salir_o_reintentar(self):
        for reintentar in (False, True):
            args = SimpleNamespace(gui=True, cripta="cripta-01", semilla=20)
            vista, sesion = Mock(), Mock()
            vista.mostrar_menu.side_effect = [("jugar", None), ("jugar" if reintentar else "salir", None)]
            vista.preguntar_reinicio.side_effect = [True, False]
            sesion.renovar.side_effect = [ErrorRed("sin datos"), None]
            with self.subTest(reintentar=reintentar), \
                    patch("vista.grafica.VistaGrafica", return_value=vista), \
                    patch("modelo.juego.crear_juego", return_value=Mock(resultado="derrota")), \
                    patch("controlador.controlador.ControladorJuego"):
                self.assertEqual(ejecutar_juego(args, sesion, Mock()), 0)
            vista.mostrar_error_replay.assert_called_once()
            self.assertEqual(sesion.renovar.call_count, 2 if reintentar else 1)
            for llamada in sesion.renovar.call_args_list:
                self.assertEqual(llamada.kwargs, {"tolerar_error": True})
            vista.cerrar.assert_called_once()
