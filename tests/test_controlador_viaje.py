import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from modelo.conocimiento import ConocimientoMapa, PuertaConocible, SalaConocible, SalidaConocible
from modelo.conocimiento_rutas import PlanificadorConocido
from modelo.snapshots import MetaPartida, ResultadoAccion
from modelo.viaje import ControlViaje, ResultadoPaso
from vista.consola import VistaConsola
from vista.grafica import VistaGrafica


class MotorPasosPrueba:
    def __init__(self):
        self.salas_conocibles = (
            SalaConocible(1, "Inicio", (SalidaConocible("N", 2, 100, 7), SalidaConocible("E", 3, 120))),
            SalaConocible(2, "Norte", (SalidaConocible("N", 4, 100),)),
            SalaConocible(3, "Este", (SalidaConocible("N", 4, 120),)),
            SalaConocible(4, "Salida", ()),
            SalaConocible(5, "Aislada", ()),
        )
        self.conocimiento = ConocimientoMapa(self.salas_conocibles, (PuertaConocible(7, 1, 2),), 1)
        for sala in (2, 3, 4, 5):
            self.conocimiento.entrar(sala)
        self.conocimiento.observar_puerta(1, 7, False)
        self.control_viaje = ControlViaje(PlanificadorConocido(self.conocimiento))
        self.posicion = 1
        self.meta = MetaPartida("prueba", "v1", "c1", 42)
        self.terminado = False
        self.movimientos = []
        self.dano = self.enemigos = False
        self.rechazar = False
        self.observar_cierre = True
        self.entregar_hechos = True

    def estado_vista(self):
        return SimpleNamespace(sala_id=self.posicion)

    def mapa_conocido(self):
        return self.conocimiento.mapa_conocido()

    def ejecutar(self, accion, direccion=None):
        self.movimientos.append((accion, direccion))
        if accion != "mover":
            return ResultadoAccion(True)
        if self.rechazar:
            self.rechazar = False
            if self.observar_cierre:
                self.conocimiento.observar_puerta(1, 7, True)
            return ResultadoAccion(False, "Puerta cerrada", hechos_paso=ResultadoPaso(
                self.posicion, False, False, False, False, False))
        sala = next(s for s in self.salas_conocibles if s.id == self.posicion)
        self.posicion = next(s.destino for s in sala.salidas if s.direccion == direccion)
        hechos = ResultadoPaso(self.posicion, True, self.dano, True, self.enemigos, self.terminado)
        return ResultadoAccion(True, hechos_paso=hechos if self.entregar_hechos else None)


class ControladorViajeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.modelo = MotorPasosPrueba()
        self.vista = Mock()
        self.control = ControladorJuego(self.modelo, self.vista, str(Path(self.tmp.name) / "viaje.log"))
        self.control.bitacora_replay.iniciar(self.modelo.meta)

    def iniciar(self, destino=4):
        self.control.procesar_comando(f"ir a {destino}")

    def acciones(self):
        return [(a.accion, a.argumento) for a in self.control.bitacora_replay.leer()[1]]

    def test_fr019_dos_pasos_con_c_real_orden_y_movimientos_en_replay(self):
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")):
            self.iniciar()
            self.assertEqual(self.modelo.movimientos, [])
            self.control._avanzar_viaje()
            self.assertEqual(self.modelo.posicion, 2)
            self.assertTrue(self.control._viaje_activo)
            self.control.procesar_comando("mapa")
            self.control._avanzar_viaje()
        self.assertEqual(self.modelo.posicion, 4)
        self.assertFalse(self.control._viaje_activo)
        self.vista.mostrar_info.assert_called_with("Viaje detenido: destino alcanzado.")
        self.assertEqual(self.acciones(), [("mover", "N"), ("mover", "N")])
        registros = [json.loads(linea) for linea in self.control.bitacora_replay.ruta.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(sum(r.get("tipo") == "comentario" for r in registros), 1)
        self.control._avanzar_viaje()
        self.assertEqual(len(self.modelo.movimientos), 2)

    def test_fr019_todas_las_causas_del_paso_sin_otro_movimiento(self):
        for dano, enemigos, terminal in ((True, False, False), (False, True, False), (True, True, True)):
            with self.subTest(dano=dano, enemigos=enemigos, terminal=terminal):
                self.modelo.posicion = 1
                self.modelo.terminado = False
                self.modelo.dano, self.modelo.enemigos = dano, enemigos
                self.iniciar(2)
                ejecutar = self.modelo.ejecutar
                def paso(*args):
                    self.modelo.terminado = terminal
                    return ejecutar(*args)
                with patch.object(self.modelo, "ejecutar", side_effect=paso):
                    self.control._avanzar_viaje()
                texto = self.vista.mostrar_info.call_args.args[0]
                self.assertIn("destino alcanzado", texto)
                if dano:
                    self.assertIn("daño recibido", texto)
                if enemigos:
                    self.assertIn("enemigos al entrar", texto)
                if terminal:
                    self.assertIn("fin de partida", texto)
                antes = len(self.modelo.movimientos)
                self.control._avanzar_viaje()
                self.assertEqual(len(self.modelo.movimientos), antes)

    def test_fr018_fr019_destino_no_explorado_sin_ruta_y_llegada_sin_acciones(self):
        for destino, motivo in ((999, "destino no explorado"), (5, "sin ruta conocida"), (1, "destino alcanzado")):
            with self.subTest(destino=destino):
                self.iniciar(destino)
                self.vista.mostrar_info.assert_called_with(f"Viaje detenido: {motivo}.")
                self.assertFalse(self.control._viaje_activo)
        self.assertEqual(self.modelo.movimientos, [])
        self.assertEqual(self.acciones(), [])

    def test_fr019_cancelacion_invalida_propuesta_y_permite_otro_viaje(self):
        self.iniciar()
        anterior = self.modelo.control_viaje.proponer()
        self.control.procesar_comando("cancelar")
        self.control._avanzar_viaje()
        self.assertEqual(self.modelo.movimientos, [])
        self.assertIsNone(self.modelo.control_viaje.pendiente)
        self.iniciar()
        self.control._avanzar_viaje()
        self.assertGreater(self.modelo.control_viaje._numero, anterior.numero)

    def test_fr007_fr019_cancelar_antes_de_pergamino_accion_manual_y_salida(self):
        for comando in ("retroceso", "usar pergamino", "esperar", "salir"):
            with self.subTest(comando=comando):
                self.control.ejecutando = True
                self.modelo.posicion = 1
                self.iniciar()
                def ejecutar(*args):
                    self.assertFalse(self.control._viaje_activo)
                    self.assertIsNone(self.modelo.control_viaje.pendiente)
                    return ResultadoAccion(True)
                with patch.object(self.modelo, "ejecutar", side_effect=ejecutar):
                    self.control.procesar_comando(comando)
                self.control._avanzar_viaje()
                self.assertFalse(self.control._viaje_activo)
        self.assertEqual(self.modelo.movimientos, [])

    def test_fr011_fr019_cancelar_antes_de_carga_incluso_si_falla(self):
        for falla in (False, True):
            with self.subTest(falla=falla):
                self.iniciar()
                def cargar(_):
                    self.assertFalse(self.control._viaje_activo)
                    if falla:
                        raise OSError("archivo roto")
                    return "estado"
                with patch("controlador.controlador.cargar_estado", side_effect=cargar):
                    self.modelo.restaurar_estado = Mock()
                    self.control._cargar("partida.bin")
                self.control._avanzar_viaje()
                self.assertEqual(self.modelo.movimientos, [])

    def test_fr019_sin_hechos_o_hechos_incompatibles_no_continua(self):
        self.modelo.entregar_hechos = False
        self.iniciar()
        with self.assertRaisesRegex(ValueError, "no entrega los hechos"):
            self.control._avanzar_viaje()
        self.control._avanzar_viaje()
        self.assertEqual(len(self.modelo.movimientos), 1)
        self.assertEqual(self.acciones(), [("mover", "N")])
        self.modelo.posicion = 1
        self.iniciar()
        with patch.object(self.modelo, "ejecutar", return_value=ResultadoAccion(
                False, hechos_paso=ResultadoPaso(2, True, False, True, False, False))):
            with self.assertRaisesRegex(ValueError, "no coinciden"):
                self.control._avanzar_viaje()
        self.assertFalse(self.control._viaje_activo)

    def test_fr019_excepcion_y_fallo_de_bitacora_no_programan_otro_paso(self):
        self.iniciar()
        with patch.object(self.modelo, "ejecutar", side_effect=RuntimeError("rollback")):
            with self.assertRaisesRegex(RuntimeError, "rollback"):
                self.control._avanzar_viaje()
        self.assertIsNone(self.modelo.control_viaje.pendiente)
        self.assertEqual(self.acciones(), [])
        self.iniciar()
        with patch.object(self.control.bitacora_replay, "registrar_accion", side_effect=OSError("disco")):
            self.control._avanzar_viaje()
        self.assertFalse(self.control.ejecutando)
        self.assertFalse(self.control._viaje_activo)
        self.control._avanzar_viaje()
        self.assertEqual(len(self.modelo.movimientos), 1)

    def test_fr019_rechazo_observado_recalcula_alternativa_sin_grabar_rechazo(self):
        self.modelo.rechazar = True
        self.iniciar()
        self.control._avanzar_viaje()
        self.assertEqual(self.acciones(), [])
        self.control._avanzar_viaje()
        self.assertEqual(self.modelo.posicion, 3)
        self.control._avanzar_viaje()
        self.assertEqual(self.modelo.posicion, 4)
        self.assertEqual(self.acciones(), [("mover", "E"), ("mover", "N")])

    def test_fr019_rechazo_sin_observacion_no_repite_el_mismo_movimiento(self):
        self.modelo.rechazar = True
        self.modelo.observar_cierre = False
        self.iniciar()
        self.control._avanzar_viaje()
        with self.assertRaisesRegex(ValueError, "ruta conocida no cambió"):
            self.control._avanzar_viaje()
        self.assertEqual(len(self.modelo.movimientos), 1)
        self.assertEqual(self.acciones(), [])

    def test_fr019_revalidar_conocimiento_y_posicion_antes_de_mover(self):
        self.iniciar()
        self.modelo.conocimiento.observar_puerta(1, 7, True)
        self.control._avanzar_viaje()
        self.assertEqual(self.modelo.posicion, 3)
        self.modelo.posicion = 1
        with self.assertRaisesRegex(ValueError, "posición cambió"):
            self.control._avanzar_viaje()
        self.assertEqual(len(self.modelo.movimientos), 1)

    def test_fr011_fr019_no_reutiliza_proveedor_reemplazado_tras_restaurar(self):
        self.iniciar()
        anterior = self.modelo.control_viaje
        nuevo = ControlViaje(PlanificadorConocido(self.modelo.conocimiento))
        self.modelo.control_viaje = nuevo
        with self.assertRaisesRegex(ValueError, "proveedor de viaje cambió"):
            self.control._avanzar_viaje()
        self.assertEqual(self.modelo.movimientos, [])
        self.assertEqual(anterior.estado, "detenido")
        self.iniciar()
        self.assertIs(self.control.control_viaje, nuevo)
        self.control._avanzar_viaje()
        self.assertEqual(self.modelo.posicion, 2)

    def test_fr019_bucle_consola_deja_comandos_entre_pasos_y_cierra_por_eof(self):
        comandos = iter(("ir a 4", "", "cancelar", "ir a 4", None))
        def entrada(_):
            comando = next(comandos)
            if comando is None:
                raise EOFError
            return comando
        self.control.vista = VistaConsola(entrada=entrada, salida=lambda _: None)
        self.control._mostrar_estado = Mock()
        self.control.iniciar()
        self.assertEqual(self.modelo.movimientos, [("mover", "N")])
        self.assertFalse(self.control._viaje_activo)
        self.assertIsNone(self.modelo.control_viaje.pendiente)


class EntradaViajeConsolaTest(unittest.TestCase):
    def test_fr019_terminal_interactiva_entrega_paso_sin_esperar_enter(self):
        with patch("builtins.input") as entrada, patch("vista.consola.sys.stdin") as stdin:
            stdin.isatty.return_value = True
            vista = VistaConsola(entrada=entrada, salida=lambda _: None)
            self.assertEqual(vista.pedir_comando_viaje(0), "")
            entrada.assert_not_called()

    def test_fr019_entrada_no_interactiva_permite_cancelar_entre_pasos(self):
        entrada = Mock(return_value="cancelar")
        vista = VistaConsola(entrada=entrada, salida=lambda _: None)
        self.assertEqual(vista.pedir_comando_viaje(), "cancelar")
        entrada.assert_called_once()

    @unittest.skipUnless(os.name == "nt", "Entrada de teclado Windows")
    def test_fr019_tecla_pendiente_atiende_comando_antes_del_paso(self):
        with patch("builtins.input", return_value="cancelar") as entrada, \
                patch("vista.consola.sys.stdin") as stdin, \
                patch("msvcrt.kbhit", return_value=True):
            stdin.isatty.return_value = True
            vista = VistaConsola(entrada=entrada, salida=lambda _: None)
            self.assertEqual(vista.pedir_comando_viaje(), "cancelar")
            entrada.assert_called_once()


class EntradaViajeGraficaTest(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.vista.cerrar)
        self.vista.root.withdraw()
        self.vista._refrescar_inv = False

    def test_fr019_espera_devuelve_turno_y_prioriza_cancelacion_sin_ejecutar_modelo(self):
        self.assertEqual(self.vista.pedir_comando_viaje(0), "")
        self.vista._refrescar_inv = False
        self.vista.root.after(0, lambda: self.vista._enviar("cancelar"))
        self.assertEqual(self.vista.pedir_comando_viaje(10), "cancelar")
        self.vista._refrescar_inv = False
        self.assertEqual(self.vista.pedir_comando_viaje(0), "")

    def test_fr019_cerrar_ventana_durante_espera_no_devuelve_un_paso(self):
        self.vista.root.after(0, self.vista.cerrar)
        self.assertIsNone(self.vista.pedir_comando_viaje(10))
