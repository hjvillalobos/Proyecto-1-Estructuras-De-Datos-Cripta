"""T006: datos sintéticos válidos; FR-001/014, NFR-005, A1/A2/A7/P2.

Se reutiliza Sala con descriptores JSON. US1 utiliza el paquete generado por
ServidorFalso existente y el cliente offline real, sin nuevos dobles.
"""

from contextlib import contextmanager
from random import Random
from tempfile import TemporaryDirectory

from datos.offline import ClienteOffline
from modelo.juego import crear_juego, _incorporar_sala_preparada
from modelo.tipos import Sala
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from tests.datos_prueba import crear_paquete


SIN_COSTO_DECLARADO = object()


def crear_salas(ids, conexiones):
    """Cada conexión es (origen, dirección, destino, vuelta, costo, cerrada).

    Origen/destino son posiciones en ids; cada par declara ambos sentidos.
    El llamador suministra un grafo válido con grado máximo cuatro.
    """
    salas = [Sala(identificador, "Sala sintética", {}) for identificador in ids]
    for origen, direccion, destino, vuelta, costo, cerrada in conexiones:
        ida = {"sala": ids[destino], "cerrada": cerrada}
        regreso = {"sala": ids[origen], "cerrada": cerrada}
        if costo is not SIN_COSTO_DECLARADO:
            ida["costo"] = costo
            regreso["costo"] = costo
        salas[origen].salidas[direccion] = ida
        salas[destino].salidas[vuelta] = regreso
    return salas


def crear_cadena(cantidad, semilla):
    """Cadena recíproca de grado ≤2, costos positivos e IDs no contiguos."""
    azar = Random(semilla)
    ids = [17 + i * 1000003 for i in range(cantidad - 1, -1, -1)]
    conexiones = [
        (i, "E", i + 1, "O", azar.randint(1, 500), bool(azar.randrange(2)))
        for i in range(cantidad - 1)
    ]
    return crear_salas(ids, conexiones)


@contextmanager
def motor_terreno(costo=SIN_COSTO_DECLARADO, velocidad=100,
                  comportamiento="guardian", velocidad_enemigo=100,
                  puerta_inicial_cerrada=False, *, costo_primera_conexion=SIN_COSTO_DECLARADO, completa=False):
    """T011/T012: motor real con fixture existente; cero HTTP real.

    El paquete sintético existente se configura antes de crear el motor:
    todas sus copias ven costos/puertas/estadísticas idénticos. La activación
    inicial programa turnos con la velocidad definitiva. El reloj comienza
    en cero; las pruebas de integración avanzan mediante acciones ordinarias.
    """
    with TemporaryDirectory(prefix="cripta-terreno-") as carpeta:
        almacen = crear_paquete(carpeta, salas=4)
        generales = almacen.leer_generales("prueba", "v1")
        generales["jugador"]["velocidad"] = velocidad
        almacen.guardar_generales(generales)
        ficha = almacen.leer_ficha("cat1", "enemigo")
        ficha["comportamiento"] = comportamiento
        ficha["velocidad"] = velocidad_enemigo
        almacen.guardar_ficha("cat1", ficha)
        pagina = almacen.leer_pagina("prueba", "v1", 1)
        for sala in pagina["salas"]:
            for salida in sala["salidas"].values():
                primera_conexion = (sala["id"], salida["sala"]) in ((100, 101), (101, 100))
                costo_salida = costo
                if primera_conexion and costo_primera_conexion is not SIN_COSTO_DECLARADO:
                    costo_salida = costo_primera_conexion
                if costo_salida is not SIN_COSTO_DECLARADO:
                    salida["costo"] = costo_salida
                if puerta_inicial_cerrada and primera_conexion:
                    salida["cerrada"] = True
                    salida["llave"] = "obj_0"
        almacen.guardar_pagina("prueba", "v1", pagina)
        cliente = ClienteOffline(carpeta)
        catalogo = GestorCatalogo(cliente, CacheCatalogoOrdenado(25), almacen)
        precarga = GestorPrecarga(cliente, catalogo)
        try:
            motor = crear_juego(precarga, "prueba", semilla=20261105, partida_completa=completa)
            for sala in precarga.salas:
                preparada = precarga.preparar_entrada(sala.id, motor._ids_en_uso(sala.id))
                _incorporar_sala_preparada(motor, preparada)
            yield motor
        finally:
            try:
                precarga.cerrar()
            finally:
                cliente.cerrar()
