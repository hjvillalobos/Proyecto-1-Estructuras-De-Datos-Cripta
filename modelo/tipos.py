# modelo/tipos.py

from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class Sala:
    id: int
    nombre: str
    salidas: Dict[str, Any]
    trampa: Any = None

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

@dataclass
class ObjetoInstancia:
    id_instancia: str
    tipo_catalogo: str
    ubicacion: str
    sala: int = None

@dataclass
class Trampa:
    id_instancia: str
    tipo_catalogo: str
    armada: bool = True