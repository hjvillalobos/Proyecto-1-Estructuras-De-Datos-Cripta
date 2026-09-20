# tests/test_cache.py

import unittest
from modelo.tipos import FichaCatalogo
from red.cache import TablaHashCatalogo


class TestCacheLRU(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba. Prepara datos falsos."""
        # Creamos una caché con capacidad muy pequeña (3) para forzar el desalojo rápido
        self.cache = TablaHashCatalogo(capacidad_maxima=3)

        # Fichas de prueba
        self.ficha1 = FichaCatalogo("id_1", "arma", "Daga", {})
        self.ficha2 = FichaCatalogo("id_2", "pocion", "Vida", {})
        self.ficha3 = FichaCatalogo("id_3", "enemigo", "Rata", {})
        self.ficha4 = FichaCatalogo("id_4", "llave", "Bronce", {})

    def test_insercion_y_busqueda_basica(self):
        """Verifica que un elemento se guarde y se pueda recuperar."""
        self.cache.insertar(self.ficha1.id, self.ficha1)
        resultado = self.cache.buscar("id_1")

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.nombre, "Daga")

    def test_desalojo_lru_normal(self):
        """Verifica que el elemento más viejo se borre al superar la capacidad."""
        self.cache.insertar(self.ficha1.id, self.ficha1)  # Más viejo
        self.cache.insertar(self.ficha2.id, self.ficha2)
        self.cache.insertar(self.ficha3.id, self.ficha3)  # Más reciente

        # La caché está llena (capacidad 3). Al insertar el 4, debería borrar el 1.
        self.cache.insertar(self.ficha4.id, self.ficha4)

        self.assertIsNone(self.cache.buscar("id_1"), "La ficha 1 debió ser desalojada")
        self.assertIsNotNone(self.cache.buscar("id_2"), "La ficha 2 debe seguir en caché")
        self.assertIsNotNone(self.cache.buscar("id_4"), "La ficha 4 debe estar en caché")

    def test_proteccion_referencias_activas(self):
        """Verifica que un elemento en uso NO sea desalojado, saltando al siguiente más viejo."""
        self.cache.insertar(self.ficha1.id, self.ficha1)  # Más viejo
        self.cache.insertar(self.ficha2.id, self.ficha2)  # Segundo más viejo
        self.cache.insertar(self.ficha3.id, self.ficha3)  # Más reciente

        # Marcamos la ficha 1 como "en uso" (ej. el jugador la tiene equipada)
        self.cache.modificar_referencia("id_1", 1)

        # Al insertar la 4, el LRU intentará borrar la 1, pero como está en uso,
        # debe saltarla y borrar la ficha 2.
        self.cache.insertar(self.ficha4.id, self.ficha4)

        self.assertIsNotNone(self.cache.buscar("id_1"), "La ficha 1 NO debió borrarse porque está en uso")
        self.assertIsNone(self.cache.buscar("id_2"), "La ficha 2 debió ser desalojada en lugar de la 1")
        self.assertIsNotNone(self.cache.buscar("id_4"), "La ficha 4 debe estar en caché")


if __name__ == '__main__':
    unittest.main()