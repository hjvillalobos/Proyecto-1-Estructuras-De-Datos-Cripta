from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from datos.almacen import AlmacenLocal
from red.cache import CacheCatalogoOrdenado, CacheSinEspacioError
from red.catalogo import GestorCatalogo
from red.errores import DatosInvalidos, VersionIncompatible
from tests.datos_prueba import ServidorFalso


class TestCatalogoPersistente(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.almacen = AlmacenLocal(self.temporal.name)
        self.cliente = ServidorFalso()
        self.cache = CacheCatalogoOrdenado(3)
        self.catalogo = GestorCatalogo(self.cliente, self.cache, self.almacen)

    def test_precarga_en_lotes_sin_desbordar_memoria(self):
        ids = [f"ficha_{i}" for i in range(31)]
        self.catalogo.precargar(ids + ids)
        lotes = [valores for operacion, valores in self.cliente.llamadas if operacion == "catalogo"]
        self.assertEqual([len(valores) for valores in lotes], [10, 10, 10, 1])
        self.assertEqual(self.cache.tamaño_actual, 0)
        antes = self.cliente.solicitudes_realizadas
        self.catalogo.precargar(ids)
        self.assertEqual(self.cliente.solicitudes_realizadas, antes)

    def test_desalojada_se_recupera_sin_red(self):
        for clave in ("a", "b", "c", "d"):
            self.catalogo.obtener_fichas([clave])
        self.assertFalse(self.cache.contiene("a"))
        solicitudes = self.cliente.solicitudes_realizadas
        recuperaciones = self.catalogo.recuperaciones_disco
        self.assertEqual(self.catalogo.obtener_fichas(["a"])[0].id, "a")
        self.assertEqual(self.cliente.solicitudes_realizadas, solicitudes)
        self.assertEqual(self.catalogo.recuperaciones_disco, recuperaciones + 1)

    def test_reinicio_y_version_distinta(self):
        self.catalogo.obtener_fichas(["a"])
        otro_cliente = ServidorFalso()
        otro = GestorCatalogo(otro_cliente, CacheCatalogoOrdenado(), self.almacen)
        self.assertEqual(otro.obtener_fichas(["a"])[0].nombre, "cat1")
        self.assertEqual(otro_cliente.llamadas, [("version_catalogo", ())])
        nuevo_cliente = ServidorFalso(version_catalogo="cat2")
        nuevo = GestorCatalogo(nuevo_cliente, CacheCatalogoOrdenado(), self.almacen)
        self.assertEqual(nuevo.obtener_fichas(["a"])[0].nombre, "cat2")
        self.assertIn(("catalogo", ("a",)), nuevo_cliente.llamadas)
        self.assertEqual(self.almacen.leer_ficha("cat1", "a")["nombre"], "cat1")

    def test_version_antigua_solo_usa_copia_compatible(self):
        self.catalogo.precargar(["a"])
        cliente = ServidorFalso(version_catalogo="cat2")
        gestor = GestorCatalogo(cliente, CacheCatalogoOrdenado(), self.almacen)
        gestor.iniciar("cat1")
        self.assertEqual(gestor.obtener_fichas(["a"])[0].nombre, "cat1")
        with self.assertRaises(VersionIncompatible):
            gestor.obtener_fichas(["b"])
        self.assertEqual(cliente.llamadas, [("version_catalogo", ())])

    def test_referencias_repetidas_protegidas_y_liberadas(self):
        fichas = self.catalogo.retener(["a", "a", "b"])
        self.assertIs(fichas[0], fichas[1])
        self.catalogo.obtener_fichas(["c"])
        self.catalogo.obtener_fichas(["d"])
        self.assertTrue(self.cache.contiene("a"))
        self.assertTrue(self.cache.contiene("b"))
        self.assertFalse(self.cache.contiene("c"))
        nodo = self.cache.arreglo[self.cache._posicion("a")]
        self.assertEqual(nodo.referencias, 2)
        self.catalogo.liberar(["a"])
        self.assertEqual(nodo.referencias, 1)
        with self.assertRaises(DatosInvalidos):
            self.catalogo.liberar(["a", "a"])
        self.assertEqual(nodo.referencias, 1)

    def test_cambio_de_sala_actualiza_referencias(self):
        self.catalogo.fijar_referencias(["a", "b", "c"])
        self.catalogo.fijar_referencias(["b", "d", "e"])
        self.assertEqual([nodo.clave for nodo in self.cache.arreglo], ["b", "d", "e"])
        self.assertEqual([nodo.referencias for nodo in self.cache.arreglo], [1, 1, 1])

    def test_capacidad_insuficiente_no_cambia_estado(self):
        self.catalogo.retener(["a", "b", "c"])
        nodos = self.cache.arreglo.copy()
        llamadas = self.cliente.solicitudes_realizadas
        with self.assertRaises(CacheSinEspacioError):
            self.catalogo.retener(["d"])
        self.assertEqual(self.cache.arreglo, nodos)
        self.assertEqual(self.cliente.solicitudes_realizadas, llamadas)
        self.assertEqual([n.referencias for n in nodos], [1, 1, 1])

    def test_copia_json_orden_y_respuesta_incompleta(self):
        datos = {"id": "a", "clase": "arma", "nombre": "Arma", "extra": [1]}
        original = deepcopy(datos)
        ficha = self.catalogo._procesar_json_a_ficha(datos)
        ficha.atributos["extra"].append(2)
        self.assertEqual(datos, original)
        self.cliente.invertir = True
        self.assertEqual([f.id for f in self.catalogo.obtener_fichas(["c", "a", "b"])],
                         ["c", "a", "b"])
        self.cliente.omitir = True
        with self.assertRaises(DatosInvalidos):
            self.catalogo.precargar(["ausente"])

    def test_dependencias_y_ciclo_no_repiten_descarga(self):
        self.catalogo.precargar(["enemigo"])
        self.assertIsNotNone(self.almacen.leer_ficha("cat1", "pocion"))
        self.almacen.guardar_ficha("cat1", {"id": "x", "clase": "enemigo",
                                          "nombre": "X", "suelta": ["y"]})
        self.almacen.guardar_ficha("cat1", {"id": "y", "clase": "enemigo",
                                          "nombre": "Y", "suelta": ["x"]})
        antes = self.cliente.solicitudes_realizadas
        self.catalogo.precargar(["x"])
        self.assertEqual(self.cliente.solicitudes_realizadas, antes)

    def test_cambio_version_con_activas_se_rechaza(self):
        self.catalogo.retener(["a"])
        self.cliente.version_catalogo = "cat2"
        with self.assertRaises(CacheSinEspacioError):
            self.catalogo.iniciar()
        self.assertEqual(self.catalogo.version, "cat1")

    def test_archivo_corrupto_y_claves_sin_escape_de_carpeta(self):
        self.catalogo.precargar(["../../otra"])
        archivos = list(Path(self.temporal.name).rglob("*.json"))
        self.assertEqual(len(archivos), 3)
        for archivo in archivos:
            self.assertTrue(archivo.resolve().is_relative_to(Path(self.temporal.name).resolve()))
        self.almacen.guardar_ficha("cat1", {"id": "mal"})
        with self.assertRaises(DatosInvalidos):
            self.catalogo.obtener_fichas(["mal"])

    def test_reporte_cache(self):
        self.catalogo.obtener_fichas(["a"])
        self.catalogo.obtener_fichas(["a"])
        reporte = self.catalogo.reporte()
        self.assertEqual(reporte["aciertos_cache"], 1)
        self.assertEqual(reporte["fallos_cache"], 1)
        self.assertEqual(reporte["recuperaciones_disco"], 1)
