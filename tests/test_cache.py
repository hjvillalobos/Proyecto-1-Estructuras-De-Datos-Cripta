
import unittest
from modelo.tipos import FichaCatalogo
from red.cache import TablaHashCatalogo

class TestCacheLRU(unittest.TestCase):

    def setUp(self):
        self.cache = TablaHashCatalogo(capacidad_maxima=3)

        self.ficha1 = FichaCatalogo("id_1", "arma", "Daga", {})
        self.ficha2 = FichaCatalogo("id_2", "pocion", "Vida", {})
        self.ficha3 = FichaCatalogo("id_3", "enemigo", "Rata", {})
        self.ficha4 = FichaCatalogo("id_4", "llave", "Bronce", {})

    def test_insercion_y_busqueda_basica(self):
        self.cache.insertar(self.ficha1.id, self.ficha1)
        resultado = self.cache.buscar("id_1")

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nombre, "Daga")

    def test_desalojo_lru_normal(self):
        self.cache.insertar(self.ficha1.id, self.ficha1)
        self.cache.insertar(self.ficha2.id, self.ficha2)
        self.cache.insertar(self.ficha3.id, self.ficha3)

        self.cache.insertar(self.ficha4.id, self.ficha4)

        self.assertIsNone(self.cache.buscar("id_1"), "La ficha 1 debió ser desalojada")
        self.assertIsNotNone(self.cache.buscar("id_2"), "La ficha 2 debe seguir en caché")
        self.assertIsNotNone(self.cache.buscar("id_4"), "La ficha 4 debe estar en caché")

    def test_proteccion_referencias_activas(self):
        self.cache.insertar(self.ficha1.id, self.ficha1)
        self.cache.insertar(self.ficha2.id, self.ficha2)
        self.cache.insertar(self.ficha3.id, self.ficha3)

        self.cache.modificar_referencia("id_1", 1)
        self.cache.insertar(self.ficha4.id, self.ficha4)

        self.assertIsNotNone(self.cache.buscar("id_1"), "La ficha 1 NO debió borrarse porque está en uso")
        self.assertIsNone(self.cache.buscar("id_2"), "La ficha 2 debió ser desalojada en lugar de la 1")
        self.assertIsNotNone(self.cache.buscar("id_4"), "La ficha 4 debe estar en caché")


if __name__ == '__main__':
    unittest.main()