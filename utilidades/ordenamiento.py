"""


Los dos algoritmos
  1) INSERCIÓN  : O(n) si los datos están (casi) ordenados, O(n²) si están desordenados.
                  Casi sin sobrecarga -> gana en listas pequeñas. Estable, en el mismo lugar.
  2) FUSIÓN     : (merge sort ascendente, iterativo) siempre O(n log n), pocas comparaciones.
                  Necesita un arreglo auxiliar de n elementos. Estable.

"""
from dataclasses import dataclass

# Umbrales (calibrados con --bench, ver docstring) 
UMBRAL_PEQUENO = 16            # n <= esto -> inserción (comparaciones baratas)
UMBRAL_PEQUENO_COSTOSO = 8     # n <= esto -> inserción (comparaciones costosas)
DESORDEN_BAJO = 0.15           # <= esto se considera "casi ordenado"
MUESTRA_MAX = 256              # máximo de pares vecinos revisados al medir el desorden
FACTOR_PRESUPUESTO = 8         # la inserción puede hacer hasta 8*n desplazamientos

INSERCION = "insercion"
FUSION = "fusion"


@dataclass
class InfoOrden:
    """Qué pasó dentro de ordenar(); lo usa --bench y el Documento de Decisiones."""
    n: int
    algoritmo: str                  # el que TERMINÓ el trabajo
    desorden: float | None          # None si no hizo falta medirlo
    abortado_por_presupuesto: bool = False


# Todo el módulo compara con UNA sola función, así ascendente/descendente comparten código
# y la estabilidad se mantiene también en descendente (a diferencia de invertir el resultado).
def _asc(a, b):
    return a < b


def _desc(a, b):
    return b < a

# Algoritmo 1: INSERCIÓN
# Trabaja sobre una lista de pares (clave, elemento). Solo mira la clave (par[0]).
def _insercion(pares, antes, presupuesto=None):
    """Ordena `pares` en el lugar. Devuelve True si terminó, False si abortó por presupuesto.

    Invariante: al empezar la vuelta i, pares[0:i] ya está ordenado. Si se aborta, se hace
    ENTRE vueltas, así que la lista queda consistente (prefijo ordenado + resto intacto)."""
    desplazamientos = 0
    for i in range(1, len(pares)):
        if presupuesto is not None and desplazamientos > presupuesto:
            return False
        actual = pares[i]
        clave = actual[0]
        j = i - 1

        # Se mueve hacia la derecha todo lo que deba ir DESPUÉS de `actual`.
        # Usar "antes(clave, previo)" estricto mantiene la estabilidad (iguales no se cruzan).
        while j >= 0 and antes(clave, pares[j][0]):
            pares[j + 1] = pares[j]
            j -= 1
            desplazamientos += 1
        pares[j + 1] = actual
    return True


# ============================================================================================
# Algoritmo 2: FUSIÓN iterativa (bottom-up)
# ============================================================================================
def _fusion(pares, antes):
    """Merge sort iterativo. Ancho 1, 2, 4, ... fusionando bloques vecinos, alternando
    entre `pares` y un arreglo auxiliar (no se copia en cada pasada)."""
    n = len(pares)
    if n < 2:
        return
    origen = pares
    destino = [None] * n
    ancho = 1
    while ancho < n:
        for inicio in range(0, n, 2 * ancho):
            medio = min(inicio + ancho, n)
            fin = min(inicio + 2 * ancho, n)
            _fusionar(origen, destino, inicio, medio, fin, antes)
        origen, destino = destino, origen
        ancho *= 2
    if origen is not pares:          # el resultado quedó en el auxiliar: se copia una vez
        pares[:] = origen


