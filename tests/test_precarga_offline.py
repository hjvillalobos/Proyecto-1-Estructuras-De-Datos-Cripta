from contextlib import redirect_stdout, redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from datos.almacen import AlmacenLocal
from datos.offline import ClienteOffline
from main import main
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.errores import DatosInvalidos, DatosNoDisponibles, PresupuestoAgotado, VersionIncompatible
from red.precarga import GestorPrecarga
from tests.datos_prueba import ServidorFalso, crear_paquete


class TestPrecarga(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.almacen = AlmacenLocal(self.temporal.name)
        self.cliente = ServidorFalso()
        self.gestor = self.crear_gestor(self.cliente)
        self.addCleanup(self.gestor.cerrar)

    def crear_gestor(self, cliente):
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), self.almacen)
        return GestorPrecarga(cliente, catalogo)

    def test_todas_las_paginas_y_lotes(self):
        self.cliente.cantidad = 103
        preparada = self.gestor.preparar_cripta("prueba")
        self.assertEqual(len(preparada.salas), 103)
        self.assertEqual(preparada.inicial.sala.id, 100)
        self.assertEqual(len(preparada.inicial.fichas), 2)
        self.gestor.cargar_contenido([sala.id for sala in preparada.salas])
        paginas = [valores for tipo, valores in self.cliente.llamadas if tipo == "pagina"]
        self.assertEqual(paginas, [(1,), (2,), (3,)])
        lotes = [valores for tipo, valores in self.cliente.llamadas if tipo == "contenido"]
        self.assertTrue(all(1 <= len(valores) <= 10 for valores in lotes))
        ids = [clave for valores in lotes for clave in valores]
        self.assertEqual(len(ids), 103)
        self.assertEqual(len([clave for i, clave in enumerate(ids) if clave not in ids[:i]]), 103)

    def test_respuestas_invertidas_y_copia_independiente(self):
        self.cliente.invertir = True
        self.gestor.preparar_cripta("prueba")
        self.assertEqual([dato["sala"] for dato in self.gestor.contenidos], list(range(100, 110)))
        datos = self.gestor.cargar_contenido([102, 100, 102])
        self.assertEqual([dato["sala"] for dato in datos], [102, 100])
        datos[0]["objetos"].clear()
        self.assertTrue(self.gestor.cargar_contenido([102])[0]["objetos"])

    def test_precarga_pendiente_no_duplica_y_no_activa_enemigos(self):
        self.gestor.preparar_cripta("prueba")
        self.cliente.bloquear = True
        self.addCleanup(self.cliente.continuar.set)
        self.assertTrue(self.gestor.anticipar(109))
        self.assertTrue(self.cliente.empezo.wait(2))
        self.assertFalse(self.gestor.anticipar(109))
        self.assertIsNone(self.gestor._contenido(110))
        self.cliente.continuar.set()
        contenido = self.gestor.cargar_contenido([110])[0]
        self.assertEqual(contenido["enemigos"][0]["instancia"], "e-110")
        self.assertNotIn("tiempo_siguiente", contenido["enemigos"][0])
        self.assertIsNone(self.gestor.pendiente)
        self.assertEqual(sum(110 in ids for tipo, ids in self.cliente.llamadas if tipo == "contenido"), 1)

    def test_reinicio_caliente_solo_consulta_versiones(self):
        self.gestor.preparar_cripta("prueba")
        self.gestor.cargar_contenido(list(range(100, 123)))
        nuevo = ServidorFalso()
        otro = self.crear_gestor(nuevo)
        otro.preparar_cripta("prueba")
        otro.cargar_contenido(list(range(100, 123)))
        self.assertEqual(nuevo.llamadas, [("version_cripta", ()), ("version_catalogo", ())])

    def test_cripta_nueva_invalida_contenido_previo(self):
        self.gestor.preparar_cripta("prueba")
        nuevo = ServidorFalso(version="v2")
        otro = self.crear_gestor(nuevo)
        preparada = otro.preparar_cripta("prueba")
        self.assertEqual(preparada.generales["version"], "v2")
        self.assertTrue(any(tipo == "contenido" for tipo, _ in nuevo.llamadas))
        self.assertFalse(any(tipo == "catalogo" for tipo, _ in nuevo.llamadas))

    def test_version_antigua_no_mezcla_contenido(self):
        self.gestor.preparar_cripta("prueba")
        nuevo = ServidorFalso(version="v2")
        otro = self.crear_gestor(nuevo)
        preparada = otro.preparar_cripta("prueba", version_cripta="v1")
        self.assertEqual(preparada.generales["version"], "v1")
        with self.assertRaises(VersionIncompatible):
            otro.cargar_contenido([122])
        self.assertFalse(any(tipo == "contenido" for tipo, _ in nuevo.llamadas))

    def test_presupuesto_bajo_no_se_supera(self):
        self.cliente.presupuesto = 2
        with self.assertRaises(PresupuestoAgotado):
            self.gestor.preparar_cripta("prueba")
        self.assertEqual(self.cliente.solicitudes_realizadas, 2)

    def test_contenido_listo_no_espera_otro_lote(self):
        self.gestor.preparar_cripta("prueba")
        self.cliente.bloquear = True
        self.addCleanup(self.cliente.continuar.set)
        self.gestor.anticipar(109)
        self.assertTrue(self.cliente.empezo.wait(2))
        self.assertEqual(self.gestor.cargar_contenido([100])[0]["sala"], 100)
        self.assertTrue(self.gestor.pendiente.hilo.is_alive())

    def test_versiones_fijadas_con_copia_completa_no_necesitan_red(self):
        self.gestor.preparar_cripta("prueba")
        self.gestor.cargar_contenido(list(range(100, 123)))
        cliente = ServidorFalso(presupuesto=0)
        cliente._contar = lambda *args: self.fail("No debe acceder a la red.")
        otro = self.crear_gestor(cliente)
        preparada = otro.preparar_cripta("prueba", version_cripta="v1", version_catalogo="cat1")
        self.assertEqual(preparada.version_catalogo, "cat1")
        self.assertEqual(len(otro.cargar_contenido(list(range(100, 123)))), 23)

    def test_error_en_segundo_plano_se_reporta(self):
        self.gestor.preparar_cripta("prueba")
        self.cliente.omitir = True
        self.gestor.anticipar(109)
        with self.assertRaises(DatosInvalidos):
            self.gestor.cargar_contenido([110])
        self.assertIsNone(self.gestor._contenido(110))
        self.assertIsNone(self.gestor.pendiente)

    def test_contenido_incompleto_no_confirma_sala(self):
        self.cliente.omitir = True
        with self.assertRaises(DatosInvalidos):
            self.gestor.preparar_cripta("prueba")
        self.assertFalse(self.gestor.contenidos)

    def test_entrada_retiene_inventario_y_enemigos_previos(self):
        self.gestor.preparar_cripta("prueba")
        nueva = self.gestor.preparar_entrada(101, ["enemigo", "obj_2"])
        self.assertEqual(nueva.sala.id, 101)
        cache = self.gestor.catalogo.cache
        self.assertEqual(cache.arreglo[cache._posicion("enemigo")].referencias, 2)
        self.assertTrue(cache.contiene("obj_2"))


