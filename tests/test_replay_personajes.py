"""RP-01/UI: replay offline renderizado con ambas apariencias, sin alterar la grabación."""
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import main
from datos.historia_binaria import codificar_historia
from dataclasses import replace
from tests.test_replay_grafico import grabacion
from vista.grafica import VistaGrafica
from vista.recursos_graficos import ImageTk


class ReplayPersonajesTest(TestCase):
    def test_replay_real_con_tigre_y_tigresa_conserva_estado_log_y_guardado(self):
        imagenes=[]
        with grabacion() as (_,original,ruta,guardado,nueva):
            antes=original.exportar_estado(),ruta.read_bytes(),guardado.read_bytes()
            for personaje in ('jugador','tigresa'):
                with self.subTest(personaje=personaje):
                    with patch('vista.grafica.leer_personaje',return_value=personaje):
                        vista=VistaGrafica()
                    self.addCleanup(vista.cerrar)
                    vista.root.withdraw()
                    imagenes.append(ImageTk.getimage(vista.recursos.imagen('jugador',230,196)).tobytes())
                    pasos=[]
                    mostrar=VistaGrafica.mostrar_replay_paso.__get__(vista)
                    def registrar(estado,mensajes,paso,total,inventario=None):
                        pasos.append((paso,estado.sala_id,estado.vida,vista.recursos.personaje))
                        return mostrar(estado,mensajes,paso,total,inventario)
                    juegos=[]
                    from modelo.juego import crear_juego
                    def fabrica(*args,**kwargs):
                        juego=crear_juego(*args,**kwargs)
                        juegos.append(juego)
                        return juego
                    with patch('vista.grafica.VistaGrafica',return_value=vista), \
                         patch('modelo.juego.crear_juego',side_effect=fabrica), \
                         patch.object(vista,'mostrar_replay_paso',side_effect=registrar), \
                         patch.object(vista,'_pausa_replay',return_value=0), \
                         patch.object(vista,'mostrar_fin') as fin, \
                         patch.object(vista,'mostrar_error_replay') as errores, \
                         patch('requests.sessions.Session.request',side_effect=AssertionError('HTTP durante offline')):
                        resultado=main.ejecutar_replay_grafico(
                            SimpleNamespace(replay_grafico=str(ruta),checkpoint_cada=2),nueva())
                    self.assertEqual(resultado,0)
                    errores.assert_not_called()
                    fin.assert_called_once()
                    self.assertEqual([p[0] for p in pasos],list(range(7)))
                    self.assertTrue(all(p[3]==personaje for p in pasos))
                    self.assertEqual(pasos[-1][1:3],(original.estado_vista().sala_id,original.estado_vista().vida))
                    self.assertEqual(replace(juegos[0].exportar_estado(),
                        historia=codificar_historia(juegos[0]._historia_h3)),antes[0])
                    self.assertEqual((original.exportar_estado(),ruta.read_bytes(),guardado.read_bytes()),antes)
            self.assertNotEqual(imagenes[0],imagenes[1])
