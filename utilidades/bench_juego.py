"""Cargas reproducibles de las estructuras reales, sin vista ni red."""

from dataclasses import dataclass
from pathlib import Path
import random
import tempfile
from time import perf_counter_ns

from datos.guardado_binario import (
    ArchivoGuardado, guardar_estado, cargar_estado, guardar_json, cargar_json)
from modelo.eventos import ColaEventos
from modelo.historial import HistorialRetroceso
from modelo.inventario import Inventario
from modelo.juego import Motor, crear_juego
from modelo.rastro import RegistroRastro
from modelo.snapshots import MetaPartida
from modelo.tipos import Jugador, ObjetoInstancia, Sala
from utilidades.ordenamiento import ordenar, INSERCION, FUSION


@dataclass
class Muestra:
    nombre: str
    operaciones: int
    tiempos_us: list

    def imprimir(self):
        t = self.tiempos_us
        print(f"{self.nombre}: n={self.operaciones} promedio={sum(t)/len(t):.3f} "
              f"min={min(t):.3f} max={max(t):.3f} us/op")


def medir_carga(nombre, operaciones, repeticiones, preparar):
    muestras = []
    for r in range(-1, repeticiones):
        ejecutar, validar = preparar()
        inicio = perf_counter_ns()
        ejecutar()
        tiempo = (perf_counter_ns() - inicio) / operaciones / 1000
        validar()
        if r >= 0:
            muestras.append(tiempo)
    return Muestra(nombre, operaciones, muestras)


def medir_agenda(cantidad, repeticiones, tamano, semilla):
    def preparar():
        cola = ColaEventos()
        azar = random.Random(semilla)
        for _ in range(tamano):
            cola.insertar(azar.randrange(100), "sintetico", None)
        ultimos = []

        def ejecutar():
            anterior = (-1, -1)
            for i in range(cantidad):
                evento = cola.extraer_minimo()
                actual = (evento.tiempo, evento.secuencia)
                if actual < anterior:
                    raise AssertionError("Agenda no determinista")
                anterior = actual
                nuevo = cola.insertar(evento.tiempo + 100, "sintetico", None)
                if i % 7 == 0:
                    cola.reprogramar(nuevo, nuevo.tiempo + 1)
            ultimos.append(anterior)

        def validar():
            assert len(cola.pendientes()) == tamano and ultimos
        return ejecutar, validar
    return medir_carga(f"agenda/{tamano} pendientes", cantidad, repeticiones, preparar)


def medir_inventario(cantidad, repeticiones, tamano):
    def preparar():
        inv = Inventario(tamano)
        for i in range(tamano):
            inv.recoger(ObjetoInstancia(str(i), "sintetico", "inventario"))
        nodo = inv.cursor

        def ejecutar():
            for _ in range(cantidad):
                inv.quitar_nodo(nodo)
                inv.reinsertar_nodo(nodo, inv.cabeza)
                inv.avanzar()
                inv.retroceder()

        def validar():
            assert len(list(inv)) == tamano and nodo.en_inventario
        return ejecutar, validar
    return medir_carga(f"inventario/{tamano} quitar-reinsertar-recorrer", cantidad, repeticiones, preparar)


def medir_historial(cantidad, repeticiones):
    def preparar():
        rastro = RegistroRastro(1)
        historial = HistorialRetroceso(rastro)
        inv = Inventario(1)

        def ejecutar():
            for i in range(cantidad):
                inv.recoger(ObjetoInstancia(str(i), "pergamino", "inventario"))
                historial.iniciar_turno(i)
                historial.registrar_rastro(1, rastro.tiempo_de(1))
                rastro.marcar_visita(1, i)
                historial.cerrar_turno()
                assert historial.usar_pergamino(inv, "pergamino") == i

        def validar():
            assert rastro.tiempo_de(1) is None and inv.esta_vacio()
            assert historial.cantidad_turnos() == 0
        return ejecutar, validar
    return medir_carga("historial/registrar-revertir-consumir", cantidad, repeticiones, preparar)


class ClaveCostosa:
    def __init__(self, valor):
        self.valor = valor

    def __lt__(self, otra):
        # Trabajo repetible en cada comparacion, no en la extraccion de clave.
        for _ in range(20):
            self.valor < otra.valor
        return self.valor < otra.valor


