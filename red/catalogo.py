
from modelo.tipos import FichaCatalogo
from red.cliente_api import ClienteApi

class GestorCatalogo:

    def __init__(self, cliente_api: ClienteApi, cache):
        self.cliente = cliente_api
        self.cache = cache  # Recibe la instancia de tu futura tabla hash

    def _procesar_json_a_ficha(self, datos_json: dict) -> FichaCatalogo:
        id_ficha = datos_json.pop("id")
        clase_ficha = datos_json.pop("clase")
        nombre_ficha = datos_json.pop("nombre")

        return FichaCatalogo(
            id=id_ficha,
            clase=clase_ficha,
            nombre=nombre_ficha,
            atributos=datos_json
        )

    def obtener_fichas(self, ids_solicitados: list[str]) -> list[FichaCatalogo]:

        fichas_resueltas = []
        ids_faltantes = []

        for id_item in ids_solicitados:
            ficha_en_cache = self.cache.buscar(id_item)
            if ficha_en_cache:
                fichas_resueltas.append(ficha_en_cache)
            else:
                if id_item not in ids_faltantes:
                    ids_faltantes.append(id_item)

        for i in range(0, len(ids_faltantes), 10):
            lote = ids_faltantes[i:i + 10]
            respuesta = self.cliente.obtener_catalogo(lote)

            for item_json in respuesta.get("entidades", []):
                nueva_ficha = self._procesar_json_a_ficha(item_json)
                fichas_resueltas.append(nueva_ficha)

                self.cache.insertar(nueva_ficha.id, nueva_ficha)

        return fichas_resueltas





