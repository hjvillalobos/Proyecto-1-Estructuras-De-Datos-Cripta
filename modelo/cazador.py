"""Decisión del cazador para un turno, con un rango válido suministrado."""


def decidir_cazador(origen_indice, destino_indice, rango, consultar_ruta):
    """Devuelve (acción, dirección o None, costo base).

    La consulta T021 usa los índices del esqueleto completo, las puertas
    actuales y el rango como límite inclusivo. Devuelve None si no hay
    ruta admisible o (primer índice, dirección, costo del paso, costo total).
    """
    if origen_indice == destino_indice:
        return "atacar", None, 100

    ruta = consultar_ruta(origen_indice, destino_indice, rango)
    if ruta is None:
        return "esperar", None, 100

    _, direccion, costo_paso, _ = ruta
    return "mover", direccion, costo_paso
