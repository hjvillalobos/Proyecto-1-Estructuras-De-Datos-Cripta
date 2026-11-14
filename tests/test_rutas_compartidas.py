"""IA-07 / FR-008..013: equivalencia con búsquedas frescas tras cambios."""
from unittest import TestCase
from random import Random
from modelo.rutas import ContextoRutasReales, ContextoRutasCompartidas
from utilidades.bench_parte_dos import cadena


class RutasCompartidasTest(TestCase):
    def test_campo_compartido_equivale_a_individual_con_puertas_y_objetivo_cambiantes(self):
        for semilla in range(6):
            salas = cadena(18, semilla)
            individual = ContextoRutasReales(salas)
            compartido = ContextoRutasCompartidas(salas)
            azar = Random(semilla)
            for _ in range(40):
                sala = salas[azar.randrange(len(salas) - 1)]
                sala.salidas['E']['cerrada'] = bool(azar.randrange(2))
                origen, destino = azar.sample(range(len(salas)), 2)
                for rango in (None, 100, 500):
                    self.assertEqual(compartido.buscar(origen, destino, rango),
                                     individual.buscar(origen, destino, rango))

    def test_benchmark_compara_decisiones_antes_de_reportar_tiempos(self):
        from utilidades.bench_parte_dos import medir_rutas
        from contextlib import redirect_stdout
        from io import StringIO
        salida = StringIO()
        with redirect_stdout(salida):
            medir_rutas(cadena(12, 42), 42, 3)
        self.assertIn('inestables compartido', salida.getvalue())
