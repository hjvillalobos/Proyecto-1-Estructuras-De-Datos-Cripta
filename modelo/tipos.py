# modelo/tipos.py

from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass(init=False)
class Sala:
    id: int
    nombre: str
    salidas: Dict[str, Any]
    trampas: List[Any]

    def __init__(self, id, nombre, salidas, trampa=None, trampas=None):
        self.id, self.nombre, self.salidas = id, nombre, salidas
        self.trampas = list(trampas) if trampas is not None else ([trampa] if trampa else [])

    @property
    def trampa(self):
        return self.trampas[0] if self.trampas else None

    @trampa.setter
    def trampa(self, valor):
        self.trampas = [valor] if valor is not None else []

@dataclass(kw_only=True)
class Actor:
    vida: int
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    tiempo_siguiente: int
    evento_pendiente: Any = None
    veneno: Any = None
    evento_velocidad: Any = None
@dataclass(kw_only=True)
class Jugador(Actor):
    inventario: Any
    posicion_actual: int
    llaves_obtenidas: List[str]

@dataclass(kw_only=True)
class InstanciaEnemigo(Actor):
    id_instancia: str
    tipo_catalogo: str
    comportamiento: str
    sala_actual: int = None        # reemplaza el dict sala_de_enemigo

@dataclass
class FichaCatalogo:
    id: str
    clase: str
    nombre: str
    atributos: Dict[str, Any]

@dataclass
class Evento:
    tiempo: int
    secuencia: int
    tipo: str
    referencia: Any
    cancelado: bool = False
    en_cola: bool = False

@dataclass
class ObjetoInstancia:
    id_instancia: str
    tipo_catalogo: str
    ubicacion: str
    sala: int = None
    encendida: bool = False

@dataclass
class Trampa:
    id_instancia: str
    tipo_catalogo: str
    armada: bool = True
