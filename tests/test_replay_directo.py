import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from controlador.aplicacion import ejecutar_juego
from controlador.controlador import ControladorJuego
from controlador.replay import ReproductorReplay
from datos.bitacora_replay import RUTA_REPLAY_PREDETERMINADA
from tests import test_regresiones_juego as base
from vista.grafica import VistaGrafica


class TestReplayDirecto(unittest.TestCase):
    def test_replay_sin_argumento_no_abre_selector_ni_modifica_modelo(self):
        d = base.TestRegresionesJuego()
        d.setUp()
        vista, lanzar = Mock(), Mock()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "ultima.log")
            c = ControladorJuego(d.motor, vista, ruta_replay=ruta, lanzador_replay=lanzar)
            c.bitacora_replay.iniciar(d.motor.meta)
            antes = d.motor.exportar_estado()
            c._replay([])
            lanzar.assert_called_once_with(ruta)
            vista.pedir_ruta_replay.assert_not_called()
            self.assertEqual(d.motor.exportar_estado(), antes)

    def test_sigue_admitiendo_archivo_explicito_y_rechaza_grabacion_incompleta(self):
        d = base.TestRegresionesJuego()
        d.setUp()
        vista, lanzar = Mock(), Mock()
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = str(Path(carpeta) / "ultima.log")
            c = ControladorJuego(d.motor, vista, ruta_replay=ruta, lanzador_replay=lanzar)
            c.bitacora_replay.iniciar(d.motor.meta)
            c._grabacion_valida = False
            c._replay([])
            lanzar.assert_not_called()
            vista.mostrar_error.assert_called_once()
            otra = Path(carpeta) / "otra.log"
            otra.write_bytes(Path(ruta).read_bytes())
            c._replay([str(otra)])
            lanzar.assert_called_once_with(str(otra))

    def test_menu_abre_ultima_y_avisa_si_no_existe(self):
        for existe in (True, False):
            with self.subTest(existe=existe):
                vista, lanzar = Mock(spec=VistaGrafica), Mock()
                def menu(replay, puntajes):
                    replay()
                    return "salir", None
                vista.mostrar_menu.side_effect = menu
                args = SimpleNamespace(gui=True, semilla=42, cripta=None)
                with patch("vista.grafica.VistaGrafica", return_value=vista), \
                        patch("controlador.aplicacion.Path.is_file", return_value=existe):
                    self.assertEqual(ejecutar_juego(args, Mock(), lanzar), 0)
                vista.pedir_ruta_replay.assert_not_called()
                if existe:
                    lanzar.assert_called_once_with(RUTA_REPLAY_PREDETERMINADA)
                else:
                    lanzar.assert_not_called()
                    vista.mostrar_error_replay.assert_called_once()

    def test_titulo_distingue_ultima_de_otro_archivo(self):
        class VistaReplaySimulada(Mock):
            def establecer_titulo_replay(self, titulo):
                self.titulo(titulo)

        for ultima in (True, False):
            vista = VistaReplaySimulada()
            meta = SimpleNamespace(cripta_id="nueva", semilla=3, version_cripta="v1", version_catalogo="c1")
            juego = Mock()
            juego.meta = SimpleNamespace(cripta_id="nueva", cripta_version="v1", catalogo_version="c1")
            vista.mostrar_replay_paso.return_value = False
            ruta = RUTA_REPLAY_PREDETERMINADA if ultima else "otra.log"
            with patch("controlador.replay.BitacoraReplay") as log:
                log.return_value.leer.return_value = (meta, [])
                ReproductorReplay(None, Mock(), vista, Mock(return_value=juego)).reproducir(ruta)
            vista.titulo.assert_called_once_with(
                "\u00daltima partida" if ultima else "Partida guardada")
