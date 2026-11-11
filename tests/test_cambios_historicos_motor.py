"""AD-H3: productor optativo y contrato con la línea de tiempo de D."""

from contextlib import contextmanager, redirect_stderr
from dataclasses import replace
from importlib.util import find_spec
from io import StringIO
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from modelo.juego import crear_juego
from modelo.tipos import ObjetoInstancia
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


@contextmanager
def motor_con_historia_offline(*, con_mapa=False, con_trampa_venenosa=False):
    def fabrica(precarga, *args, **opciones):
        almacen = precarga.cliente.almacen
        almacen.guardar_ficha("cat1", {
            "id": "pergamino-h3", "clase": "pergamino_retroceso", "nombre": "Pergamino",
        })
        if con_trampa_venenosa:
            almacen.guardar_ficha("cat1", {
                "id": "trampa-h3", "clase": "trampa", "nombre": "Trampa venenosa",
                "veneno": {"dano_por_pulso": 1},
            })
            contenido = almacen.leer_contenido("prueba", "v1", 101)
            contenido["trampas"] = [{"instancia": "t-h3-101", "tipo": "trampa-h3"}]
            almacen.guardar_contenido("prueba", "v1", contenido)
        return crear_juego(precarga, *args, historia_para_pruebas=True,
                           conocimiento_para_pruebas=con_mapa, **opciones)

    with patch("tests.datos_terreno_cazador.crear_juego", new=fabrica), motor_terreno() as motor:
        yield motor


