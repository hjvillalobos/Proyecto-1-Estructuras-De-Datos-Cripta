"""Adaptación del reporte de B a los modos de D."""
from dataclasses import dataclass


@dataclass(frozen=True)
class VerificacionNoDisponible:
    cripta_id: str
    estado: str = "no_completada"
    causa: str = "El módulo de verificación de resolubilidad todavía no está disponible en esta rama."
    limitacion: str = "Verificación por alcanzabilidad acumulada; no garantiza una trayectoria única si hay salidas sin regreso."


def verificar(sesion, cripta_id, version=None):
    try:
        from red.verificacion import verificar_cripta
    except ModuleNotFoundError as error:
        if error.name != "red.verificacion":
            raise
        return VerificacionNoDisponible(cripta_id)
    almacen = sesion.cliente.almacen if sesion.args.offline is not None else sesion.almacen
    return verificar_cripta(sesion.cliente, almacen, cripta_id, version)


def permite_inicio(reporte, forzar=False):
    return reporte.estado == "resoluble" or (forzar and reporte.estado == "no_resoluble")


def _condicion(condicion):
    return f"{condicion.tipo} {condicion.identificador}"


def texto_reporte(reporte):
    texto = [f"Verificación de {reporte.cripta_id}: {reporte.estado.replace('_', ' ')}"]
    texto.append(reporte.limitacion)
    if reporte.estado == "no_completada":
        return "\n".join((*texto, reporte.causa))
    if reporte.estado == "resoluble":
        texto.append("Orden de llaves: " + (" → ".join(reporte.orden_llaves) or "(ninguna)"))
    else:
        for llave in reporte.llaves_inalcanzables:
            ubicaciones = ", ".join(f"sala {u.sala}" + (f", enemigo {u.enemigo}" if u.enemigo else "")
                                    for u in llave.ubicaciones)
            texto.append(f"Llave inaccesible {llave.id}: {ubicaciones or 'sin ubicación registrada'}")
        for puerta in reporte.frontera:
            texto.append(f"Puerta {puerta.origen} {puerta.direccion} → {puerta.destino}: {puerta.llave}")
        for ciclo in reporte.ciclos:
            testigo = " → ".join(_condicion(reporte.evidencia[i]) for i in ciclo.testigo)
            integrantes = ", ".join(_condicion(reporte.evidencia[i]) for i in ciclo.integrantes)
            texto.append(f"Ciclo ({ciclo.clasificacion.replace('_', ' ')}): {testigo}")
            texto.append(f"  Integrantes: {integrantes}")
            for origen, destino in ciclo.bloqueos_externos:
                texto.append(f"  Dependencia externa: {_condicion(reporte.evidencia[origen])}"
                             f" → {_condicion(reporte.evidencia[destino])}")
    return "\n".join(texto)
