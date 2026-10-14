import json
import struct
import tempfile
import tkinter as tk
import unittest
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from datos.almacen import AlmacenLocal
from datos.bitacora_replay import BitacoraReplay, ReplayIncompatible
from datos.guardado_binario import guardar_estado, cargar_estado, FormatoIncompatible
from modelo.coleccion_enemigos import EnemigosSala
from modelo.tipos import InstanciaEnemigo
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from tests import test_regresiones_juego as base
from tests.datos_prueba import ServidorFalso
from vista.grafica import VistaGrafica


class TestCumplimientoIntegrado(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor

    def test_cursor_actual_no_se_busca_desde_la_cabeza(self):
        for posicion in (0, 4, 8):
            d = base.TestRegresionesJuego()
            d.setUp()
            for i in range(9):
                d._inventario("daga", str(i))
            inv = d.motor.jugador.inventario
            inv.seleccionar(str(posicion))
            with patch.object(inv, "cabeza", object()):
                self.assertTrue(d.motor._posicionar_cursor_en(str(posicion)))
            self.assertTrue(d.motor.ejecutar("soltar", str(posicion)).ok)
            self.assertEqual(inv.tamaño, 8)
            self.assertEqual(d.motor.objetos_en_suelo[1][0].id_instancia, str(posicion))

    def test_seleccionar_es_gratis_y_no_se_registra(self):
        self.datos._inventario("daga")
        self.datos._inventario("coraza")
        c = ControladorJuego(self.motor, Mock())
        c.bitacora_replay = Mock()
        antes = deepcopy(self.motor.exportar_estado())
        c.procesar_comando("seleccionar coraza")
        self.assertEqual(self.motor.jugador.inventario.cursor.objeto.id_instancia, "coraza")
        self.assertEqual(self.motor.exportar_estado(), antes)
        c.bitacora_replay.registrar_accion.assert_not_called()

    def test_gui_sincroniza_seleccion_antes_de_soltar(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        try:
            vista.root.withdraw()
            self.datos._inventario("daga")
            self.datos._inventario("coraza")
            vista.mostrar_inventario(self.motor.inventario_vista())
            vista.lista.selection_clear(0, "end")
            vista.lista.selection_set(1)
            vista._seleccionar_inventario()
            c = ControladorJuego(self.motor, vista)
            c.bitacora_replay = Mock()
            c.procesar_comando(vista._cola.pop(0))
            self.assertEqual(self.motor.reloj, 0)
            self.assertEqual(self.motor.jugador.inventario.cursor.objeto.id_instancia, "coraza")
            vista._accion_inventario("soltar")
            c.procesar_comando(vista._cola.pop(0))
            self.assertEqual(self.motor.objetos_en_suelo[1][0].id_instancia, "coraza")
        finally:
            vista.cerrar()

    def test_traslados_no_recorrer_listas_y_retroceso_restaura_orden(self):
        self.motor.salas[1].salidas["E"]["cerrada"] = False
        class SinRecorridos(EnemigosSala):
            def __contains__(self, enemigo):
                raise AssertionError("No buscar en la lista.")

            def remove(self, enemigo):
                raise AssertionError("No eliminar mediante busqueda/desplazamiento.")

            def __iter__(self):
                raise AssertionError("No recorrer la lista al trasladar.")

        for cantidad in (16, 256, 1024):
            origen = SinRecorridos()
            actores = [InstanciaEnemigo(vida=20, vida_max=20, ataque=2, defensa=1,
                        velocidad=100, tiempo_siguiente=0, id_instancia=str(i),
                        tipo_catalogo="enemigo", comportamiento="rastreador", sala_actual=1)
                       for i in range(cantidad)]
            origen.extend(actores)
            destino = EnemigosSala()
            self.motor.enemigos_por_sala[1] = origen
            self.motor.enemigos_por_sala[2] = destino
            self.motor.historial.iniciar_turno(self.motor.reloj)
            for actor in reversed(actores):
                self.motor._ejecutar_turno_enemigo(actor, lambda *args: ("mover", "E"))
            self.assertEqual(len(origen), 0)
            self.assertEqual(len(destino), cantidad)
            self.motor.historial.descartar_turno()
            self.assertEqual(len(destino), 0)
            for i, actor in enumerate(actores):
                self.assertIs(origen[i], actor)
                self.assertEqual(actor.indice_sala, i)
                self.assertEqual(actor.sala_actual, 1)

    def test_extraccion_intermedia_se_deshace_en_la_misma_posicion(self):
        actores = [SimpleNamespace(indice_sala=-1) for _ in range(5)]
        sala = EnemigosSala(actores)
        indice = sala.extraer(actores[2])
        self.assertIs(sala[2], actores[4])
        sala.restaurar(actores[2], indice)
        for i, actor in enumerate(actores):
            self.assertIs(sala[i], actor)
            self.assertEqual(actor.indice_sala, i)

    def test_puerta_inicialmente_abierta_no_concede_victoria(self):
        for con_llave in (False, True):
            d = base.TestRegresionesJuego()
            d.setUp()
            d.motor.salas[1].salidas["E"]["cerrada"] = False
            if con_llave:
                d._inventario("llave")
            self.assertTrue(d.motor.estado_vista().salidas[0].apertura_pendiente)
            self.assertTrue(d.motor.ejecutar("mover", "E").ok)
            self.assertFalse(d.motor.terminado)

    def test_apertura_se_guarda_y_permite_ganar_sin_consumir_llave(self):
        self.datos._inventario("llave")
        self.assertTrue(self.motor.ejecutar("abrir", "E").ok)
        self.assertEqual(self.motor.jugador.inventario.contar("llave"), 1)
        self.assertTrue(self.motor.ejecutar("soltar", "llave").ok)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "partida.bin")
            guardar_estado(self.motor.exportar_estado(), ruta)
            estado = cargar_estado(ruta)
            self.assertTrue(estado.salas[0].puertas[0].abierta_con_llave)
            self.motor.restaurar_estado(estado)
            self.assertTrue(self.motor.ejecutar("mover", "E").ok)
            self.assertEqual(self.motor.resultado, "victoria")

    def test_deshacer_apertura_retira_evidencia_y_cierre_automatico_se_conserva(self):
        self.datos._inventario("llave")
        self.datos._inventario("pergamino")
        self.motor.salas[1].salidas["E"]["cierre_automatico"] = 100
        self.assertTrue(self.motor.ejecutar("abrir", "E").ok)
        self.assertTrue(self.motor.ejecutar("retroceso").ok)
        self.assertEqual(self.motor.puertas_abiertas_con_llave, [])
        self.assertTrue(self.motor.salas[1].salidas["E"]["cerrada"])
        self.assertTrue(self.motor.ejecutar("abrir", "E").ok)
        self.assertTrue(self.motor.ejecutar("esperar").ok)
        self.assertTrue(self.motor.salas[1].salidas["E"]["cerrada"])
        self.assertFalse(self.motor.ejecutar("mover", "E").ok)

    def test_formato_v2_y_carga_de_replay_antigua_se_rechazan(self):
        estado = self.motor.exportar_estado()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "antiguo.bin"
            guardar_estado(estado, str(ruta))
            with ruta.open("r+b") as archivo:
                archivo.seek(4)
                archivo.write(struct.pack("<H", 2))
            with self.assertRaises(FormatoIncompatible):
                cargar_estado(str(ruta))
            log = BitacoraReplay(Path(carpeta) / "antiguo.log")
            log.iniciar(estado.meta)
            antiguo = estado.a_dict()
            for sala in antiguo["salas"]:
                for puerta in sala["puertas"]:
                    puerta.pop("abierta_con_llave")
            with log.ruta.open("a", encoding="utf-8") as archivo:
                archivo.write(json.dumps(dict(tipo="cargar", estado=antiguo)) + "\n")
            with self.assertRaises(ReplayIncompatible):
                log.leer()

    def test_modelo_carga_mediante_transaccion_sin_conocer_cache(self):
        usos = []
        fuente = self.motor.gestor_precarga

        @contextmanager
        def transaccion():
            usos.append("abrir")
            yield fuente
            usos.append("confirmar")

        fuente.transaccion_catalogo = transaccion
        estado = self.motor.exportar_estado()
        self.motor.restaurar_estado(estado)
        self.assertEqual(usos, ["abrir", "confirmar"])
        self.assertEqual(self.motor.exportar_estado(), estado)

    def test_transaccion_del_adaptador_confirma_o_descarta_cache(self):
        with tempfile.TemporaryDirectory() as carpeta:
            catalogo = GestorCatalogo(ServidorFalso(), CacheCatalogoOrdenado(3), AlmacenLocal(carpeta))
            catalogo.fijar_referencias(["a"])
            cache = catalogo.cache
            antes = [(n.clave, n.referencias) for n in cache.arreglo]
            with self.assertRaises(ValueError):
                with catalogo.transaccion() as preparado:
                    preparado.fijar_referencias(["b"])
                    raise ValueError("carga rechazada")
            self.assertEqual([(n.clave, n.referencias) for n in cache.arreglo], antes)
            with catalogo.transaccion() as preparado:
                preparado.fijar_referencias(["b"])
            self.assertIs(catalogo.cache, cache)
            self.assertEqual(catalogo._referencias_actuales(), ["b"])
