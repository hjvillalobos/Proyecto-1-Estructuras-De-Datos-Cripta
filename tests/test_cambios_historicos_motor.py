"""AD-H3: productor optativo y contrato con la línea de tiempo de D."""

from importlib.util import find_spec
from random import Random
import unittest
from unittest.mock import patch

from tests.datos_terreno_cazador import motor_terreno


def estado_motor(motor):
    agenda = tuple(sorted((e.tiempo, e.secuencia, id(e), e.en_cola)
                          for e in motor.cola.pendientes()))
    return motor.exportar_estado(), agenda, motor.historial.cantidad_turnos()


class PruebasProductorH3(unittest.TestCase):
    def test_proyecciones_validas_comparan_valores_por_clave(self):
        with motor_terreno() as motor:
            anterior = motor.proyeccion_h3()
            self.assertEqual(motor._cambios_h3(anterior), ())
            sala = (101, motor.salas[101].nombre)
            jugador = (anterior[1][1][0] - 1, *anterior[1][1][1:])
            with patch.object(motor, "proyeccion_h3", return_value=(("sala", sala), ("jugador", jugador))):
                self.assertEqual(motor._cambios_h3(anterior), (
                    ("sala", anterior[0][1], sala),
                    ("jugador", anterior[1][1], jugador),
                ))

    def test_proyecciones_incompatibles_fallan_antes_de_producir_deltas(self):
        with motor_terreno() as motor:
            anterior = motor.proyeccion_h3()
            casos = (
                ("invertidas", anterior[::-1], "mismas claves en el mismo orden"),
                ("más corta", anterior[:1], "distinta longitud"),
                ("más larga", anterior + (("extra", 0),), "distinta longitud"),
            )
            for caso, posterior, mensaje in casos:
                with self.subTest(caso=caso):
                    with patch.object(motor, "proyeccion_h3", return_value=posterior):
                        with self.assertRaisesRegex(ValueError, mensaje):
                            motor._cambios_h3(anterior)

    def test_proyeccion_invalida_despues_del_ataque_revierte_sin_publicar(self):
        with motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            previo = estado_motor(motor)
            vida_inicial = motor.jugador.vida
            proyectar = motor.proyeccion_h3
            mensajes, lotes = [], []
            motor.establecer_notificador(mensajes.append)

            def proyectar_con_desajuste():
                proyeccion = proyectar()
                if motor.jugador.vida < vida_inicial:
                    self.assertEqual(motor.reloj, 100)
                    return proyeccion[::-1]
                return proyeccion

            with patch.object(motor, "proyeccion_h3", side_effect=proyectar_con_desajuste):
                with self.assertRaisesRegex(ValueError, "mismas claves en el mismo orden"):
                    motor.ejecutar("mover", "E", registrar_h3=lambda *lote: lotes.append(lote))

            self.assertEqual(lotes, [])
            self.assertEqual(mensajes, [])
            self.assertEqual(estado_motor(motor), previo)

    def test_sin_receptor_conserva_el_flujo_y_no_consulta_proyecciones(self):
        resultados = []
        for opciones in ({}, {"registrar_h3": None}):
            with motor_terreno() as motor:
                mensajes = []
                motor.establecer_notificador(mensajes.append)
                with patch.object(motor, "proyeccion_h3", side_effect=AssertionError("H3 deshabilitado")):
                    rechazado = motor.ejecutar("mover", "O", **opciones)
                    movimiento = motor.ejecutar("mover", "E", **opciones)
                    espera = motor.ejecutar("esperar", **opciones)
                self.assertFalse(rechazado.ok)
                self.assertTrue(movimiento.ok)
                self.assertTrue(espera.ok)
                resultados.append((motor.exportar_estado(), motor.historial.cantidad_turnos(), mensajes))
        self.assertEqual(resultados[0], resultados[1])

    def test_base_independiente_y_lote_despues_de_los_eventos_empatados(self):
        with motor_terreno() as motor:
            self.assertNotIn("costo", motor.salas[100].salidas["E"])
            motor.cola.fijar_contador(10)
            base = motor.proyeccion_h3()
            lotes = []
            mensajes = []
            motor.establecer_notificador(mensajes.append)
            destino = motor.enemigos_por_sala[101][0]
            azar = Random()
            azar.setstate(motor.azar.getstate())
            dano = max(1, destino.ataque + azar.randint(0, 4) - motor.jugador.defensa)
            vida_inicial = base[1][1][0]

            def registrar(*lote):
                self.assertEqual(motor.reloj, 100)
                self.assertEqual(motor.historial.cantidad_turnos(), 0)
                self.assertEqual(mensajes, [])
                self.assertEqual(destino.evento_pendiente.tiempo, 200)
                lotes.append(lote)

            self.assertTrue(motor.ejecutar("mover", "E", registrar_h3=registrar).ok)
            self.assertEqual(motor.historial.cantidad_turnos(), 1)
            self.assertTrue(mensajes)
            self.assertEqual(base[0][1][0], 100)
            self.assertEqual(base[1][1][0], vida_inicial)
            self.assertEqual(motor.azar.getstate(), azar.getstate())
            vida_final = (vida_inicial - dano, *base[1][1][1:])
            self.assertEqual(lotes, [(0, 100, 1, (
                ("sala", base[0][1], (101, motor.salas[101].nombre)),
            ), (
                (100, 0, ()),
                (100, 10, ()),
                (100, 11, (("jugador", base[1][1], vida_final),)),
            ))])

    def test_movimiento_rechazado_no_entrega_lote(self):
        with motor_terreno() as motor:
            previo = estado_motor(motor)
            lotes = []
            self.assertFalse(motor.ejecutar("mover", "O", registrar_h3=lotes.append).ok)
            self.assertEqual(lotes, [])
            self.assertEqual(estado_motor(motor), previo)

    def test_fallo_durante_el_motor_revierte_sin_invocar_al_receptor(self):
        with motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            previo = estado_motor(motor)
            vida = motor.jugador.vida
            lotes = []
            procesar = motor.ejecutar_ciclo

            def fallar_despues_del_ataque(*args, **kwargs):
                evento = procesar(*args, **kwargs)
                if motor.jugador.vida < vida:
                    raise RuntimeError("Fallo después de aplicar el daño")
                return evento

            with patch.object(motor, "ejecutar_ciclo", side_effect=fallar_despues_del_ataque):
                with self.assertRaisesRegex(RuntimeError, "después de aplicar el daño"):
                    motor.ejecutar("mover", "E", registrar_h3=lotes.append)
            self.assertEqual(lotes, [])
            self.assertEqual(estado_motor(motor), previo)


