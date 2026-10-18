"""python -m tests.medir_presentacion: primer uso y repeticion de la vista Tk.

Los snapshots son sinteticos: mide presentacion, no HTTP ni reglas del motor.
No incluye el tiempo intencional de las animaciones. No escribe partidas.
"""
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import tempfile
from time import perf_counter

from modelo.snapshots import ItemVista, EnemigoVista, TrampaVista
from tests import test_regresiones_juego as base
from vista.cache_visual import CacheVisual
from vista.grafica import VistaGrafica
from vista.recursos_graficos import RecursosGraficos


def escenarios(estado):
    lleno = replace(estado, arma_tipo="itm_daga_oxidada", armadura_tipo="itm_coraza_cuero", efectos=["antorcha"])
    for coraza, daga, antorcha in product((0, 1), repeat=3):
        if not (coraza or daga or antorcha):
            continue
        final = replace(estado, armadura_tipo="itm_coraza_cuero" if coraza else None,
                        arma_tipo="itm_daga_oxidada" if daga else None, efectos=["antorcha"] if antorcha else [])
        yield f"equipo/{coraza}{daga}{antorcha}", estado, final, "equipar", None
    for coraza, antorcha, antidoto in product((0, 1), repeat=3):
        anterior = replace(estado, armadura_tipo="itm_coraza_cuero" if coraza else None,
                           efectos=["antorcha"] if antorcha else [])
        item = ItemVista("bebida", "Antidoto" if antidoto else "Pocion", "antidoto" if antidoto else "pocion", 1, 1,
                        tipo="itm_antidoto" if antidoto else "itm_pocion_menor")
        yield f"beber/{coraza}{antorcha}{antidoto}", anterior, replace(anterior, reloj=1), "usar", item
    for tipo in ("itm_pocion_menor", "itm_antidoto", "itm_daga_oxidada", "itm_coraza_cuero", "itm_antorcha",
                 "itm_pergamino_retroceso", "itm_llave_bronce", "itm_llave_negra", "tipo_nuevo"):
        item = ItemVista("objeto", tipo, "objeto", 1, 1, tipo=tipo)
        yield "recoger/"+tipo, replace(estado, objetos_suelo=[item]), replace(estado, reloj=1), "recoger", item
    for accion in ("atacar", "soltar", "esperar", "retroceso", "cargar"):
        yield accion, lleno, replace(lleno, reloj=1), accion, None
    yield "mover", lleno, replace(lleno, sala_id=2, reloj=1), "mover", None
    yield "derrota", lleno, replace(lleno, vida=0, reloj=1), "atacar", None
    yield "sala_poblada", estado, replace(estado, reloj=1,
        enemigos=[EnemigoVista(f"e{i}", "Guardian", 10, 10, tipo="ent_guardian_oseo") for i in range(16)],
        trampas=[TrampaVista(f"t{i}", "Dardos", True, 4, tipo="trp_dardos") for i in range(8)]), "esperar", None


def main():
    salida = Path(".cache/presentacion.json")
    salida.parent.mkdir(exist_ok=True)
    vista = VistaGrafica()
    registros = []
    try:
        datos = base.TestRegresionesJuego()
        datos.setUp()
        estado = datos.motor.estado_vista()
        for tamano in ("1100x760", "1280x850"):
            vista.root.geometry(tamano)
            vista.root.update()
            for nombre, anterior, final, accion, item in escenarios(estado):
                with tempfile.TemporaryDirectory() as carpeta:
                    vista.recursos = RecursosGraficos(vista.root)
                    vista.recursos._cache_visual = CacheVisual(vista.recursos.carpeta, carpeta)
                    for fase in ("primero", "repetido"):
                        vista.reiniciar_presentacion()
                        vista.mostrar_estado(estado, [])
                        vista.mostrar_estado(anterior, [])
                        vista._items = [item] if item else []
                        inicio = perf_counter()
                        vista.preparar_animacion(accion, item.instancia if item else None)
                        vista.mostrar_estado(final, [])
                        if vista.transicion_salas.activa:
                            vista.escena.animacion._al_llegar()
                        vista.mostrar_inventario([item] if item else [])
                        vista.root.update_idletasks()
                        registros.append({"tamano": tamano, "escenario": nombre, "fase": fase,
                                          "ms": (perf_counter()-inicio)*1000})
        informe = {"alcance": __doc__, "mediciones": registros}
        salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
        for fase in ("primero", "repetido"):
            muestras = sorted((r for r in registros if r["fase"] == fase), key=lambda r: r["ms"])
            print(f"{fase}: {len(muestras)} escenarios, media={sum(r['ms'] for r in muestras)/len(muestras):.2f} ms, "
                  f"p95={muestras[int(len(muestras)*.95)]['ms']:.2f} ms, max={muestras[-1]['ms']:.2f} ms")
            print("Mayores:", [(r["escenario"], r["tamano"], round(r["ms"], 2)) for r in muestras[-5:]])
        print(f"Detalle: {salida}")
    finally:
        vista.cerrar()


if __name__ == "__main__":
    main()
