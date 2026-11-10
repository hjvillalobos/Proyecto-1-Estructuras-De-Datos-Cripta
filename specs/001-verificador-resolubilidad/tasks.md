# Tasks: Verificador de resolubilidad

**Fecha:** 2026-11-01. **Rama:** `codex/verificador-resolubilidad`.

**Entrada:** [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contrato](contracts/verificador.md) y [quickstart.md](quickstart.md).

**Estado:** implementación autorizada y en curso. Preparación confirmada en el commit `17dc4bc`, anterior al código. Línea base: 69 pruebas aprobadas. Solo se marcan tareas completadas y verificadas; no se autoriza un nuevo commit con este registro.

**Reglas:** B es responsable salvo indicación D o B+D. Sin tablas hash como índices, ordenamientos automáticos, bibliotecas de grafos ni comentarios nuevos en código. Se reutilizan las estructuras existentes. El dictamen usa alcanzabilidad acumulada confirmada, no trayectoria única. Toda prueba cita FR y AC en su nombre o identificador, sin exigir comentarios en código.

**Formato:** casilla, ID correlativo, `[P]` cuando hay independencia real dentro de una fase y `[USn]` en tareas de historias. Las rutas son relativas al repositorio. `[P]` indica posibilidad de coordinación, no autorización para lanzar agentes. Los cambios futuros en documentos conservan la aprobación solicitada por el usuario.

## Fase 1 — Preparación

Objetivo: asegurar antecedentes y estado reproducible; no reinicializar proyecto ni instalar dependencias nuevas.

- [X] T001 Verificar que `specs/001-verificador-resolubilidad/spec.md`, `plan.md` y este `tasks.md` pasaron `speckit-analyze`, que se resolvieron hallazgos críticos y que el commit de especificación precede al código; preservar archivos ajenos. Aceptación: identificar commit y resultado del análisis antes de T002. (FR-001–015; constitución IV) C1 aprobado el 2026-11-02 por respuesta afirmativa del profesor comunicada por el usuario; verificar registro de esa aclaración y commit previo, sin marcar esta tarea ejecutada todavía.
- [X] T002 Ejecutar la línea base de `tests/test_cliente_api.py`, `tests/test_precarga_offline.py`, `tests/test_sesion_datos.py`, `tests/test_cache.py` y `tests/test_catalogo.py`; distinguir fallos previos de regresiones sin corregir módulos ajenos automáticamente. (FR-008–011, FR-014)

## Fase 2 — Base compartida

Objetivo: registros y validación reutilizables. Depende de T001–T002; ninguna historia modifica código antes de cerrar esta fase.

- [X] T003 Definir registros de entrada y resultado en `modelo/resolubilidad.py` según `data-model.md`: «Datos completos de una misma versión; IDs de inicio/salida existentes», «ID entero, no booleano, único; direcciones válidas sin duplicación», «Destino existente; estado booleano normalizado; cerrada exige llave válida», «ID de texto válido, sala existente; enemigo ausente o nulo significa suelo. Repetir ID en otras ubicaciones es válido». Mantener estados `resoluble`, `no_resoluble`, `no_completada`, modelo `alcanzabilidad_acumulada` y limitación explícita; «versión puede faltar si no se obtuvieron datos válidos». No iniciar vista ni red. (FR-008, FR-010, FR-012–014)
- [X] T004 Agregar pruebas de esos registros y sus invariantes en `tests/test_resolubilidad.py`: bool como entero, sala duplicada, destino inexistente, campo obligatorio ausente, llave con varias ubicaciones y resultado incompleto sin diagnóstico concluyente. Comprobar entradas no mutadas. (FR-008, FR-010, FR-012, FR-014; AC-14, AC-18)
- [X] T005 Implementar validación y normalización en `modelo/resolubilidad.py`, reutilizando `utilidades/ordenamiento.py` en modo fusión y búsqueda binaria propia: índices densos, llaves de puertas/salida sin ubicación y deduplicación contigua de ubicaciones idénticas. Aplicar «cerrada omitida o nula equivale al estado abierto por defecto» y «Una salida abierta no exige poseer su llave declarada». Ejecutar T004; ningún índice se dimensiona por máximo ID. (FR-001, FR-003–004, FR-007–008, FR-010, FR-015)

