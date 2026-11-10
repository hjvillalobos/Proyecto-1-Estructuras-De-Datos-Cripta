from datos.offline import ClienteOffline
from modelo.resolubilidad import (DatosVerificacion, ResultadoVerificacion, SalaVerificacion,
                                  SalidaVerificacion, UbicacionLlave, normalizar,
                                  verificar_resolubilidad)
from red.errores import DatosInvalidos, DatosNoDisponibles, ErrorCripta, VersionIncompatible
from red.precarga import validar_generales, validar_pagina_esqueleto
from red.validacion import identificador, validar_llaves


def _version(cliente, cripta_id):
    respuesta = cliente.obtener_version_cripta(cripta_id)
    if not isinstance(respuesta, dict) or respuesta.get('id') != cripta_id:
        raise DatosInvalidos('La versión no corresponde a la cripta solicitada.')
    return identificador(respuesta.get('version'))


def _convertir(generales, paginas, llaves):
    salas = []
    for numero, pagina in enumerate(paginas, 1):
        for sala in validar_pagina_esqueleto(pagina, numero, generales['paginas']):
            salidas = [SalidaVerificacion(sala.id, direccion, salida['sala'],
                                          salida.get('cerrada'), salida.get('llave'))
                       for direccion, salida in sala.salidas.items()]
            salas.append(SalaVerificacion(sala.id, salidas))
    if len(salas) != generales['salas_total']:
        raise DatosInvalidos('El total de salas no coincide con los metadatos.')
    validar_llaves(llaves)
    ubicaciones = [UbicacionLlave(u['id'], u['sala'], u.get('enemigo')) for u in llaves['llaves']]
    datos = DatosVerificacion(generales['id'], generales['version'], generales['sala_inicial'],
                              generales['sala_salida'], generales['llave_salida'], salas, ubicaciones)
    normalizar(datos)
    return datos


def preparar_verificacion(cliente, almacen, cripta_id, version_cripta=None):
    identificador(cripta_id)
    offline = isinstance(cliente, ClienteOffline)
    solo_local = offline and cliente.almacen.carpeta.resolve() == almacen.carpeta.resolve()
    if version_cripta is None and offline:
        version_cripta = cliente.version_cripta
    if version_cripta is not None:
        identificador(version_cripta)
    generales = almacen.leer_generales(cripta_id, version_cripta)
    version_red = None
    nuevo = generales is None
    if generales is not None:
        validar_generales(generales, cripta_id)
        if version_cripta is not None and generales['version'] != version_cripta:
            raise VersionIncompatible('Los metadatos locales tienen otra versión.')
        cliente.configurar_presupuesto(generales['presupuesto_solicitudes'])
        if not solo_local and version_cripta is None:
            version_red = _version(cliente, cripta_id)
            if version_red != generales['version']:
                generales = None
                nuevo = True
    if generales is None:
        if solo_local:
            raise DatosNoDisponibles(f'Faltan metadatos locales de {cripta_id}, versión {version_cripta or "actual"}.')
        generales = cliente.obtener_datos_generales(cripta_id)
        validar_generales(generales, cripta_id)
        cliente.configurar_presupuesto(generales['presupuesto_solicitudes'])
    version = generales['version']
    if version_cripta is not None and version != version_cripta:
        raise VersionIncompatible('La versión solicitada no está disponible.')

    def confirmar_red():
        nonlocal version_red
        if solo_local:
            raise DatosNoDisponibles(f'Faltan datos locales de {cripta_id}, versión {version}.')
        if version_red is None:
            version_red = _version(cliente, cripta_id)
        if version_red != version:
            raise VersionIncompatible('No se pueden mezclar versiones de cripta.')

    if nuevo:
        confirmar_red()
    paginas = []
    nuevas = []
    for numero in range(1, generales['paginas'] + 1):
        pagina = almacen.leer_pagina(cripta_id, version, numero)
        if pagina is None:
            confirmar_red()
            pagina = cliente.obtener_esqueleto(cripta_id, numero)
            nuevas.append(pagina)
        paginas.append(pagina)
    llaves = almacen.leer_llaves(cripta_id, version)
    nuevas_llaves = llaves is None
    if nuevas_llaves:
        confirmar_red()
        llaves = cliente.obtener_llaves(cripta_id)
    datos = _convertir(generales, paginas, llaves)
    if nuevo or nuevas or nuevas_llaves:
        if _version(cliente, cripta_id) != version:
            raise VersionIncompatible('La cripta cambió durante la adquisición; se descartó el lote.')
        for pagina in nuevas:
            almacen.guardar_pagina(cripta_id, version, pagina)
        if nuevas_llaves:
            almacen.guardar_llaves(cripta_id, version, llaves)
        if nuevo:
            almacen.guardar_generales(generales)
    return datos


def verificar_cripta(cliente, almacen, cripta_id, version_cripta=None):
    try:
        datos = preparar_verificacion(cliente, almacen, cripta_id, version_cripta)
        return verificar_resolubilidad(datos)
    except ErrorCripta as error:
        return ResultadoVerificacion('no_completada', cripta_id, causa=str(error))
