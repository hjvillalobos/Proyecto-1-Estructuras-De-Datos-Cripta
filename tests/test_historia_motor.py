"""Pruebas de D con un productor de contrato."""
import io
import struct
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import main
from controlador.controlador import ControladorJuego
from controlador.partida_historica import integrar_historia
from controlador.resumen_historia import consultar
from datos.guardado_binario import (ArchivoGuardado, ErrorGuardado, FormatoIncompatible, GuardadoCorrupto,
                                     guardar_estado, cargar_estado_partida)
from datos.historia_binaria import codificar_historia, decodificar_historia
from modelo.errores_historia import CambioHistoriaIncoherente, ReferenciaHistoricaInvalida
from modelo.juego import Motor, crear_juego
from modelo.linea_tiempo import LineaTiempo
from red.sesion import SesionDatos
from tests.datos_integracion_d import ProductorPrueba, cambio
from tests.datos_prueba import crear_paquete
from tests.datos_terreno_cazador import motor_terreno


class HistoriaMotorTest(unittest.TestCase):
    def test_fr001_fr002_fr003_fr005_costos_eventos_empatados_y_consulta_pura(self):
        productor = ProductorPrueba()
        partida = integrar_historia(productor, 2)
        self.assertTrue(partida.ejecutar("mover", "E").ok)
        estado = partida.exportar_estado()
        historia = partida.linea_tiempo
        self.assertEqual(historia.consultar_accion(1).estado.obtener("sala")[0], 1)
        self.assertEqual(historia.consultar_t(249).estado.obtener("sala")[0], 2)
        self.assertEqual(historia.consultar_t(249).estado.obtener("jugador")[0], 20)
        self.assertEqual(historia.consultar_t(250).estado.obtener("jugador")[0], productor.vida)
        self.assertEqual(historia.consultar_t(250).estado.obtener("mapa:2"), "Patio explorado")
        with self.assertRaises(ReferenciaHistoricaInvalida):
            historia.consultar_t(251)
        self.assertEqual(estado, partida.exportar_estado())
        self.assertTrue(partida.ejecutar("esperar").ok)
        self.assertEqual(consultar(historia, "250").estado.obtener("jugador")[0],
                         estado.jugador.vida)
        self.assertEqual(consultar(historia, "#2").estado.obtener("jugador")[0],
                         estado.jugador.vida)

    def test_fr002_fr003_h3_frontera_del_motor_real(self):
        with motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            partida = integrar_historia(motor, 2)
            if partida is motor:
                self.skipTest("Falta el productor de cambios históricos del motor.")
            vida_inicial = motor.jugador.vida
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            self.assertEqual(motor.reloj, 100)
            vida_en_la_frontera = motor.jugador.vida
            self.assertLess(vida_en_la_frontera, vida_inicial)
            self.assertTrue(partida.ejecutar("esperar").ok)
            historia = partida.linea_tiempo
            for referencia, vida in (("99", vida_inicial), ("100", vida_en_la_frontera),
                                     ("#2", vida_en_la_frontera)):
                with self.subTest(referencia=referencia):
                    self.assertEqual(consultar(historia, referencia).estado.obtener("jugador")[0],
                                     vida)

    def _comprobar_historia_guardado_replay(self, productor, carpeta, opciones, instante):
        partida = integrar_historia(productor, 2)
        vista = Mock()
        bitacora = carpeta / "partida.log"
        guardado = carpeta / "partida.bin"
        control = ControladorJuego(partida, vista, str(bitacora), partida_p2=True)
        control.bitacora_replay.iniciar(partida.meta)
        inicial = partida.exportar_estado()
        control.procesar_comando("mover E")
        esperado = partida.exportar_estado()
        self.assertEqual(esperado.reloj, instante)
        self.assertLess(esperado.jugador.vida, inicial.jugador.vida)
        control.procesar_comando(f"historia {instante}")
        resumen = vista.mostrar_info.call_args.args[0]
        self.assertIn(f"Historia t={instante}", resumen)
        self.assertIn(f"Vida {esperado.jugador.vida}/", resumen)

        control.procesar_comando(f'guardar "{guardado}"')
        with ArchivoGuardado(guardado) as archivo:
            self.assertEqual(archivo.version, 4)
        self.assertEqual(cargar_estado_partida(guardado), esperado)
        control.procesar_comando("esperar")
        self.assertGreater(partida.reloj, instante)
        control.procesar_comando("historia #2")
        self.assertEqual(vista.mostrar_info.call_args.args[0], resumen)
        control.procesar_comando(f'cargar "{guardado}"')
        self.assertEqual(partida.exportar_estado(), esperado)
        control.procesar_comando(f"historia {instante}")
        self.assertEqual(vista.mostrar_info.call_args.args[0], resumen)
        self.assertEqual([paso.accion for paso in control.bitacora_replay.leer()[1]],
                         ["mover", "esperar", "cargar"])
        vista.mostrar_error.assert_not_called()

        guardado.unlink()
        with redirect_stdout(io.StringIO()) as salida, \
                patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
            codigo = main.main([*opciones, "--replay", str(bitacora), "--hasta", str(instante)])
        self.assertEqual(codigo, 0)
        self.assertEqual(salida.getvalue().rstrip("\n"), resumen)

    def test_fr002_fr011_fr013_historia_guardado_replay_con_productor_de_prueba(self):
        with TemporaryDirectory() as tmp, \
                patch("modelo.juego.crear_juego", side_effect=lambda *a, **k: ProductorPrueba()):
            opciones = ["--offline", tmp, "--datos-dir", tmp, "--checkpoint-cada", "2"]
            self._comprobar_historia_guardado_replay(ProductorPrueba(), Path(tmp), opciones, 250)

    def test_fr002_fr011_fr013_historia_guardado_replay_con_motor_real(self):
        if not callable(getattr(Motor, "conectar_historia", None)):
            self.skipTest("Falta el productor de cambios históricos del motor.")
        if not callable(getattr(Motor, "restaurar_estado_con_historia", None)):
            self.skipTest("Falta la restauración conjunta de estado e historia.")
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            paquete = raiz / "paquete"
            crear_paquete(paquete, salas=4)
            opciones = ["--offline", str(paquete), "--datos-dir", str(paquete),
                        "--checkpoint-cada", "2"]
            sesion = SesionDatos(main.leer_argumentos(opciones))
            try:
                sesion.abrir()
                sesion.preparar()
                motor = crear_juego(sesion.precarga, "prueba", semilla=20261105)
                self._comprobar_historia_guardado_replay(motor, raiz, opciones, 100)
            finally:
                sesion.cerrar()

    def test_fr002_fr011_accion_terminal_instantanea_respeta_la_decision(self):
        historia = LineaTiempo(ProductorPrueba().estado_historico_inicial(), 1)
        inicial = (20, 20, 5, 3, 100)
        final = (0, 20, 5, 3, 100)
        historia.registrar_accion(0, (cambio("jugador", inicial, final),), terminal=True)
        copia = decodificar_historia(codificar_historia(historia))
        self.assertEqual(copia.consultar_t(0).estado.obtener("jugador"), inicial)
        self.assertEqual(copia.consultar_accion(1).estado.obtener("jugador"), inicial)
        self.assertEqual(copia.consultar_final().estado.obtener("jugador"), final)
        with self.assertRaises(CambioHistoriaIncoherente):
            copia.registrar_accion(10)

    def test_fr007_pergamino_descarta_futuro_y_corrige_rama(self):
        partida = integrar_historia(ProductorPrueba(), 1)
        partida.ejecutar("mover", "E")
        partida.ejecutar("retroceso")
        with self.assertRaises(ReferenciaHistoricaInvalida):
            partida.linea_tiempo.consultar_t(250)
        with self.assertRaises(KeyError):
            partida.linea_tiempo.consultar_t(0).estado.obtener("inventario:00")
        partida.ejecutar("esperar")
        self.assertEqual(partida.linea_tiempo.consultar_t(250).estado.obtener("sala")[0], 1)

    def test_fr011_guardar_cargar_conserva_historia_k_y_continuacion(self):
        a = integrar_historia(ProductorPrueba(), 3)
        b = integrar_historia(ProductorPrueba(), 50)
        a.ejecutar("mover", "E")
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "partida.bin"
            guardar_estado(a.exportar_estado(), ruta)
            with ArchivoGuardado(ruta) as archivo:
                self.assertEqual(archivo.version, 4)
                self.assertEqual(archivo.leer_sala(2).sala_id, 2)
            b.restaurar_estado(cargar_estado_partida(ruta))
        self.assertEqual(a.linea_tiempo.exportar(), b.linea_tiempo.exportar())
        self.assertEqual(b.linea_tiempo.checkpoint_cada, 3)
        for partida in (a, b):
            partida.ejecutar("esperar")
        self.assertEqual(a.exportar_estado(), b.exportar_estado())

    def test_fr011_si_falla_reemplazo_v4_se_conserva_el_archivo_y_se_limpia(self):
        partida = integrar_historia(ProductorPrueba(), 4)
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "partida.bin"
            guardar_estado(partida.exportar_estado(), ruta)
            anterior = ruta.read_bytes()
            partida.ejecutar("mover", "E")
            with patch("datos.guardado_binario.os.replace", side_effect=OSError("disco")):
                with self.assertRaisesRegex(ErrorGuardado, "disco"):
                    guardar_estado(partida.exportar_estado(), ruta)
            self.assertEqual(ruta.read_bytes(), anterior)
            self.assertEqual(list(Path(tmp).iterdir()), [ruta])

    def test_fr011_fr012_rechaza_v3_corrupcion_y_frontera_incoherente(self):
        partida = integrar_historia(ProductorPrueba(), 4)
        partida.ejecutar("mover", "E")
        antes = partida.exportar_estado()
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "partida.bin"
            guardar_estado(replace(antes, historia=None), ruta)
            with self.assertRaisesRegex(FormatoIncompatible, "Parte I"):
                cargar_estado_partida(ruta)
            guardar_estado(antes, ruta)
            datos = bytearray(ruta.read_bytes())
            inicio, longitud = struct.unpack_from("<QQ", datos, 32)
            datos[inicio + longitud - 1] ^= 1
            ruta.write_bytes(datos)
            with self.assertRaises(GuardadoCorrupto):
                partida.restaurar_estado(cargar_estado_partida(ruta))
            struct.pack_into("<Q", datos, 32, 1)
            ruta.write_bytes(datos)
            with self.assertRaises(GuardadoCorrupto):
                cargar_estado_partida(ruta)
        with self.assertRaises(GuardadoCorrupto):
            partida.restaurar_estado(replace(antes, reloj=antes.reloj + 1))
        self.assertEqual(partida.restauraciones, 0)
        self.assertEqual(partida.exportar_estado(), antes)