class PruebasAdaptadorHistoricoOffline(unittest.TestCase):
    def test_consultas_del_adaptador_en_la_frontera_del_motor(self):
        from controlador.partida_historica import PartidaHistorica, integrar_historia
        from controlador.resumen_historia import consultar, resumir

        with motor_con_historia_offline() as motor:
            motor.cola.fijar_contador(10)
            vida_inicial = motor.jugador.vida
            partida = integrar_historia(motor, 2)
            self.assertIsInstance(partida, PartidaHistorica)
            historia = partida.linea_tiempo
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (0, 0))
            inicial = historia.consultar_t(0).estado
            self.assertEqual(inicial.obtener("sala")[0], 100)
            self.assertEqual(inicial.obtener("efectos"), ())

            self.assertTrue(partida.ejecutar("mover", "E").ok)
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (100, 1))
            vida_frontera = motor.jugador.vida
            self.assertLess(vida_frontera, vida_inicial)
            eventos = historia.exportar().acciones[0].eventos
            self.assertEqual(tuple((e.tiempo, e.secuencia) for e in eventos),
                             ((100, 0), (100, 10), (100, 11)))
            self.assertEqual(eventos[1].cambios, ())
            self.assertEqual(eventos[2].cambios[0].clave, "jugador")
            self.assertEqual(eventos[2].cambios[0].nuevo.valor[0], vida_frontera)

            self.assertTrue(partida.ejecutar("esperar").ok)
            self.assertEqual((motor.reloj, motor.acciones_jugador), (200, 2))
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (200, 2))
            self.assertLess(motor.jugador.vida, vida_frontera)
            antes = estado_motor(motor), historia.exportar()
            for referencia, reloj, vida in (("99", 99, vida_inicial), ("100", 100, vida_frontera),
                                           ("#2", 100, vida_frontera)):
                with self.subTest(referencia=referencia):
                    consulta = consultar(historia, referencia)
                    self.assertEqual(consulta.reloj, reloj)
                    self.assertEqual(consulta.estado.obtener("sala")[0], 101)
                    self.assertEqual(consulta.estado.obtener("jugador")[0], vida)
                    texto = resumir(consulta)
                    self.assertIn(f"Historia t={reloj} | Sala 101", texto)
                    self.assertIn(f"Vida {vida}/", texto)
            self.assertEqual((estado_motor(motor), historia.exportar()), antes)

    def test_rechazo_del_registro_del_adaptador_revierte_el_turno(self):
        from controlador.partida_historica import integrar_historia
        from modelo.errores_historia import CambioHistoriaIncoherente

        with motor_con_historia_offline() as motor:
            motor.cola.fijar_contador(10)
            partida = integrar_historia(motor, 2)
            historia = partida.linea_tiempo
            registrar = historia.registrar_accion
            previo = estado_motor(motor), historia.exportar()
            mensajes = []
            motor.establecer_notificador(mensajes.append)

            def agregar_delta_incoherente(fin, cambios, eventos, **opciones):
                self.assertEqual((fin, motor.reloj, motor.acciones_jugador), (100, 100, 1))
                self.assertEqual(cambios[0].clave, "sala")
                self.assertEqual(motor.historial.cantidad_turnos(), 0)
                return registrar(fin, cambios + (cambios[0],), eventos, **opciones)

            with patch.object(historia, "registrar_accion", side_effect=agregar_delta_incoherente) as intento:
                with self.assertRaises(CambioHistoriaIncoherente):
                    partida.ejecutar("mover", "E")
            intento.assert_called_once()
            self.assertEqual((estado_motor(motor), historia.exportar()), previo)
            self.assertEqual(mensajes, [])
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (100, 1))

    def test_partida_normal_no_se_envuelve_y_variante_limita_acciones(self):
        from controlador.partida_historica import integrar_historia

        with motor_terreno() as motor:
            self.assertIs(integrar_historia(motor, 2), motor)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
        with motor_con_historia_offline() as motor:
            partida = integrar_historia(motor, 2)
            historia = partida.linea_tiempo
            previo = estado_motor(motor), historia.exportar()
            with self.assertRaisesRegex(ValueError, "solo admite mover y esperar"):
                partida.ejecutar("atacar", "e-100")
            self.assertEqual((estado_motor(motor), historia.exportar()), previo)

    def dar_pergamino(self, motor):
        inventario = motor.jugador.inventario
        self.assertIsNotNone(inventario.recoger(
            ObjetoInstancia("p-h3", "pergamino-h3", "inventario")))
        return inventario

    def test_historia_registra_veneno_expiracion_y_retroceso(self):
        from controlador.partida_historica import integrar_historia
        from controlador.resumen_historia import resumir
        from modelo.errores_historia import ReferenciaHistoricaInvalida
        from modelo.snapshots import CambioHistorico, ValorHistorico

        with motor_con_historia_offline(con_trampa_venenosa=True) as motor:
            partida = integrar_historia(motor, 2)
            historia = partida.linea_tiempo
            inventario = self.dar_pergamino(motor)
            self.assertEqual(historia.consultar_t(0).estado.obtener("efectos"), ())
            resultado = partida.ejecutar("mover", "E")
            self.assertTrue(resultado.ok)
            self.assertEqual(resultado.trampas_activadas, ["t-h3-101"])
            expiracion = motor.jugador.veneno.evento_fin
            self.assertEqual((motor.reloj, expiracion.tiempo, expiracion.tipo),
                             (100, 400, "fin_veneno"))
            self.assertEqual(historia.consultar_t(1).estado.obtener("efectos"), ("veneno",))

            for reloj in (200, 300):
                self.assertTrue(partida.ejecutar("esperar").ok)
                self.assertEqual(motor.reloj, reloj)
            self.assertEqual(historia.consultar_t(300).estado.obtener("efectos"), ("veneno",))
            self.assertTrue(partida.ejecutar("esperar").ok)
            self.assertEqual((motor.reloj, historia.reloj), (400, 400))
            self.assertIsNone(motor.jugador.veneno)
            self.assertFalse(expiracion.en_cola)
            self.assertIn("Efectos: veneno", resumir(historia.consultar_t(399)))
            self.assertIn("Efectos: ninguno", resumir(historia.consultar_t(400)))

            alta = CambioHistorico("efectos", ValorHistorico(True, ()),
                                   ValorHistorico(True, ("veneno",)))
            baja = CambioHistorico("efectos", alta.nuevo, alta.anterior)
            cambios_accion = []
            cambios_evento = []
            for ordinal, accion in enumerate(historia.exportar().acciones, 1):
                cambios_accion.extend((ordinal, c) for c in accion.cambios if c.clave == "efectos")
                for evento in accion.eventos:
                    cambios_evento.extend((ordinal, evento.tiempo, evento.secuencia, c)
                                          for c in evento.cambios if c.clave == "efectos")
            self.assertEqual(cambios_accion, [(1, alta)])
            self.assertEqual(cambios_evento, [(4, 400, expiracion.secuencia, baja)])

            self.assertTrue(partida.ejecutar("retroceso").ok)
            self.assertEqual((motor.reloj, historia.reloj, historia.cantidad_acciones), (300, 300, 3))
            self.assertIs(motor.jugador.veneno.evento_fin, expiracion)
            self.assertTrue(expiracion.en_cola)
            self.assertFalse(expiracion.cancelado)
            self.assertEqual(historia.consultar_final().estado.obtener("efectos"), ("veneno",))
            self.assertEqual(inventario.contar("pergamino-h3"), 0)
            with self.assertRaises(ReferenciaHistoricaInvalida):
                historia.consultar_t(400)

    def test_pergamino_recorta_solo_la_ultima_accion_y_permite_otra_rama(self):
        from controlador.partida_historica import integrar_historia
        from controlador.resumen_historia import consultar
        from modelo.errores_historia import ReferenciaHistoricaInvalida

        with motor_con_historia_offline() as motor:
            partida = integrar_historia(motor, 2)
            historia = partida.linea_tiempo
            inventario = self.dar_pergamino(motor)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            retenida = historia.exportar().acciones[0]
            consultas = tuple(consultar(historia, referencia).estado.campos()
                              for referencia in ("99", "100"))
            estado, agenda, turnos = estado_motor(motor)

            self.assertTrue(partida.ejecutar("esperar").ok)
            descartada = historia.exportar().acciones[1]
            self.assertTrue(descartada.eventos)
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (200, 2))
            self.assertNotEqual(motor.azar.getstate(), estado.rng_estado)
            with patch.object(historia, "registrar_accion", wraps=historia.registrar_accion) as registrar:
                self.assertTrue(partida.ejecutar("retroceso").ok)
            registrar.assert_not_called()

            self.assertEqual(historia.exportar().acciones, (retenida,))
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (100, 1))
            self.assertEqual((motor.reloj, motor.acciones_jugador), (100, 1))
            self.assertEqual((motor.jugador.posicion_actual, motor.jugador.vida),
                             (estado.jugador.sala_id, estado.jugador.vida))
            self.assertEqual(estado_motor(motor)[1:], (agenda, turnos))
            self.assertEqual(motor.cola.proxima_secuencia(), estado.siguiente_secuencia)
            self.assertEqual(motor.azar.getstate(), estado.rng_estado)
            self.assertEqual(inventario.contar("pergamino-h3"), 0)
            self.assertEqual(tuple(consultar(historia, referencia).estado.campos()
                                   for referencia in ("99", "100")), consultas)
            for referencia in ("#2", "200"):
                with self.subTest(referencia=referencia):
                    with self.assertRaises(ReferenciaHistoricaInvalida):
                        consultar(historia, referencia)

            self.assertTrue(partida.ejecutar("mover", "O").ok)
            self.assertEqual((motor.reloj, motor.acciones_jugador), (200, 2))
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (200, 2))
            primera, nueva = historia.exportar().acciones
            self.assertEqual(primera, retenida)
            self.assertEqual((nueva.inicio, nueva.fin), (100, 200))
            self.assertNotEqual(nueva.eventos, descartada.eventos)
            self.assertEqual(consultar(historia, "#2").estado.campos(), consultas[1])
            self.assertEqual(consultar(historia, "200").estado.obtener("sala")[0], 100)

    def test_recorte_incoherente_no_revierte_el_motor_ni_consume_pergamino(self):
        from controlador.partida_historica import integrar_historia
        from modelo.errores_historia import CambioHistoriaIncoherente
        from modelo.snapshots import CambioHistorico, ValorHistorico

        with motor_con_historia_offline() as motor:
            partida = integrar_historia(motor, 2)
            historia = partida.linea_tiempo
            inventario = self.dar_pergamino(motor)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            self.assertTrue(partida.ejecutar("esperar").ok)
            previo = estado_motor(motor), historia.exportar()
            recortar = historia.recortar
            mensajes = []
            motor.establecer_notificador(mensajes.append)

            def correccion_incoherente(conservadas):
                correccion = CambioHistorico("sala", ValorHistorico(True, (999, "Otra")),
                                             ValorHistorico(True, (100, "Entrada")))
                return recortar(conservadas, (correccion,))

            with patch.object(historia, "recortar", side_effect=correccion_incoherente) as intento:
                with self.assertRaisesRegex(CambioHistoriaIncoherente, "valor anterior"):
                    partida.ejecutar("retroceso")
            intento.assert_called_once_with(1)
            self.assertEqual((estado_motor(motor), historia.exportar()), previo)
            self.assertEqual(mensajes, [])
            self.assertEqual(inventario.contar("pergamino-h3"), 1)
            self.assertTrue(partida.ejecutar("retroceso").ok)
            self.assertEqual((historia.reloj, historia.cantidad_acciones), (100, 1))

    def test_sin_pergamino_o_sin_turno_no_intenta_recortar(self):
        from controlador.partida_historica import integrar_historia

        for con_turno in (False, True):
            with self.subTest(con_turno=con_turno), motor_con_historia_offline() as motor:
                partida = integrar_historia(motor, 2)
                historia = partida.linea_tiempo
                if con_turno:
                    self.assertTrue(partida.ejecutar("esperar").ok)
                else:
                    self.dar_pergamino(motor)
                previo = estado_motor(motor), historia.exportar()
                with patch.object(historia, "recortar", wraps=historia.recortar) as recortar:
                    self.assertFalse(partida.ejecutar("retroceso").ok)
                recortar.assert_not_called()
                self.assertEqual((estado_motor(motor), historia.exportar()), previo)


