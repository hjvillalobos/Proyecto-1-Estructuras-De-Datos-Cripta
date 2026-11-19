# Manejo de errores — entrega integrada y antecedentes

> **Estado vigente de entrega:** las cuatro capacidades están integradas en `004-linea-tiempo`. Consultar [estado, trazabilidad y límites actuales](../../ESTADO_ENTREGA.md). Los balances y restricciones de autorización fechados anteriores son registros históricos, no bloqueos de la implementación actual. La revisión humana y los faltantes auténticos no se dan por resueltos mediante este aviso.


## Política vigente — 18 de noviembre de 2026

El motor valida las acciones ordinarias; el controlador presenta diagnósticos y el arranque distingue errores de datos, red, historia y archivos. Las secciones fechadas del 2 y 7 de noviembre, debajo, documentan cortes anteriores y no describen capacidades actualmente ausentes. [Decisión de excepciones y recuperación](../../DECISIONES.md), [CD-04](spec.md) y [plan](plan.md).

| Situación actual | Diagnóstico y recuperación | Implementación | Pruebas |
|---|---|---|---|
| Argumentos CLI incompatibles o K no positivo | Error de uso antes de abrir datos; no inicia una partida inválida. | `main.py` | `tests/test_modos_historia.py` |
| Acción inválida, inventario lleno, objetivo inexistente o falta de llave | Rechazo presentado al jugador; no consume tiempo ni se graba como acción aceptada. | `modelo/juego.py`, `controlador/controlador.py` | `tests/test_juego.py`, `tests/test_fallos_transaccionales.py` |
| HTTP fallido, timeout o JSON inválido | Error con operación/contexto; no se usa una respuesta parcial como válida. | `red/cliente_api.py`, `red/errores.py` | `tests/test_cliente_api.py` |
| HTTP 429 y presupuesto agotado | Espera/reintento acotado, contados en presupuesto; la espera real no mueve el reloj virtual. Si se agota, error explícito. | `red/cliente_api.py` | `tests/test_cliente_api.py` |
| Datos offline ausentes o versiones incompatibles | Diagnóstico de datos/versiones; no mezcla silenciosa ni HTTP en offline. | `datos/offline.py`, `red/catalogo.py`, `red/precarga.py` | `tests/test_precarga_offline.py`, `tests/test_catalogo.py` |
| Caché llena con fichas protegidas | Error de capacidad; no se desalojan fichas en uso ni se amplía el tope silenciosamente. | `red/cache.py`, `red/catalogo.py` | `tests/test_cache.py`, `tests/test_catalogo.py` |
| Verificación incompleta o cripta no resoluble | Reporte diferenciado; incompleta bloquea incluso con `--forzar`; negativa permite forzar explícitamente. | `red/verificacion.py`, `controlador/aplicacion.py` | `tests/test_verificacion_datos.py`, `tests/test_verificacion_entrega.py` |
| Historia inválida/futura o registros incoherentes | `ErrorHistoria` y subclases; consulta rechazada sin cambiar partida, rama ni log. | `modelo/errores_historia.py`, `controlador/controlador.py` | `tests/test_errores_historia.py`, `tests/test_controlador_ac_real.py` |
| Guardado inexistente, corrupto, truncado o incompatible | Excepción de archivo con causa; validar/preparar antes de adoptar la carga, conservando la partida ante rechazo comprobado. | `datos/guardado_binario.py`, `datos/historia_binaria.py`, `modelo/juego.py` | `tests/test_persistencia_historia.py`, `tests/test_integridad_operaciones.py` |
| Escritura o reemplazo fallidos; falla también la limpieza | Se conserva el error principal y destino anterior al reemplazo. La excepción conserva una nota del temporal que no pudo limpiarse. | `datos/almacen.py`, `datos/historia_binaria.py` | `tests/test_almacen_errores.py`, `tests/test_errores_historia.py` |
| Replay corrupto o de versiones incompatibles | Rechazo explícito; no se reproduce contra otra versión silenciosamente. | `datos/bitacora_replay.py`, `controlador/replay.py` | `tests/test_replay_grafico.py`, `tests/test_correcciones_enunciado.py` |
| Fallo de escritura de la bitácora de replay | Detener sesión e identificar grabación incompleta para evitar una reproducción divergente; distinguir inicio fallido de una acción o carga ya realizada. | `controlador/controlador.py` | `tests/test_replay_reinicio.py` |
| Puntajes con registros inválidos o fallo de escritura | Validar registros; comunicar el fallo y permitir cierre controlado. | `datos/puntajes.py`, `controlador/controlador.py` | `tests/test_fin_partida.py`, `tests/test_puntajes_apagado.py`, `tests/test_verificacion_entrega.py` |

La atomicidad se atribuye a las operaciones y casos verificados, no a cualquier excepción inesperada. En las fronteras de interfaz hay capturas para presentar errores; no demuestran rollback universal. La nota técnica de limpieza se conserva en el objeto excepción: mostrar solamente `str(error)` no garantiza visualizar esa nota. La sustitución atómica protege el destino hasta el reemplazo, pero no garantiza durabilidad absoluta ante cortes eléctricos ni éxito de limpieza cuando el sistema deniega acceso.

Validación vigente del cierre CD: suite integral de 905 pruebas/238.658 s, cero fallos/errores y cuatro omisiones opcionales. Incluye el diagnóstico preciso de CD-06 y el buffer compartido. Las pruebas nuevas de contenido inédito pasaron después en un conjunto de 17/14.170 s, sin omisiones. [Resultados y límites](../../ESTADO_ENTREGA.md). No se suman conjuntos ni se convierten pruebas funcionales en cifras de rendimiento.

