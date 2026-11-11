import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from controlador.controlador import ControladorJuego
from controlador.presentacion_conocimiento import inventario_historico, lineas_mapa
from controlador.resumen_historia import resumir
from datos.historia_binaria import codificar_historia, decodificar_historia
from modelo.conocimiento_historia import campos_iniciales as base_mapa, convertir_cambios
from modelo.errores_historia import CambioHistoriaIncoherente
from modelo.inventario import Inventario
from modelo.inventario_historia import campos_iniciales as base_inventario, CapturaInventario
from modelo.linea_tiempo import EstadoHistorico, LineaTiempo
from modelo.snapshots import ResultadoAccion
from modelo.tipos import ObjetoInstancia
from modelo.viaje import ResultadoPaso
from tests.test_conocimiento import crear


class PresentacionConocimientoTest(unittest.TestCase):
    def preparar(self):
        mapa = crear()
        inv = Inventario(4)
        for identidad in ("z", "a", "m"):
            inv.recoger(ObjetoInstancia(identidad, "arma", "suelo", 10))
        base = (("sala", (10, "Entrada")), ("jugador", (20, 20, 5, 3, 100)),
                ("efectos", ()))
        return mapa, inv, LineaTiempo(EstadoHistorico(base + base_mapa(mapa) + base_inventario(inv)), 2)

    def test_fr018_mapa_real_filtrado_y_memoria_sin_tocar_conocimiento(self):
        mapa = crear()
        modelo = SimpleNamespace(mapa_conocido=mapa.mapa_conocido)
        vista = Mock()
        control = ControladorJuego(modelo, vista)
        antes = mapa.mapa_conocido(), mapa.revision
        with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")):
            control.procesar_comando("mapa")
        texto = vista.mostrar_info.call_args.args[0]
        self.assertIn("Sala 10 · Entrada: explorada", texto)
        self.assertIn("Sala 9000: avistada", texto)
        self.assertIn("E → sala 9000 | costo 100 | puerta 7: sin observar", texto)
        self.assertNotIn("Galería", texto)
        self.assertNotIn("Secreto", texto)
        self.assertNotIn("42", texto)
        self.assertEqual((mapa.mapa_conocido(), mapa.revision), antes)
        mapa.observar_puerta(10, 7, False)
        self.assertIn("abierta (recuerdo)", "\n".join(lineas_mapa(mapa.mapa_conocido())))
        mapa.observar_puerta(10, 7, True)
        self.assertIn("cerrada (recuerdo)", "\n".join(lineas_mapa(mapa.mapa_conocido())))

    def test_fr018_conserva_proveedor_de_lineas_y_mapa_vacio(self):
        self.assertEqual(lineas_mapa(("Sala 1: explorada",)), ["Sala 1: explorada"])
        vista = Mock()
        control = ControladorJuego(SimpleNamespace(mapa_conocido=lambda: ()), vista)
        control.procesar_comando("mapa")
        vista.mostrar_info.assert_called_once_with("El mapa está vacío.")

    def test_fr004_fr007_fr011_historia_con_deltas_reales_de_c_y_binario(self):
        mapa, inv, historia = self.preparar()
        antes = historia.exportar()
        captura = CapturaInventario(inv)
        inv.seleccionar("a")
        inv.equipar_actual("arma")
        cambios_mapa = mapa.entrar(9000) + mapa.observar_puerta(9000, 7, True)
        historia.registrar_accion(100, captura.terminar() + convertir_cambios(cambios_mapa))
        historia.registrar_accion(200)
        vivo = historia.exportar(), mapa.mapa_conocido(), base_inventario(inv)
        for h in (historia, decodificar_historia(codificar_historia(historia))):
            with patch("requests.sessions.Session.request", side_effect=AssertionError("HTTP")):
                pasado = resumir(h.consultar_t(0))
                cierre = resumir(h.consultar_t(100))
            self.assertLess(pasado.index("[z]"), pasado.index("[a]"))
            self.assertIn("Sala 9000: avistada", pasado)
            self.assertNotIn("Sala 42", pasado)
            self.assertNotIn("Puerta 7:", pasado)
            self.assertLess(cierre.index("[a]"), cierre.index("[z]"))
            self.assertIn("arma [a] (equipado) (cursor)", cierre)
            self.assertIn("Sala 9000: explorada", cierre)
            self.assertIn("Sala 42: avistada", cierre)
            self.assertIn("Puerta 7: cerrada (recuerdo)", cierre)
            self.assertEqual(resumir(h.consultar_accion(2)), cierre)
        self.assertEqual((historia.exportar(), mapa.mapa_conocido(), base_inventario(inv)), vivo)
        historia.recortar(0)
        self.assertEqual(historia.exportar().estado_inicial, antes.estado_inicial)
        self.assertEqual(resumir(historia.consultar_t(0)), pasado)

    def test_fr004_inventario_vacio_de_c_prevalece_sobre_proyeccion_anterior(self):
        _, _, historia = self.preparar()
        base = historia.consultar_t(0).estado.campos()
        base = tuple((k, v) for k, v in base if not k.startswith("inventario_"))
        estado = EstadoHistorico(base + base_inventario(Inventario(4)) +
                                (("inventario:00", ("viejo", "arma", True)),))
        self.assertIn("Inventario: vacío", resumir(SimpleNamespace(estado=estado, reloj=0)))

    def test_fr005_inventario_incoherente_falla_sin_recorrer_ciclos(self):
        for meta, nodos in (
                ((4, 1, "a", "a", "a", None, None), ()),
                ((4, 1, "a", "a", "a", None, None),
                 (("inventario_nodo:a", ("arma", "suelo", 10, False, None, "a")),))):
            with self.subTest(meta=meta, nodos=nodos), self.assertRaises(CambioHistoriaIncoherente):
                inventario_historico(EstadoHistorico((("inventario_estado", meta),) + nodos))

    def test_fr019_resultado_completo_conserva_booleano_replay_y_trampas(self):
        hechos = ResultadoPaso(2, True, True, True, True, False)
        resultado = ResultadoAccion(True, "Paso terminado", ["trampa"], hechos)
        modelo = SimpleNamespace(ejecutar=Mock(return_value=resultado))
        vista = Mock()
        control = ControladorJuego(modelo, vista)
        control.bitacora_replay = Mock()
        self.assertIs(control._accion_modelo("mover", "E"), True)
        self.assertIs(control.ultimo_resultado_accion.hechos_paso, hechos)
        control.bitacora_replay.registrar_accion.assert_called_once_with("mover", "E")
        rechazado = ResultadoAccion(False, "Cerrada")
        modelo.ejecutar.return_value = rechazado
        self.assertIs(control._accion_modelo("mover", "N"), False)
        self.assertIs(control.ultimo_resultado_accion, rechazado)
        control.bitacora_replay.registrar_accion.assert_called_once()
        modelo.ejecutar.side_effect = RuntimeError("fallo")
        with self.assertRaises(RuntimeError):
            control._accion_modelo("mover", "N")
        self.assertIsNone(control.ultimo_resultado_accion)
        self.assertIsNone(ResultadoAccion(True).hechos_paso)