class PruebasRestauracionHistoricaOffline(unittest.TestCase):
    def test_restaura_en_memoria_y_registra_en_la_linea_restaurada(self):
        from controlador.partida_historica import integrar_historia
        from controlador.resumen_historia import consultar
        from modelo.errores_historia import ReferenciaHistoricaInvalida

        with motor_con_historia_offline() as motor:
            partida = integrar_historia(motor, 2)
            anterior = partida.linea_tiempo
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            guardado = partida.exportar_estado()
            consultas = tuple(consultar(anterior, ref).estado.campos() for ref in ("99", "100"))
            jugador = motor.jugador
            self.assertTrue(partida.ejecutar("esperar").ok)
            futuro = anterior.exportar()

            partida.restaurar_estado(guardado)
            restaurada = partida.linea_tiempo
            self.assertIsNot(restaurada, anterior)
            self.assertIs(motor._historia_h3, restaurada)
            self.assertIs(motor.jugador, jugador)
            self.assertEqual((motor.reloj, motor.acciones_jugador), (100, 1))
            self.assertEqual((restaurada.reloj, restaurada.cantidad_acciones), (100, 1))
            self.assertEqual((jugador.posicion_actual, jugador.vida),
                             (101, guardado.jugador.vida))
            self.assertEqual(motor.exportar_estado().eventos, guardado.eventos)
            self.assertEqual(motor.cola.proxima_secuencia(), guardado.siguiente_secuencia)
            self.assertEqual(motor.azar.getstate(), guardado.rng_estado)
            self.assertEqual(partida.exportar_estado(), guardado)
            self.assertEqual(motor.historial.cantidad_turnos(), 0)
            self.assertEqual(tuple(consultar(restaurada, ref).estado.campos()
                                   for ref in ("99", "100")), consultas)
            for ref in ("#2", "200"):
                with self.subTest(ref=ref), self.assertRaises(ReferenciaHistoricaInvalida):
                    consultar(restaurada, ref)

            self.assertTrue(partida.ejecutar("mover", "O").ok)
            self.assertEqual((restaurada.reloj, restaurada.cantidad_acciones), (200, 2))
            self.assertEqual(consultar(restaurada, "200").estado.obtener("sala")[0], 100)
            self.assertEqual(anterior.exportar(), futuro)
            self.assertEqual(motor.historial.cantidad_turnos(), 1)

    def test_rechaza_fronteras_de_historia_incompatibles_sin_mutar(self):
        from controlador.partida_historica import integrar_historia
        from datos.historia_binaria import codificar_historia, decodificar_historia
        from modelo.errores_historia import CambioHistoriaIncoherente
        from modelo.linea_tiempo import EstadoHistorico, LineaTiempo

        with motor_con_historia_offline() as motor:
            partida = integrar_historia(motor, 2)
            activa = partida.linea_tiempo
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            guardado = partida.exportar_estado()
            candidata = decodificar_historia(guardado.historia)
            self.assertTrue(partida.ejecutar("esperar").ok)
            previo = estado_motor(motor), activa.exportar()
            for estado in (replace(guardado, reloj=101), replace(guardado, acciones_jugador=2)):
                with self.subTest(reloj=estado.reloj, ordinal=estado.acciones_jugador):
                    with self.assertRaisesRegex(CambioHistoriaIncoherente, "reloj u ordinal"):
                        motor.restaurar_estado_con_historia(estado, candidata)
                    self.assertEqual((estado_motor(motor), activa.exportar()), previo)
                    self.assertIs(motor._historia_h3, activa)

            final = candidata.consultar_final().estado
            jugador = final.obtener("jugador")
            for clave, valor in (("sala", (100, motor.salas[100].nombre)),
                                 ("jugador", (jugador[0] + 1, *jugador[1:]))):
                with self.subTest(clave=clave):
                    campos = tuple((k, valor if k == clave else v) for k, v in final.campos())
                    incompatible = LineaTiempo(EstadoHistorico(campos), 2)
                    incompatible.registrar_accion(100)
                    estado = replace(guardado, historia=codificar_historia(incompatible))
                    with self.assertRaisesRegex(CambioHistoriaIncoherente, "no coinciden con la historia"):
                        partida.restaurar_estado(estado)
                    self.assertEqual((estado_motor(motor), activa.exportar()), previo)
                    self.assertIs(partida.linea_tiempo, activa)
                    self.assertIs(motor._historia_h3, activa)

    def test_estado_invalido_y_ficha_ausente_conservan_motor_y_receptor(self):
        from controlador.partida_historica import integrar_historia
        from red.errores import ErrorCripta

        with motor_con_historia_offline() as motor:
            partida = integrar_historia(motor, 2)
            activa = partida.linea_tiempo
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            guardado = partida.exportar_estado()
            self.assertTrue(partida.ejecutar("esperar").ok)
            previo = estado_motor(motor), activa.exportar()
            evento = replace(guardado.eventos[0], secuencia=guardado.siguiente_secuencia)
            agenda_invalida = replace(guardado, eventos=[evento, *guardado.eventos[1:]])
            salas = [
                replace(sala, enemigos=[replace(e, tipo="enemigo-inexistente") for e in sala.enemigos])
                if sala.sala_id == 101 else sala for sala in guardado.salas
            ]
            ficha_ausente = replace(guardado, salas=salas)
            for estado, error, mensaje in (
                (agenda_invalida, ValueError, "tiempo o secuencia"),
                (ficha_ausente, ErrorCripta, "enemigo-inexistente"),
            ):
                with self.subTest(mensaje=mensaje):
                    with self.assertRaisesRegex(error, mensaje):
                        partida.restaurar_estado(estado)
                    self.assertEqual((estado_motor(motor), activa.exportar()), previo)
                    self.assertIs(partida.linea_tiempo, activa)
                    self.assertIs(motor._historia_h3, activa)
            self.assertTrue(partida.ejecutar("mover", "O").ok)
            self.assertEqual((activa.reloj, activa.cantidad_acciones), (300, 3))

    def test_mapa_activo_rechaza_restauracion_sin_mutaciones(self):
        from controlador.partida_historica import integrar_historia
        from modelo.errores_historia import CambioHistoriaIncoherente

        with motor_con_historia_offline(con_mapa=True) as motor:
            partida = integrar_historia(motor, 2)
            activa = partida.linea_tiempo
            guardado = partida.exportar_estado()
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            previo = estado_motor(motor), activa.exportar(), motor.mapa_conocido()
            with self.assertRaisesRegex(CambioHistoriaIncoherente, "mapa conocido activo"):
                partida.restaurar_estado(guardado)
            self.assertEqual((estado_motor(motor), activa.exportar(), motor.mapa_conocido()), previo)
            self.assertIs(partida.linea_tiempo, activa)
            self.assertIs(motor._historia_h3, activa)


