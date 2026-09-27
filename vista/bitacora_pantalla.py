"""
vista/bitacora_pantalla.py  —  PERSONA D  (§4.8)

Requisitos
  * La interfaz muestra SOLO los últimos 20 mensajes.
  * Memoria CONSTANTE durante toda la partida.
  * Agregar un mensaje NO debe desplazar físicamente los 19 anteriores.

Solución: BUFFER CIRCULAR. Un arreglo de tamaño fijo reservado UNA vez y un índice `_cabeza`
que apunta a la próxima posición de escritura. Agregar = escribir en `_cabeza` y avanzar el
índice (módulo capacidad): O(1) sin mover nada. El mensaje más viejo simplemente se
sobrescribe (y su memoria se libera).
"""


class BufferCircular:
    __slots__ = ("_datos", "_cabeza", "_cuenta", "_capacidad")

    def __init__(self, capacidad=20):
        if capacidad < 1:
            raise ValueError("la capacidad debe ser >= 1")
        self._capacidad = capacidad
        self._datos = [None] * capacidad      # se reserva una sola vez y nunca crece
        self._cabeza = 0                      # dónde se escribirá el próximo mensaje
        self._cuenta = 0                      # cuántos mensajes válidos hay (<= capacidad)

    def agregar(self, mensaje):
        """O(1): un solo acceso al arreglo y dos actualizaciones de índice."""
        self._datos[self._cabeza] = mensaje
        self._cabeza += 1
        if self._cabeza == self._capacidad:
            self._cabeza = 0
        if self._cuenta < self._capacidad:
            self._cuenta += 1

    def ultimos(self):
        """Mensajes del más antiguo al más reciente (los que se muestran en pantalla)."""
        inicio = (self._cabeza - self._cuenta) % self._capacidad
        return [self._datos[(inicio + i) % self._capacidad] for i in range(self._cuenta)]

    def vaciar(self):
        for i in range(self._capacidad):
            self._datos[i] = None
        self._cabeza = 0
        self._cuenta = 0

    @property
    def capacidad(self):
        return self._capacidad

    def __len__(self):
        return self._cuenta

    def __iter__(self):
        return iter(self.ultimos())