"""UX-01..03: abandono cancelable, reinicio y victoria por puerta física."""
import tkinter as tk
import unittest
import io
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from tests import test_regresiones_juego as base
from controlador.controlador import ControladorJuego
from vista.grafica import VistaGrafica
from vista.salida_partida import SalidaPartida


class SalidaControlTest(unittest.TestCase):
    def test_cancelar_no_toca_viaje_estado_log_o_guardado(self):
        datos = base.TestRegresionesJuego()
        datos.setUp()
        class Vista:
            def preguntar_salida(self): return 'cancelar'
        with TemporaryDirectory() as carpeta:
            log = Path(carpeta)/'partida.log'
            guardado = Path(carpeta)/'guardado.bin'
            guardado.write_bytes(b'guardado anterior')
            c = ControladorJuego(datos.motor, Vista(), ruta_replay=log)
            c.bitacora_replay.iniciar(datos.motor.meta)
            c._viaje_activo = True
            c.control_viaje = Mock()
            antes = datos.motor.exportar_estado(), log.read_bytes(), guardado.read_bytes()
            c.procesar_comando('salir')
            self.assertTrue(c.ejecutando)
            self.assertTrue(c._viaje_activo)
            c.control_viaje.cancelar.assert_not_called()
            self.assertEqual((datos.motor.exportar_estado(), log.read_bytes(), guardado.read_bytes()), antes)

    def test_elecciones_explicitas_marcan_solo_su_destino(self):
        class Vista:
            def preguntar_salida(self): return self.accion
            def marcar_volver_menu(self): self.menu = True
            def marcar_reinicio(self): self.reinicio = True
        for accion in ('menu','reiniciar','terminar'):
            with self.subTest(accion=accion):
                d = base.TestRegresionesJuego(); d.setUp()
                v = Vista(); v.accion = accion
                c = ControladorJuego(d.motor, v)
                antes = d.motor.exportar_estado()
                c.procesar_comando('salir')
                self.assertFalse(c.ejecutando)
                self.assertEqual(c.reiniciar_solicitado, accion=='reiniciar')
                self.assertEqual(getattr(v,'menu',False), accion=='menu')
                self.assertEqual(getattr(v,'reinicio',False), accion=='reiniciar')
                self.assertEqual(d.motor.exportar_estado(), antes)

    def test_abrir_desde_sala_de_salida_acredita_la_misma_puerta(self):
        d = base.TestRegresionesJuego(); d.setUp()
        d.motor.jugador.posicion_actual = 2
        d.motor.salas[2].salidas['O']['cerrada'] = True
        d._inventario('llave')
        d._accion('abrir','O')
        from datos.guardado_binario import guardar_estado, cargar_estado
        with TemporaryDirectory() as carpeta:
            ruta=Path(carpeta)/'puerta.bin'
            guardar_estado(d.motor.exportar_estado(),ruta)
            d.motor.restaurar_estado(cargar_estado(ruta))
        d._accion('mover','O')
        d._accion('mover','E')
        self.assertEqual(d.motor.resultado, 'victoria')

    def test_objetivo_respeta_mapa_y_explicita_apertura_y_cruce(self):
        from tests.datos_terreno_cazador import motor_terreno
        with motor_terreno(completa=True) as m:
            self.assertNotIn(str(m.sala_salida), m.estado_vista().objetivo)
        d=base.TestRegresionesJuego(); d.setUp()
        self.assertIn('abre E',d.motor.estado_vista().objetivo)
        d._inventario('llave'); d._accion('abrir','E')
        self.assertIn('cruza E',d.motor.estado_vista().objetivo)


