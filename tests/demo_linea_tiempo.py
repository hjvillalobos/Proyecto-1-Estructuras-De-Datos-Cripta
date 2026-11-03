"""Demostración sintética: python -m tests.demo_linea_tiempo."""
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from modelo.snapshots import CambioHistorico, EventoHistorico, ValorHistorico
from datos.historia_binaria import codificar_historia, decodificar_historia


def cambio(clave, antes, despues):
    return CambioHistorico(clave, ValorHistorico(True, antes), ValorHistorico(True, despues))


def main():
    historia = LineaTiempo(EstadoHistorico((('vida', 20), ('sala', 1))), checkpoint_cada=2)
    historia.registrar_accion(100, (cambio('sala', 1, 2),), (
        EventoHistorico(50, 1, (cambio('vida', 20, 17),)),))
    historia.registrar_accion(200, (cambio('sala', 2, 3),))
    for tiempo in (0, 25, 50, 100, 150, 200):
        consulta = historia.consultar_t(tiempo)
        print(f't={tiempo}: sala={consulta.estado.obtener("sala")}, '
              f'vida={consulta.estado.obtener("vida")}, '
              f'acciones reconstruidas={consulta.acciones_reconstruidas}')
    print('Antes de la acción #2:', historia.consultar_accion(2).estado.campos())
    historia.recortar(1)
    print('Tras recortar la segunda acción: reloj=', historia.reloj)
    historia.registrar_accion(160, (cambio('sala', 2, 4),))
    print('Nueva rama:', historia.consultar_t(160).estado.campos())
    binario = codificar_historia(historia)
    cargada = decodificar_historia(binario)
    print(f'Historia codificada: {len(binario)} bytes; '
          f'carga idéntica: {historia.exportar() == cargada.exportar()}')
    cargada.registrar_accion(200, (cambio('vida', 17, 15),))
    print('Continuación después de cargar:', cargada.consultar_t(200).estado.campos())
    print('Demostración terminada; no se inició ni modificó una partida real.')


if __name__ == '__main__':
    main()
