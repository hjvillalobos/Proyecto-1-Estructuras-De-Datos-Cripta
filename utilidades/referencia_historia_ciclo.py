"""RC-01: productor anterior d43ded2, solo para equivalencia y medición."""
from modelo.partida import MotorPartida, Proyeccion, diferencias, campos_inventario
from modelo.juego import _MotorConHistoriaDePrueba


class MotorHistoriaAnterior(MotorPartida):
    def proyeccion_h3(self):
            basicos = _MotorConHistoriaDePrueba.proyeccion_h3(self)
            # HU-02: comparar ambos algoritmos con los mismos campos observables.
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
                cambios = diferencias(anterior.basicos, posterior.basicos)
                inventario_anterior = getattr(self, '_inventario_inicio', None)
                if inventario_anterior is None:
                    inventario_anterior = anterior.inventario
                if inventario_anterior is not posterior.inventario:
                    cambios += diferencias(inventario_anterior, posterior.inventario)
                self._inventario_inicio = None
                if anterior.mapa is not posterior.mapa:
                    cambios += diferencias(anterior.mapa, posterior.mapa)
            else:
                cambios = diferencias(anterior, posterior)
            from modelo.conocimiento_historia import convertir_cambios
            cambios += convertir_cambios(tuple(self._deltas_conocimiento))
            self._deltas_conocimiento.clear()
            return tuple((c.clave, c.anterior.valor if c.anterior.presente else None,
                          c.nuevo.valor if c.nuevo.presente else None)
                         for c in cambios)
