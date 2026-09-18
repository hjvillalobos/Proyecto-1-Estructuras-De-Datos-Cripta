
class ClienteApi:

    # Cliente HTTP para interactuar con CRIPTA

    # Este es un MOCK temporal que simula respuestas JSON

    def __init__(self):

        # El enunciado pide crear este ID una sola vez por ejecucion

        # Se usa un URL falso para no gastar el presupuesto de solicitudes

        self.cliente_id = "ID-INICIO"

        self.base_url = "https://mock-cripta-api/v1"

    # Ahora voy a usar la base del enunciado


    def obtener_datos_generales(self,cripta_id: str) -> dict:

        # GET /criptas/cripta-01

        return {
            "id": "cripta-01",
            "version": "a3f91c",
            "salas_total": 20,
            "paginas": 1,
            "salas_por_pagina": 50,
            "sala_inicial": 1,
            "sala_salida": 19,
            "llave_salida": "itm_llave_negra",
            "presupuesto_solicitudes": 9,
            "inventario_max": 10,
            "jugador": {
                "vida_max": 30,
                "ataque": 6,
                "defensa": 2,
                "velocidad": 100
            }
        }


    def obtener_esqueleto(self, cripta_id: str, pagina: int = 1) -> dict:

        # GET /criptas/cripta-01/salas?pagina=1

        return {
            "pagina": 1,
            "total_paginas": 1,
            "salas": [
                {"id": 1, "nombre": "Entrada derruida",
                 "salidas": {"N": {"sala": 2}}},
                {"id": 2, "nombre": "Pasillo de las urnas",
                 "salidas": {
                     "S": {"sala": 1},
                     "N": {"sala": 3},
                     "E": {"sala": 7, "cerrada": True,
                           "llave": "itm_llave_bronce", "cierre_automatico": 500}
                 }
                 }
            ]
        }


    def obtener_contenido_salas(self, cripta_id: str, salas_ids: list[int]) -> dict:

        # GET /criptas/cripta-01/contenido?salas=1,2,3

        return {
            "contenido": [
                {"sala": 1, "enemigos": [],
                 "objetos": ["itm_antorcha"], "trampas": []},
                {"sala": 2,
                 "enemigos": [
                     {"instancia": "e-201", "tipo": "ent_rata_gigante", "vida": 12},
                     {"instancia": "e-202", "tipo": "ent_rata_gigante", "vida": 12}
                 ],
                 "objetos": ["itm_daga_oxidada"],
                 "trampas": [{"instancia": "t-17", "tipo": "trp_dardos"}]}
            ]
        }

    def obtener_catalogo(self, ids: list[str]) -> dict:

        # GET /catalogo?ids=ent_rata_gigante,itm_daga_oxidada,itm_antorcha,trp_dardos

        base_datos_catalogo = {
            "ent rata_gigante:": {"id": "ent_rata_gigante", "clase": "enemigo", "nombre": "Rata gigante",
                                  "vida_max": 12, "ataque": 5, "defensa": 1, "velocidad": 150,
                                  "comportamiento": "rastreador", "suelta": ["itm_pocion_menor"]},

            "itm_daga_oxidada:": {"id": "itm_daga_oxidada", "clase": "arma", "nombre": "Daga oxidada",
                                  "peso": 2, "valor": 15, "ataque_bonus": 3},

            "itm_antorcha:": {"id": "itm_antorcha", "clase": "antorcha", "nombre": "Antorcha",
                              "peso": 1, "valor": 5, "duracion": 2000},

            "trp_dardos:": {"id": "trp_dardos", "clase": "trampa", "nombre": "Dardos en la pared",
                            "daño": 4, "rearme": 300}
        }

        # Filtrar los elementos del catálogo según los IDs proporcionados
        entidades_filtradas = [base_datos_catalogo[id_item] for id_item in ids if id_item in base_datos_catalogo]
        return {"entidades" : entidades_filtradas}










