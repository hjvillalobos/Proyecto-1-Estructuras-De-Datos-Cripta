from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
from urllib.parse import urlsplit

from datos.almacen import AlmacenLocal
from datos.offline import ClienteOffline
from modelo.cazador import decidir_cazador
from modelo.juego import crear_juego
from modelo.rutas import EspacioBusqueda, GrafoTerreno, HeapRutas, buscar_ruta
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.cliente_api import ClienteApi
from red.errores import DatosNoDisponibles
from red.precarga import GestorPrecarga
from tests.datos_prueba import ServidorFalso
from tests.test_cliente_api import respuesta


class PruebasEntregaTerreno(unittest.TestCase):
    def setUp(self):
        temporal = TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.carpeta = Path(temporal.name)
        self.servidor = ServidorFalso(salas=3)
        self.transporte = Mock()
        self.transporte.get.side_effect = self.responder
        self.cliente = ClienteApi(base_url="https://prueba.invalid", transporte=self.transporte)

    def responder(self, url, params, **opciones):
        ruta = urlsplit(url).path
        if ruta == "/criptas/prueba":
            datos = self.servidor.obtener_datos_generales("prueba")
        elif ruta == "/catalogo/version":
            datos = self.servidor.obtener_version_catalogo()
        elif ruta == "/criptas/prueba/salas":
            datos = self.servidor.obtener_esqueleto("prueba", params["pagina"])
            datos["salas"][0]["salidas"]["E"]["costo"] = 250
            datos["salas"][1]["salidas"]["O"]["costo"] = 250
        elif ruta == "/criptas/prueba/contenido":
            datos = self.servidor.obtener_contenido_salas("prueba", [int(i) for i in params["salas"].split(",")])
            for sala in datos["contenido"]:
                sala["enemigos"] = []
                if sala["sala"] == 100:
                    sala["enemigos"] = [{"instancia": "i-72", "tipo": "largo"},
                                        {"instancia": "i-19", "tipo": "corto"}]
        elif ruta == "/catalogo":
            datos = self.servidor.obtener_catalogo(params["ids"].split(","))
            for ficha in datos["entidades"]:
                if ficha["id"] in ("largo", "corto"):
                    ficha.update(clase="enemigo", comportamiento="cazador", vida_max=10, ataque=2,
                                 defensa=1, velocidad=100, rango=350 if ficha["id"] == "largo" else 349)
        else:
            self.fail(f"Petición inesperada a {ruta}")
        return respuesta(200, datos)

    def preparar(self, cliente, historica=False):
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(), AlmacenLocal(self.carpeta))
        precarga = GestorPrecarga(cliente, catalogo)
        self.addCleanup(precarga.cerrar)
        cripta = precarga.preparar_cripta("prueba", "v1" if historica else None, "cat1" if historica else None)
        self.assertEqual((cripta.generales["id"], cripta.generales["version"], cripta.version_catalogo),
                         ("prueba", "v1", "cat1"))
        return cripta, catalogo

    def comprobar_costos(self, cripta):
        grafo = GrafoTerreno(cripta.salas)
        costos = [(grafo.ids[arco.origen], grafo.ids[arco.destino], arco.costo)
                  for vecinos in grafo.adyacencias for arco in vecinos]
        self.assertCountEqual(costos, [(100, 101, 250), (101, 100, 250), (101, 102, 100), (102, 101, 100)])

    def test_E_B_COSTOS_descarga_y_reapertura(self):
        cripta, _ = self.preparar(self.cliente)
        self.comprobar_costos(cripta)
        pagina = AlmacenLocal(self.carpeta).leer_pagina("prueba", "v1", 1)
        self.assertNotIn("costo", pagina["salas"][1]["salidas"]["E"])
        offline = ClienteOffline(self.carpeta, "v1")
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP en modo offline")):
            cripta, _ = self.preparar(offline, historica=True)
            self.comprobar_costos(cripta)
        self.assertEqual(offline.solicitudes_realizadas, 0)

    def test_T013_movimiento_del_motor_con_costos_reabiertos_offline(self):
        """FR-001/002/003/016: el paquete de B llega a la agenda real del jugador."""
        almacen = AlmacenLocal(self.carpeta)
        catalogo = GestorCatalogo(self.cliente, CacheCatalogoOrdenado(), almacen)
        precarga = GestorPrecarga(self.cliente, catalogo)
        self.addCleanup(precarga.cerrar)
        precarga.preparar_cripta("prueba")
        # Completar el paquete para que la segunda entrada pueda leerse offline.
        precarga.preparar_entrada(102, [])
        solicitudes_previas = self.cliente.solicitudes_realizadas
        llamadas_previas = self.transporte.get.call_count
        self.assertGreater(solicitudes_previas, 0)

        offline = ClienteOffline(self.carpeta, "v1")
        self.addCleanup(offline.cerrar)
        catalogo_offline = GestorCatalogo(offline, CacheCatalogoOrdenado(), AlmacenLocal(self.carpeta))
        precarga_offline = GestorPrecarga(offline, catalogo_offline)
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP durante T013")) as http:
            try:
                motor = crear_juego(precarga_offline, "prueba", semilla=42,
                                    version_cripta="v1", version_catalogo="cat1")
                self.assertEqual((motor.meta.cripta_id, motor.meta.cripta_version, motor.meta.catalogo_version),
                                 ("prueba", "v1", "cat1"))
                self.assertEqual((motor.jugador.posicion_actual, motor.jugador.velocidad, motor.reloj), (100, 100, 0))
                self.assertEqual(motor.salas[100].salidas["E"]["costo"], 250)
                self.assertNotIn("costo", motor.salas[101].salidas["E"])
                mover_real = motor.mover
                turnos = []

                def observar_movimiento(*args, **kwargs):
                    resultado = mover_real(*args, **kwargs)
                    if resultado[0]:
                        turno = motor.jugador.evento_pendiente
                        self.assertTrue(turno.en_cola)
                        self.assertIn(turno, motor.cola.pendientes())
                        self.assertIs(turno.referencia, motor.jugador)
                        self.assertTrue(motor.contenido_cargado[motor.jugador.posicion_actual])
                        turnos.append((motor.reloj, motor.jugador.posicion_actual, turno))
                    return resultado

                with patch.object(motor, "mover", side_effect=observar_movimiento):
                    for numero, (origen, destino, inicio, fin) in enumerate(
                            ((100, 101, 0, 250), (101, 102, 250, 350)), start=1):
                        self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (origen, inicio))
                        resultado = motor.ejecutar("mover", "E")
                        self.assertTrue(resultado.ok, resultado.mensaje)
                        self.assertEqual(len(turnos), numero)
                        instante, sala, turno = turnos[-1]
                        self.assertEqual((instante, sala, turno.tipo, turno.tiempo),
                                         (inicio, destino, "turno_jugador", fin))
                        self.assertEqual((motor.jugador.posicion_actual, motor.reloj), (destino, fin))
                        self.assertFalse(turno.en_cola)
                        self.assertIsNone(motor.jugador.evento_pendiente)
                self.assertLess(turnos[0][2].secuencia, turnos[1][2].secuencia)
                self.assertEqual((motor.acciones_jugador, motor.historial.cantidad_turnos()), (2, 2))
            finally:
                precarga_offline.cerrar()
            http.assert_not_called()
        self.assertEqual(offline.solicitudes_realizadas, 0)
        self.assertEqual(self.cliente.solicitudes_realizadas, solicitudes_previas)
        self.assertEqual(self.transporte.get.call_count, llamadas_previas)

    def comprobar_cazadores(self, cripta, catalogo):
        grafo = GrafoTerreno(cripta.salas)
        espacio = EspacioBusqueda(grafo.ids)
        consulta = partial(buscar_ruta, grafo, espacio, HeapRutas(espacio))
        origen = grafo.indice(cripta.inicial.sala.id)
        destino = grafo.indice(102)
        decisiones = []
        for enemigo in cripta.inicial.contenido["enemigos"]:
            ficha = catalogo.ficha_preparada(enemigo["tipo"])
            self.assertEqual(ficha.atributos["comportamiento"], "cazador")
            rango = ficha.atributos["rango"]
            decision = decidir_cazador(origen, destino, rango, consulta)
            decisiones.append((enemigo["instancia"], ficha.id, rango, decision))
        self.assertCountEqual(decisiones, [("i-72", "largo", 350, ("mover", "E", 250)),
                                          ("i-19", "corto", 349, ("esperar", None, 100))])
        with self.assertRaises(DatosNoDisponibles):
            catalogo.ficha_preparada("i-72")

    def test_E_B_RANGO_por_tipo_en_memoria_y_tras_reapertura(self):
        cripta, catalogo = self.preparar(self.cliente)
        solicitudes = self.cliente.solicitudes_realizadas
        self.transporte.get.side_effect = AssertionError("HTTP durante búsqueda")
        with patch.object(catalogo.almacen, "leer_ficha", side_effect=AssertionError("Lectura durante búsqueda")):
            self.comprobar_cazadores(cripta, catalogo)
        self.assertEqual(self.cliente.solicitudes_realizadas, solicitudes)
        offline = ClienteOffline(self.carpeta, "v1")
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP en modo offline")):
            cripta, catalogo = self.preparar(offline, historica=True)
            with patch.object(catalogo.almacen, "leer_ficha", side_effect=AssertionError("Lectura durante búsqueda")):
                self.comprobar_cazadores(cripta, catalogo)
        self.assertEqual(offline.solicitudes_realizadas, 0)
