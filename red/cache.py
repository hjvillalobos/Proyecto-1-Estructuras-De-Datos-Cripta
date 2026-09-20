# red/cache.py

# red/cache.py

from modelo.tipos import FichaCatalogo


class NodoLRU:
    """Nodo para la lista doblemente enlazada y almacenamiento en hash."""

    def __init__(self, clave: str, ficha: FichaCatalogo):
        self.clave = clave
        self.ficha = ficha
        self.referencias = 0  # Contador en_uso
        self.siguiente = None  # Puntero al siguiente (más reciente)
        self.anterior = None  # Puntero al anterior (más viejo)


class TablaHashCatalogo:
    def __init__(self, capacidad_maxima: int = 25):
        self.capacidad = capacidad_maxima  # Límite de la caché
        self.tamaño_actual = 0
        self.arreglo = [[] for _ in range(self.capacidad)]

        # Punteros de la lista doblemente enlazada (Centinelas vacíos para facilitar inserción)
        self.cabeza = NodoLRU("CABEZA", None)  # El más reciente
        self.cola = NodoLRU("COLA", None)  # El más viejo
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza

    def _hash(self, clave: str) -> int:
        valor = 0
        for i, char in enumerate(clave):
            valor = (valor + ord(char) * (31 ** i)) % (10 ** 9 + 9)
        return valor % self.capacidad

    # --- LÓGICA DE PUNTEROS (LISTA DOBLEMENTE ENLAZADA) ---

    def _mover_al_frente(self, nodo: NodoLRU):
        """Mueve un nodo consultado justo detrás de la cabeza (el más reciente)."""
        # 1. Desconectar de su posición actual
        if nodo.anterior and nodo.siguiente:
            nodo.anterior.siguiente = nodo.siguiente
            nodo.siguiente.anterior = nodo.anterior

        # 2. Conectar detrás de la cabeza
        primer_nodo_real = self.cabeza.siguiente
        self.cabeza.siguiente = nodo
        nodo.anterior = self.cabeza
        nodo.siguiente = primer_nodo_real
        primer_nodo_real.anterior = nodo

    def _desalojar_lru(self):
        """Busca desde la cola hacia arriba un nodo sin referencias y lo elimina[cite: 1]."""
        actual = self.cola.anterior  # Empezamos por el candidato más viejo

        while actual != self.cabeza:
            if actual.referencias == 0:
                # 1. Quitarlo de la lista enlazada
                actual.anterior.siguiente = actual.siguiente
                actual.siguiente.anterior = actual.anterior

                # 2. Quitarlo del arreglo Hash
                indice = self._hash(actual.clave)
                self.arreglo[indice].remove((actual.clave, actual))

                self.tamaño_actual -= 1
                # TODO (Opcional): Guardar los datos de 'actual.ficha' en disco antes de borrarlo definitivamente
                return True

            actual = actual.anterior  # Retroceder al siguiente más viejo

        # Si llegamos aquí, la caché está llena y TODOS están en uso.
        # (Esto requeriría que el GestorCatalogo arroje un error o espere).
        return False

    # --- LÓGICA DE LA TABLA HASH ---

    def insertar(self, clave: str, ficha: FichaCatalogo):
        indice = self._hash(clave)
        cubeta = self.arreglo[indice]

        # Verificar actualización
        for i, (k, nodo_existente) in enumerate(cubeta):
            if k == clave:
                nodo_existente.ficha = ficha
                self._mover_al_frente(nodo_existente)
                return

        # Si llegamos al límite, ejecutamos el desalojo antes de insertar
        if self.tamaño_actual >= self.capacidad:
            self._desalojar_lru()

        # Inserción de un nuevo elemento
        nuevo_nodo = NodoLRU(clave, ficha)
        cubeta.append((clave, nuevo_nodo))
        self._mover_al_frente(nuevo_nodo)
        self.tamaño_actual += 1

    def buscar(self, clave: str) -> FichaCatalogo | None:
        indice = self._hash(clave)
        cubeta = self.arreglo[indice]

        for k, nodo in cubeta:
            if k == clave:
                self._mover_al_frente(nodo)  # Actualizamos su posición de uso
                return nodo.ficha
        return None

    # --- CONTROL DE REFERENCIAS ---

    def modificar_referencia(self, clave: str, incremento: int):
        """Suma o resta al contador de uso. Si es > 0, el LRU no lo borra."""
        indice = self._hash(clave)
        for k, nodo in self.arreglo[indice]:
            if k == clave:
                nodo.referencias += incremento
                return