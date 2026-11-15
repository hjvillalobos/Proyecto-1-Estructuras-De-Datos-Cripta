"""RF-02: memoria acotada por salas, identidad y copia independiente."""
from copy import deepcopy
from unittest import TestCase
from modelo.almacen_salas import TablaPorId, crear_almacen


class AlmacenSalasTest(TestCase):
    def test_ids_grandes_no_reservan_huecos(self):
        tabla = crear_almacen((0, 1_000_000_000, 4_000_000_000), list)
        self.assertIsInstance(tabla, TablaPorId)
        self.assertEqual(len(tabla.valores), 3)
        tabla[1_000_000_000].append('objeto')
        self.assertEqual(list(tabla), [[], ['objeto'], []])
        self.assertIsNone(tabla[12])
        with self.assertRaises(IndexError):
            tabla[12] = []
        copia = deepcopy(tabla)
        copia[1_000_000_000].clear()
        self.assertEqual(tabla[1_000_000_000], ['objeto'])

    def test_denso_conserva_acceso_directo(self):
        tabla = crear_almacen((1, 2, 3), lambda: False)
        self.assertIsInstance(tabla, list)
        self.assertEqual(tabla, [False] * 4)

    def test_radix_limites_de_digitos_y_huecos(self):
        ids = (0, 15, 16, 255, 256, 65535, 65536, 2**32 - 1)
        tabla = TablaPorId(ids, lambda: None)
        for i in ids:
            tabla[i] = i + 1
        for i in ids:
            self.assertEqual(tabla[i], i + 1)
        for i in (1, 14, 17, 254, 257, 65534, 65537, 2**32):
            self.assertIsNone(tabla[i])

    def test_rastro_en_ids_grandes_y_empate(self):
        from modelo.rastro import RegistroRastro
        r = RegistroRastro(ids=(1_000_000_000, 4_000_000_000))
        for i in (1_000_000_000, 4_000_000_000):
            r.marcar_visita(i, 20)
        self.assertEqual(r.sala_mas_fresca((4_000_000_000, 1_000_000_000), 21), 1_000_000_000)
        self.assertIsNone(r.tiempo_de(30))
