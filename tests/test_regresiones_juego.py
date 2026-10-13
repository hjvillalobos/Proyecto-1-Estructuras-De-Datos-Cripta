import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from datos.guardado_binario import cargar_estado, guardar_estado
from modelo.inventario import Inventario
from modelo.juego import Motor
from modelo.snapshots import MetaPartida
from modelo.tipos import FichaCatalogo, InstanciaEnemigo, Jugador, ObjetoInstancia, Sala, Trampa


class TestRegresionesJuego(unittest.TestCase):
    def setUp(self):
        self.fichas = [
            FichaCatalogo("llave", "llave", "Llave", {"abre": "puerta_salida"}),
            FichaCatalogo("daga", "arma", "Daga", {"ataque_bonus": 3}),
            FichaCatalogo("espada", "arma", "Espada", {"ataque_bonus": 5}),
            FichaCatalogo("coraza", "armadura", "Coraza", {"defensa_bonus": 2}),
            FichaCatalogo("pocion", "pocion", "Pocion", {"cura": 8}),
            FichaCatalogo("velocidad", "pocion", "Velocidad",
                          {"modificador_velocidad": 2, "duracion": 300}),
            FichaCatalogo("antidoto", "antidoto", "Antidoto", {}),
            FichaCatalogo("antorcha", "antorcha", "Antorcha", {"duracion": 200}),
            FichaCatalogo("pergamino", "pergamino_retroceso", "Pergamino", {}),
            FichaCatalogo("trampa", "trampa", "Dardos", {"daño": 4, "rearme": 300}),
            FichaCatalogo("enemigo", "enemigo", "Enemigo",
                          {"vida_max": 30, "ataque": 3, "defensa": 1,
                           "velocidad": 100, "comportamiento": "guardián", "suelta": ["pocion"]}),
        ]
        jugador = Jugador(vida=30, vida_max=30, ataque=6, defensa=2, velocidad=100,
                          tiempo_siguiente=0, inventario=Inventario(10),
                          posicion_actual=1, llaves_obtenidas=[])
        salas = [Sala(1, "Entrada", {"E": {"sala": 2, "cerrada": True, "llave": "llave"}}),
                 Sala(2, "Salida", {"O": {"sala": 1}})]
        self.motor = Motor(jugador, salas, semilla=42)
        self.motor.meta = MetaPartida("prueba", "v1", "cat1", 42)
        self.motor.gestor_precarga = SimpleNamespace(
            catalogo=SimpleNamespace(obtener_fichas=self._obtener_fichas),
            generales={"jugador": {"velocidad": 100}}, anticipar=lambda sala: False)
        self.motor.contenido_cargado[1] = self.motor.contenido_cargado[2] = True
        self.motor.sala_salida = 2
        self.motor.llave_salida = "llave"

    def _obtener_fichas(self, ids):
        return [next(f for f in self.fichas if f.id == id_tipo) for id_tipo in ids]

    def _inventario(self, tipo, id_instancia=None):
        objeto = ObjetoInstancia(id_instancia or tipo, tipo, "inventario")
        self.motor.jugador.inventario.recoger(objeto)
        return objeto

    def _suelo(self, tipo, id_instancia=None, sala=1):
        objeto = ObjetoInstancia(id_instancia or tipo, tipo, "suelo", sala)
        self.motor.objetos_en_suelo[sala].append(objeto)
        return objeto

    def _enemigo(self, sala=1, velocidad=100, comportamiento="guardián"):
        enemigo = InstanciaEnemigo(
            vida=30, vida_max=30, ataque=3, defensa=1, velocidad=velocidad,
            tiempo_siguiente=0, id_instancia="enemigo-1", tipo_catalogo="enemigo",
            comportamiento=comportamiento)
        self.motor.enemigos_por_sala[sala].append(enemigo)
        self.motor.activar_enemigos_de_sala(sala, [enemigo])
        return enemigo

    def _accion(self, accion, argumento=None):
        resultado = self.motor.ejecutar(accion, argumento)
        self.assertTrue(resultado.ok, resultado.mensaje)
        return resultado

    def _agenda(self):
        return [(e.tiempo, e.secuencia, e.tipo) for e in self.motor.cola.pendientes()]

    def test_llave_se_valida_por_id_y_no_por_abre(self):
        self._inventario("llave")
        self._accion("abrir", "E")
        self.assertFalse(self.motor.salas[1].salidas["E"]["cerrada"])
        self.assertEqual(self.motor.jugador.inventario.contar("llave"), 1)

    def test_sin_llave_no_se_abre_ni_se_consume_tiempo(self):
        self.assertFalse(self.motor.ejecutar("abrir", "E").ok)
        self.assertEqual(self.motor.reloj, 0)
        self.assertEqual(self.motor.historial.cantidad_turnos(), 0)

    def test_victoria_al_entrar_por_puerta_abierta_aunque_se_suelte_la_llave(self):
        self._inventario("llave")
        self._accion("abrir", "E")
        self._accion("soltar", "llave")
        instante_entrada = self.motor.reloj
        self._accion("mover", "E")
        self.assertEqual(self.motor.resultado, "victoria")
        self.assertEqual(self.motor.reloj, instante_entrada)

    def test_retroceso_de_recoger_restaura_objeto_y_orden_del_suelo(self):
        self._inventario("pergamino")
        primero = self._suelo("daga")
        segundo = self._suelo("pocion")
        self._accion("recoger", "daga")
        self._accion("retroceso")
        self.assertEqual(self.motor.objetos_en_suelo[1], [primero, segundo])
        self.assertEqual((primero.ubicacion, primero.sala), ("suelo", 1))
        self.assertEqual(self.motor.jugador.inventario.contar("daga"), 0)

    def test_retroceso_de_soltar_no_duplica_y_recupera_el_mismo_nodo(self):
        self._inventario("daga")
        self._inventario("pergamino")
        inventario = self.motor.jugador.inventario
        nodo = inventario.cursor
        self._accion("soltar", "daga")
        self._accion("retroceso")
        self.assertIs(inventario.cursor, nodo)
        self.assertEqual(self.motor.objetos_en_suelo[1], [])
        self.assertEqual((nodo.objeto.ubicacion, nodo.objeto.sala), ("inventario", None))

    def test_dos_retrocesos_recoger_y_soltar_no_corrompen_la_lista(self):
        self._inventario("pergamino", "p1")
        self._inventario("pergamino", "p2")
        objeto = self._suelo("daga")
        self._accion("recoger", "daga")
        self._accion("soltar", "daga")
        self._accion("retroceso")
        self._accion("retroceso")
        self.assertEqual(list(self.motor.jugador.inventario), [])
        self.assertEqual(self.motor.objetos_en_suelo[1], [objeto])
        self.assertEqual(self.motor.reloj, 0)
        self.assertEqual(self.motor.acciones_jugador, 0)

    def test_recoger_pergamino_no_se_revierte(self):
        self._inventario("pergamino", "p1")
        self._suelo("pergamino", "p2")
        self._accion("recoger", "p2")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.inventario.contar("pergamino"), 1)
        self.assertEqual(self.motor.objetos_en_suelo[1], [])

    def test_soltar_pergamino_no_se_revierte(self):
        self._inventario("pergamino", "p1")
        self._inventario("pergamino", "p2")
        self._accion("soltar", "p2")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.inventario.contar("pergamino"), 0)
        self.assertEqual([o.id_instancia for o in self.motor.objetos_en_suelo[1]], ["p2"])

    def test_inventario_lleno_rechaza_sin_cambiar_estado(self):
        self.motor.jugador.inventario.capacidad_max = 1
        self._inventario("daga")
        objeto = self._suelo("pocion")
        self.assertFalse(self.motor.ejecutar("recoger", "pocion").ok)
        self.assertEqual(self.motor.objetos_en_suelo[1], [objeto])
        self.assertEqual(self.motor.reloj, 0)

    def test_retroceso_recupera_evento_enemigo_extraido_y_su_secuencia(self):
        self._inventario("pergamino")
        enemigo = self._enemigo()
        pendiente = enemigo.evento_pendiente
        agenda = self._agenda()
        vida = self.motor.jugador.vida
        self._accion("esperar")
        self._accion("retroceso")
        self.assertEqual(self._agenda(), agenda)
        self.assertIs(enemigo.evento_pendiente, pendiente)
        self.assertEqual(enemigo.tiempo_siguiente, 100)
        self.assertEqual(self.motor.jugador.vida, vida)
        self._accion("esperar")
        self.assertLess(self.motor.jugador.vida, vida)

    def test_eventos_creados_y_ejecutados_en_intervalo_no_reviven_al_deshacer(self):
        self._inventario("pergamino")
        self._enemigo(velocidad=400)
        agenda = self._agenda()
        self._accion("esperar")
        self._accion("retroceso")
        self.assertEqual(self._agenda(), agenda)

    def test_retroceso_restaura_azar_y_repetir_ataque_da_mismo_dano(self):
        self._inventario("pergamino")
        enemigo = self._enemigo()
        azar = self.motor.azar.getstate()
        self._accion("atacar", enemigo.id_instancia)
        vida_enemigo = enemigo.vida
        vida_jugador = self.motor.jugador.vida
        self._accion("retroceso")
        self.assertEqual(self.motor.azar.getstate(), azar)
        self._accion("atacar", enemigo.id_instancia)
        self.assertEqual((enemigo.vida, self.motor.jugador.vida), (vida_enemigo, vida_jugador))

    def test_deshacer_muerte_restaura_eventos_y_retira_botin(self):
        self._inventario("pergamino")
        enemigo = self._enemigo()
        enemigo.vida = 1
        self._accion("atacar", enemigo.id_instancia)
        self._accion("retroceso")
        self.assertEqual(enemigo.vida, 1)
        self.assertEqual(self.motor.enemigos_derrotados, 0)
        self.assertEqual(self.motor.objetos_en_suelo[1], [])
        self.assertTrue(any(e.referencia is enemigo for e in self.motor.cola.pendientes()))

    def test_retroceso_trampa_restaura_vida_armado_y_agenda(self):
        self._inventario("pergamino")
        self.motor.salas[1].salidas["E"]["cerrada"] = False
        self.motor.sala_salida = None
        trampa = Trampa("t1", "trampa")
        self.motor.salas[2].trampa = trampa
        self._accion("mover", "E")
        self.assertEqual(self.motor.jugador.vida, 26)
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.vida, 30)
        self.assertTrue(trampa.armada)
        self.assertEqual(self.motor.jugador.posicion_actual, 1)
        self.assertEqual(self._agenda(), [])

    def test_retroceso_rearme_recupera_trampa_desarmada_y_evento(self):
        self._inventario("pergamino")
        trampa = Trampa("t1", "trampa", armada=False)
        self.motor.salas[1].trampa = trampa
        self.motor.programar_evento(50, "rearmar_trampa", trampa)
        self._accion("esperar")
        self.assertTrue(trampa.armada)
        self._accion("retroceso")
        self.assertFalse(trampa.armada)
        self.assertEqual([e.tipo for e in self.motor.cola.pendientes()], ["rearmar_trampa"])

    def test_retroceso_veneno_restaura_vida_y_siguiente_pulso(self):
        self._inventario("pergamino")
        self.motor.efectos.aplicar_veneno(self.motor.jugador, 2)
        agenda = self._agenda()
        self._accion("esperar")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.vida, 30)
        self.assertCountEqual(self._agenda(), agenda)
        self._accion("esperar")
        self.assertEqual(self.motor.jugador.vida, 28)

    def test_retroceso_antidoto_restaura_veneno_y_consumible(self):
        self._inventario("pergamino")
        self._inventario("antidoto")
        self.motor.efectos.aplicar_veneno(self.motor.jugador, 2)
        self._accion("usar", "antidoto")
        self.assertIsNone(self.motor.jugador.veneno)
        self._accion("retroceso")
        self.assertIsNotNone(self.motor.jugador.veneno)
        self.assertEqual(self.motor.jugador.inventario.contar("antidoto"), 1)
        self._accion("esperar")
        self.assertEqual(self.motor.jugador.vida, 28)

    def test_retroceso_pocion_restaura_vida_y_nodo_consumido(self):
        self._inventario("pergamino")
        self._inventario("pocion")
        self.motor.jugador.vida = 10
        self._accion("usar", "pocion")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.vida, 10)
        self.assertEqual(self.motor.jugador.inventario.contar("pocion"), 1)

    def test_soltar_y_reequipar_no_acumula_bonus(self):
        for tipo, atributo, base, bonus in (("daga", "ataque", 6, 3), ("coraza", "defensa", 2, 2)):
            with self.subTest(tipo=tipo):
                self._inventario(tipo)
                self._accion("equipar", tipo)
                self.assertEqual(getattr(self.motor.jugador, atributo), base + bonus)
                self._accion("soltar", tipo)
                self.assertEqual(getattr(self.motor.jugador, atributo), base)
                self._accion("recoger", tipo)
                self._accion("equipar", tipo)
                self.assertEqual(getattr(self.motor.jugador, atributo), base + bonus)

    def test_retroceso_sustituir_arma_recupera_equipo_bonus_y_orden(self):
        self._inventario("pergamino")
        self._inventario("daga")
        self._inventario("espada")
        self._accion("equipar", "daga")
        orden = list(self.motor.jugador.inventario)
        self._accion("equipar", "espada")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.ataque, 9)
        self.assertEqual(self.motor.jugador.inventario.arma_equipada_objeto.tipo_catalogo, "daga")
        self.assertEqual(list(self.motor.jugador.inventario), [o for o in orden if o.tipo_catalogo != "pergamino"])

    def test_retroceso_soltar_equipo_restaura_bonus_y_marca(self):
        self._inventario("pergamino")
        self._inventario("daga")
        self._accion("equipar", "daga")
        self._accion("soltar", "daga")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.ataque, 9)
        self.assertEqual(self.motor.jugador.inventario.arma_equipada_objeto.tipo_catalogo, "daga")

    def test_consultas_de_vista_y_llave_no_mueven_cursor(self):
        self._inventario("daga")
        self._inventario("llave")
        self._inventario("coraza")
        cursor = self.motor.jugador.inventario.cursor
        self.motor.estado_vista()
        self.motor.inventario_vista("nombre")
        self.motor._ids_en_uso()
        self.assertTrue(self.motor._tiene_llave("llave"))
        self.assertIs(self.motor.jugador.inventario.cursor, cursor)

    def test_accion_rechazada_conserva_cursor_e_historial_previo(self):
        self._inventario("daga")
        self._inventario("llave")
        self._accion("esperar")
        cursor = self.motor.jugador.inventario.cursor
        self.assertFalse(self.motor.ejecutar("equipar", "llave").ok)
        self.assertIs(self.motor.jugador.inventario.cursor, cursor)
        self.assertEqual(self.motor.historial.cantidad_turnos(), 1)
        self.assertEqual(self.motor.reloj, 100)

    def test_antorcha_consumida_sigue_visible_hasta_su_apagado(self):
        antorcha = self._inventario("antorcha")
        self._accion("usar", "antorcha")
        self.assertTrue(antorcha.encendida)
        self.assertEqual(self.motor.jugador.inventario.contar("antorcha"), 0)
        self.assertIn("antorcha", self.motor.estado_vista().efectos)
        self._accion("esperar")
        self._accion("esperar")
        self.assertFalse(antorcha.encendida)
        self.assertNotIn("antorcha", self.motor.estado_vista().efectos)

    def test_retroceso_encender_antorcha_restaura_objeto_y_cancela_apagado(self):
        self._inventario("pergamino")
        antorcha = self._inventario("antorcha")
        self._accion("usar", "antorcha")
        self._accion("retroceso")
        self.assertFalse(antorcha.encendida)
        self.assertEqual(self.motor.jugador.inventario.contar("antorcha"), 1)
        self.assertEqual(self.motor.efectos.antorchas_encendidas, [])
        self.assertEqual(self._agenda(), [])

    def test_retroceso_apagado_restaura_antorcha_activa(self):
        self._inventario("pergamino")
        antorcha = self._inventario("antorcha")
        self._accion("usar", "antorcha")
        self._accion("esperar")
        self._accion("esperar")
        self._accion("retroceso")
        self.assertTrue(antorcha.encendida)
        self.assertIn("antorcha", self.motor.estado_vista().efectos)

    def test_guardado_binario_conserva_antorcha_y_fin_de_velocidad(self):
        self._inventario("antorcha")
        self._inventario("velocidad")
        self._accion("usar", "antorcha")
        self._accion("usar", "velocidad")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "partida.bin")
            guardar_estado(self.motor.exportar_estado(), ruta)
            self.motor.restaurar_estado(cargar_estado(ruta))
        self.assertIn("antorcha", self.motor.estado_vista().efectos)
        self.assertEqual(self.motor.jugador.velocidad, 200)
        for _ in range(7):
            self._accion("esperar")
        self.assertEqual(self.motor.jugador.velocidad, 100)
        self.assertNotIn("antorcha", self.motor.estado_vista().efectos)

    def test_cargar_restaura_puertas_de_salas_no_visitadas(self):
        puerta = self.motor.salas[1].salidas["E"]
        self.motor.salas[2].salidas["N"] = {"sala": 1, "cerrada": True}
        self.motor._puertas_iniciales.append((2, "N", True, True))
        self.motor.contenido_cargado[2] = False
        estado = self.motor.exportar_estado()
        puerta["cerrada"] = False
        self.motor.salas[2].salidas["N"]["cerrada"] = False
        self.motor.restaurar_estado(estado)
        self.assertTrue(puerta["cerrada"])
        self.assertTrue(self.motor.salas[2].salidas["N"]["cerrada"])

    def test_guardado_cargado_continua_con_los_mismos_eventos_y_azar(self):
        self._enemigo()
        self._inventario("velocidad")
        self._accion("usar", "velocidad")
        estado = self.motor.exportar_estado()
        for _ in range(4):
            self._accion("esperar")
        esperado = self.motor.exportar_estado()
        self.motor.restaurar_estado(estado)
        for _ in range(4):
            self._accion("esperar")
        self.assertEqual(self.motor.exportar_estado(), esperado)

    def test_cada_accion_refresca_rastro_y_retroceso_lo_restaura(self):
        self._inventario("pergamino")
        self._accion("esperar")
        self._accion("esperar")
        self.assertEqual(self.motor.registro_rastro.tiempo_de(1), 100)
        self._accion("retroceso")
        self.assertEqual(self.motor.registro_rastro.tiempo_de(1), 0)

    def test_abrir_y_retroceder_cancela_cierre_automatico(self):
        self._inventario("pergamino")
        self._inventario("llave")
        self.motor.salas[1].salidas["E"]["cierre_automatico"] = 200
        self._accion("abrir", "E")
        self._accion("retroceso")
        self.assertTrue(self.motor.salas[1].salidas["E"]["cerrada"])
        self.assertEqual(self._agenda(), [])

    def test_retroceso_de_primera_entrada_vuelve_a_dormir_enemigos(self):
        self._inventario("pergamino")
        self.motor.salas[1].salidas["E"]["cerrada"] = False
        self.motor.sala_salida = None
        enemigo = self._enemigo(sala=2, velocidad=400)
        self.motor.cola = type(self.motor.cola)()
        self.motor.historial = type(self.motor.historial)(self.motor.registro_rastro, self.motor.cola)
        enemigo.sala_actual = None
        enemigo.evento_pendiente = None
        enemigo.tiempo_siguiente = 0
        self._accion("mover", "E")
        self.assertEqual(enemigo.sala_actual, 2)
        self._accion("retroceso")
        self.assertIsNone(enemigo.sala_actual)
        self.assertIsNone(enemigo.evento_pendiente)
        self.assertEqual(enemigo.tiempo_siguiente, 0)
        self.assertEqual(self._agenda(), [])
        self._accion("mover", "E")
        self.assertEqual(enemigo.sala_actual, 2)

    def test_retroceso_regeneracion_restaura_vida_y_evento_original(self):
        self._inventario("pergamino")
        enemigo = self._enemigo(sala=2)
        enemigo.vida = 10
        self.motor.efectos.aplicar_regeneracion(enemigo, 4, intervalo=50)
        agenda = self._agenda()
        self._accion("esperar")
        self.assertEqual(enemigo.vida, 14)
        self._accion("retroceso")
        self.assertEqual(enemigo.vida, 10)
        self.assertCountEqual(self._agenda(), agenda)

    def test_retroceso_velocidad_restaura_pocion_y_fin_del_efecto(self):
        self._inventario("pergamino", "p1")
        self._inventario("pergamino", "p2")
        self._inventario("velocidad")
        self._accion("usar", "velocidad")
        self._accion("esperar")
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.velocidad, 200)
        self.assertTrue(any(e.tipo == "restaurar_velocidad" for e in self.motor.cola.pendientes()))
        self._accion("retroceso")
        self.assertEqual(self.motor.jugador.velocidad, 100)
        self.assertEqual(self.motor.jugador.inventario.contar("velocidad"), 1)
        self.assertEqual(self._agenda(), [])

    def test_retroceso_despues_de_derrota_restaura_partida_activa(self):
        self._inventario("pergamino")
        enemigo = self._enemigo()
        enemigo.ataque = 100
        self._accion("esperar")
        self.assertEqual(self.motor.resultado, "derrota")
        self._accion("retroceso")
        self.assertFalse(self.motor.terminado)
        self.assertIsNone(self.motor.resultado)
        self.assertEqual(self.motor.jugador.vida, 30)

    def test_uso_de_pergamino_desde_gui_no_consume_tiempo(self):
        self._inventario("pergamino")
        self._accion("esperar")
        self._accion("usar", "pergamino")
        self.assertEqual(self.motor.reloj, 0)
        self.assertEqual(self.motor.acciones_jugador, 0)
        self.assertEqual(self.motor.jugador.inventario.contar("pergamino"), 0)

    def test_retroceso_conserva_referencia_a_predecesor_pergamino_consumido(self):
        self._inventario("pergamino", "p1")
        self._inventario("daga")
        self._inventario("pergamino", "p2")
        self._inventario("coraza")
        self._accion("soltar", "daga")
        self._accion("soltar", "coraza")
        self._accion("retroceso")
        self._accion("retroceso")
        self.assertEqual([o.tipo_catalogo for o in self.motor.jugador.inventario], ["daga", "coraza"])
        self.assertEqual(self.motor.jugador.inventario.tamaño, 2)
        self.assertEqual(self.motor.objetos_en_suelo[1], [])
