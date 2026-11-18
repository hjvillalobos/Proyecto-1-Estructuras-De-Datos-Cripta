"""HU-02: detalle pasado, privacidad, persistencia y continuidad antigua."""
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from controlador.resumen_historia import detallar, detallar_partida
from datos.historia_binaria import codificar_historia, decodificar_historia
from modelo.conocimiento_historia import campos_iniciales, convertir_cambios
from modelo.inventario_historia import campos_iniciales as inventario_inicial, CapturaInventario
from modelo.inventario import Inventario
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from modelo.tipos import ObjetoInstancia, FichaCatalogo
from tests.test_conocimiento import crear
from tests import test_controlador_ac_real as integracion


class HistoriaDetalladaTest(TestCase):
    def test_hu02_inventario_mapa_y_puertas_usan_el_pasado(self):
        mapa, inv = crear(), Inventario(4)
        for identidad in ('z', 'a'):
            inv.recoger(ObjetoInstancia(identidad, 'arma', 'suelo', 10))
        base = (('sala', (10, 'Entrada')), ('jugador', (20, 20, 5, 3, 100)),
                ('efectos', ()), ('estadisticas_partida', (0, None)))
        historia = LineaTiempo(EstadoHistorico(base + campos_iniciales(mapa) + inventario_inicial(inv)), 2)
        def ficha(tipo):
            return FichaCatalogo(tipo, 'arma', 'Espada histórica', {})
        pasado = detallar(historia.consultar_t(0), resolver_ficha=ficha,
                          mapa=mapa.mapa_historico(historia.consultar_t(0).estado))
        captura = CapturaInventario(inv)
        inv.seleccionar('a')
        inv.equipar_actual('arma')
        cambios = mapa.entrar(9000) + mapa.observar_puerta(9000, 7, True)
        historia.registrar_accion(100, captura.terminar() + convertir_cambios(cambios))
        historia.registrar_accion(200)
        consulta = historia.consultar_t(100)
        actual = detallar(consulta, resolver_ficha=ficha, mapa=mapa.mapa_historico(consulta.estado))
        self.assertLess(pasado.index('instancia: z'), pasado.index('instancia: a'))
        self.assertLess(actual.index('instancia: a'), actual.index('instancia: z'))
        self.assertIn('Espada histórica [arma]', actual)
        self.assertIn('equipado', actual)
        self.assertIn('Sala 9000: avistada', pasado)
        self.assertNotIn('Galería', pasado)
        self.assertNotIn('Secreto', pasado)
        self.assertNotIn('Sala 42:', pasado)
        self.assertIn('sin observar', pasado)
        self.assertIn('cerrada; último recuerdo', actual)
        self.assertIn('acciones 1', actual)
        self.assertNotIn('usos:', actual)
        antes = historia.exportar(), mapa.mapa_conocido(), tuple(inventario_inicial(inv))
        with patch('requests.sessions.Session.request', side_effect=AssertionError('HTTP')):
            consulta_pasada = historia.consultar_t(0)
            self.assertEqual(detallar(consulta_pasada, resolver_ficha=ficha,
                                     mapa=mapa.mapa_historico(consulta_pasada.estado)), pasado)
        self.assertEqual((historia.exportar(), mapa.mapa_conocido(), tuple(inventario_inicial(inv))), antes)

    def test_hu02_derrotados_resultado_binario_y_consulta_no_usan_el_vivo(self):
        with integracion.ControladorACRealTest().partida() as (motor, juego, control, _, raiz, __):
            inicial = juego.linea_tiempo.consultar_t(0)
            control.procesar_comando('mover E')
            enemigo = motor.enemigos_por_sala[motor.jugador.posicion_actual][0]
            for _ in range(6):
                if enemigo.vida <= 0: break
                control.procesar_comando('atacar ' + enemigo.id_instancia)
            self.assertEqual(motor.enemigos_derrotados, 1)
            consulta = juego.linea_tiempo.consultar_final()
            texto = detallar_partida(consulta, juego)
            self.assertIn('Enemigos derrotados: 1', texto)
            self.assertIn('Ninguno vivo.', texto)
            self.assertIn('Enemigos derrotados: 0', detallar_partida(inicial, juego))
            copia = decodificar_historia(codificar_historia(juego.linea_tiempo))
            self.assertEqual(detallar_partida(copia.consultar_final(), juego), texto)
            antes = juego.exportar_estado(), control.bitacora_replay.ruta.read_bytes()
            ruta = raiz / 'detalle.bin'
            control.procesar_comando(f'guardar "{ruta}"')
            control.procesar_comando('esperar')
            control.procesar_comando(f'cargar "{ruta}"')
            self.assertEqual(detallar_partida(juego.linea_tiempo.consultar_final(), juego), texto)
            self.assertEqual(juego.exportar_estado(), antes[0])
            vivo = motor.enemigos_derrotados
            motor.enemigos_derrotados = 999
            try:
                self.assertIn('Enemigos derrotados: 0', detallar_partida(inicial, juego))
            finally:
                motor.enemigos_derrotados = vivo

    def test_hu02_guardado_anterior_sin_resumen_carga_y_continua(self):
        with integracion.ControladorACRealTest().partida() as (motor, juego, control, _, __, ___):
            motor._resumen_historico = False
            legado = LineaTiempo(EstadoHistorico(motor.proyeccion_completa()), 2)
            motor._historia_h3 = juego.linea_tiempo = legado
            control.procesar_comando('mover E')
            guardado = juego.exportar_estado()
            anterior = detallar_partida(legado.consultar_final(), juego)
            self.assertIn('Resultado: no registrado', anterior)
            motor._resumen_historico = True
            juego.restaurar_estado(guardado)
            self.assertFalse(motor._resumen_historico)
            control.procesar_comando('esperar')
            self.assertIn('Enemigos derrotados: no registrado', detallar_partida(juego.linea_tiempo.consultar_final(), juego))

    def test_hu02_resultado_historico_no_se_infiere_de_vida_actual(self):
        estado = EstadoHistorico((('sala', (5, 'Salida')), ('jugador', (8, 30, 6, 2, 100)),
                                  ('efectos', ()), ('estadisticas_partida', (3, 'victoria'))))
        texto = detallar(SimpleNamespace(estado=estado, reloj=300, acciones=8))
        self.assertIn('Resultado: victoria', texto)
        self.assertIn('Enemigos derrotados: 3', texto)
        self.assertIn('acciones 8', texto)
