"""RE-02/03: contenido inédito, WAV reales y animación de cazadores."""
import os
import tempfile
import tkinter as tk
import unittest
import wave
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from controlador.controlador import ControladorJuego
from datos.almacen import AlmacenLocal
from modelo.juego import crear_juego
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.test_verificacion_entrega import CriptaDesconocida
from vista.grafica import VistaGrafica
from vista.sonidos import Sonidos


class RevisionEntregaVisualTest(unittest.TestCase):
    def setUp(self):
        try:
            self.vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.vista.cerrar)
        self.vista.root.withdraw()
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        catalogo = GestorCatalogo(CriptaDesconocida(17), CacheCatalogoOrdenado(25),
                                 AlmacenLocal(self.temporal.name))
        self.precarga = GestorPrecarga(catalogo.cliente, catalogo)
        self.addCleanup(self.precarga.cerrar)
        self.motor = crear_juego(self.precarga, 'cripta-inedita-revision', 12345,
                                partida_completa=True)

    def test_re02_objeto_nuevo_conserva_interrogacion_y_sonido_desde_otro_cwd(self):
        v, motor = self.vista, self.motor
        reproducciones = []
        def reproducir(ruta, flags):
            if ruta is None:
                return
            with wave.open(ruta, 'rb') as wav:
                self.assertGreater(wav.getnframes(), 0)
                self.assertEqual(wav.getframerate(), 22050)
            reproducciones.append((Path(ruta).stem, flags))
        backend = SimpleNamespace(PlaySound=reproducir, SND_FILENAME=1,
                                  SND_ASYNC=2, SND_NODEFAULT=4)
        v.sonidos.cerrar()
        v.sonidos = Sonidos(backend)
        v.sonidos.habilitar(True)
        control = ControladorJuego(motor, v, ruta_replay=str(Path(self.temporal.name)/'partida.log'))
        control.bitacora_replay = Mock()
        cwd = Path.cwd()
        try:
            os.chdir(self.temporal.name)
            v.mostrar_estado(motor.estado_vista(), [])
            iconos = [item for item in v.canvas.find_withtag('objeto_0') if v.canvas.type(item)=='image']
            self.assertTrue(iconos)
            for item in iconos:
                self.assertIn(v.canvas.itemcget(item, 'image'),
                              [str(imagen) for _, imagen in v.recursos._neutras])
            arma = next(o for o in motor.objetos_en_suelo[100] if o.tipo_catalogo == 'arma_nueva')
            self.assertTrue(control._accion_modelo('recoger', arma.id_instancia))
            self.assertTrue(control._accion_modelo('equipar', arma.id_instancia))
            v.mostrar_estado(motor.estado_vista(), [])
            v.mostrar_inventario(motor.inventario_vista())
            v.lista.selection_set(0)
            v._mostrar_detalle()
            self.assertIs(v._imagen_detalle, v.recursos.imagen_neutra(52, 52))
            self.assertEqual([nombre for nombre, _ in reproducciones], ['recoger', 'equipar'])
            self.assertTrue(all(flags == 7 for _, flags in reproducciones))
            self.assertTrue(v.sonidos.activo)
            v.var_sonido.set(True)
            v.reiniciar_presentacion()
            self.assertTrue(control._accion_modelo('mover', 'E'))
            self.assertEqual(reproducciones[-1][0], 'mover')
        finally:
            os.chdir(cwd)

    def test_re03_cazadores_animan_reposo_y_dano_sin_cambiar_modelo(self):
        v, motor = self.vista, self.motor
        self.assertTrue(motor.ejecutar('mover', 'E').ok)
        base = motor.estado_vista()
        antes = motor.exportar_estado()
        for tipo in ('ent_sabueso_oseo', 'ent_espectro_acechador', 'cazador-inedito'):
            with self.subTest(tipo=tipo):
                enemigo = replace(base.enemigos[0], tipo=tipo, comportamiento='cazador')
                estado = replace(base, enemigos=[enemigo])
                v._movimiento_activo = True
                v.mostrar_estado(estado, [])
                sprite = next(i for i in v.canvas.find_withtag('enemigo_0') if v.canvas.type(i)=='image')
                reposo = v.canvas.coords(sprite)
                v.escena.animacion.situar(20)
                self.assertNotEqual(v.canvas.coords(sprite), reposo)
                v.mostrar_estado(replace(estado, enemigos=[replace(enemigo, vida=enemigo.vida-1)]), [])
                self.assertTrue(any(a[0] == next(i for i in v.canvas.find_withtag('enemigo_0')
                    if v.canvas.type(i)=='image') and a[4] for a in v.escena.animacion.actores))
                v._movimiento_activo = False
                v.mostrar_estado(estado, [])
                self.assertTrue(any(v.canvas.type(i)=='image' for i in v.canvas.find_withtag('enemigo_0')))
                self.assertEqual(motor.exportar_estado(), antes)
