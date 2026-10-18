"""Auditoria reproducible: python -m tests.medir_rendimiento --paquete .cache/cripta.

Mide las rutas funcionales completas y su replay. No accede a HTTP ni afirma
que una ruta de prueba cubra cualquier contenido posible del profesor.
"""
import argparse
import json
import os
import platform
from pathlib import Path
from time import perf_counter
import unittest
from unittest.mock import patch

from modelo.juego import Motor, crear_juego


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paquete", required=True)
    parser.add_argument("--salida", default=".cache/rendimiento.json")
    args = parser.parse_args()
    os.environ["CRIPTA_PAQUETE_API"] = args.paquete
    os.environ["CRIPTA_SIN_AUDIO"] = "1"
    from tests.test_criptas_api import TestPaqueteOficial
    from tests.test_verificacion_entrega import TestCriptaDesconocida

    ciclos, arranques, eventos = [], [], []
    ejecutar_original = Motor.ejecutar
    ciclo_original = Motor.ejecutar_ciclo

    def ciclo(motor, decidir):
        inicio = perf_counter()
        resultado = ciclo_original(motor, decidir)
        eventos.append((motor.meta.cripta_id, (perf_counter() - inicio) * 1000))
        return resultado

    def ejecutar(motor, accion, argumento=None):
        inicio = perf_counter()
        resultado = ejecutar_original(motor, accion, argumento)
        ciclos.append({"cripta": motor.meta.cripta_id, "accion": accion,
                       "ms": (perf_counter() - inicio) * 1000, "ok": resultado.ok})
        return resultado

    def crear(*argumentos, **opciones):
        inicio = perf_counter()
        motor = crear_juego(*argumentos, **opciones)
        arranques.append({"cripta": motor.meta.cripta_id,
                          "ms": (perf_counter() - inicio) * 1000})
        return motor

    suite = unittest.TestSuite([
        TestPaqueteOficial("test_partidas_hasta_victoria_y_replay_en_las_cuatro_criptas"),
        TestPaqueteOficial("test_todas_las_salas_iconos_guardado_y_carga"),
        TestCriptaDesconocida("test_137_salas_tipos_nuevos_eventos_victoria_guardado_replay"),
    ])
    with patch.object(Motor, "ejecutar", ejecutar), \
            patch.object(Motor, "ejecutar_ciclo", ciclo), \
            patch("tests.test_criptas_api.crear_juego", crear), \
            patch("tests.test_verificacion_entrega.crear_juego", crear):
        resultado = unittest.TextTestRunner(verbosity=1).run(suite)
    resumen, resumen_eventos = [], []
    for cripta in ("cripta-01", "cripta-02", "cripta-03", "cripta-04", "desconocida"):
        tiempos = sorted(c["ms"] for c in ciclos if c["cripta"] == cripta)
        if tiempos:
            resumen.append({"cripta": cripta, "acciones": len(tiempos),
                "media_ms": sum(tiempos) / len(tiempos),
                "p95_ms": tiempos[min(len(tiempos)-1, int(len(tiempos)*.95))],
                "max_ms": max(tiempos), "acciones_ge_20_ms": sum(t >= 20 for t in tiempos)})
        tiempos_evento = [ms for clave, ms in eventos if clave == cripta]
        if tiempos_evento:
            resumen_eventos.append({"cripta": cripta, "eventos": len(tiempos_evento),
                "media_ms": sum(tiempos_evento) / len(tiempos_evento),
                "max_ms": max(tiempos_evento),
                "eventos_ge_20_ms": sum(t >= 20 for t in tiempos_evento)})
    informe = {"exito": resultado.wasSuccessful(), "python": platform.python_version(), "resumen": resumen,
               "ciclos_eventos": resumen_eventos,
               "arranques": arranques, "ciclos": ciclos,
               "alcance": "Motor completo; incluye cargas locales y precarga, excluye Tk, audio y HTTP. Una ejecucion, sin calentamiento descartado."}
    ruta = Path(args.salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print(json.dumps(resumen_eventos, ensure_ascii=False, indent=2))
    print(f"Datos completos: {ruta}")
    return 0 if resultado.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