def medir_ordenamientos(cantidad, repeticiones, tamanos, semilla):
    resultados = []
    for n in tamanos:
        azar = random.Random(semilla)
        aleatorios = list(range(n))
        azar.shuffle(aleatorios)
        casi = list(range(n))
        if n > 1:
            casi[n // 2], casi[n // 2 - 1] = casi[n // 2 - 1], casi[n // 2]
        for nombre, datos, costosa in (("aleatorio", aleatorios, False),
                                        ("casi_ordenado", casi, False),
                                        ("comparacion_costosa", aleatorios, True)):
            vueltas = max(1, cantidad // n)
            for algoritmo in (INSERCION, FUSION, None):
                def preparar(datos=datos, costosa=costosa, algoritmo=algoritmo, n=n, vueltas=vueltas):
                    claves = [ClaveCostosa(v) for v in datos] if costosa else datos
                    salida = []

                    def ejecutar():
                        for _ in range(vueltas):
                            salida[:] = ordenar(claves, comparacion_costosa=costosa, algoritmo=algoritmo)

                    def validar():
                        valores = [v.valor for v in salida] if costosa else salida
                        assert valores == list(range(n))
                        assert ([v.valor for v in claves] if costosa else claves) == datos
                    return ejecutar, validar
                resultados.append(medir_carga(
                    f"orden/{n}/{nombre}/{algoritmo or 'automatico'} (us/lista)",
                    vueltas, repeticiones, preparar))
    return resultados


def motor_sintetico(tamano, semilla):
    jugador = Jugador(vida=30, vida_max=30, ataque=6, defensa=2, velocidad=100,
                      tiempo_siguiente=0, inventario=Inventario(10),
                      posicion_actual=1, llaves_obtenidas=[])
    motor = Motor(jugador, [Sala(i, f"Sintetica {i}", {}) for i in range(1, tamano + 1)], semilla)
    motor.meta = MetaPartida("sintetica", "bench", "bench", semilla)
    motor.contenido_cargado[1] = True
    return motor


def medir_guardado(cantidad, repeticiones, tamano, semilla):
    motor = motor_sintetico(tamano, semilla)
    for i in range(1, tamano + 1):
        motor.contenido_cargado[i] = True
    estado = motor.exportar_estado()
    resultados = []
    vueltas = max(1, cantidad // tamano)
    with tempfile.TemporaryDirectory() as carpeta:
        for nombre, guardar, cargar in (("binario", guardar_estado, cargar_estado),
                                         ("json", guardar_json, cargar_json)):
            ruta = str(Path(carpeta) / nombre)
            guardar(estado, ruta)
            print(f"guardado/{nombre}: salas={tamano} bytes={Path(ruta).stat().st_size}")
            for operacion in ("guardar", "cargar", "sala_directa"):
                if operacion == "sala_directa" and nombre == "json":
                    continue

                def preparar(operacion=operacion, guardar=guardar, cargar=cargar, ruta=ruta):
                    leidos = []

                    def ejecutar():
                        for _ in range(vueltas):
                            if operacion == "guardar":
                                guardar(estado, ruta)
                            elif operacion == "cargar":
                                leidos[:] = [cargar(ruta)]
                            else:
                                with ArchivoGuardado(ruta) as archivo:
                                    leidos[:] = [archivo.leer_sala(tamano)]

                    def validar():
                        if operacion == "sala_directa":
                            assert leidos[0] == estado.salas[-1]
                        else:
                            assert (leidos[0] if leidos else cargar(ruta)) == estado
                    return ejecutar, validar
                resultados.append(medir_carga(f"guardado/{nombre}/{operacion}", vueltas, repeticiones, preparar))
    return resultados


def medir_ciclo(cantidad, repeticiones, tamano, semilla, paquete=None, cripta=None):
    from datos.almacen import AlmacenLocal
    from datos.offline import ClienteOffline
    from red.cache import CacheCatalogoOrdenado
    from red.catalogo import GestorCatalogo
    from red.precarga import GestorPrecarga

    muestras = []
    for repeticion in range(-1, repeticiones):
        gestor = None
        try:
            if paquete:
                cliente = ClienteOffline(paquete)
                gestor = GestorPrecarga(cliente, GestorCatalogo(
                    cliente, CacheCatalogoOrdenado(25), AlmacenLocal(paquete)))
                motor = crear_juego(gestor, cripta, semilla)
                gestor.cargar_contenido([s.id for s in gestor.salas])
            else:
                motor = motor_sintetico(tamano, semilla)
            tiempos = []
            for _ in range(cantidad):
                if motor.terminado:
                    break
                if not paquete:
                    # Preparacion fuera del tiempo: el ciclo SI procesa todos estos eventos.
                    for _ in range(tamano):
                        motor.programar_evento(motor.reloj + 1, "rearmar_trampa", _trampa_sintetica())
                inicio = perf_counter_ns()
                resultado = motor.ejecutar("esperar")
                tiempos.append((perf_counter_ns() - inicio) / 1000)
                assert resultado.ok
            if repeticion >= 0:
                muestras.extend(tiempos)
        finally:
            if gestor is not None:
                gestor.cerrar()
    assert muestras
    resultado = Muestra(f"ciclo/{cripta or 'sintetico'}/esperar", len(muestras), muestras)
    resultado.imprimir()
    print(f"  limite=20000 us; ciclos sobre limite={sum(t >= 20000 for t in muestras)}; "
          "sin red/renderizado; solo esta carga, no certifica otras rutas")
    return resultado


def _trampa_sintetica():
    from modelo.tipos import Trampa
    return Trampa("bench", "bench", False)
