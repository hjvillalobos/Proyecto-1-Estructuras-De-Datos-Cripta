"""Escala/contenido nuevo y verificacion explicita de API real (opcional)."""

import os
from pathlib import Path
import tempfile
import unittest

from datos.almacen import AlmacenLocal
from datos.bitacora_replay import BitacoraReplay, aplicar_accion_replay
from datos.guardado_binario import guardar_estado, cargar_estado
from modelo.juego import crear_juego
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.cliente_api import ClienteApi
from red.precarga import GestorPrecarga
from tests.datos_prueba import ServidorFalso
from controlador.controlador import ControladorJuego
from datos.puntajes import TablaPuntajes
from utilidades.bench_juego import motor_sintetico
from vista.consola import VistaConsola


class TestCierrePuntajeConsola(unittest.TestCase):
    def test_cancelar_nombre_no_pierde_puntaje_ni_impide_cierre(self):
        for error in (EOFError, KeyboardInterrupt):
            with self.subTest(error=error), tempfile.TemporaryDirectory() as carpeta:
                motor = motor_sintetico(1, 42)
                motor.terminado, motor.resultado, motor.jugador.vida = True, "derrota", 0
                mensajes = []

                def entrada(_):
                    raise error()
                vista = VistaConsola(entrada=entrada, salida=mensajes.append)
                tabla = TablaPuntajes(str(Path(carpeta) / "puntajes.jsonl"))
                controlador = ControladorJuego(motor, vista,
                    ruta_replay=str(Path(carpeta) / "partida.log"), tabla_puntajes=tabla)
                antes = motor.exportar_estado()
                controlador.iniciar()
                controlador._registrar_puntaje()
                self.assertEqual(motor.exportar_estado(), antes)
                self.assertIn("Sesión finalizada.", mensajes)
                registros = tabla.cargar()
                self.assertEqual(len(registros), 1)
                self.assertEqual(registros[0].nombre, "Jugador")


class CriptaDesconocida(ServidorFalso):
    """Contenido de prueba, no reglas ni estadisticas del juego distribuido."""

    def __init__(self, salas=137):
        super().__init__(salas=salas, presupuesto=200, version="nueva", version_catalogo="nuevos_tipos")

    def obtener_datos_generales(self, cripta_id):
        datos = super().obtener_datos_generales(cripta_id)
        datos["jugador"]["vida_max"] = 10000
        datos["llave_salida"] = "llave_nueva"
        return datos

    def obtener_esqueleto(self, cripta_id, pagina=1):
        datos = super().obtener_esqueleto(cripta_id, pagina)
        for sala in datos["salas"]:
            if sala["id"] == 100 + self.cantidad - 2:
                sala["salidas"]["E"].update(cerrada=True, llave="llave_nueva", cierre_automatico=500)
        return datos

    def obtener_contenido_salas(self, cripta_id, salas_ids):
        self._contar("contenido", salas_ids)
        contenido = []
        for sala in salas_ids:
            contenido.append({"sala": sala,
                "enemigos": [{"instancia": f"nuevo-{sala}-{i}", "tipo": f"actor_nuevo_{(sala+i)%3}", "vida": 8}
                             for i in range(2)] if sala != 100 else [],
                "objetos": ["llave_nueva", "arma_nueva"] if sala == 100 else ["cura_nueva"],
                "trampas": [{"instancia": f"trampa-{sala}-{i}", "tipo": "trampa_nueva"}
                            for i in range(2)] if sala % 7 == 0 else []})
        # El adaptador debe devolver el orden solicitado, no el de la red.
        return {"contenido": list(reversed(contenido))}

    def obtener_catalogo(self, ids):
        self._contar("catalogo", ids)
        fichas = []
        for clave in ids:
            ficha = {"id": clave, "nombre": clave, "peso": 1, "valor": 2}
            if clave.startswith("actor_nuevo_"):
                comportamiento = ("guardian", "errante", "rastreador")[int(clave[-1])]
                ficha.update(clase="enemigo", vida_max=12, ataque=1, defensa=1,
                             velocidad=150, comportamiento=comportamiento,
                             regeneracion=1, suelta=["cura_nueva"])
            elif clave == "llave_nueva":
                ficha.update(clase="llave", abre="salida_nueva")
            elif clave == "arma_nueva":
                ficha.update(clase="arma", ataque_bonus=20)
            elif clave == "trampa_nueva":
                ficha.update(clase="trampa", rearme=50, veneno={"dano_por_pulso": 1})
                ficha["daño"] = 1
            else:
                ficha.update(clase="pocion", cura=20)
            fichas.append(ficha)
        return {"entidades": list(reversed(fichas))}