class PruebasPersistenciaHistoricaOffline(unittest.TestCase):
    def comprobar_rechazo(self, motor, partida, ruta, error, mensaje):
        from datos.guardado_binario import cargar_estado_partida

        activa = partida.linea_tiempo
        previo = estado_motor(motor), activa.exportar()
        with self.assertRaisesRegex(error, mensaje):
            partida.restaurar_estado(cargar_estado_partida(ruta))
        self.assertEqual((estado_motor(motor), activa.exportar()), previo)
        self.assertIs(partida.linea_tiempo, activa)
        self.assertIs(motor._historia_h3, activa)

    def test_archivo_v4_restaura_el_motor_y_permite_continuar(self):
        from controlador.partida_historica import integrar_historia
        from controlador.resumen_historia import consultar, resumir
        from datos.guardado_binario import ArchivoGuardado, cargar_estado_partida, guardar_estado
        from modelo.errores_historia import ReferenciaHistoricaInvalida

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            anterior = partida.linea_tiempo
            ruta = Path(carpeta) / "partida.bin"
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            esperado = partida.exportar_estado()
            consultas = tuple(resumir(consultar(anterior, ref)) for ref in ("99", "100"))
            guardar_estado(esperado, ruta)
            with ArchivoGuardado(ruta) as archivo:
                self.assertEqual(archivo.version, 4)

            self.assertTrue(partida.ejecutar("esperar").ok)
            self.assertEqual((motor.reloj, motor.acciones_jugador), (200, 2))
            futuro = anterior.exportar()
            self.assertNotEqual(motor.azar.getstate(), esperado.rng_estado)

            leido = cargar_estado_partida(ruta)
            self.assertEqual(leido, esperado)
            partida.restaurar_estado(leido)
            restaurada = partida.linea_tiempo
            self.assertIsNot(restaurada, anterior)
            self.assertIs(motor._historia_h3, restaurada)
            self.assertEqual((restaurada.reloj, restaurada.cantidad_acciones), (100, 1))
            self.assertEqual(partida.exportar_estado(), esperado)
            self.assertEqual(motor.historial.cantidad_turnos(), 0)
            self.assertEqual(tuple(resumir(consultar(restaurada, ref))
                                   for ref in ("99", "100")), consultas)
            for ref in ("#2", "200"):
                with self.subTest(ref=ref), self.assertRaises(ReferenciaHistoricaInvalida):
                    consultar(restaurada, ref)

            self.assertTrue(partida.ejecutar("mover", "O").ok)
            self.assertEqual((motor.reloj, motor.acciones_jugador), (200, 2))
            self.assertEqual((restaurada.reloj, restaurada.cantidad_acciones), (200, 2))
            self.assertEqual(resumir(consultar(restaurada, "#2")), consultas[1])
            self.assertEqual(consultar(restaurada, "200").estado.obtener("sala")[0], 100)
            self.assertEqual(anterior.exportar(), futuro)

    def test_archivo_corrupto_conserva_el_motor_y_el_receptor(self):
        from controlador.partida_historica import integrar_historia
        from datos.guardado_binario import GuardadoCorrupto, guardar_estado

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            original = Path(carpeta) / "partida.bin"
            guardar_estado(partida.exportar_estado(), original)
            datos = original.read_bytes()
            copia = Path(carpeta) / "truncada.bin"
            copia.write_bytes(datos[:-1])

            self.assertTrue(partida.ejecutar("esperar").ok)
            self.comprobar_rechazo(motor, partida, copia, GuardadoCorrupto, "truncado")
            self.assertEqual(original.read_bytes(), datos)

    def test_archivo_v3_se_rechaza_como_incompatible_con_parte_ii(self):
        from controlador.partida_historica import integrar_historia
        from datos.guardado_binario import ArchivoGuardado, FormatoIncompatible, guardar_estado

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            ruta = Path(carpeta) / "parte-i.bin"
            guardar_estado(motor.exportar_estado(), ruta)
            with ArchivoGuardado(ruta) as archivo:
                self.assertEqual(archivo.version, 3)

            self.assertTrue(partida.ejecutar("esperar").ok)
            self.comprobar_rechazo(motor, partida, ruta, FormatoIncompatible, "Parte I")

    def test_archivos_v4_validos_rechazan_historias_incoherentes_con_el_motor(self):
        from controlador.partida_historica import integrar_historia
        from datos.guardado_binario import (
            ArchivoGuardado, GuardadoCorrupto, cargar_estado_partida, guardar_estado,
        )
        from datos.historia_binaria import codificar_historia
        from modelo.errores_historia import CambioHistoriaIncoherente
        from modelo.linea_tiempo import EstadoHistorico, LineaTiempo

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            guardado = partida.exportar_estado()
            final = partida.linea_tiempo.consultar_final().estado
            jugador = final.obtener("jugador")
            self.assertTrue(partida.ejecutar("esperar").ok)

            for nombre, tiempos, reemplazo, error, mensaje in (
                ("reloj", (101,), (), GuardadoCorrupto, "frontera"),
                ("ordinal", (50, 100), (), GuardadoCorrupto, "frontera"),
                ("sala", (100,), (("sala", (100, motor.salas[100].nombre)),),
                 CambioHistoriaIncoherente, "no coinciden con la historia"),
                ("vida", (100,), (("jugador", (jugador[0] + 1, *jugador[1:])),),
                 CambioHistoriaIncoherente, "no coinciden con la historia"),
            ):
                with self.subTest(campo=nombre):
                    campos = tuple((clave, next((nuevo for k, nuevo in reemplazo if k == clave), valor))
                                   for clave, valor in final.campos())
                    historia = LineaTiempo(EstadoHistorico(campos), 2)
                    for tiempo in tiempos:
                        historia.registrar_accion(tiempo)
                    incompatible = replace(guardado, historia=codificar_historia(historia))
                    ruta = Path(carpeta) / f"{nombre}.bin"
                    guardar_estado(incompatible, ruta)
                    with ArchivoGuardado(ruta) as archivo:
                        self.assertEqual(archivo.version, 4)
                    self.assertEqual(cargar_estado_partida(ruta), incompatible)
                    self.comprobar_rechazo(motor, partida, ruta, error, mensaje)


