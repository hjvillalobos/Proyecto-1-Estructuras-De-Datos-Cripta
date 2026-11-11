"""C33–C36: adaptador local con Inventario y LineaTiempo reales."""
import unittest
from unittest.mock import patch
from modelo.inventario import Inventario
from modelo.tipos import ObjetoInstancia


def objeto(nombre, tipo='arma'):
    return ObjetoInstancia(nombre, tipo, 'suelo', 1)


class TestInventarioHistoria(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
        except ModuleNotFoundError as error:
            if error.name != 'modelo.linea_tiempo':
                raise
            raise unittest.SkipTest('Ejecutar python -m utilidades.verificar_inventario_historia')
        from modelo.inventario_historia import campos_iniciales, CapturaInventario
        cls.Estado, cls.Historia = EstadoHistorico, LineaTiempo
        cls.base = staticmethod(campos_iniciales)
        cls.Captura = CapturaInventario

    def comprobar(self, inventario, historia):
        actual = historia.consultar_t(historia.reloj).estado.campos()
        self.assertEqual(sorted(actual), sorted(self.base(inventario)))

    def test_recoger_equipar_quitar_conserva_orden_y_cursor(self):
        """C33 / FR-020: conservar enlaces al mover un nodo intermedio."""
        inv = Inventario(5)
        h = self.Historia(self.Estado(self.base(inv)))
        for i in range(3):
            captura = self.Captura(inv)
            nodo = inv.recoger(objeto(str(i)))
            h.registrar_accion(i + 1, captura.terminar(nodo))
            self.comprobar(inv, h)
        captura = self.Captura(inv)
        inv.seleccionar('1')
        h.registrar_accion(4, captura.terminar())
        captura = self.Captura(inv)
        inv.equipar_actual('arma')
        h.registrar_accion(5, captura.terminar())
        self.comprobar(inv, h)
        self.assertEqual([o.id_instancia for o in inv], ['1', '0', '2'])
        antes = h.consultar_t(4).estado.obtener('inventario_estado')
        despues = h.consultar_t(5).estado.obtener('inventario_estado')
        self.assertEqual((antes[2], antes[5], despues[2], despues[5]), ('0', None, '1', '1'))
        captura = self.Captura(inv)
        inv.soltar_actual()
        h.registrar_accion(6, captura.terminar())
        self.comprobar(inv, h)
        self.assertIsNone(inv.arma_equipada)

    def test_quitar_del_medio_y_final_y_armadura(self):
        """C33: ambos bordes, vecinos y segundo tipo de equipo."""
        inv = Inventario(5)
        nodos = [inv.recoger(objeto(str(i))) for i in range(3)]
        h = self.Historia(self.Estado(self.base(inv)))
        captura = self.Captura(inv, nodos[1])
        inv.quitar_nodo(nodos[1])
        h.registrar_accion(1, captura.terminar())
        self.comprobar(inv, h)
        captura = self.Captura(inv)
        inv.seleccionar('2')
        h.registrar_accion(2, captura.terminar())
        captura = self.Captura(inv)
        inv.equipar_actual('armadura')
        h.registrar_accion(3, captura.terminar())
        self.comprobar(inv, h)
        for t in (4, 5):
            captura = self.Captura(inv)
            inv.soltar_actual()
            h.registrar_accion(t, captura.terminar())
            self.comprobar(inv, h)
        self.assertTrue(inv.esta_vacio())

    def test_rechazo_capacidad_y_atomicidad_de_historia(self):
        """C34 / FR-020/017: sin cambios y rechazo tras un delta válido."""
        from modelo.snapshots import CambioHistorico, ValorHistorico
        inv = Inventario(1)
        inv.recoger(objeto('a'))
        h = self.Historia(self.Estado(self.base(inv)))
        captura = self.Captura(inv)
        self.assertIsNone(inv.recoger(objeto('b')))
        self.assertEqual(captura.terminar(), ())
        captura = self.Captura(inv)
        inv.soltar_actual()
        lote = captura.terminar()
        antes = h.exportar()
        incoherente = CambioHistorico('inventario_estado', ValorHistorico(True, ('incorrecto',)), ValorHistorico(True, ()))
        with self.assertRaises(ValueError):
            h.registrar_accion(1, lote + (incoherente,))
        self.assertEqual(h.exportar(), antes)
        with self.assertRaises(ValueError):
            captura.terminar()

    def test_pergamino_consumido_sobrevive_al_recorte(self):
        """C35: corrección de D; no reemplaza usar_pergamino del motor."""
        inv = Inventario(4)
        inv.recoger(objeto('arma'))
        pergamino = inv.recoger(objeto('pergamino', 'perg'))
        h = self.Historia(self.Estado(self.base(inv)))
        h.registrar_accion(100)  # Acción sin cambios de inventario.
        from modelo.historial import HistorialRetroceso
        historial = HistorialRetroceso(None)
        historial.iniciar_turno(0)
        historial.cerrar_turno()
        captura = self.Captura(inv, pergamino)
        self.assertEqual(historial.usar_pergamino(inv, 'perg'), 0)
        h.recortar(0, correcciones=captura.terminar())
        self.comprobar(inv, h)
        self.assertEqual(inv.contar('perg'), 0)
        self.assertEqual(h.cantidad_acciones, 0)

    def test_captura_local_y_valores_independientes(self):
        """C36: operaciones locales sin recorrer lista ni base completa."""
        inv = Inventario(1001)
        for i in range(1000):
            inv.recoger(objeto(str(i)))
        inv.seleccionar('500')
        with patch.object(Inventario, '__iter__', side_effect=AssertionError('Recorrido completo')):
            captura = self.Captura(inv)
            inv.equipar_actual('arma')
            lote = captura.terminar()
        self.assertLessEqual(len(lote), 10)
        datos = tuple((c.clave, c.anterior, c.nuevo) for c in lote)
        inv.cursor.objeto.encendida = True
        self.assertEqual(tuple((c.clave, c.anterior, c.nuevo) for c in lote), datos)

    def test_encendido_y_captura_incompleta_se_validan(self):
        """C33/C34/C36: encendido explícito y no perder un nodo recogido."""
        inv = Inventario(3)
        h = self.Historia(self.Estado(self.base(inv)))
        captura = self.Captura(inv)
        nodo = inv.recoger(objeto('antorcha', 'antorcha'))
        with self.assertRaises(ValueError):
            captura.terminar()  # No puede omitir el nodo nuevo.
        h.registrar_accion(1, captura.terminar(nodo))
        captura = self.Captura(inv, nodo)
        nodo.objeto.encendida = True
        h.registrar_accion(2, captura.terminar())
        self.comprobar(inv, h)
        self.assertFalse(h.consultar_t(1).estado.obtener('inventario_nodo:antorcha')[3])
        self.assertTrue(h.consultar_t(2).estado.obtener('inventario_nodo:antorcha')[3])


if __name__ == '__main__':
    unittest.main()
