"""VD-01: privacidad, validación y cancelación real del diálogo temático."""
import tkinter as tk
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from controlador.controlador import ControladorJuego
from tests.test_replay_grafico import grabacion
from vista.destino_viaje import DestinoViaje
from vista.grafica import VistaGrafica


PROYECCION=((10,2,'Entrada',()),(42,2,'Galería',()),
            (20,1,'NOMBRE OCULTO',()),(99,0,'SECRETO',()))


class DestinoViajeTest(unittest.TestCase):
    def setUp(self):
        try: self.v=VistaGrafica()
        except tk.TclError as e: self.skipTest(str(e))
        self.addCleanup(self.v.cerrar)
        self.v.root.geometry('1100x760'); self.v.root.update()

    def crear(self):
        d=DestinoViaje(self.v,PROYECCION,10)
        self.addCleanup(lambda:d.dialogo.destroy() if d.dialogo.winfo_exists() else None)
        return d

    def test_privacidad_y_validacion_no_distinguen_destinos_no_permitidos(self):
        d=self.crear()
        opciones=' '.join(d.lista.get(0,'end'))
        self.assertIn('Galería',opciones)
        for oculto in ('OCULTO','SECRETO','20','99'): self.assertNotIn(oculto,opciones)
        for texto in ('', 'abc','-1','1.5'):
            d.numero.set(texto); d.aceptar()
            self.assertIsNone(d.resultado)
            self.assertTrue(d.dialogo.winfo_exists())
        errores=[]
        for texto in ('20','99','123456','9'*100):
            d.numero.set(texto); d.aceptar(); errores.append(d.error.get())
            self.assertIsNone(d.resultado)
        self.assertEqual(len(set(errores)),1)

    def test_seleccion_enter_y_foco_confirman_id_explorado(self):
        d=self.crear()
        def elegir():
            d.lista.selection_set(1); d.seleccionar()
            self.assertEqual(d.numero.get(),'42')
            self.assertIn('Galería',d.detalle.get())
            d.entrada.focus_force(); self.v.root.update()
            d.entrada.event_generate('<Return>')
        self.v.root.after(100,elegir)
        self.assertEqual(d.mostrar(),42)

    def test_cancelar_escape_y_cierre_conservan_cola(self):
        for accion in ('boton','escape','cerrar'):
            with self.subTest(accion=accion):
                d=self.crear(); self.v._cola[:]=['inv']
                def cancelar():
                    self.v.root.update(); self.v._enviar('esperar')
                    d.entrada.focus_force(); self.v.root.update()
                    if accion=='escape': d.entrada.event_generate('<Escape>')
                    elif accion=='cerrar': d.dialogo.tk.call(d.dialogo.protocol('WM_DELETE_WINDOW'))
                    else: d.boton_cancelar.invoke()
                self.v.root.after(100,cancelar)
                self.assertIsNone(d.mostrar())
                self.assertEqual(self.v._cola,['inv'])
                self.assertFalse(self.v._en_menu)

    def test_controles_caben_y_botones_estan_en_espanol(self):
        d=self.crear()
        d.dialogo.deiconify(); self.v.root.update()
        self.assertEqual(d.dialogo.title(),'Viajar a una sala')
        self.assertEqual(d.boton_viajar.cget('text'),'Viajar')
        self.assertEqual(d.boton_cancelar.cget('text'),'Cancelar')
        for widget in (d.lista,d.entrada,d.boton_cancelar,d.boton_viajar):
            self.assertTrue(widget.winfo_viewable())
            self.assertLessEqual(widget.winfo_rooty()+widget.winfo_height(),
                d.dialogo.winfo_rooty()+d.dialogo.winfo_height())

    def test_cerrar_principal_con_dialogo_abierto_cancela_sin_cerrar_partida(self):
        self.v._cola[:]=['inv']
        self.v.root.after(100,self.v._al_cerrar)
        self.assertIsNone(self.v.pedir_destino(PROYECCION,10))
        self.assertFalse(self.v._cerrada)
        self.assertEqual(self.v._cola,['inv'])


class DestinoControlTest(unittest.TestCase):
    def test_cancelar_conserva_viaje_estado_archivos_y_aceptar_usa_flujo_normal(self):
        class Vista:
            respuesta=None
            def pedir_destino(self,p,actual): self.recibido=(p,actual); return self.respuesta
        with grabacion() as (raiz,j,ruta,guardado,nueva):
            v=Vista(); c=ControladorJuego(j,v,ruta_replay=str(ruta))
            c._viaje_activo=True; c.control_viaje=Mock()
            antes=(j.exportar_estado(),ruta.read_bytes(),guardado.read_bytes())
            c.procesar_comando('viajar')
            self.assertTrue(c._viaje_activo)
            c.control_viaje.cancelar.assert_not_called()
            self.assertEqual((j.exportar_estado(),ruta.read_bytes(),guardado.read_bytes()),antes)
            self.assertEqual(v.recibido,(j.mapa_conocido(),j.jugador.posicion_actual))
            v.respuesta=100
            from unittest.mock import patch
            with patch.object(c,'_viaje') as viajar:
                c.procesar_comando('viajar')
            viajar.assert_called_once_with(['a','100'])