## Fase 3 — US1: Dictamen acumulativo y orden de llaves (P1, MVP)

Objetivo: analizar datos preparados sin red. Prueba independiente: entradas pequeñas con resultado conocido, orden válido y diez ejecuciones idénticas. Depende de la base; no necesita US3.

- [X] T006 [US1] Escribir pruebas en `tests/test_resolubilidad.py` para cadena, llave de salida ausente, entrada incorrecta a salida, llave en sala inicial/enemigo inicial, llave reutilizable, trampas/autocierre no bloqueantes y alternativas de ubicación. Incluir AC-21 y puerta abierta examinada antes de obtener la llave de salida; comprobar fallos antes de implementar recorrido. (FR-001–004, FR-007, FR-010, FR-013; AC-01–05, AC-08, AC-21)
- [X] T007 [US1] Implementar recorrido incremental en `modelo/resolubilidad.py`: cola con lista/índice, marcar al encolar, llaves antes de salidas N/S/E/O, activar pendientes una vez por llave, conservar primera evidencia y no repetir salas ni IDs de llave. Criterio: pasan cadenas, ubicaciones alternativas y ramas sin regreso según AC-21. (FR-001, FR-003–004, FR-007, FR-015)
- [X] T008 [US1] Implementar condición final y resultado positivo en `modelo/resolubilidad.py`: llave de salida obtenida más entrada que la requiere desde origen alcanzado; no basta alcanzar sala de salida. Incluir modelo/limitación y orden de obtención, sin certificar una trayectoria única. (FR-002, FR-004, FR-012–013; AC-01–02, AC-21)
- [X] T009 [US1] Completar y ejecutar en `tests/test_resolubilidad.py` diez repeticiones, variantes de orden de entrada normalizada, IDs dispersos y comprobación independiente del orden: cada llave alcanzable con las anteriores. Verificar ausencia de mutaciones, red, vista y cambios de azar/reloj. No usar el mismo algoritmo como único oráculo. (FR-004, FR-007, FR-014; AC-04, AC-18)

Checkpoint: MVP del análisis positivo sobre datos sintéticos. No equivale a verificador completo ni a integración del juego.

## Fase 4 — US2: Frontera, llaves inaccesibles y ciclos (P1)

Objetivo: explicar dictámenes negativos. Depende de US1. Prueba independiente: autoencierro, cadena circular y desconexión, con evidencias verificadas contra entrada.

- [X] T010 [US2] Escribir casos negativos en `tests/test_resolubilidad.py`: autoencierro R1, ciclo A→B→A, alternativas accesibles, alternativa bloqueada por llave ausente, región desconectada, ciclo solo de salas y llave opcional inaccesible. Exigir frontera y ausencia de ciclos inventados; comprobar fallos antes del diagnóstico. (FR-002, FR-005–008; AC-06–10) Incluir AC-22: región desconectada con K en A, A→B abierta y B→A que exige K; no certificar esa puerta de regreso como causa del bloqueo. Agregar AC-24 y AC-25 antes de implementar, incluyendo dos SCC dependientes y múltiples ciclos en una SCC.
- [X] T011 [US2] Construir en `modelo/resolubilidad.py` el grafo de condiciones y certificado global con valores finales, todas las alternativas OR y requisitos AND; justificar cada pendiente por requisitos falsos o ausencia. Conservar referencias compartidas para no expandir dependencias por llave. (FR-005–007, FR-015)
- [X] T012 [US2] Obtener llaves inaccesibles y frontera en `modelo/resolubilidad.py`: puerta cerrada de origen alcanzado con llave no obtenida; llave ausente tiene ubicaciones vacías; frontera puede estar vacía. Diferenciar imposibilidad de salida, ausencia de llave y desconexión. (FR-005–006, FR-008; AC-06, AC-09–10)
- [X] T013 [US2] Implementar en `modelo/resolubilidad.py` Kosaraju iterativo, accesibilidad estructural global y testigo determinista por componente con llaves; adjuntar integrantes y referencias a alternativas del certificado. Clasificar como bloqueo_circular_autonomo, dependencia_circular_con_bloqueos_externos o ciclo_en_region_desconectada. El certificado global demuestra pendientes; las SCC describen ciclos sin atribuir exclusividad. (FR-005–007, FR-015; AC-06–08, AC-22, AC-24–25)
- [X] T014 [US2] Completar `tests/test_resolubilidad.py` validando todas las alternativas del certificado y cada arco del testigo contra entrada; R1/AC-07 muestran ciclos concretos. Incluir AC-22, AC-24 y AC-25: desconexión, bloqueos entre componentes y varios ciclos en un grupo. Comprobar que ningún pendiente carece de explicación, alternativas accesibles eliminan bloqueo, el orden es determinista y el reporte no se duplica por llave. (FR-005–007, FR-015)

