import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
from importlib.util import find_spec
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys
from unittest.mock import Mock, patch

import main
from controlador.aplicacion import ejecutar_juego
from controlador.verificacion import VerificacionNoDisponible, texto_reporte, verificar
from datos.almacen import AlmacenLocal
from datos.bitacora_replay import BitacoraReplay, RUTA_REPLAY_PREDETERMINADA
from tests.datos_integracion_d import ProductorPrueba, reporte_prueba
from tests.datos_prueba import crear_paquete
from tests.datos_terreno_cazador import motor_terreno
from tests.test_verificacion_datos import ServidorVerificacion


class ModosHistoriaTest(unittest.TestCase):
    def test_fr013_ac18_ac21_no_completada_muestra_causa_y_alcance_sin_diagnostico(self):
        from modelo.resolubilidad import LIMITACION, ResultadoVerificacion

        for reporte in (ResultadoVerificacion("no_completada", "prueba", causa="Faltan llaves"),
                        VerificacionNoDisponible("prueba")):
            with self.subTest(tipo=type(reporte).__name__):
                self.assertEqual(texto_reporte(reporte).splitlines(), [
                    "Verificación de prueba: no completada", LIMITACION, reporte.causa])

    def test_fr008_fr020_argumentos_invalidos_antes_de_abrir_sesion(self):
        casos = (
            ["--checkpoint-cada", "0"], ["--checkpoint-cada", "a"], ["--hasta", "4"],
            ["--replay", "partida.log", "--hasta", "-1"], ["--replay", "p", "--gui"],
            ["--verificar", "id", "--replay", "p"], ["--verificar", "id", "--forzar"],
            ["--bench", "--verificar", "id"],
        )
        with patch("main.SesionDatos") as sesion, redirect_stderr(io.StringIO()):
            for argumentos in casos:
                with self.subTest(argumentos=argumentos), self.assertRaises(SystemExit) as salida:
                    main.main(argumentos)
                self.assertEqual(salida.exception.code, 2)
            sesion.assert_not_called()

    def test_fr013_fr014_fr017_replay_completo_y_hasta_sin_vista(self):
        with TemporaryDirectory() as tmp:
            ruta = str(Path(tmp) / "partida.log")
            log = BitacoraReplay(ruta)
            log.iniciar(ProductorPrueba().meta)
            log.registrar_accion("mover", "E")
            for argumentos, contenido in (([], "t=250"), (["--hasta", "249"], "t=249"),
                                          (["--hasta", "300"], "terminó antes de t=300")):
                salida = io.StringIO()
                with self.subTest(argumentos=argumentos), redirect_stdout(salida), \
                        patch("main.SesionDatos"), \
                        patch("modelo.juego.crear_juego", side_effect=lambda *a, **k: ProductorPrueba()), \
                        patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                        patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
                    self.assertEqual(main.main(["--replay", ruta, *argumentos]), 0)
                self.assertIn(contenido, salida.getvalue())
                self.assertIn("Patio", salida.getvalue())

    def test_fr017_motor_actual_reproduce_sin_vista_y_explica_si_falta_historia(self):
        with motor_terreno(250) as motor, TemporaryDirectory() as tmp:
            ruta = str(Path(tmp) / "partida.log")
            log = BitacoraReplay(ruta)
            log.iniciar(motor.meta)
            log.registrar_accion("mover", "E")
            salida = io.StringIO()
            error = io.StringIO()
            with redirect_stdout(salida), redirect_stderr(error), patch("main.SesionDatos") as sesion, \
                    patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                    patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
                sesion.return_value.precarga = motor.gestor_precarga
                self.assertEqual(main.main(["--replay", ruta]), 0)
                self.assertEqual(main.main(["--replay", ruta, "--hasta", "100"]), 1)
            self.assertIn("Replay t=250", salida.getvalue())
            self.assertIn("todavía no entrega cambios", error.getvalue())

    def test_fr013_replay_respeta_carga_y_retroceso_posteriores(self):
        from controlador.partida_historica import integrar_historia
        partida = integrar_historia(ProductorPrueba(), 9)
        partida.ejecutar("esperar")
        with TemporaryDirectory() as tmp:
            ruta = str(Path(tmp) / "partida.log")
            log = BitacoraReplay(ruta)
            log.iniciar(partida.meta)
            log.registrar_accion("mover", "E")
            log.registrar_accion("retroceso")
            log.registrar_carga(partida.exportar_estado())
            salida = io.StringIO()
            with redirect_stdout(salida), patch("main.SesionDatos"), \
                    patch("modelo.juego.crear_juego", side_effect=lambda *a, **k: ProductorPrueba()):
                self.assertEqual(main.main(["--replay", ruta, "--hasta", "150"]), 0)
            self.assertIn("Entrada", salida.getvalue())
            self.assertNotIn("Patio", salida.getvalue())

    def test_fr015_verificar_no_crea_juego_ni_catalogo_ni_vista(self):
        salida = io.StringIO()
        with redirect_stdout(salida), patch("main.SesionDatos") as sesion, \
                patch("controlador.verificacion.verificar", return_value=reporte_prueba("resoluble")), \
                patch("modelo.juego.crear_juego", side_effect=AssertionError("juego")), \
                patch("vista.consola.VistaConsola", side_effect=AssertionError("vista")), \
                patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista")):
            self.assertEqual(main.main(["--verificar", "prueba"]), 0)
        sesion.return_value.preparar.assert_not_called()
        self.assertIn("Orden de llaves: llave", salida.getvalue())

    def test_fr016_no_resoluble_solo_inicia_con_forzar(self):
        for estado, forzar, inicia in (("no_resoluble", False, False),
                                      ("no_resoluble", True, True),
                                      ("no_completada", True, False),
                                      ("resoluble", False, True)):
            args = SimpleNamespace(gui=False, semilla=42, cripta="prueba",
                                   checkpoint_cada=50, forzar=forzar)
            with self.subTest(estado=estado, forzar=forzar), \
                    patch("controlador.aplicacion.verificar", return_value=reporte_prueba(estado)), \
                    patch("vista.consola.VistaConsola") as vista, \
                    patch("modelo.juego.crear_juego", return_value=ProductorPrueba()) as crear, \
                    patch("controlador.controlador.ControladorJuego") as control:
                self.assertEqual(ejecutar_juego(args, Mock(), None), int(not inicia))
            self.assertEqual(crear.called, inicia)
            self.assertEqual(control.called, inicia)
            self.assertEqual(vista.return_value.mostrar_informe.called, inicia)

    def test_fr015_fr016_r4_cli_offline_con_verificador_real(self):
        if find_spec("red.verificacion") is None:
            self.skipTest("Falta integrar el verificador de B.")
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            paquete = raiz / "paquete"
            almacen = crear_paquete(paquete, salas=2)
            # La llave de salida está en la sala a la que solo ella permite entrar.
            pagina = almacen.leer_pagina("prueba", "v1", 1)
            for sala in pagina["salas"]:
                for salida in sala["salidas"].values():
                    salida.update(cerrada=True, llave="obj_0")
            almacen.guardar_pagina("prueba", "v1", pagina)
            contenido = almacen.leer_contenido("prueba", "v1", 101)
            contenido["objetos"].append("obj_0")
            almacen.guardar_contenido("prueba", "v1", contenido)
            almacen.guardar_llaves("prueba", "v1", {"llaves": [{"id": "obj_0", "sala": 101}]})
            comando = [sys.executable, "-B", "-X", "utf8", str(Path(main.__file__).resolve()),
                       "--offline", str(paquete), "--datos-dir", str(paquete)]
            bitacora = raiz / RUTA_REPLAY_PREDETERMINADA
            casos = ((["--verificar", "prueba"], 1, False),
                     (["--cripta", "prueba", "--semilla", "42"], 1, False),
                     (["--cripta", "prueba", "--semilla", "42", "--forzar"], 0, True))
            for argumentos, codigo, inicio in casos:
                with self.subTest(argumentos=argumentos):
                    salida = run([*comando, *argumentos], cwd=raiz, input="salir\n",
                                 capture_output=True, encoding="utf-8", timeout=20)
                    self.assertEqual(salida.returncode, codigo, salida.stdout + salida.stderr)
                    self.assertIn("Verificación de prueba: no resoluble", salida.stdout)
                    self.assertIn("Llave inaccesible obj_0: sala 101", salida.stdout)
                    self.assertIn("Ciclo (", salida.stdout)
                    self.assertEqual(bitacora.is_file(), inicio, salida.stdout)
                    if inicio:
                        self.assertLess(salida.stdout.index("Verificación de prueba"),
                                        salida.stdout.index("Partida iniciada."))

    def test_fr015_paquete_descargado_se_verifica_offline(self):
        # B FR-008–011: el mismo paquete contiene esqueleto, contenido y llaves.
        servidor = ServidorVerificacion(salas=7)
        servidor.llaves = {"llaves": [{"id": "obj_0", "sala": 105}]}
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida, \
                patch("red.cliente_api.ClienteApi", return_value=servidor):
            self.assertEqual(main.main(["--cripta", "prueba", "--descargar-todo",
                                        "--datos-dir", tmp]), 0)
            almacen = AlmacenLocal(tmp)
            self.assertEqual(almacen.leer_llaves("prueba", "v1"), servidor.llaves)
            self.assertIn("obj_0", almacen.leer_contenido("prueba", "v1", 105)["objetos"])
            self.assertIn("Respuestas completas guardadas", salida.getvalue())
            self.assertEqual([tipo for tipo, _ in servidor.llamadas].count("llaves"), 1)
            solicitudes = servidor.solicitudes_realizadas
            salida.seek(0)
            salida.truncate()
            self.assertEqual(main.main(["--offline", tmp, "--datos-dir", tmp,
                                        "--verificar", "prueba"]), 0)
            self.assertIn("Verificación de prueba: resoluble", salida.getvalue())
            self.assertEqual(servidor.solicitudes_realizadas, solicitudes)

    def test_fr015_descarga_rechaza_llaves_si_cambia_la_version(self):
        servidor = ServidorVerificacion(salas=2)
        servidor.version_final = "v2"
        with TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida, \
                redirect_stderr(io.StringIO()) as errores, \
                patch("red.cliente_api.ClienteApi", return_value=servidor):
            self.assertEqual(main.main(["--cripta", "prueba", "--descargar-todo",
                                        "--datos-dir", tmp]), 1)
            almacen = AlmacenLocal(tmp)
            self.assertIsNone(almacen.leer_llaves("prueba", "v1"))
            self.assertIsNone(almacen.leer_generales("prueba", "v1"))
            self.assertNotIn("Respuestas completas guardadas", salida.getvalue())
            self.assertIn("cambió durante la adquisición", errores.getvalue())

    def test_fr016_forzar_no_inicia_con_paquete_sin_llaves(self):
        # B FR-012 y AC-18: falta de datos no equivale a cripta no resoluble.
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            paquete = raiz / "paquete"
            crear_paquete(paquete, salas=2)
            comando = [sys.executable, "-B", "-X", "utf8", str(Path(main.__file__).resolve()),
                       "--offline", str(paquete), "--datos-dir", str(paquete)]
            for argumentos in (["--verificar", "prueba"], ["--cripta", "prueba", "--forzar"]):
                with self.subTest(argumentos=argumentos):
                    salida = run([*comando, *argumentos], cwd=raiz, input="salir\n",
                                 capture_output=True, encoding="utf-8", timeout=20)
                    self.assertEqual(salida.returncode, 1, salida.stdout + salida.stderr)
                    self.assertIn("Verificación de prueba: no completada", salida.stdout)
                    self.assertIn("Verificación por alcanzabilidad acumulada; no garantiza una trayectoria única si hay salidas sin regreso.", salida.stdout)
                    self.assertFalse((raiz / RUTA_REPLAY_PREDETERMINADA).exists())
            descarga = run([*comando, "--cripta", "prueba", "--descargar-todo"], cwd=raiz,
                           capture_output=True, encoding="utf-8", timeout=20)
            self.assertEqual(descarga.returncode, 1, descarga.stdout + descarga.stderr)
            self.assertNotIn("Respuestas completas guardadas", descarga.stdout)
            self.assertIn(str(paquete.resolve()), descarga.stderr)

    def test_fr013_detiene_el_replay_cuando_no_hay_revisiones_posteriores(self):
        with TemporaryDirectory() as tmp:
            ruta = str(Path(tmp) / "partida.log")
            log = BitacoraReplay(ruta)
            log.iniciar(ProductorPrueba().meta)
            log.registrar_accion("mover", "E")
            log.registrar_accion("inexistente")
            salida = io.StringIO()
            with redirect_stdout(salida), patch("main.SesionDatos"), \
                    patch("modelo.juego.crear_juego", side_effect=lambda *a, **k: ProductorPrueba()):
                self.assertEqual(main.main(["--replay", ruta, "--hasta", "150"]), 0)
            self.assertIn("t=150", salida.getvalue())

    def test_fr015_delega_la_version_y_el_almacen_de_datos_offline(self):
        modulo = SimpleNamespace(verificar_cripta=Mock(return_value=reporte_prueba()))
        sesion = Mock()
        with patch.dict(sys.modules, {"red.verificacion": modulo}):
            verificar(sesion, "prueba", "v1")
            modulo.verificar_cripta.assert_called_once_with(
                sesion.cliente, sesion.cliente.almacen, "prueba", "v1")

    def test_fr015_reporte_negativo_expone_frontera_ubicacion_y_ciclo(self):
        reporte = reporte_prueba("no_resoluble")
        reporte.llaves_inalcanzables = [SimpleNamespace(
            id="negra", ubicaciones=[SimpleNamespace(sala=9, enemigo="guardián")])]
        reporte.frontera = [SimpleNamespace(origen=8, direccion="E", destino=9, llave="negra")]
        reporte.evidencia = [SimpleNamespace(tipo="llave", identificador="negra"),
                             SimpleNamespace(tipo="sala", identificador=9)]
        reporte.ciclos = [SimpleNamespace(clasificacion="bloqueo_circular_autonomo",
                                          testigo=[0, 1, 0], integrantes=[0, 1],
                                          bloqueos_externos=[])]
        texto = texto_reporte(reporte)
        self.assertIn("sala 9, enemigo guardián", texto)
        self.assertIn("Puerta 8 E → 9: negra", texto)
        self.assertIn("llave negra → sala 9 → llave negra", texto)

    def test_fr015_no_confunde_modulo_ausente_con_no_resoluble(self):
        resultado = VerificacionNoDisponible("prueba")
        self.assertIn("no completada", texto_reporte(resultado))
        self.assertIn("todavía no está disponible", texto_reporte(resultado))
