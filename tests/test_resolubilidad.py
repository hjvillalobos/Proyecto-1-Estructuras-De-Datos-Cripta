import unittest
from copy import deepcopy
from dataclasses import replace
from modelo.resolubilidad import (DatosVerificacion, SalaVerificacion, SalidaVerificacion,
                                  UbicacionLlave, normalizar, verificar_resolubilidad)
from red.errores import DatosInvalidos


def datos(salas, llaves, salida=3, clave="K"):
    return DatosVerificacion("sintetica", "v1", 1, salida, clave, salas, llaves)


def puerta(origen, destino, llave=None, direccion="N", cerrada=None):
    return SalidaVerificacion(origen, direccion, destino,
                              llave is not None if cerrada is None else cerrada, llave)


class TestResolubilidad(unittest.TestCase):
    def test_FR008_AC14_validacion(self):
        base = datos([SalaVerificacion(1, [puerta(1, 3, "K")]), SalaVerificacion(3, [])],
                     [UbicacionLlave("K", 1)])
        casos = [replace(base, sala_inicial=True), replace(base, salas=base.salas + [base.salas[0]]),
                 replace(base, sala_salida=99), replace(base, ubicaciones=[UbicacionLlave("K", 99)]),
                 replace(base, ubicaciones=[UbicacionLlave("", 1)]),
                 replace(base, salas=[SalaVerificacion(1, [puerta(1, 99)]), base.salas[1]]),
                 replace(base, salas=[SalaVerificacion(1, [puerta(1, 3, cerrada=True)]), base.salas[1]])]
        for caso in casos:
            with self.subTest(caso=caso), self.assertRaises(DatosInvalidos):
                normalizar(caso)

    def test_FR001_FR004_AC01_AC04_cadena(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, "A")]),
                      SalaVerificacion(2, [puerta(2, 3, "K")]), SalaVerificacion(3, [])],
                     [UbicacionLlave("A", 1), UbicacionLlave("K", 2, "enemigo")])
        copia = deepcopy(base)
        esperado = verificar_resolubilidad(base)
        self.assertEqual(esperado.estado, "resoluble")
        self.assertEqual(esperado.orden_llaves, ["A", "K"])
        for _ in range(10):
            self.assertEqual(verificar_resolubilidad(base), esperado)
        self.assertEqual(base, copia)
        self.assertEqual(verificar_resolubilidad(replace(base, salas=list(reversed(base.salas)),
                         ubicaciones=list(reversed(base.ubicaciones)))), esperado)

    def test_FR002_AC02_no_basta_salida(self):
        base = datos([SalaVerificacion(1, [puerta(1, 3)]), SalaVerificacion(3, [])],
                     [UbicacionLlave("K", 1)])
        self.assertEqual(verificar_resolubilidad(base).estado, "no_resoluble")
        base = replace(base, salas=[SalaVerificacion(1, [puerta(1, 3, "K")]), SalaVerificacion(3, [])],
                       ubicaciones=[])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(r.llaves_inalcanzables[0].ubicaciones, [])

    def test_FR003_AC03_AC05_AC08_alternativas(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, "K"), puerta(1, 3, "K", "S")]),
                      SalaVerificacion(2, []), SalaVerificacion(3, [])],
                     [UbicacionLlave("K", 1, "errante"), UbicacionLlave("K", 2)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(r.orden_llaves, ["K"])
        self.assertEqual(r.ciclos, [])

    def test_FR001_AC21_sin_regreso(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2), puerta(1, 3, "K", "S")]),
                      SalaVerificacion(2, []), SalaVerificacion(3, [])], [UbicacionLlave("K", 2)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(r.modelo, "alcanzabilidad_acumulada")
        self.assertTrue(r.limitacion)
        self.assertEqual(verificar_resolubilidad(replace(base, ubicaciones=[])).estado, "no_resoluble")

    def test_FR002_puerta_abierta_antes_de_llave(self):
        base = datos([SalaVerificacion(1, [puerta(1, 3, "K", cerrada=False), puerta(1, 2, direccion="S")]),
                      SalaVerificacion(2, []), SalaVerificacion(3, [])], [UbicacionLlave("K", 2)])
        self.assertEqual(verificar_resolubilidad(base).estado, "resoluble")

    def test_FR001_FR014_ids_dispersos(self):
        base = datos([SalaVerificacion(1, [puerta(1, 1000000000, "K")]),
                      SalaVerificacion(1000000000, [])], [UbicacionLlave("K", 1)], 1000000000)
        n = normalizar(base)
        self.assertEqual(len(n.salas), 2)
        self.assertEqual(verificar_resolubilidad(base).metricas.salas_procesadas, 2)

    def test_FR005_AC06_AC24_ciclo_y_certificado(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, "K")]),
                      SalaVerificacion(2, [puerta(2, 3, "K")]), SalaVerificacion(3, [])],
                     [UbicacionLlave("K", 2)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(r.ciclos[0].clasificacion, "bloqueo_circular_autonomo")
        self.comprobar_certificado(r, base)
        self.comprobar_testigos(r)
        self.assertEqual(r.frontera, [puerta(1, 2, "K")])

    def test_FR005_AC22_ciclo_desconectado(self):
        base = datos([SalaVerificacion(1, []), SalaVerificacion(2, [puerta(2, 3, "K")]),
                      SalaVerificacion(3, [puerta(3, 2)])], [UbicacionLlave("K", 3)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.ciclos[0].clasificacion, "ciclo_en_region_desconectada")
        self.comprobar_certificado(r, base)
        self.comprobar_testigos(r)

    def test_FR005_AC25_alternativa_externa_bloqueada(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, "K"), puerta(1, 4, "A", "S")]),
                      SalaVerificacion(2, [puerta(2, 3, "K")]), SalaVerificacion(3, []),
                      SalaVerificacion(4, [])], [UbicacionLlave("K", 2), UbicacionLlave("K", 4)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.ciclos[0].clasificacion, "dependencia_circular_con_bloqueos_externos")
        self.assertTrue(r.ciclos[0].bloqueos_externos)
        self.comprobar_certificado(r, base)
        self.comprobar_testigos(r)

    def test_FR005_AC07_alternativa_obtenible_elimina_ciclo(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, "K"), puerta(1, 4, direccion="S")]),
                      SalaVerificacion(2, [puerta(2, 3, "K")]), SalaVerificacion(3, []),
                      SalaVerificacion(4, [])], [UbicacionLlave("K", 2), UbicacionLlave("K", 4)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(r.ciclos, [])


    def test_FR005_AC24_dos_componentes_dependientes(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, 'B'), puerta(1, 3, 'A', 'S'),
                                          puerta(1, 4, 'C', 'E')]),
                      SalaVerificacion(2, []), SalaVerificacion(3, []),
                      SalaVerificacion(4, [])],
                     [UbicacionLlave('A', 2), UbicacionLlave('B', 3),
                      UbicacionLlave('C', 4), UbicacionLlave('A', 4)], clave='A')
        r = verificar_resolubilidad(base)
        self.assertEqual(len(r.ciclos), 2)
        self.assertTrue(any('A' in c.llaves and 'B' in c.llaves for c in r.ciclos))
        self.assertTrue(any(c.llaves == ['C'] for c in r.ciclos))
        self.comprobar_certificado(r, base)
        self.comprobar_testigos(r)
        for _ in range(10):
            self.assertEqual(verificar_resolubilidad(base), r)

    def test_FR005_AC25_multiples_ciclos_mismo_grupo(self):
        base = datos([SalaVerificacion(1, [puerta(1, 2, 'A'), puerta(1, 3, 'B', 'S')]),
                      SalaVerificacion(2, []), SalaVerificacion(3, [])],
                     [UbicacionLlave('A', 2), UbicacionLlave('A', 3),
                      UbicacionLlave('B', 2), UbicacionLlave('B', 3)], clave='A')
        r = verificar_resolubilidad(base)
        self.assertEqual(len(r.ciclos), 1)
        self.assertEqual(len(r.ciclos[0].llaves), 2)
        self.assertEqual(len(r.evidencia), 7)
        self.comprobar_certificado(r, base)
        self.comprobar_testigos(r)

    def test_FR005_AC09_ciclo_solo_salas_y_llave_opcional(self):
        base = datos([SalaVerificacion(1, [puerta(1, 3, 'K')]),
                      SalaVerificacion(2, [puerta(2, 4)]), SalaVerificacion(3, []),
                      SalaVerificacion(4, [puerta(4, 2)])], [UbicacionLlave('X', 4)])
        r = verificar_resolubilidad(base)
        self.assertEqual(r.ciclos, [])
        self.assertEqual([u.id for u in r.llaves_inalcanzables], ['K', 'X'])
        self.comprobar_certificado(r, base)
        base = replace(base, ubicaciones=base.ubicaciones + [UbicacionLlave('K', 1)])
        self.assertEqual(verificar_resolubilidad(base).estado, 'resoluble')

    def test_FR008_AC14_opcionales_duplicados_y_campos_invalidos(self):
        base = datos([SalaVerificacion(1, [SalidaVerificacion(1, 'N', 3, None, 'K')]),
                      SalaVerificacion(3, [])], [UbicacionLlave('K', 1), UbicacionLlave('K', 1)])
        self.assertEqual(len(normalizar(base).ubicaciones_por_llave[0]), 1)
        self.assertEqual(verificar_resolubilidad(base).estado, 'resoluble')
        for salida in (SalidaVerificacion(1, 'X', 3), SalidaVerificacion(1, 'N', 3, 1),
                       SalidaVerificacion(True, 'N', 3), SalidaVerificacion(1, 'N', True)):
            with self.assertRaises(DatosInvalidos):
                normalizar(replace(base, salas=[SalaVerificacion(1, [salida]), base.salas[1]]))
        with self.assertRaises(DatosInvalidos):
            normalizar(replace(base, salas=[SalaVerificacion(1, base.salas[0].salidas * 2), base.salas[1]]))

    def test_FR014_AC18_sin_azar_red_o_mutaciones(self):
        import random
        from unittest.mock import patch
        base = datos([SalaVerificacion(1, [puerta(1, 3, 'K')]), SalaVerificacion(3, [])],
                     [UbicacionLlave('K', 1)])
        estado = random.getstate()
        copia = deepcopy(base)
        with patch('requests.sessions.Session.request', side_effect=AssertionError('Red inesperada')):
            r = verificar_resolubilidad(base)
        self.assertEqual(random.getstate(), estado)
        self.assertEqual(base, copia)
        self.assertEqual(r.orden_llaves, ['K'])

    def test_FR005_FR015_sin_recursion_en_ciclo_largo(self):
        salas = [SalaVerificacion(i, [puerta(i, i + 1)]) for i in range(1, 1600)]
        salas[0].salidas[0] = puerta(1, 2, 'K')
        salas.append(SalaVerificacion(1600, []))
        base = datos(salas, [UbicacionLlave('K', 1600)], salida=1600)
        r = verificar_resolubilidad(base)
        self.assertEqual(len(r.ciclos), 1)
        self.comprobar_certificado(r, base)
        self.comprobar_testigos(r)
    def comprobar_certificado(self, resultado, base):
        self.assertTrue(resultado.evidencia)
        for c in resultado.evidencia:
            valores = [resultado.evidencia[i].valor for i in c.requisitos]
            esperado = c.base or (all(valores) if c.operacion == "AND" else any(valores))
            self.assertEqual(c.valor, esperado)
            if c.tipo == 'sala':
                esperados = [i for i, paso in enumerate(resultado.evidencia)
                             if paso.tipo == 'paso' and paso.salida.destino == c.identificador]
                self.assertEqual(c.base, c.identificador == base.sala_inicial)
            elif c.tipo == 'llave':
                ubicaciones = []
                for u in base.ubicaciones:
                    if u.id == c.identificador and u not in ubicaciones:
                        ubicaciones.append(u)
                esperados = [next(i for i, s in enumerate(resultado.evidencia)
                                  if s.tipo == 'sala' and s.identificador == u.sala) for u in ubicaciones]
            else:
                original = next(salida for sala in base.salas for salida in sala.salidas
                                if salida.origen == c.salida.origen and salida.direccion == c.salida.direccion)
                self.assertEqual(original.destino, c.salida.destino)
                self.assertEqual(original.llave, c.salida.llave)
                esperados = [next(i for i, s in enumerate(resultado.evidencia)
                                  if s.tipo == 'sala' and s.identificador == original.origen)]
                if original.cerrada:
                    esperados.append(next(i for i, s in enumerate(resultado.evidencia)
                                          if s.tipo == 'llave' and s.identificador == original.llave))
            self.assertCountEqual(c.requisitos, esperados)

    def comprobar_testigos(self, resultado):
        for ciclo in resultado.ciclos:
            self.assertEqual(ciclo.testigo[0], ciclo.testigo[-1])
            self.assertGreater(len(ciclo.testigo), 1)
            for a, b in zip(ciclo.testigo, ciclo.testigo[1:]):
                self.assertIn(b, resultado.evidencia[a].requisitos)
                self.assertFalse(resultado.evidencia[a].valor)


if __name__ == "__main__":
    unittest.main()
