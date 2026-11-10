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
    def __init__(self, mapa, tipo_arco):
        self._mapa = mapa
        abierta = _PasoAbierto()
        self._arcos = tuple(
            tuple((tipo_arco(origen, destino, salida.direccion, salida.costo, abierta), puerta)
                  for salida, destino, puerta in salidas)
            for origen, salidas in enumerate(mapa._salidas))

    def __getitem__(self, origen):
        mapa = self._mapa
        if mapa._estados[origen] != EXPLORADA:
            return
        for arco, puerta in self._arcos[origen]:
            if (mapa._estados[arco.destino] == EXPLORADA
                    and (puerta is None or mapa._recuerdos[puerta] is False)):
                yield arco


class _FuenteConocida:
    def __init__(self, mapa, tipo_arco):
        self.ids = mapa._ids
        self.adyacencias = _AdyacenciasConocidas(mapa, tipo_arco)


class PlanificadorConocido:
    """Una instancia por mapa; consultas secuenciales, sin caché de rutas.

    Preparación O(V+E). Filtra durante la expansión, no después de buscar.
    La interfaz compartida y el movimiento del motor se integran por separado.
    """

    def __init__(self, mapa):
        if type(mapa) is not ConocimientoMapa:
            raise ValueError('Se requiere ConocimientoMapa.')
        from modelo.rutas import ArcoTerreno, EspacioBusqueda, HeapRutas, buscar_ruta

        self._mapa = mapa
        self._fuente = _FuenteConocida(mapa, ArcoTerreno)
        self._espacio = EspacioBusqueda(self._fuente.ids)
        self._frontera = HeapRutas(self._espacio)
        self._buscar = buscar_ruta

    def consultar(self, origen, destino):
        """FR-007/008/010/012: no modifica mapa, reloj, historial ni posición."""
        if self._mapa.estado_sala(destino) != EXPLORADA:
            return ConsultaRuta('destino_no_explorado')
        if self._mapa.estado_sala(origen) != EXPLORADA:
            return ConsultaRuta('origen_no_explorado')
        if origen == destino:
            return ConsultaRuta('llegada', costo_total=0)
        fuente = self._fuente
        paso = self._buscar(fuente, self._espacio, self._frontera,
                            _indice(fuente.ids, origen), _indice(fuente.ids, destino), None)
        if paso is None:
            return ConsultaRuta('sin_ruta')
        siguiente, direccion, costo, total = paso
        return ConsultaRuta('paso', fuente.ids[siguiente], direccion, costo, total)
