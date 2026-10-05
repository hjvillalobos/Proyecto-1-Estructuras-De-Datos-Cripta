
from copy import deepcopy
from threading import RLock

from datos.almacen import AlmacenLocal
from modelo.tipos import FichaCatalogo
from red.cache import CacheSinEspacioError
from red.errores import DatosInvalidos, VersionIncompatible
from red.validacion import identificador, registros, texto, unicos


class GestorCatalogo:
    def __init__(self, cliente_api, cache, almacen=None):
        self.cliente = cliente_api
        self.cache = cache
        self.almacen = almacen if almacen is not None else AlmacenLocal()
        self.version = None
        self.red_compatible = True
        self.aciertos = 0
        self.fallos = 0
        self.recuperaciones_disco = 0
        self._candado = RLock()

    def iniciar(self, version_esperada=None):
        with self._candado:
            if version_esperada is not None and self.almacen.tiene_version_catalogo(version_esperada):
                version = identificador(version_esperada)
                actual = None
            else:
                respuesta = self.cliente.obtener_version_catalogo()
                actual = identificador(respuesta.get("version"))
                version = actual if version_esperada is None else identificador(version_esperada)
            if self.version != version:
                self.cache.vaciar()
            self.version = version
            self.red_compatible = None if actual is None else version == actual
            if actual is not None:
                self.almacen.guardar_version_catalogo(actual)
            return version

    def _iniciar_si_falta(self):
        if self.version is None:
            self.iniciar()

    def _validar_ficha(self, datos, clave):
        if not isinstance(datos, dict) or datos.get("id") != clave:
            raise DatosInvalidos(f"Ficha inválida: {clave}.")
        identificador(datos.get("id"))
        texto(datos.get("clase"))
        texto(datos.get("nombre"))
        suelta = datos.get("suelta") or []
        if not isinstance(suelta, list):
            raise DatosInvalidos(f"La ficha {clave} tiene suelta inválido.")
        for dependencia in suelta:
            identificador(dependencia)
        return datos

    def _procesar_json_a_ficha(self, datos):
        self._validar_ficha(datos, datos.get("id"))
        atributos = deepcopy(datos)
        return FichaCatalogo(
            id=atributos.pop("id"),
            clase=atributos.pop("clase"),
            nombre=atributos.pop("nombre"),
            atributos=atributos
        )

    def precargar(self, ids_solicitados):
        with self._candado:
            self._iniciar_si_falta()
            pendientes = unicos(ids_solicitados)
            for clave in pendientes:
                identificador(clave)
            revisados = []
            while pendientes:
                lote = pendientes[:10]
                pendientes = pendientes[10:]
                datos_lote = []
                faltantes = []
                for clave in lote:
                    ficha = self.cache.consultar(clave)
                    if ficha is None:
                        datos = self.almacen.leer_ficha(self.version, clave)
                    else:
                        datos = {"id": ficha.id, "clase": ficha.clase,
                                 "nombre": ficha.nombre, **ficha.atributos}
                    if datos is None:
                        faltantes.append(clave)
                    else:
                        datos_lote.append(self._validar_ficha(datos, clave))
                if faltantes:
                    if self.red_compatible is None:
                        actual = self.cliente.obtener_version_catalogo()
                        self.red_compatible = identificador(actual.get("version")) == self.version
                    if not self.red_compatible:
                        raise VersionIncompatible(
                            f"Faltan fichas de catálogo {self.version} y el origen tiene otra versión."
                        )
                    respuesta = self.cliente.obtener_catalogo(faltantes)
                    nuevas = registros(respuesta, "entidades", "id", faltantes)
                    for datos in nuevas:
                        self._validar_ficha(datos, datos["id"])
                    for datos in nuevas:
                        self.almacen.guardar_ficha(self.version, datos)
                    datos_lote.extend(nuevas)
                for clave in lote:
                    datos = next(fila for fila in datos_lote if fila["id"] == clave)
                    revisados.append(clave)
                    for dependencia in datos.get("suelta") or []:
                        if dependencia not in revisados and dependencia not in pendientes and dependencia not in lote:
                            pendientes.append(dependencia)

    def _referencias_actuales(self):
        return [nodo.clave for nodo in self.cache.arreglo for _ in range(nodo.referencias)]

    def fijar_referencias(self, ids_en_uso):
        with self._candado:
            ids = list(ids_en_uso)
            claves = unicos(ids)
            if len(claves) > self.cache.capacidad:
                raise CacheSinEspacioError(
                    f"Se necesitan {len(claves)} fichas activas; la capacidad es {self.cache.capacidad}."
                )
            self.precargar(claves)
            pendientes = []
            for clave in claves:
                if not self.cache.contiene(clave):
                    datos = self.almacen.leer_ficha(self.version, clave)
                    pendientes.append(self._validar_ficha(datos, clave))
            self.cache.ajustar_referencias(ids)
            fichas = []
            for clave in claves:
                ficha = self.cache.buscar(clave)
                if ficha is None:
                    self.fallos += 1
                    datos = next(fila for fila in pendientes if fila["id"] == clave)
                    ficha = self._procesar_json_a_ficha(datos)
                    self.cache.insertar(clave, ficha)
                    self.cache.modificar_referencia(clave, ids.count(clave))
                    self.recuperaciones_disco += 1
                else:
                    self.aciertos += 1
                fichas.append(ficha)
            return [next(ficha for ficha in fichas if ficha.id == clave) for clave in ids]

    def retener(self, ids_solicitados):
        with self._candado:
            ids = list(ids_solicitados)
            actuales = self._referencias_actuales()
            return self.fijar_referencias(actuales + ids)[len(actuales):]

    def liberar(self, ids_solicitados):
        with self._candado:
            actuales = self._referencias_actuales()
            for clave in ids_solicitados:
                if clave not in actuales:
                    raise DatosInvalidos(f"La ficha {clave} no tiene una referencia que liberar.")
                actuales.remove(clave)
            self.cache.ajustar_referencias(actuales)

    def obtener_fichas(self, ids_solicitados):
        with self._candado:
            actuales = self._referencias_actuales()
            try:
                return self.retener(ids_solicitados)
            finally:
                self.cache.ajustar_referencias(actuales)

    def reporte(self):
        with self._candado:
            return {
                "solicitudes_realizadas": self.cliente.solicitudes_realizadas,
                "presupuesto_solicitudes": self.cliente.presupuesto_solicitudes,
                "aciertos_cache": self.aciertos,
                "fallos_cache": self.fallos,
                "recuperaciones_disco": self.recuperaciones_disco,
                "fichas_en_memoria": self.cache.tamaño_actual,
                "capacidad_cache": self.cache.capacidad,
                "version_catalogo": self.version
            }





