"""002-niebla-viaje FR-018, C15/C16: decisión local, no viaje integrado."""
import unittest
from modelo.detencion_viaje import HechosPaso, evaluar_detencion


class TestDetencionViaje(unittest.TestCase):
    def test_todas_las_combinaciones(self):
        for mascara in range(64):
            llegada, dano, entrada, enemigos, ruta, cancelado = (
                bool(mascara & (1 << i)) for i in range(6))
            hechos = HechosPaso(llegada, dano, entrada, enemigos, ruta, cancelado)
            resultado = evaluar_detencion(hechos)
            esperado = cancelado or dano or (entrada and enemigos) or llegada or not ruta
            self.assertEqual(not resultado.continuar, esperado)
            self.assertEqual("cancelacion" in resultado.causas, cancelado)
            self.assertEqual("dano" in resultado.causas, dano)
            self.assertEqual("enemigos" in resultado.causas, entrada and enemigos)
            self.assertEqual("llegada" in resultado.causas, llegada)
            self.assertEqual("sin_ruta" in resultado.causas, not ruta)
            self.assertEqual(resultado, evaluar_detencion(hechos))

    def test_conserva_todas_las_causas(self):
        self.assertEqual(evaluar_detencion(HechosPaso(True, True, True, True, False, True)).causas,
                         ("cancelacion", "dano", "enemigos", "llegada", "sin_ruta"))

    def test_no_deduce_dano_desde_vida_final(self):
        # La vida final ni siquiera es entrada: el hecho de daño basta.
        self.assertEqual(evaluar_detencion(HechosPaso(False, True, True, False, True, False)).causas,
                         ("dano",))

    def test_rechaza_hechos_no_booleanos(self):
        for valor in (0, 1, None, "si"):
            with self.assertRaises(ValueError):
                HechosPaso(valor, False, False, False, True, False)

    def test_no_acepta_objetos_ajenos(self):
        with self.assertRaises(ValueError):
            evaluar_detencion(None)


if __name__ == "__main__":
    unittest.main()
