"""Anclajes de los recursos existentes: son coordenadas artisticas, no reglas."""


_POSES = {
    "correr": (((.03, -.56), (.29, -.60)), ((.02, -.54), (.32, -.51)),
               ((.04, -.57), (.28, -.68)), ((.06, -.56), (.31, -.50))),
    "atacar": (((-.01, -.48), (.33, -.62)), ((.09, -.47), (.35, -.49))),
    "caer": (((.03, -.27), (.16, -.39)), ((.05, -.18), (.16, -.17))),
}


def dibujar_equipo(escena, estado, sprite, reposo, cuadros, accion, recogido, invertir=False):
    if not (getattr(estado, "arma_tipo", None) or getattr(estado, "armadura_tipo", None) or recogido):
        return
    canvas = escena.vista.canvas
    animacion = escena.animacion
    x, y = canvas.coords(sprite)
    w, h = reposo.width(), reposo.height()
    torso = (w * .08, -h * .58)
    mano = (w * .34, -h * .33)
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

    accesorio(getattr(estado, "armadura_tipo", None), (w * .34, h * .38), torso, torsos,
              "armadura_visible")
    # El mango de la daga esta en el cuadrante superior izquierdo de su imagen.
    tamano_arma = min(54, h * .31)
    mango = 16 * tamano_arma / 54
    agarre = (mano[0] + mango, mano[1] + mango)
    agarres = [(px + mango, py + mango) for px, py in manos]
    levantando = recogido is not None and animacion is not None and accion != "caer"
    accesorio(getattr(estado, "arma_tipo", None), (tamano_arma, tamano_arma), agarre, agarres,
              "arma_visible", ocultar_hasta=45 if levantando else 0)
    if levantando:
        tamano_objeto = min(42, h * .24)
        accesorio(recogido.tipo, (tamano_objeto, tamano_objeto), mano, manos, "objeto_recogido", duracion=45)
