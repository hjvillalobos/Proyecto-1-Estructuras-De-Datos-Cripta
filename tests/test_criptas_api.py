"""Seleccion de criptas y comprobacion opcional del paquete oficial descargado."""
import io
import os
import shutil
import tempfile
import tkinter as tk
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

import main
from datos.almacen import AlmacenLocal
from datos.bitacora_replay import BitacoraReplay, aplicar_accion_replay
from datos.guardado_binario import cargar_estado, guardar_estado
from datos.offline import ClienteOffline
from modelo.juego import crear_juego, _incorporar_sala_preparada
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from vista.grafica import VistaGrafica


CRIPTAS = [
    {"id": "cripta-01", "nombre": "Osario menor", "salas": 6, "dificultad": 1},
    {"id": "cripta-02", "nombre": "Catacumbas menores", "salas": 20, "dificultad": 2},
    {"id": "cripta-03", "nombre": "Catacumbas medias", "salas": 40, "dificultad": 3},
    {"id": "cripta-04", "nombre": "Catacumbas profundas", "salas": 50, "dificultad": 4},
]


class TestSeleccionCriptas(unittest.TestCase):
    def test_jugar_usa_identificador_elegido_sin_alterar_reglas(self):
        for cripta in CRIPTAS:
            with self.subTest(cripta=cripta["id"]), tempfile.TemporaryDirectory() as carpeta:
                vista = Mock(spec=VistaGrafica)
                vista.mostrar_menu.return_value = ("jugar", None)
                vista.elegir_cripta.return_value = cripta["id"]
                sesion = Mock()
                sesion.cliente.listar_criptas.return_value = {"criptas": CRIPTAS}
                juego = Mock(resultado=None)
                with patch("main.SesionDatos", return_value=sesion), \
                        patch("vista.grafica.VistaGrafica", return_value=vista), \
                        patch("modelo.juego.crear_juego", return_value=juego) as crear, \
                        patch("controlador.controlador.ControladorJuego"), \
                        redirect_stdout(io.StringIO()):
                    self.assertEqual(main.main(["--gui", "--semilla", "20", "--datos-dir", carpeta]), 0)
                self.assertEqual(crear.call_args.args, (sesion.precarga, cripta["id"], 20))
                vista.elegir_cripta.assert_called_once_with(CRIPTAS)

    def test_descarga_todas_renueva_sesion_entre_criptas(self):
        sesion = Mock()
        sesion.cliente.listar_criptas.return_value = {"criptas": CRIPTAS}
        sesion.precarga.preparar_cripta.return_value.salas = [Mock(id=1)]
        with patch("main.SesionDatos", return_value=sesion), redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(["--descargar-todo"]), 0)
        self.assertEqual(sesion.renovar.call_count, 3)
        self.assertEqual([llamada.args[0] for llamada in sesion.precarga.preparar_cripta.call_args_list],
                         [cripta["id"] for cripta in CRIPTAS])

    def test_selector_real_permite_las_cuatro_opciones_y_cancelar(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.withdraw()
            for indice, cripta in enumerate(CRIPTAS):
                def elegir(indice=indice):
                    vista._enviar("mover E")
                    self.assertEqual(vista._cola, [])
                    dialogo = next(h for h in vista.root.winfo_children() if isinstance(h, tk.Toplevel))
                    lista = next(h for h in dialogo.winfo_children() if isinstance(h, tk.Listbox))
                    lista.selection_clear(0, "end")
                    lista.selection_set(indice)
                    lista.event_generate("<Return>")
                    # Invocar el callback tambien en ventanas sin foco del SO.
                    if dialogo.winfo_exists():
                        controles = next(h for h in dialogo.winfo_children() if isinstance(h, tk.Frame))
                        controles.winfo_children()[1].invoke()
                vista.root.after(100, elegir)
                self.assertEqual(vista.elegir_cripta(CRIPTAS), cripta["id"])
                self.assertEqual(vista._cola, [])
            vista.root.after(100, lambda: next(h for h in vista.root.winfo_children()
                                             if isinstance(h, tk.Toplevel)).destroy())
            self.assertIsNone(vista.elegir_cripta(CRIPTAS))
        finally:
            vista.cerrar()


@unittest.skipUnless(os.environ.get("CRIPTA_PAQUETE_API"), "Paquete oficial opcional no indicado")
class TestPaqueteOficial(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = str(Path(temporal.name) / "paquete")
        shutil.copytree(os.environ["CRIPTA_PAQUETE_API"], self.carpeta)

    def test_partidas_hasta_victoria_y_replay_en_las_cuatro_criptas(self):
        carpeta = self.carpeta
        for cripta in CRIPTAS:
            with self.subTest(cripta=cripta["id"]), tempfile.TemporaryDirectory() as salida:
                cliente = ClienteOffline(carpeta)
                precarga = GestorPrecarga(cliente, GestorCatalogo(
                    cliente, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta)))
                semilla = 1916 if cripta["id"] == "cripta-01" else 20
                motor = crear_juego(precarga, cripta["id"], semilla)
                bitacora = BitacoraReplay(Path(salida) / "partida.log")
                bitacora.iniciar(motor.meta)

                def actuar(accion, argumento=None):
                    resultado = motor.ejecutar(accion, argumento)
                    self.assertTrue(resultado.ok, (accion, argumento, resultado.mensaje))
                    bitacora.registrar_accion(accion, argumento)

                def objeto(tipo, suelo=False):
                    objetos = (motor.objetos_en_suelo[motor.jugador.posicion_actual]
                               if suelo else motor.jugador.inventario)
                    return next((o.id_instancia for o in objetos if o.tipo_catalogo == tipo), None)

                def recoger(tipo):
                    instancia = objeto(tipo, suelo=True)
                    if instancia is not None:
                        actuar("recoger", instancia)
                    return instancia

                try:
                    if cripta["id"] == "cripta-01":
                        actuar("mover", "N")
                        actuar("mover", "N")
                        actuar("equipar", recoger("itm_coraza_cuero"))
                        actuar("mover", "N")
                        actuar("usar", recoger("itm_pocion_menor"))
                        recoger("itm_llave_negra")
                        actuar("abrir", "E")
                        actuar("mover", "E")
                    else:
                        for _ in range(100):
                            if motor.terminado:
                                break
                            for tipo in ("itm_daga_oxidada", "itm_coraza_cuero"):
                                instancia = recoger(tipo)
                                if instancia is not None:
                                    actuar("equipar", instancia)
                            for _ in range(100):
                                if motor.terminado:
                                    break
                                enemigos = [e for e in motor.enemigos_por_sala[motor.jugador.posicion_actual]
                                            if e.vida > 0]
                                pocion = objeto("itm_pocion_menor")
                                umbral = 12 if enemigos else motor.jugador.vida_max - 8
                                if motor.jugador.vida <= umbral:
                                    if pocion is None:
                                        pocion = recoger("itm_pocion_menor")
                                    if pocion is not None:
                                        actuar("usar", pocion)
                                        continue
                                if not enemigos:
                                    break
                                actuar("atacar", enemigos[0].id_instancia)
                            if motor.terminado:
                                break
                            while objeto("itm_pocion_menor", suelo=True) is not None:
                                recoger("itm_pocion_menor")
                            recoger("itm_llave_negra")
                            puerta = motor.salas[motor.jugador.posicion_actual].salidas["N"]
                            if puerta.get("cerrada", False):
                                actuar("abrir", "N")
                            actuar("mover", "N")
                    self.assertEqual(motor.resultado, "victoria",
                                     (cripta["id"], motor.jugador.vida, motor.jugador.posicion_actual))
                    estado = motor.exportar_estado()
                    precarga.cerrar()
                    nuevo_cliente = ClienteOffline(carpeta)
                    nuevo = GestorPrecarga(nuevo_cliente, GestorCatalogo(
                        nuevo_cliente, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta)))
                    try:
                        replay = crear_juego(nuevo, cripta["id"], semilla)
                        for accion in bitacora.leer()[1]:
                            self.assertTrue(aplicar_accion_replay(replay, accion).ok)
                        self.assertEqual(replay.exportar_estado(), estado)
                    finally:
                        nuevo.cerrar()
                finally:
                    precarga.cerrar()

    def test_todas_las_salas_iconos_guardado_y_carga(self):
        carpeta = self.carpeta
        cliente = ClienteOffline(carpeta)
        criptas = cliente.listar_criptas()["criptas"]
        self.assertEqual(len(criptas), 4)
        recursos = Path(__file__).resolve().parents[1] / "vista" / "recursos"
        self.assertTrue((recursos / "jugador.png").is_file())
        for cripta in criptas:
            with self.subTest(cripta=cripta["id"]):
                catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta))
                precarga = GestorPrecarga(cliente, catalogo)
                try:
                    motor = crear_juego(precarga, cripta["id"], 20)
                    salas = [sala for sala in motor.salas if sala is not None]
                    self.assertEqual(len(salas), cripta["salas"])
                    precarga.cargar_contenido([sala.id for sala in salas])
                    for sala in salas:
                        preparada = precarga.preparar_entrada(sala.id, [])
                        _incorporar_sala_preparada(motor, preparada)
                        for ficha in preparada.fichas:
                            self.assertTrue((recursos / (ficha.id + ".png")).is_file(), ficha.id)
                    self.assertTrue(all(motor.contenido_cargado[sala.id] for sala in salas))
                    estado = motor.exportar_estado()
                    with tempfile.TemporaryDirectory() as salida:
                        ruta = str(Path(salida) / "partida.bin")
                        guardar_estado(estado, ruta)
                        motor.ejecutar("esperar")
                        motor.restaurar_estado(cargar_estado(ruta))
                    self.assertEqual(motor.exportar_estado(), estado)
                    self.assertEqual(cliente.solicitudes_realizadas, 0)
                finally:
                    precarga.cerrar()
