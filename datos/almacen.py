import json
import os
from pathlib import Path
import tempfile

from red.errores import DatosInvalidos, DatosNoDisponibles
from red.validacion import identificador


class AlmacenLocal:
    def __init__(self, carpeta=".cache/cripta"):
        self.carpeta = Path(carpeta)

    def _nombre(self, valor):
        return identificador(str(valor)).encode("utf-8").hex()

    def _leer(self, ruta):
        try:
            with ruta.open(encoding="utf-8") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return None
        except (OSError, ValueError) as error:
            raise DatosInvalidos(f"No se puede leer {ruta}: {error}") from error

    def _guardar(self, ruta, datos):
        temporal = None
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=ruta.parent,
                                             suffix=".tmp", delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump(datos, archivo, ensure_ascii=False, allow_nan=False)
            os.replace(temporal, ruta)
        except (OSError, ValueError, TypeError) as error:
            raise DatosNoDisponibles(f"No se puede guardar {ruta}: {error}") from error
        finally:
            if temporal is not None and temporal.exists():
                temporal.unlink()

    def leer_lista(self):
        return self._leer(self.carpeta / "criptas.json")

    def guardar_lista(self, datos):
        self._guardar(self.carpeta / "criptas.json", datos)

    def _cripta(self, cripta, version):
        return self.carpeta / "criptas" / self._nombre(cripta) / self._nombre(version)

    def leer_generales(self, cripta, version=None):
        if version is None:
            dato = self._leer(self.carpeta / "criptas" / self._nombre(cripta) / "actual.json")
            if dato is None:
                return None
            version = dato.get("version") if isinstance(dato, dict) else None
            identificador(version)
        return self._leer(self._cripta(cripta, version) / "general.json")

    def guardar_generales(self, datos):
        self._guardar(self._cripta(datos["id"], datos["version"]) / "general.json", datos)
        self._guardar(self.carpeta / "criptas" / self._nombre(datos["id"]) / "actual.json",
                      {"version": datos["version"]})

    def leer_pagina(self, cripta, version, pagina):
        return self._leer(self._cripta(cripta, version) / "paginas" / f"{int(pagina)}.json")

    def guardar_pagina(self, cripta, version, datos):
        self._guardar(self._cripta(cripta, version) / "paginas" / f"{int(datos['pagina'])}.json", datos)

    def leer_contenido(self, cripta, version, sala):
        return self._leer(self._cripta(cripta, version) / "contenido" / f"{int(sala)}.json")

    def guardar_contenido(self, cripta, version, datos):
        self._guardar(self._cripta(cripta, version) / "contenido" / f"{int(datos['sala'])}.json", datos)

    def leer_version_catalogo(self):
        datos = self._leer(self.carpeta / "catalogo" / "actual.json")
        if datos is None:
            return None
        return identificador(datos.get("version") if isinstance(datos, dict) else None)

    def guardar_version_catalogo(self, version):
        self._guardar(self.carpeta / "catalogo" / self._nombre(version) / "version.json",
                      {"version": version})
        self._guardar(self.carpeta / "catalogo" / "actual.json", {"version": version})

    def tiene_version_catalogo(self, version):
        datos = self._leer(self.carpeta / "catalogo" / self._nombre(version) / "version.json")
        return isinstance(datos, dict) and datos.get("version") == version

    def leer_ficha(self, version, clave):
        ruta = self.carpeta / "catalogo" / self._nombre(version) / f"{self._nombre(clave)}.json"
        return self._leer(ruta)

    def guardar_ficha(self, version, datos):
        ruta = self.carpeta / "catalogo" / self._nombre(version) / f"{self._nombre(datos['id'])}.json"
        self._guardar(ruta, datos)
