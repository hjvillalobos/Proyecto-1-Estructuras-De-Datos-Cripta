"""T020: FR-007/008/009/012/014, NFR-004; A3/A4/A5 y T1/T2.

Casos con rango entero válido o None explícito y datos válidos.
No implementa política, motor ni servicios; reutiliza fixtures existentes.
"""

from importlib import import_module
import unittest

from modelo.rutas import GrafoTerreno, EspacioBusqueda, HeapRutas, buscar_ruta
from modelo.tipos import Sala
from tests.datos_prueba import ServidorFalso
from tests.datos_terreno_cazador import crear_salas, motor_terreno


class PruebasDecisionCazador(unittest.TestCase):
    def preparar_consulta(self, salas):
        grafo = GrafoTerreno(salas)
        espacio = EspacioBusqueda(grafo.ids)
        frontera = HeapRutas(espacio)
        llamadas = []

        def consultar(origen, destino, limite):
            # Sonda interna: registra y ejecuta el algoritmo real, sin
            # sustituir resultados ni simular un componente de B/C/D.
            llamadas.append((origen, destino, limite))
            return buscar_ruta(grafo, espacio, frontera, origen, destino, limite)

        return grafo, llamadas, consultar

    def decidir(self, origen, destino, rango, consultar):
        """Propuesta interna T022, ajena a decidir_accion de C.

        decidir_cazador(origen_indice, destino_indice, rango, consultar_ruta)
        devuelve (accion, direccion_o_None, costo_base). No ejecuta acciones.
        La importación por caso deja visibles los escenarios aún pendientes.
        """
        modulo = import_module("modelo.cazador")
        return modulo.decidir_cazador(origen, destino, rango, consultar)

    def comprobar_decision(self, salas, origen, destino, rango, esperado):
        grafo, llamadas, consultar = self.preparar_consulta(salas)
        o, d = grafo.indice(origen), grafo.indice(destino)
        resultado = self.decidir(o, d, rango, consultar)
        self.assertEqual(resultado, esperado)
        self.assertEqual(llamadas, [] if o == d else [(o, d, rango)])

    def alternativas(self, atajo_cerrado=False):
        return crear_salas([90, 7, 80], [
            (0, "E", 2, "O", 50 if atajo_cerrado else 500, atajo_cerrado),
            (0, "N", 1, "S", 100, False),
            (1, "E", 2, "S", 100, False),
        ])

    def test_a3_compartir_sala_ataca_antes_de_consultar_rutas(self):
        for rango in (1, None):
            with self.subTest(rango=rango):
                self.comprobar_decision(crear_salas([90], []), 90, 90, rango,
                                        ("atacar", None, 100))

    def test_ruta_admisible_devuelve_primer_paso_optimo_y_su_costo(self):
        self.comprobar_decision(self.alternativas(), 90, 80, 250,
                                ("mover", "N", 100))

    def test_t1_destino_desconectado_espera_con_costo_100(self):
        salas = crear_salas([90, 7, 80], [(0, "N", 1, "S", 50, False)])
        for rango in (100, None):
            with self.subTest(rango=rango):
                self.comprobar_decision(salas, 90, 80, rango,
                                        ("esperar", None, 100))

    def test_t2_costo_101_supera_rango_100_y_espera(self):
        salas = crear_salas([90, 80], [(0, "E", 1, "O", 101, False)])
        self.comprobar_decision(salas, 90, 80, 100, ("esperar", None, 100))
        self.comprobar_decision(salas, 90, 80, None, ("mover", "E", 101))

    def test_a4_distancia_igual_al_rango_permite_perseguir(self):
        self.comprobar_decision(self.alternativas(), 90, 80, 200,
                                ("mover", "N", 100))

    def test_unica_puerta_cerrada_impide_movimiento(self):
        salas = crear_salas([90, 80], [(0, "E", 1, "O", 50, True)])
        for rango in (100, None):
            with self.subTest(rango=rango):
                self.comprobar_decision(salas, 90, 80, rango, ("esperar", None, 100))

    def test_atajo_cerrado_no_impide_usar_alternativa_abierta(self):
        for rango in (200, None):
            with self.subTest(rango=rango):
                self.comprobar_decision(self.alternativas(True), 90, 80, rango,
                                        ("mover", "N", 100))

    def test_consulta_no_modifica_posiciones_azar_agenda_ni_puertas(self):
        with motor_terreno(250) as motor:
            # El jugador se separa mediante una acción completa real. No se
            # altera el comportamiento del enemigo ni se adelanta su turno.
            self.assertTrue(motor.ejecutar("mover", "E").ok)
            enemigo = motor.enemigos_por_sala[100][0]
            grafo, llamadas, consultar = self.preparar_consulta(
                [s for s in motor.salas if s is not None])
            origen = grafo.indice(enemigo.sala_actual)
            destino = grafo.indice(motor.jugador.posicion_actual)
            estado = motor.exportar_estado()
            azar = motor.azar.getstate()
            eventos = [(id(e), e.tiempo, e.secuencia, e.tipo,
                        e.cancelado, e.en_cola) for e in motor.cola._datos]
            posiciones = (enemigo.sala_actual, motor.jugador.posicion_actual)
            puertas = [(arco.origen, arco.destino, arco.puerta.get("cerrada", False))
                       for vecinos in grafo.adyacencias for arco in vecinos]

            self.assertEqual(self.decidir(origen, destino, 250, consultar),
                             ("mover", "E", 250))
            self.assertEqual(llamadas, [(origen, destino, 250)])
            self.assertEqual(motor.exportar_estado(), estado)
            self.assertEqual(motor.azar.getstate(), azar)
            self.assertEqual((enemigo.sala_actual, motor.jugador.posicion_actual),
                             posiciones)
            self.assertEqual([(id(e), e.tiempo, e.secuencia, e.tipo,
                               e.cancelado, e.en_cola) for e in motor.cola._datos],
                             eventos)
            self.assertEqual([(a.origen, a.destino, a.puerta.get("cerrada", False))
                              for vecinos in grafo.adyacencias for a in vecinos],
                             puertas)

    def test_a5_misma_decision_sin_descargas_adicionales_de_contenido(self):
        # ServidorFalso ya existente, sin añadir otro doble o cambiarlo.
        servidor = ServidorFalso(salas=4)
        pagina = servidor.obtener_esqueleto("prueba", 1)
        salas = [Sala(s["id"], s["nombre"], s["salidas"])
                 for s in pagina["salas"]]
        grafo, llamadas, consultar = self.preparar_consulta(salas)
        origen, destino = grafo.indice(100), grafo.indice(103)
        for contenido_descargado in (False, True):
            with self.subTest(contenido_descargado=contenido_descargado):
                if contenido_descargado:
                    contenido = servidor.obtener_contenido_salas(
                        "prueba", [100, 101, 102, 103])
                    self.assertEqual(len(contenido["contenido"]), 4)
                peticiones = list(servidor.llamadas)
                cantidad = servidor.solicitudes_realizadas
                previas = len(llamadas)
                self.assertEqual(self.decidir(origen, destino, 300, consultar),
                                 ("mover", "E", 100))
                self.assertEqual(llamadas[previas:], [(origen, destino, 300)])
                self.assertEqual(servidor.solicitudes_realizadas, cantidad)
                self.assertEqual(servidor.llamadas, peticiones)


if __name__ == "__main__":
    unittest.main()
