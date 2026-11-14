# Implementation Plan: Terreno, cazador y validez de rutas

**Branch**: `feature/motor-eventos` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

**Corte histórico del 2026-11-05 (plan provisional).** Plan y 51 tareas generados; dos revisiones Analyze realizadas. Tras las primeras correcciones I1/C1/I2/I3/I4/D1, se incorporan las correcciones documentales I1/I5/C2 de la segunda revisión. Q1–Q3 y contratos externos siguen pendientes. No hay autorización de código, pruebas ni nuevas ejecuciones de habilidades. Estas últimas correcciones requieren revisión posterior autorizada antes de liberar implementación.

**Histórico:** el Plan del 2026-11-02 fue autorizado como borrador condicionado; Tasks y Analyze se autorizaron posteriormente de forma separada. Las prohibiciones previas de avanzar se conservan aquí como historia de permisos, no como una negación de las fases documentales ya realizadas.

**Input**: [Solicitud textual de Plan](prompt-plan-registro-pendiente.md). La exigencia habitual de la habilidad de resolver todas las aclaraciones no se interpreta como permiso para inventar respuestas externas.

## Summary

La búsqueda individual limitada por rango es la base propuesta, con Dijkstra lexicográfico, heap indexado y arreglos propios con marcas por generación. Comparar contra selección lineal, heap con entradas obsoletas y búsquedas compartidas hacia el jugador. El cálculo compartido es exclusivamente alternativa de evaluación: no se integra automáticamente en producción ni tiene umbrales de activación seleccionados. Conservar la agenda actual como candidata inicial y medir su cancelación perezosa frente a eliminación indexada. Son decisiones propuestas con justificación analítica; no ganadoras empíricas.

Los entregables de integración siguen pendientes. La adenda describe la decisión técnica de Persona A para compatibilidad con `historia <t>`, pendiente de validación de integración con D. El algoritmo usa datos válidos suministrados y no hace HTTP. La búsqueda del cazador usa puertas reales. La de C debe usar exclusivamente conocimiento permitido. [Contratos de integración](contracts/integracion.md).

