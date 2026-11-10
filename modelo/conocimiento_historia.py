"""Conversión local de C al contrato histórico de D (FR-019).

No registra acciones ni muta el mapa. Los nombres de campos son propuesta de
C; no reemplazan la proyección de texto mapa:<id> de la interfaz de D.
Requiere los tipos de historia reales al llamar convertir_cambios.
"""
from modelo.conocimiento import CambioConocimiento, ConocimientoMapa
from utilidades.ordenamiento import ordenar


def _clave(ambito, identificador):
    if ambito not in ('sala', 'puerta') or type(identificador) is not int or identificador < 0:
        raise ValueError('Ámbito o identificador de conocimiento inválido.')
    return f'conocimiento:{ambito}:{identificador}'


def _presente(ambito, valor):
    if ambito == 'sala':
        if type(valor) is not int or valor not in (0, 1, 2):
            raise ValueError('Estado de sala inválido.')
        return valor != 0
    if valor is not None and type(valor) is not bool:
        raise ValueError('Recuerdo de puerta inválido.')
    return valor is not None


def campos_iniciales(mapa):
    """Base única para iniciar historia; no llamar después de cada acción."""
    if type(mapa) is not ConocimientoMapa:
        raise ValueError('Se requiere ConocimientoMapa.')
    campos, puertas = [], []
    for identificador, estado, _, salidas in mapa.mapa_conocido():
        campos.append((_clave('sala', identificador), estado))
        for _, _, _, puerta, recuerdo in salidas:
            if puerta is not None and recuerdo is not None:
                puertas.append((puerta, recuerdo))
    puertas = ordenar(puertas, clave=lambda p: p[0], algoritmo='fusion')
    anterior = None
    for identificador, recuerdo in puertas:
        if identificador != anterior:
            campos.append((_clave('puerta', identificador), recuerdo))
            anterior = identificador
    return tuple(campos)


def convertir_cambios(cambios):
    """O(D): conserva orden y presencia; no busca ni copia el mapa completo."""
    from modelo.snapshots import CambioHistorico, ValorHistorico

    if type(cambios) is not tuple:
        raise ValueError('Se requiere una tupla de cambios de conocimiento.')
    resultado = []
    for cambio in cambios:
        if type(cambio) is not CambioConocimiento:
            raise ValueError('Se requiere CambioConocimiento.')
        clave = _clave(cambio.ambito, cambio.id)
        anterior_presente = _presente(cambio.ambito, cambio.anterior)
        nuevo_presente = _presente(cambio.ambito, cambio.nuevo)
        resultado.append(CambioHistorico(
            clave,
            ValorHistorico(anterior_presente, cambio.anterior if anterior_presente else None),
            ValorHistorico(nuevo_presente, cambio.nuevo if nuevo_presente else None)))
    return tuple(resultado)
