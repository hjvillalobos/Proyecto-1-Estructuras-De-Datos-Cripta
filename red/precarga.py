from copy import deepcopy
from dataclasses import dataclass
from threading import Thread

from modelo.tipos import Sala, FichaCatalogo
from red.errores import DatosInvalidos, VersionIncompatible
from red.validacion import entero, identificador, registros, texto, unicos


@dataclass
class SalaPreparada:
    sala: Sala
    contenido: dict
    fichas: list[FichaCatalogo]


@dataclass
class CriptaPreparada:
    generales: dict
    salas: list[Sala]
    inicial: SalaPreparada
    version_catalogo: str


class CargaPendiente:
    def __init__(self, ids):
        self.ids = ids
        self.resultado = []
        self.error = None
        self.hilo = None


class GestorPrecarga:
    def __init__(self, cliente_api, gestor_catalogo):
        self.cliente = cliente_api
        self.catalogo = gestor_catalogo
        self.almacen = gestor_catalogo.almacen
        self.generales = None
        self.salas = []
        self.contenidos = []
        self.pendiente = None
        self.red_compatible = True

    def _validar_generales(self, datos, cripta_id):
        if not isinstance(datos, dict) or datos.get("id") != cripta_id:
            raise DatosInvalidos(f"Datos generales inválidos para {cripta_id}.")
        identificador(datos.get("version"))
        identificador(datos.get("llave_salida"))
        for campo in ("salas_total", "paginas", "salas_por_pagina"):
            entero(datos.get(campo), 1)
        for campo in ("sala_inicial", "sala_salida"):
            entero(datos.get(campo), None)
        for campo in ("presupuesto_solicitudes", "inventario_max"):
            entero(datos.get(campo))
        if not isinstance(datos.get("jugador"), dict):
            raise DatosInvalidos("Faltan las estadísticas iniciales del jugador.")
        for campo in ("vida_max", "velocidad"):
            entero(datos["jugador"].get(campo), 1)
        for campo in ("ataque", "defensa"):
            entero(datos["jugador"].get(campo), None)

    def preparar_cripta(self, cripta_id, version_cripta=None, version_catalogo=None):
        if self.generales is not None:
            raise DatosInvalidos("Crea un GestorPrecarga nuevo para iniciar otra partida.")
        identificador(cripta_id)
        guardados = self.almacen.leer_generales(cripta_id, version_cripta)
        self.red_compatible = True
        if guardados is not None:
            self._validar_generales(guardados, cripta_id)
            self.cliente.configurar_presupuesto(guardados["presupuesto_solicitudes"])
            if version_cripta is not None:
                datos = guardados
                self.red_compatible = None
            else:
                actual = self.cliente.obtener_version_cripta(cripta_id)
                if actual.get("id") != cripta_id:
                    raise DatosInvalidos("La versión recibida pertenece a otra cripta.")
                identificador(actual.get("version"))
                if actual["version"] == guardados["version"]:
                    datos = guardados
                else:
                    datos = self.cliente.obtener_datos_generales(cripta_id)
        else:
            datos = self.cliente.obtener_datos_generales(cripta_id)
        self._validar_generales(datos, cripta_id)
        if version_cripta is not None and datos["version"] != version_cripta:
            raise VersionIncompatible(f"No está disponible la cripta {cripta_id}, versión {version_cripta}.")
        self.cliente.configurar_presupuesto(datos["presupuesto_solicitudes"])
        if guardados is None or version_cripta is None:
            self.almacen.guardar_generales(datos)
        self.generales = datos
        self.catalogo.iniciar(version_catalogo)
        for pagina in range(1, datos["paginas"] + 1):
            respuesta = self.almacen.leer_pagina(cripta_id, datos["version"], pagina)
            if respuesta is None:
                self._comprobar_version_red()
                respuesta = self.cliente.obtener_esqueleto(cripta_id, pagina)
            if (not isinstance(respuesta, dict) or respuesta.get("pagina") != pagina
                    or respuesta.get("total_paginas") != datos["paginas"]
                    or not isinstance(respuesta.get("salas"), list)
                    or len(respuesta["salas"]) > 50):
                raise DatosInvalidos(f"Página de esqueleto inválida: {pagina}.")
            for sala in respuesta["salas"]:
                if not isinstance(sala, dict):
                    raise DatosInvalidos("Sala inválida en el esqueleto.")
                entero(sala.get("id"), None)
                texto(sala.get("nombre"))
                salidas = sala.get("salidas", {})
                if not isinstance(salidas, dict):
                    raise DatosInvalidos("Las salidas deben ser un objeto JSON.")
                if any(existente.id == sala["id"] for existente in self.salas):
                    raise DatosInvalidos(f"Sala duplicada: {sala['id']}.")
                for direccion, salida in salidas.items():
                    if direccion not in ("N", "S", "E", "O") or not isinstance(salida, dict):
                        raise DatosInvalidos("Salida inválida en el esqueleto.")
                    entero(salida.get("sala"), None)
                self.salas.append(Sala(sala["id"], sala["nombre"], deepcopy(salidas)))
            self.almacen.guardar_pagina(cripta_id, datos["version"], respuesta)
        if len(self.salas) != datos["salas_total"]:
            raise DatosInvalidos("La cantidad de salas no coincide con los datos generales.")
        for sala in self.salas:
            for salida in sala.salidas.values():
                self._sala(salida["sala"])
        self._sala(datos["sala_inicial"])
        self._sala(datos["sala_salida"])
        self._incorporar(self._descargar(self._candidatas(datos["sala_inicial"])))
        inicial = self.preparar_entrada(datos["sala_inicial"], [])
        return CriptaPreparada(deepcopy(datos), deepcopy(self.salas), inicial, self.catalogo.version)

    def _sala(self, sala_id):
        for sala in self.salas:
            if sala.id == sala_id:
                return sala
        raise DatosInvalidos(f"La sala {sala_id} no pertenece al esqueleto.")

    def _comprobar_version_red(self):
        if self.red_compatible is None:
            actual = self.cliente.obtener_version_cripta(self.generales["id"])
            self.red_compatible = (actual.get("id") == self.generales["id"]
                                   and actual.get("version") == self.generales["version"])
        if not self.red_compatible:
            raise VersionIncompatible("Faltan datos locales de la versión solicitada.")

    def _contenido(self, sala_id):
        return next((dato for dato in self.contenidos if dato["sala"] == sala_id), None)

    def _ids_contenido(self, contenido):
        if not isinstance(contenido, dict):
            raise DatosInvalidos("Contenido de sala inválido.")
        entero(contenido.get("sala"), None)
        ids = []
        for campo in ("objetos", "enemigos", "trampas"):
            valores = contenido.get(campo, [])
            if not isinstance(valores, list):
                raise DatosInvalidos(f"La sala tiene un campo {campo} inválido.")
            for valor in valores:
                if campo == "objetos":
                    ids.append(identificador(valor))
                else:
                    if not isinstance(valor, dict):
                        raise DatosInvalidos(f"Instancia inválida en {campo}.")
                    identificador(valor.get("instancia"))
                    ids.append(identificador(valor.get("tipo")))
        return ids

    def _descargar(self, ids):
        resultado = []
        faltantes = []
        for sala in ids:
            dato = self.almacen.leer_contenido(self.generales["id"], self.generales["version"], sala)
            if dato is None:
                faltantes.append(sala)
            else:
                registros({"contenido": [dato]}, "contenido", "sala", [sala])
                self._ids_contenido(dato)
                resultado.append(dato)
        for inicio in range(0, len(faltantes), 10):
            lote = faltantes[inicio:inicio + 10]
            self._comprobar_version_red()
            respuesta = self.cliente.obtener_contenido_salas(self.generales["id"], lote)
            nuevos = registros(respuesta, "contenido", "sala", lote)
            for dato in nuevos:
                self._ids_contenido(dato)
            for dato in nuevos:
                self.almacen.guardar_contenido(self.generales["id"], self.generales["version"], dato)
            resultado.extend(nuevos)
        resultado = [next(dato for dato in resultado if dato["sala"] == sala) for sala in ids]
        ids_catalogo = []
        for dato in resultado:
            ids_catalogo.extend(self._ids_contenido(dato))
        self.catalogo.precargar(ids_catalogo)
        return resultado

    def _incorporar(self, datos):
        for dato in datos:
            if self._contenido(dato["sala"]) is None:
                self.contenidos.append(dato)

    def _candidatas(self, sala_id):
        self._sala(sala_id)
        cola = [sala_id]
        visitadas = [sala_id]
        candidatas = []
        posicion = 0
        while posicion < len(cola) and len(candidatas) < 10:
            actual = cola[posicion]
            posicion += 1
            if self._contenido(actual) is None:
                candidatas.append(actual)
            sala = self._sala(actual)
            for direccion in ("N", "S", "E", "O"):
                salida = sala.salidas.get(direccion)
                if salida is not None and salida["sala"] not in visitadas:
                    visitadas.append(salida["sala"])
                    cola.append(salida["sala"])
        return candidatas

    def _trabajar(self, pendiente):
        try:
            pendiente.resultado = self._descargar(pendiente.ids)
        except Exception as error:
            pendiente.error = error

    def incorporar_pendientes(self, esperar=False):
        if self.pendiente is None:
            return
        pendiente = self.pendiente
        if not esperar and pendiente.hilo.is_alive():
            return
        pendiente.hilo.join()
        self.pendiente = None
        if pendiente.error is not None:
            raise pendiente.error
        self._incorporar(pendiente.resultado)

    def anticipar(self, sala_id):
        self.incorporar_pendientes()
        if self.pendiente is not None:
            return False
        ids = self._candidatas(sala_id)
        if not ids:
            return False
        limite = self.cliente.presupuesto_solicitudes
        if limite is not None and self.cliente.solicitudes_realizadas >= limite:
            return False
        self.pendiente = CargaPendiente(ids)
        self.pendiente.hilo = Thread(target=self._trabajar, args=(self.pendiente,))
        self.pendiente.hilo.start()
        return True

    def cargar_contenido(self, ids):
        ids = unicos(ids)
        for sala in ids:
            self._sala(sala)
        if all(self._contenido(sala) is not None for sala in ids):
            return [deepcopy(self._contenido(sala)) for sala in ids]
        self.incorporar_pendientes(esperar=True)
        faltantes = [sala for sala in ids if self._contenido(sala) is None]
        if faltantes:
            self._incorporar(self._descargar(faltantes))
        return [deepcopy(self._contenido(sala)) for sala in ids]

    def preparar_entrada(self, sala_id, ids_en_uso):
        contenido = self.cargar_contenido([sala_id])[0]
        referencias = list(ids_en_uso) + self._ids_contenido(contenido)
        fichas = self.catalogo.fijar_referencias(referencias)
        propias = [ficha for ficha in fichas if ficha.id in self._ids_contenido(contenido)]
        unicas = []
        for ficha in propias:
            if not any(actual.id == ficha.id for actual in unicas):
                unicas.append(ficha)
        return SalaPreparada(deepcopy(self._sala(sala_id)), contenido, unicas)

    def cerrar(self):
        self.incorporar_pendientes(esperar=True)
