# Manejo de errores — núcleo histórico y persistencia independiente

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

## Errores en las entradas de D (2026-11-07)

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