class TestCriptaDesconocida(unittest.TestCase):
    def test_arma_enemigos_botin_y_pocion_con_ids_nuevos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            servidor = CriptaDesconocida(17)
            precarga = GestorPrecarga(servidor, GestorCatalogo(
                servidor, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta)))
            self.addCleanup(precarga.cerrar)
            motor = crear_juego(precarga, "cripta-inedita", 12345)
            arma = next(o for o in motor.objetos_en_suelo[100] if o.tipo_catalogo == "arma_nueva")
            self.assertTrue(motor.ejecutar("recoger", arma.id_instancia).ok)
            self.assertTrue(motor.ejecutar("equipar", arma.id_instancia).ok)
            self.assertEqual(motor.jugador.ataque, 26)
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            for enemigo in list(motor.estado_vista().enemigos):
                self.assertTrue(motor.ejecutar("atacar", enemigo.instancia).ok)
            self.assertFalse(motor.estado_vista().enemigos)
            self.assertEqual(motor.enemigos_derrotados, 2)
            pociones = [o for o in motor.objetos_en_suelo[101] if o.tipo_catalogo == "cura_nueva"]
            self.assertEqual(len(pociones), 3)
            pocion = pociones[0]
            self.assertTrue(motor.ejecutar("recoger", pocion.id_instancia).ok)
            motor.jugador.vida = 100
            self.assertTrue(motor.ejecutar("usar", pocion.id_instancia).ok)
            self.assertEqual(motor.jugador.vida, 120)
            self.assertFalse(any(i.instancia == pocion.id_instancia for i in motor.inventario_vista()))
            self.assertFalse(motor.ejecutar("usar", pocion.id_instancia).ok)
            precarga.cerrar()

    def test_137_salas_tipos_nuevos_eventos_victoria_guardado_replay(self):
        with tempfile.TemporaryDirectory() as carpeta:
            servidor = CriptaDesconocida()
            almacen = AlmacenLocal(carpeta)

            def preparar():
                return GestorPrecarga(servidor, GestorCatalogo(servidor, CacheCatalogoOrdenado(25), almacen))

            precarga = preparar()
            self.addCleanup(precarga.cerrar)
            motor = crear_juego(precarga, "desconocida", 12345)
            log = BitacoraReplay(Path(carpeta) / "prueba.log")
            log.iniciar(motor.meta)

            def actuar(accion, argumento=None):
                resultado = motor.ejecutar(accion, argumento)
                self.assertTrue(resultado.ok, resultado.mensaje)
                log.registrar_accion(accion, argumento)

            for objeto in list(motor.objetos_en_suelo[100]):
                actuar("recoger", objeto.id_instancia)
                if objeto.tipo_catalogo == "arma_nueva":
                    actuar("equipar", objeto.id_instancia)
            for _ in range(servidor.cantidad - 1):
                puerta = motor.salas[motor.jugador.posicion_actual].salidas["E"]
                if puerta.get("cerrada"):
                    actuar("abrir", "E")
                actuar("mover", "E")
            self.assertEqual(motor.resultado, "victoria")
            self.assertGreater(motor.jugador.vida, 0)
            estado = motor.exportar_estado()
            ruta = str(Path(carpeta) / "partida.bin")
            guardar_estado(estado, ruta)
            self.assertEqual(cargar_estado(ruta), estado)
            precarga.cerrar()
            antes = servidor.solicitudes_realizadas
            nuevo = preparar()
            self.addCleanup(nuevo.cerrar)
            replay = crear_juego(nuevo, "desconocida", 12345,
                                 version_cripta=motor.meta.cripta_version,
                                 version_catalogo=motor.meta.catalogo_version)
            for accion in log.leer()[1]:
                self.assertTrue(aplicar_accion_replay(replay, accion).ok)
            self.assertEqual(replay.exportar_estado(), estado)
            self.assertEqual(servidor.solicitudes_realizadas, antes)
            self.assertLessEqual(servidor.solicitudes_realizadas, servidor.presupuesto)
            self.assertTrue(any(op == "pagina" and valores == (3,) for op, valores in servidor.llamadas))


@unittest.skipUnless(os.environ.get("CRIPTA_API_REAL") == "1", "API real: habilitacion explicita requerida")
class TestApiRealEntrega(unittest.TestCase):
    def test_cuatro_criptas_cache_fria_y_caliente_dentro_de_presupuesto(self):
        for cripta in ("cripta-01", "cripta-02", "cripta-03", "cripta-04"):
            with self.subTest(cripta=cripta), tempfile.TemporaryDirectory() as carpeta:
                conteos = []
                for caliente in (False, True):
                    cliente = ClienteApi()
                    catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), AlmacenLocal(carpeta))
                    precarga = GestorPrecarga(cliente, catalogo)
                    try:
                        # Incluye la consulta que hace el menu de seleccion.
                        lista = cliente.listar_criptas()
                        self.assertTrue(any(c["id"] == cripta for c in lista["criptas"]))
                        motor = crear_juego(precarga, cripta, 20)
                        precarga.cargar_contenido([s.id for s in precarga.salas])
                        for _ in range(3):
                            self.assertTrue(motor.ejecutar("esperar").ok)
                        precarga.cerrar()
                        reporte = catalogo.reporte()
                        self.assertLessEqual(reporte["solicitudes_realizadas"], reporte["presupuesto_solicitudes"])
                        self.assertLessEqual(reporte["fichas_en_memoria"], 25)
                        conteos.append(reporte["solicitudes_realizadas"])
                        print(f"API {cripta} {'caliente' if caliente else 'fria'}: "
                              f"{conteos[-1]}/{reporte['presupuesto_solicitudes']} solicitudes", flush=True)
                    finally:
                        try:
                            precarga.cerrar()
                        finally:
                            cliente.cerrar()
                self.assertLess(conteos[1], conteos[0])
