from red.errores import DatosInvalidos


def unicos(valores):
    resultado = []
    for valor in valores:
        if valor not in resultado:
            resultado.append(valor)
    return resultado


def texto(valor):
    if not isinstance(valor, str) or not valor.strip():
        raise DatosInvalidos("Se esperaba texto no vacío.")
    return valor


def identificador(valor):
    texto(valor)
    if "," in valor:
        raise DatosInvalidos("El identificador debe ser texto no vacío y sin comas.")
    return valor


def entero(valor, minimo=0):
    if type(valor) is not int or (minimo is not None and valor < minimo):
        raise DatosInvalidos(f"Se esperaba un entero mayor o igual que {minimo}.")
    return valor


def lote(valores, salas=False):
    valores = list(valores)
    for valor in valores:
        entero(valor, None) if salas else identificador(valor)
    valores = unicos(valores)
    if not 1 <= len(valores) <= 10:
        raise DatosInvalidos("Cada consulta debe contener entre 1 y 10 IDs distintos.")
    return valores


def registros(respuesta, campo, clave, esperados):
    if not isinstance(respuesta, dict) or not isinstance(respuesta.get(campo), list):
        raise DatosInvalidos(f"La respuesta debe contener la lista {campo}.")
    filas = respuesta[campo]
    ids = []
    for fila in filas:
        if not isinstance(fila, dict) or clave not in fila:
            raise DatosInvalidos(f"Registro inválido en {campo}.")
        if fila[clave] in ids or fila[clave] not in esperados:
            raise DatosInvalidos(f"ID duplicado o inesperado en {campo}: {fila[clave]}")
        ids.append(fila[clave])
    if len(ids) != len(esperados):
        raise DatosInvalidos(f"Faltan registros solicitados en {campo}.")
    return [next(fila for fila in filas if fila[clave] == valor) for valor in esperados]
