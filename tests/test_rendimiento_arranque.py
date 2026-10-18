"""Regresiones de capacidad de respuesta, sin depender de tiempos del equipo."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
import random
from threading import Event, get_ident
from types import SimpleNamespace
from unittest.mock import Mock, patch

from datos.almacen import AlmacenLocal
from modelo.eventos import ColaEventos
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import ServidorFalso
from vista.grafica import VistaGrafica
from vista.sonidos import Sonidos, _NOTAS
from vista.tarea import ejecutar_tarea


class TestTareaNoBloqueante(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        def limpiar():
            try:
                self.root.destroy()
            except tk.TclError:
                pass
        self.addCleanup(limpiar)
        self.vista = SimpleNamespace(root=self.root, _cerrada=False)

    def test_ventana_procesa_eventos_y_descarta_comandos_durante_carga(self):
        liberar = Event()
        principal = get_ident()
        eventos = []
        vista = self.vista
        vista._cola, vista._en_menu, vista._en_replay = [], False, False

        def evento():
            eventos.append(get_ident())
            VistaGrafica._enviar(vista, "mover E")
            liberar.set()

        def trabajo():
            if not liberar.wait(2):
                raise AssertionError("Tk no proceso el evento durante la carga")
            return get_ident()

        self.root.after(10, evento)
        self.assertNotEqual(ejecutar_tarea(vista, trabajo), principal)
        self.assertEqual(eventos, [principal])
        self.assertEqual(vista._cola, [])
        self.assertFalse(vista._ocupada)

    def test_error_se_propaga_y_restaura_cursor(self):
        def fallar():
            raise ValueError("respuesta invalida")
        with self.assertRaisesRegex(ValueError, "respuesta invalida"):
            ejecutar_tarea(self.vista, fallar)
        self.assertFalse(self.vista._ocupada)
        self.assertEqual(self.root.cget("cursor"), "")

    def test_cierre_no_deja_trabajador_usando_sesion(self):
        liberar, terminado = Event(), Event()
        def trabajo():
            liberar.wait(2)
            terminado.set()
            return 42
        def cerrar():
            self.vista._cerrada = True
            liberar.set()
            self.root.destroy()
        self.root.after(10, cerrar)
        self.assertEqual(ejecutar_tarea(self.vista, trabajo), 42)
        self.assertTrue(terminado.is_set())


class TestAudioPreparado(unittest.TestCase):
    def test_inicio_no_sintetiza_audio_al_abrir_ventana(self):
        reproductor = SimpleNamespace(PlaySound=Mock(), SND_FILENAME=1, SND_ASYNC=2, SND_NODEFAULT=4)
        sonido = Sonidos(reproductor)
        self.addCleanup(sonido.cerrar)
        sonido.habilitar(True)
        with patch("vista.sonidos.math.sin", side_effect=AssertionError("Sintetizo en el arranque")):
            sonido.reproducir("inicio")
        reproductor.PlaySound.assert_called_once()

    def test_wav_preparado_conserva_el_sonido_original_y_hay_respaldo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            preparada, generada = Path(carpeta)/"preparada.wav", Path(carpeta)/"generada.wav"
            Sonidos._crear_efecto(preparada, _NOTAS["inicio"], "inicio")
            with patch.object(Path, "is_file", return_value=False):
                Sonidos._crear_efecto(generada, _NOTAS["inicio"], "inicio")
            self.assertEqual(preparada.read_bytes(), generada.read_bytes())


class TestPrecargaEscalable(unittest.TestCase):
    def test_consulta_residente_no_reconstruye_referencias_activas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = ServidorFalso()
            catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta))
            ficha = catalogo.retener(["obj_0"])[0]
            referencias = catalogo._referencias_actuales()
            with patch.object(catalogo, "fijar_referencias", side_effect=AssertionError("Reconstruyo referencias")):
                self.assertEqual(catalogo.obtener_fichas(["obj_0", "obj_0"]), [ficha, ficha])
            self.assertEqual(catalogo._referencias_actuales(), referencias)

    def test_todo_cargado_no_recorre_grafo_y_arranque_caliente_no_reescribe_paginas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            almacen = AlmacenLocal(carpeta)
            for vuelta in range(2):
                cliente = ServidorFalso(salas=137)
                gestor = GestorPrecarga(cliente, GestorCatalogo(cliente, CacheCatalogoOrdenado(25), almacen))
                try:
                    with patch.object(almacen, "guardar_pagina", wraps=almacen.guardar_pagina) as guardar:
                        gestor.preparar_cripta("id-inedito")
                        self.assertEqual(guardar.call_count, 3 if vuelta == 0 else 0)
                    gestor.cargar_contenido([s.id for s in gestor.salas])
                    with patch.object(gestor, "_contenido", side_effect=AssertionError("Recorrio el grafo")):
                        self.assertEqual(gestor._candidatas(100), [])
                finally:
                    gestor.cerrar()

    def test_indice_admite_paginas_desordenadas(self):
        with tempfile.TemporaryDirectory() as carpeta:
            cliente = ServidorFalso(salas=137)
            original = cliente.obtener_esqueleto
            def invertido(*args):
                datos = original(*args)
                datos["salas"].reverse()
                return datos
            cliente.obtener_esqueleto = invertido
            gestor = GestorPrecarga(cliente, GestorCatalogo(cliente, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta)))
            self.addCleanup(gestor.cerrar)
            gestor.preparar_cripta("cripta-otra")
            for sala in gestor.salas:
                self.assertIs(gestor._sala(sala.id), sala)


class TestHeapEscalable(unittest.TestCase):
    def test_empates_y_cancelaciones_conservan_orden_en_2000_eventos(self):
        cola, azar = ColaEventos(), random.Random(42)
        esperados = []
        for i in range(2000):
            evento = cola.insertar(azar.randrange(100), "prueba", i)
            if i % 7 == 0:
                cola.cancelar(evento)
            else:
                esperados.append((evento.tiempo, evento.secuencia, i))
        reales = []
        while (evento := cola.extraer_minimo()) is not None:
            reales.append((evento.tiempo, evento.secuencia, evento.referencia))
        self.assertEqual(reales, sorted(esperados))
