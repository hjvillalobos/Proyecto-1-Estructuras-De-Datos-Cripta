# Plan de aceptación y mediciones

Pruebas diseñadas, todavía no implementadas ni ejecutadas. En el código de cada prueba debe aparecer su FR-.

| Caso | Requisito | Preparación y resultado esperado | Tarea |
|---|---|---|---|
| H1 | FR-001,020 | Reloj 100, historia 101: rechazo, estado intacto | T004, T006 |
| H2 | FR-007 | Ejecutar acciones, pergamino, nueva acción: historia refleja solo rama vigente | T008, T009 |
| H3 | FR-002 | Varios eventos en t, incluido uno que agenda otro en t: incluir todos antes de decisión | T003, T004, T006 |
| H4 | FR-005 | Comparar estado, RNG, log y retroceso antes/después de consultar: idénticos | T004, T006 |
| H5 | FR-014 | Replay termina en 100; --hasta 200: estado final y aviso, sin vista | T012, T014 |
| H6 | FR-012 | Archivo P1 formato 3: incompatibilidad explícita y original conservado | T008, T011 |
| R4 integración | FR-016 | No resoluble sin --forzar: reporte y no inicia; con --forzar permite inicio | T012, T015 |
| EX01 | FR-003 | #1 y #k antes de acción, especialmente si comparten reloj | T004, T006 |
| EX02 | FR-008,020 | K=0, negativo, texto; t negativo; #0 o inexistente: errores sin efectos | T004, T012, T013 |
| EX03 | FR-009,010 | K=1 y K=10; consultas junto a límites y entre eventos: <=K acciones reconstruidas | T004, T005, T006 |
| EX04 | FR-011 | Guardar/cargar antes/después de pergamino y checkpoint: igual historia, RNG y continuación | T008, T011 |
| EX05 | FR-017 | Sustituir constructores de vista por fallo deliberado: replay/bench/verificar terminan sin invocarlos | T012, T013, T014 |
| EX06 | FR-018,019 | Vista consume mapa de conocimiento; no revela salas desconocidas; cada paso viaje genera movimiento | T016, T017, T018 |
| EX07 | FR-011 | Archivo truncado, CRC inválido, offsets inválidos: error y partida activa intacta | T008, T011 |
| EX08 | FR-004,010 | Consulta entre decisiones reconstruye enemigos, efectos, puertas y conocimiento históricos correctos | T004, T006, T010 |

## Protocolo de bench integración

Semillas fijas y cargas comparables. Al menos 5 000 acciones; tamaños de estado y densidades de cambios diferentes; K 10/50/100 y reconstrucción desde inicio sin controles. Consultas al inicio/medio/final y junto a controles; medir localización y reconstrucción por separado y juntas. Comparar inversión desde presente cuando la captura permita esa alternativa. Medir recorte con prefijos crecientes y sufijo fijo; registrar liberación de memoria aparte.

Una repetición de calentamiento y al menos cinco repeticiones medidas, misma máquina y entorno. Registrar Python, sistema, CPU/RAM, semilla, acciones, eventos, volumen de cambios, copias completas, pico de memoria y bytes persistidos. Tiempos: media, mediana, p95, máximo y número de consultas >50 ms. El límite debe informarse por consulta, no ocultarse en un promedio. Separar red, preparación y renderizado. Verificar igualdad del resultado antes de aceptar una muestra.

Además del tiempo, instrumentar número de acciones reconstruidas para certificar el límite K. Medir historia de 10 000 o más acciones para estudiar crecimiento, sin sustituir el caso mínimo exigido. La referencia publicada y cualquier enmienda del profesor prevalecen.

## Plantilla de resultados (sin datos inventados)

| K | Acciones/eventos | Memoria pico | Búsqueda | Reconstrucción p95/máx | Total máx | Acciones reconstruidas máx | Correcto |
|---|---|---|---|---|---|---|---|
| 10 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| 50 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| 100 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Sin controles | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Puede superar K | Pendiente |
