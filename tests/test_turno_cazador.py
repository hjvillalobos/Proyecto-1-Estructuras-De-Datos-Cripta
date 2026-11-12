"""T025: datos offline y turnos reales del cazador (FR-007–FR-012)."""

from contextlib import contextmanager
from random import Random
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from datos.offline import ClienteOffline
from modelo.juego import crear_juego
from modelo.tipos import ObjetoInstancia
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import crear_paquete


RANGO_AUSENTE = object()


@contextmanager
def partida_cazador(rango, *, velocidad_jugador=350, costo_segunda_conexion=None):
    with TemporaryDirectory(prefix="cripta-t025-") as carpeta:
        almacen = crear_paquete(carpeta, salas=3)
        generales = almacen.leer_generales("prueba", "v1")
        generales["jugador"]["velocidad"] = velocidad_jugador
        almacen.guardar_generales(generales)
        pagina = almacen.leer_pagina("prueba", "v1", 1)
        pagina["salas"][0]["salidas"]["E"]["costo"] = 250
        pagina["salas"][1]["salidas"]["O"]["costo"] = 250
        if costo_segunda_conexion is not None:
            pagina["salas"][1]["salidas"]["E"]["costo"] = costo_segunda_conexion
            pagina["salas"][2]["salidas"]["O"]["costo"] = costo_segunda_conexion
        almacen.guardar_pagina("prueba", "v1", pagina)
        ficha = almacen.leer_ficha("cat1", "enemigo")
        ficha["comportamiento"] = "cazador"
        if rango is not RANGO_AUSENTE:
            ficha["rango"] = rango
        almacen.guardar_ficha("cat1", ficha)
        almacen.guardar_ficha("cat1", {"id": "pergamino", "clase": "pergamino_retroceso",
                                       "nombre": "Pergamino"})
        for sala in (100, 101, 102):
            contenido = almacen.leer_contenido("prueba", "v1", sala)
            contenido["objetos"] = []
            if sala != 100:
                contenido["enemigos"] = []
            almacen.guardar_contenido("prueba", "v1", contenido)

        cliente = ClienteOffline(carpeta, "v1")
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(), cliente.almacen)
        precarga = GestorPrecarga(cliente, catalogo)
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP durante T025")) as http:
            try:
                motor = crear_juego(precarga, "prueba", semilla=42,
                                    version_cripta="v1", version_catalogo="cat1")
                yield motor, motor.enemigos_por_sala[100][0], catalogo
            finally:
                try:
                    precarga.cerrar()
                finally:
                    cliente.cerrar()
            http.assert_not_called()
            assert cliente.solicitudes_realizadas == 0


class TestDatosYRegresionesT025(unittest.TestCase):
    def test_rango_versionado_residente_distingue_null_y_ausencia(self):
        for rango in (350, 349, None, RANGO_AUSENTE):
            with self.subTest(rango=rango), partida_cazador(rango) as (motor, cazador, catalogo):
                self.assertEqual((motor.meta.cripta_id, motor.meta.cripta_version, catalogo.version),
                                 ("prueba", "v1", "cat1"))
                disco = catalogo.almacen.leer_ficha("cat1", cazador.tipo_catalogo)
                with patch.object(catalogo.almacen, "leer_ficha", side_effect=AssertionError("Ficha en disco")):
                    ficha = catalogo.ficha_preparada(cazador.tipo_catalogo)
                for datos in (disco, ficha.atributos):
                    if rango is RANGO_AUSENTE:
                        self.assertNotIn("rango", datos)
                    elif rango is None:
                        self.assertIn("rango", datos)
                        self.assertIsNone(datos["rango"])
                    else:
                        self.assertIs(type(datos["rango"]), int)
                        self.assertEqual(datos["rango"], rango)

    def test_ataque_empatado_y_retroceso_restauran_agenda_y_rng(self):
        with partida_cazador(350, velocidad_jugador=100) as (motor, cazador, catalogo):
            pergamino = ObjetoInstancia("p-t025", "pergamino", "inventario")
            self.assertIsNotNone(motor.jugador.inventario.recoger(pergamino))
            inicial = cazador.evento_pendiente
            futuro = motor.programar_evento(101, "cierre_puerta", (motor.salas[100], "E"))
            vida = motor.jugador.vida
            estado_rng = motor.azar.getstate()
            azar = Random()
            azar.setstate(estado_rng)
            dano = max(1, cazador.ataque + azar.randint(0, 4) - motor.jugador.defensa)
            secuencia = motor.cola.proxima_secuencia()
            ciclo_real = motor.ejecutar_ciclo
            orden = []

            def observar(*args, **kwargs):
                evento = ciclo_real(*args, **kwargs)
                if evento is not None:
                    orden.append((evento.tipo, evento.tiempo, evento.secuencia))
                return evento

            def esperar():
                with patch.object(motor, "ejecutar_ciclo", side_effect=observar), \
                        patch.object(catalogo, "ficha_preparada", side_effect=AssertionError("Rango en ataque")):
                    self.assertTrue(motor.ejecutar("esperar").ok)
                self.assertEqual((motor.reloj, motor.jugador.vida), (100, vida - dano))
                self.assertEqual(motor.azar.getstate(), azar.getstate())
                self.assertEqual(orden, [("turno_enemigo", 100, inicial.secuencia),
                                         ("turno_jugador", 100, secuencia)])
                self.assertTrue(futuro.en_cola)
                return cazador.evento_pendiente

            siguiente = esperar()
            self.assertTrue(motor.ejecutar("retroceso").ok)
            self.assertEqual((motor.reloj, motor.jugador.vida, motor.acciones_jugador), (0, vida, 0))
            self.assertEqual(motor.azar.getstate(), estado_rng)
            self.assertEqual(motor.cola.proxima_secuencia(), secuencia)
            self.assertIs(cazador.evento_pendiente, inicial)
            self.assertTrue(inicial.en_cola)
            self.assertTrue(siguiente.cancelado)
            self.assertTrue(futuro.en_cola)
            self.assertEqual(motor.jugador.inventario.contar("pergamino"), 0)
            orden.clear()
            repetido = esperar()
            self.assertEqual((repetido.tiempo, repetido.secuencia), (siguiente.tiempo, siguiente.secuencia))


