"""Conocimiento local del jugador (002-niebla-viaje, incremento I1).

Recibe observaciones, nunca consulta el estado real de una puerta. No conecta
todavía el motor, antorcha, viaje ni guardado. Los IDs externos se traducen a
posiciones compactas mediante búsqueda binaria propia.
"""
from dataclasses import dataclass

from utilidades.ordenamiento import ordenar

DESCONOCIDA, AVISTADA, EXPLORADA = 0, 1, 2


@dataclass(frozen=True)
class SalidaConocible:
    direccion: str
    destino: int
    costo: int
    puerta: int | None = None


@dataclass(frozen=True)
class SalaConocible:
    id: int
    nombre: str
    salidas: tuple[SalidaConocible, ...]


@dataclass(frozen=True)
class PuertaConocible:
    id: int
    extremo_a: int
    extremo_b: int


@dataclass(frozen=True)
class CambioConocimiento:
    ambito: str
    id: int
    anterior: int | bool | None
    nuevo: int | bool | None


def _id_valido(valor):
    return type(valor) is int and valor >= 0


def _indice(ids, identificador):
    if not _id_valido(identificador):
        raise ValueError("El identificador debe ser un entero no negativo.")
    inicio, fin = 0, len(ids)
    while inicio < fin:
        medio = (inicio + fin) // 2
        if ids[medio] < identificador:
            inicio = medio + 1
        else:
            fin = medio
    if inicio == len(ids) or ids[inicio] != identificador:
        raise ValueError("Identificador no disponible en este esqueleto.")
    return inicio


def _preparar(entidades, tipo):
    elementos = list(entidades)
    for elemento in elementos:
        if type(elemento) is not tipo or not _id_valido(elemento.id):
            raise ValueError("Entidad o identificador inválido.")
    elementos = ordenar(elementos, clave=lambda e: e.id, algoritmo="fusion")
    ids = [elemento.id for elemento in elementos]
    for i in range(1, len(ids)):
        if ids[i - 1] == ids[i]:
            raise ValueError("Identificador duplicado.")
    return tuple(elementos), tuple(ids)


