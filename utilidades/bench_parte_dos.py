"""IA-07: alternativas de rutas y carga integrada reproducibles, sin red/vista."""
from random import Random
from time import perf_counter_ns
from types import SimpleNamespace

from modelo.rutas import GrafoTerreno, EspacioBusqueda, HeapRutas, ArcoTerreno, buscar_ruta
from modelo.tipos import Sala, Jugador, InstanciaEnemigo, FichaCatalogo


def cadena(cantidad, semilla):
    azar = Random(semilla)
    salas = [Sala(i, 'Sintética', {}) for i in range(cantidad)]
    for i in range(cantidad - 1):
        costo = azar.randint(1, 150)
        salas[i].salidas['E'] = {'sala': i + 1, 'costo': costo, 'cerrada': False}
        salas[i + 1].salidas['O'] = {'sala': i, 'costo': costo, 'cerrada': False}
    return salas


from modelo.rutas_compartidas import RutasCompartidas

def medir_rutas(salas, semilla, repeticiones):
    """Mismas consultas/puertas para todas las estrategias; comprueba igualdad."""
    grafo = GrafoTerreno(salas)
    azar = Random(semilla)
    for actores in (1, 30):
        origenes = [azar.randrange(len(salas) - 1) for _ in range(actores)]
        for rango in (100, None):
            for periodo, nombre in ((100, 'estables'), (1, 'inestables')):
                resultados, tiempos = [], []
                for estrategia in ('individual', 'reutilizacion', 'compartido'):
                    espacio = EspacioBusqueda(grafo.ids)
                    heap = HeapRutas(espacio)
                    compartidas = RutasCompartidas(grafo)
                    cache = [None] * actores
                    firmas, epoca = [], 0
                    for fila in grafo.adyacencias:
                        for a in fila: a.puerta['cerrada'] = False
                    inicio = perf_counter_ns()
                    for ciclo in range(repeticiones):
                        if ciclo % periodo == 0:
                            epoca += 1
                            for a in grafo.adyacencias[len(salas) // 2]:
                                a.puerta['cerrada'] = ciclo % 2 == 1
                        for i, origen in enumerate(origenes):
                            if estrategia == 'compartido':
                                paso = compartidas.buscar(origen, len(salas) - 1, rango, epoca)
                            elif estrategia == 'reutilizacion' and cache[i] is not None and cache[i][0] == epoca:
                                paso = cache[i][1]
                            else:
                                paso = buscar_ruta(grafo, espacio, heap, origen, len(salas) - 1, rango)
                                cache[i] = (epoca, paso)
                            firmas.append(paso)
                    tiempos.append((estrategia, (perf_counter_ns() - inicio) / 1e6))
                    resultados.append(firmas)
                if resultados[0] != resultados[1] or resultados[0] != resultados[2]:
                    raise AssertionError('Las estrategias producen decisiones distintas.')
                for estrategia, total in tiempos:
                    print(f'Rutas V={len(salas)} H={actores} rango={rango} puertas={nombre} '
                          f'{estrategia}: total={total:.3f} ms consultas={actores * repeticiones}')


def medir_integracion(salas, semilla, repeticiones):
    from modelo.partida import MotorPartida, conectar_mapa
    from modelo.inventario import Inventario
    from modelo.snapshots import MetaPartida
    from controlador.partida_historica import integrar_historia
    from modelo.conocimiento_rutas import PlanificadorConocido
    jugador = Jugador(vida=10**9, vida_max=10**9, ataque=1, defensa=1, velocidad=100,
        tiempo_siguiente=0, inventario=Inventario(10), posicion_actual=salas[0].id, llaves_obtenidas=[])
    for sala in salas:
        for salida in sala.salidas.values(): salida['cerrada'] = False
    motor = MotorPartida(jugador, salas, semilla)
    motor.meta = MetaPartida('sintetica', 'bench', 'bench', semilla)
    ficha = FichaCatalogo('cazador-bench', 'enemigo', 'Cazador sintético', {'rango': None})
    catalogo = SimpleNamespace(ficha_preparada=lambda _: ficha,
        obtener_fichas=lambda ids: [ficha for _ in ids])
    motor.gestor_precarga = SimpleNamespace(catalogo=catalogo, generales=None)
    conectar_mapa(motor)
    for sala in salas: motor._conocimiento.entrar(sala.id)
    for puerta in motor._conocimiento._puertas:
        motor._conocimiento.observar_puerta(puerta.extremo_a, puerta.id, False)
    for i in range(30):
        e = InstanciaEnemigo(vida=10, vida_max=10, ataque=1, defensa=1, velocidad=100,
            tiempo_siguiente=0, id_instancia=f'bench-{i}', tipo_catalogo=ficha.id, comportamiento='cazador')
        motor.enemigos_por_sala[salas[-1].id].append(e)
    motor.activar_enemigos_de_sala(salas[-1].id, motor.enemigos_por_sala[salas[-1].id])
    juego = integrar_historia(motor, 50)
    tiempos = []
    for _ in range(repeticiones):
        inicio = perf_counter_ns()
        assert juego.ejecutar('esperar').ok
        tiempos.append((perf_counter_ns() - inicio) / 1e6)
    plan = PlanificadorConocido(motor._conocimiento)
    pasos = []
    for i in range(repeticiones):
        origen = salas[i % (len(salas) - 1)].id
        inicio = perf_counter_ns()
        paso = plan.consultar(origen, salas[-1].id)
        pasos.append((perf_counter_ns() - inicio) / 1e6)
        if paso.estado not in ('paso', 'llegada'):
            raise AssertionError('La medición debe resolver una ruta, no un rechazo.')
    print(f'Ciclo integrado H=30 historia+mapa completo: máximo={max(tiempos):.3f} ms '
          f'media={sum(tiempos)/len(tiempos):.3f} ms sobre20={sum(t > 20 for t in tiempos)}/{len(tiempos)}')
    print(f'Paso conocido: máximo={max(pasos):.3f} ms media={sum(pasos)/len(pasos):.3f} ms '
          f'sobre5={sum(t > 5 for t in pasos)}/{len(pasos)}')


def medir(cantidad, semilla, repeticiones, paquete=None, cripta=None):
    if paquete:
        from datos.offline import ClienteOffline
        from red.precarga import validar_pagina_esqueleto
        cliente = ClienteOffline(paquete)
        datos = cliente.obtener_datos_generales(cripta)
        salas = []
        for pagina in range(1, datos['paginas'] + 1):
            salas.extend(validar_pagina_esqueleto(cliente.obtener_esqueleto(cripta, pagina), pagina, datos['paginas']))
        print(f"Referencia {cripta}@{datos['version']}: {len(salas)} salas, 30 cazadores inyectados para carga, cero HTTP.")
    else:
        print('Parte II: carga sintética determinista; no sustituye la referencia oficial.')
        salas = cadena(max(3, cantidad), semilla)
    medir_rutas(salas, semilla, repeticiones)
    medir_integracion(salas, semilla, repeticiones)