## Antecedente — núcleo independiente, 2 de noviembre de 2026

Fecha: 2026-11-02. Requisitos: FR-005, FR-011, FR-012 y FR-020.

El núcleo señala fallos mediante excepciones con mensajes en español; no imprime, no abre ventanas y no registra acciones por sí mismo. El controlador las capturará al integrar los comandos. Por ahora se comprueba este contrato mediante pruebas independientes.

## Errores esperados

| Situación | Excepción pública | Qué se conserva | Evidencia |
|---|---|---|---|
| K inválido, tipo incorrecto, clave inválida o registro mal formado | EntradaHistoriaInvalida, derivada de ErrorHistoria y ValueError | La historia antes de la operación | tests/test_errores_historia.py y tests/test_linea_tiempo.py |
| Consulta futura, acción inexistente o recorte fuera de la rama | ReferenciaHistoricaInvalida, derivada de ErrorHistoria y ValueError | Reloj, acciones, rama y controles | test_referencia_invalida_se_distingue_de_entrada |
| Valor anterior distinto del registrado, tiempos o eventos incoherentes | CambioHistoriaIncoherente, derivada de ErrorHistoria y ValueError | Registrar/recortar valida antes de modificar la historia | test_cambio_incoherente_no_modifica_la_historia y pruebas de transacciones |
| Campo histórico ausente | KeyError | No se crea ni sustituye el campo; no se confunde con None | test_claves_invalidas_y_campo_ausente_son_distintos |
| Entrada no binaria o ruta inválida | ErrorGuardado | Historia y archivo de destino | test_tipos_no_binarios_y_rutas_invalidas |
| Archivo inexistente, acceso denegado o escritura/reemplazo fallidos | ErrorGuardado con causa original | El destino anterior hasta reemplazo exitoso | Pruebas de archivo, permisos y reemplazo |
| CRPT pasado al lector CRLH o versión de fragmento no soportada | FormatoIncompatible, derivada de ErrorGuardado | Archivo original; no se interpreta ni convierte silenciosamente | test_p1_y_version_futura_rechazados_explicita |
| Longitud/CRC/etiqueta/UTF-8 inválidos, contenido incoherente o truncado | GuardadoCorrupto, derivada de ErrorGuardado | No se devuelve una historia parcialmente cargada | Pruebas de corrupción y estructura con CRC válido |
| Falla la limpieza del temporal después de fallar el guardado | ErrorGuardado original, con nota sobre el temporal | Causa del primer error y destino anterior; el temporal puede permanecer | test_limpieza_fallida_no_oculta_el_error_principal |

## Política de recuperación

- Una consulta entrega estado independiente: un error no altera el juego vivo ni su historia.
- Registro y recorte verifican todos los valores anteriores antes de cambiar su estado.
- Importación valida sobre una instancia nueva; el consumidor solo la adopta después de una carga exitosa.
- Guardado codifica antes de escribir y utiliza temporal único en el mismo directorio. Solo reemplaza el destino cuando termina de escribir, vaciar buffers y sincronizar el archivo.
- El temporal que se intenta eliminar es exclusivamente el creado por esa llamada. No se borra el destino ni se eliminan archivos por patrones.
- Los errores esperados del dominio mantienen compatibilidad con ValueError. Los de persistencia reutilizan las excepciones de datos existentes.
- No se agrega un `except Exception` para ocultar errores inesperados de programación. Se conservan las causas técnicas para diagnóstico.

## Límites

La escritura atómica protege frente a fallos anteriores al reemplazo; no se afirma durabilidad absoluta ante cortes eléctricos o fallos del sistema de archivos. El lector del fragmento no es el lector integrado de partidas; el rechazo de CRPT aquí no certifica aún la carga interactiva H6.

No se captura todavía este contrato desde el menú o los comandos del juego. Al conectar el controlador, debe distinguir ErrorHistoria y las subclases específicas de ErrorGuardado, mostrar su mensaje y permitir continuar solo si el estado sigue válido. Un CambioHistoriaIncoherente requiere revisar el productor de registros; no debe tratarse como una acción de juego exitosa.

## Verificación reproducible

```powershell
python -m unittest tests.test_errores_historia tests.test_linea_tiempo tests.test_persistencia_historia -v
```

Estos módulos contienen 39 pruebas. Con las regresiones seleccionadas del núcleo, 172 pruebas aprobaron en la ejecución registrada en baseline.md. No equivale a la suite gráfica completa ni a una medición de rendimiento.

## Antecedente — errores en las entradas de D (2026-11-07)

| Entrada | Diagnóstico y efecto |
|---|---|
| Consulta inválida, futura o de acción inexistente | Mensaje en la vista y salida del comando sin mover reloj ni escribir log. |
| Guardado v3 desde la partida de Parte II | Incompatibilidad explícita y partida intacta. |
| CRPT v4 truncado, offset inválido, CRC incorrecto o rama incoherente | Error antes de invocar la restauración del productor. |
| Fallo al reemplazar el guardado | Se conserva el destino previo, se limpia el temporal y se conserva la causa. |
| Argumentos incompatibles de CLI | Error de uso antes de abrir la sesión de datos. |
| Replay inválido o productor histórico ausente | Error de replay; no se construye la vista ni se muestra un resumen incorrecto. |
| Verificación incompleta | Se presenta la causa y se bloquea el inicio, incluso con `--forzar`. |
| Mapa/viaje sin productor | Se informa que la capacidad no está disponible. No se muestra el esqueleto descargado. |
