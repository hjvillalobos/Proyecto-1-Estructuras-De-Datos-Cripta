from modelo.conocimiento import AVISTADA, EXPLORADA
from modelo.errores_historia import CambioHistoriaIncoherente


def lineas_mapa(proyeccion):
    lineas = []
    for registro in proyeccion:
        if isinstance(registro, str):
            lineas.append(registro)
            continue
        identificador, estado, nombre, salidas = registro
        if estado == AVISTADA:
            lineas.append(f"Sala {identificador}: avistada")
        elif estado == EXPLORADA:
            lineas.append(f"Sala {identificador} · {nombre}: explorada")
            for direccion, destino, costo, puerta, recuerdo in salidas:
                detalle = ""
                if puerta is not None:
                    memoria = "sin observar" if recuerdo is None else ("cerrada" if recuerdo else "abierta")
                    detalle = f" | puerta {puerta}: {memoria} (recuerdo)"
                lineas.append(f"  {direccion} → sala {destino} | costo {costo}{detalle}")
    return lineas


def inventario_historico(estado):
    try:
        meta = estado.obtener("inventario_estado")
    except KeyError:
        return None
    _, cantidad, primero, ultimo, cursor, arma, armadura = meta
    resultado = []
    actual, previo = primero, None
    try:
        for _ in range(cantidad):
            if actual is None:
                raise CambioHistoriaIncoherente("El inventario histórico termina antes de su tamaño.")
            tipo, _, _, _, anterior, siguiente = estado.obtener("inventario_nodo:" + actual)
            if anterior != previo:
                raise CambioHistoriaIncoherente("Los enlaces del inventario histórico no coinciden.")
            detalle = " (equipado)" if actual in (arma, armadura) else ""
            detalle += " (cursor)" if actual == cursor else ""
            resultado.append(f"{tipo} [{actual}]{detalle}")
            previo, actual = actual, siguiente
    except KeyError as error:
        raise CambioHistoriaIncoherente("Falta un nodo del inventario histórico.") from error
    if actual is not None or previo != ultimo:
        raise CambioHistoriaIncoherente("La frontera del inventario histórico no coincide.")
    return resultado


def mapa_historico(estado):
    lineas = []
    for clave, valor in estado.campos():
        if clave.startswith("conocimiento:sala:"):
            identificador = clave.removeprefix("conocimiento:sala:")
            if valor == AVISTADA:
                lineas.append(f"Sala {identificador}: avistada")
            elif valor == EXPLORADA:
                lineas.append(f"Sala {identificador}: explorada")
        elif clave.startswith("conocimiento:puerta:"):
            identificador = clave.removeprefix("conocimiento:puerta:")
            lineas.append(f"Puerta {identificador}: {'cerrada' if valor else 'abierta'} (recuerdo)")
    return lineas
