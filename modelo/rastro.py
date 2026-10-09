# modelo/rastro.py

RASTRO_FRESCURA_MAX = 400  # unidades de tiempo virtual (§2.9)


class RegistroRastro:
    """
    Guarda, por sala, el instante del reloj virtual en el que el jugador
    estuvo ahí por última vez (§2.9).

    Un valor por sala es suficiente. Se usa un arreglo indexado
    directamente por el id de sala (list, almacenamiento contiguo de bajo
    nivel permitido por §7) en vez de un dict, para que "¿hay rastro aquí?"
    sea O(1) y sin tabla de búsqueda.
    """

    def __init__(self, salas_total: int = 0):
        # +1 porque en el enunciado los ids de sala empiezan en 1
        self._tiempos = [None] * (salas_total + 1)

    def _asegurar_capacidad(self, sala_id: int):
        if sala_id >= len(self._tiempos):
            faltan = sala_id + 1 - len(self._tiempos)
            self._tiempos.extend([None] * faltan)

    def marcar_visita(self, sala_id: int, tiempo: int | None):
        self._asegurar_capacidad(sala_id)
        self._tiempos[sala_id] = tiempo

    def tiempo_de(self, sala_id: int):
        if sala_id < 0 or sala_id >= len(self._tiempos):
            return None
        return self._tiempos[sala_id]

    def es_fresco(self, tiempo_registrado, tiempo_actual: int) -> bool:
        if tiempo_registrado is None:
            return False
        return (tiempo_actual - tiempo_registrado) < RASTRO_FRESCURA_MAX

    def sala_mas_fresca(self, salas_vecinas_ids, tiempo_actual: int):
        """
        §2.9 — de una lista de ids de salas vecinas (ya filtradas a solo las
        conectadas por una salida abierta), devuelve el id de la sala con
        rastro más fresco, o None si ninguna califica.

        Empate -> menor id de sala. El costo es proporcional a la cantidad
        de vecinas recibidas (a lo sumo 4, una por dirección), nunca al
        tamaño de la cripta: quien llama debe pasar solo las salidas de la
        sala actual del rastreador, no el mapa completo (§4.7).
        """
        mejor_id = None
        mejor_tiempo = None
        for sala_id in salas_vecinas_ids:
            tiempo = self.tiempo_de(sala_id)
            if not self.es_fresco(tiempo, tiempo_actual):
                continue
            if (
                mejor_tiempo is None
                or tiempo > mejor_tiempo
                or (tiempo == mejor_tiempo and sala_id < mejor_id)
            ):
                mejor_id = sala_id
                mejor_tiempo = tiempo
        return mejor_id

    # --- adaptador hacia modelo/snapshots.py (SalaGuardada.rastro usa -1, no None) ---

    def exportar(self, sala_id: int) -> int:
        """Para SalaGuardada.rastro (§4.10): -1 si la sala nunca fue
        visitada, igual que ya lo define modelo/snapshots.py."""
        tiempo = self.tiempo_de(sala_id)
        return -1 if tiempo is None else tiempo

    def importar(self, sala_id: int, valor: int) -> None:
        """Inverso de exportar(): -1 vuelve a ser 'sin rastro'."""
        self.marcar_visita(sala_id, None if valor == -1 else valor)
