# modelo/inventario.py

from modelo.tipos import ObjetoInstancia
from modelo.snapshots import ItemVista, ItemInventarioGuardado


def descripcion_objeto(ficha):
    atributos = ficha.atributos
    partes = []
    for campo, etiqueta in (("ataque_bonus", "Ataque"), ("defensa_bonus", "Defensa"), ("cura", "Cura")):
        if campo in atributos:
            partes.append(f"{etiqueta} +{atributos[campo]}")
    if "modificador_velocidad" in atributos:
        partes.append(f"Velocidad x{atributos['modificador_velocidad']:g}")
    if "duracion" in atributos:
        partes.append(f"Duracion {atributos['duracion']} u.t.")
    if ficha.clase == "llave":
        partes.append("Abre su puerta sin consumirse")
    if ficha.clase == "antidoto":
        partes.append("Cancela el veneno")
    if ficha.clase == "pergamino_retroceso":
        partes.append("Deshace la ultima accion y sus consecuencias")
    return " | ".join(partes)


class NodoInventario:
    """Nodo de la lista doblemente enlazada del inventario."""

    def __init__(self, objeto: ObjetoInstancia):
        self.objeto = objeto
        self.anterior = None
        self.siguiente = None
        self.en_inventario = False


class Inventario:
    """
    Lista doblemente enlazada propia (§2.7, §4.5). Usa el mismo patrón de
    centinelas vacíos que red/cache.py (cabeza/cola) para simplificar la
    inserción/eliminación en los bordes.

    - Recorrido adelante/atrás desde la posición actual (`cursor`).
    - Soltar el objeto que se está viendo cuesta O(1) sin importar su
      posición, porque `cursor` ya apunta directo al nodo.
    - Equipar mueve el nodo al frente del orden real.
    - Las vistas ordenadas (vista_ordenada) no alteran este orden real.
    """

    def __init__(self, capacidad_max: int):
        self.capacidad_max = capacidad_max
        self.tamaño = 0

        self.cabeza = NodoInventario(None)
        self.cola = NodoInventario(None)
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza

        self.cursor = None  # NodoInventario actual, o None si está vacío

        self.arma_equipada = None    # NodoInventario, o None
        self.armadura_equipada = None

    def esta_vacio(self) -> bool:
        return self.tamaño == 0

    def esta_lleno(self) -> bool:
        return self.tamaño >= self.capacidad_max

    # --- primitivas de bajo nivel (las usa historial.py para deshacer) ---

    def insertar_despues(self, nodo_referencia: "NodoInventario", objeto: ObjetoInstancia) -> "NodoInventario":
        """Inserta `objeto` justo después de `nodo_referencia` (o de la
        cabeza si `nodo_referencia` es None) y devuelve el nodo nuevo."""
        nuevo = NodoInventario(objeto)
        self.reinsertar_nodo(nuevo, nodo_referencia)
        return nuevo

    def _referencia_vigente(self, nodo):
        # Un pergamino excluido del retroceso pudo desaparecer entre acciones.
        while nodo is not None and nodo is not self.cabeza and not nodo.en_inventario:
            nodo = nodo.anterior
        return self.cabeza if nodo is None else nodo

    def reinsertar_nodo(self, nuevo: "NodoInventario", nodo_referencia=None):
        """Restaura el mismo nodo para conservar las referencias del historial."""
        nodo_referencia = self._referencia_vigente(nodo_referencia)
        siguiente = nodo_referencia.siguiente

        nodo_referencia.siguiente = nuevo
        nuevo.anterior = nodo_referencia
        nuevo.siguiente = siguiente
        siguiente.anterior = nuevo
        nuevo.en_inventario = True

        self.tamaño += 1
        if self.cursor is None:
            self.cursor = nuevo

    def quitar_nodo(self, nodo: "NodoInventario") -> None:
        """Desconecta `nodo` de la lista sin tocar el objeto en sí."""
        nodo.anterior.siguiente = nodo.siguiente
        nodo.siguiente.anterior = nodo.anterior
        self.tamaño -= 1
        nodo.en_inventario = False

        if self.cursor is nodo:
            if nodo.siguiente is not self.cola:
                self.cursor = nodo.siguiente
            elif nodo.anterior is not self.cabeza:
                self.cursor = nodo.anterior
            else:
                self.cursor = None

        if self.arma_equipada is nodo:
            self.arma_equipada = None
        if self.armadura_equipada is nodo:
            self.armadura_equipada = None

    def mover_despues(self, nodo: "NodoInventario", nodo_referencia: "NodoInventario") -> None:
        """Reubica `nodo` (ya en la lista) justo después de `nodo_referencia`
        sin crear ni destruir nodos."""
        nodo.anterior.siguiente = nodo.siguiente
        nodo.siguiente.anterior = nodo.anterior

        nodo_referencia = self._referencia_vigente(nodo_referencia)
        siguiente = nodo_referencia.siguiente
        nodo_referencia.siguiente = nodo
        nodo.anterior = nodo_referencia
        nodo.siguiente = siguiente
        siguiente.anterior = nodo

    # --- navegación ---

    def __iter__(self):
        nodo = self.cabeza.siguiente
        while nodo is not self.cola:
            yield nodo.objeto
            nodo = nodo.siguiente

    def seleccionar(self, id_instancia):
        nodo = self.cabeza.siguiente
        while nodo is not self.cola:
            if nodo.objeto.id_instancia == id_instancia:
                self.cursor = nodo
                return True
            nodo = nodo.siguiente
        return False

    def normalizar_cursor(self):
        if self.cursor is None or not self.cursor.en_inventario:
            self.cursor = None if self.esta_vacio() else self.cabeza.siguiente

    def avanzar(self) -> ObjetoInstancia | None:
        if self.cursor is not None and self.cursor.siguiente is not self.cola:
            self.cursor = self.cursor.siguiente
        return self.objeto_actual()

    def retroceder(self) -> ObjetoInstancia | None:
        if self.cursor is not None and self.cursor.anterior is not self.cabeza:
            self.cursor = self.cursor.anterior
        return self.objeto_actual()

    def objeto_actual(self) -> ObjetoInstancia | None:
        return self.cursor.objeto if self.cursor is not None else None

    @property
    def arma_equipada_objeto(self) -> ObjetoInstancia | None:
        """El ObjetoInstancia del arma equipada (no el nodo interno), o None.
        Para que quien calcule daño (Persona A) no tenga que conocer
        NodoInventario."""
        return self.arma_equipada.objeto if self.arma_equipada is not None else None

    @property
    def armadura_equipada_objeto(self) -> ObjetoInstancia | None:
        """Igual que arma_equipada_objeto, pero para la armadura equipada."""
        return self.armadura_equipada.objeto if self.armadura_equipada is not None else None

    # --- operaciones del jugador (§4.5, Apéndice B) ---

    def recoger(self, objeto: ObjetoInstancia) -> "NodoInventario | None":
        """Agrega `objeto` al final del orden real. Devuelve None (y no
        consume tiempo virtual: eso lo decide quien llama) si el inventario
        ya está lleno."""
        if self.esta_lleno():
            return None
        objeto.ubicacion = "inventario"
        objeto.sala = None
        return self.insertar_despues(self.cola.anterior, objeto)

    def soltar_actual(self) -> ObjetoInstancia | None:
        """Quita el objeto que se está viendo (cursor), sin importar su
        posición: O(1) porque no hay que buscarlo."""
        if self.cursor is None:
            return None
        nodo = self.cursor
        objeto = nodo.objeto
        self.quitar_nodo(nodo)
        return objeto

    def equipar_actual(self, clase: str) -> bool:
        """Mueve el objeto actual al frente del orden real y lo marca como
        equipado. `clase` la resuelve quien llama (arma/armadura) contra el
        catálogo, ya que Inventario no conoce fichas de catálogo."""
        if self.cursor is None:
            return False

        nodo = self.cursor
        self.mover_despues(nodo, self.cabeza)
        self.cursor = nodo

        if clase == "arma":
            self.arma_equipada = nodo
        elif clase == "armadura":
            self.armadura_equipada = nodo
        return True

    def contar(self, tipo_catalogo: str) -> int:
        """Cuenta cuántas instancias de un tipo hay en el inventario (p.ej.
        pergaminos de retroceso disponibles)."""
        total = 0
        nodo = self.cabeza.siguiente
        while nodo is not self.cola:
            if nodo.objeto.tipo_catalogo == tipo_catalogo:
                total += 1
            nodo = nodo.siguiente
        return total

    def quitar_primero_de_tipo(self, tipo_catalogo: str) -> ObjetoInstancia | None:
        """Consume una instancia de `tipo_catalogo` (p.ej. al usar un
        pergamino de retroceso) sin depender de la posición del cursor.
        Devuelve None si no hay ninguna."""
        nodo = self.cabeza.siguiente
        while nodo is not self.cola:
            if nodo.objeto.tipo_catalogo == tipo_catalogo:
                objeto = nodo.objeto
                self.quitar_nodo(nodo)
                return objeto
            nodo = nodo.siguiente
        return None

    # --- vistas ordenadas (§4.5, §4.9) ---

    def _recolectar(self) -> list[ObjetoInstancia]:
        elementos = []
        nodo = self.cabeza.siguiente
        while nodo is not self.cola:
            elementos.append(nodo.objeto)
            nodo = nodo.siguiente
        return elementos

    def vista_ordenada(self, clave: str, resolver_ficha, descendente: bool = False) -> list[ObjetoInstancia]:
        """
        Devuelve una lista nueva (no toca el orden real) ordenada por
        "peso", "valor" o "nombre". `resolver_ficha(tipo_catalogo)` debe
        devolver la FichaCatalogo correspondiente (la entrega quien conecte
        este módulo con red/catalogo.py).

        Usa utilidades.ordenamiento.ordenar (§4.9) en vez de sort()/sorted()
        o un algoritmo propio: es lo que pide explícitamente
        controlador/contrato.py para inventario_vista, así toda vista
        ordenada del proyecto pasa por la misma selección inserción/fusión
        medida con --bench.
        """
        from utilidades.ordenamiento import ordenar

        def valor_clave(objeto: ObjetoInstancia):
            ficha = resolver_ficha(objeto.tipo_catalogo)
            if clave == "nombre":
                return ficha.nombre
            return ficha.atributos.get(clave, 0)

        elementos = self._recolectar()
        return ordenar(elementos, clave=valor_clave, descendente=descendente)

    # --- adaptadores hacia el contrato compartido (controlador/contrato.py, modelo/snapshots.py) ---

    def _esta_equipado(self, objeto: ObjetoInstancia) -> bool:
        return objeto is self.arma_equipada_objeto or objeto is self.armadura_equipada_objeto

    def _a_item_vista(self, objeto: ObjetoInstancia, resolver_ficha) -> ItemVista:
        ficha = resolver_ficha(objeto.tipo_catalogo)
        return ItemVista(
            instancia=objeto.id_instancia,
            nombre=ficha.nombre,
            clase=ficha.clase,
            peso=ficha.atributos.get("peso", 0),
            valor=ficha.atributos.get("valor", 0),
            equipado=self._esta_equipado(objeto),
            detalle=descripcion_objeto(ficha),
            tipo=objeto.tipo_catalogo,
        )

    def vista(self, resolver_ficha, orden: str | None = None, descendente: bool = False) -> list[ItemVista]:
        """Implementa ModeloJuego.inventario_vista de controlador/contrato.py:
        orden=None -> orden real; "peso"/"valor"/"nombre" -> vista ordenada
        sin alterar el orden real (delega en vista_ordenada)."""
        elementos = (
            self.vista_ordenada(orden, resolver_ficha, descendente)
            if orden is not None
            else self._recolectar()
        )
        return [self._a_item_vista(o, resolver_ficha) for o in elementos]

    def cursor_vista(self, movimiento: str, resolver_ficha) -> ItemVista | None:
        """Implementa ModeloJuego.inventario_cursor de controlador/contrato.py.
        movimiento: "actual" | "siguiente" | "anterior"."""
        if movimiento == "siguiente":
            objeto = self.avanzar()
        elif movimiento == "anterior":
            objeto = self.retroceder()
        else:
            objeto = self.objeto_actual()
        if objeto is None:
            return None
        return self._a_item_vista(objeto, resolver_ficha)

    def a_lista_guardado(self) -> list[ItemInventarioGuardado]:
        """Orden real -> JugadorGuardado.inventario (§4.10): el primer
        elemento es el frente de la lista, tal como pide modelo/snapshots.py."""
        resultado = []
        nodo = self.cabeza.siguiente
        while nodo is not self.cola:
            resultado.append(ItemInventarioGuardado(
                instancia=nodo.objeto.id_instancia,
                tipo=nodo.objeto.tipo_catalogo,
                equipado=nodo is self.arma_equipada or nodo is self.armadura_equipada,
            ))
            nodo = nodo.siguiente
        return resultado

    def vaciar(self):
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza
        self.tamaño = 0
        self.cursor = None
        self.arma_equipada = None
        self.armadura_equipada = None

    def restaurar_desde_guardado(self, items: list[ItemInventarioGuardado], resolver_clase) -> None:
        """Inverso de a_lista_guardado(). `resolver_clase(tipo_catalogo)`
        debe devolver la `clase` de catálogo ("arma"/"armadura"/...) para
        volver a marcar qué estaba equipado, ya que ItemInventarioGuardado
        solo guarda un booleano `equipado`, no cuál puntero es."""
        self.vaciar()
        for item in items:
            objeto = ObjetoInstancia(
                id_instancia=item.instancia,
                tipo_catalogo=item.tipo,
                ubicacion="inventario",
            )
            nodo = self.insertar_despues(self.cola.anterior, objeto)
            if item.equipado:
                clase = resolver_clase(item.tipo)
                if clase == "arma":
                    self.arma_equipada = nodo
                elif clase == "armadura":
                    self.armadura_equipada = nodo
        self.cursor = self.cabeza.siguiente if self.cabeza.siguiente is not self.cola else None