class TestDespachoCazadorT025(unittest.TestCase):
    """Estos casos de aceptación requieren conectar el despacho de T025."""

    def alejar_jugador(self, motor):
        for destino, tiempo in ((101, 71), (102, 99)):
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (destino, tiempo))

    def comprobar_turno(self, motor, cazador, catalogo, sala, proximo):
        anterior = cazador.evento_pendiente
        rng = motor.azar.getstate()
        ejecutar = motor._ejecutar_turno_enemigo

        def sin_disco(enemigo, decidir):
            if enemigo is cazador:
                with patch.object(catalogo.almacen, "leer_ficha", side_effect=AssertionError("Ficha en disco")):
                    return ejecutar(enemigo, decidir)
            return ejecutar(enemigo, decidir)

        with patch.object(motor, "_ejecutar_turno_enemigo", side_effect=sin_disco):
            self.assertTrue(motor.ejecutar("esperar").ok)
        siguiente = cazador.evento_pendiente
        self.assertEqual((cazador.sala_actual, siguiente.tiempo), (sala, proximo))
        self.assertFalse(anterior.en_cola)
        self.assertTrue(siguiente.en_cola)
        self.assertIs(siguiente.referencia, cazador)
        self.assertLess(anterior.secuencia, siguiente.secuencia)
        self.assertEqual(motor.azar.getstate(), rng)

    def test_rango_350_recorre_los_arcos_de_250_y_100(self):
        with partida_cazador(350) as (motor, cazador, catalogo):
            self.alejar_jugador(motor)
            self.comprobar_turno(motor, cazador, catalogo, 101, 350)
            for _ in range(7):
                self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual(motor.reloj, 323)
            self.comprobar_turno(motor, cazador, catalogo, 102, 450)

    def test_rango_349_espera_y_lee_la_ficha_residente(self):
        with partida_cazador(349) as (motor, cazador, catalogo):
            self.alejar_jugador(motor)
            with patch.object(catalogo, "ficha_preparada", wraps=catalogo.ficha_preparada) as consultar:
                self.comprobar_turno(motor, cazador, catalogo, 100, 200)
            consultar.assert_called_once_with(cazador.tipo_catalogo)

    def test_rango_null_explicito_persigue_sin_tope(self):
        with partida_cazador(None) as (motor, cazador, catalogo):
            self.alejar_jugador(motor)
            self.comprobar_turno(motor, cazador, catalogo, 101, 350)

    def test_rango_null_explicito_persigue_por_ruta_de_400(self):
        with partida_cazador(None, velocidad_jugador=500, costo_segunda_conexion=150) as (motor, cazador, catalogo):
            ficha = catalogo.ficha_preparada(cazador.tipo_catalogo)
            self.assertIsNone(ficha.atributos["rango"])
            for origen, destino, costo in ((100, 101, 250), (101, 102, 150)):
                ida, vuelta = motor.salas[origen].salidas["E"], motor.salas[destino].salidas["O"]
                self.assertEqual((ida["sala"], vuelta["sala"]), (destino, origen))
                self.assertEqual((ida["costo"], vuelta["costo"]), (costo, costo))
                self.assertFalse(ida.get("cerrada", False) or vuelta.get("cerrada", False))
            for destino, tiempo in ((101, 50), (102, 80)):
                self.assertTrue(motor.ejecutar("mover", "E").ok)
                self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (destino, tiempo))
            self.assertEqual(cazador.evento_pendiente.tiempo, 100)
            self.comprobar_turno(motor, cazador, catalogo, 101, 350)
            self.assertEqual(motor.reloj, 100)

    def test_cierre_real_antes_del_turno_impide_cruzar(self):
        with partida_cazador(None) as (motor, cazador, catalogo):
            cierre = motor.programar_evento(99, "cierre_puerta", (motor.salas[100], "E"))
            self.alejar_jugador(motor)
            self.assertFalse(cierre.en_cola)
            self.assertTrue(motor.salas[100].salidas["E"]["cerrada"])
            with patch.object(catalogo, "ficha_preparada", wraps=catalogo.ficha_preparada) as consultar:
                self.comprobar_turno(motor, cazador, catalogo, 100, 200)
            consultar.assert_called_once_with(cazador.tipo_catalogo)