class ConocimientoMapa:
    """FR-001–005, FR-014 local, FR-017. Sin estado de posición o reloj.

    El llamador garantiza que la sala de una observación es la ocupada.
    Entrar no observa puertas automáticamente: sus estados llegan por separado.
    """

    def __init__(self, salas, puertas, sala_inicial):
        self._salas, self._ids = _preparar(salas, SalaConocible)
        self._puertas, self._ids_puertas = _preparar(puertas, PuertaConocible)
        self._estados = [DESCONOCIDA] * len(self._salas)
        self._recuerdos = [None] * len(self._puertas)
        self._revision = 0
        for puerta in self._puertas:
            _indice(self._ids, puerta.extremo_a)
            _indice(self._ids, puerta.extremo_b)
            if puerta.extremo_a == puerta.extremo_b:
                raise ValueError("La puerta requiere dos extremos distintos.")
        self._salidas = []
        for sala in self._salas:
            if type(sala.nombre) is not str or type(sala.salidas) is not tuple:
                raise ValueError("Nombre y salidas deben ser texto y tupla.")
            for salida in sala.salidas:
                if (type(salida) is not SalidaConocible
                        or type(salida.direccion) is not str or not salida.direccion
                        or type(salida.costo) is not int or salida.costo < 1):
                    raise ValueError("Salida inválida: dirección y costo positivo requeridos.")
            salidas = ordenar(sala.salidas, clave=lambda s: s.direccion, algoritmo="fusion")
            preparadas = []
            anterior = None
            for salida in salidas:
                if salida.direccion == anterior:
                    raise ValueError("Dirección duplicada en la sala.")
                anterior = salida.direccion
                destino = _indice(self._ids, salida.destino)
                puerta_indice = None
                if salida.puerta is not None:
                    puerta_indice = _indice(self._ids_puertas, salida.puerta)
                    puerta = self._puertas[puerta_indice]
                    if not ((sala.id == puerta.extremo_a and salida.destino == puerta.extremo_b)
                            or (sala.id == puerta.extremo_b and salida.destino == puerta.extremo_a)):
                        raise ValueError("La salida no conecta los extremos de su puerta.")
                preparadas.append((salida, destino, puerta_indice))
            self._salidas.append(tuple(preparadas))
        self.entrar(sala_inicial)

    @property
    def revision(self):
        """Marca local de invalidación; no es tiempo ni estado de partida."""
        return self._revision

    def estado_sala(self, sala_id):
        try:
            posicion = _indice(self._ids, sala_id)
        except ValueError:
            if not _id_valido(sala_id):
                raise
            return DESCONOCIDA
        return self._estados[posicion]

    def recuerdo_puerta(self, puerta_id):
        return self._recuerdos[_indice(self._ids_puertas, puerta_id)]

    def entrar(self, sala_id):
        """Explora una sala y avista sus destinos: O(log V + grado)."""
        posicion = _indice(self._ids, sala_id)
        cambios = []
        self._cambiar_sala(posicion, EXPLORADA, cambios)
        for _, destino, _ in self._salidas[posicion]:
            if self._estados[destino] == DESCONOCIDA:
                self._cambiar_sala(destino, AVISTADA, cambios)
        return tuple(cambios)

    def _cambiar_sala(self, posicion, nuevo, cambios):
        anterior = self._estados[posicion]
        if anterior != nuevo:
            cambios.append(CambioConocimiento("sala", self._ids[posicion], anterior, nuevo))
            self._estados[posicion] = nuevo
            self._revision += 1

    def observar_puerta(self, sala_id, puerta_id, cerrada):
        if type(cerrada) is not bool:
            raise ValueError("La observación debe indicar abierta o cerrada.")
        posicion = _indice(self._ids_puertas, puerta_id)
        sala = _indice(self._ids, sala_id)
        puerta = self._puertas[posicion]
        if (sala_id not in (puerta.extremo_a, puerta.extremo_b)
                or self._estados[sala] != EXPLORADA):
            raise ValueError("La observación requiere un extremo explorado.")
        anterior = self._recuerdos[posicion]
        if anterior is cerrada:
            return ()
        self._recuerdos[posicion] = cerrada
        self._revision += 1
        return (CambioConocimiento("puerta", puerta_id, anterior, cerrada),)

    def mapa_conocido(self):
        """Proyección de datos; no es la fachada de líneas de la interfaz."""
        resultado = []
        for i, sala in enumerate(self._salas):
            estado = self._estados[i]
            if estado == DESCONOCIDA:
                continue
            if estado == AVISTADA:
                resultado.append((sala.id, estado, None, ()))
                continue
            salidas = []
            for salida, _, puerta in self._salidas[i]:
                recuerdo = False if puerta is None else self._recuerdos[puerta]
                salidas.append((salida.direccion, salida.destino, salida.costo,
                                salida.puerta, recuerdo))
            resultado.append((sala.id, estado, sala.nombre, tuple(salidas)))
        return tuple(resultado)

    def aplicar(self, cambios):
        self._procesar(cambios, False)

    def revertir(self, cambios):
        self._procesar(cambios, True)

    def _procesar(self, cambios, inverso):
        if type(cambios) is not tuple:
            raise ValueError("Un lote de cambios debe ser una tupla.")
        aplicados = []
        secuencia = reversed(cambios) if inverso else iter(cambios)
        try:
            for cambio in secuencia:
                if type(cambio) is not CambioConocimiento:
                    raise ValueError("Cambio inválido.")
                if cambio.ambito == "sala":
                    for valor in (cambio.anterior, cambio.nuevo):
                        if type(valor) is not int or valor not in (0, 1, 2):
                            raise ValueError("Estado de sala inválido.")
                    valores, ids = self._estados, self._ids
                elif cambio.ambito == "puerta":
                    for valor in (cambio.anterior, cambio.nuevo):
                        if valor is not None and type(valor) is not bool:
                            raise ValueError("Recuerdo de puerta inválido.")
                    valores, ids = self._recuerdos, self._ids_puertas
                else:
                    raise ValueError("Ámbito de cambio inválido.")
                posicion = _indice(ids, cambio.id)
                anterior, nuevo = ((cambio.nuevo, cambio.anterior) if inverso
                                   else (cambio.anterior, cambio.nuevo))
                if valores[posicion] != anterior:
                    raise ValueError("El lote no corresponde al estado actual.")
                aplicados.append((valores, posicion, anterior))
                valores[posicion] = nuevo
                if anterior != nuevo:
                    self._revision += 1
        except Exception:
            for valores, posicion, anterior in reversed(aplicados):
                if valores[posicion] != anterior:
                    self._revision += 1
                valores[posicion] = anterior
            raise
