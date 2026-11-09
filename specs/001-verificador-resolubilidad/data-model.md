# Modelo de datos del verificador

Diseño propuesto, todavía sin implementación. El resultado usa alcanzabilidad acumulada, según AC-21.

## Registros de entrada

| Registro | Campos | Validación |
|---|---|---|
| DatosVerificacion | cripta_id, version, sala_inicial, sala_salida, llave_salida, salas, ubicaciones | Datos completos de una misma versión; IDs de inicio/salida existentes. |
| SalaVerificacion | id, salidas | ID entero, no booleano, único; direcciones válidas sin duplicación. |
| SalidaVerificacion | origen, direccion, destino, cerrada, llave | Destino existente; estado booleano normalizado; cerrada exige llave válida. Una salida abierta no exige poseer su llave declarada. |
| UbicacionLlave | id, sala, enemigo opcional | ID de texto válido, sala existente; enemigo ausente o nulo significa suelo. Repetir ID en otras ubicaciones es válido. |

Convertir las respuestas JSON en estos registros antes del análisis. `enemigo` identifica una instancia y no exige descargar contenidos para comprobar su posición: se confía en la sala inicial publicada por `/llaves`. IDs de llaves ausentes del listado pero requeridos por puertas o por la salida también forman parte del índice, con cero ubicaciones.

La normalización de campos opcionales sigue el contrato: `cerrada` omitida o nula equivale al estado abierto por defecto; no inventar llave para una puerta cerrada. Los valores originales se preservan para el diagnóstico cuando corresponda. Duplicados idénticos de ubicación pueden deduplicarse mediante ordenamiento propio por ID, sala y enemigo y comparación contigua.

## Estado interno

- Arreglo de salas ordenado por ID; cada posición es el índice interno.
- Arreglo de llaves únicas ordenado por ID, con listas de ubicaciones y puertas pendientes.
- Arreglos booleanos `alcanzada` y `obtenida`.
- Cola de índices de sala, con índice de lectura.
- Lista de IDs de llaves en el orden de su primera obtención.
- Evidencias: primera ubicación obtenible por llave y primera salida que incorpora cada sala.
- Grafo de condiciones con nodos sala, llave y paso por salida; listas de adyacencia y de adyacencia inversa. Aristas de condición hacia sus requisitos, conservando si son alternativas o requisitos conjuntos y la evidencia de la salida/ubicación.
- Diagnóstico: marcas de visita, pila propia, orden de finalización, índice de componente y predecesores para testigos. Sin recursión, tablas hash ni estructuras de bibliotecas.

Transiciones: sala no alcanzada → encolada → procesada; llave no obtenida → obtenida una vez; puerta pendiente → habilitada al obtener su llave. No se revierte ningún estado durante el análisis. La dirección de una salida no se invierte.

## Resultado

`ResultadoVerificacion` contiene:

- `estado`: `resoluble`, `no_resoluble` o `no_completada`.
- `cripta_id`, `version`: contexto; versión puede faltar si no se obtuvieron datos válidos.
- `modelo`: valor `alcanzabilidad_acumulada`.
- `limitacion`: no garantiza una trayectoria única en mapas sin regreso.
- `orden_llaves`: IDs sin repetición, en orden de obtención acumulativa.
- `llaves_inalcanzables`: registros con ID y ubicaciones conocidas; lista vacía de ubicaciones significa ausencia confirmada en listado válido.
- `frontera`: origen, dirección, destino y llave de cada puerta cerrada de origen alcanzado cuya llave no se obtuvo.
- `evidencia`: arreglo de condiciones con valor final, tipo sala/llave/paso y referencias a todos sus requisitos/alternativas. Los requisitos falsos justifican cada condición pendiente; condiciones base y ausencias se identifican expresamente. No duplicar subgrafos por llave.
- `ciclos`: integrantes, testigo concreto y referencias a evidencia; clasificación `bloqueo_circular_autonomo`, `dependencia_circular_con_bloqueos_externos` o `ciclo_en_region_desconectada`. Los bloqueos externos están explicados por el certificado global; no se afirma causa única.
- `causa`: explicación de condición de salida incumplida o error esperado de preparación; nunca traceback presentado como regla del juego.
- `metricas`: visitas, salidas examinadas, llaves obtenidas y pendientes activadas; registro de campos fijos, no índice hash.

Para `no_completada`, no publicar diagnósticos parciales como hechos concluyentes. Para `resoluble`, devolver orden y alcance; para `no_resoluble`, agregar frontera, inaccesibles y ciclos existentes. Los resultados se construyen con registros y listas, sin mutar entrada.

## Lote de adquisición

Lista privada de generales, páginas y llaves descargadas, con versión inicial y comprobación final. Transiciones: adquisición → validación completa → confirmación de versión → publicación de archivos → actualización de actual.json. Ante fallo previo a publicación, descartar lote sin tocar copias válidas. No añadir una promesa de transacción multiarquivo: una publicación interrumpida solo puede dejar archivos ya validados y de la misma versión, con faltantes detectables.
