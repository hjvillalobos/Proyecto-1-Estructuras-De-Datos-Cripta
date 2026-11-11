import unittest
from unittest.mock import patch

from controlador.receptor_h3 import ReceptorH3
from controlador.resumen_historia import consultar
from datos.historia_binaria import codificar_historia, decodificar_historia
from modelo.errores_historia import ErrorHistoria
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from tests.datos_terreno_cazador import motor_terreno
from tests.test_cambios_historicos_motor import estado_motor


class ReceptorH3DTest(unittest.TestCase):
    def test_fr002_fr003_h3_motor_real_antes_despues_y_ordinal_sin_mutacion(self):
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")), motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            historia = LineaTiempo(EstadoHistorico(motor.proyeccion_h3()), 2)
            receptor = ReceptorH3(historia)
            inicial = motor.jugador.vida
            self.assertTrue(motor.ejecutar("mover", "E", registrar_h3=receptor).ok)
            final = motor.jugador.vida
            self.assertLess(final, inicial)
            self.assertTrue(motor.ejecutar("esperar", registrar_h3=receptor).ok)
            antes = estado_motor(motor), historia.exportar()
            for h in (historia, decodificar_historia(codificar_historia(historia))):
                for referencia, vida in (("99", inicial), ("100", final), ("#2", final)):
                    with self.subTest(referencia=referencia):
                        estado = consultar(h, referencia).estado
                        self.assertEqual(estado.obtener("sala")[0], 101)
                        self.assertEqual(estado.obtener("jugador")[0], vida)
            self.assertEqual((estado_motor(motor), historia.exportar()), antes)

    def test_fr002_fr006_rechazo_de_delta_tardio_revierte_motor_y_conserva_historia(self):
        with motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            historia = LineaTiempo(EstadoHistorico(motor.proyeccion_h3()), 2)
            receptor = ReceptorH3(historia)
            mensajes = []
            motor.establecer_notificador(mensajes.append)
            antes = estado_motor(motor), historia.exportar()
            def rechazar(inicio, fin, ordinal, cambios, eventos):
                incompatible = (("jugador", (999, 999, 999, 999, 999), (0, 0, 0, 0, 0)),)
                receptor(inicio, fin, ordinal, cambios, eventos + ((fin, 999, incompatible),))
            with self.assertRaises(ErrorHistoria):
                motor.ejecutar("mover", "E", registrar_h3=rechazar)
            self.assertEqual((estado_motor(motor), historia.exportar()), antes)
            self.assertEqual(mensajes, [])
            self.assertTrue(motor.ejecutar("mover", "E", registrar_h3=receptor).ok)
            self.assertEqual(historia.cantidad_acciones, 1)
            self.assertEqual(historia.reloj, 100)

    def test_fr002_fr005_no_reordena_eventos_ni_acepta_lotes_repetidos(self):
        historia = LineaTiempo(EstadoHistorico((("sala", (1, "Inicio")),)), 2)
        receptor = ReceptorH3(historia)
        cambios = (("sala", (1, "Inicio"), (2, "Destino")),)
        antes = historia.exportar()
        with self.assertRaises(ErrorHistoria):
            receptor(0, 100, 1, cambios, ((100, 11, ()), (100, 10, ())))
        self.assertEqual(historia.exportar(), antes)
        receptor(0, 100, 1, cambios, ((100, 10, ()), (100, 11, ())))
        aceptado = historia.exportar()
        for inicio, ordinal in ((0, 1), (100, 1), (True, 2), (100, True)):
            with self.subTest(inicio=inicio, ordinal=ordinal), self.assertRaises(ErrorHistoria):
                receptor(inicio, 200, ordinal, (), ())
            self.assertEqual(historia.exportar(), aceptado)

    def test_fr005_lote_invalido_no_publica_cambios_parciales(self):
        historia = LineaTiempo(EstadoHistorico((("sala", (1, "Inicio")),)), 2)
        receptor = ReceptorH3(historia)
        valido = (("sala", (1, "Inicio"), (2, "Destino")),)
        casos = ((list(valido), ()), (valido + (("sala", 1),), ()),
                 (valido, [(100, 1, ())]), (valido, ((100, 1, (("azar", 0, 1),)),)),
                 (valido, ((100, True, ()),)), (valido, ((100, 1, (("sala", (2, "Destino"), []),)),)))
        antes = historia.exportar()
        for cambios, eventos in casos:
            with self.subTest(cambios=cambios, eventos=eventos), self.assertRaises(ErrorHistoria):
                receptor(0, 100, 1, cambios, eventos)
            self.assertEqual(historia.exportar(), antes)
