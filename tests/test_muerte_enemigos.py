import tempfile
import tkinter as tk
import unittest
from pathlib import Path

from datos.guardado_binario import cargar_estado, guardar_estado
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica


class TestMuerteEnemigos(unittest.TestCase):
    def setUp(self):
        self.datos = base.TestRegresionesJuego()
        self.datos.setUp()
        self.motor = self.datos.motor

    def matar(self, regeneracion=False):
        if regeneracion:
            self.datos.fichas[-1].atributos["regeneracion"] = 3
        enemigo = self.datos._enemigo()
        enemigo.vida = 1
        evento = enemigo.evento_pendiente
        self.assertTrue(self.motor.ejecutar("atacar", enemigo.id_instancia).ok)
        self.assertEqual(enemigo.vida, 0)
        self.assertTrue(evento.cancelado)
        self.assertIsNone(enemigo.evento_pendiente)
        self.assertEqual(self.motor.estado_vista().enemigos, [])
        return enemigo

    def test_muerto_no_ataca_no_regenera_y_no_duplica_botin(self):
        enemigo = self.matar(regeneracion=True)
        vida = self.motor.jugador.vida
        antes = self.motor.exportar_estado()
        self.assertFalse(self.motor.ejecutar("atacar", enemigo.id_instancia).ok)
        self.assertEqual(self.motor.exportar_estado(), antes)
        for _ in range(4):
            self.assertTrue(self.motor.ejecutar("esperar").ok)
        self.assertEqual(self.motor.jugador.vida, vida)
        self.assertEqual(enemigo.vida, 0)
        self.assertEqual(self.motor.enemigos_derrotados, 1)
        self.assertEqual(len(self.motor.objetos_en_suelo[1]), 1)
        self.assertFalse(any(e.tipo == "turno_enemigo" and e.referencia is enemigo
                             for e in self.motor.cola.pendientes()))
        botin = self.motor.objetos_en_suelo[1][0]
        self.assertTrue(self.motor.ejecutar("recoger", botin.id_instancia).ok)
        self.assertTrue(self.motor.ejecutar("usar", botin.id_instancia).ok)

    def test_guardar_cargar_no_resucita_ni_repite_botin(self):
        self.matar(regeneracion=True)
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "muerte.bin"
            guardar_estado(self.motor.exportar_estado(), str(ruta))
            self.motor.restaurar_estado(cargar_estado(str(ruta)))
        self.assertEqual(self.motor.estado_vista().enemigos, [])
        for _ in range(3):
            self.assertTrue(self.motor.ejecutar("esperar").ok)
        self.assertEqual(self.motor.enemigos_derrotados, 1)
        self.assertEqual(len(self.motor.objetos_en_suelo[1]), 1)
        self.assertEqual(self.motor.estado_vista().enemigos, [])

    def test_retroceso_restaura_enemigo_agenda_y_retira_botin(self):
        self.datos._inventario("pergamino")
        enemigo = self.matar(regeneracion=True)
        self.assertTrue(self.motor.ejecutar("retroceso").ok)
        self.assertEqual(enemigo.vida, 1)
        self.assertEqual(self.motor.enemigos_derrotados, 0)
        self.assertEqual(self.motor.objetos_en_suelo[1], [])
        self.assertFalse(enemigo.evento_pendiente.cancelado)
        self.assertEqual(len(self.motor.estado_vista().enemigos), 1)
        self.assertTrue(self.motor.ejecutar("atacar", enemigo.id_instancia).ok)
        self.assertEqual(self.motor.enemigos_derrotados, 1)
        self.assertEqual(len(self.motor.objetos_en_suelo[1]), 1)

    def test_vista_retira_el_enemigo_y_muestra_su_botin(self):
        try:
            vista = VistaGrafica()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(vista.cerrar)
        vista.root.withdraw()
        enemigo = self.datos._enemigo()
        enemigo.vida = 1
        vista.mostrar_estado(self.motor.estado_vista(), [])
        self.assertTrue(vista.canvas.find_withtag("enemigo_0"))
        self.assertTrue(self.motor.ejecutar("atacar", enemigo.id_instancia).ok)
        vista.preparar_animacion("atacar")
        vista.mostrar_estado(self.motor.estado_vista(), [])
        self.assertFalse(vista.canvas.find_withtag("enemigo_0"))
        self.assertTrue(vista.canvas.find_withtag("objeto_0"))
        despues = self.motor.exportar_estado()
        vista.escena.animacion.situar(40)
        self.assertEqual(self.motor.exportar_estado(), despues)