class TestOffline(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.paquete = self.raiz / "paquete"
        crear_paquete(self.paquete)

    def test_mismo_contrato_cero_red_y_sin_requests(self):
        cliente = ClienteOffline(self.paquete)
        almacen = AlmacenLocal(self.raiz / "sesion")
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(), almacen)
        gestor = GestorPrecarga(cliente, catalogo)
        with patch("requests.sessions.Session.request", side_effect=AssertionError("Se usó red")):
            preparada = gestor.preparar_cripta("prueba")
            gestor.cargar_contenido([sala.id for sala in preparada.salas])
        self.assertEqual(cliente.solicitudes_realizadas, 0)
        self.assertEqual(preparada.inicial.sala.id, 100)
        self.assertEqual(cliente.listar_criptas()["criptas"][0]["id"], "prueba")

    def test_offline_incompleto_error_claro(self):
        cliente = ClienteOffline(self.paquete)
        with self.assertRaises(DatosNoDisponibles):
            cliente.obtener_catalogo(["inexistente"])
        with self.assertRaises(DatosNoDisponibles):
            cliente.obtener_contenido_salas("prueba", [999])
        self.assertEqual(cliente.solicitudes_realizadas, 0)

    def test_cli_offline_y_reporte(self):
        salida = io.StringIO()
        with redirect_stdout(salida), patch("requests.sessions.Session.request",
                                          side_effect=AssertionError("Se usó red")):
            codigo = main(["--offline", str(self.paquete), "--cripta", "prueba",
                           "--datos-dir", str(self.raiz / "sesion"), "--cache-size", "3",
                           "--descargar-todo"])
        self.assertEqual(codigo, 0)
        self.assertIn('"solicitudes_realizadas": 0', salida.getvalue())
        self.assertIn('"capacidad_cache": 3', salida.getvalue())

    def test_cli_error_controlado(self):
        salida = io.StringIO()
        errores = io.StringIO()
        with redirect_stdout(salida), redirect_stderr(errores):
            codigo = main(["--offline", str(self.paquete), "--cripta", "ausente",
                           "--datos-dir", str(self.raiz / "sesion")])
        self.assertEqual(codigo, 1)
        self.assertIn("faltan datos", errores.getvalue())