## Fase 5 — US3: Red, versiones y offline (P1)

Objetivo: preparar entradas compatibles y distinguir errores de información. Prueba independiente: transporte falso y archivos temporales con iguales datos online/offline. Preparación puede desarrollarse tras la base; validación integral depende de US1 y US2.

- [X] T015 [P] [US3] Agregar pruebas HTTP en `tests/test_cliente_api.py` para ruta de llaves, UUID estable, intentos incluidos 429 y consultas de versión, agotamiento y respuesta inválida; esperas no modifican reloj virtual. (FR-009; AC-12, AC-14)
- [X] T016 [P] [US3] Crear `tests/test_verificacion_datos.py` con contratos de persistencia, listado vacío frente a archivo ausente/corrupto, versiones históricas y cambio de versión durante adquisición; comprobar fallo inicial de capacidades nuevas. (FR-008, FR-010–012; AC-11, AC-13–14) Añadir AC-23 con segunda ejecución offline tras cambio de versión, fallo de consulta final y agotamiento de presupuesto; comprobar copias previas intactas y ausencia de datos rechazados.
- [X] T017 [US3] Agregar `obtener_llaves` en `red/cliente_api.py` usando `_hacer_peticion_get` y validación de ID existentes; no duplicar transporte, UUID o contador. Ejecutar T015. (FR-009–010; AC-12)
- [X] T018 [US3] Agregar validación de respuesta de llaves en `red/validacion.py`: lista obligatoria, campos `id`/`sala`, enemigo opcional/nulo, sin rechazar varias ubicaciones por ID. Distinguir formato inválido de llave requerida no publicada. (FR-008, FR-010, FR-012; AC-08, AC-14)
- [X] T019 [US3] Agregar `leer_llaves`/`guardar_llaves` en `datos/almacen.py` bajo versión de cripta, escritura temporal y reemplazo existentes; validar antes de publicar y conservar versiones anteriores. Probar fallo de escritura sin destruir copia previa y retorno `None` solo para ausencia. (FR-008, FR-010–012; AC-11, AC-14) Publicar únicamente tras autorización del coordinador posterior a comprobación final de versión; actualizar actual.json al final. Un fallo de escritura puede dejar solo archivos de la misma versión ya validada; el lector detecta faltantes.
- [X] T020 [US3] Agregar `obtener_llaves` y selección coherente de versión en `datos/offline.py`, preservando llamadas existentes; generales, páginas y llaves usan versión explícita cuando se solicita, sin sustituirla por `actual.json`. Ausencias generan `DatosNoDisponibles`, cero HTTP. (FR-008, FR-010–012; AC-11, AC-13–14)
- [X] T021 [US3] Extraer en `red/precarga.py` la preparación común de generales y esqueleto sin iniciar catálogo ni descargar contenido para verificar; conservar comportamiento de `preparar_cripta`. Ejecutar regresiones en `tests/test_precarga_offline.py` y `tests/test_sesion_datos.py`. (FR-008–009, FR-014; AC-11–12, AC-18) Separar adquisición de persistencia para que el coordinador pueda mantener el lote nuevo privado; evitar escrituras anticipadas de generales/páginas en el flujo de verificación.
- [X] T022 [US3] Implementar `preparar_verificacion` y coordinador de resultado en `red/verificacion.py`: versión antes/después de adquisición, presupuesto desde generales, validación completa antes de exponer datos, históricos compatibles y conversión de errores esperados a `no_completada`. No capturar indiscriminadamente errores de programación. (FR-008–012, FR-014; AC-11–14) Mantener lote descargado en memoria; no guardar ni actualizar actual.json hasta validar conjunto y versión final. Descartarlo si cambia versión o falla comprobación; conservar copias previas. (AC-23)
- [X] T023 [US3] Completar `tests/test_verificacion_datos.py` y ejecutar pruebas US3: igualdad de dictámenes/reportes online/offline, reuso válido sin red innecesaria, paginación completa, cambio de versión sin mezcla, presupuesto insuficiente, catálogo independiente y ninguna descarga de contenido ni activación. Distinguir llave ausente válida de entrada sin sala. (FR-008–012, FR-014; AC-11–14, AC-18) Ejecutar AC-23 sobre disco real temporal y una instancia offline nueva; no limitar la prueba al estado de error de la primera ejecución.

