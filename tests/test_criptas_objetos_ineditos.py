"""RE-02/IA-01: siete clases del contrato con IDs inéditos y sin arte local."""
import tempfile
import tkinter as tk
import unittest

from datos.almacen import AlmacenLocal
from modelo.juego import crear_juego
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from red.verificacion import verificar_cripta
from tests.datos_prueba import ServidorFalso
from vista.grafica import VistaGrafica


class ServidorSieteClases(ServidorFalso):
    """Datos sintéticos inéditos del contrato; no inventa clases ni reglas."""
    salas_ids = (2_900_000_001, 3_000_000_127, 4_000_000_255)
    clases = ("arma", "armadura", "pocion", "antidoto", "llave",
              "antorcha", "pergamino_retroceso")

    def __init__(self):
        super().__init__(salas=3, presupuesto=100, version="mapa-profesor-inedito",
                         version_catalogo="catalogo-profesor-inedito")

    @staticmethod
    def tipo(clase):
        return "objeto_profesor_7_clases_" + clase

    def obtener_datos_generales(self, cripta_id):
        datos = super().obtener_datos_generales(cripta_id)
        datos.update(sala_inicial=self.salas_ids[0], sala_salida=self.salas_ids[-1],
                     llave_salida=self.tipo("llave"))
        return datos

    def obtener_esqueleto(self, cripta_id, pagina=1):
        self._contar("pagina", [pagina])
        a, b, c = self.salas_ids
        llave = self.tipo("llave")
        return {"pagina": 1, "total_paginas": 1, "salas": [
            {"id": a, "nombre": "Entrada inédita", "salidas": {"E": {"sala": b}}},
            {"id": b, "nombre": "Galería inédita", "salidas": {
                "O": {"sala": a}, "E": {"sala": c, "cerrada": True, "llave": llave}}},
            {"id": c, "nombre": "Salida inédita", "salidas": {
                "O": {"sala": b, "cerrada": True, "llave": llave}}},
        ]}

    def obtener_llaves(self, cripta_id):
        self._contar("llaves")
        return {"llaves": [{"id": self.tipo("llave"), "sala": self.salas_ids[0]}]}

    def obtener_contenido_salas(self, cripta_id, salas_ids):
        self._contar("contenido", salas_ids)
        return {"contenido": [{
            "sala": sala, "enemigos": [],
            "objetos": [self.tipo(clase) for clase in self.clases]
                       if sala == self.salas_ids[0] else [],
            "trampas": [{"instancia": "trampa-profesor-nueva", "tipo": "trampa_profesor_7_clases"}]
                       if sala == self.salas_ids[1] else [],
        } for sala in salas_ids]}

    def obtener_catalogo(self, ids):
        self._contar("catalogo", ids)
        atributos = {
            "arma": {"ataque_bonus": 5}, "armadura": {"defensa_bonus": 4},
            "pocion": {"cura": 9}, "antidoto": {},
            "llave": {"abre": self.tipo("llave")},
            "antorcha": {"duracion": 10000}, "pergamino_retroceso": {},
        }
        fichas = []
        for clave in ids:
            if clave == "trampa_profesor_7_clases":
                fichas.append({"id": clave, "clase": "trampa", "nombre": "Trampa inédita",
                               "daño": 3, "veneno": {"dano_por_pulso": 1}, "rearme": 1000})
            else:
                clase = next(c for c in self.clases if clave == self.tipo(c))
                fichas.append({"id": clave, "clase": clase, "nombre": "Nuevo " + clase,
                               "peso": 2, "valor": 17, **atributos[clase]})
        return {"entidades": fichas}


