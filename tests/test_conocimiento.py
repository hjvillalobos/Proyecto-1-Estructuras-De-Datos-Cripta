"""C01–C04, C12–C14 de 002-niebla-viaje; sin motor, red ni interfaz."""
import unittest

from modelo.conocimiento import (
    ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible,
    CambioConocimiento, DESCONOCIDA, AVISTADA, EXPLORADA,
)


def escenario():
    return (
        SalaConocible(10, "Entrada", (SalidaConocible("E", 9000, 100, 7),)),
        SalaConocible(9000, "Galería", (
            SalidaConocible("O", 10, 100, 7), SalidaConocible("N", 42, 3))),
        SalaConocible(42, "Secreto", (SalidaConocible("S", 9000, 3),)),
    )


def crear(salas=None):
    return ConocimientoMapa(escenario() if salas is None else salas,
                            (PuertaConocible(7, 10, 9000),), 10)


class TestConocimiento(unittest.TestCase):
    def test_inicial_y_proyeccion_sin_filtraciones(self):
        """FR-001–003/005: C01, C02, C04."""
        mapa = crear()
        self.assertEqual(mapa.estado_sala(10), EXPLORADA)
        self.assertEqual(mapa.estado_sala(9000), AVISTADA)
        self.assertEqual(mapa.estado_sala(42), DESCONOCIDA)
        self.assertEqual(mapa.estado_sala(123), DESCONOCIDA)
        self.assertEqual(mapa.mapa_conocido(), (
            (10, EXPLORADA, "Entrada", (("E", 9000, 100, 7, None),)),
            (9000, AVISTADA, None, ()),
        ))
        self.assertIsNone(mapa.recuerdo_puerta(7))

    def test_entrada_sin_recursion_y_repeticion(self):
        """FR-001/003/014: solo las vecinas pasan a avistadas."""
        m = crear()
        cambios = m.entrar(9000)
        self.assertEqual(m.estado_sala(42), AVISTADA)
        self.assertEqual(m.entrar(9000), ())
        self.assertEqual(m.estado_sala(10), EXPLORADA)
        m.revertir(cambios)
        self.assertEqual(m.mapa_conocido(), crear().mapa_conocido())

    def test_memoria_desde_ambos_extremos(self):
        """FR-004: C03; solo la observación explícita actualiza."""
        m = crear()
        abrir = m.observar_puerta(10, 7, False)
        entrada = m.entrar(9000)
        self.assertIs(m.recuerdo_puerta(7), False)
        cerrar = m.observar_puerta(9000, 7, True)
        self.assertIs(m.mapa_conocido()[0][3][0][4], True)
        m.revertir(cerrar)
        m.revertir(entrada)
        m.revertir(abrir)
        self.assertIsNone(m.recuerdo_puerta(7))

    def test_reconstruccion_y_reversion_varios_lotes(self):
        """FR-014/017: C12, datos de cambios transportables."""
        a, b = crear(), crear(tuple(reversed(escenario())))
        lotes = (a.observar_puerta(10, 7, False), a.entrar(9000),
                 a.observar_puerta(9000, 7, True), a.entrar(42))
        for lote in lotes:
            b.aplicar(lote)
        self.assertEqual(a.mapa_conocido(), b.mapa_conocido())
        for lote in reversed(lotes):
            a.revertir(lote)
            b.revertir(lote)
        self.assertEqual(a.mapa_conocido(), crear().mapa_conocido())
        self.assertEqual(a.mapa_conocido(), b.mapa_conocido())

    def test_lote_incompatible_no_deja_prefijo_aplicado(self):
        """FR-014/017: rechazo atómico C12."""
        m = crear()
        antes = m.mapa_conocido()
        lote = (CambioConocimiento("sala", 9000, AVISTADA, EXPLORADA),
                CambioConocimiento("puerta", 7, False, True))
        with self.assertRaises(ValueError):
            m.aplicar(lote)
        self.assertEqual(m.mapa_conocido(), antes)

    def test_cambios_consecutivos_mismo_campo(self):
        """FR-014: inversión exacta, sin deduplicación que pierda estados."""
        m = crear()
        lote = (CambioConocimiento("puerta", 7, None, False),
                CambioConocimiento("puerta", 7, False, True))
        m.aplicar(lote)
        self.assertIs(m.recuerdo_puerta(7), True)
        m.revertir(lote)
        self.assertIsNone(m.recuerdo_puerta(7))

    def test_observaciones_invalidas_no_mutan(self):
        """FR-004: no observar desde sala ajena o no explorada."""
        m = crear()
        for sala, puerta, estado in ((9000, 7, False), (42, 7, False),
                                     (10, 7, 0), (10, 99, False)):
            with self.assertRaises(ValueError):
                m.observar_puerta(sala, puerta, estado)
        self.assertIsNone(m.recuerdo_puerta(7))

    def test_ids_dispersos_no_reservan_hasta_id_maximo(self):
        """PR-002: C13; memoria por entidad, no por ID."""
        m = ConocimientoMapa((SalaConocible(10**12, "A", ()),), (), 10**12)
        self.assertEqual(len(m._estados), 1)
        self.assertEqual(m.estado_sala(10**12), EXPLORADA)

    def test_rechaza_esqueleto_incoherente(self):
        """C14: precondición interna, no política de corrección de API."""
        casos = (
            (SalaConocible(1, "A", ()), SalaConocible(1, "B", ())),
            (SalaConocible(1, "A", (SalidaConocible("E", 2, 1),)),),
            (SalaConocible(1, "A", (SalidaConocible("E", 1, 0),)),),
        )
        for salas in casos:
            with self.assertRaises(ValueError):
                ConocimientoMapa(salas, (), 1)

    def test_entrada_inexistente_no_muta(self):
        m = crear()
        antes = m.mapa_conocido()
        with self.assertRaises(ValueError):
            m.entrar(999)
        self.assertEqual(m.mapa_conocido(), antes)

    def test_lotes_mal_tipados_no_mutan(self):
        m = crear()
        for lote in ((CambioConocimiento("sala", 10, True, 2),),
                     (CambioConocimiento("puerta", 7, None, 0),),
                     (CambioConocimiento("otro", 7, None, True),)):
            with self.assertRaises(ValueError):
                m.aplicar(lote)
        self.assertEqual(m.mapa_conocido(), crear().mapa_conocido())

    def test_reversion_incompatible_es_atomica(self):
        """FR-014: también el rollback de una reversión parcial es exacto."""
        m = crear()
        m.observar_puerta(10, 7, True)
        antes = m.mapa_conocido()
        lote = (CambioConocimiento("sala", 9000, AVISTADA, EXPLORADA),
                CambioConocimiento("puerta", 7, None, True))
        with self.assertRaises(ValueError):
            m.revertir(lote)
        self.assertEqual(m.mapa_conocido(), antes)

    def test_observacion_repetida_no_produce_cambios(self):
        m = crear()
        m.observar_puerta(10, 7, False)
        self.assertEqual(m.observar_puerta(10, 7, False), ())

    def test_direcciones_y_puertas_invalidas(self):
        """C14: validación sin atribuir políticas a los adaptadores de B."""
        with self.assertRaises(ValueError):
            ConocimientoMapa((SalaConocible(1, "A", (
                SalidaConocible("E", 1, 1), SalidaConocible("E", 1, 2))),), (), 1)
        with self.assertRaises(ValueError):
            ConocimientoMapa(escenario(), (PuertaConocible(7, 10, 42),), 10)
        with self.assertRaises(ValueError):
            ConocimientoMapa(escenario(), (), 10)

    def test_entrada_no_recorre_mapa_completo(self):
        """PR-002: C13 verifica localidad, no solo un tiempo favorable."""
        from utilidades.bench_conocimiento import cadena

        class Accesos(list):
            def __init__(self, valores):
                super().__init__(valores)
                self.lecturas = 0

            def __iter__(self):
                raise AssertionError("No se debe recorrer todo el estado al entrar")

            def __getitem__(self, indice):
                self.lecturas += 1
                return super().__getitem__(indice)

        resultados = []
        for cantidad in (10, 10000):
            m = ConocimientoMapa(cadena(cantidad), (), 0)
            m._estados = Accesos(m._estados)
            m._salidas = Accesos(m._salidas)
            cambios = m.entrar(1009)
            resultados.append((m._estados.lecturas, m._salidas.lecturas, len(cambios)))
        self.assertEqual(resultados[0], resultados[1])
        self.assertEqual(resultados[0][2], 2)

    def test_sin_puerta_y_costo_se_conservan(self):
        m = crear()
        m.entrar(9000)
        salidas = m.mapa_conocido()[-1][3]
        self.assertIn(("N", 42, 3, None, False), salidas)


if __name__ == "__main__":
    unittest.main()
