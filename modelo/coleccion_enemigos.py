class EnemigosSala(list):
    """Arreglo propio con extraccion O(1) por posicion guardada en el actor."""

    def __init__(self, enemigos=()):
        super().__init__()
        self.extend(enemigos)

    def append(self, enemigo):
        enemigo.indice_sala = len(self)
        super().append(enemigo)

    def extend(self, enemigos):
        for enemigo in enemigos:
            self.append(enemigo)

    def extraer(self, enemigo):
        indice = enemigo.indice_sala
        if not 0 <= indice < len(self) or self[indice] is not enemigo:
            raise ValueError("El enemigo no pertenece a esta sala.")
        ultimo = super().pop()
        if indice < len(self):
            self[indice] = ultimo
            ultimo.indice_sala = indice
        enemigo.indice_sala = -1
        return indice

    def restaurar(self, enemigo, indice):
        if indice == len(self):
            self.append(enemigo)
        else:
            desplazado = self[indice]
            self.append(desplazado)
            self[indice] = enemigo
            enemigo.indice_sala = indice
