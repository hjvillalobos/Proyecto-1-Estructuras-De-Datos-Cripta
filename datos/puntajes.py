"""

Cada partida terminada agrega UNA línea JSON al archivo (append-only, una línea por partida):
nombre, id y versión de la cripta, acciones, enemigos derrotados y tiempo final del reloj.

Ranking: primero las victorias; luego menor tiempo final; luego menos acciones.
Como los registros llegan en orden cronológico (no por puntaje), el ranking usa el
ordenamiento automático de utilidades/ordenamiento.py.
"""
import json
import os
from dataclasses import dataclass, asdict

from utilidades.ordenamiento import ordenar


@dataclass
class RegistroPuntaje:
    nombre: str
    cripta_id: str
    cripta_version: str
    acciones: int
    derrotados: int
    tiempo_final: int
    resultado: str            # "victoria", "derrota" o "abandono"

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip()
               for v in (self.nombre, self.cripta_id, self.cripta_version)):
            raise ValueError("Identidad de puntaje invalida.")
        if any(type(v) is not int or v < 0 for v in (self.acciones, self.derrotados, self.tiempo_final)):
            raise ValueError("Contadores de puntaje invalidos.")
        if self.resultado not in ("victoria", "derrota", "abandono"):
            raise ValueError("Resultado de puntaje invalido.")


def _clave_ranking(r: RegistroPuntaje):
    # Tupla comparable: victoria (0) antes que lo demás (1), luego tiempo, luego acciones.
    return (0 if r.resultado == "victoria" else 1, r.tiempo_final, r.acciones)


class TablaPuntajes:
    def __init__(self, ruta):
        self.ruta = ruta
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

    def registrar(self, registro: RegistroPuntaje):
        with open(self.ruta, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(registro), ensure_ascii=False) + "\n")

    def cargar(self):
        if not os.path.exists(self.ruta):
            return []
        registros = []
        with open(self.ruta, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    registros.append(RegistroPuntaje(**json.loads(linea)))
                except (ValueError, TypeError):
                    continue                    # una línea dañada no debe tumbar el ranking
        return registros

    def ranking(self, cripta_id=None, limite=10):
        registros = self.cargar()
        if cripta_id is not None:
            registros = [r for r in registros if r.cripta_id == cripta_id]
        return ordenar(registros, clave=_clave_ranking)[:limite]
