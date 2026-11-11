import os
from subprocess import CalledProcessError

from controlador.resumen_historia import consultar, resumir
from controlador.presentacion_conocimiento import lineas_mapa
from modelo.errores_historia import ErrorHistoria
from modelo.viaje import ControlViaje, ResultadoPaso
from datos.bitacora_replay import BitacoraReplay, RUTA_REPLAY_PREDETERMINADA
from datos.guardado_binario import (
    guardar_estado, cargar_estado, cargar_estado_partida, RUTA_GUARDADO_PREDETERMINADA,
)
from datos.puntajes import RegistroPuntaje
from vista.bitacora_pantalla import BufferCircular


DIRECCIONES = {
    "n": "N",
    "s": "S",
    "e": "E",
    "o": "O",
    "norte": "N",
    "sur": "S",
    "este": "E",
    "oeste": "O",
    "N": "N",
    "S": "S",
    "E": "E",
    "O": "O",
}


class ControladorJuego:

    def __init__(
        self,
        modelo,
        vista,
        ruta_replay=RUTA_REPLAY_PREDETERMINADA,
        tabla_puntajes=None,
        lanzador_replay=None,
        partida_p2=False,
        control_viaje=None,
    ):
        self.modelo = modelo
        self.vista = vista
        self.partida_p2 = partida_p2

        self.mensajes = BufferCircular(20)
        self._modelo_notifica = callable(getattr(type(modelo), "establecer_notificador", None))
        if self._modelo_notifica:
            modelo.establecer_notificador(self.notificar)

        self.bitacora_replay = BitacoraReplay(ruta_replay)

        self.tabla_puntajes = tabla_puntajes

        # función(ruta) que abre un replay; la entrega main.py
        self.lanzador_replay = lanzador_replay

        self.ejecutando = True
        self._puntaje_registrado = False
        self._grabacion_valida = True
        self.ultimo_resultado_accion = None
        self._control_viaje_inyectado = control_viaje
        self.control_viaje = self._obtener_control_viaje()
        self._viaje_activo = False
        self._paso_rechazado = None

    # ---------------------------------------------------------
    # BITÁCORA EN PANTALLA
    # ---------------------------------------------------------

    def notificar(self, mensaje):
        self.mensajes.agregar(str(mensaje))

    # ---------------------------------------------------------
    # INICIAR
    # ---------------------------------------------------------

    def iniciar(self, estado_inicial=None):
        self._cancelar_viaje(mostrar=False)

    # Iniciar bitácora de replay.
        if hasattr(self.modelo, "meta"):
            try:
                self.bitacora_replay.iniciar(self.modelo.meta)
            except OSError as error:
                self._fallo_grabacion(error)
                return False

        self.notificar("Partida iniciada.")
        if estado_inicial is not None:
            try:
                self.modelo.restaurar_estado(estado_inicial)
                self.bitacora_replay.registrar_carga(estado_inicial)
            except OSError as error:
                self._fallo_grabacion(error)
                return False
            except Exception as error:
                self.ejecutando = False
                if callable(getattr(type(self.vista), "mostrar_error_replay", None)):
                    self.vista.mostrar_error_replay(f"No se pudo cargar: {error}")
                else:
                    self.vista.mostrar_error(f"No se pudo cargar: {error}")
                return False
        self.vista.mostrar_ayuda()

        while self.ejecutando:

            # Si el modelo ya terminó, no pedir otro comando.
            if getattr(self.modelo, "terminado", False):
                break

            self._mostrar_estado()

            try:
                if self._viaje_activo and callable(getattr(type(self.vista), "pedir_comando_viaje", None)):
                    comando = self.vista.pedir_comando_viaje()
                else:
                    comando = self.vista.pedir_comando()
            except (EOFError, KeyboardInterrupt):
                self.vista.mostrar_info("\nPartida interrumpida.")
                break

            if comando is None:
                break

            comando = comando.strip()

            if not comando:
                if self._viaje_activo:
                    try:
                        self._avanzar_viaje()
                    except KeyboardInterrupt:
                        self._cancelar_viaje()
                    except Exception as error:
                        self._cancelar_viaje(mostrar=False)
                        self.vista.mostrar_error(f"Viaje detenido: {error}")
                continue

            try:
                self.procesar_comando(comando)

            except KeyboardInterrupt:
                self.vista.mostrar_info(
                    "\nPartida interrumpida."
                )
                break

            except Exception as error:
                self.vista.mostrar_error(
                    f"Error: {error}"
                )

            # La acción pudo haber causado victoria o derrota.
            if getattr(self.modelo, "terminado", False):
                break

        self._cancelar_viaje(mostrar=False)
        # Mostrar el último estado para que se vea cómo terminó.
        if getattr(self.modelo, "terminado", False):
            self._mostrar_estado()
            self._registrar_puntaje()

            if hasattr(self.modelo, "resumen"):
                self.vista.mostrar_fin(
                    self.modelo.resumen()
                )

        self.vista.mostrar_info(
            "Sesión finalizada."
        )
        return True

    # ---------------------------------------------------------
    # ESTADO
    # ---------------------------------------------------------

    def _mostrar_estado(self):
        estado = self.modelo.estado_vista()
        salas = getattr(self.modelo, "salas", None)
        if isinstance(salas, list) and 0 <= estado.sala_id < len(salas):
            sala = salas[estado.sala_id]
            if sala is not None:
                for salida in estado.salidas:
                    salida.costo = sala.salidas.get(salida.direccion, {}).get("costo", 100)

        self.vista.mostrar_estado(
            estado,
            self.mensajes.ultimos(),
        )

    def _registrar_puntaje(self):
        if self.tabla_puntajes is None or self._puntaje_registrado or not self.modelo.terminado:
            return
        resumen = self.modelo.resumen()
        meta = self.modelo.meta
        try:
            nombre = self.vista.pedir_texto("Nombre para la tabla de puntajes:") or "Jugador"
        except (EOFError, KeyboardInterrupt):
            nombre = "Jugador"
        try:
            self.tabla_puntajes.registrar(RegistroPuntaje(
                nombre=nombre, cripta_id=meta.cripta_id, cripta_version=meta.cripta_version,
                acciones=resumen.acciones, derrotados=resumen.derrotados,
                tiempo_final=resumen.reloj_final, resultado=resumen.resultado))
        except OSError as error:
            self.vista.mostrar_error(f"No se pudo registrar el puntaje: {error}")
            return
        self._puntaje_registrado = True

    # ---------------------------------------------------------
    # PARSEAR COMANDOS
    # ---------------------------------------------------------

    def procesar_comando(self, texto):

        partes = texto.split(maxsplit=1)
        if not partes:
            return

        comando = partes[0].lower()

        if comando in ("guardar", "cargar", "replay"):
            ruta = partes[1].strip() if len(partes) > 1 else ""
            if len(ruta) >= 2 and ruta[0] == ruta[-1] and ruta[0] in ("\"", "'"):
                ruta = ruta[1:-1]
            argumentos = [ruta] if ruta else []
        else:
            argumentos = partes[1].split() if len(partes) > 1 else []

        if comando == "cancelar":
            if argumentos:
                return self.vista.mostrar_error("Uso: cancelar")
            if not self._viaje_activo:
                return self.vista.mostrar_info("No hay un viaje activo.")
            return self._cancelar_viaje()
        if self._viaje_activo and comando not in ("historia", "mapa", "inv", "ayuda", "guardar", "puntajes"):
            self._cancelar_viaje()

        # ---------------------------------------------
        # MOVIMIENTO RÁPIDO
        # ---------------------------------------------

        if comando == "historia":
            return self._historia(argumentos)
        if comando == "mapa":
            return self._mapa(argumentos)
        if comando == "ir":
            return self._viaje(argumentos)
        if comando in ("n", "s", "e", "o"):
            return self._accion_modelo(
                "mover",
                DIRECCIONES[comando],
            )

        # ---------------------------------------------
        # mover <dir>
        # ---------------------------------------------

        if comando == "mover":

            if not argumentos:
                return self.vista.mostrar_error(
                    "Uso: mover <n|s|e|o>"
                )

            direccion = self._direccion(argumentos[0])

            if direccion is None:
                return self.vista.mostrar_error(
                    "Dirección inválida."
                )

            return self._accion_modelo(
                "mover",
                direccion,
            )

        # ---------------------------------------------
        # abrir <dir>
        # ---------------------------------------------

        if comando == "abrir":

            if not argumentos:
                return self.vista.mostrar_error(
                    "Uso: abrir <n|s|e|o>"
                )

            direccion = self._direccion(argumentos[0])

            if direccion is None:
                return self.vista.mostrar_error(
                    "Dirección inválida."
                )

            return self._accion_modelo(
                "abrir",
                direccion,
            )

        # ---------------------------------------------
        # esperar
        # ---------------------------------------------

        if comando == "esperar":
            return self._accion_modelo(
                "esperar"
            )

        # ---------------------------------------------
        # atacar
        # ---------------------------------------------

        if comando == "atacar":

            enemigo = None

            if argumentos:
                enemigo = argumentos[0]

            else:
                # Si hay exactamente un enemigo,
                # podemos seleccionarlo automáticamente.

                estado = self.modelo.estado_vista()

                vivos = estado.enemigos

                if len(vivos) == 1:
                    enemigo = vivos[0].instancia

                elif len(vivos) == 0:
                    return self.vista.mostrar_error(
                        "No hay enemigos en esta sala."
                    )

                else:
                    return self.vista.mostrar_error(
                        "Hay varios enemigos. Usa: atacar <id>"
                    )

            return self._accion_modelo(
                "atacar",
                enemigo,
            )

        # ---------------------------------------------
        # INVENTARIO
        # ---------------------------------------------

        if comando == "inv":
            return self._comando_inventario(argumentos)

        if comando == "seleccionar":
            if argumentos and self.modelo.inventario_seleccionar(argumentos[0]):
                return
            return self.vista.mostrar_error("No tienes ese objeto en el inventario.")

        if comando == "sig":
            return self._mover_cursor("siguiente")

        if comando == "ant":
            return self._mover_cursor("anterior")

        # ---------------------------------------------
        # OBJETOS
        # ---------------------------------------------

        if comando in ("recoger", "usar", "equipar", "soltar"):

            objeto = argumentos[0] if argumentos else None

            # usar/equipar/soltar pueden utilizar el cursor actual
            if objeto is None and comando != "recoger":
                objeto = self._id_cursor_actual()

            if objeto is None:
                return self.vista.mostrar_error(
                    f"Debes indicar un objeto para '{comando}'."
                )

            return self._accion_modelo(
                comando,
                objeto,
            )

        # ---------------------------------------------
        # RETROCESO
        # ---------------------------------------------

        if comando == "retroceso":
            return self._accion_modelo(
                "retroceso"
            )

        # ---------------------------------------------
        # GUARDAR
        # ---------------------------------------------

        if comando == "guardar":

            ruta = (
                argumentos[0]
                if argumentos
                else RUTA_GUARDADO_PREDETERMINADA
            )

            return self._guardar(ruta)

        # ---------------------------------------------
        # CARGAR
        # ---------------------------------------------

        if comando == "cargar":

            ruta = (
                argumentos[0]
                if argumentos
                else RUTA_GUARDADO_PREDETERMINADA
            )

            return self._cargar(ruta)

        # ---------------------------------------------
        # PUNTAJES
        # ---------------------------------------------

        if comando == "puntajes":

            if self.tabla_puntajes is None:
                return self.vista.mostrar_error(
                    "La tabla de puntajes no está configurada."
                )

            registros = self.tabla_puntajes.ranking()

            self.vista.mostrar_puntajes(registros)

            return

        # ---------------------------------------------
        # REPLAY
        # ---------------------------------------------

        if comando == "replay":
            return self._replay(argumentos)

        # ---------------------------------------------
        # AYUDA
        # ---------------------------------------------

        if comando == "ayuda":
            self.vista.mostrar_ayuda()
            return

        # ---------------------------------------------
        # SALIR
        # ---------------------------------------------

        if comando == "salir":
            self.ejecutando = False
            if callable(getattr(type(self.vista), "marcar_volver_menu", None)):
                self.vista.marcar_volver_menu()
            return

        self.vista.mostrar_error(
            f"Comando desconocido: {comando}"
        )

    # ---------------------------------------------------------
    # EJECUTAR ACCIÓN DEL MODELO
    # ---------------------------------------------------------

    def _mostrar_informe(self, titulo, texto):
        if callable(getattr(type(self.vista), "mostrar_informe", None)):
            return self.vista.mostrar_informe(titulo, texto)
        return self.vista.mostrar_info(texto)

    def _historia(self, argumentos):
        if len(argumentos) != 1:
            return self.vista.mostrar_error("Uso: historia <t> o historia #<acción>.")
        historia = getattr(self.modelo, "linea_tiempo", None)
        if historia is None:
            return self.vista.mostrar_error("El motor todavía no entrega cambios históricos.")
        try:
            texto = resumir(consultar(historia, argumentos[0]))
        except ErrorHistoria as error:
            return self.vista.mostrar_error(str(error))
        return self._mostrar_informe("Historia", texto)

    def _mapa(self, argumentos):
        if argumentos:
            return self.vista.mostrar_error("Uso: mapa")
        mapa = getattr(self.modelo, "mapa_conocido", None)
        if not callable(mapa):
            return self.vista.mostrar_error("El mapa conocido todavía no está disponible.")
        return self._mostrar_informe("Mapa conocido", "\n".join(lineas_mapa(mapa())) or "El mapa está vacío.")

    def _viaje(self, argumentos):
        if len(argumentos) != 2 or argumentos[0].lower() != "a":
            return self.vista.mostrar_error("Uso: ir a <sala>")
        try:
            destino = int(argumentos[1])
            if destino < 0:
                raise ValueError()
        except ValueError:
            return self.vista.mostrar_error("El destino debe ser un identificador de sala válido.")
        self._cancelar_viaje(mostrar=False)
        self.control_viaje = self._obtener_control_viaje()
        if self.control_viaje is not None:
            try:
                self.control_viaje.iniciar(self.modelo.estado_vista().sala_id, destino)
            except ValueError as error:
                return self.vista.mostrar_error(str(error))
            if self.control_viaje.estado != "listo":
                return self._mostrar_fin_viaje()
            if not self._registrar_orden_viaje(destino):
                self.control_viaje.cancelar()
                return
            self._viaje_activo = True
            self._paso_rechazado = None
            return self.vista.mostrar_info(f"Viaje a sala {destino} iniciado. Puedes cancelar entre pasos.")
        viajar = getattr(self.modelo, "viajar_hasta", None)
        if not callable(viajar):
            return self.vista.mostrar_error("El viaje automático todavía no está disponible.")
        if not self._registrar_orden_viaje(destino):
            return

        def mover(direccion):
            return self.ejecutando and self._accion_modelo("mover", direccion)

        return self.vista.mostrar_info(viajar(destino, mover))

    def _obtener_control_viaje(self):
        proveedor = (self._control_viaje_inyectado if self._control_viaje_inyectado is not None
                     else getattr(self.modelo, "control_viaje", None))
        return proveedor if isinstance(proveedor, ControlViaje) else None

    def _registrar_orden_viaje(self, destino):
        if not self.ejecutando or not self._grabacion_valida:
            return False
        try:
            self.bitacora_replay.registrar_comentario(f"ir a {destino}")
        except OSError as error:
            self._fallo_grabacion(error)
            return False
        return True

    def _cancelar_viaje(self, mostrar=True):
        activo = self._viaje_activo
        self._viaje_activo = False
        self._paso_rechazado = None
        if self.control_viaje is not None and (activo or self.control_viaje.pendiente is not None):
            self.control_viaje.cancelar()
        if activo and mostrar:
            self.vista.mostrar_info("Viaje detenido: cancelación.")

    def _mostrar_fin_viaje(self):
        self._viaje_activo = False
        etiquetas = (("llegada", "destino alcanzado"), ("dano", "daño recibido"),
                     ("enemigos", "enemigos al entrar"), ("fin_partida", "fin de partida"),
                     ("sin_ruta", "sin ruta conocida"), ("destino_no_explorado", "destino no explorado"),
                     ("origen_no_explorado", "origen no explorado"), ("cancelacion", "cancelación"))
        motivos = [next((texto for clave, texto in etiquetas if clave == causa), causa)
                   for causa in self.control_viaje.causas]
        return self.vista.mostrar_info("Viaje detenido: " + "; ".join(motivos) + ".")

    def _avanzar_viaje(self):
        if not self._viaje_activo:
            return
        if not self.ejecutando or not self._grabacion_valida or getattr(self.modelo, "terminado", False):
            return self._cancelar_viaje(mostrar=False)
        try:
            if self.control_viaje is not self._obtener_control_viaje():
                raise ValueError("El proveedor de viaje cambió; inicia otro viaje.")
            if self.modelo.estado_vista().sala_id != self.control_viaje.posicion:
                raise ValueError("La posición cambió fuera del viaje; inicia otro viaje.")
            paso = self.control_viaje.proponer()
            if paso is None:
                return self._mostrar_fin_viaje()
            identidad = (paso.origen, paso.ruta.siguiente, paso.ruta.direccion)
            if identidad == self._paso_rechazado:
                raise ValueError("El movimiento fue rechazado y la ruta conocida no cambió.")
            if not self._viaje_activo or self.control_viaje.pendiente is not paso:
                return self._cancelar_viaje(mostrar=False)
            self._accion_modelo("mover", paso.ruta.direccion, desde_viaje=True)
            if not self._viaje_activo:
                return
            resultado = self.ultimo_resultado_accion
            hechos = getattr(resultado, "hechos_paso", None)
            if not isinstance(hechos, ResultadoPaso):
                raise ValueError("El motor todavía no entrega los hechos del movimiento para continuar el viaje.")
            if hechos.aceptado != resultado.ok or hechos.posicion != self.modelo.estado_vista().sala_id:
                raise ValueError("Los hechos del movimiento no coinciden con el resultado del motor.")
            self.control_viaje.registrar_resultado(paso.numero, hechos)
            self._paso_rechazado = identidad if not resultado.ok else None
            if self.control_viaje.estado == "detenido":
                return self._mostrar_fin_viaje()
        except Exception:
            self._cancelar_viaje(mostrar=False)
            raise

    def _accion_modelo(self, accion, argumento=None, *, desde_viaje=False):
        if not desde_viaje:
            self._cancelar_viaje()
        self.ultimo_resultado_accion = None
        if (callable(getattr(type(self.vista), "ejecutar_tarea", None))
                and getattr(self.vista, "root", None) is not None):
            resultado = self.vista.ejecutar_tarea(self.modelo.ejecutar, accion, argumento)
        else:
            resultado = self.modelo.ejecutar(accion, argumento)

        self.ultimo_resultado_accion = resultado
        if not resultado.ok:

            mensaje = (
                resultado.mensaje
                or "La acción no pudo realizarse."
            )

            self.vista.mostrar_error(mensaje)

            self.notificar(
                f"Acción rechazada: {mensaje}"
            )

            # IMPORTANTE:
            # acciones rechazadas NO se guardan en replay.
            return False

        # Solo registramos acciones aceptadas.
        if callable(getattr(type(self.vista), "preparar_animacion", None)):
            if accion == "usar":
                self.vista.preparar_animacion(accion, argumento)
            else:
                self.vista.preparar_animacion(accion)
        if (getattr(resultado, "trampas_activadas", None)
                and callable(getattr(type(self.vista), "preparar_trampas", None))):
            self.vista.preparar_trampas(resultado.trampas_activadas)
        if self._grabacion_valida:
            try:
                self.bitacora_replay.registrar_accion(accion, argumento)
            except OSError as error:
                self._fallo_grabacion(error)

        if resultado.mensaje:
            self.notificar(resultado.mensaje)
        elif not self._modelo_notifica:
            if argumento is None:
                self.notificar(
                    f"Acción: {accion}"
                )
            else:
                self.notificar(
                    f"Acción: {accion} {argumento}"
                )

        return True

    # ---------------------------------------------------------
    # INVENTARIO
    # ---------------------------------------------------------

    def _comando_inventario(self, argumentos):

        if not hasattr(self.modelo, "inventario_vista"):
            return self.vista.mostrar_error(
                "Inventario todavía no integrado por Persona C."
            )

        # inv
        if not argumentos:

            items = self.modelo.inventario_vista()

            cursor = self._id_cursor_actual()

            self.vista.mostrar_inventario(
                items,
                cursor=cursor,
            )

            return

        # inv orden peso
        # inv orden valor desc
        # inv orden nombre

        if argumentos[0].lower() != "orden":
            return self.vista.mostrar_error(
                "Uso: inv orden peso|valor|nombre [desc]"
            )

        if len(argumentos) < 2:
            return self.vista.mostrar_error(
                "Debes indicar peso, valor o nombre."
            )

        criterio = argumentos[1].lower()

        if criterio not in ("peso", "valor", "nombre"):
            return self.vista.mostrar_error(
                "Orden inválido. Usa peso, valor o nombre."
            )

        descendente = (
            len(argumentos) >= 3
            and argumentos[2].lower() == "desc"
        )

        items = self.modelo.inventario_vista(
            criterio,
            descendente,
        )

        self.vista.mostrar_inventario(
            items,
            orden=criterio,
            cursor=self._id_cursor_actual(),
        )

    def _mover_cursor(self, movimiento):

        if not hasattr(self.modelo, "inventario_cursor"):
            return self.vista.mostrar_error(
                "Inventario todavía no integrado por Persona C."
            )

        item = self.modelo.inventario_cursor(
            movimiento
        )

        self.vista.mostrar_item(item)

    def _id_cursor_actual(self):

        if not hasattr(self.modelo, "inventario_cursor"):
            return None

        try:
            item = self.modelo.inventario_cursor(
                "actual"
            )
        except Exception:
            return None

        if item is None:
            return None

        return item.instancia

    # ---------------------------------------------------------
    # REPLAY
    # ---------------------------------------------------------

    def _replay(self, argumentos):

        if self.lanzador_replay is None:
            return self.vista.mostrar_error(
                "El replay no está disponible en esta sesión."
            )

        if argumentos:
            ruta = argumentos[0]

        else:
            # Sin argumento: abrir directamente la grabacion de esta sesion.
            ruta = str(self.bitacora_replay.ruta)

        if not self._grabacion_valida and os.path.abspath(ruta) == os.path.abspath(self.bitacora_replay.ruta):
            return self.vista.mostrar_error("La grabacion actual esta incompleta y no se puede reproducir.")
        if not os.path.exists(ruta):
            return self.vista.mostrar_error(
                f"No existe el archivo de replay: {ruta}"
            )

        try:
            if callable(getattr(type(self.vista), "ejecutar_tarea", None)):
                salida = self.vista.ejecutar_tarea(self.lanzador_replay, ruta)
            else:
                salida = self.lanzador_replay(ruta)

        except (OSError, CalledProcessError) as error:
            return self.vista.mostrar_error(
                f"No se pudo abrir el replay: {error}"
            )

        self.notificar(f"Replay abierto: {ruta}")
        if isinstance(salida, str):
            self._mostrar_informe("Replay", salida)
        else:
            self.vista.mostrar_info(f"Replay abierto: {ruta}")

    # ---------------------------------------------------------
    # GUARDADO
    # ---------------------------------------------------------

    def _guardar(self, ruta):

        if not hasattr(self.modelo, "exportar_estado"):
            return self.vista.mostrar_error(
                "El modelo todavía no implementa exportar_estado()."
            )

        try:
            estado = self.modelo.exportar_estado()
            if self.partida_p2 and estado.historia is None:
                return self.vista.mostrar_error("No se puede guardar Parte II sin la historia del motor.")

            guardar_estado(
                estado,
                ruta,
            )

            self.notificar(
                f"Partida guardada en {ruta}"
            )

            self.vista.mostrar_info(
                f"Partida guardada: {ruta}"
            )

        except Exception as error:

            self.vista.mostrar_error(
                f"No se pudo guardar: {error}"
            )

    def _fallo_grabacion(self, error):
        self._cancelar_viaje(mostrar=False)
        self._grabacion_valida = False
        self.ejecutando = False
        texto = (f"La accion se realizo, pero no pudo grabarse: {error}. "
                 "La sesion se detiene para evitar un replay divergente. La bitacora esta incompleta.")
        self.notificar(texto)
        if callable(getattr(type(self.vista), "mostrar_error_replay", None)):
            self.vista.mostrar_error_replay(texto)
        else:
            self.vista.mostrar_error(texto)

    # ---------------------------------------------------------
    # CARGA
    # ---------------------------------------------------------

    def _cargar(self, ruta):
        self._cancelar_viaje(mostrar=False)
        if not hasattr(self.modelo, "restaurar_estado"):
            return self.vista.mostrar_error(
                "El modelo todavía no implementa restaurar_estado()."
            )

        try:
            estado = (cargar_estado_partida if self.partida_p2 else cargar_estado)(ruta)
            if self.partida_p2 and getattr(self.modelo, "linea_tiempo", None) is None:
                return self.vista.mostrar_error("El motor todavía no admite restaurar la historia.")

            self.modelo.restaurar_estado(
                estado
            )
            if callable(getattr(type(self.vista), "preparar_animacion", None)):
                self.vista.preparar_animacion("cargar")
            if self._grabacion_valida:
                try:
                    self.bitacora_replay.registrar_carga(estado)
                except OSError as error:
                    self._fallo_grabacion(error)
                    return
            self._puntaje_registrado = False

            self.notificar(
                f"Partida cargada desde {ruta}"
            )

            self.vista.mostrar_info(
                f"Partida cargada: {ruta}"
            )

        except Exception as error:

            self.vista.mostrar_error(
                f"No se pudo cargar: {error}"
            )

    # ---------------------------------------------------------
    # UTILIDAD
    # ---------------------------------------------------------

    def _direccion(self, texto):
        return DIRECCIONES.get(texto.lower())