class PruebasReplayHistoricoOffline(unittest.TestCase):
    def reproducir_offline(self, motor, ruta, hasta):
        from controlador.replay_sin_vista import reproducir
        from datos.offline import ClienteOffline
        from red.cache import CacheCatalogoOrdenado
        from red.catalogo import GestorCatalogo
        from red.precarga import GestorPrecarga

        carpeta = motor.gestor_precarga.cliente.almacen.carpeta
        cliente = ClienteOffline(carpeta, motor.meta.cripta_version)
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), cliente.almacen)
        precarga = GestorPrecarga(cliente, catalogo)

        def fabrica(fuente, cripta_id, semilla, *, version_cripta, version_catalogo):
            self.assertEqual((cripta_id, semilla, version_cripta, version_catalogo),
                             (motor.meta.cripta_id, motor.meta.semilla,
                              motor.meta.cripta_version, motor.meta.catalogo_version))
            return crear_juego(fuente, cripta_id, semilla, version_cripta=version_cripta,
                               version_catalogo=version_catalogo, historia_para_pruebas=True)

        with patch("vista.consola.VistaConsola", side_effect=AssertionError("vista de consola")), \
                patch("vista.grafica.VistaGrafica", side_effect=AssertionError("vista gráfica")), \
                patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP en replay")):
            try:
                return reproducir(ruta, precarga, fabrica, checkpoint_cada=2, hasta=hasta)
            finally:
                try:
                    precarga.cerrar()
                finally:
                    cliente.cerrar()

    def test_replay_sin_vista_con_carga_v4_y_continuacion(self):
        from controlador.partida_historica import integrar_historia
        from controlador.resumen_historia import consultar, resumir
        from datos.bitacora_replay import BitacoraReplay
        from datos.guardado_binario import ArchivoGuardado, cargar_estado_partida, guardar_estado

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            bitacora = BitacoraReplay(Path(carpeta) / "partida.log")
            bitacora.iniciar(partida.meta)
            vida_inicial = motor.jugador.vida
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            bitacora.registrar_accion("mover", "E")
            guardado = partida.exportar_estado()
            self.assertEqual(guardado.reloj, 100)
            self.assertLess(guardado.jugador.vida, vida_inicial)
            archivo_v4 = Path(carpeta) / "partida.bin"
            guardar_estado(guardado, archivo_v4)
            with ArchivoGuardado(archivo_v4) as archivo:
                self.assertEqual(archivo.version, 4)

            self.assertTrue(partida.ejecutar("esperar").ok)
            bitacora.registrar_accion("esperar")
            self.assertEqual(motor.reloj, 200)
            leido = cargar_estado_partida(archivo_v4)
            self.assertEqual(leido, guardado)
            partida.restaurar_estado(leido)
            bitacora.registrar_carga(leido)
            self.assertTrue(partida.ejecutar("mover", "O").ok)
            bitacora.registrar_accion("mover", "O")
            self.assertEqual((motor.reloj, motor.jugador.posicion_actual), (200, 100))
            archivo_v4.unlink()
            self.assertFalse(archivo_v4.exists())

            historia = partida.linea_tiempo
            for tiempo, sala, vida in ((99, 101, vida_inicial), (100, 101, guardado.jugador.vida),
                                       (200, 100, motor.jugador.vida)):
                with self.subTest(hasta=tiempo):
                    consulta = consultar(historia, str(tiempo))
                    self.assertEqual(consulta.estado.obtener("sala")[0], sala)
                    self.assertEqual(consulta.estado.obtener("jugador")[0], vida)
                    self.assertEqual(self.reproducir_offline(motor, bitacora.ruta, tiempo),
                                     resumir(consulta))
            self.assertEqual(self.reproducir_offline(motor, bitacora.ruta, 201),
                             "El replay terminó antes de t=201.\n" + resumir(historia.consultar_final()))

    def test_parser_rechaza_hasta_negativo(self):
        from main import leer_argumentos

        salida = StringIO()
        with redirect_stderr(salida), self.assertRaises(SystemExit) as error:
            leer_argumentos(["--replay", "partida.log", "--hasta", "-1"])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("instante entero no negativo", salida.getvalue())

    def test_replay_rechaza_bitacora_mal_formada(self):
        from datos.bitacora_replay import BitacoraReplay, ReplayCorrupto

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            bitacora = BitacoraReplay(Path(carpeta) / "truncada.log")
            bitacora.iniciar(motor.meta)
            with bitacora.ruta.open("a", encoding="utf-8") as archivo:
                archivo.write('{"tipo": "accion",')
            with self.assertRaises(ReplayCorrupto):
                self.reproducir_offline(motor, bitacora.ruta, 100)

    def test_replay_rechaza_cargas_historicas_invalidas(self):
        from controlador.partida_historica import integrar_historia
        from datos.bitacora_replay import BitacoraReplay, ReplayIncompatible

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            estado = partida.exportar_estado()
            for nombre, carga, mensaje in (
                ("sin-historia", replace(estado, historia=None), "no contiene una historia"),
                ("historia-corrupta", replace(estado, historia=estado.historia[:-1]), "historia"),
                ("frontera-incoherente", replace(estado, reloj=101), "frontera"),
            ):
                with self.subTest(caso=nombre):
                    bitacora = BitacoraReplay(Path(carpeta) / f"{nombre}.log")
                    bitacora.iniciar(motor.meta)
                    bitacora.registrar_carga(carga)
                    with self.assertRaisesRegex(ReplayIncompatible, mensaje):
                        self.reproducir_offline(motor, bitacora.ruta, 100)

    def test_archivos_invalidos_no_se_registran_como_carga(self):
        from controlador.partida_historica import integrar_historia
        from datos.bitacora_replay import BitacoraReplay
        from datos.guardado_binario import (
            FormatoIncompatible, GuardadoCorrupto, cargar_estado_partida, guardar_estado,
        )

        with motor_con_historia_offline() as motor, TemporaryDirectory() as carpeta:
            partida = integrar_historia(motor, 2)
            self.assertTrue(partida.ejecutar("mover", "E").ok)
            raiz = Path(carpeta)
            bitacora = BitacoraReplay(raiz / "partida.log")
            bitacora.iniciar(motor.meta)
            bitacora.registrar_accion("mover", "E")
            log_original = bitacora.ruta.read_bytes()
            v3, v4, truncado = raiz / "v3.bin", raiz / "v4.bin", raiz / "truncado.bin"
            guardar_estado(motor.exportar_estado(), v3)
            guardar_estado(partida.exportar_estado(), v4)
            truncado.write_bytes(v4.read_bytes()[:-1])

            for ruta, error in ((v3, FormatoIncompatible), (truncado, GuardadoCorrupto)):
                with self.subTest(archivo=ruta.name), self.assertRaises(error):
                    bitacora.registrar_carga(cargar_estado_partida(ruta))
            self.assertEqual(bitacora.ruta.read_bytes(), log_original)


if __name__ == "__main__":
    unittest.main()
