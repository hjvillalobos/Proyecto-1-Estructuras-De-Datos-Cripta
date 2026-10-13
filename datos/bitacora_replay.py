import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


VERSION_FORMATO_REPLAY = 1


class ErrorReplay(Exception):
    """Error general relacionado con un replay."""


class ReplayCorrupto(ErrorReplay):
    """El archivo de replay no tiene un formato válido."""


class ReplayIncompatible(ErrorReplay):
    """El replay pertenece a versiones incompatibles."""


@dataclass(frozen=True)
class MetaReplay:
    cripta_id: str
    version_cripta: str
    version_catalogo: str
    semilla: int


@dataclass(frozen=True)
class AccionReplay:
    accion: str
    argumento: Any = None


def extraer_version(valor):
    """
    B puede devolver directamente la versión o un diccionario
    que contenga la clave 'version'.
    """
    if isinstance(valor, dict):
        return valor.get("version")

    return valor


class BitacoraReplay:
    """
    Bitácora append-only de las acciones aceptadas del jugador.

    Primera línea:
        encabezado del replay.

    Líneas siguientes:
        acciones aceptadas.
    """

    def __init__(self, ruta):
        self.ruta = Path(ruta)

    def iniciar(self, meta):
        self.ruta.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        encabezado = {
            "tipo": "encabezado",
            "formato": VERSION_FORMATO_REPLAY,
            "cripta_id": meta.cripta_id,
            "version_cripta": meta.cripta_version,
            "version_catalogo": meta.catalogo_version,
            "semilla": meta.semilla,
        }

        with self.ruta.open(
            "w",
            encoding="utf-8",
        ) as archivo:
            archivo.write(
                json.dumps(
                    encabezado,
                    ensure_ascii=False,
                )
            )
            archivo.write("\n")

    def registrar_carga(self, estado=None):
        """Anexa la base cargada; el replay no depende de un archivo mutable."""
        with self.ruta.open(
            "a",
            encoding="utf-8",
        ) as archivo:
            archivo.write(
                json.dumps({"tipo": "cargar", "estado": estado.a_dict() if estado else None})
            )
            archivo.write("\n")

    def registrar_accion(
        self,
        accion,
        argumento=None,
    ):
        registro = {
            "tipo": "accion",
            "accion": accion,
            "argumento": argumento,
        }

        with self.ruta.open(
            "a",
            encoding="utf-8",
        ) as archivo:
            archivo.write(
                json.dumps(
                    registro,
                    ensure_ascii=False,
                )
            )
            archivo.write("\n")

    def leer(self):
        if not self.ruta.exists():
            raise ReplayCorrupto(
                f"No existe el replay: {self.ruta}"
            )

        try:
            with self.ruta.open(
                "r",
                encoding="utf-8",
            ) as archivo:
                lineas = [
                    linea.strip()
                    for linea in archivo
                    if linea.strip()
                ]

        except (OSError, UnicodeError) as error:
            raise ReplayCorrupto(
                f"No se pudo leer el replay: {error}"
            ) from error

        if not lineas:
            raise ReplayCorrupto(
                "El replay está vacío."
            )

        try:
            encabezado = json.loads(
                lineas[0]
            )
        except json.JSONDecodeError as error:
            raise ReplayCorrupto(
                "El encabezado del replay no es JSON válido."
            ) from error

        if not isinstance(encabezado, dict):
            raise ReplayCorrupto("El encabezado debe ser un objeto JSON.")
        if encabezado.get("tipo") != "encabezado":
            raise ReplayCorrupto(
                "Falta el encabezado del replay."
            )

        if (
            encabezado.get("formato")
            != VERSION_FORMATO_REPLAY
        ):
            raise ReplayIncompatible(
                "Versión del formato de replay incompatible."
            )

        campos = (
            "cripta_id",
            "version_cripta",
            "version_catalogo",
            "semilla",
        )

        for campo in campos:
            if campo not in encabezado:
                raise ReplayCorrupto(
                    f"Falta '{campo}' en el encabezado."
                )

        for campo in campos[:-1]:
            if not isinstance(encabezado[campo], str) or not encabezado[campo].strip():
                raise ReplayCorrupto(f"Campo '{campo}' invalido en el encabezado.")
        if type(encabezado["semilla"]) is not int:
            raise ReplayCorrupto("La semilla debe ser un entero.")

        meta = MetaReplay(
            cripta_id=str(
                encabezado["cripta_id"]
            ),
            version_cripta=str(
                encabezado["version_cripta"]
            ),
            version_catalogo=str(
                encabezado["version_catalogo"]
            ),
            semilla=int(
                encabezado["semilla"]
            ),
        )

        acciones = []

        for numero, linea in enumerate(
            lineas[1:],
            start=2,
        ):
            try:
                registro = json.loads(
                    linea
                )
            except json.JSONDecodeError as error:
                raise ReplayCorrupto(
                    f"Línea {numero} inválida."
                ) from error

            if not isinstance(registro, dict):
                raise ReplayCorrupto(f"Linea {numero}: se esperaba un objeto JSON.")
            if registro.get("tipo") == "cargar":
                if not isinstance(registro.get("estado"), dict):
                    raise ReplayIncompatible("La carga no contiene el estado necesario para reproducirla.")
                acciones.append(AccionReplay("cargar", registro["estado"]))
                continue

            if registro.get("tipo") != "accion":
                raise ReplayCorrupto(
                    f"Línea {numero}: "
                    "se esperaba una acción."
                )

            accion = registro.get(
                "accion"
            )

            if not isinstance(
                accion,
                str,
            ) or not accion:
                raise ReplayCorrupto(
                    f"Línea {numero}: "
                    "acción inválida."
                )

            if registro.get("argumento") is not None and not isinstance(registro["argumento"], str):
                raise ReplayCorrupto(f"Linea {numero}: argumento invalido.")
            acciones.append(
                AccionReplay(
                    accion=accion,
                    argumento=registro.get(
                        "argumento"
                    ),
                )
            )

        return meta, acciones


