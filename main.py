import json
from red.cliente_api import ClienteApi

def probar_conexion_real():
    print("Iniciando prueba de conexión HTTP con la API de CRIPTA...")
    cliente = ClienteApi()
    cripta_id = "cripta-01"

    try:
        # 1. Probar datos generales
        print(f"\n--- Datos Generales de {cripta_id} ---")
        datos = cliente.obtener_datos_generales(cripta_id)
        print(json.dumps(datos, indent=2, ensure_ascii=False))

        # 2. Probar esqueleto (página 1)
        print(f"\n--- Esqueleto de {cripta_id} (Página 1) ---")
        esqueleto = cliente.obtener_esqueleto(cripta_id, pagina=1)
        print(json.dumps(esqueleto, indent=2, ensure_ascii=False))

        # 3. Probar contenido de salas
        print(f"\n--- Contenido de Salas 1 y 2 ---")
        contenido = cliente.obtener_contenido_salas(cripta_id, [1, 2])
        print(json.dumps(contenido, indent=2, ensure_ascii=False))

        # 4. Probar catálogo
        print(f"\n--- Catálogo de prueba ---")
        catalogo = cliente.obtener_catalogo(["ent_rata_gigante", "itm_daga_oxidada"])
        print(json.dumps(catalogo, indent=2, ensure_ascii=False))

        print("\n¡Todas las peticiones HTTP se ejecutaron con éxito!")

    except Exception as e:
        print(f"\nError de red o de servidor capturado: {e}")

if __name__ == "__main__":
    probar_conexion_real()