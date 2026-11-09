"""C17: oráculo independiente y carga reproducible de exploración/reversión."""
import random
import unittest

from modelo.conocimiento import (
    ConocimientoMapa, SalaConocible, SalidaConocible, PuertaConocible,
)


class TestSecuenciasConocimiento(unittest.TestCase):
    def test_secuencia_larga_reconstruye_y_revierte(self):
        n = 23
        salas = tuple(SalaConocible(i * 101, str(i), (
            SalidaConocible("E", ((i + 1) % n) * 101, 3, i),
            SalidaConocible("O", ((i - 1) % n) * 101, 3, (i - 1) % n),
        )) for i in range(n))
        puertas = tuple(PuertaConocible(i, i * 101, ((i + 1) % n) * 101) for i in range(n))
        mapa = ConocimientoMapa(salas, puertas, 0)
        copia = ConocimientoMapa(tuple(reversed(salas)), puertas, 0)
        estados = [0] * n
        estados[0], estados[1], estados[-1] = 2, 1, 1
        recuerdos = [None] * n
        pasos = []
        rng = random.Random(20261109)
        posicion = 0

        def comprobar(objeto):
            for i in range(n):
                self.assertEqual(objeto.estado_sala(i * 101), estados[i])
                self.assertIs(objeto.recuerdo_puerta(i), recuerdos[i])
            visibles = objeto.mapa_conocido()
            self.assertEqual(len(visibles), sum(e != 0 for e in estados))
            for identificador, estado, nombre, salidas in visibles:
                if estado == 1:
                    self.assertIsNone(nombre)
                    self.assertEqual(salidas, ())

        for _ in range(1000):
            # Copias completas solo en el oráculo de pruebas, nunca producción.
            antes = (estados[:], recuerdos[:])
            if rng.randrange(2):
                posicion = (posicion + (1 if rng.randrange(2) else -1)) % n
                cambios = mapa.entrar(posicion * 101)
                estados[posicion] = 2
                for vecino in ((posicion + 1) % n, (posicion - 1) % n):
                    estados[vecino] = max(estados[vecino], 1)
            else:
                puerta = posicion if rng.randrange(2) else (posicion - 1) % n
                cerrada = bool(rng.randrange(2))
                cambios = mapa.observar_puerta(posicion * 101, puerta, cerrada)
                recuerdos[puerta] = cerrada
            copia.aplicar(cambios)
            pasos.append((cambios, antes))
            comprobar(mapa)
            comprobar(copia)
        for cambios, (estados, recuerdos) in reversed(pasos):
            mapa.revertir(cambios)
            copia.revertir(cambios)
            comprobar(mapa)
            comprobar(copia)

    def test_puertas_paralelas_y_componente_desconectado(self):
        salas = (
            SalaConocible(1, "A", (SalidaConocible("N", 2, 1, 5), SalidaConocible("E", 2, 9, 8))),
            SalaConocible(2, "B", (SalidaConocible("S", 1, 1, 5), SalidaConocible("O", 1, 9, 8))),
            SalaConocible(999, "Aislada", ()),
        )
        m = ConocimientoMapa(salas, (PuertaConocible(5, 1, 2), PuertaConocible(8, 1, 2)), 1)
        m.observar_puerta(1, 5, False)
        m.observar_puerta(1, 8, True)
        m.entrar(2)
        self.assertIs(m.recuerdo_puerta(5), False)
        self.assertIs(m.recuerdo_puerta(8), True)
        self.assertEqual(m.estado_sala(999), 0)
        self.assertEqual(len(m.mapa_conocido()), 2)


if __name__ == "__main__":
    unittest.main()
