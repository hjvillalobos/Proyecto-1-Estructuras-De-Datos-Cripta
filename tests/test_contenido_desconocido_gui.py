import io
import tempfile
import tkinter as tk
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

import main
from datos.almacen import AlmacenLocal
from modelo.juego import crear_juego
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.test_verificacion_entrega import CriptaDesconocida
from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos
from vista.selector_cripta import SelectorCripta


class TestContenidoDesconocidoGUI(unittest.TestCase):
    def setUp(self):
        try:
            self.v = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.v.cerrar)
        self.v.root.geometry("1280x800")
        self.v.root.update()
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)

    def test_neutro_compartido_y_sin_pillow(self):
        r = self.v.recursos
        a = r.imagen_entidad("id-no-conocido-1", 52, 52)
        self.assertIs(a, r.imagen_entidad("id-no-conocido-2", 52, 52))
        self.assertNotEqual(a.get(0, 0), a.get(21, 3))
        with patch("vista.recursos_graficos.Image", None):
            self.assertIsNotNone(r.imagen_entidad("id-no-conocido-3", 26, 26))
        for ancho, alto in ((8, 8), (26, 26), (52, 52), (205, 144)):
            foto = r.imagen_neutra(ancho, alto)
            self.assertLessEqual(foto.width(), ancho)
            self.assertLessEqual(foto.height(), alto)
        self.assertLessEqual(len(r._neutras), 7)

    def test_imagenes_conocidas_se_conservan_y_png_danado_tiene_respaldo(self):
        r = self.v.recursos
        original = r.imagen("itm_pocion_menor", 26, 26)
        self.assertIs(r.imagen_entidad("itm_pocion_menor", 26, 26), original)
        carpeta = Path(self.temporal.name)
        (carpeta / "id-nuevo.png").write_bytes(b"no es un PNG")
        otro = RecursosGraficos(self.v.root, carpeta)
        self.assertIsNotNone(otro.imagen_entidad("id-nuevo", 26, 26))
        with patch.object(Path, "is_file", side_effect=AssertionError("Busco de nuevo")):
            self.assertIsNotNone(otro.imagen_entidad("id-nuevo", 26, 26))

    def test_muchos_ids_no_crean_un_icono_por_tipo(self):
        r = self.v.recursos
        for i in range(80):
            r.imagen_entidad(f"tipo_sin_arte_{i}", 52, 52)
        self.assertEqual(len(r._neutras), 1)
        self.assertLessEqual(len(r._ausentes), 64)

    def test_catalogo_nuevo_en_escena_inventario_equipo_y_trampas(self):
        v = self.v
        servidor = CriptaDesconocida(17)
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), AlmacenLocal(self.temporal.name))
        precarga = GestorPrecarga(servidor, catalogo)
        self.addCleanup(precarga.cerrar)
        motor = crear_juego(precarga, "cripta-profesor-nueva", 12345)
        for objeto in list(motor.objetos_en_suelo[100]):
            self.assertTrue(motor.ejecutar("recoger", objeto.id_instancia).ok)
            if objeto.tipo_catalogo == "arma_nueva":
                self.assertTrue(motor.ejecutar("equipar", objeto.id_instancia).ok)
                arma = objeto
        self.assertEqual(motor.jugador.ataque, 26)
        for _ in range(5):
            self.assertTrue(motor.ejecutar("mover", "E").ok)
        antes = motor.exportar_estado()
        estado = motor.estado_vista()
        self.assertTrue(estado.enemigos and estado.objetos_suelo and estado.trampas)
        with patch.object(v, "_ligar", wraps=v._ligar) as ligar:
            v.mostrar_estado(estado, [])
        v.mostrar_inventario(motor.inventario_vista())
        indice = next(i for i, item in enumerate(v._items) if item.instancia == arma.id_instancia)
        v.lista.selection_clear(0, "end")
        v.lista.selection_set(indice)
        v._mostrar_detalle()
        self.assertIs(v._imagen_detalle, v.recursos.imagen_neutra(52, 52))
        self.assertIn("arma_nueva", v.var_detalle.get())
        self.assertIn("20", v.var_detalle.get())
        self.assertTrue(v.canvas.find_withtag("arma_visible"))
        for i, enemigo in enumerate(estado.enemigos[:8]):
            ligar.assert_any_call(f"enemigo_{i}", f"atacar {enemigo.instancia}")
            textos = [v.canvas.itemcget(item, "text") for item in v.canvas.find_withtag(f"enemigo_{i}")
                      if v.canvas.type(item) == "text"]
            self.assertIn(enemigo.nombre, textos)
        for i, objeto in enumerate(estado.objetos_suelo[:8]):
            ligar.assert_any_call(f"objeto_{i}", f"recoger {objeto.instancia}")
        for trampa in estado.trampas:
            self.assertTrue(any(v.canvas.type(i) == "image" for i in v.canvas.find_withtag("trampa_" + trampa.instancia)))
        v.escena.animacion.situar(20)
        self.assertEqual(motor.exportar_estado(), antes)
        v.var_movimiento.set(False)
        v._alternar_movimiento()
        self.assertTrue(v.canvas.find_withtag("arma_visible"))
        self.assertEqual(motor.exportar_estado(), antes)

    def test_selector_acepta_mas_de_cuatro_criptas_e_ids_no_previstos(self):
        criptas = [{"id": f"cripta-inedita-{i}", "nombre": f"Cripta inedita {i}",
                    "salas": 73 + i, "dificultad": 2} for i in range(7)]
        selector = SelectorCripta(self.v, criptas)
        selector.lista.selection_clear(0, "end")
        selector.lista.selection_set(6)
        selector.lista.see(6)
        selector.aceptar()
        self.assertEqual(selector.resultado, criptas[6]["id"])
        vista, sesion = Mock(spec=VistaGrafica), Mock()
        vista.mostrar_menu.return_value = ("jugar", None)
        vista.elegir_cripta.return_value = criptas[6]["id"]
        sesion.cliente.listar_criptas.return_value = {"criptas": criptas}
        with patch("main.SesionDatos", return_value=sesion), \
                patch("vista.grafica.VistaGrafica", return_value=vista), \
                patch("modelo.juego.crear_juego", return_value=Mock(resultado=None)) as crear, \
                patch("controlador.controlador.ControladorJuego"), redirect_stdout(io.StringIO()):
            self.assertEqual(main.main(["--gui", "--semilla", "4", "--datos-dir", self.temporal.name]), 0)
        self.assertEqual(crear.call_args.args, (sesion.precarga, criptas[6]["id"], 4))

    def test_equipo_nuevo_con_antorcha_poses_y_movimiento_desactivado(self):
        v = self.v
        servidor = CriptaDesconocida(17)
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), AlmacenLocal(self.temporal.name))
        precarga = GestorPrecarga(servidor, catalogo)
        self.addCleanup(precarga.cerrar)
        motor = crear_juego(precarga, "cripta-profesor-nueva", 12345)
        antes = motor.exportar_estado()
        base = replace(motor.estado_vista(), arma_tipo="arma_sin_imagen",
                       armadura_tipo="armadura_sin_imagen", efectos=["antorcha", "veneno", "efecto_nuevo"])
        for movimiento in (True, False):
            v._movimiento_activo = movimiento
            for accion, vida in ((None, base.vida), ("atacar", base.vida), (None, 0),
                                 ("cargar", base.vida), ("retroceso", base.vida)):
                with self.subTest(movimiento=movimiento, accion=accion, vida=vida):
                    v._accion_visual = accion
                    v.mostrar_estado(replace(base, vida=vida), [])
                    self.assertTrue(v.canvas.find_withtag("jugador"))
                    for etiqueta in ("arma_visible", "armadura_visible"):
                        items = v.canvas.find_withtag(etiqueta)
                        self.assertEqual(len(items), 1)
                        foto = v.canvas.itemcget(items[0], "image")
                        self.assertIn(foto, [str(imagen) for _, imagen in v.recursos._neutras])
                    if v.escena.animacion is not None:
                        v.escena.animacion.situar(20)
                    self.assertEqual(motor.exportar_estado(), antes)
