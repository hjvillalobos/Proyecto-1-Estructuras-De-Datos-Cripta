# Contratos propuestos entre B y D

Diseño pendiente de implementación. Sin rutas nuevas del servicio ni cambios al contrato oficial.

## Adquisición

`ClienteApi.obtener_llaves(cripta_id)` consulta `GET /v1/criptas/{id}/llaves` mediante el transporte existente. Devuelve el objeto JSON con `llaves`, una lista de entradas `id`, `sala`, `enemigo` opcional. Mantiene UUID y presupuesto; reintentos y consultas de versión cuentan. La respuesta no lleva una versión inventada: el coordinador comprueba la versión de cripta.

`AlmacenLocal.leer_llaves(cripta_id, version)` devuelve el objeto persistido o `None` si falta. JSON ilegible produce `DatosInvalidos`. `guardar_llaves(cripta_id, version, respuesta)` conserva el mecanismo atómico y directorio de versión. `{"llaves": []}` es válido y distinto de ausencia.

`ClienteOffline.obtener_llaves(cripta_id)` conserva el método del cliente HTTP y obtiene la versión de sus metadatos seleccionados. La selección explícita debe ser coherente para generales, páginas y llaves. Adaptar la selección de versión del cliente offline sin romper sus llamadas existentes; no reutilizar silenciosamente `actual.json` cuando el usuario pidió una versión histórica. Datos faltantes producen `DatosNoDisponibles`; nunca HTTP.

## Preparación

`preparar_verificacion(cliente, almacen, cripta_id, version_cripta=None)` devuelve `DatosVerificacion` completo o lanza un error esperado del módulo `red.errores`. Reúne generales, páginas y llaves sin iniciar catálogo, descargar contenidos ni construir la vista. El coordinador convierte errores esperados a `ResultadoVerificacion(estado="no_completada")`. El análisis no recibe clientes ni almacenamiento.

## Análisis

`verificar_resolubilidad(datos)` recibe `DatosVerificacion` validado y devuelve `ResultadoVerificacion`, descrito en [data-model.md](../data-model.md). Es determinista para entradas equivalentes normalizadas. No hace red, no lee archivos ni modifica datos. Invariantes de entrada rotas producen `DatosInvalidos`, nunca un falso dictamen negativo.

Semántica positiva: llave de salida obtenida y entrada hacia sala de salida desde un origen alcanzado que requiere esa llave. La clave puede habilitar la entrada desde cualquier sala incorporada; no se prueba una trayectoria única.

## Consumidor D

| Estado | Inicio normal | Con `--forzar` | `--verificar` |
|---|---|---|---|
| resoluble | Puede continuar | Puede continuar | Mostrar resultado y terminar sin vista. |
| no_resoluble | Bloquear | Mostrar diagnóstico y permitir continuar | Mostrar diagnóstico y terminar sin vista. |
| no_completada | Bloquear | Bloquear | Mostrar causa y terminar sin vista. |

Mostrar siempre el alcance: «Verificación por alcanzabilidad acumulada; no garantiza una trayectoria única si hay salidas sin regreso». La redacción puede adaptarse conservando el significado. D no recalcula ni modifica el dictamen. Códigos de salida y presentación visual se coordinan con D sin cambiar estos comportamientos.

## Medición

B entrega `medir_resolubilidad(tamanos, repeticiones, semilla)` y medición de datos reales ya preparados. D conecta el subsistema `resolubilidad` a `bench.py` y al modo `--bench`. El registro incluye tamaño, versión cuando corresponda, estrategia, muestras, promedio, mínimo, máximo, desviación y conteos. La comparación valida primero los dictámenes y órdenes; un orden distinto entre estrategias es admisible si ambos son válidos y deterministas.

## Correcciones de revisión

- **Conformidad:** el profesor aceptó acumular llaves sin trayectoria única, según respuesta afirmativa comunicada por el usuario el 2026-11-02. C1 aprobado para ese alcance. La limitación continúa mostrándose para explicar el modelo.
- **Publicación:** el coordinador conserva las respuestas nuevas en memoria hasta validar conjunto y versión final. Solo entonces llama a las escrituras del almacén y actualiza `actual.json` al final. Una versión distinta, consulta fallida o presupuesto agotado antes de ese punto descarta el lote sin persistirlo. La siguiente ejecución debe conservar las copias previas o informar faltantes. La escritura atómica es por archivo, no por conjunto.
- **Diagnóstico:** D distingue `bloqueo_circular_autonomo`, `dependencia_circular_con_bloqueos_externos` y `ciclo_en_region_desconectada`. Mostrar integrantes, un ciclo concreto y alternativas bloqueadas por referencias al certificado global. No atribuir al testigo causa única ni confundir ciclo local con causa de desconexión. Todas las llaves inaccesibles conservan explicación, aun con bloqueos externos.
- **Mediciones:** incluir normalización, recorrido, diagnóstico y reporte en el total; comparar N, 2N, 4N con N=V+E+K+L e informar tamaño del reporte e IDs. Las razones temporales describen resultados, no prueban por sí mismas una cota asintótica.
