# red/catalogo.py

from modelo.tipos import FichaCatalogo
from red.cliente_api import ClienteApi


class GestorCatalogo:
    """
    Resuelve referencias de IDs crudos, consultando la caché o agrupando
    solicitudes HTTP en lotes de 10 para convertirlos en FichaCatalogo.
    """

    def __init__(self, cliente_api: ClienteApi, cache):
        self.cliente = cliente_api
        self.cache = cache  # Recibe la instancia de tu futura tabla hash

    def _procesar_json_a_ficha(self, datos_json: dict) -> FichaCatalogo:
        """Convierte un diccionario JSON crudo en el contrato FichaCatalogo."""
        id_ficha = datos_json.pop("id")
        clase_ficha = datos_json.pop("clase")
        nombre_ficha = datos_json.pop("nombre")

        # Todo lo que queda en el diccionario pasa a ser los atributos específicos
        return FichaCatalogo(
            id=id_ficha,
            clase=clase_ficha,
            nombre=nombre_ficha,
            atributos=datos_json
        )

    def obtener_fichas(self, ids_solicitados: list[str]) -> list[FichaCatalogo]:
        """
        Devuelve las fichas solicitadas resolviéndolas desde caché o red.
        Garantiza que no se pida dos veces un ID vigente.
        """
        fichas_resueltas = []
        ids_faltantes = []

        # 1. Filtrar usando la caché
        for id_item in ids_solicitados:
            # Asumimos que tu futura tabla hash tendrá un método buscar()
            ficha_en_cache = self.cache.buscar(id_item)
            if ficha_en_cache:
                fichas_resueltas.append(ficha_en_cache)
            else:
                if id_item not in ids_faltantes:  # Evitar duplicados en la misma petición
                    ids_faltantes.append(id_item)

        # 2. Pedir a la API los faltantes en lotes de máximo 10[cite: 1]
        for i in range(0, len(ids_faltantes), 10):
            lote = ids_faltantes[i:i + 10]
            respuesta = self.cliente.obtener_catalogo(lote)

            # 3. Instanciar objetos y guardarlos en caché
            for item_json in respuesta.get("entidades", []):
                nueva_ficha = self._procesar_json_a_ficha(item_json)
                fichas_resueltas.append(nueva_ficha)

                # Asumimos que tu futura tabla hash tendrá un método insertar()
                self.cache.insertar(nueva_ficha.id, nueva_ficha)

        return fichas_resueltas





