"""Anclajes de los recursos existentes: son coordenadas artisticas, no reglas."""


_POSES = {
    "correr": (((.03, -.56), (.29, -.60)), ((.02, -.54), (.32, -.51)),
               ((.04, -.57), (.28, -.68)), ((.06, -.56), (.31, -.50))),
    "atacar": (((-.01, -.48), (.33, -.62)), ((.09, -.47), (.35, -.49))),
    "caer": (((.03, -.27), (.16, -.39)), ((.05, -.18), (.16, -.17))),
}

# Hombro izquierdo, hombro derecho y cintura izquierda sobre cada ilustracion.
# El chaleco se deforma con el torso antes de reducir o reflejar el fotograma.
_TORSOS = (
    ((.50, .278), (.708, .343), (.458, .482)),
    ((.50, .278), (.708, .343), (.458, .482)),
    ((.50, .260), (.708, .325), (.458, .464)),
    ((.50, .300), (.708, .343), (.450, .504)),
    ((.37, .320), (.57, .350), (.340, .500)),
    ((.42, .350), (.62, .390), (.350, .540)),
    ((.242, .500), (.375, .382), (.448, .714)),
    ((.255, .790), (.285, .665), (.475, .815)),
)

_MANOS = ((.828, .439), (.784, .462), (.774, .377), (.831, .473),
          (.839, .286), (.815, .363), (.508, .368), (.362, .850))
_MANOS_IZQUIERDAS = ((.365, .456), (.365, .484), (.30, .43), (.48, .507),
                     (.275, .405), (.693, .484), (.273, .686), (.23, .88))


