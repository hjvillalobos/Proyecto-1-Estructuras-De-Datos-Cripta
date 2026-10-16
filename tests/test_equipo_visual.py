import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from dataclasses import replace

from datos.guardado_binario import guardar_estado, cargar_estado
from tests import test_regresiones_juego as base
from vista.animacion import AnimacionEscena
from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos, Image, ImageTk
from vista.equipo_visual import vestir_jugador


class TestEquipoVisual(unittest.TestCase):
    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_coraza_real_forma_parte_del_sprite_y_desaparece_al_quitarla(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(vista.cerrar)
        vista.root.withdraw()
        antes = datos.motor.exportar_estado()
        estado = replace(datos.motor.estado_vista(), armadura_tipo="itm_coraza_cuero")
        vista.mostrar_estado(estado, [])
        jugador = vista.canvas.find_withtag("jugador")[0]
        self.assertEqual(vista.canvas.find_withtag("armadura_visible"), (jugador,))
        for accion in ("atacar", "caer"):
            vista._accion_visual = accion
            if accion == "caer":
                estado = replace(estado, vida=0)
            vista.escena.dibujar(estado)
            self.assertEqual(vista.canvas.find_withtag("armadura_visible"),
                             vista.canvas.find_withtag("jugador"))
            self.assertEqual(len(vista.escena.animacion.secuencias), 1)
        vista.var_movimiento.set(False)
        vista._alternar_movimiento()
        self.assertTrue(vista.canvas.find_withtag("armadura_visible"))
        vista.mostrar_estado(datos.motor.estado_vista(), [])
        self.assertFalse(vista.canvas.find_withtag("armadura_visible"))
        self.assertEqual(datos.motor.exportar_estado(), antes)

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_chaleco_integrado_conserva_silueta_y_no_modifica_original(self):
        carpeta = Path(__file__).resolve().parents[1] / "vista" / "recursos"
        with Image.open(carpeta / "jugador.png") as origen:
            jugador = origen.convert("RGBA")
        with Image.open(carpeta / "itm_coraza_cuero.png") as origen:
            chaleco = origen.convert("RGBA")
            chaleco = chaleco.crop(chaleco.getchannel("A").getbbox())
        antes = jugador.tobytes()
        vestido = vestir_jugador(jugador, chaleco)
        self.assertEqual(vestido.size, jugador.size)
        self.assertEqual(vestido.getchannel("A").tobytes(), jugador.getchannel("A").tobytes())
        self.assertEqual(jugador.tobytes(), antes)
        self.assertNotEqual(vestido.tobytes(), antes)
        from PIL import ImageChops
        zona_ropa = ImageChops.difference(jugador.convert("RGB"), vestido.convert("RGB")).getbbox()
        self.assertGreater(zona_ropa[2] - zona_ropa[0], jugador.width * .20)
        # Cabeza y piernas originales no deben quedar cubiertas por ropa flotante.
        for zona in ((0, 0, jugador.width, int(jugador.height * .20)),
                     (0, int(jugador.height * .46), jugador.width, jugador.height)):
            self.assertEqual(vestido.crop(zona).tobytes(), jugador.crop(zona).tobytes())

    @unittest.skipIf(Image is None, "Pillow no disponible")
    def test_fotogramas_vestidos_siguen_pose_y_reflejo_con_cache_acotada(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(root.destroy)
        root.withdraw()
        recursos = RecursosGraficos(root)
        ropa = "itm_coraza_cuero"
        desnudos = recursos.fotogramas_jugador(290, 196)
        vestidos = recursos.fotogramas_jugador(290, 196, armadura=ropa)
        reflejados = recursos.fotogramas_jugador(290, 196, invertir=True, armadura=ropa)
        self.assertIs(recursos.fotogramas_jugador(290, 196, armadura=ropa), vestidos)
        self.assertEqual(len(vestidos), 8)
        for original, vestido, reflejado in zip(desnudos, vestidos, reflejados):
            original, vestido, reflejado = map(ImageTk.getimage, (original, vestido, reflejado))
            self.assertEqual(original.size, vestido.size)
            self.assertNotEqual(original.tobytes(), vestido.tobytes())
            self.assertEqual(vestido.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(),
                             reflejado.tobytes())
        for alto in (120, 140, 160, 180, 196):
            self.assertIsNotNone(recursos.jugador_vestido(230, alto, ropa))
        self.assertLessEqual(len(recursos._jugadores_vestidos), 4)
        self.assertLessEqual(len(recursos._secuencias), 4)
        self.assertIsNone(recursos.jugador_vestido(230, 196, "no_existe"))

    def test_snapshot_refleja_equipo_soltar_retroceso_y_carga(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        motor = datos.motor
        for tipo in ("daga", "coraza", "pergamino"):
            datos._inventario(tipo)
        motor.ejecutar("equipar", "daga")
        motor.ejecutar("equipar", "coraza")
        self.assertEqual((motor.estado_vista().arma_tipo, motor.estado_vista().armadura_tipo), ("daga", "coraza"))
        estado = motor.exportar_estado()
        motor.ejecutar("soltar", "daga")
        self.assertIsNone(motor.estado_vista().arma_tipo)
        motor.ejecutar("retroceso")
        self.assertEqual(motor.estado_vista().arma_tipo, "daga")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "equipo.bin")
            guardar_estado(estado, ruta)
            motor.ejecutar("soltar", "coraza")
            motor.restaurar_estado(cargar_estado(ruta))
        self.assertEqual((motor.estado_vista().arma_tipo, motor.estado_vista().armadura_tipo), ("daga", "coraza"))

    def test_anclajes_siguen_actor_y_recogida_desaparece(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [100, 200]
        a = AnimacionEscena(root, canvas)
        a.anclar(2, 1, (10, -20), duracion=45)
        canvas.coords.assert_called_with(2, 110, 180)
        a.anclar(3, 1, (30, -10), ocultar_hasta=45)
        canvas.itemconfig.assert_called_with(3, state="hidden")
        a.paso = 45
        a._actualizar_anclajes()
        canvas.delete.assert_called_with(2)
        canvas.itemconfig.assert_called_with(3, state="normal")
        a.detener()
        self.assertEqual(a.anclajes, [])

    def test_anclaje_cambia_con_pose_y_vuelve_al_reposo(self):
        root, canvas = Mock(), Mock()
        canvas.coords.return_value = [100, 200]
        a = AnimacionEscena(root, canvas)
        a.secuencia(1, ["paso1", "paso2"], reposo="quieto")
        a.anclar(2, 1, (10, -20), [(20, -30), (40, -50)])
        canvas.coords.assert_called_with(2, 120, 170)
        a.paso = 3
        a._actualizar_anclajes()
        canvas.coords.assert_called_with(2, 140, 150)
        a.paso = 6
        a._actualizar_anclajes()
        canvas.coords.assert_called_with(2, 110, 180)

    def test_interfaz_equipo_y_recogida_no_alteran_simulacion(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        datos._inventario("daga")
        datos._inventario("coraza")
        datos._suelo("pocion")
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        original = vista.recursos.imagen
        equivalencias = {"daga": "itm_daga_oxidada", "coraza": "itm_coraza_cuero", "pocion": "itm_pocion_menor"}
        try:
            vista.root.withdraw()
            with patch.object(vista.recursos, "imagen", side_effect=lambda n, w, h: original(equivalencias.get(n, n), w, h)):
                datos.motor.ejecutar("equipar", "daga")
                datos.motor.ejecutar("equipar", "coraza")
                vista.mostrar_estado(datos.motor.estado_vista(), [])
                self.assertTrue(vista.canvas.find_withtag("arma_visible"))
                self.assertTrue(vista.canvas.find_withtag("armadura_visible"))
                datos.motor.ejecutar("recoger", "pocion")
                vista.preparar_animacion("recoger")
                vista.mostrar_estado(datos.motor.estado_vista(), [])
                self.assertTrue(vista.canvas.find_withtag("objeto_recogido"))
                antes = datos.motor.exportar_estado()
                vista.root.after(120, vista.root.quit)
                vista.root.mainloop()
                # El limite se prueba por pasos; la carga del equipo no altera el resultado.
                vista.escena.animacion.paso = 45
                vista.escena.animacion._actualizar_anclajes()
                self.assertFalse(vista.canvas.find_withtag("objeto_recogido"))
                arma = vista.canvas.find_withtag("arma_visible")[0]
                self.assertEqual(vista.canvas.itemcget(arma, "state"), "normal")
                self.assertEqual(datos.motor.exportar_estado(), antes)
                self.assertEqual(vista._cola, [])
                vista.var_movimiento.set(False)
                vista._alternar_movimiento()
                self.assertIsNone(vista.escena.animacion)
                self.assertTrue(vista.canvas.find_withtag("armadura_visible"))
                self.assertFalse(vista.canvas.find_withtag("objeto_recogido"))
        finally:
            vista.cerrar()
