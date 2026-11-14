"""Fundamentos, búsqueda limitada y contexto de rutas reales de A.

Precondición del grafo: salas/IDs únicos y destinos existentes, costos válidos
positivos y simétricos. No define políticas de datos inválidos de B (Q1/Q2).
"""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class ArcoTerreno:
    origen: int
    destino: int
    direccion: str
    costo: int
    puerta: object


class EstadoEmparejamiento(Enum):
    EMPAREJADA = "emparejada"
    SIN_RETORNO = "sin_retorno"
    AMBIGUA = "ambigua"


@dataclass(frozen=True, slots=True)
class EmparejamientoSalida:
    estado: EstadoEmparejamiento
    retorno: tuple[int, str] | None = None


def _ordenar_salas(salas):
    """Fusión iterativa propia: O(V log V), auxiliar O(V), sin mutar entrada."""
    origen = list(salas)
    cantidad = len(origen)
    destino = [None] * cantidad
    ancho = 1
    while ancho < cantidad:
        for inicio in range(0, cantidad, ancho * 2):
            medio = min(inicio + ancho, cantidad)
            fin = min(inicio + ancho * 2, cantidad)
            izquierda, derecha = inicio, medio
            for posicion in range(inicio, fin):
                if izquierda < medio and (derecha == fin or
                        origen[izquierda].id <= origen[derecha].id):
                    destino[posicion] = origen[izquierda]
                    izquierda += 1
                else:
                    destino[posicion] = origen[derecha]
                    derecha += 1
        origen, destino = destino, origen
        ancho *= 2
    return origen


class GrafoTerreno:
    """Índices densos y vecinos resueltos; no conserva índices hash.

    Preparación O(V log V + E log V), espacio O(V+E). Los descriptores
    JSON existentes solo se leen; puerta referencia el descriptor original.
    No se filtran puertas ni se ejecutan efectos. El llamador no debe mutar
    ids/adyacencias después de preparar el grafo.
    """

    def __init__(self, salas):
        ordenadas = _ordenar_salas(salas)
        self.ids = [sala.id for sala in ordenadas]
        self.adyacencias = [[] for _ in ordenadas]
        for origen, sala in enumerate(ordenadas):
            for direccion, salida in sala.salidas.items():
                destino = self.indice(salida["sala"])
                self.adyacencias[origen].append(ArcoTerreno(
                    origen, destino, direccion, salida.get("costo", 100), salida,
                ))

    def indice(self, identificador):
        """Búsqueda binaria propia O(log V), para un ID del grafo preparado."""
        izquierda, derecha = 0, len(self.ids)
        while izquierda < derecha:
            medio = (izquierda + derecha) // 2
            if self.ids[medio] < identificador:
                izquierda = medio + 1
            else:
                derecha = medio
        if izquierda == len(self.ids) or self.ids[izquierda] != identificador:
            raise LookupError("El ID no pertenece al grafo preparado")
        return izquierda

    def resolver_retorno(self, sala_id, direccion):
        """Resuelve extremos por topología, sin inferir una identidad de puerta.

        Exige unicidad en ambos sentidos. No usa la dirección opuesta, el
        costo, la llave ni el estado de apertura para decidir entre candidatas.
        """
        origen = self.indice(sala_id)
        salidas = self.adyacencias[origen]
        arco = next((salida for salida in salidas if salida.direccion == direccion), None)
        if arco is None:
            raise LookupError("La dirección no pertenece a la sala indicada")

        retornos = [salida for salida in self.adyacencias[arco.destino]
                    if salida.destino == origen and salida is not arco]
        if not retornos:
            return EmparejamientoSalida(EstadoEmparejamiento.SIN_RETORNO)
        if (origen == arco.destino or len(retornos) != 1
                or sum(salida.destino == arco.destino for salida in salidas) != 1):
            return EmparejamientoSalida(EstadoEmparejamiento.AMBIGUA)
        return EmparejamientoSalida(EstadoEmparejamiento.EMPAREJADA,
                                   (self.ids[arco.destino], retornos[0].direccion))


