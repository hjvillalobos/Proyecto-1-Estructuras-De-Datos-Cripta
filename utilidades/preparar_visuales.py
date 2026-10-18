"""Genera PNG sin perdida para distribuir: python -m utilidades.preparar_visuales.

No abre Tk ni toca el motor o la red. Regenerar si se cambia el arte o su codigo.
"""
from itertools import product

from vista.recursos_graficos import RecursosGraficos, Image


ALTURAS = (122, 165, 193, 196)


def hoja(cuadros):
    w, h = cuadros[0].size
    atlas = Image.new("RGBA", (w * len(cuadros), h))
    for i, cuadro in enumerate(cuadros):
        atlas.paste(cuadro, (i*w, 0))
    return atlas


def reducir_cuadros(cuadros, tamano, invertir=False):
    resultado = []
    for original in cuadros:
        cuadro = original.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if invertir else original.copy()
        cuadro.thumbnail(tamano, Image.Resampling.LANCZOS)
        limite = cuadro.getchannel("A").point(lambda a: 255 if a >= 32 else 0).getbbox()
        if limite is not None and limite[3] < cuadro.height:
            alineado = Image.new("RGBA", cuadro.size)
            alineado.paste(cuadro, (0, cuadro.height - limite[3]))
            cuadro = alineado
        resultado.append(cuadro)
    return resultado


def main():
    if Image is None:
        raise SystemExit("Se necesita Pillow para generar las composiciones.")
    recursos = RecursosGraficos(None)
    preparadas = recursos._preparadas
    preparadas.habilitada = False
    for coraza, daga, antorcha in product((0, 1), repeat=3):
        armadura = "itm_coraza_cuero" if coraza else None
        arma = "itm_daga_oxidada" if daga else None
        equipo = (coraza, daga, antorcha)
        reposo = recursos._componer_reposo(armadura, arma, antorcha)
        cuadros = recursos._componer_fotogramas(armadura, arma, antorcha)
        preparadas.guardar(("reposo", *equipo), reposo)
        preparadas.guardar(("acciones", *equipo), hoja(cuadros))
        for alto in ALTURAS:
            reducido = reposo.copy()
            reducido.thumbnail((230, alto), Image.Resampling.LANCZOS)
            preparadas.guardar(("reposo", 230, alto, *equipo), reducido)
            for invertir in (0, 1):
                preparadas.guardar(("secuencia", 290, alto, invertir, *equipo),
                    hoja(reducir_cuadros(cuadros, (290, alto), invertir)))
    for coraza, antidoto, antorcha in product((0, 1), repeat=3):
        armadura = "itm_coraza_cuero" if coraza else None
        cuadro = recursos._componer_bebida(armadura, antidoto, antorcha)
        opciones = (coraza, antidoto, antorcha)
        preparadas.guardar(("bebida_original", *opciones), cuadro)
        for alto in ALTURAS:
            reducido = cuadro.copy()
            reducido.thumbnail((290, alto), Image.Resampling.LANCZOS)
            preparadas.guardar(("bebida", alto, *opciones), reducido)
    archivos = list(preparadas.carpeta.glob("*.png"))
    print(f"{len(archivos)} composiciones; {sum(p.stat().st_size for p in archivos)/1e6:.2f} MB")


if __name__ == "__main__":
    main()
