"""Preferencia cosmetica local; nunca forma parte del estado del motor."""
import json
import os
from pathlib import Path
import tempfile

PERSONAJES = (("jugador", "Tigre"), ("tigresa", "Tigresa"))
RUTA_PREFERENCIA = Path("datos_generados/personaje_visual.json")


def validar_personaje(personaje):
    if personaje not in dict(PERSONAJES):
        raise ValueError(f"Personaje desconocido: {personaje!r}")
    return personaje


def leer_personaje(ruta=RUTA_PREFERENCIA):
    try:
        return validar_personaje(json.loads(Path(ruta).read_text(encoding="utf-8"))["personaje"])
    except (OSError, ValueError, KeyError, TypeError):
        return "jugador"


def guardar_personaje(personaje, ruta=RUTA_PREFERENCIA):
    validar_personaje(personaje)
    ruta = Path(ruta)
    temporal = None
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=ruta.parent,
                                         suffix=".tmp", delete=False) as archivo:
            temporal = Path(archivo.name)
            json.dump({"personaje": personaje}, archivo)
        os.replace(temporal, ruta)
    except OSError:
        pass  # La eleccion sigue vigente en la ventana aunque no se pueda guardar.
    finally:
        if temporal is not None:
            try:
                temporal.unlink(missing_ok=True)
            except OSError:
                pass
