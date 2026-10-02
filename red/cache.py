
from modelo.tipos import FichaCatalogo


class NodoLRU:

    def __init__(self, clave: str, ficha: FichaCatalogo):
        self.clave = clave
        self.ficha = ficha
        self.referencias = 0
        self.siguiente = None
        self.anterior = None


class TablaHashCatalogo:
    def __init__(self, capacidad_maxima: int = 25):
        self.capacidad = capacidad_maxima  # Límite de la caché
        self.tamaño_actual = 0
        self.arreglo = [[] for _ in range(self.capacidad)]


        self.cabeza = NodoLRU("CABEZA", None)
        self.cola = NodoLRU("COLA", None)
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza

    def _hash(self, clave: str) -> int:
        valor = 0
        for i, char in enumerate(clave):
            valor = (valor + ord(char) * (31 ** i)) % (10 ** 9 + 9)
        return valor % self.capacidad


    def _mover_al_frente(self, nodo: NodoLRU):
        if nodo.anterior and nodo.siguiente:
            nodo.anterior.siguiente = nodo.siguiente
            nodo.siguiente.anterior = nodo.anterior

        primer_nodo_real = self.cabeza.siguiente
        self.cabeza.siguiente = nodo
        nodo.anterior = self.cabeza
        nodo.siguiente = primer_nodo_real
        primer_nodo_real.anterior = nodo

    def _desalojar_lru(self):
        actual = self.cola.anterior

        while actual != self.cabeza:
            if actual.referencias == 0:
                actual.anterior.siguiente = actual.siguiente
                actual.siguiente.anterior = actual.anterior

                indice = self._hash(actual.clave)
                self.arreglo[indice].remove((actual.clave, actual))

                self.tamaño_actual -= 1
                return True

            actual = actual.anterior

        return False

    def insertar(self, clave: str, ficha: FichaCatalogo):
        indice = self._hash(clave)
        cubeta = self.arreglo[indice]

        for i, (k, nodo_existente) in enumerate(cubeta):
            if k == clave:
                nodo_existente.ficha = ficha
                self._mover_al_frente(nodo_existente)
                return

        if self.tamaño_actual >= self.capacidad:
            self._desalojar_lru()

        nuevo_nodo = NodoLRU(clave, ficha)
        cubeta.append((clave, nuevo_nodo))
        self._mover_al_frente(nuevo_nodo)
        self.tamaño_actual += 1

    def buscar(self, clave: str) -> FichaCatalogo | None:
        indice = self._hash(clave)
        cubeta = self.arreglo[indice]

        for k, nodo in cubeta:
            if k == clave:
                self._mover_al_frente(nodo)
                return nodo.ficha
        return None

    def modificar_referencia(self, clave: str, incremento: int):
        indice = self._hash(clave)
        for k, nodo in self.arreglo[indice]:
            if k == clave:
                nodo.referencias += incremento
                return