# modelo/tipos.py

from dataclasses import dataclass
from typing import Dict, Any, List

# 1. Definición de la Sala
@dataclass
class Sala:
    id: int
    nombre: str
    salidas: Dict[str, Any]  # Ej: {"N": {"sala": 2, "cerrada": True, "llave": "itm_llave_bronce"}}
    trampa: Any = None

# 2. Definición del Actor base
@dataclass
class Actor:
    vida: int
    vida_max: int
    ataque: int
    defensa: int
    velocidad: int
    tiempo_siguiente: int

# 3. Herencia: El Jugador hereda de Actor
@dataclass
class Jugador(Actor):
    inventario: Any  # Referencia a la estructura del inventario de Persona C
    posicion_actual: int  # ID de la sala actual
    llaves_obtenidas: List[str]

# 4. Herencia: Los enemigos también heredan de Actor
@dataclass
class InstanciaEnemigo(Actor):
    id_instancia: str
    tipo_catalogo: str   # Referencia al ID en el catálogo
    comportamiento: str  # "guardian", "errante" o "rastreador"

# 5. Ficha del catálogo (Datos compartidos por clase de objeto/enemigo)
@dataclass
class FichaCatalogo:
    id: str
    clase: str      # "enemigo", "arma", "pocion", etc.
    nombre: str
    # Los demás atributos dependen del tipo, puedes usar un dict para los datos extra
    atributos: Dict[str, Any]

# 6. Evento programado en el reloj virtual
@dataclass
class Evento:
    tiempo: int              # instante del reloj virtual en que debe ejecutarse
    secuencia: int           # desempate determinista si el tiempo coincide con otro evento
    tipo: str                # ej: "accion_jugador", "ataque_enemigo", "veneno", "cierre_puerta"
    referencia: Any          # el actor o efecto al que pertenece (para poder cancelarlo o reprogramarlo)
    cancelado: bool = False  # invalidación perezosa: se marca así en lugar de borrarlo del heap

# 7. Instancia de un objeto en el mundo (inventario o suelo de una sala)
@dataclass
class ObjetoInstancia:
    id_instancia: str        # identificador único de esta instancia concreta
    tipo_catalogo: str       # referencia al id en el catálogo (ej: "itm_daga_oxidada")
    ubicacion: str           # "inventario" o "suelo"
    sala: int = None         # id de la sala, solo si ubicacion == "suelo"