class EspacioBusqueda:
    """Auxiliares O(V) reservados una vez; una generación habilita cada valor.

    Un espacio pertenece a una sola frontera y no se comparte entre consultas
    simultáneas. Sus generaciones son locales, ajenas a eventos y azar del motor.
    """

    def __init__(self, ids):
        self.ids = list(ids)
        cantidad = len(self.ids)
        self.generacion = 0
        self._marcas = [-1] * cantidad
        self._distancias = [0] * cantidad
        self._primeros = [None] * cantidad
        self._posiciones = [-1] * cantidad
        self._cerrados = [-1] * cantidad

    def etiqueta(self, indice):
        if self._marcas[indice] != self.generacion:
            return None
        return self._distancias[indice], self._primeros[indice]

    def posicion(self, indice):
        if self._marcas[indice] != self.generacion:
            return -1
        return self._posiciones[indice]

    def cerrar(self, indice):
        self._cerrados[indice] = self.generacion

    def esta_cerrado(self, indice):
        return self._cerrados[indice] == self.generacion

    def _registrar(self, indice, distancia, primer_id):
        self._marcas[indice] = self.generacion
        self._distancias[indice] = distancia
        self._primeros[indice] = primer_id


class HeapRutas:
    """Min-heap indexado propio; insertar/disminuir/extraer O(log(F+1)).

    F es el tamaño de frontera. Un nodo ocupa una sola posición; prioridades
    (distancia, primer ID, ID de sala). None marca el origen, precede a IDs
    a igual distancia y no inventa un ID de juego. No decide rutas ni rangos.
    """

    def __init__(self, espacio):
        self.espacio = espacio
        self._nodos = []

    def __len__(self):
        return len(self._nodos)

    def iniciar(self):
        """O(1) operaciones de arreglos; nunca barre V ni limpia trabajo previo."""
        if self._nodos:
            raise RuntimeError("Finalice la frontera anterior antes de iniciar otra")
        self.espacio.generacion += 1

    @staticmethod
    def _clave_etiqueta(distancia, primer_id):
        primero = (0, 0) if primer_id is None else (1, primer_id)
        return distancia, primero

    def _clave(self, indice):
        # Los nodos del heap siempre tienen etiqueta de la generación vigente.
        espacio = self.espacio
        primero = espacio._primeros[indice]
        return espacio._distancias[indice], primero is not None, primero, espacio.ids[indice]

    def _intercambiar(self, primera, segunda):
        self._nodos[primera], self._nodos[segunda] = (
            self._nodos[segunda], self._nodos[primera],
        )
        self.espacio._posiciones[self._nodos[primera]] = primera
        self.espacio._posiciones[self._nodos[segunda]] = segunda

    def _subir(self, posicion):
        clave = self._clave(self._nodos[posicion])
        while posicion > 0:
            padre = (posicion - 1) // 2
            if self._clave(self._nodos[padre]) <= clave:
                break
            self._intercambiar(posicion, padre)
            posicion = padre

    def _bajar(self, posicion):
        cantidad = len(self._nodos)
        clave = self._clave(self._nodos[posicion])
        while posicion * 2 + 1 < cantidad:
            hijo = posicion * 2 + 1
            clave_hijo = self._clave(self._nodos[hijo])
            if hijo + 1 < cantidad:
                clave_derecha = self._clave(self._nodos[hijo + 1])
                if clave_derecha < clave_hijo:
                    hijo += 1
                    clave_hijo = clave_derecha
            if clave <= clave_hijo:
                break
            self._intercambiar(posicion, hijo)
            posicion = hijo

    def insertar_o_disminuir(self, indice, distancia, primer_id):
        """Registra solo mejoras lexicográficas; retorna si hubo mejora.

        Índices y etiquetas son internos válidos del algoritmo consumidor.
        No es validación de los datos de entrada del servicio de B.
        """
        espacio = self.espacio
        anterior = espacio.etiqueta(indice)
        if anterior is not None and self._clave_etiqueta(*anterior) <= (
                self._clave_etiqueta(distancia, primer_id)):
            return False
        posicion = espacio.posicion(indice)
        espacio._registrar(indice, distancia, primer_id)
        if posicion == -1:
            posicion = len(self._nodos)
            self._nodos.append(indice)
            espacio._posiciones[indice] = posicion
        self._subir(posicion)
        return True

    def extraer(self):
        """Retorna (índice, distancia, primer ID); cerrar el nodo es explícito."""
        if not self._nodos:
            raise IndexError("La frontera está vacía")
        menor = self._nodos[0]
        ultimo = self._nodos.pop()
        self.espacio._posiciones[menor] = -1
        if self._nodos:
            self._nodos[0] = ultimo
            self.espacio._posiciones[ultimo] = 0
            self._bajar(0)
        return (menor,) + self.espacio.etiqueta(menor)

    def finalizar(self):
        """Descarta F pendientes en O(F), imputados a la consulta que termina.

        La siguiente iniciar() exige frontera vacía; no carga limpieza de una
        consulta grande a otra pequeña. Los auxiliares O(V) no se recorren.
        """
        while self._nodos:
            self.espacio._posiciones[self._nodos.pop()] = -1


