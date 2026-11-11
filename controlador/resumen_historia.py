"""Presentación común de historia, independiente de la vista."""
from modelo.errores_historia import EntradaHistoriaInvalida
from controlador.presentacion_conocimiento import inventario_historico, mapa_historico


def consultar(historia, texto):
    if texto.startswith("#"):
        if not texto[1:].isascii() or not texto[1:].isdigit():
            raise EntradaHistoriaInvalida("Uso: historia <t> o historia #<acción>.")
        try:
            numero = int(texto[1:])
        except ValueError as error:
            raise EntradaHistoriaInvalida("Número de acción inválido.") from error
        return historia.consultar_accion(numero)
    if not texto.isascii() or not texto.isdigit():
        raise EntradaHistoriaInvalida("Uso: historia <t> o historia #<acción>.")
    try:
        tiempo = int(texto)
    except ValueError as error:
        raise EntradaHistoriaInvalida("Instante inválido.") from error
    return historia.consultar_t(tiempo)


def resumir(consulta):
    estado = consulta.estado
    sala, nombre = estado.obtener("sala")
    vida, maxima, ataque, defensa, velocidad = estado.obtener("jugador")
    inventario, enemigos, mapa = [], [], []
    for clave, valor in estado.campos():
        if clave.startswith("inventario:"):
            instancia, tipo, equipado = valor
            inventario.append(f"{tipo} [{instancia}]" + (" (equipado)" if equipado else ""))
        elif clave.startswith("enemigo:"):
            tipo, actual, total, comportamiento = valor
            instancia = clave.removeprefix("enemigo:")
            detalle = f" ({comportamiento})" if comportamiento else ""
            enemigos.append(f"{tipo} [{instancia}] {actual}/{total}{detalle}")
        elif clave.startswith("mapa:"):
            mapa.append(str(valor))
    inventario_c = inventario_historico(estado)
    if inventario_c is not None:
        inventario = inventario_c
    mapa_c = mapa_historico(estado)
    if mapa_c:
        mapa = mapa_c
    try:
        mapa_disponible = estado.obtener("conocimiento")
    except KeyError:
        mapa_disponible = bool(mapa_c)
    efectos = estado.obtener("efectos")
    lineas = [
        f"Historia t={consulta.reloj} | Sala {sala} · {nombre}",
        f"Vida {vida}/{maxima} | Ataque {ataque} | Defensa {defensa} | Velocidad {velocidad}",
        f"Inventario: {', '.join(inventario) or 'vacío'}",
        f"Efectos: {', '.join(efectos) or 'ninguno'}",
        f"Enemigos: {', '.join(enemigos) or 'ninguno'}",
        "Mapa conocido: " + (", ".join(mapa) or ("vacío" if mapa_disponible else "no disponible")),
    ]
    return "\n".join(lineas)
