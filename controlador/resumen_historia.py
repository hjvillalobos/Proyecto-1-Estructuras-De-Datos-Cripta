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


def detallar_partida(consulta, modelo):
    """Completar nombres estáticos con datos residentes, nunca con valores vivos."""
    precarga = getattr(modelo, 'gestor_precarga', None)
    catalogo = getattr(precarga, 'catalogo', None)
    resolver = getattr(catalogo, 'ficha_preparada', None)
    proyectar = getattr(modelo, 'mapa_historico', None)
    mapa = proyectar(consulta.estado) if callable(proyectar) else ()
    return detallar(consulta, resolver_ficha=resolver, mapa=mapa)


def detallar(consulta, *, resolver_ficha=None, mapa=()):
    from modelo.conocimiento import AVISTADA, EXPLORADA
    from red.errores import DatosNoDisponibles

    def ficha(tipo):
        if callable(resolver_ficha):
            try:
                return resolver_ficha(tipo)
            except DatosNoDisponibles:
                pass
        return None

    estado = consulta.estado
    sala, nombre = estado.obtener('sala')
    vida, maxima, ataque, defensa, velocidad = estado.obtener('jugador')
    try:
        derrotados, resultado = estado.obtener('estadisticas_partida')
        resultado = resultado or 'jugando'
    except KeyError:
        derrotados = resultado = 'no registrado'
    acciones = getattr(consulta, 'acciones', None)
    lineas = [f'Historia — reloj {consulta.reloj} · acciones {acciones if acciones is not None else "no registradas"}',
              f'Resultado: {resultado}', f'Sala del jugador: {sala} · {nombre}',
              f'Vida: {vida}/{maxima} · ataque: {ataque} · defensa: {defensa} · velocidad: {velocidad}',
              f'Enemigos derrotados: {derrotados}', '', 'Inventario (orden histórico):']
    inventario = inventario_historico(estado)
    antorcha = False
    if inventario is not None:
        _, cantidad, actual, _, cursor, arma, armadura = estado.obtener('inventario_estado')
        for numero in range(1, cantidad + 1):
            tipo, _, _, encendida, _, siguiente = estado.obtener('inventario_nodo:' + actual)
            datos = ficha(tipo)
            descripcion = f'{datos.nombre if datos else tipo} [{tipo}] · instancia: {actual}'
            if datos:
                descripcion += f' · {datos.clase}'
                if 'usos' in datos.atributos:
                    descripcion += f' · usos: {datos.atributos["usos"]}'
            if actual in (arma, armadura):
                descripcion += ' · equipado'
            if actual == cursor:
                descripcion += ' · seleccionado'
            if encendida:
                descripcion += ' · encendida'
                antorcha = True
            lineas.append(f'  {numero}) {descripcion}')
            actual = siguiente
        if not cantidad:
            lineas.append('  Vacío.')
    else:
        anteriores = [valor for clave, valor in estado.campos() if clave.startswith('inventario:')]
        for numero, (instancia, tipo, equipado) in enumerate(anteriores, 1):
            datos = ficha(tipo)
            lineas.append(f'  {numero}) {datos.nombre if datos else tipo} [{instancia}]' +
                          (' · equipado' if equipado else ''))
        if not anteriores:
            lineas.append('  Vacío.')
    efectos = list(estado.obtener('efectos'))
    if antorcha and not any('antorcha' in e.lower() for e in efectos):
        efectos.append('antorcha encendida')
    lineas += ['', f'Efectos activos: {", ".join(efectos) or "ninguno"}', '', 'Enemigos de la sala:']
    enemigos = [(clave.removeprefix('enemigo:'), valor) for clave, valor in estado.campos()
                if clave.startswith('enemigo:') and valor[1] > 0]
    for instancia, (tipo, actual, total, comportamiento) in enemigos:
        datos = ficha(tipo)
        lineas.append(f'  {datos.nombre if datos else tipo} [{instancia}] · vida: {actual}/{total} · {comportamiento}')
    if not enemigos:
        lineas.append('  Ninguno vivo.')
    lineas.append('')
    if mapa:
        exploradas = sum(nivel == EXPLORADA for _, nivel, _, _ in mapa)
        avistadas = sum(nivel == AVISTADA for _, nivel, _, _ in mapa)
        lineas.append(f'Mapa conocido: {exploradas} salas exploradas · {avistadas} salas avistadas (sin explorar)')
        for identidad, nivel, nombre, salidas in mapa:
            if nivel == AVISTADA:
                lineas.append(f'Sala {identidad}: avistada (sin explorar)')
                continue
            lineas.append(f'Sala {identidad}: {nombre} (explorada)')
            for direccion, destino, costo, puerta, recuerdo in salidas:
                acceso = 'sin puerta' if puerta is None else ('sin observar' if recuerdo is None else
                                                             'cerrada' if recuerdo else 'abierta')
                lineas.append(f'  {direccion} → sala {destino} (costo {costo}, {acceso}' +
                              ('; último recuerdo)' if puerta is not None else ')'))
    else:
        lineas.append('Mapa conocido:')
        lineas.extend('  ' + linea for linea in mapa_historico(estado))
        if lineas[-1] == 'Mapa conocido:':
            lineas.append('  Sin detalle registrado.')
    return '\n'.join(lineas)
