import time

from datos.bitacora_replay import BitacoraReplay, ErrorReplay
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
                return self._vista.mostrar_replay_paso(estado, mensajes.ultimos(), paso, total)
            self._vista.mostrar_estado(estado, mensajes.ultimos())
            time.sleep(0.8)
            return True

        # estado inicial
        try:
            juego = self._crear_juego(self._precarga, meta.cripta_id, meta.semilla)
        except Exception as e:
            self._vista.mostrar_error(f"No se pudo cargar la cripta: {e}")
            return

        if not mostrar(juego, 0):
            return

        for i, accion in enumerate(acciones, start=1):
            resultado = juego.ejecutar(accion.accion, accion.argumento)
            if not resultado.ok:
                self._vista.mostrar_error(
                    f"Acción inválida en paso {i}: {accion.accion} {accion.argumento}"
                )
                return
            arg = f" {accion.argumento}" if accion.argumento else ""
            mensajes.agregar(f"► {accion.accion}{arg}")
            if not mostrar(juego, i):
                return

        if hasattr(juego, "resumen"):
            self._vista.mostrar_fin(juego.resumen())
