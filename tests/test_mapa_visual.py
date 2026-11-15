"""VI-01..04: privacidad del dibujo, controles y delegación de viaje."""
from copy import deepcopy
from unittest import TestCase
from unittest.mock import Mock, patch
import tkinter as tk
from vista.mapa_visual import preparar_cartografia, VentanaMapa
from vista.recursos_graficos import RecursosGraficos
from controlador.controlador import ControladorJuego
from tests import test_controlador_ac_real as integrada


def proyeccion():
    return ((10, 2, 'Entrada', (('E', 9000, 70, 7, False), ('N', 42, 100, None, False))),
            (9000, 2, 'Galería', (('O', 10, 70, 7, False),)),
            (42, 1, 'NOMBRE OCULTO', (('S', 777, 30, None, False),)),
            (777, 0, 'SECRETO', (('N', 10, 99, None, False),)))


class CartografiaTest(TestCase):
    def test_nunca_incluye_datos_ocultos(self):
        p = proyeccion()
        antes = deepcopy(p)
        dibujo = preparar_cartografia(p, 10)
        self.assertEqual([r[0] for r in dibujo.registros], [10, 42, 9000])
        self.assertEqual(dibujo.registros[1], (42, 1, None, ()))
        self.assertNotIn('OCULTO', repr(dibujo))
        self.assertNotIn('SECRETO', repr(dibujo))
        self.assertNotIn('777', repr(dibujo))
        self.assertEqual(p, antes)

    def test_disposicion_determinista_sin_inventar_salidas(self):
        p = ((2**32-1, 2, 'Lejana', ()), (1, 2, 'Origen', (('N', 2**32-1, 1, None, False),)),
             (99, 2, 'Isla', ()))
        a = preparar_cartografia(p, 1)
        b = preparar_cartografia(tuple(reversed(p)), 1)
        self.assertEqual(a, b)
        self.assertEqual(len(a.conexiones), 1)
        self.assertEqual(len(a.posiciones), 3)
        self.assertEqual(len({p for p in a.posiciones}), 3)

    def test_ciclos_y_mapa_grande_no_superponen_nodos(self):
        p = tuple((i, 2, f'Sala {i}', (('E', (i+1) % 1000, 100, None, False),)) for i in range(1000))
        dibujo = preparar_cartografia(p, 0)
        self.assertEqual(len(dibujo.posiciones), 1000)
        self.assertEqual(len(set(dibujo.posiciones)), 1000)
        self.assertEqual(len(dibujo.conexiones), 1000)

    def test_delega_proyeccion_sin_alterar_estado_ni_hacer_http(self):
        class VistaMapa:
            def mostrar_mapa(self, p, actual, destino):
                self.recibido = (p, actual, destino)
        with integrada.ControladorACRealTest.partida(self) as (motor, juego, _, __, ___, ____):
            vista = VistaMapa()
            control = ControladorJuego(juego, vista)
            antes = juego.exportar_estado()
            with patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP en mapa')):
                control.procesar_comando('mapa')
            self.assertEqual(vista.recibido, (motor.mapa_conocido(), motor.jugador.posicion_actual, None))
            self.assertEqual(juego.exportar_estado(), antes)


class MapaGUITest(TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as e:
            self.skipTest(str(e))
        self.root.withdraw()
        self.addCleanup(self.root.destroy)

    def crear(self):
        mapa = VentanaMapa(self.root, proyeccion(), 10, 9000)
        self.addCleanup(lambda: mapa.cerrar() if mapa.ventana.winfo_exists() else None)
        self.root.update()
        return mapa

    def test_niebla_listado_y_zoom_no_filtran_informacion(self):
        mapa = self.crear()
        self.assertTrue(mapa.canvas.find_withtag('niebla'))
        mapa.ampliar(.15)
        mapa.centrar()
        mapa.alternar_texto()
        texto = mapa.texto.get('1.0', 'end')
        self.assertIn('Avistada (?)', texto)
        self.assertIn('costo 70', texto)
        self.assertNotIn('OCULTO', texto)
        self.assertNotIn('777', texto)
        mapa.alternar_texto()
        self.assertIsNone(mapa.comando)

    def test_viaje_solo_emite_comando_hacia_explorada(self):
        mapa = self.crear()
        mapa.seleccionar(1)  # avistada 42
        self.assertEqual(str(mapa.boton_viajar['state']), 'disabled')
        mapa.viajar()
        self.assertIsNone(mapa.comando)
        mapa.seleccionar(2)
        self.assertEqual(str(mapa.boton_viajar['state']), 'normal')
        mapa.viajar()
        self.assertEqual(mapa.comando, 'ir a 9000')

    def test_cazador_tiene_alpha_cache_y_respaldo_por_comportamiento(self):
        from PIL import Image
        recursos = RecursosGraficos(self.root)
        with Image.open(recursos.carpeta / 'cazador_ilustrado.png') as im:
            self.assertEqual(im.mode, 'RGBA')
            self.assertEqual(im.getpixel((0, 0))[3], 0)
        a = recursos.imagen_enemigo('ent_sabueso_oseo', 'cazador', 205, 140)
        b = recursos.imagen_enemigo('tipo-nuevo-del-servidor', 'cazador', 205, 140)
        self.assertIs(a, b)
        self.assertGreater(a.width(), 96)  # No es el signo genérico.
        self.assertLessEqual(a.height(), 140)
        for tipo, comportamiento in (('ent_espectro_acechador', 'cazador'), ('ent_carcelero_errante', 'errante')):
            propia = recursos.imagen_enemigo(tipo, comportamiento, 205, 140)
            self.assertIsNot(propia, a)
            self.assertGreater(propia.height(), 96)
