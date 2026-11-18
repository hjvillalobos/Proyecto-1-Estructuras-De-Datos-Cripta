import unittest
import wave
from array import array
from pathlib import Path
from unittest.mock import Mock

from vista.musica_partida import MusicaPartida
from vista.sonidos import Sonidos


class TestMusicaPartida(unittest.TestCase):
    def setUp(self):
        self.root = Mock()
        self.mezclador = Mock()
        self.mezclador.get_init.return_value = None
        self.canales = [Mock(), Mock()]
        self.mezclador.Channel.side_effect = self.canales
        self.musica = MusicaPartida(self.root, self.mezclador)
        self.addCleanup(self.musica.cerrar)

    def completar_transicion(self):
        for _ in range(30):
            if self.musica.pendiente is None:
                break
            self.musica._mezclar()
        self.assertIsNone(self.musica.pendiente)

    def test_cambio_gradual_sin_reiniciar_pistas(self):
        self.musica.actualizar(False)
        self.completar_transicion()
        self.canales[0].set_volume.assert_called_with(.6)
        self.canales[1].set_volume.assert_called_with(0)
        self.musica.actualizar(True)
        self.assertGreater(self.musica.tension, 0)
        self.assertLess(self.musica.tension, 1)
        self.completar_transicion()
        self.canales[0].set_volume.assert_called_with(0)
        self.canales[1].set_volume.assert_called_with(.6)
        self.musica.actualizar(False)
        self.completar_transicion()
        for canal in self.canales:
            canal.play.assert_called_once()
            self.assertEqual(canal.play.call_args.kwargs, {"loops": -1})

    def test_estado_estable_no_programa_trabajo(self):
        self.musica.actualizar(True)
        self.completar_transicion()
        self.root.after.reset_mock()
        for _ in range(1000):
            self.musica.actualizar(True)
        self.root.after.assert_not_called()

    def test_silenciar_reactivar_y_fin_de_partida(self):
        sonido = Sonidos(Mock(), root=self.root)
        sonido._musica_partida = self.musica
        sonido.activo = True
        sonido.actualizar_partida(True)
        self.assertTrue(self.musica.activa)
        sonido.habilitar(False)
        self.assertFalse(self.musica.activa)
        self.assertIsNone(self.musica.pendiente)
        sonido.habilitar(True)
        self.assertTrue(self.musica.activa)
        sonido.habilitar(False)
        sonido.reproducir("inicio")
        sonido.habilitar(True)
        self.assertFalse(self.musica.activa)

    def test_pistas_misma_duracion_y_union_continua(self):
        longitudes = []
        for nombre in ("calma", "tension"):
            with wave.open(str(Path("vista/recursos/sonidos") / ("pasillos_" + nombre + ".wav")), "rb") as archivo:
                self.assertEqual(archivo.getnchannels(), 2)
                self.assertEqual(archivo.getsampwidth(), 2)
                longitudes.append(archivo.getnframes())
                muestras = array("h", archivo.readframes(archivo.getnframes()))
            for canal in range(2):
                cercanas = muestras[canal:2000:2]
                salto = abs(muestras[-2 + canal] - muestras[canal])
                self.assertLessEqual(salto, max(abs(b - a) for a, b in zip(cercanas, cercanas[1:])))
        self.assertEqual(longitudes[0], longitudes[1])
