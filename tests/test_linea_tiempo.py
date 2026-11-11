"""Contrato sintético de historia; no requiere motor, red ni interfaz."""
import unittest

from modelo.snapshots import CambioHistorico, EventoHistorico, ValorHistorico
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo


def valor(dato):
    return ValorHistorico(True, dato)


def cambio(clave, antes, despues):
    return CambioHistorico(clave, valor(antes), valor(despues))


class TestLineaTiempo(unittest.TestCase):
    def crear(self, k=2):
        return LineaTiempo(EstadoHistorico((('vida', 10), ('sala', 1))), k)

    def avanzar(self, historia, cantidad):
        for _ in range(cantidad):
            n = historia.cantidad_acciones
            historia.registrar_accion(
                (n + 1) * 10, (cambio('sala', n + 1, n + 2),))

    def test_instante_y_antes_de_accion_no_confunden_la_decision(self):
        """FR-001, FR-002, FR-003: acción inmediata excluida en su inicio."""
        h = self.crear()
        h.registrar_accion(10, (cambio('sala', 1, 2),), (
            EventoHistorico(5, 1, (cambio('vida', 10, 9),)),))
        self.assertEqual(h.consultar_t(0).estado.obtener('sala'), 1)
        self.assertEqual(h.consultar_t(1).estado.obtener('sala'), 2)
        self.assertEqual(h.consultar_t(4).estado.obtener('vida'), 10)
        self.assertEqual(h.consultar_t(5).estado.obtener('vida'), 9)
        self.assertEqual(h.consultar_accion(1).estado.obtener('sala'), 1)
        h.registrar_accion(20, (cambio('sala', 2, 3),))
        self.assertEqual(h.consultar_t(10).estado.obtener('sala'), 2)
        self.assertEqual(h.consultar_accion(2).estado.obtener('vida'), 9)

    def test_h3_incluye_todos_los_eventos_del_instante(self):
        """FR-002: lotes empatados respetan su secuencia total."""
        h = self.crear()
        h.registrar_accion(10, (), (
            EventoHistorico(10, 1, (cambio('vida', 10, 8),)),
            EventoHistorico(10, 2, (cambio('vida', 8, 5),)),))
        self.assertEqual(h.consultar_t(10).estado.obtener('vida'), 5)
        self.assertEqual(h.consultar_t(9).estado.obtener('vida'), 10)

    def test_h1_rechaza_futuro_y_referencias_invalidas(self):
        """FR-001, FR-003, FR-020: errores sin cambios."""
        h = self.crear()
        self.avanzar(h, 1)
        for t in (-1, 11, True, 1.5, '5'):
            with self.subTest(t=t), self.assertRaises(ValueError):
                h.consultar_t(t)
        for k in (0, 2, -1, True):
            with self.subTest(k=k), self.assertRaises(ValueError):
                h.consultar_accion(k)
        self.assertEqual(h.reloj, 10)
        self.assertEqual(h.cantidad_acciones, 1)

    def test_h4_consulta_y_estado_inicial_no_comparten_mutables(self):
        """FR-005: consultar no altera historia ni datos del productor."""
        base = EstadoHistorico((('vida', 10),))
        h = LineaTiempo(base, 2)
        base.aplicar(cambio('vida', 10, 99))
        h.registrar_accion(10, (cambio('vida', 10, 8),))
        consulta = h.consultar_t(10)
        consulta.estado.aplicar(cambio('vida', 8, 0))
        self.assertEqual(h.consultar_t(10).estado.obtener('vida'), 8)
        self.assertEqual(h.consultar_t(0).estado.obtener('vida'), 10)
        self.assertEqual(h.cantidad_acciones, 1)

    def test_limite_k_incluso_consultas_parciales_y_historia_larga(self):
        """FR-009, FR-010: <=K acciones y copias solo en cadencia."""
        for k in (1, 3, 10):
            h = self.crear(k)
            self.avanzar(h, 101)
            self.assertEqual(h.cantidad_puntos_control, 1 + 101 // k)
            for t in range(1011):
                c = h.consultar_t(t)
                self.assertLessEqual(c.acciones_reconstruidas, k)
                esperado = 1 if t == 0 else 2 + (t - 1) // 10
                self.assertEqual(c.estado.obtener('sala'), esperado)
            for n in range(1, 102):
                self.assertEqual(h.consultar_accion(n).estado.obtener('sala'), n)

    def test_validacion_atomica_de_accion_sin_snapshot_por_accion(self):
        """FR-020: no queda una acción parcialmente aplicada."""
        h = self.crear()
        with self.assertRaises(ValueError):
            h.registrar_accion(10, (cambio('vida', 10, 8),), (
                EventoHistorico(5, 1, (cambio('vida', 99, 0),)),))
        self.assertEqual(h.cantidad_acciones, 0)
        self.assertEqual(h.reloj, 0)
        h.registrar_accion(10, (cambio('vida', 10, 7),))
        self.assertEqual(h.consultar_t(10).estado.obtener('vida'), 7)

    def test_validacion_de_orden_temporal_y_tipos(self):
        """FR-008, FR-020: no se aceptan secuencias ambiguas o mutables."""
        for k in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                self.crear(k)
        with self.assertRaises(ValueError):
            valor([1, 2])
        with self.assertRaises(ValueError):
            EstadoHistorico((('vida', 10), ('vida', 8)))
        for eventos in (
            (EventoHistorico(0, 1, ()),),
            (EventoHistorico(11, 1, ()),),
            (EventoHistorico(5, 2, ()), EventoHistorico(5, 1, ())),
            (EventoHistorico(5, 1, ()), EventoHistorico(5, 1, ())),
        ):
            with self.subTest(eventos=eventos), self.assertRaises(ValueError):
                self.crear().registrar_accion(10, (), eventos)

    def test_creacion_eliminacion_y_valor_nulo_son_distintos(self):
        """FR-004, FR-010: entidades creadas y eliminadas reconstruibles."""
        h = self.crear()
        ausente = ValorHistorico(False)
        h.registrar_accion(10, (
            CambioHistorico('objeto', ausente, valor(None)),), (
            EventoHistorico(8, 1, (
                CambioHistorico('objeto', valor(None), ausente),)),))
        self.assertIsNone(h.consultar_t(1).estado.obtener('objeto'))
        with self.assertRaises(KeyError):
            h.consultar_t(8).estado.obtener('objeto')

    def test_h2_recorte_elimina_futuro_y_permite_nueva_rama(self):
        """FR-007: no permanece el sufijo descartado."""
        h = self.crear()
        self.avanzar(h, 7)
        h.recortar(3)
        self.assertEqual(h.cantidad_acciones, 3)
        self.assertEqual(h.reloj, 30)
        self.assertEqual(h.cantidad_puntos_control, 2)
        with self.assertRaises(ValueError):
            h.consultar_t(70)
        h.registrar_accion(35, (cambio('sala', 4, 99),))
        self.assertEqual(h.consultar_t(35).estado.obtener('sala'), 99)
        self.assertEqual(h.consultar_accion(4).estado.obtener('sala'), 4)

    def test_correccion_persistente_en_y_entre_checkpoints(self):
        """FR-007: excepción de pergamino corrige frontera sin copia extra."""
        for conservar in (0, 2, 3):
            h = self.crear()
            self.avanzar(h, 5)
            h.recortar(conservar, (cambio('vida', 10, 8),))
            self.assertEqual(h.consultar_t(conservar * 10).estado.obtener('vida'), 8)
            self.assertEqual(h.cantidad_puntos_control, 1 + conservar // 2)
            h.registrar_accion((conservar + 1) * 10, (cambio('vida', 8, 7),))
            self.assertEqual(h.consultar_accion(conservar + 1).estado.obtener('vida'), 8)
            self.assertEqual(h.consultar_t(h.reloj).estado.obtener('vida'), 7)

    def test_recorte_fallido_no_descarta_historia(self):
        """FR-007, FR-020: validar antes de truncar."""
        h = self.crear()
        self.avanzar(h, 5)
        with self.assertRaises(ValueError):
            h.recortar(2, (cambio('vida', 0, 7),))
        self.assertEqual(h.cantidad_acciones, 5)
        self.assertEqual(h.consultar_t(50).estado.obtener('sala'), 6)

    def test_cinco_mil_acciones_con_cambios_y_consultas(self):
        """FR-006, FR-010: historia larga; verifica resultados, no latencia."""
        h = self.crear(50)
        self.avanzar(h, 5000)
        for n in (1, 49, 50, 51, 2499, 4999, 5000):
            consulta = h.consultar_accion(n)
            self.assertEqual(consulta.estado.obtener('sala'), n)
            self.assertLessEqual(consulta.acciones_reconstruidas, 50)
        self.assertEqual(h.consultar_t(50000).estado.obtener('sala'), 5001)
        self.assertEqual(h.cantidad_puntos_control, 101)

    def test_accion_fallida_tras_eliminar_campo_no_lo_resucita(self):
        """FR-020: transacción distingue ausencia de no haber tocado la clave."""
        h = self.crear()
        with self.assertRaises(ValueError):
            h.registrar_accion(10, (
                CambioHistorico('vida', valor(10), ValorHistorico(False)),
                cambio('vida', 10, 9)))
        self.assertEqual(h.consultar_t(0).estado.obtener('vida'), 10)

    def test_recorte_repetido_y_vuelta_al_inicio(self):
        """FR-007: nuevas ramas no reutilizan datos del futuro descartado."""
        h = self.crear(3)
        self.avanzar(h, 8)
        h.recortar(5)
        h.recortar(2)
        h.recortar(0)
        self.assertEqual(h.cantidad_puntos_control, 1)
        self.avanzar(h, 7)
        for n in range(1, 8):
            self.assertEqual(h.consultar_accion(n).estado.obtener('sala'), n)


if __name__ == '__main__':
    unittest.main()
