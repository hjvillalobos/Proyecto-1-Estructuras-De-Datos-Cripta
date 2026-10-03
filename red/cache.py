
from modelo.tipos import FichaCatalogo
from red.errores import ErrorCripta


class CacheSinEspacioError(ErrorCripta, RuntimeError):
    pass

class NodoLRU:

    def __init__(self, clave: str, ficha: FichaCatalogo | None):
        self.clave = clave
        self.ficha = ficha
        self.referencias = 0
        self.siguiente = None
        self.anterior = None


class CacheCatalogoOrdenado:

    def __init__(self, capacidad_maxima: int = 25):
        if isinstance(capacidad_maxima, bool) or not isinstance(capacidad_maxima, int):
            raise ValueError("La capacidad debe ser un entero positivo.")
        if capacidad_maxima <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")
        self.capacidad = capacidad_maxima
        self.tamaño_actual = 0
        self.arreglo: list[NodoLRU] = []

        self.cabeza = NodoLRU("CABEZA", None)
        self.cola = NodoLRU("COLA", None)
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza

    def _posicion(self, clave: str) -> int:

        izquierda = 0
        derecha = len(self.arreglo)
        while izquierda < derecha:
            medio = (izquierda + derecha) // 2
            if self.arreglo[medio].clave < clave:
                izquierda = medio + 1
            else:
                derecha = medio
        return izquierda


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
                indice = self._posicion(actual.clave)
                for i in range(indice, len(self.arreglo) - 1):
                    self.arreglo[i] = self.arreglo[i + 1]
                self.arreglo.pop()

                actual.anterior.siguiente = actual.siguiente
                actual.siguiente.anterior = actual.anterior
                actual.anterior = None
                actual.siguiente = None

                self.tamaño_actual -= 1
                return True

            actual = actual.anterior

        return False

    def insertar(self, clave: str, ficha: FichaCatalogo):
        indice = self._posicion(clave)
        if indice < len(self.arreglo) and self.arreglo[indice].clave == clave:
            nodo_existente = self.arreglo[indice]
            nodo_existente.ficha = ficha
            self._mover_al_frente(nodo_existente)
            return

        if self.tamaño_actual >= self.capacidad:
            if not self._desalojar_lru():
                raise CacheSinEspacioError(
                    f"No se puede insertar {clave}: las {self.capacidad} fichas "
                    "de la caché están en uso."
                )
            indice = self._posicion(clave)

        nuevo_nodo = NodoLRU(clave, ficha)
        self.arreglo.append(nuevo_nodo)
        for i in range(len(self.arreglo) - 1, indice, -1):
            self.arreglo[i] = self.arreglo[i - 1]
        self.arreglo[indice] = nuevo_nodo
        self._mover_al_frente(nuevo_nodo)
        self.tamaño_actual += 1

    def buscar(self, clave: str) -> FichaCatalogo | None:
        indice = self._posicion(clave)
        if indice < len(self.arreglo) and self.arreglo[indice].clave == clave:
            nodo = self.arreglo[indice]
            self._mover_al_frente(nodo)
            return nodo.ficha
        return None

    def modificar_referencia(self, clave: str, incremento: int):
        if isinstance(incremento, bool) or not isinstance(incremento, int):
            raise ValueError("El incremento de referencias debe ser entero.")
        indice = self._posicion(clave)
        if indice == len(self.arreglo) or self.arreglo[indice].clave != clave:
            raise KeyError(f"La ficha {clave} no está en caché.")
        nodo = self.arreglo[indice]
        if nodo.referencias + incremento < 0:
            raise ValueError(f"Las referencias de {clave} no pueden ser negativas.")
        nodo.referencias += incremento

    def contiene(self, clave):
        indice = self._posicion(clave)
        return indice < len(self.arreglo) and self.arreglo[indice].clave == clave

    def consultar(self, clave):
        indice = self._posicion(clave)
        if indice < len(self.arreglo) and self.arreglo[indice].clave == clave:
            return self.arreglo[indice].ficha
        return None

    def ajustar_referencias(self, ids):
        for nodo in self.arreglo:
            nodo.referencias = ids.count(nodo.clave)

    def vaciar(self):
        if any(nodo.referencias for nodo in self.arreglo):
            raise CacheSinEspacioError("No se puede cambiar de versión con fichas en uso.")
        for nodo in self.arreglo:
            nodo.anterior = None
            nodo.siguiente = None
        self.arreglo.clear()
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza
        self.tamaño_actual = 0
