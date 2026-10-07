# modelo/enemigos.py

import random

ACCION_ATACAR = "atacar"
ACCION_MOVER = "mover"
ACCION_ESPERAR = "esperar"

GUARDIAN = "guardian"
ERRANTE = "errante"
RASTREADOR = "rastreador"


def _salidas_abiertas(sala) -> list:
    """[(direccion, sala_destino_id), ...] para las salidas de `sala` que
    existen y no están cerradas. `sala.salidas` es el dict del esqueleto
    (§3.3): {"N": {"sala": 2, "cerrada": True, ...}, ...}."""
    resultado = []
    for direccion, salida in sala.salidas.items():
        if not salida.get("cerrada", False):
            resultado.append((direccion, salida["sala"]))
    return resultado


def decidir_accion(enemigo, sala_actual, jugador_en_sala: bool, registro_rastro, azar: random.Random, tiempo_actual: int):
    """
    §2.8 — decide la acción de un enemigo cuando le toca actuar.

    - enemigo: InstanciaEnemigo (usa su campo `comportamiento`:
      "guardian" | "errante" | "rastreador").
    - sala_actual: objeto Sala en la que está el enemigo. Se pasa
      explícito porque InstanciaEnemigo no trae hoy su propia ubicación en
      el contrato compartido; quien invoca (el motor de Persona A) es
      quien sabe en qué sala está cada enemigo.
    - jugador_en_sala: True si el jugador comparte sala con el enemigo.
    - registro_rastro: instancia de modelo.rastro.RegistroRastro.
    - azar: random.Random(semilla) del modelo — nunca el módulo random
      global (§2.6).
    - tiempo_actual: reloj virtual en el instante de esta decisión.

    Devuelve (accion, dato):
      (ACCION_ATACAR, None)
      (ACCION_MOVER, direccion)
      (ACCION_ESPERAR, None)
    """
    if jugador_en_sala:
        return (ACCION_ATACAR, None)

    if enemigo.comportamiento == GUARDIAN:
        return (ACCION_ESPERAR, None)

    salidas = _salidas_abiertas(sala_actual)
    if not salidas:
        return (ACCION_ESPERAR, None)

    if enemigo.comportamiento == ERRANTE:
        indice = azar.randint(0, len(salidas) - 1)
        direccion, _destino = salidas[indice]
        return (ACCION_MOVER, direccion)

    if enemigo.comportamiento == RASTREADOR:
        ids_vecinos = [destino for _direccion, destino in salidas]
        mejor_id = registro_rastro.sala_mas_fresca(ids_vecinos, tiempo_actual)
        if mejor_id is None:
            return (ACCION_ESPERAR, None)
        for direccion, destino in salidas:
            if destino == mejor_id:
                return (ACCION_MOVER, direccion)
        return (ACCION_ESPERAR, None)  # inalcanzable en la práctica

    # Comportamiento no reconocido: por seguridad, esperar en vez de fallar.
    return (ACCION_ESPERAR, None)
