"""RP-01..04: entradas GUI, fábrica completa, cargas/retroceso y CLI separados."""
import io
import tkinter as tk
import unittest
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

import main
from controlador.aplicacion import ejecutar_juego
from controlador.controlador import ControladorJuego
from controlador.partida_historica import integrar_historia
from controlador.replay import ReproductorReplay
from controlador.resumen_historia import resumir
from datos.bitacora_replay import BitacoraReplay
from datos.guardado_binario import guardar_estado
from datos.offline import ClienteOffline
from modelo.juego import crear_juego
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import crear_paquete
from vista.grafica import VistaGrafica


class VistaRegistrada:
    def __init__(self, detener=None):
        self.pasos=[]; self.animaciones=[]; self.errores=[]; self.fin=None
        self.detener=detener; self.cerrada=False; self.tareas=0
    def modo_replay(self): self.replay=True
    def establecer_titulo_replay(self,titulo): self.titulo=titulo
    def ejecutar_tarea(self,f,*args,**kwargs):
        self.tareas+=1
        return f(*args,**kwargs)
    def mostrar_replay_paso(self,e,m,p,total,inventario=None):
        self.pasos.append((deepcopy(e),p,total,deepcopy(inventario)))
        return p!=self.detener
    def preparar_animacion(self,accion,*args): self.animaciones.append(accion)
    def mostrar_error_replay(self,texto): self.errores.append(texto)
    def mostrar_fin(self,resumen): self.fin=resumen
    def cerrar(self): self.cerrada=True


@contextmanager
def grabacion():
    with TemporaryDirectory() as carpeta:
        raiz=Path(carpeta); paquete=raiz/'paquete'
        almacen=crear_paquete(paquete,salas=3)
        almacen.guardar_ficha('cat1',{'id':'perg-rp','clase':'pergamino_retroceso','nombre':'Pergamino'})
        pagina=almacen.leer_pagina('prueba','v1',1)
        for s in pagina['salas']:
            for salida in s['salidas'].values(): salida['costo']=250
            almacen.guardar_contenido('prueba','v1',dict(sala=s['id'],enemigos=[],trampas=[],
                objetos=['perg-rp'] if s['id']==100 else []))
        almacen.guardar_pagina('prueba','v1',pagina)
        precargas=[]
        def nueva():
            c=ClienteOffline(paquete)
            p=GestorPrecarga(c,GestorCatalogo(c,CacheCatalogoOrdenado(25),c.almacen))
            precargas.append(p)
            return p
        try:
            original=integrar_historia(crear_juego(nueva(),'prueba',42,partida_completa=True),2)
            ruta=raiz/'partida.log'; log=BitacoraReplay(ruta); log.iniciar(original.meta)
            def actuar(accion,arg=None):
                assert original.ejecutar(accion,arg).ok
                log.registrar_accion(accion,arg)
            perg=original.objetos_en_suelo[100][0].id_instancia
            actuar('recoger',perg); actuar('mover','E'); actuar('retroceso')
            estado=original.exportar_estado()
            guardado=raiz/'partida.bin'; guardar_estado(estado,guardado)
            actuar('esperar')
            original.restaurar_estado(estado); log.registrar_carga(estado)
            actuar('mover','E')
            yield raiz,original,ruta,guardado,nueva
        finally:
            for p in precargas: p.cerrar()