## Fase 6 — US4: Entregar resultado e integrar con D (P2)

Objetivo: usar el resultado antes de jugar sin absorber la interfaz de D. Depende de US1–US3. Prueba independiente: matriz de tres estados, con/sin forzar, sin vista en verificación exclusiva.

- [X] T024 [US4] B: agregar pruebas de contrato del resultado en `tests/test_verificacion_datos.py`: tres estados, identidad/versión, alcance/limitación, diagnóstico y errores sin dictamen parcial; validar que D no necesita ejecutar lógica de B para mostrarlo. (FR-012–014; AC-15–18, AC-21)
- [ ] T025 [US4] D con revisión B: conectar en `main.py` el coordinador para `--verificar`, `--forzar` e inicio normal según `specs/001-verificador-resolubilidad/contracts/verificador.md`; mostrar alcance acumulativo. No instanciar vista/motor en verificación exclusiva; error de datos bloquea incluso con forzar. (FR-012–014; AC-15–18, AC-21)
- [X] T026 [US4] B+D: incorporar en `tests/test_verificacion_entrega.py` pruebas de inicio y salida exclusiva para todos los estados, R4, forzar y ausencia de importaciones/instancias de vista; ejecutar con la integración real de T025. Si D no integró, mantener tarea pendiente, no marcarla satisfecha con un doble. (FR-012–014; AC-15–18, AC-21)

## Fase 7 — US5: Rendimiento con evidencia (P2)

Objetivo: comparar incremental y repetitivo y medir total. Depende de US1–US3; integración de medición con D puede avanzar sin US4 si no hay cambios simultáneos en el mismo archivo.

- [X] T027 [US5] Crear `tests/test_bench_resolubilidad.py` con comparación lógica, órdenes válidos, repetibilidad por semilla y conteos de trabajo en cadenas/ciclos/alternativas; sin afirmar tiempos por pruebas frágiles. Exigir que el total incluya normalización, diagnóstico y reporte. (FR-007, FR-015; AC-19–20) Probar contadores separados de normalización/recorrido/diagnóstico/reporte y familias N, 2N, 4N; incluir conteo de relaciones examinadas al certificar ciclos.
- [X] T028 [US5] Implementar en `utilidades/bench_resolubilidad.py` generadores sintéticos reproducibles y referencia de recorrido repetido, aislados de producción; validar órdenes y dictámenes iguales antes de comparar. Generador local no altera azar del juego. (FR-014–015; AC-19)
- [X] T029 [US5] Implementar medición en `utilidades/bench_resolubilidad.py` para al menos tres tamaños, diez repeticiones y cripta real preparada: muestras, promedio, mínimo, máximo, desviación, visitas y pendientes, tiempo total y desglose; disco/red separados. Ejecutar T027 y comprobar que el benchmark no hace HTTP. (FR-015; AC-19–20; SC-003–005) Aplicar protocolo del plan: N=V+E+K+L, razones entre tamaños, trabajo/N y comparaciones/(N log2(max(2,N))), longitud de IDs y tamaño del reporte. No excluir normalización del total ni afirmar linealidad estricta.
- [ ] T030 [US5] D con revisión B: conectar subsistema `resolubilidad` en `bench.py` y entrada `--bench` de `main.py`, reutilizando parámetros tamaños/repeticiones/semilla y paquete/cripta. Validar comando de `specs/001-verificador-resolubilidad/quickstart.md` sin vista. (FR-014–015; AC-19–20)
- [ ] T031 [US5] B: ejecutar mediciones sintéticas y mayor cripta publicada disponible; con aprobación documental, registrar evidencia en `DECISIONES.md` con versiones, equipo, tamaño, muestras, complejidad y límites. Si falta la cripta real o supera 200 ms, dejar AC-20 pendiente o fallido, sin declararlo aprobado por promedio. (FR-015; AC-19–20; SC-003–004) Documentar que total O(N log N + salida) no equivale a linealidad estricta; mantener evaluación de FR-015 pendiente si la evidencia o criterio académico no respalda crecimiento aproximadamente lineal.

