"""python -m tests.medir_puertas: transiciones reales de 26 pasos con Tk.

Mide dibujo inicial, redibujo al llegar, costo de cada callback e intervalos.
Las salas son sinteticas; no mide HTTP. Se preserva la duracion de la animacion.
"""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
from time import perf_counter
import tkinter as tk
from unittest.mock import patch

from tests import test_regresiones_juego as base
from vista.animacion import AnimacionEscena
from vista.cache_visual import CacheVisual
from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos


def main():
    vista, registros = VistaGrafica(), []
    original = AnimacionEscena._avanzar
    try:
        for tamano in ("1100x760", "1280x850"):
            vista.root.geometry(tamano)
            vista.root.update()
            for equipo in (False, True):
                for direccion, opuesta in (("N", "S"), ("S", "N"), ("E", "O"), ("O", "E")):
                    with tempfile.TemporaryDirectory() as carpeta:
                        vista.recursos = RecursosGraficos(vista.root)
                        vista.recursos._cache_visual = CacheVisual(vista.recursos.carpeta, carpeta)
                        for fase in ("primero", "repetido"):
                            datos = base.TestRegresionesJuego()
                            datos.setUp()
                            motor = datos.motor
                            motor.sala_salida = None
                            motor.salas[1].salidas = {direccion: {"sala": 2}}
                            motor.salas[2].salidas = {opuesta: {"sala": 1}}
                            def estado():
                                e = motor.estado_vista()
                                return replace(e, arma_tipo="itm_daga_oxidada", armadura_tipo="itm_coraza_cuero",
                                               efectos=["antorcha"]) if equipo else e
                            vista.reiniciar_presentacion()
                            vista.mostrar_estado(estado(), [])
                            inicio_motor = perf_counter()
                            assert motor.ejecutar("mover", direccion).ok
                            motor_ms = (perf_counter()-inicio_motor)*1000
                            final, esperado = estado(), motor.exportar_estado()
                            fin = tk.BooleanVar(master=vista.root, value=False)
                            ticks, tiempos, llegadas = [], [], []
                            def avanzar(animacion):
                                t = perf_counter()
                                activa = vista.transicion_salas.activa
                                original(animacion)
                                costo = (perf_counter()-t)*1000
                                ticks.append((t, costo))
                                if activa and not vista.transicion_salas.activa:
                                    llegadas.append(costo)
                                else:
                                    tiempos.append(costo)
                                if not vista.transicion_salas.activa and vista.escena.animacion.paso >= 16:
                                    fin.set(True)
                            with patch.object(AnimacionEscena, "_avanzar", avanzar):
                                t = perf_counter()
                                vista.preparar_animacion("mover")
                                vista.mostrar_estado(final, [])
                                dibujo = (perf_counter()-t)*1000
                                vista.root.wait_variable(fin)
                                total = (perf_counter()-t)*1000
                            assert motor.exportar_estado() == esperado
                            assert len(ticks) == 26, len(ticks)
                            intervalos = [(b[0]-a[0])*1000 for a, b in zip(ticks, ticks[1:])]
                            registros.append({"tamano": tamano, "equipo": equipo, "direccion": direccion,
                                "fase": fase, "motor_ms": motor_ms, "inicio_ms": dibujo,
                                "llegada_ms": max(llegadas), "callback_normal_max_ms": max(tiempos),
                                "intervalo_max_ms": max(intervalos), "total_ms": total})
        salida = Path(".cache/puertas.json")
        salida.write_text(json.dumps({"alcance": __doc__, "mediciones": registros}, indent=2), encoding="utf-8")
        for fase in ("primero", "repetido"):
            filas = [r for r in registros if r["fase"] == fase]
            print(fase, {k: round(max(r[k] for r in filas), 2) for k in
                ("inicio_ms", "llegada_ms", "callback_normal_max_ms", "intervalo_max_ms", "total_ms")})
        print(f"{len(registros)} recorridos; estado del motor conservado. Detalle: {salida}")
    finally:
        vista.cerrar()


if __name__ == "__main__":
    main()