class TestCriptaYObjetosIneditos(unittest.TestCase):
    def preparar(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        almacen = AlmacenLocal(temporal.name)
        servidor = ServidorSieteClases()
        cripta_id = "cripta-profesor-nueva-siete-clases"
        reporte = verificar_cripta(servidor, almacen, cripta_id)
        self.assertEqual(reporte.estado, "resoluble")
        precarga = GestorPrecarga(servidor, GestorCatalogo(
            servidor, CacheCatalogoOrdenado(25), almacen))
        self.addCleanup(precarga.cerrar)
        motor = crear_juego(precarga, cripta_id, 7331, partida_completa=True)
        return servidor, motor

    def recoger_todos(self, servidor, motor):
        instancias = {}
        for objeto in list(motor.objetos_en_suelo[servidor.salas_ids[0]]):
            clase = next(c for c in servidor.clases if objeto.tipo_catalogo == servidor.tipo(c))
            instancias[clase] = objeto.id_instancia
            resultado = motor.ejecutar("recoger", objeto.id_instancia)
            self.assertTrue(resultado.ok, resultado.mensaje)
        self.assertEqual({item.clase for item in motor.inventario_vista()}, set(servidor.clases))
        return instancias

    def test_re02_siete_clases_por_precarga_acciones_y_salida_en_ids_dispersos(self):
        servidor, motor = self.preparar()
        items = self.recoger_todos(servidor, motor)
        for clase in ("arma", "armadura"):
            self.assertTrue(motor.ejecutar("equipar", items[clase]).ok)
        self.assertEqual((motor.jugador.ataque, motor.jugador.defensa), (11, 6))

        antes_esperar = motor.reloj
        self.assertTrue(motor.ejecutar("esperar").ok)
        self.assertTrue(motor.ejecutar("usar", items["pergamino_retroceso"]).ok)
        self.assertEqual(motor.reloj, antes_esperar)
        self.assertFalse(any(i.clase == "pergamino_retroceso" for i in motor.inventario_vista()))

        self.assertTrue(motor.ejecutar("usar", items["antorcha"]).ok)
        self.assertIn("antorcha", motor.estado_vista().efectos)
        self.assertTrue(motor.ejecutar("mover", "E").ok)
        self.assertLess(motor.jugador.vida, motor.jugador.vida_max)
        self.assertIsNotNone(motor.jugador.veneno)
        self.assertTrue(motor.ejecutar("usar", items["antidoto"]).ok)
        self.assertIsNone(motor.jugador.veneno)
        self.assertTrue(motor.ejecutar("usar", items["pocion"]).ok)
        self.assertEqual(motor.jugador.vida, motor.jugador.vida_max)
        antes = motor.exportar_estado()
        self.assertFalse(motor.ejecutar("mover", "E").ok)
        self.assertEqual(motor.exportar_estado(), antes)
        self.assertTrue(motor.ejecutar("abrir", "E").ok)
        self.assertTrue(motor.ejecutar("mover", "E").ok)
        self.assertEqual(motor.resultado, "victoria")
        self.assertEqual(motor.jugador.posicion_actual, servidor.salas_ids[-1])
        self.assertLessEqual(servidor.solicitudes_realizadas, servidor.presupuesto)

    def test_re02_siete_tipos_sin_png_muestran_pregunta_en_suelo_inventario_y_equipo(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(vista.cerrar)
        vista.root.geometry("1280x800")
        vista.root.update()
        servidor, motor = self.preparar()
        estado = motor.estado_vista()
        antes = motor.exportar_estado()
        vista.mostrar_estado(estado, [])
        for i, objeto in enumerate(estado.objetos_suelo):
            with self.subTest(suelo=objeto.tipo):
                self.assertIsNone(vista.recursos.imagen(objeto.tipo, 26, 26))
                neutral = str(vista.recursos.imagen_neutra(26, 26))
                imagenes = [vista.canvas.itemcget(item, "image")
                            for item in vista.canvas.find_withtag(f"objeto_{i}")
                            if vista.canvas.type(item) == "image"]
                self.assertEqual(imagenes, [neutral])
        self.assertEqual(motor.exportar_estado(), antes)

        items = self.recoger_todos(servidor, motor)
        vista.mostrar_inventario(motor.inventario_vista())
        for indice, item in enumerate(vista._items):
            with self.subTest(inventario=item.clase):
                vista.lista.selection_clear(0, "end")
                vista.lista.selection_set(indice)
                vista._mostrar_detalle()
                self.assertIs(vista._imagen_detalle, vista.recursos.imagen_neutra(52, 52))
                self.assertIn(item.nombre, vista.var_detalle.get())
                self.assertIn("17", vista.var_detalle.get())

        for clase in ("arma", "armadura"):
            self.assertTrue(motor.ejecutar("equipar", items[clase]).ok)
        antes = motor.exportar_estado()
        vista.mostrar_estado(motor.estado_vista(), [])
        for etiqueta in ("arma_visible", "armadura_visible"):
            imagenes = [vista.canvas.itemcget(i, "image") for i in vista.canvas.find_withtag(etiqueta)
                        if vista.canvas.type(i) == "image"]
            self.assertEqual(len(imagenes), 1)
            self.assertIn(imagenes[0], [str(foto) for _, foto in vista.recursos._neutras])
        self.assertEqual(motor.exportar_estado(), antes)


if __name__ == "__main__":
    unittest.main()
