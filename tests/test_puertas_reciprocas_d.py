"""Aceptación propuesta A–D PD-01..04: motor/binario reales, sin HTTP.

Suite TDD: los fallos acreditan pendientes de integración, no regresiones nuevas
introducidas por D. Las preparaciones de estado abierto aíslan carga y cierre
de la apertura todavía unilateral. No se parchean reglas del motor.
"""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from datos.guardado_binario import cargar_estado, guardar_estado
from modelo.inventario import Inventario
from modelo.juego import Motor
from modelo.snapshots import MetaPartida
from modelo.tipos import FichaCatalogo, Jugador, ObjetoInstancia, Sala


class PuertasReciprocasDTest(unittest.TestCase):
    def motor(self, *, abierta=False, opuesta_cargada=True):
        jugador = Jugador(vida=30, vida_max=30, ataque=6, defensa=2,
                          velocidad=100, tiempo_siguiente=0,
                          inventario=Inventario(10), posicion_actual=1,
                          llaves_obtenidas=[])
        jugador.inventario.recoger(ObjetoInstancia("pergamino-1", "pergamino", "inventario"))
        salas = [Sala(1, "Origen", {"E": {"sala": 2, "cerrada": not abierta,
                                          "cierre_automatico": 250}}),
                 Sala(2, "Destino", {"O": {"sala": 1, "cerrada": not abierta,
                                           "cierre_automatico": 250}})]
        motor = Motor(jugador, salas, semilla=42)
        motor.meta = MetaPartida("puertas-sinteticas", "v1", "cat1", 42)
        ficha = FichaCatalogo("pergamino", "pergamino_retroceso", "Pergamino", {})
        def obtener(ids):
            self.assertTrue(all(tipo == "pergamino" for tipo in ids))
            return [ficha for _ in ids]
        motor.gestor_precarga = SimpleNamespace(
            catalogo=SimpleNamespace(obtener_fichas=obtener),
            generales={"jugador": {"velocidad": 100}})
        motor.contenido_cargado[1] = True
        motor.contenido_cargado[2] = opuesta_cargada
        if abierta:
            motor.programar_evento(250, "cierre_puerta", (motor.salas[1], "E"))
        return motor

    def accion(self, motor, nombre, argumento=None):
        resultado = motor.ejecutar(nombre, argumento)
        self.assertTrue(resultado.ok, resultado.mensaje)

    def extremos(self, motor):
        return (motor.salas[1].salidas["E"]["cerrada"],
                motor.salas[2].salidas["O"]["cerrada"])

    def cierres(self, motor):
        return [(e.tiempo, e.secuencia, e.referencia[0].id, e.referencia[1])
                for e in motor.cola.pendientes() if e.tipo == "cierre_puerta"]

    def cargar_archivo(self, motor):
        # La restauración recibe datos que recorrieron el escritor y lector reales.
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "partida.bin")
            guardar_estado(motor.exportar_estado(), ruta)
            motor.restaurar_estado(cargar_estado(ruta))

    def test_pd01_abrir_guardar_cargar_con_opuesta_no_visitada(self):
        motor = self.motor(opuesta_cargada=False)
        self.accion(motor, "abrir", "E")
        self.assertEqual(self.extremos(motor), (False, False), "Apertura bilateral pendiente")
        self.assertEqual(len(self.cierres(motor)), 1)
        self.cargar_archivo(motor)
        self.assertEqual(self.extremos(motor), (False, False))
        self.assertFalse(motor.contenido_cargado[2])
        self.assertEqual(motor.registro_rastro.tiempo_de(2), -1)

    def test_pd01_binario_conserva_extremo_modificado_sin_cargar_sala(self):
        motor = self.motor(opuesta_cargada=False)
        # Estado que entregaría el productor bilateral; aísla la omisión al exportar.
        for sala, direccion in ((1, "E"), (2, "O")):
            motor.salas[sala].salidas[direccion]["cerrada"] = False
        motor.programar_evento(250, "cierre_puerta", (motor.salas[1], "E"))
        self.cargar_archivo(motor)
        self.assertEqual(self.extremos(motor), (False, False), "Se perdió el extremo no visitado")
        self.assertFalse(motor.contenido_cargado[2])
        self.assertEqual(motor.registro_rastro.tiempo_de(2), -1)

    def test_pd02_binario_preserva_evento_unico_y_estado_completo(self):
        motor = self.motor(abierta=True)
        antes = motor.exportar_estado()
        cierres = self.cierres(motor)
        contador = motor.cola.proxima_secuencia()
        self.cargar_archivo(motor)
        self.assertEqual(motor.exportar_estado(), antes)
        self.assertEqual(self.cierres(motor), cierres)
        self.assertEqual(len(cierres), 1)
        self.assertEqual(motor.cola.proxima_secuencia(), contador)

    def test_pd02_evento_cargado_cierra_ambos_extremos(self):
        motor = self.motor(abierta=True)
        self.cargar_archivo(motor)
        mensajes = []
        motor.establecer_notificador(mensajes.append)
        for _ in range(3):
            self.accion(motor, "esperar")
        self.assertEqual(motor.reloj, 300)
        self.assertEqual(self.extremos(motor), (True, True), "Cierre bilateral pendiente")
        self.assertEqual(self.cierres(motor), [])
        self.assertEqual(sum("se cierra" in mensaje for mensaje in mensajes), 1)

    def test_pd03_retroceder_apertura_restaura_extremos_y_cancela_cierre(self):
        motor = self.motor()
        self.accion(motor, "abrir", "E")
        self.assertEqual(self.extremos(motor), (False, False), "Apertura bilateral pendiente")
        self.accion(motor, "retroceso")
        self.assertEqual(self.extremos(motor), (True, True))
        self.assertEqual(self.cierres(motor), [])
        self.assertEqual(motor.reloj, 0)
        self.assertEqual(motor.jugador.inventario.contar("pergamino"), 0)

    def test_pd03_retroceder_cierre_restaurado_recupera_mismo_evento(self):
        motor = self.motor(abierta=True)
        self.cargar_archivo(motor)
        for _ in range(2):
            self.accion(motor, "esperar")
        evento = next(e for e in motor.cola.pendientes() if e.tipo == "cierre_puerta")
        cierres = self.cierres(motor)
        contador = motor.cola.proxima_secuencia()
        self.accion(motor, "esperar")
        self.assertEqual(self.extremos(motor), (True, True), "Cierre bilateral pendiente")
        self.accion(motor, "retroceso")
        self.assertEqual(self.extremos(motor), (False, False))
        self.assertEqual(motor.reloj, 200)
        self.assertEqual(self.cierres(motor), cierres)
        self.assertTrue(any(e is evento for e in motor.cola.pendientes()))
        self.assertEqual(motor.cola.proxima_secuencia(), contador)
        self.assertEqual(motor.jugador.inventario.contar("pergamino"), 0)

    def test_pd04_continuar_desde_archivo_coincide_con_corrida_sin_carga(self):
        continuo = self.motor(abierta=True)
        cargado = self.motor(abierta=True)
        self.accion(continuo, "esperar")
        self.accion(cargado, "esperar")
        self.cargar_archivo(cargado)
        for _ in range(3):
            self.accion(continuo, "esperar")
            self.accion(cargado, "esperar")
        self.assertEqual(cargado.exportar_estado(), continuo.exportar_estado())
        self.assertEqual(self.extremos(cargado), (True, True), "Igualdad no basta: deben cerrar ambos")
        self.assertEqual(self.cierres(cargado), [])


if __name__ == "__main__":
    unittest.main()