## Fase 8 — Cierre y revisión transversal

Depende de historias completadas; no sustituye la revisión de D ni la evidencia faltante.

- [X] T032 Revisar `modelo/resolubilidad.py`, `red/verificacion.py` y `utilidades/bench_resolubilidad.py` contra la constitución: índices propios, sin recorridos completos por llave en producción, sin comentarios nuevos ni datos de criptas reales incrustados. Ejecutar pruebas de todas las historias y regresiones de red/caché/inicio; corregir solo regresiones atribuibles al cambio. (FR-001–015)
- [X] T033 Con aprobación documental, actualizar `README.md` y `specs/001-verificador-resolubilidad/quickstart.md` con comandos realmente disponibles y resultado de validación; enlazar `DECISIONES.md` sin inventar resultados, mantener alcance confirmado y limitación. (FR-013–015; AC-15–21)
- [ ] T034 Con aprobación documental, completar trazabilidad y estado real en `specs/001-verificador-resolubilidad/tasks.md` y `PROMPTS_LLM.md`; solicitar revisión cruzada B↔D, verificar commit previo de especificación y no marcar como completas tareas de D o mediciones pendientes. (FR-001–015; constitución IV) Registrar también recomendaciones aprobadas y conservar explícitos los controles pendientes; conservar la procedencia de la confirmación: respuesta afirmativa comunicada por el usuario el 2026-11-02.

## Dependencias y orden de ejecución

```text
T001 → T002 → T003 → T004 → T005
Base → US1 (T006–T009) → US2 (T010–T014)
Base → US3 preparación (T015–T022)
US1 + US2 + preparación US3 → T023
US1 + US2 + US3 → US4 (T024–T026)
US1 + US2 + US3 → US5 (T027–T031)
US4 + US5 → cierre (T032–T034)
```

Dentro de cada historia se sigue el orden numérico salvo las dos pruebas independientes T015/T016. T017 requiere T015; T018 requiere T016 y base; T019 requiere T018; T020 requiere T019; T021 requiere T020 para comprobar regresión offline; T022 requiere T017–T021. T028 precede a T029; T030 requiere T029; T031 requiere T030 y datos reales preparados. Las pruebas nuevas se escriben antes de su implementación y se confirma que fallan por la capacidad ausente, no por entorno roto.

## Paralelismo seguro

- US1: T006–T009 son secuenciales por compartir `modelo/resolubilidad.py` y su archivo de pruebas. Tras base, US3 puede avanzar en red/datos sin tocar esos archivos.
- US2: T010–T014 son secuenciales; preparación US3 puede continuar en paralelo. No editar simultáneamente normalización y diagnóstico del mismo módulo.
- US3: T015 y T016 pueden escribirse a la vez en archivos distintos. No ejecutar una integración que dependa de implementación aún incompleta.
- US4: T024 precede a T025/T026. D puede integrar T025 mientras B desarrolla mediciones T027–T029; no modificar simultáneamente `main.py` en T025 y T030.
- US5: T027–T031 son secuenciales; T028/T029 pueden coincidir con T025. La evidencia real no se reemplaza por pruebas sintéticas.

## Matriz mínima de aceptación

| Escenarios | Pruebas/tareas responsables |
|---|---|
| AC-01–05 | T006, T009 |
| AC-06–10 | T010, T014; AC-08 también T006 |
| AC-11–14 | T015, T016, T023; validaciones base T004 |
| AC-15–18 | T024, T026; aislamiento T009, T023 |
| AC-19–20 | T027, T029, T031 |
| AC-21 | T006, T024, T026 |
| AC-22 | T010, T013, T014 |
| AC-23 | T016, T019, T021–T023 |
| AC-24–25 | T010–T014 |

