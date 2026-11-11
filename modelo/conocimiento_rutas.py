"""I4: consulta de pasos con conocimiento vigente y el buscador propio de A.

No ejecuta movimientos. Los índices privados pertenecen al componente de C;
el adaptador solo los lee. El mapa no debe mutar durante una consulta.
"""
from dataclasses import dataclass

from modelo.conocimiento import ConocimientoMapa, EXPLORADA, _indice


@dataclass(frozen=True, slots=True)
class ConsultaRuta:
    estado: str
    siguiente: int | None = None
    direccion: str | None = None
    costo_paso: int | None = None
    costo_total: int | None = None


class _PasoAbierto:
    """Contrato de lectura de A, sin diccionario ni estado real de puerta."""

    def get(self, clave, defecto=None):
        return False if clave == 'cerrada' else defecto


class _AdyacenciasConocidas:
    def __init__(self, mapa, tipo_arco, inversa=False):
        self._mapa = mapa
        abierta = _PasoAbierto()
        arcos = [[] for _ in mapa._ids]
        for origen, salidas in enumerate(mapa._salidas):
            for salida, destino, puerta in salidas:
                desde, hasta = (destino, origen) if inversa else (origen, destino)
                arcos[desde].append((tipo_arco(desde, hasta, salida.direccion,
                                              salida.costo, abierta), puerta))
        self._arcos = tuple(tuple(fila) for fila in arcos)

    def __getitem__(self, origen):
        mapa = self._mapa
        if mapa._estados[origen] != EXPLORADA:
            return
        for arco, puerta in self._arcos[origen]:
            if (mapa._estados[arco.destino] == EXPLORADA
                    and (puerta is None or mapa._recuerdos[puerta] is False)):
                yield arco


class _FuenteConocida:
    def __init__(self, mapa, tipo_arco, inversa=False):
        self.ids = mapa._ids
        self.adyacencias = _AdyacenciasConocidas(mapa, tipo_arco, inversa)


class PlanificadorConocido:
    """Una instancia por mapa; distancias cerradas para un destino/revisión.

    Preparación O(V+E). Filtra durante la expansión, no después de buscar.
    La interfaz compartida y el movimiento del motor se integran por separado.
    """

    def __init__(self, mapa):
        if type(mapa) is not ConocimientoMapa:
            raise ValueError('Se requiere ConocimientoMapa.')
        from modelo.rutas import ArcoTerreno, EspacioBusqueda, HeapRutas, buscar_ruta

        self._mapa = mapa
        self._fuente = _FuenteConocida(mapa, ArcoTerreno)
        self._inversa = _FuenteConocida(mapa, ArcoTerreno, inversa=True)
        self._espacio = EspacioBusqueda(self._fuente.ids)
        self._frontera = HeapRutas(self._espacio)
        self._buscar = buscar_ruta
        self._cache = None

    def consultar(self, origen, destino):
        """FR-007/008/010/012: no modifica mapa, reloj, historial ni posición."""
        if self._mapa.estado_sala(destino) != EXPLORADA:
            return ConsultaRuta('destino_no_explorado')
        if self._mapa.estado_sala(origen) != EXPLORADA:
            return ConsultaRuta('origen_no_explorado')
        if origen == destino:
            return ConsultaRuta('llegada', costo_total=0)
        fuente = self._fuente
        indice_origen = _indice(fuente.ids, origen)
        clave = (destino, self._mapa.revision)
        if self._cache != clave or not self._espacio.esta_cerrado(indice_origen):
            self._cache = None  # Una excepción no publica etiquetas parciales.
            # Sin un primer paso conocido no existe una ruta al otro destino.
            # Revisar solo al recalcular: el caso reutilizado conserva su costo.
            if next(iter(fuente.adyacencias[indice_origen]), None) is None:
                return ConsultaRuta('sin_ruta')
            self._buscar(self._inversa, self._espacio, self._frontera,
                         _indice(fuente.ids, destino), indice_origen, None)
            self._cache = clave
        if not self._espacio.esta_cerrado(indice_origen):
            return ConsultaRuta('sin_ruta')
        # Costos positivos: todo sucesor óptimo tiene menor distancia al destino
        # y quedó cerrado antes que el origen, incluso si A detuvo la búsqueda.
        mejor = None
        elegido = None
        for arco in fuente.adyacencias[indice_origen]:
            if not self._espacio.esta_cerrado(arco.destino):
                continue
            restante, _ = self._espacio.etiqueta(arco.destino)
            candidato = (arco.costo + restante, fuente.ids[arco.destino], arco.costo)
            if mejor is None or candidato < mejor:
                mejor, elegido = candidato, arco
        distancia, _ = self._espacio.etiqueta(indice_origen)
        if elegido is None or mejor[0] != distancia:
            raise RuntimeError('Las distancias no corresponden al conocimiento vigente.')
        return ConsultaRuta('paso', fuente.ids[elegido.destino], elegido.direccion,
                            elegido.costo, distancia)
