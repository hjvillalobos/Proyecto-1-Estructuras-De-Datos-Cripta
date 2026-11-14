"""T034/A12: restauración del motor offline con movimiento, agenda y efectos."""

from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from datos.guardado_binario import cargar_estado, guardar_estado
from modelo.juego import crear_juego
from modelo.errores_historia import CambioHistoriaIncoherente
from modelo.tipos import ObjetoInstancia
from red.errores import ErrorCripta
from tests.datos_terreno_cazador import motor_terreno
from tests.test_turno_cazador import partida_cazador


PERGAMINO = "pergamino-a12"
POCION = "velocidad-a12"


class PruebasRestauracionRutas(unittest.TestCase):
    def test_rollback_descarta_las_marcas_de_la_busqueda_del_turno(self):
        """A12 / FR-018: un turno fallido invalida las etiquetas que produjo."""
        for fase in ("accion", "publicacion"):
            with self.subTest(fase=fase):
                self.comprobar_rollback_de_busqueda(fase)

    def comprobar_rollback_de_busqueda(self, fase):
        with partida_cazador(350) as (motor, cazador, _):
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            antes = motor.exportar_estado()
            turno = cazador.evento_pendiente
            cantidad_turnos = motor.historial.cantidad_turnos()
            contexto = motor._rutas_reales
            origen = contexto.grafo.indice(100)
            espacio = contexto._espacio
            self.assertIsNone(espacio.etiqueta(origen))

            def rechazar_lote(*_):
                self.assertEqual((motor.reloj, cazador.sala_actual), (127, 101))
                self.assertIsNotNone(espacio.etiqueta(origen))
                raise CambioHistoriaIncoherente("lote rechazado")

            ejecutar_ciclo = motor.ejecutar_ciclo

            def fallar_despues_del_turno_enemigo(*args, **kwargs):
                evento = ejecutar_ciclo(*args, **kwargs)
                if evento is turno:
                    self.assertEqual((motor.reloj, cazador.sala_actual), (100, 101))
                    self.assertIsNotNone(espacio.etiqueta(origen))
                    raise RuntimeError("fallo durante la accion")
                return evento

            if fase == "accion":
                contexto_fallo = patch.object(motor, "ejecutar_ciclo", side_effect=fallar_despues_del_turno_enemigo)
                receptor, error, mensaje = None, RuntimeError, "fallo durante la accion"
            else:
                contexto_fallo = nullcontext()
                receptor, error, mensaje = rechazar_lote, CambioHistoriaIncoherente, "lote rechazado"
            with contexto_fallo, self.assertRaisesRegex(error, mensaje):
                motor.ejecutar("esperar", registrar_h3=receptor)

            self.assertEqual(motor.exportar_estado(), antes)
            self.assertEqual(motor.historial.cantidad_turnos(), cantidad_turnos)
            self.assertIs(cazador.evento_pendiente, turno)
            self.assertTrue(turno.en_cola)
            self.assertFalse(turno.cancelado)
            self.assertEqual(cazador.sala_actual, 100)
            self.assertIs(motor._rutas_reales, contexto)
            self.assertIs(motor._rutas_reales._espacio, espacio)
            self.assertIsNone(espacio.etiqueta(origen))
            self.assertFalse(espacio.esta_cerrado(origen))

            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual((motor.reloj, cazador.sala_actual, cazador.tiempo_siguiente), (127, 101, 350))

    def test_guardado_conserva_cierre_en_sala_sin_contenido_cargado(self):
        """FR-015/018: el estado de una salida no depende de cargar su sala."""
        with partida_cazador(350) as (motor, _, _), TemporaryDirectory() as carpeta:
            sala = motor.salas[102]
            salida = sala.salidas["O"]
            self.assertFalse(motor.contenido_cargado[102])
            self.assertNotIn("cerrada", salida)
            cierre = motor.programar_evento(1, "cierre_puerta", (sala, "O"))
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertFalse(cierre.en_cola)
            self.assertTrue(salida["cerrada"])
            self.assertFalse(motor.contenido_cargado[102])

            ruta = Path(carpeta) / "puerta.bin"
            guardado = motor.exportar_estado()
            guardar_estado(guardado, ruta)
            motor.restaurar_estado(cargar_estado(ruta))

            self.assertIs(motor.salas[102].salidas["O"], salida)
            self.assertTrue(salida["cerrada"])
            self.assertFalse(motor.contenido_cargado[102])
            self.assertEqual(motor.exportar_estado(), guardado)

    def test_guardado_omite_puerta_inicial_sin_cambios_en_sala_no_cargada(self):
        def preparar(precarga, *args, **kwargs):
            almacen = precarga.cliente.almacen
            pagina = almacen.leer_pagina("prueba", "v1", 1)
            pagina["salas"][2]["salidas"]["O"]["cerrada"] = False
            almacen.guardar_pagina("prueba", "v1", pagina)
            return crear_juego(precarga, *args, **kwargs)

        with patch("tests.test_turno_cazador.crear_juego", new=preparar), partida_cazador(350) as (motor, _, _):
            salida = motor.salas[102].salidas["O"]
            self.assertIs(salida["cerrada"], False)
            self.assertFalse(motor.contenido_cargado[102])
            anterior = motor.exportar_estado()
            self.assertNotIn(102, [sala.sala_id for sala in anterior.salas])

            salida["cerrada"] = True
            motor.restaurar_estado(anterior)

            self.assertIs(salida["cerrada"], False)
            self.assertFalse(motor.contenido_cargado[102])
            self.assertEqual(motor.exportar_estado(), anterior)

    def test_contexto_real_descarta_marcas_al_retroceder_y_cargar(self):
        """T031 / FR-013 y FR-018: rutas frescas tras restaurar un arco real."""
        with partida_cazador(350) as (motor, cazador, _):
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            pergamino = ObjetoInstancia("pergamino-t031", "pergamino", "inventario")
            self.assertIsNotNone(motor.jugador.inventario.recoger(pergamino))
            salida = motor.salas[100].salidas["E"]
            cierre = motor.programar_evento(110, "cierre_puerta", (motor.salas[100], "E"))
            guardado = motor.exportar_estado()

            contexto = motor._rutas_reales
            grafo = contexto.grafo
            espacio = contexto._espacio
            origen, vecino, objetivo = (grafo.indice(sala) for sala in (100, 101, 102))
            ruta_abierta = (vecino, "E", 250, 350)
            self.assertEqual(contexto.buscar(origen, objetivo, 350), ruta_abierta)

            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual((cazador.sala_actual, cazador.tiempo_siguiente), (101, 350))
            self.assertTrue(salida["cerrada"])
            self.assertIsNone(contexto.buscar(origen, objetivo, 350))
            self.assertIsNotNone(espacio.etiqueta(origen))

            self.assertTrue(motor.ejecutar("retroceso").ok)
            self.assertIsNone(espacio.etiqueta(origen))
            self.assertFalse(espacio.esta_cerrado(origen))
            self.assertTrue(cierre.en_cola)
            self.assertFalse(salida.get("cerrada", False))
            self.assertEqual(contexto.buscar(origen, objetivo, 350), ruta_abierta)

            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertTrue(salida["cerrada"])
            self.assertIsNotNone(espacio.etiqueta(origen))
            generacion = espacio.generacion
            with self.assertRaises(ValueError):
                motor.restaurar_estado(replace(guardado, reloj=-1))
            self.assertEqual(espacio.generacion, generacion)
            self.assertTrue(salida["cerrada"])

            motor.restaurar_estado(guardado)
            self.assertIs(motor._rutas_reales, contexto)
            self.assertIs(contexto.grafo, grafo)
            self.assertIs(contexto._espacio, espacio)
            self.assertIsNone(espacio.etiqueta(origen))
            self.assertFalse(espacio.esta_cerrado(origen))
            self.assertFalse(salida.get("cerrada", False))
            self.assertEqual(contexto.buscar(origen, objetivo, 350), ruta_abierta)
            restaurado = motor.enemigos_por_sala[100][0]
            self.assertTrue(motor.ejecutar("esperar").ok)
            self.assertEqual((restaurado.sala_actual, restaurado.tiempo_siguiente), (101, 350))

    def preparar_pergaminos(self, motor, cantidad):
        catalogo = motor.gestor_precarga.catalogo
        catalogo.almacen.guardar_ficha(motor.meta.catalogo_version, {
            "id": PERGAMINO, "clase": "pergamino_retroceso", "nombre": "Pergamino",
        })
        for numero in range(cantidad):
            self.assertIsNotNone(motor.jugador.inventario.recoger(
                ObjetoInstancia(f"pergamino-{numero}", PERGAMINO, "inventario")))

    def aplicar_aceleracion(self, motor):
        motor.gestor_precarga.catalogo.almacen.guardar_ficha(motor.meta.catalogo_version, {
            "id": POCION, "clase": "pocion", "nombre": "Poción",
            "modificador_velocidad": 2.0, "duracion": 100,
        })
        self.assertIsNotNone(motor.jugador.inventario.recoger(
            ObjetoInstancia("pocion-a12", POCION, "inventario")))
        self.assertTrue(motor.ejecutar("usar", "pocion-a12").ok)
        self.assertEqual((motor.reloj, motor.jugador.velocidad), (25, 200))
        expiracion = motor.jugador.evento_velocidad
        self.assertEqual((expiracion.tipo, expiracion.tiempo), ("restaurar_velocidad", 100))
        self.assertIs(expiracion.referencia[0], motor.jugador)
        self.assertTrue(expiracion.en_cola)
        self.assertFalse(expiracion.cancelado)
        return expiracion

    def comprobar_mismos_eventos(self, motor, anteriores):
        actuales = sorted(motor.cola.pendientes(), key=lambda evento: evento.secuencia)
        self.assertEqual(len(actuales), len(anteriores))
        for actual, anterior in zip(actuales, anteriores):
            self.assertIs(actual, anterior)
            self.assertTrue(actual.en_cola)
            self.assertFalse(actual.cancelado)

    def test_retroceso_reinserta_eventos_originales_y_repetir_es_determinista(self):
        with motor_terreno(250) as motor:
            self.preparar_pergaminos(motor, 1)
            expiracion = self.aplicar_aceleracion(motor)
            enemigo_origen = motor.enemigos_por_sala[100][0]
            turno_enemigo = enemigo_origen.evento_pendiente
            anteriores = sorted(motor.cola.pendientes(), key=lambda evento: evento.secuencia)
            antes = motor.exportar_estado()
            programar_real = motor.programar_evento
            turnos_jugador = []

            def observar_programacion(tiempo, tipo, referencia):
                evento = programar_real(tiempo, tipo, referencia)
                if tipo == "turno_jugador":
                    turnos_jugador.append(evento)
                return evento

            with patch.object(motor, "programar_evento", side_effect=observar_programacion):
                self.assertTrue(motor.ejecutar("mover", "E").ok)
            sustituido, vigente = turnos_jugador
            self.assertEqual((sustituido.tiempo, vigente.tiempo), (150, 200))
            self.assertGreater(vigente.secuencia, sustituido.secuencia)
            self.assertTrue(sustituido.cancelado)
            self.assertFalse(sustituido.en_cola)
            self.assertFalse(expiracion.en_cola)
            self.assertEqual((motor.reloj, motor.jugador.posicion_actual, motor.jugador.velocidad),
                             (200, 101, 100))
            despues = motor.exportar_estado()
            self.assertLess(despues.jugador.vida, antes.jugador.vida)
            self.assertNotEqual(despues.rng_estado, antes.rng_estado)

            self.assertTrue(motor.ejecutar("retroceso").ok)
            self.comprobar_mismos_eventos(motor, anteriores)
            self.assertIs(motor.jugador.evento_velocidad, expiracion)
            self.assertIs(expiracion.referencia[0], motor.jugador)
            self.assertIs(enemigo_origen.evento_pendiente, turno_enemigo)
            self.assertIs(turno_enemigo.referencia, enemigo_origen)
            self.assertTrue(vigente.cancelado)
            self.assertEqual(motor.jugador.inventario.contar(PERGAMINO), 0)
            esperado = replace(antes, jugador=replace(antes.jugador, inventario=[]))
            self.assertEqual(motor.exportar_estado(), esperado)

            self.assertTrue(motor.ejecutar("mover", "E").ok)
            esperado = replace(despues, jugador=replace(despues.jugador, inventario=[]))
            self.assertEqual(motor.exportar_estado(), esperado)

    def test_carga_reconstruye_eventos_y_referencias_del_efecto_activo(self):
        with motor_terreno(250) as motor:
            expiracion = self.aplicar_aceleracion(motor)
            enemigo_anterior = motor.enemigos_por_sala[100][0]
            turno_anterior = enemigo_anterior.evento_pendiente
            guardado = motor.exportar_estado()
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            despues = motor.exportar_estado()

            motor.restaurar_estado(guardado)
            self.assertEqual(motor.exportar_estado(), guardado)
            self.assertEqual(motor.historial.cantidad_turnos(), 0)
            restaurado = motor.jugador.evento_velocidad
            enemigo = motor.enemigos_por_sala[100][0]
            turno = enemigo.evento_pendiente
            self.assertIsNot(restaurado, expiracion)
            self.assertIsNot(turno, turno_anterior)
            self.assertIs(restaurado.referencia[0], motor.jugador)
            self.assertEqual(restaurado.referencia[1], 100)
            self.assertIs(turno.referencia, enemigo)
            self.assertCountEqual(motor.cola.pendientes(), (restaurado, turno))
            for evento in (restaurado, turno):
                self.assertTrue(evento.en_cola)
                self.assertFalse(evento.cancelado)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            self.assertIsNone(motor.jugador.evento_velocidad)
            self.assertFalse(restaurado.en_cola)
            self.assertEqual(motor.exportar_estado(), despues)

    def test_pergamino_solo_revierte_cinco_de_seis_acciones(self):
        with motor_terreno(velocidad=1000) as motor:
            self.preparar_pergaminos(motor, 6)
            for ordinal in range(1, 7):
                self.assertTrue(motor.ejecutar("esperar").ok)
                self.assertEqual((motor.reloj, motor.acciones_jugador), (ordinal * 10, ordinal))
            self.assertEqual(motor.historial.cantidad_turnos(), 5)
            for ordinal in range(5, 0, -1):
                self.assertTrue(motor.ejecutar("retroceso").ok)
                self.assertEqual((motor.reloj, motor.acciones_jugador), (ordinal * 10, ordinal))
            self.assertEqual(motor.historial.cantidad_turnos(), 0)
            self.assertEqual(motor.jugador.inventario.contar(PERGAMINO), 1)
            antes = motor.exportar_estado()
            self.assertFalse(motor.ejecutar("retroceso").ok)
            self.assertEqual(motor.exportar_estado(), antes)

    def test_restauracion_fallida_conserva_efecto_agenda_y_turno_reversible(self):
        with motor_terreno(250) as motor:
            self.preparar_pergaminos(motor, 1)
            expiracion = self.aplicar_aceleracion(motor)
            antes = motor.exportar_estado()
            historial = motor.historial
            anteriores = sorted(motor.cola.pendientes(), key=lambda evento: evento.secuencia)
            evento_invalido = replace(antes.eventos[0], secuencia=antes.siguiente_secuencia)
            agenda_invalida = replace(antes, eventos=[evento_invalido, *antes.eventos[1:]])
            salas = [
                replace(sala, enemigos=[replace(enemigo, tipo="enemigo-inexistente")
                                         for enemigo in sala.enemigos])
                if sala.sala_id == 100 else sala for sala in antes.salas
            ]
            ficha_ausente = replace(antes, salas=salas)
            for estado, error, mensaje in (
                (agenda_invalida, ValueError, "tiempo o secuencia"),
                (ficha_ausente, ErrorCripta, "enemigo-inexistente"),
            ):
                with self.subTest(mensaje=mensaje):
                    with self.assertRaisesRegex(error, mensaje):
                        motor.restaurar_estado(estado)
                    self.assertEqual(motor.exportar_estado(), antes)
                    self.assertIs(motor.historial, historial)
                    self.assertEqual(historial.cantidad_turnos(), 1)
                    self.assertIs(motor.jugador.evento_velocidad, expiracion)
                    self.comprobar_mismos_eventos(motor, anteriores)
            self.assertTrue(motor.ejecutar("retroceso").ok)
            self.assertEqual((motor.reloj, motor.jugador.velocidad, motor.acciones_jugador),
                             (0, 100, 0))
            self.assertIsNone(motor.jugador.evento_velocidad)
            self.assertTrue(expiracion.cancelado)
            self.assertEqual(motor.jugador.inventario.contar(POCION), 1)
            self.assertEqual(motor.jugador.inventario.contar(PERGAMINO), 0)