E-B-COSTOS y E-B-RANGO son entregables independientes: T013/T014 requieren solo costos; T025 requiere ambos y el despacho de C. T027 necesita T024 para su finalización completa; una ejecución parcial del núcleo no libera el cierre. La [comunicación reportada de B sobre OpenAPI 1.1.0](research.md#comunicación-reportada-de-b-sobre-openapi-110) carece de copia primaria verificable. La evidencia posterior de entrega y consumo para datos válidos está en los [contratos](contracts/integracion.md). FR-009 recoge la aclaración de que `rango=null` explícito permite buscar sin tope. Q1 sigue abierta para rango ausente o inválido. Q2 conserva la regla de costo ausente 100 y la simetría, con `costo=null`, valores inválidos e inconsistencias aún pendientes.

## Technical Context

### Adenda de frontera temporal (2026-11-06)

El cambio futuro se concentra en el bucle de `Motor._ejecutar_accion()` llamado por `Motor.ejecutar()`. Al obtener el turno vigente del jugador, usar su tiempo como límite, despachar los eventos de ese instante por la ruta existente y cerrar la misma transacción de historial antes de devolver el resultado. Terminar inmediatamente si acaba la partida. El alcance se limita al momento de devolución del control, con el despacho, los costos, el orden del heap, el RNG y la lógica de rutas y cazador actuales. `ejecutar_ciclo()` sin límite conserva su contrato de un evento. [FR-020 y A14–A18](spec.md#frontera-temporal-del-jugador).

El límite debe aplicarse **antes de extraer un evento vigente posterior**, también al descartar raíces canceladas. Una sola inspección de la raíz seguida de `extraer_minimo()` sin límite no basta: esa extracción puede saltar cancelados en t y alcanzar t+1. Opción propuesta: un límite opcional propagado por `ejecutar_ciclo()` al extractor del heap, que compruebe el tiempo de la raíz en cada iteración. Reutiliza el heap y evita escanear `pendientes()` o sacar/reinsertar un evento futuro. Ese auxiliar requeriría autorizar expresamente el ajuste en `modelo/eventos.py`; esta etapa no autoriza ningún cambio de producción.

El lote debe quedar dentro de los deltas y la publicación diferida de mensajes de la acción anterior. Mantener restauración en caso de fallo, contador y azar, y verificar regresiones de retroceso/replay cuando se implemente. La frontera queda pendiente de validación de integración con D. El formato de cambios, las capturas y la reconstrucción siguen pendientes en E-D-CAMBIOS. La medición del ciclo incluirá este trabajo futuro. Q3 sigue pendiente.

**Estado integrado.** La frontera temporal, la restauración y la publicación histórica ya tienen evidencia conjunta en [la entrega integrada](tasks.md#cierre-de-la-entrega-integrada-de-a). La CLI de medición está conectada y queda pendiente medir sobre la referencia oficial Q3.

**Language/Version**: Python ≥3.11 por enunciado; versión exacta y equipo de medición por registrar. No se impone el intérprete auxiliar de lectura de PDF.

**Primary Dependencies**: Ninguna nueva para rutas. list como almacenamiento de bajo nivel, azar controlado y medición de biblioteca estándar. requirements.txt declara requests >=2.31,<3 y Pillow >=10,<13 para adaptadores/vista; esto no acredita versiones instaladas. Spec Kit 1.2.3 y Codex son herramientas de proceso.

**Storage**: Derivados de búsqueda en memoria; D acuerda serialización y formato binario versionado del estado del juego. No persistir resultados de rutas como autoridad.

**Testing**: unittest existente; pruebas nuevas propuestas, no creadas. [Guía de validación](quickstart.md).

**Target Platform**: Entorno local Windows/PowerShell, núcleo Python independiente de vista y red.

**Project Type**: Juego MVC existente y adaptadores externos.

**Performance Goals**: <20 ms por ciclo completo entre decisiones del jugador, decenas de cazadores, sin red ni renderizado. Consulta pequeña limitada a región pertinente, incluyendo inicialización/limpieza. No medido.

**Constraints**: Estructuras y ordenamientos propios; sin dict/set como índices/cachés, heapq, bisect, collections ni bibliotecas de rutas. Semántica determinista de eventos. NEEDS CLARIFICATION: Q1 rango; Q2 datos inconsistentes; Q3 cripta de referencia/enmiendas.

**Scale/Scope**: V salas, E salidas dirigidas (hasta cuatro por sala), H cazadores y N eventos físicos almacenados. No asumir IDs contiguos ni max(ID)=O(V).

## Constitution Check

Revisión previa y posterior del diseño documental, no certificación del programa existente.

| Gate | Antes | Después del diseño provisional |
| --- | --- | --- |
| I: estructuras propias | Obligatorio | Arreglos, heap y búsqueda binaria propios; sin cambiar caché de B. |
| II: determinismo | Obligatorio | Claves explícitas, sin azar en rutas; preservar eventos/azar del motor. |
| III: MVC | Obligatorio | Rutas sin HTTP/vista; integración headless a revisar con D. |
| IV: spec antes de código | Obligatorio | Solo documentos; spec confirmada antes del futuro código sigue siendo gate. No se hicieron commits. |
| V: datos externos | Obligatorio | Datos de B, cifras sintéticas solo en pruebas. |
| VI: red | Obligatorio | Cero solicitudes dentro de rutas; versiones y presupuesto de B. |
| VII: mediciones | Sin evidencia nueva | Matriz prevista; no se afirma rendimiento. Q3 impide certificación final. |
| Documentación y trazabilidad | Obligatorio | Requisitos enlazados; prompt íntegro pendiente de traslado autorizado a bitácora compartida. |
| Aclaraciones cerradas, gate normal de Plan | No cumple: Q1–Q3 | Sigue abierto; se autorizaron Plan/Tasks provisionales y Analyze de lectura, sin PASS global ni autorización de código/pruebas. |

No se solicita excepción a las prohibiciones académicas. El usuario autoriza Plan provisional; no declara resueltas las dependencias.

## Project Structure

### Documentation (this feature)

```text
specs/001-terreno-cazador/
  spec.md                              # requisitos conservados; estado actualizado
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/integracion.md
  prompt-plan-registro-pendiente.md
  tasks.md                             # 51 tareas pendientes, con entregables E-* independientes
  prompt-tasks-registro-pendiente.md
  prompts-registro-local.md             # textos verificables, fechas contextuales y vacíos
  checklists/requirements.md            # criterios sin completar artificialmente
  prompt-registro-pendiente.md          # existente, intacto
```

Tasks ya fue generado en una fase posterior. Los documentos son provisionales y no acreditan ejecución de tareas.

### Source Code (repository root)

```text
modelo/juego.py       # futura integración de A; contiene zonas compartidas
modelo/eventos.py     # agenda; conservar API de historial/guardado
modelo/efectos.py     # integración temporal y puertas de A
modelo/rutas.py       # nuevo propuesto: grafo, espacios de búsqueda y heap
modelo/cazador.py     # nuevo propuesto: política atacar/esperar/paso
tests/               # futuras pruebas de A, con autorización posterior
```

**Structure Decision**: Separar búsqueda y política permite comparar estrategias y probar sin motor. No reutilizar el objeto ColaEventos para rutas: sus eventos, secuencias y cancelaciones tienen semántica del juego. Un heap específico debe justificar similitudes/diferencias y evitar una generalización invasiva.

Consultar sin editar: enemigos.py, historial.py, rastro.py e inventario.py de C; tipos.py compartido; snapshots.py y persistencia de D; red/ de B; controlador/, vista/, main.py y bench.py de D. Los contratos no autorizan alterar esos archivos ni incorporar mocks.

## Decisiones propuestas y hallazgos

1. **Grafo:** adyacencias compactas con índices densos construidos al preparar el esqueleto, IDs externos preservados y estado real de puertas por referencia. Q2 impide cerrar conducta ante inconsistencias.
2. **Individual:** Dijkstra con etiquetas (distancia, primerID), heap propio indexado y generaciones. No explorar candidatos de costo superior al rango ni limpiar V posiciones por consulta.
3. **Compartida:** medir distancias inversas por objetivo y versión de puertas en una alternativa experimental separada de la base individual. Un cache hit exacto es técnicamente aprovechable, pero eso no autoriza activar la estrategia en producción. Una consulta pequeña no dispara una búsqueda global en un fallo. Cualquier integración futura requiere mediciones, prueba de localidad, revisión y autorización; no fijar umbrales de H o rango sin evidencia.
4. **Validez y reutilización:** invalidación global conservadora ante cambio efectivo de puerta, con claves por identidad de grafo/época/origen/objetivo/rango según estrategia. Recalcular siempre es referencia; la caché de última consulta es una alternativa mínima, no la decisión final ni una representante de toda reutilización. Comparar también diseños acotados para consultas alternadas bajo cargas equivalentes, midiendo aciertos, memoria, invalidaciones y mantenimiento con puertas estables/inestables; selectiva es otra alternativa por medir. No descartar reutilización por el resultado de una sola caché.
5. **Agenda:** mantener inicialmente heap propio actual y medir obsoletos; no certificarlo sin carga nueva.

Lectura del código al preparar el plan (línea base histórica):

- mover y la rama de movimiento enemigo usan costo fijo 100; ambos deben utilizar el costo real, conservando 100 en activación inicial.
- cambiar_velocidad ya implementa la fórmula y pasa por cancelación/programación con historial. Conservar y probar.
- ColaEventos preserva identidad, en_cola y contador mediante restauración; una refactorización debe mantener esos contratos.
- Apertura/cierre actualiza la salida local. No se ha probado coherencia entre extremos de una puerta; antes de cachear hay que acordar identidad y propagación con B/C y probar ambos extremos.
- InstanciaEnemigo no declara rango: acceso desde ficha retenida o extensión compartida requieren acuerdo; nunca una descarga en la búsqueda.
- El motor reserva salas por max(ID). El índice denso propuesto evita repetir ese supuesto en auxiliares; no autoriza refactorizar toda la representación compartida.
- El historial usa callbacks reversibles, insuficientes por sí solos como formato serializable de D. A debe proponer cambios explícitos sin reemplazar el historial de C.
- main.ejecutar_replay crea VistaConsola en la rama sin GUI; D debe revisar el requisito sin vista antes de usar ese camino como evidencia headless. A no lo corrige aquí.

En `53c9453`, el movimiento ordinario ya usa costos de salida y el motor despacha al cazador con el grafo completo y las fichas residentes. El grafo conserva referencias a los descriptores de salida y la decisión vuelve a buscar sobre el estado actual. La evidencia de producción para datos válidos no sustituye el acuerdo de despacho E-C-DESPACHO ni acredita la coherencia entre ambos extremos de una puerta. La conexión del mapa y el productor histórico H3 del motor de A siguen bajo activación offline explícita. Véase la [verificación parcial de T027](quickstart.md#revalidación-parcial-de-t027-y-estado-de-integración).

## Dependencias y gates para Tasks

| Pendiente | Evidencia/responsable | Efecto |
| --- | --- | --- |
| Q1 | B/profesor | No cerrar dominio/defaults/invalidez de rango. |
| Q2 | B/contrato/acuerdo respaldado | No cerrar rechazo/normalización/conciliación por sentidos. |
| Q3 | Profesor/fuente oficial | No certificar rendimiento final; sí diseñar y comparar sintéticos. |
| Puertas, filtros, despacho, deltas y guardado | B/C/D con A | Borradores en contracts; no implementados ni aceptados. |
| Revisión del plan y evidencia | Usuario/equipo | Aprobar preferencias o revisarlas; registrar desviaciones motivadas por medición. |

Tasks se generó con alcance condicionado explícitamente autorizado y Q1–Q3 visibles. Cada consumidor espera solo los entregables E-* indicados en tasks.md y contracts/integracion.md, no la finalización global de T003. Actualizar documentación autorizada usa G-DOC; código y pruebas esperan G0/GA, revisión de Analyze vigente y spec confirmada antes del código. Las mediciones finales se incorporarán a DECISIONES.md solo con autorización y evidencia real. Preparar un paquete local no significa publicar cambios compartidos.

## Complexity Tracking

No se justifican violaciones constitucionales. Costos y límites de alternativas en [research.md](research.md). El gate de aclaraciones permanece abierto; la autorización de documentos provisionales no se presenta como cumplimiento final.
