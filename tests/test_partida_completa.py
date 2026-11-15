"""IA-01..06: aceptación de producción, sin sustituir reglas del motor."""
from unittest import TestCase
from tests import test_controlador_ac_real as base
from modelo.conocimiento import EXPLORADA
from modelo.tipos import ObjetoInstancia
from datos.guardado_binario import cargar_estado_partida


class PartidaCompletaTest(TestCase):
    partida = base.ControladorACRealTest.partida

    def test_ia05_antorcha_revela_sin_activar_vecina_y_revierte(self):
        with self.partida(mapa=True) as (motor, juego, control, vista, raiz, precarga):
            precarga.catalogo.almacen.guardar_ficha('cat1', {
                'id': 'antorcha-local', 'clase': 'antorcha', 'nombre': 'Luz', 'duracion': 1000})
            motor.objetos_en_suelo[100].append(ObjetoInstancia('luz', 'antorcha-local', 'suelo', 100))
            self.assertTrue(juego.ejecutar('recoger', 'luz').ok)
            self.assertTrue(juego.ejecutar('usar', 'luz').ok)
            antes = motor.mapa_conocido()
            self.assertTrue(juego.ejecutar('mover', 'E').ok)
            self.assertEqual(motor._conocimiento.estado_sala(102), EXPLORADA)
            self.assertFalse(motor.contenido_cargado[102])
            self.assertFalse(motor.enemigos_por_sala[102])
            motor.jugador.inventario.recoger(ObjetoInstancia('p', 'pergamino-d', 'inventario'))
            self.assertTrue(juego.ejecutar('retroceso').ok)
            self.assertEqual(motor.mapa_conocido(), antes)
            self.assertEqual(motor.jugador.inventario.contar('pergamino-d'), 0)

    def test_ia02_inventario_equipo_cursor_y_carga(self):
        with self.partida(mapa=True) as (motor, juego, control, vista, raiz, _):
            instancia = motor.objetos_en_suelo[100][0].id_instancia
            for accion in ('recoger', 'equipar'):
                self.assertTrue(juego.ejecutar(accion, instancia).ok)
            guardado = juego.exportar_estado()
            ruta = raiz / 'partida.bin'
            control.procesar_comando(f'guardar "{ruta}"')
            self.assertEqual(cargar_estado_partida(ruta), guardado)
            self.assertTrue(juego.ejecutar('soltar', instancia).ok)
            control.procesar_comando(f'cargar "{ruta}"')
            vista.mostrar_error.assert_not_called()
            self.assertEqual(juego.exportar_estado(), guardado)
            self.assertEqual(motor.jugador.inventario.cursor.objeto.id_instancia, instancia)

    def test_ia06_movimiento_entrega_enemigos_y_dano(self):
        with self.partida(mapa=True) as (motor, juego, _, __, ___, ____):
            resultado = juego.ejecutar('mover', 'E')
            self.assertTrue(resultado.hechos_paso.aceptado)
            self.assertTrue(resultado.hechos_paso.hubo_entrada)
            self.assertTrue(resultado.hechos_paso.enemigos_al_entrar)
            self.assertTrue(resultado.hechos_paso.recibio_dano)

    def test_ia02_seleccion_gratuita_no_rompe_la_siguiente_accion(self):
        with self.partida(mapa=True) as (motor, juego, _, __, ___, ____):
            primero = motor.objetos_en_suelo[100][0]
            segundo = ObjetoInstancia('otro', primero.tipo_catalogo, 'suelo', 100)
            motor.objetos_en_suelo[100].append(segundo)
            self.assertTrue(juego.ejecutar('recoger', primero.id_instancia).ok)
            self.assertTrue(juego.ejecutar('recoger', segundo.id_instancia).ok)
            motor.jugador.inventario.seleccionar(segundo.id_instancia)
            self.assertTrue(juego.ejecutar('soltar', segundo.id_instancia).ok)
            self.assertEqual(motor.jugador.inventario.tamaño, 1)

    def test_ia02_explorar_no_copia_el_mapa_completo_por_evento(self):
        from unittest.mock import patch
        with self.partida(mapa=True) as (motor, juego, _, __, ___, ____):
            with patch.object(motor._conocimiento, 'mapa_conocido',
                              side_effect=AssertionError('No copiar mapa durante un turno')):
                self.assertTrue(juego.ejecutar('mover', 'E').ok)