def iluminar_jugador(imagen, antorcha, puno, pose=None):
    """Antorcha en el puno izquierdo, independiente del arma y de sus efectos."""
    from PIL import Image, ImageDraw, ImageOps

    mano = ((.36, .60) if pose == "beber" else (.38, .57) if pose is None
            else _MANOS_IZQUIERDAS[pose])
    tamano = max(1, int(imagen.height * .42))
    objeto = antorcha.copy()
    objeto.thumbnail((tamano, tamano), Image.Resampling.LANCZOS)
    capa = Image.new("RGBA", (tamano * 2, tamano * 2))
    capa.alpha_composite(objeto, (tamano - int(objeto.width * .24), tamano - int(objeto.height * .72)))
    # La llama apunta fuera del antebrazo; el giro conserva el mango en la palma.
    giro = -25 if pose in (5, 6) else -50 if pose == 7 else 80
    capa = capa.rotate(giro, resample=Image.Resampling.BICUBIC)
    x, y = int(mano[0] * imagen.width), int(mano[1] * imagen.height)
    resultado = imagen.copy()
    abierta = pose in (None, "beber") or pose >= 4
    mascara = Image.new("L", imagen.size)
    dibujo = ImageDraw.Draw(mascara)
    if abierta:
        dibujo.rectangle((x - imagen.width * .045, y - imagen.height * .025,
                           x + imagen.width * .05, y + imagen.height * .08), fill=255)
        resultado.paste((0, 0, 0, 0), (0, 0, imagen.width, imagen.height), mascara)
    resultado.alpha_composite(capa, (x - tamano, y - tamano))
    if abierta:
        cerrado = ImageOps.mirror(puno)
        altura = max(1, int(imagen.height * .085))
        cerrado = cerrado.resize((max(1, int(cerrado.width * altura / cerrado.height)), altura),
                                 Image.Resampling.LANCZOS)
        cerrado = cerrado.rotate(120 if pose in (None, "beber") else 15,
                                  expand=True, resample=Image.Resampling.BICUBIC)
        resultado.alpha_composite(cerrado, (x - cerrado.width // 2, y - cerrado.height // 2))
    else:
        dibujo.ellipse((x - imagen.width * .04, y - imagen.height * .05,
                         x + imagen.width * .04, y + imagen.height * .05), fill=255)
        resultado.paste(imagen, (0, 0), mascara)
    return resultado


def armar_jugador(imagen, daga, puno, pose=None):
    """Sustituye la mano abierta por un puno del propio tigre alrededor del mango."""
    from PIL import Image, ImageDraw

    mano = (.835, .565) if pose is None else _MANOS[pose]
    tamano = max(1, int(imagen.height * .24))
    arma = daga.copy()
    arma.thumbnail((tamano, tamano), Image.Resampling.LANCZOS)
    capa = Image.new("RGBA", (tamano * 2, tamano * 2))
    capa.alpha_composite(arma, (tamano - int(arma.width * .28), tamano - int(arma.height * .22)))
    angulo = 0 if pose is None else (0, 20, -15, 15, 85, 35, 20, 70)[pose]
    capa = capa.rotate(angulo, resample=Image.Resampling.BICUBIC)
    x, y = int(mano[0] * imagen.width), int(mano[1] * imagen.height)
    resultado = imagen.copy()
    mano_abierta = pose is None or pose >= 4
    if mano_abierta:
        borrar = Image.new("L", imagen.size)
        dibujo = ImageDraw.Draw(borrar)
        if pose is None:
            dibujo.polygon([(int(px * imagen.width), int(py * imagen.height)) for px, py in
                ((.755, .535), (.91, .535), (.91, .66), (.755, .66))], fill=255)
        else:
            zonas = (
                ((306, 69), (355, 69), (355, 145), (306, 145)),
                ((299, 116), (312, 80), (360, 80), (380, 116), (380, 176),
                 (325, 176), (312, 148), (298, 143)),
                ((185, 108), (192, 72), (242, 72), (242, 154), (197, 162), (185, 142)),
                ((110, 283), (190, 283), (190, 353), (110, 353)),
            )
            dibujo.polygon([(int(px * imagen.width / 384), int(py * imagen.height / 353))
                             for px, py in zonas[pose - 4]], fill=255)
        resultado.paste((0, 0, 0, 0), (0, 0, imagen.width, imagen.height), borrar)
    resultado.alpha_composite(capa, (x - tamano, y - tamano))
    if mano_abierta:
        cerrado = puno.copy()
        altura = max(1, int(imagen.height * .085))
        cerrado = cerrado.resize((max(1, int(cerrado.width * altura / cerrado.height)), altura),
                                 Image.Resampling.LANCZOS)
        giro = -120 if pose is None else (0, -15, 15, -60)[pose - 4]
        cerrado = cerrado.rotate(giro, expand=True, resample=Image.Resampling.BICUBIC)
        resultado.alpha_composite(cerrado, (x - cerrado.width // 2, y - cerrado.height // 2))
    else:
        dedos = Image.new("L", imagen.size)
        rx, ry = imagen.width * .04, imagen.height * .05
        ImageDraw.Draw(dedos).ellipse((x - rx, y - ry, x + rx, y + ry), fill=255)
        resultado.paste(imagen, (0, 0), dedos)
    return resultado


def vestir_jugador(imagen, chaleco, pose=None):
    """Compone ropa ajustada al torso; no cambia el recurso original ni su alfa."""
    from PIL import Image, ImageChops, ImageDraw

    puntos = ((.445, .205), (.695, .220), (.475, .425)) if pose is None else _TORSOS[pose]
    (x, y), (derecha, arriba), (izquierda, abajo) = [
        (px * imagen.width, py * imagen.height) for px, py in puntos]
    ux, uy = derecha - x, arriba - y
    vx, vy = izquierda - x, abajo - y
    if pose is not None:
        x, y = x - ux * .10, y - uy * .10
        ux, uy = ux * 1.20, uy * 1.20
        vx, vy = vx * 1.08, vy * 1.08
    determinante = ux * vy - uy * vx
    a, b = chaleco.width * vy / determinante, -chaleco.width * vx / determinante
    d, e = -chaleco.height * uy / determinante, chaleco.height * ux / determinante
    ropa = chaleco.transform(imagen.size, Image.Transform.AFFINE,
        (a, b, -a * x - b * y, d, e, -d * x - e * y), Image.Resampling.BICUBIC)
    alfa_original = imagen.getchannel("A")
    ropa.putalpha(ImageChops.multiply(ropa.getchannel("A"), alfa_original))
    resultado = Image.alpha_composite(imagen, ropa)
    # El antebrazo adelantado cruza el pecho en el segundo ataque.
    if pose == 5:
        mascara = Image.new("L", imagen.size)
        ImageDraw.Draw(mascara).polygon([(int(px * imagen.width), int(py * imagen.height))
            for px, py in ((.53, .43), (.78, .33), (.88, .42), (.61, .56))], fill=255)
        resultado.paste(imagen, (0, 0), mascara)
    resultado.putalpha(alfa_original)
    return resultado


def dibujar_equipo(escena, estado, sprite, reposo, cuadros, accion, recogido, invertir=False,
                   armadura_integrada=False, arma_integrada=False):
    if not (getattr(estado, "arma_tipo", None) or getattr(estado, "armadura_tipo", None) or recogido):
        return
    canvas = escena.vista.canvas
    animacion = escena.animacion
    x, y = canvas.coords(sprite)
    w, h = reposo.width(), reposo.height()
    torso = (w * .08, -h * .58)
    mano = (w * .335, -h * .435)
    poses = _POSES.get(accion, ())
    if cuadros and poses:
        w_cuadro, h_cuadro = cuadros[0].width(), cuadros[0].height()
        torsos = [(p[0][0] * w_cuadro, p[0][1] * h_cuadro) for p in poses]
        manos = [(p[1][0] * w_cuadro, p[1][1] * h_cuadro) for p in poses]
        if invertir:
            torsos = [(-px, py) for px, py in torsos]
            manos = [(-px, py) for px, py in manos]
    else:
        torsos, manos = (), ()

    def accesorio(tipo, tamano, posicion, anclajes, etiqueta, duracion=None, ocultar_hasta=0):
        if not tipo:
            return
        imagen = escena._imagen(tipo, *tamano)
        if imagen is None:
            return
        identificador = canvas.create_image(x + posicion[0], y + posicion[1], image=imagen,
                                            tags=("equipo_jugador", etiqueta))
        if animacion is not None:
            animacion.anclar(identificador, sprite, posicion, anclajes,
                             duracion=duracion, ocultar_hasta=ocultar_hasta)

    if not armadura_integrada:
        accesorio(getattr(estado, "armadura_tipo", None), (w * .34, h * .38), torso, torsos,
                  "armadura_visible")
    # El mango de la daga esta en el cuadrante superior izquierdo de su imagen.
    tamano_arma = min(54, h * .31)
    mango = 16 * tamano_arma / 54
    agarre = (mano[0] + mango, mano[1] + mango)
    agarres = [(px + mango, py + mango) for px, py in manos]
    levantando = recogido is not None and animacion is not None and accion != "caer"
    if not arma_integrada:
        accesorio(getattr(estado, "arma_tipo", None), (tamano_arma, tamano_arma), agarre, agarres,
                  "arma_visible", ocultar_hasta=45 if levantando else 0)
    if levantando:
        tamano_objeto = min(42, h * .24)
        mano_objeto = (-w * .12, -h * .435) if arma_integrada else mano
        accesorio(recogido.tipo, (tamano_objeto, tamano_objeto), mano_objeto,
                  () if arma_integrada else manos, "objeto_recogido", duracion=45)
