
import unittest
import random
from modelo.tipos import FichaCatalogo
from red.cache import CacheCatalogoOrdenado, CacheSinEspacioError
from utilidades.bench_cache import CacheCatalogoLineal

class TestCacheLRU(unittest.TestCase):
    tipo_cache = CacheCatalogoOrdenado

    def setUp(self):
        self.cache = self.tipo_cache(capacidad_maxima=3)

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


    def claves_lru(self, cache):
        claves = []
        anterior = cache.cabeza
        actual = anterior.siguiente
        while actual is not cache.cola:
            self.assertIs(actual.anterior, anterior)
            claves.append(actual.clave)
            self.assertLessEqual(len(claves), cache.capacidad, "Ciclo o exceso de capacidad")
            anterior, actual = actual, actual.siguiente
        self.assertIs(cache.cola.anterior, anterior)
        self.assertEqual(len(claves), cache.tamaño_actual)
        self.assertEqual(len(cache.arreglo), cache.tamaño_actual)
        for i, nodo in enumerate(cache.arreglo):
            self.assertIn(nodo.clave, claves)
            if i:
                self.assertLess(cache.arreglo[i - 1].clave, nodo.clave)
        return claves

    def test_indice_ordenado_independiente_de_lru(self):
        for ficha in (self.ficha3, self.ficha1, self.ficha2):
            self.cache.insertar(ficha.id, ficha)
        self.assertEqual([n.clave for n in self.cache.arreglo], ["id_1", "id_2", "id_3"])
        self.assertEqual(self.claves_lru(self.cache), ["id_2", "id_1", "id_3"])
        self.assertIs(self.cache.buscar("id_3"), self.ficha3)
        self.assertEqual(self.claves_lru(self.cache), ["id_3", "id_2", "id_1"])

    def test_busquedas_ausentes_y_limites(self):
        self.assertIsNone(self.cache.buscar("id_1"))
        for ficha in (self.ficha1, self.ficha3):
            self.cache.insertar(ficha.id, ficha)
        for clave in ("id_0", "id_2", "id_4"):
            self.assertIsNone(self.cache.buscar(clave))
        self.assertIs(self.cache.buscar("id_1"), self.ficha1)
        self.assertIs(self.cache.buscar("id_3"), self.ficha3)

    def test_busqueda_actualiza_lru(self):
        for ficha in (self.ficha1, self.ficha2, self.ficha3):
            self.cache.insertar(ficha.id, ficha)
        self.cache.buscar("id_1")
        self.cache.insertar("id_4", self.ficha4)
        self.assertIsNone(self.cache.buscar("id_2"))
        self.assertEqual(self.claves_lru(self.cache), ["id_4", "id_1", "id_3"])

    def test_recalcula_posicion_despues_del_desalojo(self):
        for ficha in (self.ficha1, self.ficha3, self.ficha4):
            self.cache.insertar(ficha.id, ficha)
        self.cache.insertar("id_2", self.ficha2)
        self.assertEqual([n.clave for n in self.cache.arreglo], ["id_2", "id_3", "id_4"])
        self.assertEqual(self.claves_lru(self.cache), ["id_2", "id_4", "id_3"])

    def test_todas_protegidas_no_cambia_estado(self):
        for ficha in (self.ficha1, self.ficha2, self.ficha3):
            self.cache.insertar(ficha.id, ficha)
            self.cache.modificar_referencia(ficha.id, 1)
        orden_antes = self.claves_lru(self.cache)
        nodos_antes = self.cache.arreglo.copy()
        with self.assertRaises(CacheSinEspacioError):
            self.cache.insertar("id_4", self.ficha4)
        self.assertEqual(self.claves_lru(self.cache), orden_antes)
        self.assertEqual(self.cache.arreglo, nodos_antes)
        self.assertIsNone(self.cache.buscar("id_4"))
        self.cache.modificar_referencia("id_2", -1)
        self.cache.insertar("id_4", self.ficha4)
        self.assertEqual(self.claves_lru(self.cache), ["id_4", "id_3", "id_1"])

    def test_actualizar_existente_conserva_nodo_y_referencias(self):
        for ficha in (self.ficha1, self.ficha2, self.ficha3):
            self.cache.insertar(ficha.id, ficha)
            self.cache.modificar_referencia(ficha.id, 1)
        nodo_original = self.cache.arreglo[0]
        nueva = FichaCatalogo("id_1", "arma", "Daga nueva", {})
        self.cache.insertar("id_1", nueva)
        self.assertIs(self.cache.arreglo[0], nodo_original)
        self.assertEqual(nodo_original.referencias, 1)
        self.assertIs(self.cache.buscar("id_1"), nueva)
        self.assertEqual(self.claves_lru(self.cache), ["id_1", "id_3", "id_2"])

    def test_referencias_invalidas(self):
        self.cache.insertar("id_1", self.ficha1)
        with self.assertRaises(KeyError):
            self.cache.modificar_referencia("ausente", 1)
        for incremento in (-1, 0.5, True):
            with self.assertRaises(ValueError):
                self.cache.modificar_referencia("id_1", incremento)
        self.assertEqual(self.cache.arreglo[0].referencias, 0)

    def test_capacidad_invalida(self):
        for capacidad in (0, -1, 1.5, True):
            with self.subTest(capacidad=capacidad), self.assertRaises(ValueError):
                self.tipo_cache(capacidad)

    def test_capacidad_uno(self):
        cache = self.tipo_cache(1)
        cache.insertar("id_1", self.ficha1)
        cache.insertar("id_2", self.ficha2)
        self.assertEqual(self.claves_lru(cache), ["id_2"])
        self.assertIsNone(cache.buscar("id_1"))

    def test_secuencia_aleatoria_contra_modelo_simple(self):
        cache = self.tipo_cache(7)
        modelo = []
        azar = random.Random(42)
        for _ in range(600):
            clave = f"id_{azar.randrange(15):02d}"
            posicion = next((i for i, fila in enumerate(modelo) if fila[0] == clave), None)
            accion = azar.randrange(3)
            if accion == 0:
                esperado = None
                if posicion is not None:
                    fila = modelo.pop(posicion)
                    modelo.insert(0, fila)
                    esperado = fila[1]
                self.assertIs(cache.buscar(clave), esperado)
            elif accion == 1:
                ficha = FichaCatalogo(clave, "arma", clave, {})
                if posicion is not None:
                    fila = modelo.pop(posicion)
                    fila[1] = ficha
                    modelo.insert(0, fila)
                    cache.insertar(clave, ficha)
                else:
                    victima = next((i for i in range(len(modelo) - 1, -1, -1)
                                    if modelo[i][2] == 0), None)
                    if len(modelo) == cache.capacidad and victima is None:
                        with self.assertRaises(CacheSinEspacioError):
                            cache.insertar(clave, ficha)
                    else:
                        if len(modelo) == cache.capacidad:
                            modelo.pop(victima)
                        modelo.insert(0, [clave, ficha, 0])
                        cache.insertar(clave, ficha)
            elif posicion is not None:
                incremento = -1 if modelo[posicion][2] and azar.randrange(2) else 1
                modelo[posicion][2] += incremento
                cache.modificar_referencia(clave, incremento)
            self.assertEqual(self.claves_lru(cache), [fila[0] for fila in modelo])
            for nodo in cache.arreglo:
                fila = next(fila for fila in modelo if fila[0] == nodo.clave)
                self.assertIs(nodo.ficha, fila[1])
                self.assertEqual(nodo.referencias, fila[2])


class TestCacheLineal(TestCacheLRU):
    tipo_cache = CacheCatalogoLineal


if __name__ == '__main__':
    unittest.main()
