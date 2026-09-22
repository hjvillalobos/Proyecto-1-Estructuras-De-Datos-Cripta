import uuid
import requests
import time

class ClienteApi:

    def __init__(self):

        # Genera un ID unico
        self.cliente_id = str(uuid.uuid4())

        self.base_url = "https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/v1"

    def _hacer_peticion_get(self, endpoint: str) -> dict:

        url = f"{self.base_url}{endpoint}"
        headers = {"X-Cripta-Client-Id": self.cliente_id}

        print(f"\n[DEBUG] Intentando acceder a: {url}")
        print(f"[DEBUG] Encabezados que se van a enviar: {headers}")

        while True:

            respuesta = requests.get(url, headers=headers, timeout=5)

            if respuesta.status_code == 400:
                print(f"\n[DEBUG] URL que falló: {url}")
                print(f"[DEBUG] Respuesta del servidor: {respuesta.text}\n")

            if respuesta.status_code == 200:
                return respuesta.json()

            if respuesta.status_code == 429:
                datos_error = respuesta.json()
                espera_ms = datos_error.get("reintenta_en", 1000)
                time.sleep(espera_ms / 1000)
                continue # Vuelve al inicio del while

            # Muestra cualquier otro error
            respuesta.raise_for_status()


    def obtener_datos_generales(self,cripta_id: str) -> dict:
        ruta = f"/criptas/{cripta_id}"
        return self._hacer_peticion_get(ruta)

    def obtener_esqueleto(self, cripta_id: str, pagina: int = 1) -> dict:
        ruta = f"/criptas/{cripta_id}/salas?pagina={pagina}"
        return self._hacer_peticion_get(ruta)

    def obtener_contenido_salas(self, cripta_id: str, salas_ids: list[int]) -> dict:
        ruta = f"/criptas/{cripta_id}/contenido?salas={','.join(map(str, salas_ids))}"
        return self._hacer_peticion_get(ruta)

    def obtener_catalogo(self, ids: list[str]) -> dict:
        ruta = f"/catalogo?ids={','.join(ids)}"
        return self._hacer_peticion_get(ruta)











