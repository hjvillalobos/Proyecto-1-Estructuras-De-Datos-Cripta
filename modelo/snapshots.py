"""
  * EstadoGuardado  -> lo que el modelo (A/C) EXPORTA para guardar la partida y lo que
                       recibe de vuelta al cargar. D lo escribe/lee en binario (§4.10).
  * EstadoVista     -> lo que el modelo ofrece para que la vista dibuje la pantalla (§10.2).
  * ResultadoAccion -> lo que devuelve el modelo tras intentar una acción del jugador.
"""
from dataclasses import dataclass, field, asdict


# Identidad de la partida (va al encabezado del log y del archivo de guardado)
@dataclass
class MetaPartida:
    cripta_id: str
    cripta_version: str
    catalogo_version: str
    semilla: int

# Estado de guardado (lo llena el modelo con exportar_estado())
@dataclass
class PuertaGuardada:
    direccion: str          # "N", "S", "E", "O"
    cerrada: bool
    abierta_con_llave: bool = False


@dataclass
class EnemigoGuardado:
    instancia: str          # ej. "e-201"
    tipo: str               # id de catálogo, ej. "ent_rata_gigante"
    vida: int
    activo: bool            # ¿ya fue activado? (§2.4)
    tiempo_siguiente: int


@dataclass
class ObjetoGuardado:
    instancia: str
    tipo: str


@dataclass
class TrampaGuardada:
    instancia: str
    tipo: str
    armada: bool


@dataclass
class SalaGuardada:
    """Todo lo dinámico que pertenece a UNA sala: se guarda en un bloque propio para
    poder leerla sin cargar el archivo completo (§4.10)."""
    sala_id: int
    rastro: int = -1        # instante en que el jugador estuvo por última vez; -1 = nunca (§2.9)
    puertas: list[PuertaGuardada] = field(default_factory=list)
    enemigos: list[EnemigoGuardado] = field(default_factory=list)
    objetos_suelo: list[ObjetoGuardado] = field(default_factory=list)
    trampas: list[TrampaGuardada] = field(default_factory=list)


@dataclass
class ItemInventarioGuardado:
    instancia: str
    tipo: str
    equipado: bool = False


@dataclass
class JugadorGuardado:
    sala_id: int
    vida: int
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    tiempo_siguiente: int
    # Orden REAL del inventario: el primer elemento es el frente de la lista (§2.7).
    inventario: list[ItemInventarioGuardado] = field(default_factory=list)
    # Campo libre para lo que A/C necesiten (ej. velocidad_base). Solo enteros.
    extras: list[int] = field(default_factory=list)


@dataclass
class EventoGuardado:
    """Un evento pendiente de la agenda (§2.3). Incluye el número de secuencia para que
    el desempate determinista sobreviva al guardado."""
    tiempo: int
    secuencia: int
    tipo: str               # "actor", "veneno", "regeneracion", "antorcha", "trampa", "puerta"...
    objetivo: str           # id de instancia (actor/trampa) o "sala:dir" para puertas
    parametros: list[int] = field(default_factory=list)


@dataclass
class EstadoGuardado:
    meta: MetaPartida
    reloj: int
    siguiente_secuencia: int        # próximo número de secuencia a asignar (§2.3)
    acciones_jugador: int
    enemigos_derrotados: int
    # Resultado de random.Random.getstate(): (version, tuple(625 ints), gauss_next).
    # Se guarda para que, tras cargar, la partida continúe con la MISMA secuencia
    # aleatoria (§2.6). El modelo hará azar.setstate(estado.rng_estado).
    rng_estado: tuple
    jugador: JugadorGuardado
    eventos: list[EventoGuardado] = field(default_factory=list)
    salas: list[SalaGuardada] = field(default_factory=list)

    #Solo para comparar contra JSON en --bench (§4.10)
    def a_dict(self):
        return asdict(self)

    @classmethod
    def desde_dict(cls, d):
        j = d["jugador"]
        jugador = JugadorGuardado(
            **{**j, "inventario": [ItemInventarioGuardado(**i) for i in j["inventario"]]})
        salas = [
            SalaGuardada(
                sala_id=s["sala_id"], rastro=s["rastro"],
                puertas=[PuertaGuardada(**p) for p in s["puertas"]],
                enemigos=[EnemigoGuardado(**e) for e in s["enemigos"]],
                objetos_suelo=[ObjetoGuardado(**o) for o in s["objetos_suelo"]],
                trampas=[TrampaGuardada(**t) for t in s["trampas"]])
            for s in d["salas"]]
        rng = d["rng_estado"]
        return cls(
            meta=MetaPartida(**d["meta"]),
            reloj=d["reloj"], siguiente_secuencia=d["siguiente_secuencia"],
            acciones_jugador=d["acciones_jugador"], enemigos_derrotados=d["enemigos_derrotados"],
            rng_estado=(rng[0], tuple(rng[1]), rng[2]),
            jugador=jugador,
            eventos=[EventoGuardado(**e) for e in d["eventos"]],
            salas=salas)


# Estado para la vista (lo llena el modelo con estado_vista())
@dataclass
class ItemVista:
    instancia: str
    nombre: str
    clase: str
    peso: int
    valor: int
    equipado: bool = False
    detalle: str = ""
    tipo: str = ""


@dataclass
class EnemigoVista:
    instancia: str
    nombre: str             
    vida: int
    vida_max: int
    tipo: str = ""
    ataque: int = 0
    defensa: int = 0
    velocidad: int = 100
    tiempo_siguiente: int = 0
    comportamiento: str = ""


@dataclass
class TrampaVista:
    instancia: str
    nombre: str
    armada: bool
    dano: int
    tipo: str = ""


@dataclass
class EventoVista:
    tiempo: int
    nombre: str


@dataclass
class SalidaVista:
    direccion: str          # "N", "S", "E", "O"
    destino: int
    cerrada: bool = False
    llave: str | None = None
    apertura_pendiente: bool = False


@dataclass
class EstadoVista:
    reloj: int
    sala_id: int
    sala_nombre: str
    salidas: list[SalidaVista]
    enemigos: list[EnemigoVista]
    objetos_suelo: list[ItemVista]
    vida: int
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    inventario_usado: int
    inventario_max: int
    efectos: list[str] = field(default_factory=list)   # ej. "veneno (faltan 120)"
    trampas: list[TrampaVista] = field(default_factory=list)
    agenda: list[EventoVista] = field(default_factory=list)
    costos: list[tuple[str, int]] = field(default_factory=list)
    arma_tipo: str | None = None
    armadura_tipo: str | None = None


@dataclass
class ResultadoAccion:
    ok: bool                # False = acción rechazada (no consume tiempo, Apéndice B)
    mensaje: str = ""


@dataclass
class ResumenPartida:
    """Datos que exige la tabla de puntajes y la verificación del replay (§2.12, §4.11)."""
    terminado: bool
    resultado: str | None   # "victoria", "derrota" o None si sigue en curso
    acciones: int
    derrotados: int
    reloj_final: int
