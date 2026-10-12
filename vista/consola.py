from modelo.snapshots import EstadoVista, ItemVista

AYUDA = """\
Comandos:
  n / s / e / o           moverse (norte, sur, este, oeste)      [mover <dir>]
  abrir <dir>             abrir la puerta de esa dirección con la llave adecuada
  atacar [id]             atacar (si hay un solo enemigo, el id es opcional)
  esperar                 pasar el tiempo
  recoger [id]            recoger un objeto del suelo
  usar | equipar | soltar [id]   actúan sobre el objeto que estás viendo en el inventario
  inv                     ver inventario (orden real)
  inv orden peso|valor|nombre [desc]   vista ordenada (no altera el orden real)
  sig | ant               recorrer el inventario hacia adelante / atrás
  retroceso               usar un pergamino de retroceso
  guardar [archivo]       guardar la partida      cargar [archivo]   cargar partida
  puntajes                ver la tabla de puntajes
  replay [archivo]        reproducir una partida guardada en bitácora (por defecto, la actual)
  ayuda                   esta ayuda              salir              terminar la sesión"""


class VistaConsola:
    def __init__(self, entrada=input, salida=print):
        self._entrada = entrada
        self._salida = salida

    #entrada
    def pedir_comando(self):
        return self._entrada("\n> ")

    def pedir_texto(self, pregunta):
        return self._entrada(f"{pregunta}: ").strip()

    def elegir_cripta(self, criptas):
        """`criptas` es la lista JSON de GET /criptas: [{id, nombre, salas, dificultad}]."""
        self._salida("Criptas disponibles:")
        for n, c in enumerate(criptas, start=1):
            self._salida(f"  {n}. {c['id']} - {c['nombre']} "
                         f"({c['salas']} salas, dificultad {c['dificultad']})")
        while True:
            eleccion = self.pedir_texto("Elige una cripta (número o id)")
            if eleccion.isdigit() and 1 <= int(eleccion) <= len(criptas):
                return criptas[int(eleccion) - 1]["id"]
            for c in criptas:
                if c["id"] == eleccion:
                    return c["id"]
            self._salida("Opción no válida.")

    #salida 
    def mostrar_estado(self, e: EstadoVista, mensajes):
        s = self._salida
        s("")
        s("=" * 64)
        s(f" t={e.reloj}   Sala {e.sala_id}: {e.sala_nombre}")
        s("=" * 64)
        if e.salidas:
            partes = []
            for sal in e.salidas:
                txt = f"{sal.direccion} -> sala {sal.destino}"
                if sal.cerrada:
                    txt += " [CERRADA" + (f", llave {sal.llave}" if sal.llave else "") + "]"
                partes.append(txt)
            s("Salidas : " + " | ".join(partes))
        else:
            s("Salidas : (ninguna)")
        if e.enemigos:
            s("Enemigos:")
            for en in e.enemigos:
                s(f"   [{en.instancia}] {en.nombre}  vida {en.vida}/{en.vida_max}")
        else:
            s("Enemigos: (ninguno)")
        if e.objetos_suelo:
            s("En el suelo: " + ", ".join(f"[{o.instancia}] {o.nombre}" for o in e.objetos_suelo))
        else:
            s("En el suelo: (nada)")
        s(f"Tú: vida {e.vida}/{e.vida_max} | ataque {e.ataque} | defensa {e.defensa} | "
          f"velocidad {e.velocidad} | inventario {e.inventario_usado}/{e.inventario_max}")
        s("Efectos: " + (", ".join(e.efectos) if e.efectos else "(ninguno)"))
        s("-" * 64)
        s(f"Últimos mensajes ({len(mensajes)}):")
        for m in mensajes:
            s(f"  - {m}")

    def mostrar_inventario(self, items, orden=None, cursor=None):
        """`cursor` es la instancia del objeto que se está viendo (se marca con >)."""
        titulo = "Inventario (orden real)" if orden is None else f"Inventario ordenado por {orden}"
        self._salida(titulo + ":")
        if not items:
            self._salida("   (vacío)")
        for it in items:
            marca = ">" if cursor is not None and it.instancia == cursor else " "
            eq = " (equipado)" if it.equipado else ""
            self._salida(f" {marca} [{it.instancia}] {it.nombre:<22} {it.clase:<10} "
                         f"peso {it.peso:<3} valor {it.valor:<4}{eq}")

    def mostrar_item(self, item: ItemVista | None):
        if item is None:
            self._salida("El inventario está vacío.")
        else:
            eq = " (equipado)" if item.equipado else ""
            self._salida(f"Viendo: [{item.instancia}] {item.nombre} - {item.clase}, "
                         f"peso {item.peso}, valor {item.valor}{eq}")

    def mostrar_error(self, texto):
        self._salida(f"(!) {texto}")

    def mostrar_info(self, texto):
        self._salida(texto)

    def mostrar_ayuda(self):
        self._salida(AYUDA)

    def mostrar_puntajes(self, registros):
        self._salida("Tabla de puntajes:")
        if not registros:
            self._salida("   (aún no hay partidas registradas)")
        for n, r in enumerate(registros, start=1):
            self._salida(f"  {n:>2}. {r.nombre:<14} {r.resultado:<9} tiempo {r.tiempo_final:<6} "
                         f"acciones {r.acciones:<4} derrotados {r.derrotados:<3} "
                         f"[{r.cripta_id}@{r.cripta_version}]")

    def mostrar_fin(self, resumen):
        self._salida("")
        self._salida("*" * 64)
        if resumen.resultado == "victoria":
            self._salida("  VICTORIA: has escapado de la cripta.")
        elif resumen.resultado == "derrota":
            self._salida("  DERROTA: has muerto en la cripta.")
        else:
            self._salida("  Sesión terminada.")
        self._salida(f"  acciones {resumen.acciones} | derrotados {resumen.derrotados} | "
                     f"tiempo virtual {resumen.reloj_final}")
        self._salida("*" * 64)

    def mostrar_replay_paso(self, estado, mensajes, paso, total, inventario=None):
        """Una línea por paso del replay. Devuelve True para seguir."""
        ultimo = mensajes[-1] if mensajes else ""
        self._salida(f"[{paso}/{total}] {ultimo}  ->  sala {estado.sala_id} | "
                     f"vida {estado.vida}/{estado.vida_max} | t={estado.reloj}")
        return True

    def mostrar_estadisticas_red(self, est):
        """§5.1: al terminar se reporta solicitudes, presupuesto y aciertos/fallos de caché."""
        self._salida(f"Red: {est.solicitudes} solicitudes de {est.presupuesto} permitidas | "
                     f"caché: {est.aciertos_cache} aciertos, {est.fallos_cache} fallos")