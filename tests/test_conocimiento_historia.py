"""C18–C20 con LineaTiempo real; ejecutar mediante el verificador aislado."""
import unittest

from modelo.conocimiento import CambioConocimiento
from tests.test_conocimiento import crear


class TestConocimientoHistoria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Dependencia aún no fusionada: reportar ausencia, nunca usar un doble.
        try:
            from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
        except ModuleNotFoundError as error:
            if error.name != 'modelo.linea_tiempo':
                raise
            raise unittest.SkipTest(
                'D no está integrado; ejecutar python -m utilidades.verificar_conocimiento_historia')
        from modelo.snapshots import CambioHistorico, ValorHistorico, EventoHistorico
        from modelo.conocimiento_historia import campos_iniciales, convertir_cambios
        cls.Estado = EstadoHistorico
        cls.Historia = LineaTiempo
        cls.Cambio = CambioHistorico
        cls.Valor = ValorHistorico
        cls.Evento = EventoHistorico
        cls.base = staticmethod(campos_iniciales)
        cls.convertir = staticmethod(convertir_cambios)

    def preparar(self):
        mapa = crear()
        return mapa, self.Historia(self.Estado(self.base(mapa)))

    def test_entrada_y_consulta_anterior_a_segunda_accion(self):
        """FR-019 C18: base y conocimiento al cierre y antes de acción 2."""
        mapa, h = self.preparar()
        lote = mapa.entrar(9000)
        h.registrar_accion(100, self.convertir(lote))
        self.assertEqual(h.consultar_t(0).estado.obtener('conocimiento:sala:9000'), 1)
        with self.assertRaises(KeyError):
            h.consultar_t(0).estado.obtener('conocimiento:sala:42')
        self.assertEqual(h.consultar_t(100).estado.obtener('conocimiento:sala:9000'), 2)
        self.assertEqual(h.consultar_t(100).estado.obtener('conocimiento:sala:42'), 1)
        estado_cierre = h.consultar_t(100).estado.campos()
        h.registrar_accion(200)
        self.assertEqual(h.consultar_accion(2).estado.campos(), estado_cierre)

    def test_rechazo_de_lote_y_rollback_local(self):
        """FR-019 C19: D no cambia; productor revierte C sin recortar D."""
        mapa, h = self.preparar()
        antes_mapa, antes_historia = mapa.mapa_conocido(), h.exportar()
        lote = mapa.entrar(9000)
        incoherente = self.Cambio('conocimiento:sala:10', self.Valor(True, 99), self.Valor(True, 1))
        with self.assertRaises(ValueError):
            h.registrar_accion(100, self.convertir(lote) + (incoherente,))
        mapa.revertir(lote)  # El futuro motor debe hacer esto con todo su turno.
        self.assertEqual(mapa.mapa_conocido(), antes_mapa)
        self.assertEqual(h.exportar(), antes_historia)
        self.assertEqual((h.reloj, h.cantidad_acciones), (0, 0))

    def test_observaciones_temporales_y_recorte(self):
        """FR-019 C20: memoria temporal y recorte de una acción aceptada."""
        mapa, h = self.preparar()
        abierto = mapa.observar_puerta(10, 7, False)
        h.registrar_accion(100, (), (self.Evento(50, 1, self.convertir(abierto)),))
        with self.assertRaises(KeyError):
            h.consultar_t(49).estado.obtener('conocimiento:puerta:7')
        self.assertIs(h.consultar_t(50).estado.obtener('conocimiento:puerta:7'), False)
        cerrado = mapa.observar_puerta(10, 7, True)
        h.registrar_accion(200, (), (self.Evento(150, 2, self.convertir(cerrado)),))
        self.assertIs(h.consultar_t(149).estado.obtener('conocimiento:puerta:7'), False)
        self.assertIs(h.consultar_t(150).estado.obtener('conocimiento:puerta:7'), True)
        h.recortar(1)
        mapa.revertir(cerrado)
        self.assertIs(mapa.recuerdo_puerta(7), False)
        self.assertEqual(h.consultar_final().estado.campos(), self.Estado(self.base(mapa)).campos())

    def test_base_no_duplica_puerta_ni_muestra_desconocidas(self):
        mapa = crear()
        mapa.observar_puerta(10, 7, False)
        mapa.entrar(9000)
        campos = self.base(mapa)
        self.assertEqual(sum(clave == 'conocimiento:puerta:7' for clave, _ in campos), 1)
        self.assertNotIn('conocimiento', tuple(clave for clave, _ in campos))
        self.assertEqual(self.Estado(campos).obtener('conocimiento:puerta:7'), False)

    def test_conversion_no_muta_y_distingue_ausencia(self):
        mapa = crear()
        lote = mapa.observar_puerta(10, 7, False)
        antes = mapa.mapa_conocido()
        salida = self.convertir(lote)
        self.assertEqual(mapa.mapa_conocido(), antes)
        self.assertEqual(salida[0].anterior, self.Valor(False))
        self.assertEqual(salida[0].nuevo, self.Valor(True, False))
        for invalido in ((CambioConocimiento('sala', 1, True, 2),),
                         (CambioConocimiento('puerta', 7, None, 0),),
                         (CambioConocimiento('otro', 7, None, True),), []):
            with self.assertRaises(ValueError):
                self.convertir(invalido)


if __name__ == '__main__':
    unittest.main()