def _fusionar(origen, destino, inicio, medio, fin, antes):
    """Mezcla origen[inicio:medio] y origen[medio:fin] (ya ordenados) en destino."""
    i, j, k = inicio, medio, inicio
    while i < medio and j < fin:
        # Solo se toma de la derecha si es ESTRICTAMENTE anterior -> estable.
        if antes(origen[j][0], origen[i][0]):
            destino[k] = origen[j]
            j += 1
        else:
            destino[k] = origen[i]
            i += 1
        k += 1
    while i < medio:
        destino[k] = origen[i]
        i += 1
        k += 1
    while j < fin:
        destino[k] = origen[j]
        j += 1
        k += 1


# Medición de propiedades y decisión automática
def medir_desorden(pares, antes=_asc):
    """Fracción de descensos entre vecinos, estimada con a lo sumo MUESTRA_MAX pares
    equiespaciados (determinista: no usa azar). Costo: O(min(n, MUESTRA_MAX)) comparaciones."""
    total = len(pares) - 1
    if total < 1:
        return 0.0
    paso = 1 if total <= MUESTRA_MAX else total // MUESTRA_MAX
    revisados = descensos = 0
    i = 0
    while i < total:
        revisados += 1
        if antes(pares[i + 1][0], pares[i][0]):
            descensos += 1
        i += paso
    return descensos / revisados


def elegir_algoritmo(n, desorden, comparacion_costosa=False):
    """Regla de decisión (pura, para poder probarla y citarla en el documento)."""
    umbral = UMBRAL_PEQUENO_COSTOSO if comparacion_costosa else UMBRAL_PEQUENO
    if n <= umbral:
        return INSERCION          # lista pequeña: la sobrecarga de fusión no se paga
    if desorden is not None and desorden <= DESORDEN_BAJO:
        return INSERCION          # casi ordenada: ~O(n) (protegida por presupuesto)
    return FUSION                 # caso general: cota O(n log n) garantizada


# API pública
def ordenar_con_info(datos, clave=None, descendente=False,
                     comparacion_costosa=False, algoritmo=None):
    """Devuelve (lista_nueva_ordenada, InfoOrden). NO modifica `datos` (las vistas del
    inventario deben dejar intacto el orden real, §4.5).

    clave       : función elemento -> valor comparable con "<". Se evalúa UNA vez por elemento.
    descendente : orden inverso, manteniendo la estabilidad.
    algoritmo   : None = automático; INSERCION o FUSION fuerzan uno (para --bench).
    """
    n = len(datos)
    pares = [((clave(x) if clave is not None else x), x) for x in datos]
    antes = _desc if descendente else _asc

    desorden = None
    abortado = False

    if algoritmo == INSERCION:
        _insercion(pares, antes)
        usado = INSERCION
    elif algoritmo == FUSION:
        _fusion(pares, antes)
        usado = FUSION
    elif algoritmo is None:
        umbral = UMBRAL_PEQUENO_COSTOSO if comparacion_costosa else UMBRAL_PEQUENO
        if n > umbral:
            desorden = medir_desorden(pares, antes)   # solo se mide si la decisión lo necesita
        elegido = elegir_algoritmo(n, desorden, comparacion_costosa)
        if elegido == INSERCION:
            # En listas pequeñas no hace falta presupuesto (el peor caso es diminuto).
            presupuesto = FACTOR_PRESUPUESTO * n if n > umbral else None
            terminado = _insercion(pares, antes, presupuesto)
            usado = INSERCION
            if not terminado:
                abortado = True
                _fusion(pares, antes)         # el prefijo ordenado ayuda poco, pero es correcto
                usado = FUSION
        else:
            _fusion(pares, antes)
            usado = FUSION
    else:
        raise ValueError(f"algoritmo desconocido: {algoritmo!r}")

    resultado = [p[1] for p in pares]
    return resultado, InfoOrden(n, usado, desorden, abortado)


def ordenar(datos, clave=None, descendente=False, comparacion_costosa=False, algoritmo=None):
    """Igual que ordenar_con_info pero devuelve solo la lista ordenada."""
    return ordenar_con_info(datos, clave, descendente, comparacion_costosa, algoritmo)[0]