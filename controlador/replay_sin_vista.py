"""Reproduce el log sin importar ni instanciar componentes de vista."""
from controlador.resumen_historia import resumir
from datos.bitacora_replay import BitacoraReplay, ReplayCorrupto, ReplayIncompatible, aplicar_accion_replay
from controlador.partida_historica import integrar_historia


def reproducir(ruta, precarga, fabrica, checkpoint_cada, hasta=None):
    meta, acciones = BitacoraReplay(ruta).leer()
    juego = fabrica(precarga, meta.cripta_id, meta.semilla,
                    version_cripta=meta.version_cripta, version_catalogo=meta.version_catalogo)
    if (juego.meta.cripta_id, juego.meta.cripta_version, juego.meta.catalogo_version) != (
            meta.cripta_id, meta.version_cripta, meta.version_catalogo):
        raise ReplayIncompatible("Las versiones cargadas no coinciden con el replay.")
    juego = integrar_historia(juego, checkpoint_cada)
    if hasta is not None and getattr(juego, "linea_tiempo", None) is None:
        raise ReplayIncompatible("El motor todavía no entrega cambios para reconstruir la historia.")

    # Una carga o un pergamino posterior puede reemplazar el pasado.
    # Usar un objeto podría ser un pergamino; el log solo guarda su ID.
    ultima_revision = max((i for i, accion in enumerate(acciones, 1)
                           if accion.accion in ("cargar", "retroceso", "usar")), default=0)
    for numero, accion in enumerate(acciones, 1):
        if hasta is not None and numero > ultima_revision and juego.linea_tiempo.reloj >= hasta:
            break
        if (accion.accion == "cargar" and "historia" in accion.argumento
                and getattr(juego, "linea_tiempo", None) is None):
            raise ReplayIncompatible("El motor todavía no admite cargas con historia de Parte II.")
        resultado = aplicar_accion_replay(juego, accion)
        if not resultado.ok:
            raise ReplayCorrupto(f"Acción inválida en el paso {numero}: {resultado.mensaje}")
    historia = getattr(juego, "linea_tiempo", None)
    if historia is None:
        resumen = juego.resumen()
        return f"Replay t={resumen.reloj_final} | acciones: {resumen.acciones} | " + (
            resumen.resultado or "partida en curso")
    if hasta is None:
        return resumir(historia.consultar_final())
    if hasta > historia.reloj:
        return f"El replay terminó antes de t={hasta}.\n{resumir(historia.consultar_final())}"
    return resumir(historia.consultar_t(hasta))