R1 → AC-06/T010/T014; R2 → AC-03/T006; R3 → AC-04/T009; R4 → AC-15/T026. Todos los FR-001–015 aparecen en tareas. La cobertura documental no prueba cumplimiento funcional.

## Estrategia de entrega

Primero base + US1 como MVP verificable con datos sintéticos. Añadir diagnóstico US2 y adquisición US3 sin mezclar análisis con red. Después integrar con D y medir. Cada incremento debe pasar sus pruebas antes del siguiente; los errores de especificación se corrigen y confirman por separado antes de cambiar código. No considerar toda la parte B terminada: terreno/cazadores están fuera de esta especificación.


## Avance verificado — 2026-11-02

- Preparación previa: `17dc4bc`; autorización de implementación y de documentación recibidas en el chat. No se realizó un commit del código.
- T001–T024: implementadas y verificadas. Las pruebas iniciales fallaron por capacidades ausentes antes de añadirlas. Análisis puro, diagnóstico, transporte, persistencia, selección de versiones y preparación sin motor disponibles.
- T027–T029: funciones y pruebas de benchmark disponibles; tres tamaños y familias, diez muestras por estrategia. Medición real de `cripta-06` de 300 salas, versión `f9ed9afa683d`, registrada en `mediciones.json`.
- T033: README y guía actualizados con funciones disponibles y comandos de D aún pendientes; cambios documentales autorizados expresamente.
- Revisión ampliada: 176 pruebas ejecutadas, 175 aprobadas y una prueba opcional existente omitida. La API real se consultó aparte para preparar y medir la mayor cripta publicada.
- T025/T026/T030: pendientes de integración de D y validación conjunta real. No se alteraron `main.py`, `bench.py` ni las pruebas de entrega para simular esa integración.
- T031: mediciones y decisión documentadas; las muestras de la cripta real cumplen 200 ms en este equipo. Se mantiene abierta por la dependencia de T030 y la revisión del crecimiento aproximadamente lineal de FR-015. No se deduce cumplimiento asintótico de los tiempos.
- T032: auditoría de B y regresiones completadas sin fallos; cierre transversal pendiente de la integración y pruebas de D.
- T034: prompt y trazabilidad registrados con autorización. Falta revisión cruzada B↔D; conservar esta casilla pendiente hasta completarla.
- `.idea/` se conserva sin modificaciones. No hay hooks de implementación en `.specify/extensions.yml`.

## Revisión de B del 2026-11-10

Rama `codex/verificador-resolubilidad`, base `694dcf6`. Especificación previa comprobada en `17dc4bc`. El registro del 2 de noviembre describe el estado de aquella fecha.

| Tarea | Resultado |
|---|---|
| T025 | Inicio y verificación exclusiva integrados. Queda un detalle de presentación para D. Con `no_completada`, el informe retorna la causa antes de mostrar la limitación que el contrato pide mostrar siempre. |
| T026 | Aprobada. Seis inicios y tres verificaciones exclusivas en procesos nuevos, con paquetes offline, motor y controlador reales. Se comprobaron dictamen, código de salida, cierre de la sesión y creación de la bitácora de partida. En verificación exclusiva se comprobó además que no se importaran vista ni motor. [Prueba reproducible](../../tests/test_verificacion_entrega.py). |
| T030 | Pendiente de D. Con las repeticiones predeterminadas el comando termina con error. Con diez repeticiones acepta paquete y cripta pero solo emite las familias sintéticas. |
| T031 | Revisión de rendimiento de B realizada. Evidencia real y evaluación de FR-015 en [DECISIONES.md](../../DECISIONES.md) y [mediciones.json](mediciones.json). Cierre de la tarea condicionado a repetir T030 tras el ajuste de D. |
| T032 | Revisión de B completada sobre esta base. Se ejecutaron 162 pruebas seleccionadas de las cinco historias y regresiones, con 161 aprobadas y una opcional omitida. La revisión de los tres módulos de cálculo, preparación y medición no encontró índices hash ni ordenamientos automáticos. |
| T033 | Guía y README actualizados con las opciones disponibles y los límites reproducidos. |
| T034 | Prompt y resultados registrados. La aceptación comunicada para costos, rango y descarga offline corresponde a las entregas anteriores. Queda la revisión cruzada con D de los hallazgos de esta fecha. |
