import time

from datos.bitacora_replay import BitacoraReplay, ErrorReplay, ReplayIncompatible, aplicar_accion_replay
from vista.bitacora_pantalla import BufferCircular


class ReproductorReplay:

    def __init__(self, cliente, gestor_precarga, vista, crear_juego):
        self._precarga = gestor_precarga
        self._vista = vista
        self._crear_juego = crear_juego

    def reproducir(self, ruta):
        bitacora = BitacoraReplay(ruta)
        try:
            meta, acciones = bitacora.leer()
        except ErrorReplay as e:
            self._vista.mostrar_error(str(e))
            return

        mensajes = BufferCircular(20)
        total = len(acciones)
        usa_paso = hasattr(self._vista, "mostrar_replay_paso")

        if hasattr(self._vista, "modo_replay"):
            self._vista.modo_replay()

        def mostrar(juego, paso):
            estado = juego.estado_vista()
            if usa_paso:
                return self._vista.mostrar_replay_paso(estado, mensajes.ultimos(), paso, total,
                                                     inventario=juego.inventario_vista())
            self._vista.mostrar_estado(estado, mensajes.ultimos())
            time.sleep(0.8)
            return True

        # estado inicial
        try:
            juego = self._crear_juego(
                self._precarga, meta.cripta_id, meta.semilla,
                version_cripta=meta.version_cripta, version_catalogo=meta.version_catalogo)
            if (juego.meta.cripta_id != meta.cripta_id
                    or juego.meta.cripta_version != meta.version_cripta
                    or juego.meta.catalogo_version != meta.version_catalogo):
                raise ReplayIncompatible("Las versiones cargadas no coinciden con el replay.")
        except Exception as e:
            self._vista.mostrar_error(f"No se pudo cargar la cripta: {e}")
            return

        if not mostrar(juego, 0):
            return
        if callable(getattr(type(juego), "establecer_notificador", None)):
            juego.establecer_notificador(mensajes.agregar)

        for i, accion in enumerate(acciones, start=1):
            try:
                resultado = aplicar_accion_replay(juego, accion)
            except ErrorReplay as error:
                self._vista.mostrar_error(str(error))
                return
            if not resultado.ok:
                self._vista.mostrar_error(
                    f"Acción inválida en paso {i}: {accion.accion} {accion.argumento}"
                )
                return
            arg = f" {accion.argumento}" if accion.argumento and accion.accion != "cargar" else ""
            mensajes.agregar(f"► {accion.accion}{arg}")
            if not mostrar(juego, i):
                return

        if hasattr(juego, "resumen"):
            self._vista.mostrar_fin(juego.resumen())
