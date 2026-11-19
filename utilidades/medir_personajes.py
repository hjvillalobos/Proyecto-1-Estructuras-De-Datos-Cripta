"""Medicion local reproducible: python -m utilidades.medir_personajes.

No consulta red ni modifica partidas. Los tiempos dependen del equipo y del SO;
cache fria significa cache visual vacia, no vaciar la cache de disco del SO.
"""
import json
from itertools import product
from pathlib import Path
import platform
from statistics import median
import tempfile
from time import perf_counter
import tkinter as tk

from vista.animacion import AnimacionEscena
from vista.cache_visual import CacheVisual
from vista.personajes import PERSONAJES
from vista.recursos_graficos import RecursosGraficos


def medir(funcion):
    inicio = perf_counter()
    resultado = funcion()
    return resultado, (perf_counter() - inicio) * 1000


def resumen(valores):
    valores = sorted(valores)
    return {"mediana_ms": round(median(valores), 3),
            "p95_ms": round(valores[min(len(valores)-1, int(len(valores)*.95))], 3),
            "max_ms": round(max(valores), 3), "muestras": len(valores)}


def medir_personaje(root, personaje, carpeta):
    r = RecursosGraficos(root, personaje=personaje)
    r._cache_visual = CacheVisual(r.carpeta, carpeta, personaje=personaje)
    # Impedir que la medicion oculte un paquete desactualizado recomponiendo poses.
    def no_componer(*args, **kwargs):
        raise AssertionError("El paquete preparado no esta vigente")
    r._componer_reposo = r._componer_fotogramas = r._componer_bebida = no_componer
    def portada():
        return (r.fondo(1100, 760), *(r.retrato_personaje(p, 225, 486) for p, _ in PERSONAJES))
    _, menu = medir(portada)
    _, menu_caliente = medir(portada)
    otro = "tigresa" if personaje == "jugador" else "jugador"
    _, cambio = medir(lambda: (r.seleccionar_personaje(otro), portada()))
    r.seleccionar_personaje(personaje)
    r._cache_visual = CacheVisual(r.carpeta, carpeta, personaje=personaje)
    primeras, repetidas = [], []
    for coraza, daga, luz in product((0, 1), repeat=3):
        armadura = "itm_coraza_cuero" if coraza else None
        arma = "itm_daga_oxidada" if daga else None
        def cargar_equipo():
            reposo = (r.jugador_armado(230, 196, arma, armadura, luz) if daga or luz else
                      r.jugador_vestido(230, 196, armadura) if coraza else r.imagen("jugador", 230, 196))
            assert reposo is not None
            for invertir in (False, True):
                for accion, cantidad in (("correr", 4), ("atacar", 2), ("caer", 2)):
                    assert len(r.fotogramas_accion(accion, 290, 196, invertir, armadura, arma, luz)) == cantidad
            assert r.pose_beber(196, armadura, False, luz) is not None
            assert r.pose_beber(196, armadura, True, luz) is not None
        _, frio = medir(cargar_equipo)
        _, caliente = medir(cargar_equipo)
        primeras.append(frio)
        repetidas.append(caliente)
    canvas = tk.Canvas(root, width=700, height=300)
    canvas.pack()
    root.update_idletasks()
    cuadros = r.fotogramas_accion("correr", 290, 196, armadura="itm_coraza_cuero",
                                   arma="itm_daga_oxidada", antorcha=True)
    sprite = canvas.create_image(150, 230, image=cuadros[0], anchor="s")
    a = AnimacionEscena(root, canvas)
    a.agregar(sprite, carrera=True)
    a.secuencia(sprite, cuadros, repetir=True, duracion=10000)
    intervalos, trabajos = [], []
    ultimo = perf_counter()
    avanzar = a._avanzar
    def tic():
        nonlocal ultimo
        ahora = perf_counter()
        intervalos.append((ahora-ultimo)*1000)
        ultimo = ahora
        _, tiempo = medir(avanzar)
        trabajos.append(tiempo)
    a._avanzar = tic
    a.iniciar()
    root.after(2000, root.quit)
    root.mainloop()
    a.detener()
    canvas.destroy()
    return {"portada_ambos_primera_carga_ms": round(menu, 3), "portada_ambos_en_memoria_ms": round(menu_caliente, 3),
            "alternar_personaje_con_ambos_retratos_ms": round(cambio, 3),
            "equipo_con_ambas_orientaciones_y_bebidas_primera_carga": resumen(primeras),
            "equipo_repetido_en_memoria": resumen(repetidas),
            "intervalo_animacion_objetivo_20ms": resumen(intervalos),
            "trabajo_por_tic": resumen(trabajos),
            "atlas_pil": len(r._hojas_accion),
            "cache_tk": {"acciones": len(r._acciones), "secuencias": len(r._secuencias),
                         "vestidos": len(r._jugadores_vestidos), "bebidas": len(r._bebidas)}}


def main():
    root = tk.Tk()
    root.withdraw()
    try:
        with tempfile.TemporaryDirectory() as carpeta:
            reporte = {"python": platform.python_version(), "sistema": platform.platform(),
                       "alcance": "Cache visual fria; disco del SO sin vaciar; Tk oculto; sin red",
                       "personajes": {p: medir_personaje(root, p, carpeta) for p, _ in PERSONAJES}}
        ruta = Path("datos_generados/medicion_personajes.json")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(reporte, ensure_ascii=False, indent=2))
        print(f"Guardado: {ruta}")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
