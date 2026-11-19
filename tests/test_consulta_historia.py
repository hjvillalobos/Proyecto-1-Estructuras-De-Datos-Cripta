"""FR-003/005/020: entradas de historia y cancelación sin acciones."""
import unittest
import tkinter as tk
from unittest.mock import Mock, patch

from vista.consulta_historia import ConsultaHistoria
from vista.grafica import VistaGrafica


class ConsultaHistoriaTest(unittest.TestCase):
    def test_rechaza_entradas_invalidas_y_accion_cero(self):
        dialogo = ConsultaHistoria.__new__(ConsultaHistoria)
        dialogo.numero, dialogo.modo, dialogo.error = Mock(), Mock(), Mock()
        for modo in ('tiempo', 'accion'):
            dialogo.modo.get.return_value = modo
            for texto in ('', '-1', '1.5', '#1', 'abc', '١', '9' * 19):
                with self.subTest(modo=modo, texto=texto):
                    dialogo.numero.get.return_value = texto
                    self.assertFalse(dialogo.validate())
            dialogo.numero.get.return_value = '0'
            self.assertEqual(dialogo.validate(), modo == 'tiempo')
            dialogo.numero.get.return_value = ' 3 '
            self.assertTrue(dialogo.validate())
            dialogo.apply()
            self.assertEqual(dialogo.result, '#3' if modo == 'accion' else '3')

    def test_cancelar_no_encola_y_error_restaura_estado_del_dialogo(self):
        vista = VistaGrafica.__new__(VistaGrafica)
        vista.root, vista._en_menu, vista._cola = Mock(), False, []
        with patch('vista.consulta_historia.ConsultaHistoria') as crear:
            crear.return_value.result = None
            vista._pedir_historia()
            self.assertEqual(vista._cola, [])
            self.assertFalse(vista._en_menu)
            crear.side_effect = RuntimeError('fallo de ventana')
            with self.assertRaises(RuntimeError):
                vista._pedir_historia()
            self.assertFalse(vista._en_menu)


class ConsultaHistoriaVentanaTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)

    def dialogo(self, reloj, acciones):
        with patch.object(ConsultaHistoria, 'wait_window'):
            dialogo = ConsultaHistoria(self.root, reloj=reloj, acciones=acciones)
        self.addCleanup(lambda: dialogo.destroy() if dialogo.winfo_exists() else None)
        return dialogo

    def test_hu01_contexto_sugerencias_y_limites_por_modo(self):
        dialogo = self.dialogo(200, 2)
        self.assertEqual(dialogo.numero.get(), '200')
        self.assertIn('0 a 200', dialogo.ejemplo.cget('text'))
        self.assertTrue(dialogo.validate())
        dialogo.numero.set('201')
        self.assertFalse(dialogo.validate())
        dialogo.modo.set('accion')
        dialogo.actualizar()
        self.assertEqual(dialogo.numero.get(), '2')
        self.assertIn('1 a 2', dialogo.ejemplo.cget('text'))
        dialogo.apply()
        self.assertEqual(dialogo.result, '#2')
        dialogo.numero.set('3')
        self.assertFalse(dialogo.validate())
        dialogo.modo.set('tiempo')
        dialogo.actualizar()
        self.assertEqual(dialogo.numero.get(), '200')

    def test_hu01_inicio_sin_acciones_y_reapertura_con_limites_nuevos(self):
        dialogo = self.dialogo(0, 0)
        self.assertTrue(dialogo.validate())
        dialogo.modo.set('accion')
        dialogo.actualizar()
        self.assertIn('Todavía no hay acciones', dialogo.ejemplo.cget('text'))
        dialogo.numero.set('1')
        self.assertFalse(dialogo.validate())
        dialogo.destroy()
        otro = self.dialogo(350, 4)
        self.assertEqual(otro.numero.get(), '350')
        otro.modo.set('accion')
        otro.actualizar()
        self.assertEqual(otro.numero.get(), '4')

    def test_hu01_boton_consulta_estados_distintos_sin_mutar_partida(self):
        from tests.test_controlador_ac_real import ControladorACRealTest
        from controlador.resumen_historia import consultar, detallar_partida
        with ControladorACRealTest().partida() as (motor, juego, control, _, raiz, __):
            control.procesar_comando('mover E')
            control.procesar_comando('esperar')
            vista = VistaGrafica()
            self.addCleanup(vista.cerrar)
            vista.root.withdraw()
            control.vista = vista
            control._mostrar_estado()
            antes = juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()
            self.assertEqual(vista._contexto_historia, (200, 2))
            textos = []
            for referencia in ('0', '200', '#1', '#2'):
                with self.subTest(referencia=referencia):
                    errores = []
                    def completar():
                        try:
                            dialogo = next(w for w in vista.root.winfo_children()
                                           if isinstance(w, ConsultaHistoria))
                            dialogo.modo.set('accion' if referencia.startswith('#') else 'tiempo')
                            dialogo.actualizar()
                            dialogo.numero.set(referencia.lstrip('#'))
                            dialogo.ok()
                        except Exception as error:
                            errores.append(error)
                            vista.cerrar()
                    vista.root.after(60, completar)
                    vista._pedir_historia()
                    self.assertEqual(errores, [])
                    self.assertEqual(vista._cola, ['historia ' + referencia])
                    with patch.object(vista, 'mostrar_informe') as mostrar:
                        control.procesar_comando(vista._cola.pop())
                    titulo, texto = mostrar.call_args.args
                    self.assertIn('acción ' + referencia if referencia.startswith('#') else 'tiempo ' + referencia, titulo)
                    self.assertEqual(texto, detallar_partida(consultar(juego.linea_tiempo, referencia), juego))
                    textos.append(texto)
                    self.assertEqual((juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()), antes)
            self.assertNotEqual(textos[0], textos[1])
            self.assertNotEqual(textos[2], textos[3])
            control.procesar_comando('esperar')
            control._mostrar_estado()
            self.assertEqual(vista._contexto_historia, (300, 3))
            guardado = raiz / 'historia.bin'
            control.procesar_comando(f'guardar "{guardado}"')
            control.procesar_comando('esperar')
            control._mostrar_estado()
            self.assertEqual(vista._contexto_historia, (400, 4))
            control.procesar_comando(f'cargar "{guardado}"')
            control._mostrar_estado()
            self.assertEqual(vista._contexto_historia, (300, 3))

    def test_hu01_resultado_permanece_visible_y_permite_volver(self):
        vista = VistaGrafica()
        self.addCleanup(vista.cerrar)
        vista.root.update_idletasks()
        resultados = []
        def comprobar():
            try:
                ventana = next(w for w in vista.root.winfo_children() if isinstance(w, tk.Toplevel))
                boton = next(w for w in ventana.winfo_children()
                             if isinstance(w, tk.ttk.Button) and w.cget('text') == 'Volver a la partida')
                resultados.append((ventana.winfo_rootx() >= 0, ventana.winfo_rooty() >= 0,
                                   bool(boton.winfo_ismapped()),
                                   boton.winfo_y() + boton.winfo_height() <= ventana.winfo_height()))
                boton.invoke()
            finally:
                for ventana in vista.root.winfo_children():
                    if isinstance(ventana, tk.Toplevel): ventana.destroy()
        vista.root.after(100, comprobar)
        vista.mostrar_informe('Historia · antes de la acción #200', 'Vida 29/30')
        self.assertEqual(resultados, [(True, True, True, True)])