class ContextoRutasReales:
    """Grafo de la partida y auxiliares reutilizables, sin guardar resultados."""

    def __init__(self, salas):
        self.grafo = GrafoTerreno(salas)
        self._espacio = EspacioBusqueda(self.grafo.ids)
        self._frontera = HeapRutas(self._espacio)

    def buscar(self, origen_indice, destino_indice, limite):
        return buscar_ruta(self.grafo, self._espacio, self._frontera,
                           origen_indice, destino_indice, limite)

    def descartar_derivados(self):
        """Invalida las marcas en O(1) entre consultas, conservando los arreglos."""
        self._frontera.iniciar()


def buscar_ruta(grafo, espacio, frontera, origen_indice, destino_indice, limite):
    """Dijkstra: (primer índice, dirección, costo del paso, total).

    Entrada interna válida: índices distintos del mismo grafo/espacio,
    frontera asociada vacía y costos positivos. Un límite entero válido
    es inclusivo y None explícito permite buscar sin tope de costo.
    Retorna None si no encuentra paso admisible; no certifica distancia
    fuera de un límite finito ni define llegada, datos inválidos o
    contratos compartidos.
    """
    frontera.iniciar()
    try:
        frontera.insertar_o_disminuir(origen_indice, 0, None)
        while frontera:
            actual, distancia, primer_id = frontera.extraer()
            espacio.cerrar(actual)
            if actual == destino_indice:
                primer_arco = None
                for arco in grafo.adyacencias[origen_indice]:
                    if (grafo.ids[arco.destino] == primer_id
                            and not arco.puerta.get("cerrada", False)
                            and (primer_arco is None or arco.costo < primer_arco.costo)):
                        primer_arco = arco
                if primer_arco is not None:
                    return (primer_arco.destino, primer_arco.direccion,
                            primer_arco.costo, distancia)
                return None

            for arco in grafo.adyacencias[actual]:
                if (arco.puerta.get("cerrada", False)
                        or espacio.esta_cerrado(arco.destino)):
                    continue
                candidata = distancia + arco.costo
                if limite is not None and candidata > limite:
                    continue
                primero = grafo.ids[arco.destino] if actual == origen_indice else primer_id
                frontera.insertar_o_disminuir(arco.destino, candidata, primero)
        return None
    finally:
        frontera.finalizar()


class ContextoRutasCompartidas(ContextoRutasReales):
    """Comparte rangos ilimitados; los rangos pequeños mantienen localidad."""
    def __init__(self, salas):
        super().__init__(salas)
        from modelo.rutas_compartidas import RutasCompartidas
        self._compartido = RutasCompartidas(self.grafo)
        self.frontera_activa = False
        self._firma = None

    def invalidar_puertas(self):
        self._firma = None
        self._compartido.clave = None

    def buscar(self, origen_indice, destino_indice, limite):
        if limite is not None:
            return super().buscar(origen_indice, destino_indice, limite)
        puertas = self._firma if self.frontera_activa else None
        if puertas is None:
            puertas = tuple(a.puerta.get('cerrada', False)
                            for fila in self.grafo.adyacencias for a in fila)
            if self.frontera_activa:
                self._firma = puertas
        return self._compartido.buscar(origen_indice, destino_indice, limite, puertas)

    def descartar_derivados(self):
        super().descartar_derivados()
        self.invalidar_puertas()
