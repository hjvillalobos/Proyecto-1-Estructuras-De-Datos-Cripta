from red.cliente_api import ClienteApi
from red.catalogo import GestorCatalogo


class GestorPrecarga:
    def __init__(self, cliente_api: ClienteApi, gestor_catalogo: GestorCatalogo):
        self.cliente = cliente_api
        self.catalogo = gestor_catalogo

    def preparar_cripta(self, cripta_id: str) -> dict:
        print(f"Iniciando precarga para la cripta: {cripta_id}...")

        datos_generales = self.cliente.obtener_datos_generales(cripta_id)
        esqueleto = self.cliente.obtener_esqueleto(cripta_id, pagina=1)

        ids_salas = [sala["id"] for sala in esqueleto.get("salas", [])]
        contenido = self.cliente.obtener_contenido_salas(cripta_id, ids_salas)

        ids_catalogo_necesarios = set()
        for sala in contenido.get("contenido", []):
            for obj in sala.get("objetos", []):
                ids_catalogo_necesarios.add(obj)
            for enemigo in sala.get("enemigos", []):
                ids_catalogo_necesarios.add(enemigo["tipo"])
            for trampa in sala.get("trampas", []):
                ids_catalogo_necesarios.add(trampa["tipo"])

        print(f"Precargando {len(ids_catalogo_necesarios)} entidades únicas en caché...")
        self.catalogo.obtener_fichas(list(ids_catalogo_necesarios))

        print("Precarga completada. El juego puede iniciar.")

        return {
            "generales": datos_generales,
            "esqueleto": esqueleto,
            "contenido_inicial": contenido
        }