import io
import unittest
import tkinter as tk
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from controlador.partida_historica import integrar_historia
from datos.guardado_binario import guardar_estado
from tests.datos_terreno_cazador import motor_terreno
from tests.datos_integracion_d import ProductorPrueba
from vista.consola import VistaConsola
from vista.grafica import VistaGrafica
from tkinter.scrolledtext import ScrolledText


class ProductorViaje(ProductorPrueba):
    def mapa_conocido(self):
        return ("Sala 1: explorada", "Sala 2: avistada")

    def viajar_hasta(self, destino, mover):
        if destino != 2:
            return "Destino desconocido."
        if not mover("E"):
            return "Movimiento rechazado."
        return "Viaje detenido: enemigos presentes."


class ComandosIntegracionTest(unittest.TestCase):
    def test_fr005_fr018_fr019_historia_mapa_viaje_y_log(self):
        with TemporaryDirectory() as tmp:
            partida = integrar_historia(ProductorViaje(), 2)
            vista = Mock()
            control = ControladorJuego(partida, vista, str(Path(tmp) / "partida.log"))
            control.bitacora_replay.iniciar(partida.meta)
            control.procesar_comando("mapa")
            vista.mostrar_info.assert_called_once_with("Sala 1: explorada\nSala 2: avistada")
            control.procesar_comando("ir a 2")
            vista.mostrar_info.assert_called_with("Viaje detenido: enemigos presentes.")
            antes = control.bitacora_replay.ruta.read_text(encoding="utf-8")
            self.assertIn('"tipo": "comentario"', antes)
            _, acciones = control.bitacora_replay.leer()
            self.assertEqual([(a.accion, a.argumento) for a in acciones], [("mover", "E")])
            estado = partida.exportar_estado()
            control.procesar_comando("historia #1")
            self.assertIn("Entrada", vista.mostrar_info.call_args.args[0])
            control.procesar_comando("historia 250")
            self.assertIn("cazador", vista.mostrar_info.call_args.args[0])
            control.procesar_comando("historia #0")
            control.procesar_comando("historia 251")
            control.procesar_comando("historia 1 extra")
            self.assertEqual(vista.mostrar_error.call_count, 3)
            self.assertEqual(partida.exportar_estado(), estado)
            self.assertEqual(control.bitacora_replay.ruta.read_text(encoding="utf-8"), antes)

    def test_fr011_fr012_guardar_y_cargar_desde_comandos_de_partida(self):
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp)
            productor = ProductorViaje()
            partida = integrar_historia(productor, 7)
            vista = Mock()
            control = ControladorJuego(partida, vista, str(ruta / "partida.log"), partida_p2=True)
            control.bitacora_replay.iniciar(partida.meta)
            control.procesar_comando("mover E")
            control.procesar_comando(f'guardar "{ruta / "con historia.bin"}"')
            guardado = partida.exportar_estado()
            control.procesar_comando("esperar")
            control.procesar_comando(f'cargar "{ruta / "con historia.bin"}"')
            self.assertEqual(partida.exportar_estado(), guardado)
            guardar_estado(productor.exportar_estado(), ruta / "viejo.bin")
            control.procesar_comando(f'cargar "{ruta / "viejo.bin"}"')
            self.assertIn("Parte I", vista.mostrar_error.call_args.args[0])
            self.assertEqual(partida.exportar_estado(), guardado)
            self.assertEqual([a.accion for a in control.bitacora_replay.leer()[1]],
                             ["mover", "esperar", "cargar"])

    def test_fr004_fr018_gui_encola_los_tres_comandos_y_muestra_informe(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(vista.cerrar)
        vista.root.withdraw()
        botones = [boton for marco in vista.root.winfo_children()
                   for boton in marco.winfo_children() if isinstance(boton, tk.ttk.Button)]
        with patch("vista.grafica.simpledialog.askstring", side_effect=["#1", "2"]):
            for etiqueta in ("Historia", "Mapa", "Viajar"):
                next(b for b in botones if b.cget("text") == etiqueta).invoke()
        self.assertEqual(vista._cola, ["historia #1", "mapa", "ir a 2"])
        contenido = []

        def cerrar_informe():
            ventana = next(w for w in vista.root.winfo_children() if isinstance(w, tk.Toplevel))
            caja = next(w for w in ventana.winfo_children()
                        for hijo in w.winfo_children() if isinstance(hijo, ScrolledText))
            texto = next(w for w in caja.winfo_children() if isinstance(w, ScrolledText))
            contenido.append(texto.get("1.0", "end-1c"))
            ventana.destroy()

        vista.root.after(60, cerrar_informe)
        limite = vista.root.after(2000, vista.cerrar)
        vista.mostrar_informe("Historia", "Línea 1\nLínea 2")
        if not vista._cerrada:
            vista.root.after_cancel(limite)
        self.assertEqual(contenido, ["Línea 1\nLínea 2"])

    def test_fr018_presenta_costo_real_sin_modificar_motor(self):
        with motor_terreno(250) as motor:
            mensajes = []
            control = ControladorJuego(motor, VistaConsola(salida=mensajes.append))
            control._mostrar_estado()
            self.assertTrue(any("costo 250" in linea for linea in mensajes))
            self.assertEqual(motor.reloj, 0)
