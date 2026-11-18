"""Productor de producción: historia por diferencias, mapa y viaje reales."""
from copy import copy, deepcopy

from modelo.juego import Motor, _MotorConHistoriaDePrueba
from modelo.conocimiento import (ConocimientoMapa, SalaConocible, SalidaConocible,
                                  PuertaConocible)
from modelo.conocimiento_historia import campos_iniciales as campos_mapa
from modelo.inventario_historia import campos_iniciales as campos_inventario
from modelo.snapshots import CambioHistorico, ValorHistorico
from modelo.errores_historia import CambioHistoriaIncoherente
from utilidades.ordenamiento import ordenar


def conectar_mapa(motor):
    """Identidad estable por extremos recíprocos; no inventa salidas inversas."""
    from modelo.almacen_salas import crear_almacen
    referencias = crear_almacen(motor._ids_salas, list)
    puertas, salas = [], []
    for sala in motor.salas:
        if sala is None:
            continue
        salidas = []
        for direccion in ('N', 'S', 'E', 'O'):
            salida = sala.salidas.get(direccion)
            if salida is None:
                continue
            puerta = None
            if (referencias[sala.id] and any(d == direccion for d, _ in referencias[sala.id])) or any(c in salida for c in ('cerrada', 'llave', 'cierre_automatico')):
                puerta = next((i for d, i in referencias[sala.id] if d == direccion), None)
                if puerta is None:
                    puerta = len(puertas)
                    puertas.append(PuertaConocible(puerta, sala.id, salida['sala']))
                    for extremo, d, _ in motor.extremos_puerta(sala, direccion):
                        referencias[extremo.id].append((d, puerta))
            salidas.append(SalidaConocible(direccion, salida['sala'], salida.get('costo', 100), puerta))
        salas.append(SalaConocible(sala.id, sala.nombre, tuple(salidas)))
    motor._puertas_conocibles = referencias
    motor._conocimiento = ConocimientoMapa(tuple(salas), tuple(puertas), motor.jugador.posicion_actual)
    motor._actualizar_conocimiento()
    from modelo.conocimiento_rutas import PlanificadorConocido
    from modelo.viaje import ControlViaje
    motor.control_viaje = ControlViaje(PlanificadorConocido(motor._conocimiento))


def diferencias(antes, despues):
    """Fusión propia; solo las diferencias sobreviven en la historia."""
    a, b = ordenar(antes, clave=lambda p: p[0]), ordenar(despues, clave=lambda p: p[0])
    i = j = 0
    cambios = []
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and a[i][0] < b[j][0]):
            clave, valor = a[i]; i += 1
            cambios.append(CambioHistorico(clave, ValorHistorico(True, valor), ValorHistorico(False)))
        elif i == len(a) or b[j][0] < a[i][0]:
            clave, valor = b[j]; j += 1
            cambios.append(CambioHistorico(clave, ValorHistorico(False), ValorHistorico(True, valor)))
        else:
            clave, valor = a[i]
            if valor != b[j][1]:
                cambios.append(CambioHistorico(clave, ValorHistorico(True, valor), ValorHistorico(True, b[j][1])))
            i += 1; j += 1
    return tuple(cambios)


def deltas_ordenados(antes, despues):
    """RC-01: fusionar campos únicos ya ordenados, sin ordenar ni tipar dos veces."""
    i = j = 0
    cambios = []
    while i < len(antes) and j < len(despues):
        clave, valor = antes[i]
        nueva, posterior = despues[j]
        if clave < nueva:
            cambios.append((clave, valor, None))
            i += 1
        elif nueva < clave:
            cambios.append((nueva, None, posterior))
            j += 1
        else:
            if valor != posterior:
                cambios.append((clave, valor, posterior))
            i += 1
            j += 1
    cambios.extend((clave, valor, None) for clave, valor in antes[i:])
    cambios.extend((clave, None, valor) for clave, valor in despues[j:])
    return tuple(cambios)