class ReplayGraficoTest(unittest.TestCase):
    def test_fabrica_grafica_completa_cargas_retroceso_y_archivos_intactos(self):
        with grabacion() as (raiz,original,ruta,guardado,nueva):
            antes=(original.exportar_estado(),ruta.read_bytes(),guardado.read_bytes())
            vista=VistaRegistrada(); juegos=[]
            fabrica=crear_juego
            def registrar(*a,**k):
                juego=fabrica(*a,**k); juegos.append(juego); return juego
            args=SimpleNamespace(replay_grafico=str(ruta),checkpoint_cada=2)
            with patch('vista.grafica.VistaGrafica',return_value=vista), \
                 patch('modelo.juego.crear_juego',side_effect=registrar), \
                 patch('requests.sessions.Session.request',side_effect=AssertionError('HTTP')):
                self.assertEqual(main.ejecutar_replay_grafico(args,nueva()),0)
            self.assertEqual(vista.errores,[])
            self.assertTrue(vista.cerrada)
            self.assertEqual([p[1] for p in vista.pasos],list(range(7)))
            self.assertEqual(vista.animaciones,['recoger','mover','retroceso','esperar','cargar','mover'])
            self.assertEqual(vista.pasos[-1][0],original.estado_vista())
            self.assertEqual(vista.pasos[-1][3],original.inventario_vista())
            self.assertEqual(vista.pasos[-1][0].salidas[0].costo,250)
            self.assertIsNotNone(juegos[0]._historia_h3)
            from dataclasses import replace
            from datos.historia_binaria import codificar_historia
            self.assertEqual(replace(juegos[0].exportar_estado(),
                historia=codificar_historia(juegos[0]._historia_h3)),original.exportar_estado())
            self.assertEqual((original.exportar_estado(),ruta.read_bytes(),guardado.read_bytes()),antes)

    def test_modo_cli_sigue_sin_vista_y_hasta_conserva_historia(self):
        with grabacion() as (raiz,original,ruta,guardado,nueva):
            for extra in ([],['--hasta','0']):
                salida=io.StringIO()
                with redirect_stdout(salida), \
                     patch('vista.grafica.VistaGrafica',side_effect=AssertionError('vista en CLI')):
                    self.assertEqual(main.main(['--replay',str(ruta),'--offline',str(raiz/'paquete'),
                        '--datos-dir',str(raiz/'paquete'),'--checkpoint-cada','2',*extra]),0)
                if not extra:
                    self.assertEqual(salida.getvalue().strip(),resumir(original.linea_tiempo.consultar_final()))
                else: self.assertIn('Historia t=0',salida.getvalue())

    def test_detener_no_ejecuta_acciones_y_cierra_sin_error(self):
        with grabacion() as (_,original,ruta,guardado,nueva):
            vista=VistaRegistrada(detener=0)
            with patch('vista.grafica.VistaGrafica',return_value=vista):
                self.assertEqual(main.ejecutar_replay_grafico(
                    SimpleNamespace(replay_grafico=str(ruta),checkpoint_cada=2),nueva()),0)
            self.assertEqual(vista.animaciones,[])
            self.assertIsNone(vista.fin)
            self.assertTrue(vista.cerrada)

    def test_errores_de_archivo_version_y_accion_se_informan(self):
        with grabacion() as (_,original,ruta,guardado,nueva):
            for caso in ('archivo','version','accion'):
                vista=VistaRegistrada()
                copia=ruta.with_name(caso+'.log'); contenido=ruta.read_text(encoding='utf-8')
                if caso=='archivo': contenido='invalido'
                if caso=='version': contenido=contenido.replace('"v1"','"version-inexistente"')
                if caso=='accion': contenido+='{"tipo":"accion","accion":"mover","argumento":"N"}\n'
                copia.write_text(contenido,encoding='utf-8')
                with self.subTest(caso=caso),patch('vista.grafica.VistaGrafica',return_value=vista):
                    self.assertEqual(main.ejecutar_replay_grafico(
                        SimpleNamespace(replay_grafico=str(copia),checkpoint_cada=2),nueva()),1)
                self.assertTrue(vista.errores)
                self.assertTrue(vista.cerrada)

    def test_parser_separa_grafico_de_cli_hasta_y_otros_modos(self):
        for opciones in (['--replay-grafico','x','--hasta','1'],['--replay','x','--replay-grafico','y'],
                         ['--replay-grafico','x','--gui'],['--replay-grafico','x','--verificar','y']):
            with self.subTest(opciones=opciones),redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                main.leer_argumentos(opciones)


class LanzadorGraficoTest(unittest.TestCase):
    def test_menu_y_partida_lanzan_proceso_grafico_sin_informe_ni_mutacion(self):
        with grabacion() as (raiz,original,ruta,guardado,nueva):
            args=main.leer_argumentos(['--gui','--offline',str(raiz/'paquete'),
                                      '--datos-dir',str(raiz/'paquete')])
            vista=Mock(spec=VistaGrafica)
            def menu(replay,puntajes): replay(); return 'salir',None
            vista.mostrar_menu.side_effect=menu
            lanzar=main.crear_lanzador_replay(args)
            antes=(original.exportar_estado(),ruta.read_bytes(),guardado.read_bytes())
            with patch('main.subprocess.Popen') as proceso, \
                 patch('main.subprocess.run',side_effect=AssertionError('CLI desde GUI')), \
                 patch('controlador.aplicacion.RUTA_REPLAY_PREDETERMINADA',str(ruta)), \
                 patch('vista.grafica.VistaGrafica',return_value=vista):
                self.assertEqual(ejecutar_juego(args,Mock(),lanzar),0)
                c=ControladorJuego(original,vista,ruta_replay=str(ruta),lanzador_replay=lanzar)
                c._replay([])
            self.assertEqual(proceso.call_count,2)
            for llamada in proceso.call_args_list:
                comando=llamada.args[0]
                self.assertIn('--replay-grafico',comando)
                self.assertNotIn('--replay',comando)
                self.assertIn(str(ruta),comando)
                self.assertIn(str(raiz/'paquete'),comando)
            vista.mostrar_informe.assert_not_called()
            self.assertEqual((original.exportar_estado(),ruta.read_bytes(),guardado.read_bytes()),antes)


class ControlesReplayGUITest(unittest.TestCase):
    def test_pausa_velocidad_detener_y_cierre_solo_de_replay(self):
        try: v=VistaGrafica()
        except tk.TclError as e: self.skipTest(str(e))
        self.addCleanup(v.cerrar)
        v.root.geometry('1100x760'); v.root.update(); v.modo_replay(); v.root.update()
        with grabacion() as (_,j,ruta,guardado,nueva):
            v.var_vel.set('rápido')
            self.assertEqual(v._pausa_replay(),.2)
            v.root.after(30,v._replay_alternar_pausa)
            v.root.after(60,lambda:v.var_vel.set('lento'))
            v.root.after(100,v._replay_parar)
            self.assertFalse(v.mostrar_replay_paso(j.estado_vista(),[],0,3,j.inventario_vista()))
            self.assertTrue(v._replay_pausado)
            self.assertEqual(v._pausa_replay(),1.4)
            self.assertTrue(v.barra_replay.winfo_ismapped())
            self.assertLess(v.barra_replay.winfo_y(),v.lbl_tiempo.winfo_y())
            for control in v.barra_replay.winfo_children():
                self.assertLessEqual(control.winfo_rooty()+control.winfo_height(),
                    v.root.winfo_rooty()+v.root.winfo_height())
            v._enviar('mover N'); self.assertEqual(v._cola,[])
            v._al_cerrar(); self.assertTrue(v._cerrada)
