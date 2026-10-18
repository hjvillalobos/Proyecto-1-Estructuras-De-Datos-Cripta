import struct
import gc
import weakref
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from controlador.replay import ReproductorReplay
from datos.almacen import AlmacenLocal
from datos.bitacora_replay import BitacoraReplay, MetaReplay, AccionReplay, ReplayIncompatible
from datos.guardado_binario import guardar_estado, cargar_estado, ArchivoGuardado, FormatoIncompatible
from datos.puntajes import TablaPuntajes
from modelo.juego import Motor, crear_juego, _incorporar_sala_preparada
from modelo.snapshots import ItemVista, EnemigoVista
from modelo.tipos import Sala, Trampa
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests import test_regresiones_juego as base
from tests.datos_prueba import ServidorFalso, crear_paquete
from vista.grafica import VistaGrafica


class TestCorreccionesEnunciado(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)

    def ruta(self, nombre):
        return str(Path(self.temporal.name) / nombre)

    def controlador(self, tabla=None):
        vista = Mock()
        vista.pedir_texto.return_value = "Ana"
        c = ControladorJuego(self.motor, vista, self.ruta("partida.log"), tabla_puntajes=tabla)
        c.bitacora_replay.iniciar(self.motor.meta)
        return c

    def test_botin_pergamino_sobrevive_dos_retrocesos_sin_duplicarse(self):
        for f in self.datos.fichas:
            if f.id == "enemigo":
                f.atributos["suelta"] = ["pergamino"]
        self.datos._inventario("pergamino", "p1")
        self.datos._inventario("pergamino", "p2")
        enemigo = self.datos._enemigo()
        enemigo.vida = 1
        self.datos._accion("atacar", enemigo.id_instancia)
        botin = self.motor.objetos_en_suelo[1][0]
        self.datos._accion("recoger", botin.id_instancia)
        self.datos._accion("retroceso")
        self.datos._accion("retroceso")
        self.assertEqual(enemigo.vida, 1)
        self.assertEqual(list(self.motor.jugador.inventario), [botin])
        self.datos._accion("atacar", enemigo.id_instancia)
        self.assertEqual(self.motor.objetos_en_suelo[1], [])

    def test_botin_pergamino_en_suelo_no_se_borra_al_retroceder(self):
        self.datos.fichas[-1].atributos["suelta"] = ["pergamino"]
        self.datos._inventario("pergamino", "p1")
        enemigo = self.datos._enemigo()
        enemigo.vida = 1
        self.datos._accion("atacar", enemigo.id_instancia)
        self.datos._accion("retroceso")
        self.assertEqual(len(self.motor.objetos_en_suelo[1]), 1)
        self.datos._accion("atacar", enemigo.id_instancia)
        self.assertEqual(len(self.motor.objetos_en_suelo[1]), 1)

    def test_turnos_descartados_se_liberan_sin_recoleccion_ciclica(self):
        habilitado = gc.isenabled()
        gc.disable()
        try:
            self.datos._accion("esperar")
            primero = weakref.ref(self.motor.historial._turnos[0])
            for _ in range(5):
                self.datos._accion("esperar")
            self.assertIsNone(primero())
            self.assertEqual(self.motor.historial.cantidad_turnos(), 5)
        finally:
            if habilitado:
                gc.enable()
    def test_replay_rechaza_version_distinta_antes_de_actuar(self):
        meta = MetaReplay("prueba", "vieja", "cat1", 42)
        vista = Mock()
        fabrica = Mock(return_value=self.motor)
        with patch("controlador.replay.BitacoraReplay.leer",
                   return_value=(meta, [AccionReplay("esperar")])):
            ReproductorReplay(None, None, vista, fabrica).reproducir("no-leido.log")
        self.assertEqual(self.motor.reloj, 0)
        vista.mostrar_error.assert_called_once()
        self.assertEqual(fabrica.call_args.kwargs,
                         {"version_cripta": "vieja", "version_catalogo": "cat1"})

    def test_replay_recupera_version_historica_local(self):
        almacen = crear_paquete(self.temporal.name, salas=2)
        servidor = ServidorFalso(salas=2, version="v2", version_catalogo="cat2")
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), almacen)
        precarga = GestorPrecarga(servidor, catalogo)
        self.addCleanup(precarga.cerrar)
        meta = MetaReplay("prueba", "v1", "cat1", 42)
        vista = Mock()
        vista.mostrar_replay_paso.return_value = True
        juegos = []
        def fabricar(*args, **kwargs):
            juego = crear_juego(*args, **kwargs)
            juegos.append(juego)
            return juego
        with patch("controlador.replay.BitacoraReplay.leer",
                   return_value=(meta, [AccionReplay("esperar")])):
            ReproductorReplay(servidor, precarga, vista, fabricar).reproducir("no-leido.log")
        vista.mostrar_error.assert_not_called()
        self.assertEqual(juegos[0].meta.cripta_version, "v1")
        self.assertEqual(juegos[0].reloj, 100)
        self.assertEqual(servidor.solicitudes_realizadas, 0)

    def test_replay_rechaza_version_historica_no_disponible(self):
        servidor = ServidorFalso(salas=2, version="v2")
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), AlmacenLocal(self.temporal.name))
        precarga = GestorPrecarga(servidor, catalogo)
        self.addCleanup(precarga.cerrar)
        meta = MetaReplay("prueba", "v1", "cat1", 42)
        vista = Mock()
        with patch("controlador.replay.BitacoraReplay.leer", return_value=(meta, [])):
            ReproductorReplay(servidor, precarga, vista, crear_juego).reproducir("no-leido.log")
        vista.mostrar_error.assert_called_once()
        vista.mostrar_replay_paso.assert_not_called()

    def test_carga_incompatible_no_modifica_la_partida(self):
        antes = self.motor.exportar_estado()
        for campo in ("cripta_id", "cripta_version", "catalogo_version"):
            with self.subTest(campo=campo):
                invalido = deepcopy(antes)
                setattr(invalido.meta, campo, "incompatible")
                with self.assertRaisesRegex(ValueError, "incompatible"):
                    self.motor.restaurar_estado(invalido)
                self.assertEqual(self.motor.exportar_estado(), antes)

    def test_carga_con_sala_inexistente_no_modifica_la_partida(self):
        antes = self.motor.exportar_estado()
        invalido = deepcopy(antes)
        invalido.jugador.sala_id = 999
        with self.assertRaises(ValueError):
            self.motor.restaurar_estado(invalido)
        self.assertEqual(self.motor.exportar_estado(), antes)

    def test_replay_reproduce_carga_aunque_desaparezca_el_archivo_binario(self):
        c = self.controlador()
        guardado = self.ruta("base.bin")
        guardar_estado(self.motor.exportar_estado(), guardado)
        c._accion_modelo("esperar")
        c._cargar(guardado)
        c._accion_modelo("esperar")
        esperado = self.motor.exportar_estado()
        Path(guardado).unlink()
        otra = base.TestRegresionesJuego()
        otra.setUp()
        vista = Mock()
        vista.mostrar_replay_paso.return_value = True
        ReproductorReplay(None, None, vista, lambda *a, **k: otra.motor).reproducir(self.ruta("partida.log"))
        vista.mostrar_error.assert_not_called()
        self.assertEqual(otra.motor.exportar_estado(), esperado)
        self.assertEqual(otra.motor.reloj, 100)

    def test_carga_rechazada_no_se_anexa_al_log(self):
        c = self.controlador()
        estado = deepcopy(self.motor.exportar_estado())
        estado.meta.cripta_id = "otra"
        with patch("controlador.controlador.cargar_estado", return_value=estado):
            c._cargar("no-leido.bin")
        self.assertEqual(c.bitacora_replay.leer()[1], [])

    def test_marca_antigua_de_carga_sin_estado_se_rechaza(self):
        c = self.controlador()
        c.bitacora_replay.registrar_carga()
        with self.assertRaises(ReplayIncompatible):
            c.bitacora_replay.leer()

    def test_guardado_de_300_salas_y_acceso_directo(self):
        motor = Motor(self.motor.jugador, [Sala(i, str(i), {}) for i in range(1, 301)], 42)
        motor.meta = self.motor.meta
        motor.contenido_cargado = [False] + [True] * 300
        estado = motor.exportar_estado()
        ruta = self.ruta("grande.bin")
        guardar_estado(estado, ruta)
        self.assertEqual(cargar_estado(ruta), estado)
        with ArchivoGuardado(ruta) as archivo:
            self.assertEqual(archivo.leer_sala(300).sala_id, 300)

    def test_formato_binario_anterior_se_rechaza(self):
        ruta = self.ruta("viejo.bin")
        guardar_estado(self.motor.exportar_estado(), ruta)
        with open(ruta, "r+b") as archivo:
            archivo.seek(4)
            archivo.write(struct.pack("<H", 1))
        with self.assertRaises(FormatoIncompatible):
            cargar_estado(ruta)

    def test_referencias_incluyen_trampas_actuales_y_no_objetos_remotos(self):
        self.datos._suelo("daga", sala=1)
        self.datos._suelo("espada", sala=2)
        self.motor.salas[1].trampas = [Trampa("t1", "trampa"), Trampa("t2", "otra-trampa")]
        self.assertEqual(self.motor._ids_en_uso(), ["daga", "trampa", "otra-trampa"])
        self.assertEqual(self.motor._ids_en_uso(2), ["espada"])

    def test_exploracion_y_revisita_con_cache_de_una_ficha(self):
        class ServidorObjetos(ServidorFalso):
            def obtener_contenido_salas(self, cripta_id, salas_ids):
                respuesta = super().obtener_contenido_salas(cripta_id, salas_ids)
                for sala in respuesta["contenido"]:
                    sala["enemigos"] = []
                return respuesta
        servidor = ServidorObjetos(salas=5)
        cache = CacheCatalogoOrdenado(1)
        catalogo = GestorCatalogo(servidor, cache, AlmacenLocal(self.temporal.name))
        precarga = GestorPrecarga(servidor, catalogo)
        self.addCleanup(precarga.cerrar)
        motor = crear_juego(precarga, "prueba", 42)
        motor.sala_salida = None
        for direccion in ("E", "E", "E", "O", "O", "O"):
            self.assertTrue(motor.ejecutar("mover", direccion).ok)
            self.assertEqual(cache.tamaño_actual, 1)
            self.assertEqual([n.clave for n in cache.arreglo if n.referencias], motor._ids_en_uso())

    def test_pociones_superpuestas_restauran_velocidad_base(self):
        self.datos._inventario("velocidad", "v1")
        self.datos._inventario("velocidad", "v2")
        self.datos._accion("usar", "v1")
        self.datos._accion("usar", "v2")
        self.assertEqual(self.motor.jugador.velocidad, 200)
        self.assertEqual(sum(e.tipo == "restaurar_velocidad" for e in self.motor.cola.pendientes()), 1)
        self.motor.restaurar_estado(self.motor.exportar_estado())
        for _ in range(8):
            self.datos._accion("esperar")
        self.assertEqual(self.motor.jugador.velocidad, 100)
        self.assertIsNone(self.motor.jugador.evento_velocidad)

    def test_retroceder_segunda_pocion_recupera_vencimiento_original(self):
        self.datos._inventario("pergamino")
        self.datos._inventario("velocidad", "v1")
        self.datos._inventario("velocidad", "v2")
        self.datos._accion("usar", "v1")
        evento = self.motor.jugador.evento_velocidad
        self.datos._accion("usar", "v2")
        self.datos._accion("retroceso")
        self.assertIs(self.motor.jugador.evento_velocidad, evento)
        self.assertFalse(evento.cancelado)
        self.assertEqual(evento.tiempo, 300)
        for _ in range(8):
            self.datos._accion("esperar")
        self.assertEqual(self.motor.jugador.velocidad, 100)

    def test_dos_trampas_dano_guardado_rearme_y_retroceso(self):
        m = self.motor
        self.datos._inventario("pergamino")
        m.contenido_cargado[2] = False
        m.sala_salida = None
        m.salas[1].salidas["E"]["cerrada"] = False
        contenido = {"enemigos": [], "objetos": [], "trampas": [
            {"instancia": "t1", "tipo": "trampa"}, {"instancia": "t2", "tipo": "trampa"}]}
        _incorporar_sala_preparada(m, SimpleNamespace(sala=m.salas[2], contenido=contenido,
                                                    fichas=self.datos.fichas))
        self.datos._accion("mover", "E")
        self.assertEqual(m.jugador.vida, 22)
        estado = m.exportar_estado()
        self.assertEqual(sum(e.tipo == "rearmar_trampa" for e in estado.eventos), 2)
        self.datos._accion("retroceso")
        self.assertEqual(m.jugador.vida, 30)
        self.assertTrue(all(t.armada for t in m.salas[2].trampas))
        ruta = self.ruta("trampas.bin")
        guardar_estado(estado, ruta)
        m.restaurar_estado(cargar_estado(ruta))
        self.assertEqual(len(m.salas[2].trampas), 2)
        for _ in range(3):
            self.datos._accion("esperar")
        self.assertTrue(all(t.armada for t in m.salas[2].trampas))

    def test_victoria_y_derrota_registran_un_puntaje_por_sesion(self):
        for resultado in ("victoria", "derrota"):
            with self.subTest(resultado=resultado):
                tabla = TablaPuntajes(self.ruta(resultado + ".jsonl"))
                c = self.controlador(tabla)
                self.motor.terminado = True
                self.motor.resultado = resultado
                c.iniciar()
                c._registrar_puntaje()
                registros = tabla.cargar()
                self.assertEqual(len(registros), 1)
                self.assertEqual(registros[0].resultado, resultado)
                self.assertEqual(registros[0].nombre, "Ana")

    def test_abandono_no_registra_partida_terminada(self):
        tabla = TablaPuntajes(self.ruta("puntajes.jsonl"))
        c = self.controlador(tabla)
        c.vista.pedir_comando.return_value = "salir"
        c.iniciar()
        self.assertEqual(tabla.cargar(), [])

    def test_paginacion_permite_seleccionar_todos_sin_comandos_de_tiempo(self):
        v = VistaGrafica.__new__(VistaGrafica)
        v.canvas = Mock()
        v._cola, v._cerrada, v._en_replay = [], False, False
        estado = SimpleNamespace(sala_id=1, sala_nombre="Sala", salidas=[], vida=30, vida_max=30,
            enemigos=[EnemigoVista(f"e{i}", "Enemigo", 10, 10) for i in range(19)],
            objetos_suelo=[ItemVista(f"o{i}", "Objeto", "llave", 0, 0) for i in range(19)])
        elegidos = []
        for pagina in range(3):
            v.canvas.reset_mock()
            if pagina == 0:
                v._dibujar_sala(estado)
            else:
                v._cambiar_pagina("enemigos", 1)
                v.canvas.reset_mock()
                v._cambiar_pagina("objetos", 1)
            self.assertEqual(v._cola, [])
            for llamada in v.canvas.tag_bind.call_args_list:
                etiqueta, evento, callback = llamada.args
                if evento == "<Button-1>" and etiqueta.startswith(("enemigo_", "objeto_")):
                    callback(None)
            elegidos.extend(v._cola)
            v._cola.clear()
        self.assertEqual(len(elegidos), 38)
        for i in range(19):
            self.assertIn(f"atacar e{i}", elegidos)
            self.assertIn(f"recoger o{i}", elegidos)
        estado.objetos_suelo = estado.objetos_suelo[:1]
        v._dibujar_sala(estado)
        self.assertEqual(v._pagina_objetos, 0)
        otro = deepcopy(estado)
        otro.sala_id = 2
        v._dibujar_sala(otro)
        self.assertEqual(v._pagina_enemigos, 0)


if __name__ == "__main__":
    unittest.main()