class SalidaGUITest(unittest.TestCase):
    def setUp(self):
        try: self.v = VistaGrafica()
        except tk.TclError as error: self.skipTest(str(error))
        self.addCleanup(self.v.cerrar)
        self.v.root.geometry('1100x760')
        self.v.root.update()

    def test_modal_cancelar_escape_y_cerrar_conservan_cola(self):
        for accion in ('cancelar','escape','cerrar'):
            with self.subTest(accion=accion):
                v=self.v; v._cola[:]=['inv']
                dialogo=SalidaPartida(v)
                def elegir():
                    v.root.update()
                    v._enviar('esperar')
                    if accion=='escape':
                        dialogo.dialogo.focus_force(); v.root.update()
                        dialogo.dialogo.event_generate('<Escape>')
                    elif accion=='cerrar': dialogo.dialogo.tk.call(dialogo.dialogo.protocol('WM_DELETE_WINDOW'))
                    else: dialogo.botones['cancelar'].invoke()
                v.root.after(100,elegir)
                self.assertEqual(dialogo.mostrar(),'cancelar')
                self.assertEqual(v._cola,['inv'])
                self.assertFalse(v._en_menu)

    def test_modal_reinicio_menu_y_terminar_no_emiten_acciones(self):
        for accion in ('reiniciar','menu','terminar'):
            dialogo=SalidaPartida(self.v)
            self.v.root.after(80,dialogo.botones[accion].invoke)
            self.assertEqual(dialogo.mostrar(),accion)
            self.assertEqual(self.v._cola,[])

    def test_cierre_principal_de_partida_activa_pide_eleccion(self):
        d=base.TestRegresionesJuego(); d.setUp()
        self.v.mostrar_estado(d.motor.estado_vista(),[])
        self.v._al_cerrar()
        self.assertFalse(self.v._cerrada)
        self.assertEqual(self.v._cola,['salir'])
        self.v._cola.clear()
        self.v._ocupada=True
        self.v._al_cerrar()
        self.assertEqual(self.v._cola,['salir'])
        self.assertFalse(self.v._cerrada)
        self.assertIn('abre E',self.v.var_objetivo.get())
        self.assertIn('prueba',self.v.var_sala.get())


class ReinicioAplicacionTest(unittest.TestCase):
    def test_reiniciar_partida_activa_renueva_motor_y_conserva_guardado(self):
        import main
        from tests.datos_prueba import crear_paquete
        from tests.datos_integracion_d import reporte_prueba
        v=Mock(spec=VistaGrafica)
        v.mostrar_menu.return_value=('jugar',None)
        v.preguntar_menu_principal.return_value=False
        v.preguntar_reinicio.return_value=True
        motores=[]
        def construir(**opciones):
            m=opciones['modelo']; motores.append(m)
            self.assertEqual(m.reloj,0)
            self.assertEqual(m.jugador.vida,m.jugador.vida_max)
            self.assertTrue(m.jugador.inventario.esta_vacio())
            self.assertEqual(m.meta.cripta_id,'prueba')
            self.assertEqual(m.meta.semilla,42)
            if len(motores)==1:
                m.jugador.vida-=3
            else:
                m.resultado='victoria'
            return Mock(reiniciar_solicitado=len(motores)==1)
        with TemporaryDirectory() as carpeta:
            crear_paquete(carpeta,salas=4)
            guardado=Path(carpeta)/'guardado.bin'; guardado.write_bytes(b'guardado existente')
            with patch('vista.grafica.VistaGrafica',return_value=v), \
                 patch('controlador.aplicacion.verificar',return_value=reporte_prueba()), \
                 patch('controlador.controlador.ControladorJuego',side_effect=construir), \
                 redirect_stdout(io.StringIO()):
                self.assertEqual(main.main(['--gui','--offline',carpeta,'--cripta','prueba',
                    '--datos-dir',carpeta,'--semilla','42']),0)
            self.assertEqual(guardado.read_bytes(),b'guardado existente')
        self.assertEqual(len(motores),2)
        self.assertIsNot(motores[0].gestor_precarga,motores[1].gestor_precarga)
        v.preguntar_reinicio.assert_called_once()
        v.mostrar_menu.assert_called_once()
