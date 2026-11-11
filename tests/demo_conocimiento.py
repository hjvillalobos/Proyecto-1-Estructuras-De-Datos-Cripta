"""Demostración sintética por consola; no modifica partidas ni interfaz."""
from modelo.conocimiento import (
    ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible,
    AVISTADA,
)


def mostrar(titulo, mapa):
    print(f"\n{titulo}")
    for identificador, estado, nombre, salidas in mapa.mapa_conocido():
        if estado == AVISTADA:
            print(f"  Sala {identificador}: avistada (sin nombre ni salidas conocidas)")
        else:
            print(f"  Sala {identificador}: {nombre}, explorada")
            for direccion, destino, costo, puerta, recuerdo in salidas:
                estado_puerta = ("sin puerta" if puerta is None else
                                 "sin observar" if recuerdo is None else
                                 "recordada cerrada" if recuerdo else "recordada abierta")
                print(f"    {direccion} -> {destino}, costo {costo}, {estado_puerta}")


def main():
    salas = (
        SalaConocible(10, "Entrada de prueba", (SalidaConocible("E", 20, 100, 7),)),
        SalaConocible(20, "Galería de prueba", (
            SalidaConocible("O", 10, 100, 7), SalidaConocible("N", 30, 25))),
        SalaConocible(30, "Sala de prueba", (SalidaConocible("S", 20, 25),)),
    )
    mapa = ConocimientoMapa(salas, (PuertaConocible(7, 10, 20),), 10)
    inicial = mapa.mapa_conocido()
    print("Demostración independiente de conocimiento. No es una partida del juego.")
    mostrar("1. Estado inicial", mapa)
    observacion = mapa.observar_puerta(10, 7, False)
    mostrar("2. Puerta observada abierta desde la entrada", mapa)
    entrada = mapa.entrar(20)
    mostrar("3. Entrada física a la galería: aparece otra sala avistada", mapa)
    cierre = mapa.observar_puerta(20, 7, True)
    mostrar("4. Nueva observación desde el otro extremo", mapa)
    mapa.revertir(cierre)
    mapa.revertir(entrada)
    mapa.revertir(observacion)
    assert mapa.mapa_conocido() == inicial
    mostrar("5. Cambios invertidos: se recuperó exactamente el mapa inicial", mapa)


if __name__ == "__main__":
    main()