class MotorPartida(_MotorConHistoriaDePrueba):
    _partida_completa = True
    _acciones_h3 = ('mover', 'esperar', 'atacar', 'recoger', 'soltar', 'equipar', 'usar', 'abrir')

    def __init__(self, jugador, salas_lista, semilla):
        super().__init__(jugador, salas_lista, semilla)
        from modelo.rutas import ContextoRutasCompartidas
        self._rutas_reales = ContextoRutasCompartidas(salas_lista)
        self._deltas_conocimiento = []
        self._resumen_historico = True

    def estado_historico_inicial(self):
        from modelo.linea_tiempo import EstadoHistorico
        return EstadoHistorico(self.proyeccion_completa())

    def mapa_historico(self, estado):
        return self._conocimiento.mapa_historico(estado) if self._conocimiento is not None else ()

    def proyeccion_completa(self):
        return tuple(self.proyeccion_h3()) + (campos_mapa(self._conocimiento) if self._conocimiento is not None else ())

    def proyeccion_h3(self):
        sala = self.jugador.posicion_actual
        actuales = tuple(self.enemigos_por_sala[sala])
        anteriores = getattr(self, '_coleccion_proyectada', ())
        if (getattr(self, '_sala_proyectada', None) != sala
                or len(actuales) != len(anteriores)
                or any(a is not b or a.id_instancia != identidad
                       for a, b, identidad in zip(actuales, anteriores,
                           getattr(self, '_ids_enemigos_proyectados', ())))):
            self._enemigos_ordenados = tuple(ordenar(actuales,
                clave=lambda e: e.id_instancia, algoritmo='fusion'))
            self._coleccion_proyectada = actuales
            self._ids_enemigos_proyectados = tuple(e.id_instancia for e in actuales)
            self._sala_proyectada = sala
        basicos = (Motor.proyeccion_h3(self)
                   + (("efectos", tuple(self._efectos_activos())),)
                   + tuple((f'enemigo:{e.id_instancia}',
                            (e.tipo_catalogo, e.vida, e.vida_max, e.comportamiento))
                           for e in self._enemigos_ordenados if e.vida > 0))
        if self._resumen_historico:
            basicos += (('estadisticas_partida', (self.enemigos_derrotados, self.resultado)),)
        inventario = campos_inventario(self.jugador.inventario)
        if inventario == getattr(self, '_inventario_proyectado', None):
            inventario = self._inventario_proyectado
        self._inventario_proyectado = inventario
        return Proyeccion(basicos, inventario, ())

    def _cambios_h3(self, anterior):
        posterior = self.proyeccion_h3()
        if isinstance(anterior, Proyeccion) and isinstance(posterior, Proyeccion):
            # El esquema fijo y el orden por ID de la cola son invariantes del
            # productor. No cambian el orden previo de las claves emitidas.
            cambios = (self._comparar_campos_fijos_h3(anterior.basicos[2:3], posterior.basicos[2:3])
                       + deltas_ordenados(anterior.basicos[3:], posterior.basicos[3:])
                       + self._comparar_campos_fijos_h3(anterior.basicos[1::-1], posterior.basicos[1::-1]))
            inventario_anterior = getattr(self, '_inventario_inicio', None)
            if inventario_anterior is None:
                inventario_anterior = anterior.inventario
            if inventario_anterior is not posterior.inventario:
                cambios += self._triples(diferencias(inventario_anterior, posterior.inventario))
            self._inventario_inicio = None
            if anterior.mapa is not posterior.mapa:
                cambios += self._triples(diferencias(anterior.mapa, posterior.mapa))
        else:
            cambios = self._triples(diferencias(anterior, posterior))
        from modelo.conocimiento_historia import convertir_cambios
        cambios += self._triples(convertir_cambios(tuple(self._deltas_conocimiento)))
        self._deltas_conocimiento.clear()
        return cambios

    @staticmethod
    def _triples(cambios):
        return tuple((c.clave, c.anterior.valor if c.anterior.presente else None,
                      c.nuevo.valor if c.nuevo.presente else None)
                     for c in cambios)

    def _antes_de_retroceder(self):
        pass  # La corrección se calcula después del consumo irreversible.

    def ejecutar(self, accion, argumento=None, *, registrar_h3=None):
        if accion == 'usar':
            objeto = next((o for o in self.jugador.inventario if o.id_instancia == argumento), None)
            if objeto is not None and self._resolver_clase(objeto.tipo_catalogo) == 'pergamino_retroceso':
                accion, argumento = 'retroceso', None
        historia = self._historia_h3
        if accion == 'retroceso' and historia is not None:
            resultado = Motor.ejecutar(self, accion, argumento)
            if resultado.ok:
                historia.recortar(self.acciones_jugador)
                cambios = diferencias(historia.consultar_final().estado.campos(), self.proyeccion_completa())
                historia.recortar(self.acciones_jugador, correcciones=cambios)
            return resultado
        contexto = self._rutas_reales
        self._deltas_conocimiento.clear()
        self._inventario_inicio = None
        if historia is not None:
            # Leer solo los nodos del inventario; no copiar el mapa/historia.
            actual = historia._actual
            meta = actual.obtener('inventario_estado')
            campos = [('inventario_estado', meta)]
            identidad = meta[2]
            for _ in range(meta[1]):
                clave = 'inventario_nodo:' + identidad
                valor = actual.obtener(clave)
                campos.append((clave, valor))
                identidad = valor[-1]
            self._inventario_inicio = tuple(campos)
        contexto.frontera_activa = True
        contexto._firma = None
        try:
            return super().ejecutar(accion, argumento, registrar_h3=registrar_h3)
        finally:
            contexto.frontera_activa = False
            contexto._firma = None

    def restaurar_estado_con_historia(self, estado, historia):
        if (estado.reloj, estado.acciones_jugador) != (historia.reloj, historia.cantidad_acciones):
            raise CambioHistoriaIncoherente('Estado e historia tienen fronteras diferentes.')
        final = historia.consultar_final().estado
        preparado = copy(self)
        try:
            historia.consultar_t(0).estado.obtener('estadisticas_partida')
            preparado._resumen_historico = True
        except KeyError:
            preparado._resumen_historico = False
        preparado.jugador = deepcopy(self.jugador)
        preparado.salas = deepcopy(self.salas)
        from modelo.rutas import ContextoRutasCompartidas
        preparado._rutas_reales = ContextoRutasCompartidas(
            [sala for sala in preparado.salas if sala is not None])
        preparado.registro_rastro = deepcopy(self.registro_rastro)
        preparado._conocimiento = deepcopy(self._conocimiento)
        preparado._deltas_conocimiento = []
        if preparado._conocimiento is not None:
            mapa = preparado._conocimiento
            for i, identidad in enumerate(mapa._ids):
                try: valor = final.obtener(f'conocimiento:sala:{identidad}')
                except KeyError: valor = 0
                if type(valor) is not int or valor not in (0, 1, 2):
                    raise CambioHistoriaIncoherente('Estado de conocimiento inválido.')
                mapa._estados[i] = valor
            for i, identidad in enumerate(mapa._ids_puertas):
                try: valor = final.obtener(f'conocimiento:puerta:{identidad}')
                except KeyError: valor = None
                if valor is not None and type(valor) is not bool:
                    raise CambioHistoriaIncoherente('Recuerdo de puerta inválido.')
                mapa._recuerdos[i] = valor
        Motor.restaurar_estado(preparado, estado)
        try:
            cursor = final.obtener('inventario_estado')[4]
        except KeyError as error:
            raise CambioHistoriaIncoherente('Falta el inventario histórico completo.') from error
        if cursor is not None:
            preparado.jugador.inventario.seleccionar(cursor)
        if diferencias(final.campos(), preparado.proyeccion_completa()):
            raise CambioHistoriaIncoherente('La historia no coincide con el estado o el conocimiento guardados.')
        Motor.restaurar_estado(self, estado)
        self._resumen_historico = preparado._resumen_historico
        if cursor is not None:
            self.jugador.inventario.seleccionar(cursor)
        if self._conocimiento is not None:
            self._conocimiento._estados[:] = preparado._conocimiento._estados
            self._conocimiento._recuerdos[:] = preparado._conocimiento._recuerdos
            self._conocimiento._revision += 1
        self._historia_h3 = historia


class Proyeccion(tuple):
    """Captura transitoria; comparte segmentos inmutables que no cambiaron."""
    def __new__(cls, basicos, inventario, mapa):
        valor = super().__new__(cls, basicos + inventario + mapa)
        valor.basicos, valor.inventario, valor.mapa = basicos, inventario, mapa
        return valor
