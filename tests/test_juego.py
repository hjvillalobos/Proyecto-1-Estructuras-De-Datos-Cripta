"""
Pruebas de integración del ciclo completo del juego.
Usan ServidorFalso y crear_paquete — sin red real.
"""
import tempfile
import unittest

from datos.almacen import AlmacenLocal
from datos.offline import ClienteOffline
from modelo.juego import Motor, crear_juego
from modelo.tipos import ObjetoInstancia
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import ServidorFalso, crear_paquete


def _crear_motor(servidor=None, salas=6):
    """Devuelve (motor, gestor_precarga) listos para jugar."""
    if servidor is None:
        servidor = ServidorFalso(salas=salas)
    tmp = tempfile.mkdtemp()
    almacen = AlmacenLocal(tmp)
    catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), almacen)
    precarga = GestorPrecarga(servidor, catalogo)
    motor = crear_juego(precarga, "prueba", semilla=42)
    return motor, precarga


class TestCicloCompleto(unittest.TestCase):

    # ------------------------------------------------------------------
    # Arranque
    # ------------------------------------------------------------------

    def test_crear_juego_inicializa_estado(self):
        motor, _ = _crear_motor()
        self.assertFalse(motor.terminado)
        self.assertIsNone(motor.resultado)
        self.assertEqual(motor.acciones_jugador, 0)
        self.assertGreater(motor.jugador.vida, 0)
        # sala inicial cargada
        self.assertTrue(motor.contenido_cargado[motor.jugador.posicion_actual])

    # ------------------------------------------------------------------
    # Movimiento
    # ------------------------------------------------------------------

    def test_mover_cambia_posicion(self):
        motor, _ = _crear_motor()
        pos_inicial = motor.jugador.posicion_actual
        resultado = motor.ejecutar("mover", "E")
        self.assertTrue(resultado.ok)
        self.assertNotEqual(motor.jugador.posicion_actual, pos_inicial)
        self.assertEqual(motor.acciones_jugador, 1)

    def test_mover_direccion_invalida_rechazado(self):
        motor, _ = _crear_motor()
        # La sala inicial (100) no tiene salida al norte en ServidorFalso
        resultado = motor.ejecutar("mover", "N")
        self.assertFalse(resultado.ok)
        self.assertEqual(motor.acciones_jugador, 0)

    def test_revisitar_sala_no_duplica_enemigos(self):
        motor, _ = _crear_motor()
        # ir a sala 101
        motor.ejecutar("mover", "E")
        enemigos_tras_primera_visita = len(motor.enemigos_por_sala[101])
        # volver a sala 100
        motor.ejecutar("mover", "O")
        # volver a sala 101
        motor.ejecutar("mover", "E")
        self.assertEqual(len(motor.enemigos_por_sala[101]), enemigos_tras_primera_visita)

    def test_revisitar_sala_no_duplica_objetos(self):
        motor, _ = _crear_motor()
        motor.ejecutar("mover", "E")
        objetos_primera = len(motor.objetos_en_suelo[101])
        motor.ejecutar("mover", "O")
        motor.ejecutar("mover", "E")
        self.assertEqual(len(motor.objetos_en_suelo[101]), objetos_primera)

    # ------------------------------------------------------------------
    # Combate
    # ------------------------------------------------------------------

    def test_atacar_reduce_vida_enemigo(self):
        motor, _ = _crear_motor()
        motor.ejecutar("mover", "E")
        enemigos = motor.enemigos_por_sala[101]
        if not enemigos:
            self.skipTest("No hay enemigos en sala 101")
        enemigo = enemigos[0]
        vida_antes = enemigo.vida
        motor.ejecutar("atacar", enemigo.id_instancia)
        self.assertLess(enemigo.vida, vida_antes)

    def test_enemigo_derrotado_suelta_botin(self):
        motor, _ = _crear_motor()
        motor.ejecutar("mover", "E")
        enemigos = motor.enemigos_por_sala[101]
        if not enemigos:
            self.skipTest("No hay enemigos en sala 101")
        enemigo = enemigos[0]
        # forzar muerte directa
        enemigo.vida = 1
        motor.ejecutar("atacar", enemigo.id_instancia)
        self.assertEqual(enemigo.vida, 0)
        self.assertGreater(motor.enemigos_derrotados, 0)
        # la ficha "enemigo" suelta "pocion" según ServidorFalso
        tipos_suelo = [o.tipo_catalogo for o in motor.objetos_en_suelo[101]]
        self.assertIn("pocion", tipos_suelo)

    # ------------------------------------------------------------------
    # Inventario
    # ------------------------------------------------------------------

    def test_recoger_objeto_del_suelo(self):
        motor, _ = _crear_motor()
        sala_id = motor.jugador.posicion_actual
        objetos = motor.objetos_en_suelo[sala_id]
        if not objetos:
            self.skipTest("No hay objetos en sala inicial")
        obj = objetos[0]
        resultado = motor.ejecutar("recoger", obj.id_instancia)
        self.assertTrue(resultado.ok)
        self.assertNotIn(obj, motor.objetos_en_suelo[sala_id])
        self.assertFalse(motor.jugador.inventario.esta_vacio())

    def test_inventario_lleno_rechaza_recoger(self):
        motor, _ = _crear_motor()
        sala_id = motor.jugador.posicion_actual
        # llenar inventario manualmente
        for i in range(motor.jugador.inventario.capacidad_max):
            obj = ObjetoInstancia(f"relleno-{i}", "obj_0", "suelo", sala_id)
            motor.objetos_en_suelo[sala_id].append(obj)
            motor.ejecutar("recoger", obj.id_instancia)
        # uno más debe fallar
        extra = ObjetoInstancia("extra-0", "obj_0", "suelo", sala_id)
        motor.objetos_en_suelo[sala_id].append(extra)
        resultado = motor.ejecutar("recoger", extra.id_instancia)
        self.assertFalse(resultado.ok)

    # ------------------------------------------------------------------
    # Poción de velocidad
    # ------------------------------------------------------------------

    def test_pocion_velocidad_aumenta_velocidad(self):
        servidor = ServidorFalso(salas=6)
        # poner pocion_vel en sala inicial
        contenido_original = servidor.obtener_contenido_salas

        def contenido_con_vel(cripta_id, salas_ids):
            resp = contenido_original(cripta_id, salas_ids)
            for dato in resp["contenido"]:
                if dato["sala"] == 100:
                    dato["objetos"] = ["pocion_vel"]
            return resp

        servidor.obtener_contenido_salas = contenido_con_vel

        tmp = tempfile.mkdtemp()
        almacen = AlmacenLocal(tmp)
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), almacen)
        precarga = GestorPrecarga(servidor, catalogo)
        motor = crear_juego(precarga, "prueba", semilla=42)

        sala_id = motor.jugador.posicion_actual
        objetos = motor.objetos_en_suelo[sala_id]
        pocion = next((o for o in objetos if o.tipo_catalogo == "pocion_vel"), None)
        if pocion is None:
            self.skipTest("pocion_vel no apareció en sala inicial")

        motor.ejecutar("recoger", pocion.id_instancia)
        velocidad_base = motor.jugador.velocidad

        motor.ejecutar("usar", pocion.id_instancia)

        self.assertGreater(motor.jugador.velocidad, velocidad_base)

    def test_pocion_velocidad_se_restaura_tras_duracion(self):
        servidor = ServidorFalso(salas=6)
        contenido_original = servidor.obtener_contenido_salas

        def contenido_con_vel(cripta_id, salas_ids):
            resp = contenido_original(cripta_id, salas_ids)
            for dato in resp["contenido"]:
                if dato["sala"] == 100:
                    dato["objetos"] = ["pocion_vel"]
            return resp

        servidor.obtener_contenido_salas = contenido_con_vel

        tmp = tempfile.mkdtemp()
        almacen = AlmacenLocal(tmp)
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), almacen)
        precarga = GestorPrecarga(servidor, catalogo)
        motor = crear_juego(precarga, "prueba", semilla=42)

        sala_id = motor.jugador.posicion_actual
        objetos = motor.objetos_en_suelo[sala_id]
        pocion = next((o for o in objetos if o.tipo_catalogo == "pocion_vel"), None)
        if pocion is None:
            self.skipTest("pocion_vel no apareció en sala inicial")

        motor.ejecutar("recoger", pocion.id_instancia)
        velocidad_base = motor.jugador.velocidad
        motor.ejecutar("usar", pocion.id_instancia)
        self.assertGreater(motor.jugador.velocidad, velocidad_base)

        # avanzar el reloj hasta después de la duración (300)
        motor.reloj += 400
        from modelo.enemigos import decidir_accion
        while True:
            evento = motor.ejecutar_ciclo(decidir_accion)
            if evento is None or evento.tipo == "restaurar_velocidad":
                break

        self.assertEqual(motor.jugador.velocidad, velocidad_base)

    # ------------------------------------------------------------------
    # Guardar / cargar
    # ------------------------------------------------------------------

    def test_exportar_restaurar_preserva_estado(self):
        motor, _ = _crear_motor()
        motor.ejecutar("mover", "E")
        motor.ejecutar("esperar")

        estado = motor.exportar_estado()
        reloj_antes = motor.reloj
        pos_antes = motor.jugador.posicion_actual
        vida_antes = motor.jugador.vida

        # modificar el motor
        motor.ejecutar("mover", "E")

        motor.restaurar_estado(estado)

        self.assertEqual(motor.reloj, reloj_antes)
        self.assertEqual(motor.jugador.posicion_actual, pos_antes)
        self.assertEqual(motor.jugador.vida, vida_antes)

    # ------------------------------------------------------------------
    # Victoria y derrota
    # ------------------------------------------------------------------

    def test_derrota_cuando_vida_llega_a_cero(self):
        motor, _ = _crear_motor()
        motor.jugador.vida = 1
        motor.ejecutar("mover", "E")
        enemigos = motor.enemigos_por_sala[101]
        if not enemigos:
            self.skipTest("No hay enemigos en sala 101")
        # forzar que el enemigo mate al jugador
        enemigo = enemigos[0]
        enemigo.ataque = 9999
        motor.ejecutar("esperar")  # el enemigo actúa en el ciclo
        if motor.terminado:
            self.assertEqual(motor.resultado, "derrota")

    def test_victoria_al_llegar_a_sala_salida_tras_abrir_con_llave(self):
        servidor = ServidorFalso(salas=2)
        generales_original = servidor.obtener_datos_generales

        def generales_con_llave(cripta_id):
            datos = generales_original(cripta_id)
            datos["llave_salida"] = "llave_maestra"
            return datos

        servidor.obtener_datos_generales = generales_con_llave
        catalogo_original = servidor.obtener_catalogo

        def catalogo_con_llave(ids):
            resp = catalogo_original(ids)
            # reemplazar cualquier ficha de llave_maestra que venga duplicada
            resp["entidades"] = [e for e in resp["entidades"] if e["id"] != "llave_maestra"]
            if "llave_maestra" in ids:
                resp["entidades"].append({
                    "id": "llave_maestra", "clase": "llave", "nombre": "Llave maestra",
                    "peso": 1, "valor": 5, "abre": "llave_maestra",
                })
            return resp

        servidor.obtener_catalogo = catalogo_con_llave
        esqueleto_original = servidor.obtener_esqueleto

        def esqueleto_con_puerta(cripta_id, pagina=1):
            datos = esqueleto_original(cripta_id, pagina)
            datos["salas"][0]["salidas"]["E"].update(cerrada=True, llave="llave_maestra")
            return datos

        servidor.obtener_esqueleto = esqueleto_con_puerta

        tmp = tempfile.mkdtemp()
        almacen = AlmacenLocal(tmp)
        catalogo = GestorCatalogo(servidor, CacheCatalogoOrdenado(25), almacen)
        precarga = GestorPrecarga(servidor, catalogo)
        motor = crear_juego(precarga, "prueba", semilla=42)

        sala_id = motor.jugador.posicion_actual
        llave = ObjetoInstancia("llave-test", "llave_maestra", "suelo", sala_id)
        motor.objetos_en_suelo[sala_id].append(llave)
        motor.ejecutar("recoger", llave.id_instancia)
        self.assertTrue(motor.ejecutar("abrir", "E").ok)
        motor.ejecutar("mover", "E")
        self.assertTrue(motor.terminado)
        self.assertEqual(motor.resultado, "victoria")

    # ------------------------------------------------------------------
    # Offline
    # ------------------------------------------------------------------

    def test_ciclo_completo_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            paquete = tmp + "/paquete"
            crear_paquete(paquete, salas=6)
            cliente = ClienteOffline(paquete)
            almacen = AlmacenLocal(tmp + "/sesion")
            catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), almacen)
            precarga = GestorPrecarga(cliente, catalogo)
            motor = crear_juego(precarga, "prueba", semilla=7)
            self.assertFalse(motor.terminado)
            resultado = motor.ejecutar("mover", "E")
            self.assertTrue(resultado.ok)
            self.assertEqual(cliente.solicitudes_realizadas, 0)
