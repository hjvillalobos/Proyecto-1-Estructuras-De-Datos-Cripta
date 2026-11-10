"""I4, C21–C25: FR-003/004/007/008/010/012/017 con búsqueda real de A."""
import unittest
from random import Random
from unittest.mock import patch

from modelo.conocimiento import ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible


def crear(ids, conexiones):
    salas = []
    for origen in ids:
        salidas = []
        for numero, (a, b, costo, puerta) in enumerate(conexiones):
            if origen in (a, b):
                salidas.append(SalidaConocible(str(numero), b if origen == a else a, costo, puerta))
        salas.append(SalaConocible(origen, str(origen), tuple(salidas)))
    puertas = tuple(PuertaConocible(p, a, b) for a, b, _, p in conexiones if p is not None)
    return ConocimientoMapa(tuple(salas), puertas, ids[0])


class TestRutasConocidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import modelo.rutas
        except ModuleNotFoundError as error:
            if error.name != 'modelo.rutas':
                raise
            raise unittest.SkipTest('A no integrado; ejecutar python -m utilidades.verificar_conocimiento_rutas')
        from modelo.conocimiento_rutas import PlanificadorConocido
        cls.planificador = PlanificadorConocido

    def test_rechazo_destinos_y_llegada_sin_paso(self):
        """C21: avistado, desconocido e inexistente no se distinguen."""
        m = crear((10, 42, 9000), ((10, 42, 7, None),))
        p = self.planificador(m)
        respuestas = [p.consultar(10, destino) for destino in (42, 9000, 99999)]
        self.assertTrue(all(r == respuestas[0] for r in respuestas))
        self.assertEqual(respuestas[0].estado, 'destino_no_explorado')
        self.assertEqual(p.consultar(42, 10).estado, 'origen_no_explorado')
        llegada = p.consultar(10, 10)
        self.assertEqual((llegada.estado, llegada.siguiente, llegada.costo_total), ('llegada', None, 0))

    def test_atajo_desconocido_y_reversion_de_exploracion(self):
        """C22/C25: no filtrar después de buscar en mapa real."""
        m = crear((10, 20, 30), ((10, 20, 1, None), (20, 30, 1, None), (10, 30, 10, None)))
        m.entrar(30)
        p = self.planificador(m)
        self.assertEqual(p.consultar(10, 30).costo_total, 10)
        lote = m.entrar(20)
        self.assertEqual((p.consultar(10, 30).siguiente, p.consultar(10, 30).costo_total), (20, 2))
        m.revertir(lote)
        self.assertEqual(p.consultar(10, 30).costo_total, 10)

    def test_empate_menor_vecina_no_orden_de_entrada(self):
        """C22: ambas rutas cuestan 4; gana primera vecina 20."""
        m = crear((100, 90, 20, 500), ((100, 90, 1, None), (90, 500, 3, None),
                                        (100, 20, 3, None), (20, 500, 1, None)))
        for sala in (90, 20, 500):
            m.entrar(sala)
        r = self.planificador(m).consultar(100, 500)
        self.assertEqual((r.siguiente, r.costo_paso, r.costo_total), (20, 3, 4))

    def test_memoria_puerta_y_reversion_sin_cache_obsoleta(self):
        """C23: no observada, abierta, cerrada y deshacer cierre."""
        m = crear((10, 9000), ((10, 9000, 100, 7),))
        m.entrar(9000)
        p = self.planificador(m)
        self.assertEqual(p.consultar(10, 9000).estado, 'sin_ruta')
        abrir = m.observar_puerta(10, 7, False)
        paso = p.consultar(10, 9000)
        self.assertEqual(paso.estado, 'paso')
        cerrar = m.observar_puerta(9000, 7, True)
        self.assertEqual(p.consultar(10, 9000).estado, 'sin_ruta')
        m.revertir(cerrar)
        self.assertEqual(p.consultar(10, 9000), paso)
        m.revertir(abrir)
        self.assertEqual(p.consultar(10, 9000).estado, 'sin_ruta')

    def test_puertas_paralelas_y_costo_sin_tope_artificial(self):
        """C24: no confundir dos puertas entre los mismos extremos."""
        costo = 10**30
        m = crear((10, 9000), ((10, 9000, costo, 7), (10, 9000, 1, 8)))
        m.entrar(9000)
        m.observar_puerta(10, 7, False)
        m.observar_puerta(10, 8, True)
        p = self.planificador(m)
        self.assertEqual((p.consultar(10, 9000).direccion, p.consultar(10, 9000).costo_total), ('0', costo))
        m.observar_puerta(10, 8, False)
        self.assertEqual((p.consultar(10, 9000).direccion, p.consultar(10, 9000).costo_total), ('1', 1))

    def test_consultas_alternadas_no_mutan_ni_proyectan_todo_el_mapa(self):
        """C24/C25: ciclos, desconexión y reutilización de auxiliares."""
        m = crear((10, 20, 30, 4000), ((10, 20, 1, None), (20, 30, 1, None), (30, 10, 4, None)))
        for sala in (20, 30, 4000):
            m.entrar(sala)
        p = self.planificador(m)
        antes = m.mapa_conocido()
        with patch.object(m, 'mapa_conocido', side_effect=AssertionError('No proyectar por paso')):
            for _ in range(20):
                self.assertEqual(p.consultar(10, 30).costo_total, 2)
                self.assertEqual(p.consultar(10, 4000).estado, 'sin_ruta')
                self.assertEqual(p.consultar(30, 10).costo_total, 2)
                self.assertEqual(p.consultar(10, 10).estado, 'llegada')
        self.assertEqual(m.mapa_conocido(), antes)

    def test_oraculo_exhaustivo_semilla_fija(self):
        """C22–C25: comparar 60 grafos con todos sus caminos simples."""
        azar = Random(927)
        ids = (10, 40, 100, 600, 9000, 20000)
        for caso in range(60):
            conexiones = []
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    if azar.random() < .45:
                        conexiones.append((ids[i], ids[j], azar.randint(1, 9), len(conexiones)))
            m = crear(ids, conexiones)
            exploradas = [ids[0], ids[-1]]
            exploradas.extend(s for s in ids[1:-1] if azar.random() < .7)
            for sala in exploradas:
                m.entrar(sala)
            abiertas = []
            for a, b, _, puerta in conexiones:
                if a in exploradas or b in exploradas:
                    estado = azar.choice((None, False, True))
                    if estado is not None:
                        m.observar_puerta(a if a in exploradas else b, puerta, estado)
                    if estado is False:
                        abiertas.append(puerta)
            candidatos = []

            def recorrer(actual, visitados, costo, primero):
                if actual == ids[-1]:
                    candidatos.append((costo, primero))
                    return
                for a, b, peso, puerta in conexiones:
                    if actual not in (a, b) or puerta not in abiertas:
                        continue
                    vecino = b if actual == a else a
                    if vecino in exploradas and vecino not in visitados:
                        recorrer(vecino, visitados + (vecino,), costo + peso,
                                 vecino if primero is None else primero)

            recorrer(ids[0], (ids[0],), 0, None)
            r = self.planificador(m).consultar(ids[0], ids[-1])
            with self.subTest(caso=caso):
                if candidatos:
                    self.assertEqual((r.costo_total, r.siguiente), min(candidatos))
                else:
                    self.assertEqual(r.estado, 'sin_ruta')

    def test_viaje_recalcula_con_observacion_y_cancelacion_tras_reversion(self):
        """I5 C27/C29: control de C con buscador real; movimiento suministrado."""
        from modelo.viaje import ControlViaje, ResultadoPaso
        m = crear((10, 20, 30), ((10, 20, 1, 7), (20, 30, 1, None), (10, 30, 8, None)))
        m.entrar(20)
        m.entrar(30)
        m.observar_puerta(10, 7, False)
        viaje = ControlViaje(self.planificador(m))
        viaje.iniciar(10, 30)
        antes = m.mapa_conocido()
        primero = viaje.proponer()
        self.assertEqual(primero.ruta.siguiente, 20)
        self.assertEqual(m.mapa_conocido(), antes)
        cierre = m.observar_puerta(10, 7, True)
        viaje.registrar_resultado(primero.numero, ResultadoPaso(10, False, False, False, False, False))
        alternativo = viaje.proponer()
        self.assertEqual((alternativo.ruta.siguiente, alternativo.ruta.costo_total), (30, 8))
        viaje.cancelar()
        m.revertir(cierre)
        self.assertIsNone(viaje.proponer())
        with self.assertRaises(ValueError):
            viaje.registrar_resultado(alternativo.numero, ResultadoPaso(30, True, False, True, False, False))
        viaje.iniciar(10, 30)
        paso = viaje.proponer()
        self.assertEqual(paso.ruta.siguiente, 20)
        viaje.registrar_resultado(paso.numero, ResultadoPaso(20, True, False, True, False, False))
        final = viaje.proponer()
        self.assertEqual(final.ruta.siguiente, 30)
        viaje.registrar_resultado(final.numero, ResultadoPaso(30, True, False, True, False, False))
        self.assertEqual(viaje.causas, ('llegada',))
        self.assertIsNone(viaje.proponer())


if __name__ == '__main__':
    unittest.main()
