"""IA-01..06: partida completa sobre IDs/costos/contenido nuevos por semilla."""
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock

from tests.datos_prueba import crear_paquete
from datos.offline import ClienteOffline
from datos.bitacora_replay import aplicar_accion_replay
from red.cache import CacheCatalogoOrdenado
from red.catalogo import GestorCatalogo
from red.precarga import GestorPrecarga
from modelo.juego import crear_juego
from controlador.partida_historica import integrar_historia
from controlador.controlador import ControladorJuego


class PartidaGeneradaTest(TestCase):
    def test_ganar_guardar_retroceder_cargar_y_replay_en_criptas_nuevas(self):
        for semilla in (37, 509, 821):
            with self.subTest(semilla=semilla), TemporaryDirectory() as carpeta:
                raiz = Path(carpeta)
                almacen = crear_paquete(raiz / 'paquete', salas=6)
                azar = Random(semilla)
                ids = azar.sample(range(500, 4000), 6)
                costos = [azar.randint(15, 90) for _ in range(5)]
                version = f'generada-{semilla}'
                generales = almacen.leer_generales('prueba', 'v1')
                generales.update(version=version, sala_inicial=ids[0], sala_salida=ids[-1])
                almacen.guardar_generales(generales)
                salas = []
                for i, identidad in enumerate(ids):
                    salidas = {}
                    if i:
                        salidas['O'] = {'sala': ids[i - 1], 'costo': costos[i - 1]}
                    if i < 5:
                        salidas['E'] = {'sala': ids[i + 1], 'costo': costos[i]}
                    if i == 4:
                        salidas['E'].update(cerrada=True, llave='obj_0', cierre_automatico=2000)
                    if i == 5:
                        salidas['O'].update(cerrada=True, llave='obj_0', cierre_automatico=2000)
                    salas.append({'id': identidad, 'nombre': f'Generada {semilla}/{i}', 'salidas': salidas})
                    almacen.guardar_contenido('prueba', version, {
                        'sala': identidad, 'trampas': [],
                        'objetos': ['obj_0', 'arma-qa', 'luz-qa', 'perg-qa'] if i == 0 else [],
                        'enemigos': [] if i in (0, 5) else [{'instancia': f'guardia-{i}', 'tipo': 'enemigo-qa'}]})
                almacen.guardar_pagina('prueba', version, {'pagina': 1, 'total_paginas': 1, 'salas': salas})
                almacen.guardar_llaves('prueba', version, {'llaves': [{'id': 'obj_0', 'sala': ids[0]}]})
                for ficha in (
                    {'id': 'arma-qa', 'clase': 'arma', 'nombre': 'Arma nueva', 'ataque_bonus': 3},
                    {'id': 'luz-qa', 'clase': 'antorcha', 'nombre': 'Luz nueva', 'duracion': 10000},
                    {'id': 'perg-qa', 'clase': 'pergamino_retroceso', 'nombre': 'Pergamino nuevo'},
                    {'id': 'enemigo-qa', 'clase': 'enemigo', 'nombre': 'Guardián nuevo', 'vida_max': 5,
                     'ataque': 1, 'defensa': 0, 'velocidad': 100, 'comportamiento': 'guardian', 'suelta': []},
                ):
                    almacen.guardar_ficha('cat1', ficha)

                def preparar():
                    cliente = ClienteOffline(almacen.carpeta)
                    precarga = GestorPrecarga(cliente, GestorCatalogo(cliente, CacheCatalogoOrdenado(25), cliente.almacen))
                    juego = integrar_historia(crear_juego(precarga, 'prueba', semilla,
                        version_cripta=version, version_catalogo='cat1', partida_completa=True), 2)
                    return cliente, precarga, juego

                cliente, precarga, juego = preparar()
                self.addCleanup(cliente.cerrar)
                self.addCleanup(precarga.cerrar)
                vista = Mock()
                control = ControladorJuego(juego, vista, str(raiz / 'partida.log'), partida_p2=True)
                control.bitacora_replay.iniciar(juego.meta)

                def actuar(texto):
                    control.procesar_comando(texto)
                    vista.mostrar_error.assert_not_called()

                for tipo in ('obj_0', 'arma-qa', 'luz-qa', 'perg-qa'):
                    objeto = next(o for o in juego.objetos_en_suelo[ids[0]] if o.tipo_catalogo == tipo)
                    actuar('recoger ' + objeto.id_instancia)
                arma = next(o.id_instancia for o in juego.jugador.inventario if o.tipo_catalogo == 'arma-qa')
                luz = next(o.id_instancia for o in juego.jugador.inventario if o.tipo_catalogo == 'luz-qa')
                actuar('equipar ' + arma)
                actuar('usar ' + luz)
                guardado, mapa = juego.exportar_estado(), juego.mapa_conocido()
                ruta = raiz / 'guardado con espacios.bin'
                actuar(f'guardar "{ruta}"')
                actuar('mover E')
                actuar('atacar guardia-1')
                frontera = juego.reloj, juego.jugador.vida, juego.azar.getstate()
                actuar('retroceso')
                self.assertEqual(juego.jugador.inventario.contar('perg-qa'), 0)
                actuar('atacar guardia-1')
                self.assertEqual((juego.reloj, juego.jugador.vida, juego.azar.getstate()), frontera)
                actuar(f'cargar "{ruta}"')
                self.assertEqual(juego.exportar_estado(), guardado)
                self.assertEqual(juego.mapa_conocido(), mapa)
                for i in range(1, 6):
                    if i == 5:
                        actuar('abrir E')
                    actuar('mover E')
                    if i < 5:
                        actuar(f'atacar guardia-{i}')
                self.assertEqual(juego.resultado, 'victoria')
                esperado = juego.exportar_estado()
                ruta.unlink()  # El replay debe usar la carga embebida en el log.
                cliente2, precarga2, repetida = preparar()
                try:
                    for accion in control.bitacora_replay.leer()[1]:
                        self.assertTrue(aplicar_accion_replay(repetida, accion).ok)
                    self.assertEqual(repetida.exportar_estado(), esperado)
                    self.assertEqual(repetida.mapa_conocido(), juego.mapa_conocido())
                    self.assertEqual(cliente.solicitudes_realizadas + cliente2.solicitudes_realizadas, 0)
                finally:
                    precarga2.cerrar()
                    cliente2.cerrar()
