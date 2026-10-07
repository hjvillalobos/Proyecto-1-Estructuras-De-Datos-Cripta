def reproducir(ruta, fuente, fabrica_juego, notificar=print):
    """
    Reproduce una partida sin pedir input al usuario.

    fuente:
        implementación de Persona B.

    fabrica_juego:
        modelo.juego.crear_juego cuando Persona A la implemente.
    """

    bitacora = BitacoraReplay(ruta)

    meta, acciones = bitacora.leer()

    # -------------------------------------------------
    # Validar versiones
    # -------------------------------------------------

    version_cripta_actual = fuente.version_cripta(
        meta.cripta_id
    )

    version_catalogo_actual = fuente.version_catalogo()

    versiones_iguales = (
        version_cripta_actual == meta.cripta_version
        and
        version_catalogo_actual == meta.catalogo_version
    )

    if not versiones_iguales:

        # B puede ofrecer una copia local compatible.
        tiene_copia = False

        if hasattr(fuente, "tiene_copia_local"):
            tiene_copia = fuente.tiene_copia_local(
                meta.cripta_id,
                meta.cripta_version,
                meta.catalogo_version,
            )

        if not tiene_copia:
            raise ReplayIncompatible(
                "Las versiones actuales no coinciden con las del replay. "
                "No se puede garantizar una reproducción fiel."
            )

    # -------------------------------------------------
    # Crear partida con LA MISMA SEMILLA
    # -------------------------------------------------

    juego = fabrica_juego(
        fuente,
        meta.cripta_id,
        meta.semilla,
        notificar,
    )

    # -------------------------------------------------
    # Ejecutar exactamente las acciones registradas
    # -------------------------------------------------

    for numero, registro in enumerate(acciones, start=1):

        resultado = juego.ejecutar(
            registro.accion,
            registro.argumento,
        )

        if not resultado.ok:
            raise ReplayCorrupto(
                f"El replay falló en la acción {numero}: "
                f"{registro.accion} {registro.argumento}. "
                f"{resultado.mensaje}"
            )

    return juego