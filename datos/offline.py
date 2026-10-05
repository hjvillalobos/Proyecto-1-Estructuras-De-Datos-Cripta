from datos.almacen import AlmacenLocal
from red.errores import DatosNoDisponibles
from red.validacion import entero, identificador, lote


class ClienteOffline:
    def __init__(self, carpeta):
        self.almacen = AlmacenLocal(carpeta)
        self.solicitudes_realizadas = 0
        self.presupuesto_solicitudes = None

    def configurar_presupuesto(self, limite):
        self.presupuesto_solicitudes = entero(limite)

    def _exigir(self, datos, operacion):
        if datos is None:
            raise DatosNoDisponibles(f"Offline: faltan datos para {operacion}.")
        return datos

    def listar_criptas(self):
        return self._exigir(self.almacen.leer_lista(), "listar criptas")

    def obtener_datos_generales(self, cripta_id):
        identificador(cripta_id)
        datos = self._exigir(self.almacen.leer_generales(cripta_id), f"cripta {cripta_id}")
        self.configurar_presupuesto(datos["presupuesto_solicitudes"])
        return datos

    def obtener_version_cripta(self, cripta_id):
        datos = self.obtener_datos_generales(cripta_id)
        return {"id": cripta_id, "version": datos["version"]}

    def obtener_esqueleto(self, cripta_id, pagina=1):
        entero(pagina, 1)
        version = self.obtener_version_cripta(cripta_id)["version"]
        return self._exigir(self.almacen.leer_pagina(cripta_id, version, pagina),
                            f"página {pagina} de {cripta_id}")

    def obtener_contenido_salas(self, cripta_id, salas_ids):
        ids = lote(salas_ids, salas=True)
        version = self.obtener_version_cripta(cripta_id)["version"]
        return {"contenido": [
            self._exigir(self.almacen.leer_contenido(cripta_id, version, sala),
                         f"sala {sala} de {cripta_id}") for sala in ids
        ]}

    def obtener_version_catalogo(self):
        version = self._exigir(self.almacen.leer_version_catalogo(), "versión de catálogo")
        return {"version": version}

    def obtener_catalogo(self, ids):
        ids = lote(ids)
        version = self.obtener_version_catalogo()["version"]
        return {"entidades": [
            self._exigir(self.almacen.leer_ficha(version, clave), f"ficha {clave}")
            for clave in ids
        ]}

    def cerrar(self):
        pass