def aplicar_accion_replay(juego, accion):
    if accion.accion == "cargar":
        from modelo.snapshots import EstadoGuardado, ResultadoAccion
        try:
            juego.restaurar_estado(EstadoGuardado.desde_dict(accion.argumento))
        except (ValueError, TypeError, KeyError, IndexError) as error:
            raise ReplayIncompatible(f"No se puede restaurar la carga del replay: {error}") from error
        return ResultadoAccion(ok=True)
    return juego.ejecutar(accion.accion, accion.argumento)


def reproducir(
    ruta,
    fuente,
    fabrica_juego,
    notificar=None,
    al_paso=None,
):
    """
    Reconstruye una partida utilizando la misma cripta,
    versiones y semilla, y ejecuta las acciones sin pedir
    entrada al usuario.
    """

    bitacora = BitacoraReplay(
        ruta
    )

    meta, acciones = bitacora.leer()

    version_cripta_actual = extraer_version(
        fuente.obtener_version_cripta(
            meta.cripta_id
        )
    )

    version_catalogo_actual = extraer_version(
        fuente.obtener_version_catalogo()
    )

    if (
        str(version_cripta_actual)
        != meta.version_cripta
    ):
        raise ReplayIncompatible(
            "La versión actual de la cripta "
            "no coincide con la del replay."
        )

    if (
        str(version_catalogo_actual)
        != meta.version_catalogo
    ):
        raise ReplayIncompatible(
            "La versión actual del catálogo "
            "no coincide con la del replay."
        )

    if notificar is None:
        notificar = lambda mensaje: None

    juego = fabrica_juego(
        fuente,
        meta.cripta_id,
        meta.semilla,
        notificar,
    )

    if al_paso is not None:
        al_paso(
            juego,
            None,
            None,
        )

    for accion in acciones:
        resultado = aplicar_accion_replay(juego, accion)

        if not resultado.ok:
            raise ReplayCorrupto(
                "El replay contiene una acción "
                f"que no pudo reproducirse: "
                f"{accion.accion!r} "
                f"{accion.argumento!r}. "
                f"{resultado.mensaje}"
            )

        if al_paso is not None:
            al_paso(
                juego,
                accion,
                resultado,
            )

    return juego
