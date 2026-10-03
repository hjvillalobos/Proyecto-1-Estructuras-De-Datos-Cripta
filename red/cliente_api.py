import math
import time
import uuid
from threading import RLock
from urllib.parse import quote

from red.errores import DatosInvalidos, ErrorRed, PresupuestoAgotado
from red.validacion import entero, identificador, lote


CLIENTE_ID = str(uuid.uuid4())


class ClienteApi:
    def __init__(self, base_url=None, transporte=None, esperar=time.sleep,
                 timeout=10, max_reintentos=3):
        if transporte is None:
            import requests
            transporte = requests.Session()
        self.transporte = transporte
        self.base_url = (base_url or
                         "https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/v1").rstrip("/")
        self.cliente_id = CLIENTE_ID
        self.esperar = esperar
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("El timeout debe ser positivo y finito.")
        self.timeout = timeout
        self.max_reintentos = entero(max_reintentos)
        self.solicitudes_realizadas = 0
        self.presupuesto_solicitudes = None
        self._candado = RLock()

    def configurar_presupuesto(self, limite):
        with self._candado:
            self.presupuesto_solicitudes = entero(limite)
            if self.solicitudes_realizadas > limite:
                raise PresupuestoAgotado(
                    f"El inicio ya usó {self.solicitudes_realizadas} solicitudes; "
                    f"la cripta declara un presupuesto de {limite}."
                )

    def _comprobar_presupuesto(self):
        if (self.presupuesto_solicitudes is not None
                and self.solicitudes_realizadas >= self.presupuesto_solicitudes):
            raise PresupuestoAgotado(
                f"Presupuesto agotado: {self.solicitudes_realizadas}/"
                f"{self.presupuesto_solicitudes} solicitudes."
            )

    def _hacer_peticion_get(self, endpoint, parametros=None):
        import requests
        with self._candado:
            for intento in range(self.max_reintentos + 1):
                self._comprobar_presupuesto()
                self.solicitudes_realizadas += 1
                respuesta = None
                try:
                    respuesta = self.transporte.get(
                        self.base_url + endpoint, params=parametros,
                        headers={"X-Cripta-Client-Id": self.cliente_id},
                        timeout=self.timeout, allow_redirects=False
                    )
                    estado = respuesta.status_code
                    try:
                        datos = respuesta.json()
                    except ValueError as error:
                        raise ErrorRed(f"GET {endpoint}: HTTP {estado}, JSON inválido.") from error
                except requests.RequestException as error:
                    raise ErrorRed(f"GET {endpoint}: fallo de conexión o timeout: {error}") from error
                finally:
                    if respuesta is not None:
                        respuesta.close()
                if not isinstance(datos, dict):
                    raise DatosInvalidos(f"GET {endpoint}: se esperaba un objeto JSON.")
                if estado == 200:
                    return datos
                if estado != 429:
                    raise ErrorRed(f"GET {endpoint}: HTTP {estado}: {datos.get('error', 'sin detalle')}")
                if intento == self.max_reintentos:
                    raise ErrorRed(f"GET {endpoint}: HTTP 429 después de {intento} reintentos.")
                espera = datos.get("reintentar_en")
                if type(espera) is not int or espera < 1:
                    raise DatosInvalidos(f"GET {endpoint}: reintentar_en debe indicar segundos positivos.")
                self._comprobar_presupuesto()
                self.esperar(espera)

    def listar_criptas(self):
        return self._hacer_peticion_get("/criptas")

    def obtener_datos_generales(self, cripta_id):
        ruta = f"/criptas/{quote(identificador(cripta_id), safe='')}"
        datos = self._hacer_peticion_get(ruta)
        if "presupuesto_solicitudes" not in datos:
            raise DatosInvalidos(f"GET {ruta}: falta presupuesto_solicitudes.")
        self.configurar_presupuesto(datos["presupuesto_solicitudes"])
        return datos

    def obtener_esqueleto(self, cripta_id, pagina=1):
        ruta = f"/criptas/{quote(identificador(cripta_id), safe='')}/salas"
        return self._hacer_peticion_get(ruta, {"pagina": entero(pagina, 1)})

    def obtener_contenido_salas(self, cripta_id, salas_ids):
        ids = lote(salas_ids, salas=True)
        ruta = f"/criptas/{quote(identificador(cripta_id), safe='')}/contenido"
        return self._hacer_peticion_get(ruta, {"salas": ",".join(map(str, ids))})

    def obtener_catalogo(self, ids):
        ids = lote(ids)
        return self._hacer_peticion_get("/catalogo", {"ids": ",".join(ids)})

    def obtener_version_cripta(self, cripta_id):
        ruta = f"/criptas/{quote(identificador(cripta_id), safe='')}/version"
        return self._hacer_peticion_get(ruta)

    def obtener_version_catalogo(self):
        return self._hacer_peticion_get("/catalogo/version")

    def cerrar(self):
        self.transporte.close()