@unittest.skipUnless(find_spec("modelo.linea_tiempo"), "Requiere el componente real de D")
class PruebasH3ConD(unittest.TestCase):
    def crear_historia(self, motor):
        from modelo.linea_tiempo import EstadoHistorico, LineaTiempo

        return LineaTiempo(EstadoHistorico(motor.proyeccion_h3()), 2)

    def registrar(self, historia, inicio, fin, ordinal, cambios, eventos, *, invalidar=False):
        from modelo.snapshots import CambioHistorico, EventoHistorico, ValorHistorico

        def traducir(cambios):
            return tuple(CambioHistorico(clave, ValorHistorico(True, antes), ValorHistorico(True, despues))
                         for clave, antes, despues in cambios)

        self.assertEqual((inicio, ordinal), (historia.reloj, historia.cantidad_acciones + 1))
        if invalidar:
            # El movimiento previo es válido. El siguiente delta contradice la sala resultante.
            cambios += (("sala", cambios[0][1], cambios[0][2]),)
        historia.registrar_accion(fin, traducir(cambios), tuple(
            EventoHistorico(tiempo, secuencia, traducir(deltas))
            for tiempo, secuencia, deltas in eventos
        ))

    def test_consultas_h3_con_los_deltas_del_motor_real(self):
        from controlador.resumen_historia import consultar

        with motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            historia = self.crear_historia(motor)

            def registrar(*lote):
                self.registrar(historia, *lote)

            vida_inicial = motor.jugador.vida
            self.assertTrue(motor.ejecutar("mover", "E", registrar_h3=registrar).ok)
            vida_frontera = motor.jugador.vida
            self.assertLess(vida_frontera, vida_inicial)
            self.assertEqual((historia.cantidad_acciones, historia.reloj), (1, 100))
            self.assertTrue(motor.ejecutar("esperar", registrar_h3=registrar).ok)
            self.assertLess(motor.jugador.vida, vida_frontera)
            self.assertEqual((historia.cantidad_acciones, historia.reloj), (2, 200))

            antes = estado_motor(motor), historia.exportar()
            for consulta, reloj, vida in (("99", 99, vida_inicial), ("100", 100, vida_frontera),
                                         ("#2", 100, vida_frontera)):
                with self.subTest(consulta=consulta):
                    resultado = consultar(historia, consulta)
                    self.assertEqual(resultado.reloj, reloj)
                    self.assertEqual(resultado.estado.obtener("sala")[0], 101)
                    self.assertEqual(resultado.estado.obtener("jugador")[0], vida)
            self.assertEqual((estado_motor(motor), historia.exportar()), antes)

    def test_rechazo_tardio_de_d_revierte_a_y_conserva_ambas_fronteras(self):
        from modelo.errores_historia import CambioHistoriaIncoherente

        with motor_terreno() as motor:
            motor.cola.fijar_contador(10)
            historia = self.crear_historia(motor)
            antes = estado_motor(motor), historia.exportar()
            mensajes = []
            intentos = []
            motor.establecer_notificador(mensajes.append)

            def rechazar(*lote):
                intentos.append(lote)
                self.registrar(historia, *lote, invalidar=True)

            with self.assertRaises(CambioHistoriaIncoherente):
                motor.ejecutar("mover", "E", registrar_h3=rechazar)
            self.assertEqual(len(intentos), 1)
            self.assertEqual(mensajes, [])
            self.assertEqual((estado_motor(motor), historia.exportar()), antes)

            def aceptar(*lote):
                self.assertEqual(lote, intentos[0])
                self.registrar(historia, *lote)

            self.assertTrue(motor.ejecutar("mover", "E", registrar_h3=aceptar).ok)
            self.assertEqual((historia.cantidad_acciones, historia.reloj), (1, 100))


if __name__ == "__main__":
    unittest.main()
