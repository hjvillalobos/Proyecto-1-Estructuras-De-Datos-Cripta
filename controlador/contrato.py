"""
OCUPO A A Y C PARA EL CONTRATO

    ModeloJuego  -> lo implementa el modelo (PERSONA A + C).  Ej.: modelo/juego.py
    FuenteDatos  -> lo implementa PERSONA B (cliente HTTP / offline + caché).
    crear_juego  -> función fábrica que A expone para arrancar una partida.
"""
from typing import Callable, Protocol

from modelo.snapshots import (
    EstadoVista, ItemVista, ResultadoAccion, ResumenPartida, MetaPartida, EstadoGuardado)


# Acciones que el jugador puede pedir (nombres que viajan al modelo y al log)
ACCIONES = ("mover", "abrir", "atacar", "esperar", "recoger",
            "usar", "equipar", "soltar", "retroceso")
DIRECCIONES = ("N", "S", "E", "O")


class ModeloJuego(Protocol):
    
    @property
    def meta(self) -> MetaPartida:
        """id/versión de cripta, versión de catálogo y semilla (van al log y al guardado)."""

    def ejecutar(self, accion: str, argumento: str | None = None) -> ResultadoAccion:
        """Ejecuta UNA acción del jugador y luego corre la agenda de eventos hasta la
        siguiente decisión del jugador (§2.3, §5.2).

          accion    : una de ACCIONES.
          argumento : "mover"/"abrir" -> dirección "N|S|E|O"; "atacar" -> id de instancia del
                      enemigo; "recoger"/"soltar"/"usar"/"equipar" -> id de instancia del
                      objeto; "esperar"/"retroceso" -> None.
          Si la acción es inválida devuelve ResultadoAccion(ok=False, mensaje=...) SIN consumir
          tiempo ni cambiar el estado (Apéndice B). Si necesita esperar contenido de red, es
          el modelo/B quien bloquea; el reloj virtual no avanza por eso (§2.4)."""

    def estado_vista(self) -> EstadoVista:
        """Foto de solo lectura de lo que la vista debe dibujar."""

    def resumen(self) -> ResumenPartida:
        """terminado/resultado/acciones/derrotados/reloj_final (puntaje y verificación de replay)."""

    # --- Inventario (PERSONA C) -----------------------------------------------------------
    def inventario_cursor(self, movimiento: str) -> ItemVista | None:
        """movimiento: "actual" | "siguiente" | "anterior". Mueve el cursor de la lista
        doblemente enlazada y devuelve el objeto visto (None si el inventario está vacío)."""

    def inventario_vista(self, orden: str | None = None,
                         descendente: bool = False) -> list[ItemVista]:
        """orden None = orden real; "peso" | "valor" | "nombre" = vista ordenada sin alterar
        el orden real. C debe usar utilidades.ordenamiento.ordenar (§4.9)."""

    # --- Guardado (A + C exportan / restauran; D solo escribe y lee el archivo) --------------
    def exportar_estado(self) -> EstadoGuardado:
        """Vuelca el estado completo a un EstadoGuardado (incluye azar.getstate())."""

    def restaurar_estado(self, estado: EstadoGuardado) -> None:
        """Deja el modelo exactamente como estaba al exportar (incluye azar.setstate())."""


class EstadisticasRed(Protocol):
    solicitudes: int
    presupuesto: int
    aciertos_cache: int
    fallos_cache: int


class FuenteDatos(Protocol):
    """Lo que D necesita de PERSONA B (cliente de red / adaptador --offline)."""

    def listar_criptas(self) -> list:
        """GET /criptas -> lista de {id, nombre, salas, dificultad}. OJO: cuenta como 1 solicitud
        del presupuesto; por eso main.py acepta --cripta ID para saltársela."""

    def version_cripta(self, cripta_id: str) -> str:
        """GET /criptas/<id>/version (o su equivalente offline). Se usa al validar un replay
        o un guardado."""

    def version_catalogo(self) -> str:
        """GET /catalogo/version (o su equivalente offline)."""

    def estadisticas(self) -> EstadisticasRed:
        """solicitudes realizadas, presupuesto, aciertos y fallos de caché (§5.1)."""

    # Opcional (D usa hasattr): si el log es de una versión vieja pero B guarda copia local
    # compatible en disco, devolver True permite reproducirlo (§4.11).
    # def tiene_copia_local(self, cripta_id, version_cripta, version_catalogo) -> bool: ...


# Fábrica que A expone (nombre acordado: modelo.juego.crear_juego). Recibe:
#   fuente     : FuenteDatos de B
#   cripta_id  : id de la cripta
#   semilla    : entero; el modelo hace random.Random(semilla)
#   notificar  : callable(str). El modelo lo llama por CADA mensaje para la bitácora en pantalla.
FabricaJuego = Callable[[FuenteDatos, str, int, Callable[[str], None]], ModeloJuego]