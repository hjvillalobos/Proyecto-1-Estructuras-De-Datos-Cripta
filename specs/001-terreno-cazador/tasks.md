# Tasks: Terreno, cazador y validez de rutas — Persona A

**Fecha:** 2026-11-02. **Rama:** `feature/motor-eventos`.

**Input:** [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contratos](contracts/integracion.md), [quickstart.md](quickstart.md) y constitución 1.1.0.

**Estado al 2026-11-05:** lista provisional de 51 tareas; segunda revisión Analyze realizada. Se incorporan las correcciones documentales I1/I5/C2 autorizadas después de las primeras correcciones I1/C1/I2/I3/I4/D1. Esta autorización no permite código ni pruebas, ni repetir Tasks/Analyze/Implement. Q1–Q3 siguen abiertas. Ningún checkbox se marca completado por estas correcciones. Histórico: la generación inicial de Tasks fue el 2026-11-02 y también fue exclusivamente documental.

**Actualización posterior — implementación limitada 2026-11-05:** el usuario autoriza explícitamente solo T005–T010, modelo/rutas.py, sus nuevas pruebas y documentación propia. Se revisaron I1/I5/C2 antes de escribir: entregables costos/rango separados, cierre T027 dependiente de T024 y reporte de B indirecto. Spec protegida en 4ee04ff; sin cambios seguidos al iniciar. Se liberan G0/GA exclusivamente para estos fundamentos sobre datos sintéticos válidos; GB1/GB2 no impiden este alcance y continúan abiertos para políticas e integración. No se libera ninguna entrega externa, T001–T004 ni T011–T051. La prohibición del párrafo anterior describe la corrección documental previa. Checklist leído: 13/16, sin modificarlo. Evidencia y límites en quickstart.md.

## Formato, alcance y gates

Cada tarea usa `- [ ] Tnnn [P?] [USn?] descripción`, ruta exacta relativa al repositorio, referencias FR/NFR y escenarios. Los números de tarea T001… son distintos de los casos de aceptación T1–T7. `[P]` permite trabajo simultáneo solo tras completar sus dependencias y liberar gates; no autoriza otros agentes ni ejecución actual.

Tipos: **BASE** (implementación propuesta), **PRUEBA**, **EVAL** (comparación aislada) y **DOC**. EVAL no activa alternativas en producción ni impone umbrales no medidos. Todas las pruebas nuevas se solicitan expresamente y deben citar sus FR/NFR.

| Gate/condición | Estado y condición de liberación |
| --- | --- |
| G-DOC | Autoriza solo actualizar documentos en las rutas y alcance expresamente pedidos. La autorización actual cubre I1/I5/C2 y su registro local. La espera del profesor no bloquea estas correcciones documentales. No necesita Implement para registrar evidencia, y no libera contratos ni marca tareas ejecutadas. |
| G0 | BLOQUEO de código y ejecución de pruebas/benchmarks: exige autorización posterior de implementación y pruebas, revisión de Analyze vigente, documentos/checklists y evidencia de spec confirmada antes de cualquier código que la implemente. Correcciones posteriores al Analyze deben revisarse antes de considerar liberado este gate. |
| GA | Los archivos Python nuevos, pruebas y utilidades propuestos aquí requieren autorización posterior de sus rutas. Los tres archivos de A contienen partes compartidas: solo su lógica aprobada. |
| GB1 / Q1 | B/profesor confirma dominio y validación de rango. Sin mínimo, default ni política de invalidez inventados. |
| GB2 / Q2 | B/contrato/acuerdo respaldado confirma costos inválidos/asimétricos/unilaterales y disponibilidad de datos válidos. |
| E-B-COSTOS | PENDIENTE: entrega verificable de B de suministro/acceso a costos de salidas, versiones, identidad y datos válidos para el motor, sin HTTP durante búsqueda. Independiente de E-B-RANGO; no cierra Q2. |
| E-B-RANGO | PENDIENTE: entrega verificable de B de suministro/acceso a rango de cazadores, versiones, identidad y datos válidos, sin HTTP durante búsqueda. Independiente de E-B-COSTOS; no cierra Q1. |
| E-BC-PUERTA | Acuerdo específico B/C/A de identidad y estado real coherente entre extremos, lectura y notificación de cambios. |
| E-C-RUTA | C acuerda fuente filtrada, modos y estados del resultado de consulta. |
| E-C-DESPACHO | C acuerda conexión de cazador conservando sus comportamientos y firma existente. |
| E-C-OBS | C acuerda observaciones de entrada/puertas/antorcha y qué cambios de conocimiento le pertenecen. |
| E-C-UNDO | C acuerda uso del historial y deltas reversibles de A, sin sustituir inventario/conocimiento. |
| E-D-CAMBIOS | D acuerda sobre de cambios, identidades, tiempos/secuencias/azar y puntos de captura de A. |
| E-D-RESTAURA | D entrega/admite contrato de restauración/carga necesario para las pruebas de A. |
| E-D-MEDICION | D acuerda función de medición de A y entrega su conexión sin vista a bench.py. |
| GR / Q3 | Profesor identifica cripta/versión de referencia y enmiendas aplicables. Sin esto no se certifica <20 ms. |

«CONDICIONADA GB1/GB2» permite código/pruebas de núcleo con datos válidos explícitos solo cuando G0/GA se liberen expresamente para ese alcance. La preparación documental usa G-DOC. Ninguna de las dos autorizaciones permite asumir política de errores ni declara respondidas Q1/Q2. Las pruebas de invalidez esperan evidencia. Cada entrega E-* tiene estado y evidencia independientes en contracts/integracion.md; no se satisface por registrar un pendiente ni por completar otro acuerdo. Si falta una entrega se detiene solo su consumidor, sin implementar módulos ajenos ni añadir mocks sin permiso.

En todos los trabajos futuros: estructuras propias y list de bajo nivel; sin dict/set como índices/cachés, heapq, bisect, collections, bibliotecas de grafos ni ordenamientos evaluados de biblioteca. Ningún nuevo HTTP, vista, recurso visual o dato real quemado. Consultar archivos B/C/D no autoriza editarlos.

## Phase 1: Setup documental y acuerdos de alcance

**Objetivo:** registrar evidencia y decisiones externas con autorización documental G-DOC, sin necesitar Implement ni liberar G0. Su listado no significa que estén realizadas; ausencia de evidencia se registra como pendiente, no como cumplimiento.

- [ ] T001 DOC Registrar en specs/001-terreno-cazador/research.md la evidencia recibida para Q1 y su fuente/fecha; actualizar propuesta de entrada en specs/001-terreno-cazador/contracts/integracion.md solo conforme a esa evidencia, manteniendo «sin mínimo/default/invalidez inventados» hasta entonces. Registrar comunicación parcial de B usa G-DOC; cierre BLOQUEADO GB1 hasta fuente y aclaración suficientes, sin considerar el reporte OpenAPI verificación independiente. Dep: ninguna. [FR-007, FR-009; NFR-006; T2, A3, A4]
- [ ] T002 DOC Registrar en specs/001-terreno-cazador/research.md la evidencia de Q2 y delimitar en specs/001-terreno-cazador/contracts/integracion.md validación de B frente a consumo de A; conservar «costo ausente 100; declarado entero ≥1 y simétrico para datos válidos» sin corregir/rechazar por iniciativa propia. Registrar comunicación parcial de B usa G-DOC; cierre BLOQUEADO GB2: costo null e inconsistencias siguen sin política, sin confundir null con ausencia. Dep: ninguna. [FR-001; NFR-006; A1, A2]
- [ ] T003 DOC Mantener en specs/001-terreno-cazador/contracts/integracion.md registros separados E-B-COSTOS, E-B-RANGO, E-BC-PUERTA, E-C-RUTA, E-C-DESPACHO, E-C-OBS, E-C-UNDO, E-D-CAMBIOS, E-D-RESTAURA y E-D-MEDICION: responsable, alcance, evidencia/fecha y estado. Puede prepararse con G-DOC; su checkbox solo se completa cuando todas las entregas requeridas estén verificadas. Los consumidores dependen de sus E-* concretos, nunca de completar T003 entero. Todos siguen pendientes hasta evidencia; A no implementa componentes ajenos. Dep: ninguna. [FR-008, FR-012, FR-015, FR-018, FR-019; NFR-004, NFR-006; A5, A9–A13]
- [ ] T004 DOC Documentar en specs/001-terreno-cazador/research.md cripta/versión oficial, equipo y posibles enmiendas de Q3 con fuente; mantener <20 ms y condiciones oficiales sin evidencia contraria. BLOQUEADA GR; no bloquea por sí sola experimentos sintéticos autorizados. Dep: ninguna. [NFR-001, NFR-003; P1]

**Checkpoint:** T001/T002 no se sustituyen por suposiciones. Un registro parcial de T003 deja su checkbox pendiente y puede acreditar únicamente la entrega E-* cuya evidencia se haya revisado. No libera ningún otro E-*. Q3 queda pendiente sin falsa certificación.

## Phase 2: Foundational — datos de prueba y representación propia

**Objetivo:** representación y soporte común sin estructura de bibliotecas. Las tareas de núcleo sobre datos válidos no requieren inventar respuestas externas. Cada integración espera únicamente sus entregas E-* indicadas; no espera la finalización global de T003.

- [X] T005 DOC Fijar en specs/001-terreno-cazador/quickstart.md nombres de suites y utilidades propuestos en esta lista, presupuesto de fixtures y autorizaciones GA; enumerar qué dobles requerirían permiso. No introducir un servidor o comportamiento nuevo de B/C/D. Dep: ninguna. [NFR-004, NFR-005, NFR-006; T1–T7, P1–P3]
- [X] T006 PRUEBA Crear en tests/datos_terreno_cazador.py constructores sintéticos de arreglos y descriptores de grafos válidos, con IDs dispersos, semillas explícitas y puertas/variaciones declaradas; reutilizar contratos existentes sin simular componentes ausentes. GA liberada únicamente para estos fixtures; no se necesitaron mocks. Dep: T005. [FR-001, FR-014; NFR-005; A1, A2, A7, P2]
- [X] T007 PRUEBA Escribir en tests/test_grafo_terreno.py pruebas de preparación de índice propio, adyacencias, traducción de IDs y lectura de costo/puerta; verificar «un índice por sala», «sin reserva por maxID» y valores válidos simétricos; no fijar conducta Q2. CONDICIONADA GB2 fuera del alcance sintético válido autorizado. Dep: T006. [FR-001, FR-008; NFR-002, NFR-005; A2, A5, P2]
- [X] T008 BASE Implementar en modelo/rutas.py índice denso, ordenamiento/búsqueda binaria propios y adyacencias: reservar/inicializar arreglos O(V) una vez, ordenar IDs O(V log V) y resolver E conexiones O(E log V); preparación total O(V log V+E log V), espacio O(V+E). Resolver vecinos antes de consultas, sin repetir preparación por decisión. Entrada: «costo ausente 100; declarado entero ≥1 y simétrico para datos válidos». CONDICIONADA GB2 fuera del alcance sintético válido autorizado; no validar ni normalizar en nombre de B. Dep: T007. [FR-001, FR-008; NFR-002, NFR-005; A2, A5, P2]
- [X] T009 PRUEBA Escribir en tests/test_heap_rutas.py pruebas de insertar/extraer/disminuir etiqueta, posición indexada y marcas de generación; verificar orden total y ausencia de reutilización de valores de una generación anterior. Dep: T006. [FR-010, FR-014; NFR-002, NFR-005; T4, A7, P2]
- [X] T010 BASE Implementar en modelo/rutas.py heap indexado y espacio de búsqueda con generación, distancias, primerID y posiciones; conservar «valor válido solo en generación vigente» y «sin limpiar V posiciones por consulta». No usar Evento ni contador semántico del motor. Dep: T008, T009. [FR-010, FR-014; NFR-002, NFR-005; T4, A7, P2]

**Checkpoint:** T007/T009 preceden al código correspondiente y verifican resultados sin bibliotecas prohibidas. La fase no exige dar por entregado el contrato completo de C/D para probar arreglos locales.

**Evidencia T005–T010:** orden T005 → fixtures T006 → pruebas T007 (fallo esperado por módulo ausente) → T008 (5 pruebas aprobadas) → T009 (fallo esperado por clases ausentes) → T010. Ejecución final limitada: 13 pruebas aprobadas en 0.013 s con Python 3.12.14, comando y contrato interno en quickstart.md. Ningún resultado certifica T1–T7, integración o rendimiento del ciclo; referencias FR/escenarios indican fundamentos cubiertos, no aceptación completa de cada FR.

## Phase 3: User Story 1 — terreno y tiempo (P1, MVP)

**Objetivo:** costos variables de todos los actores manteniendo reglas temporales existentes. **Prueba independiente:** comprobar posiciones inmediatas, costos e intervalos sin cazadores.

**Etapa de pruebas T011/T012, 2026-11-05:** autorización posterior limitada a las dos suites y ampliación de tests/datos_terreno_cazador.py; dependencias T006/T010 satisfechas. Se reutiliza ServidorFalso existente junto a precarga/catálogo/motor reales; no hay mocks nuevos ni HTTP real. La ejecución final de las cuatro suites autorizadas produjo 32 pruebas: 22 aprobadas, 10 fallos de aserción por costos de movimiento aún fijos en 100, cero errores. T011 tiene 5 aprobadas/7 fallidas; T012 tiene 4 aprobadas/3 fallidas; fundamentos mantienen 13/13. Los diez fallos son requisitos pendientes de T013/T014, no regresiones observadas en las estructuras. La reprogramación aislada pasa; T7 integrado falla antes del cambio de velocidad porque la acción inicial queda en 100 y no 250. **T011 y T012 se conservan sin completar**, aunque sus pruebas están preparadas. T013–T015 no se ejecutan ni se autorizan por este resultado. Q1–Q3 y entregables externos permanecen pendientes. Evidencia y comando en quickstart.md.

**Corrección posterior de la auditoría de pruebas, 2026-11-05:** el registro anterior conserva la ejecución histórica, no certifica que sus escenarios temporales fueran adecuados. Se corrigieron el regreso sin consumir tiempo, los turnos enemigos anticipados y la confusión entre extracción de cola y acción semántica. Datos/costos/puertas/velocidades se preparan en el paquete sintético antes de crear el motor; no se teletransporta al jugador ni se reasigna la velocidad del enemigo activo. Se verifican copias y _puertas_iniciales sin probar restauración. Resultado vigente: 35 pruebas, 25 aprobadas/10 fallidas/0 errores: costos 6/13 aprobadas, velocidad 6/9 y fundamentos 13/13. La prueba de ataque único usa motor real, vida, azar y siguiente evento; la prueba de cola es independiente. T7 parcial se nombra como tal y sus snapshots unitarios no se presentan como secuencias completas. T011/T012 continúan sin completar y T013–T051 no se ejecutan. Detalles de fuentes, cronologías y evidencia actual en quickstart.md.

- [X] T011 [P] [US1] PRUEBA Crear tests/test_costos_terreno.py con A1/A2/T6 para jugador, errante y rastreador: costo ausente 100, costo 250 con velocidad 100, y costo 1 con velocidad 1000 desde t=20 produce próxima acción t=21. Incluir los demás costos inalterados. CONDICIONADA GB2. Dep: T006, T010. [FR-001, FR-002, FR-003, FR-004, FR-011]

**Consolidación de evidencia T011 en T017, 2026-11-06:** se cierra la tarea de pruebas para datos válidos expresamente autorizados, con T006/T010 completos y sus 14 casos actuales aprobados en la corrida conjunta. El condicionamiento GB2 se mantiene fuera de ese alcance: no se acredita validación/entrada real de B ni política de costos null/inconsistentes. No se cambian expectativas, pruebas ni producción para consolidar este resultado.
- [X] T012 [P] [US1] PRUEBA Crear tests/test_velocidad_terreno.py con T7: costo 250, velocidad 100, pendiente t=250; cambio en t=50 a 200 produce t=150 con nueva secuencia y sin duplicado; repetir ralentización y terminación del efecto. Dep: T006, T010. [FR-005, FR-006, FR-017; T7]

**Cierre de cobertura T012 autorizado, 2026-11-06:** se añaden tres cronologías integradas sin modificar pruebas previas, fixture ni producción. Solo se usa restaurar_velocidad existente para vencer un efecto temporal preparado coherentemente en t=0: base 200/temporal 100 produce pendiente 250 → cambio t=50 → turno 150; base 50/temporal 100 produce 250 → 450; base 100/temporal 200 produce 125 → 200. No hay reloj manual, evento nuevo ni acción del jugador antes de su turno. Cada caso comprueba cancelación/nueva secuencia, una única llegada de turno, ataque ordinario con un daño/una tirada de azar y continuación legal más allá del tiempo cancelado sin otra decisión ni daño al objetivo. Suite velocidad 12/12; cuatro suites 38/38 y regresiones 53/53, cero fallos/errores. T7 queda acreditado para el jugador en estas cronologías de datos válidos; el ejemplo histórico encadenado 250→150→225 sigue parcial, no se inventa un evento de inicio de efecto para hacerlo integral. Preparación del efecto inicial no prueba adquisición/uso de poción ni efectos superpuestos. Esto completa T012 en su alcance de pruebas, sin cerrar Q1–Q3, E-B-COSTOS, T013/T014 o T015 ni ejecutar T016. Detalle y límites en quickstart.md; prompt P27.

**Etapa T013 autorizada, 2026-11-05:** la solicitud posterior autoriza exclusivamente el movimiento del jugador con entradas válidas, usando las pruebas T011/T012 ya preparadas; no exige completar antes los casos de enemigos de T011, que requieren T014. En mover se lee salida.get("costo", 100) antes de cambiar posición y se pasa a _avanzar_actor, sin alterar fórmulas, activación ni movimiento enemigo. Resultado: costos 9/13, velocidad 9/9 y fundamentos 13/13; quedan cuatro fallos de errantes/rastreadores de T014. Las 53 regresiones seleccionadas pasan antes y después. **Implementación local de T013 verificada para datos válidos; su casilla permanece pendiente de cierre de entrada integrada E-B-COSTOS**, cuya entrega no se acredita aquí. T011 continúa pendiente por enemigos; T012 tiene ahora su suite verde, sin declarar aceptación completa de T7 a partir de snapshots parciales ni ejecutar/cerrar T015. Las notas previas son históricas; esta autorización no resuelve GB2/Q2, Q1, Q3 ni contratos externos. Evidencia reproducible en quickstart.md. Ninguna tarea posterior se ejecuta ni se marca completa.

- [ ] T013 [US1] BASE Integrar en modelo/juego.py, solo en mover, el costo real del arco antes de cambiar posición y programar con max(1,costo*100//velocidad), preservando carga del contenido, deltas y activación. CONDICIONADA GB2; BLOQUEADA E-B-COSTOS para entrada integrada; no requiere E-B-RANGO. Dep: T011. [FR-001, FR-002, FR-003, FR-016; A1, A2, T6]
- [ ] T014 [US1] BASE Integrar en modelo/juego.py, rama mover de _ejecutar_turno_enemigo, el costo del arco; conservar decisiones de C y costo 100 de la primera activación; no tocar enemigos.py. CONDICIONADA GB2; BLOQUEADA E-B-COSTOS para costos de actores existentes; no requiere E-B-RANGO, el contrato nuevo de rutas filtradas de C ni acuerdos de D. Dep: T013. [FR-002, FR-003, FR-011, FR-016; A1, A9, A13]

**Evidencia posterior de T014, 2026-11-06:** autorización específica del usuario para datos válidos, con T013 local verificada. En la rama mover de _ejecutar_turno_enemigo se obtiene salida/costo de la sala de origen antes de cambiar posición y se entrega a _avanzar_actor. No cambian decidir_accion, ataques, esperas, activación inicial ni fórmulas. Las cuatro suites existentes pasan 35/35: costos 13/13, velocidad 9/9, fundamentos 13/13; desaparecen los cuatro fallos de errantes/rastreadores sin editar pruebas/fixtures. Las mismas 53 regresiones seleccionadas pasan 53/53. La prueba del fixture con costo 250 y enemigo de velocidad 500 conserva activación en t=20 (costo inicial 100), y los casos de costo 250 verifican turno inicial t=100 a velocidad 100. T014 está implementada/verificada para datos válidos; la casilla permanece pendiente de cierre integrado E-B-COSTOS, sin acreditar esa entrega ni resolver Q2. No se modifican casillas de T011/T012/T013 ni se ejecutan T015 o tareas posteriores. T7 integral, Q1–Q3 y contratos externos siguen pendientes. Comandos/resultados y límites en quickstart.md.

- [ ] T015 [US1] BASE Verificar y ajustar solo si falla T012 la integración de cambiar_velocidad en modelo/juego.py; conservar literalmente restante=max(1,(tiempo_siguiente-t)*velocidad_anterior//velocidad_nueva), cancelación anterior y nueva secuencia, sin cambiar efectos de otros integrantes. Dep: T012, T014. [FR-005, FR-006, FR-017; T7]

**Verificación limitada de T015, 2026-11-06:** se revisó íntegramente el diff T013/T014 (cuatro hunks, tres líneas eliminadas/seis agregadas), incluida cada sustitución: solo captura y uso del costo real en ambos movimientos, sin eliminar reglas heredadas. No se encontró defecto en cambiar_velocidad/_avanzar_actor ni se modificó producción o pruebas. La suite test_velocidad_terreno pasa 9/9 (aceleración 150, ralentización 450, mínimo 1, fin de efecto 225, cancelación y secuencia nueva); las 53 regresiones seleccionadas pasan 53/53. La prueba semántica acredita un solo ataque mediante vida/azar/agenda en su escenario separado; los snapshots de movimiento costoso siguen siendo parciales, no acreditan T7 integral. T015 se considera verificada dentro del alcance probado, sin ajuste necesario; su casilla conserva pendiente el cierre de sus prerrequisitos T012/T014 y la cobertura integral declarada, sin convertir la comprobación local en cierre global. No se ejecuta T016 ni tareas posteriores. Q1–Q3 y entregas externas no cambian. Diff completo, comandos, resultados y cobertura faltante en quickstart.md; prompt P26 en registro local.

- [ ] T016 [US1] PRUEBA Añadir a tests/test_costos_terreno.py comprobaciones de ataque/espera=100, usar/equipar/abrir=50, recoger/soltar=25 y posición inmediata sin ataques gratuitos; ejecutar tras T015 y registrar fallos reales. Dep: T014, T015. [FR-003, FR-004, FR-011; A1, A2, T6]

**Verificación autorizada de T016, 2026-11-06:** los siete costos, posición inmediata y costos de movimiento ya tienen pruebas; se reutilizan sin duplicarlos. Se añade únicamente test_movimiento_sin_ataques_gratuitos_respeta_agenda_y_empates, con subcasos de costo 250 y 100: verifica vida/azar intactos al moverse, espera del guardián de origen sin ataque gratuito, ataques del destino solo en turnos programados, orden tiempo/secuencia y empate con jugador. El avance usa ejecutar_ciclo y una espera legal al recuperar decisión; no se escribe reloj ni agenda para forzar orden. No cambia fixture ni producción. Resultado: costos 14/14, velocidad 12/12, fundamentos 13/13 (39/39), regresiones seleccionadas 53/53, cero fallos/errores. T016 queda verificada dentro del alcance probado, con casilla pendiente por cierre formal de sus prerrequisitos T014/T015, no por fallos de esta suite. No se completa ni ejecuta T017/T018 ni se acredita E-B-COSTOS o respuesta Q1–Q3. Comandos, cobertura existente/nueva y pendientes US1 en quickstart.md; prompt P28.

- [ ] T017 [US1] PRUEBA Ejecutar tests/test_costos_terreno.py y tests/test_velocidad_terreno.py junto con tests/test_juego.py y tests/test_enemigos.py; registrar comando, resultado y límites en specs/001-terreno-cazador/quickstart.md sin marcar resultados históricos como actuales. Dep: T016. [FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-011, FR-016; NFR-006; A1, A2, A9, T6, T7]

**Evidencia T017, 2026-11-06:** corrida única de costos/velocidad/grafo/heap/juego/enemigos/regresiones y precarga fallida seleccionada: 99/99 aprobadas (39 propias + 53 regresiones previas + 7 enemigos), cero fallos/errores/skips/expected failures. Se revisan el diff completo seguido de Python (solo seis líneas agregadas/tres sustituidas en mover y _ejecutar_turno_enemigo) y las pruebas nuevas, sin detectar un defecto que requiera corrección. rutas.py sin seguimiento pertenece a fundamentos T005–T010 anteriores, no es un cambio nuevo de T017 ni otra integración de movimiento. US1 funcionalmente verificada localmente para los escenarios válidos ejecutados; T6 cubre los tres actores existentes y T7 las cronologías integradas de jugador y límites previos. T011 puede cerrarse y se consolida aquí; T012 ya cerrada. T013/T014 conservan E-B-COSTOS pendiente, y T015/T016/T017 conservan cierre formal pendiente por la cadena de prerrequisitos, aunque sus comprobaciones locales están cumplidas. La casilla T017 no niega la ejecución real ni indica una falla de la suite. T018 no se ejecuta; Q1–Q3 y contratos externos siguen abiertos. Matriz de cobertura, comando y limitaciones en quickstart.md; prompt P29.
- [ ] T018 [US1] DOC Cuando llegue evidencia T001/T002, añadir a specs/001-terreno-cazador/quickstart.md los casos de entrada autorizados que A debe consumir y los errores cuya prueba corresponde a B; no escribir política de rechazo/normalización en modelo/juego.py por defecto. BLOQUEADA GB1/GB2. Dep: T001, T002, T017. [FR-001, FR-009; NFR-006; A1, A2, A4]

**Checkpoint:** MVP de movimiento con datos válidos verificable al completar T017; T018 puede seguir pendiente y mantiene explícita la falta de contrato de entrada completo.

## Phase 4: User Story 2 — persecución óptima (P1)

**Objetivo:** decisión individual del cazador, primer paso óptimo y rango. **Prueba independiente:** grafos sintéticos, cazador activo y jugador, sin niebla/viaje/historia.

- [X] T019 [P] [US2] PRUEBA Crear tests/test_rutas_cazador.py con T1–T4 y A4; incluir caminos de 2 arcos/500 frente a 3/300, empate vecinos 7/3 en orden inverso, convergencias, ciclos positivos y distancia igual al rango. Datos válidos explícitos, sin inventar Q1. CONDICIONADA GB1/GB2. Dep: T006, T010. [FR-008, FR-009, FR-010; NFR-005]

**Preparación autorizada de T019, 2026-11-06:** T006/T010 satisfechas; se crea exclusivamente tests/test_rutas_cazador.py usando crear_salas y las estructuras reales de rutas.py. Diez métodos/once casos incluyendo enumeración invertida, solo costos positivos/simétricos y límites enteros explícitos. Contrato interno propuesto de prueba: buscar_ruta(grafo, espacio, frontera, origen_indice, destino_indice, limite) devuelve (primer_indice, direccion, costo_paso, costo_total) o None si no encuentra ruta dentro del límite; no es contrato aprobado de C ni política de entrada null. Ejecución real: diez pruebas, once errores AttributeError por buscar_ruta ausente, cero fallos de aserción/skips/expectedFailure; no llegan a comprobar resultados de rutas. T019 preparada para TDD pero casilla pendiente de verificación satisfactoria tras T021. Las 99 pruebas existentes pasan de nuevo. No hay bloqueo externo para estos grafos válidos; Q1–Q3 y entregas E-* permanecen abiertas para políticas/integración/medición. T020 (decisión) no se prepara en este alcance; siguiente tarea de algoritmo T021, todavía sin ejecutar ni autorizar. Evidencia y diseño interno en quickstart.md; prompt P30.

- [X] T020 [P] [US2] PRUEBA Crear tests/test_decision_cazador.py con A3/A5: compartir sala produce ataque primero, fuera de ruta/rango espera 100 y la consulta no modifica posición, azar ni agenda; no descargar contenido para decidir. CONDICIONADA GB1/GB2; doble externo solo con permiso. Dep: T006, T010. [FR-007, FR-009, FR-012, FR-014; NFR-004]

**Preparación autorizada de T020, 2026-11-06:** T006/T010 completas; se crea exclusivamente tests/test_decision_cazador.py con nueve métodos/diez casos y rangos positivos explícitos. Firma interna propuesta para T022: decidir_cazador(origen_indice, destino_indice, rango, consultar_ruta) → (accion, direccion_o_None, costo_base). Sonda local registra llamadas y delega en buscar_ruta real para demostrar ataque sin búsqueda; no sustituye resultados ni simula servicios nuevos. Reutiliza motor_terreno y ServidorFalso existentes para preparar observación de estado y ausencia de descargas, sin modificar fixtures/componentes. Ejecución inicial: nueve métodos, diez errores ModuleNotFoundError por modelo.cazador ausente, sin aceptación comprobada de decisiones. Corrida de T019 y 99 pruebas previas: 109/109 aprobadas. T020 queda preparada para TDD pero pendiente de verificación; siguiente implementación T022, no autorizada ni ejecutada aquí. Q1–Q3 y contratos E-* permanecen pendientes. Detalles, límites A5 y comandos en quickstart.md; prompt P32.

- [X] T021 [US2] BASE Implementar en modelo/rutas.py Dijkstra individual limitado, etiquetas (distancia,primerID), prioridad total estable y poda al superar rango; propagar primerID y cerrar objetivo solo con etiqueta definitiva. Retornar primer paso/costo sin copiar caminos completos. CONDICIONADA GB1/GB2. Dep: T019, T010. [FR-008, FR-009, FR-010, FR-014; NFR-002; T1–T4, A4]

**Evidencia de T021 y cierre T019, 2026-11-06:** autorización específica para buscar_ruta con la firma interna de T019, sin cambiar esa suite. Se implementa solo rutas.py: Dijkstra con heap/generaciones existentes, puertas reales consultadas por arco, poda de costo > límite, cierre definitivo y preferencia lexicográfica por primerID. finally vacía solo frontera pendiente. Diez métodos/once casos de T019 aprobados, junto a 13 pruebas de estructuras (23/23); segunda ejecución de las 99 pruebas previas, 99/99. Control complementario de tres consultas consecutivas reutiliza arreglos/frontera y produce resultados previstos, sin cambiar objetos ni dejar pendientes. T019/T021 se completan para los escenarios válidos de núcleo autorizados; no se acreditan políticas GB1/GB2 ni contratos externos, equivalencia generativa T026, localidad medida T039 o presupuesto Q3. Precondición interna: origen y destino distintos, grafo/auxiliares coherentes y límite explícito; llegada compartida sigue reservada a T023/T024. T020/T022 y tareas posteriores no se ejecutan. Detalles/comandos/límites en quickstart.md; prompt P31.
- [X] T022 [US2] BASE Implementar en modelo/cazador.py decisión atacar/esperar/paso con rango válido suministrado; «atacar primero si coincide con jugador» y «mínimo/default/invalidez de rango pendientes Q1». No mover ni programar desde la búsqueda. CONDICIONADA GB1. Dep: T020, T021. [FR-007, FR-008, FR-009, FR-012; A3, A4, A5, T1, T2]
- [ ] T023 [US2] PRUEBA Añadir en tests/test_contrato_rutas_c.py las condiciones propuestas LLEGADA/RUTA_VALIDA/SIN_RUTA/SIN_RUTA_DENTRO_LIMITE y evidencia necesaria para FUERA_LIMITE; probar SIN_LIMITE en fuente filtrada de prueba aprobada. BLOQUEADA E-C-RUTA y permiso de dobles; sin exigir FUERA_LIMITE a la base sin certificado. Dep: T006, T021. [FR-008, FR-009, FR-010, FR-012; NFR-004; A4, A5; contrato A–C]
- [ ] T024 [US2] BASE Adaptar en modelo/rutas.py el contrato aprobado de modo y resultado: «SIN_LIMITE no elimina el filtro de conocimiento», «una búsqueda acotada no inventa existencia ni distancia fuera del rango» y llegada sin movimiento; no implementar conocimiento ni viaje de C. BLOQUEADA E-C-RUTA. Dep: T023. [FR-008, FR-009, FR-010, FR-012; NFR-004; A4, A5; contrato A–C]
- [ ] T025 [US2] BASE Conectar modelo/cazador.py desde el despacho de A en modelo/juego.py, conservando firma/decisiones existentes de C y ejecutando el paso mediante motor ordinario con costo real. Rango debe llegar por acceso ya acordado, sin modificar tipos.py ni hacer HTTP. BLOQUEADA E-B-COSTOS/E-B-RANGO/E-C-DESPACHO; CONDICIONADA GB1/GB2. Dep: T014, T022. La integración del cazador necesita costos y rango; no espera T024 ni el contrato de viaje de C. [FR-002, FR-007, FR-008, FR-009, FR-011, FR-012; T1–T4, A3–A5]
- [ ] T026 [US2] PRUEBA Ampliar tests/test_rutas_cazador.py con referencia independiente de selección lineal o caminos simples en mapas pequeños sobre arreglos propios; contrastar distancia/primerID ante muchas rutas empatadas y distinta enumeración. Dep: T021. [FR-008, FR-009, FR-010, FR-014; NFR-005; T3, T4, A7]
- [ ] T027 [US2] PRUEBA Ejecutar tests/test_rutas_cazador.py, tests/test_decision_cazador.py y tests/test_contrato_rutas_c.py para resultados y ausencia de efectos secundarios; registrar en specs/001-terreno-cazador/quickstart.md evidencia y bloqueos. Tras autorización de pruebas y prerrequisitos del subconjunto, puede ejecutarse parcialmente el núcleo del cazador sin esperar E-C-RUTA, identificando suites omitidas y motivo. Ese resultado parcial NO completa T027 ni libera cierres que la requieren. La finalización total exige T024, T025 y T026 y evidencia satisfactoria de las tres suites, con E-C-RUTA y permisos de dobles liberados donde correspondan. Dep: T024, T025, T026. [FR-007, FR-008, FR-009, FR-010, FR-012, FR-014; NFR-004, NFR-006; T1–T4, A3–A5]
- [ ] T028 [US2] DOC Registrar en specs/001-terreno-cazador/research.md invariantes y límites de la búsqueda individual y evidencia de T026/T027; distinguir prueba de corrección de medición de tiempo y conservar Q1/Q2 pendientes si falta fuente. Dep: T027. [FR-010, FR-014; NFR-002, NFR-006; T4, A7, P2]

## Phase 5: User Story 3 — validez, eventos y reversibilidad (P1)

**Objetivo:** decisión equivalente a recálculo en estado actual. **Prueba independiente:** cambiar puertas/objetivo/eventos entre decisiones y comparar contra referencia sin reutilización.

- [ ] T029 [P] [US3] PRUEBA Crear tests/test_validez_rutas.py con T5/A6: cerrar puerta del camino, abrir otra que mejora o empata con primerID menor y mover objetivo; verificar también el extremo opuesto y no inventar coherencia aún no acordada. BLOQUEADA E-BC-PUERTA. Dep: T026. [FR-008, FR-010, FR-013, FR-015]
- [ ] T030 [P] [US3] PRUEBA Crear tests/test_eventos_terreno.py con A7–A11: eventos simultáneos por secuencia, activación por ID/costo100, muerte, veneno cancelado, regeneración/curación limitadas, trampa y cierre tras cruce. Dep: T017, T025. [FR-006, FR-014, FR-015, FR-016, FR-017]
- [ ] T031 [US3] BASE Implementar en modelo/rutas.py contexto derivado de validez con identidad/época y objetivo, separación de fuente real/recordada y descarte seguro tras restauración; no almacenar cache ilimitado ni introducir estrategia compartida. Dep: T029, T021. El contexto real de A no espera el modo filtrado de C; si se integra esa fuente, requiere E-C-RUTA y T024 sin liberar otros contratos. [FR-012, FR-013, FR-018; NFR-002, NFR-005; T5, A5, A6, A12]
- [ ] T032 [US3] BASE Conectar en modelo/juego.py y modelo/efectos.py cambios efectivos de puertas al contexto de A, registrando deltas antes de mutar conforme al acuerdo y preservando observaciones de C; no modificar historial.py ni estructuras de B/C. BLOQUEADA E-BC-PUERTA/E-C-OBS/E-C-UNDO. Dep: T029, T030, T031. [FR-013, FR-015, FR-018; T5, A6, A8, A10, A12]
- [ ] T033 [US3] PRUEBA Ampliar tests/test_validez_rutas.py para demostrar que velocidad cambia programación pero no distancias por sí sola, movimientos/muertes no inventan bloqueo por ocupación y cambios indirectos sí producen decisiones actuales. Dep: T032, T015. [FR-005, FR-013, FR-017; T5, T7, A6, A11]
- [ ] T034 [US3] PRUEBA Escribir en tests/test_restauracion_rutas.py A12: undo/carga/rollback preservan reloj, eventos, identidad/en_cola, contador y azar; excluyen pergaminos y caché de infraestructura, y no reutilizan una época antigua. BLOQUEADA E-C-UNDO/E-D-RESTAURA; no implementar restauración ajena. Dep: T032. [FR-006, FR-014, FR-018; A12]
- [ ] T035 [US3] BASE Instrumentar solo cambios del motor de A en modelo/juego.py según sobre aprobado por D y registrar deltas de A con el historial existente; descartar derivados de rutas al restaurar, sin convertir callbacks de C en persistencia ni editar snapshots.py. BLOQUEADA E-C-UNDO/E-D-CAMBIOS. Dep: T034. [FR-014, FR-018; A12; contrato A–D]
- [ ] T036 [US3] BASE Verificar y ajustar únicamente defectos de A detectados en modelo/eventos.py, modelo/juego.py y modelo/efectos.py conservando tiempo/secuencia, nueva secuencia en reprogramación, cancelación, identidad/en_cola/contador y efectos heredados; si no fallan pruebas, no refactorizar. Dep: T030, T033, T035. [FR-005, FR-006, FR-015, FR-016, FR-017, FR-018; T7, A7–A12]
- [ ] T037 [US3] PRUEBA Ejecutar tests/test_eventos_terreno.py, tests/test_validez_rutas.py, tests/test_restauracion_rutas.py y regresiones de quickstart.md; agregar A13 en tests/test_costos_terreno.py para rastro por acción, frescura <400, desempate y guardián; reportar fallos ajenos sin corregirlos. Dep: T036. [FR-006, FR-011, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018, FR-019; NFR-006; T5, T7, A7–A13]
- [ ] T038 [US3] DOC Registrar en specs/001-terreno-cazador/research.md matriz evento→distancias/programación, demostración de invalidación conservadora y resultados reales de T029–T037, separando infraestructura y estado semántico. Dep: T037. [FR-013, FR-014, FR-018; NFR-003, NFR-006; T5, A6–A12]

## Phase 6: User Story 4 — fluidez y evaluación comparativa (P2)

**Objetivo:** medir sin afirmar resultados no obtenidos. **Prueba independiente:** mismas cargas/semillas/acciones, decisiones contra referencia y medición del ciclo completo. Las comparaciones son obligatorias donde el enunciado lo exige; adoptar sus alternativas en producción no lo es.

- [ ] T039 [US4] PRUEBA Crear tests/test_localidad_rutas.py con región local fija y mapa exterior creciente, contabilizando expansión, asignaciones y limpieza por consulta; verificar igualdad de decisiones y ausencia de barridos V al rango pequeño. Dep: T021, T026. [FR-008, FR-010; NFR-002, NFR-005; P2]
- [ ] T040 [US4] EVAL Preparar utilidades/bench_terreno_cazador.py con cargas sintéticas deterministas uno/muchos cazadores, rangos pequeños/grandes y puertas estables/inestables; registrar equipo, semilla, V/E/H, repeticiones, memoria y tiempo separadamente, incluyendo mantenimiento. BLOQUEADA GA para nueva utilidad; solo datos válidos, no referencia oficial. Dep: T037, T039. [FR-014; NFR-001, NFR-002, NFR-003; P1–P3]
- [ ] T041 [US4] EVAL Añadir en utilidades/bench_terreno_cazador.py alternativa individual de heap con obsoletos y referencia lineal frente al heap indexado; usar estructuras propias, incluir construcción/limpieza y validar con T026 antes de medir. No reemplazar la base automáticamente. Dep: T040. [FR-008, FR-010; NFR-002, NFR-003, NFR-005; T3, T4, P2, P3]
- [ ] T042 [US4] EVAL Comparar en utilidades/bench_terreno_cazador.py cálculo individual y campo inverso compartido sobre arcos entrantes preparados; comprobar decisiones y contabilizar preparación/hits/fallos/reconstrucción, señalando incumplimientos de localidad. Sin activación en producción ni umbral por H/rango inventado. Dep: T041. [FR-008, FR-009, FR-010, FR-013; NFR-002, NFR-003; T1–T5, P2, P3]
- [ ] T043 [US4] EVAL Comparar en utilidades/bench_terreno_cazador.py recálculo siempre, última consulta y varias entradas propias acotadas con capacidad declarada; mismas consultas repetidas/alternadas y puertas estables/inestables; medir aciertos, fallos por reemplazo/invalidez, memoria y costo de claves/inserción/reemplazo/liberación/invalidez. No concluir contra toda reutilización por una sola caché ni activar alternativas en producción. Dep: T042. [FR-013; NFR-002, NFR-003, NFR-005; T5, A6, P3]
- [ ] T044 [US4] EVAL Medir en utilidades/bench_terreno_cazador.py agenda actual con obsoletos y candidato indexado aislado, conservando orden/identidad de eventos; repetir cargas P1 con cazadores y cambios de velocidad, contar N físico/válido y costo de extracción tras cancelaciones. No reemplazar modelo/eventos.py sin evidencia/revisión. Dep: T043, T036. [FR-005, FR-006, FR-016, FR-017; NFR-003; T7, A7–A11, P3]
- [ ] T045 [US4] DOC Entregar en specs/001-terreno-cazador/contracts/integracion.md a D la función de medición de A y resultados reproducibles de utilidades/bench_terreno_cazador.py para conexión por D en bench.py; registrar entrega/pendiente, no editar bench.py, main.py ni CLI de D. BLOQUEADA E-D-MEDICION para acuerdo y conexión recibida de D; registrar una solicitud de entrega no completa la tarea. Dep: T044. [NFR-001, NFR-003, NFR-004, NFR-006; P1, P3; contrato A–D]
- [ ] T046 [US4] PRUEBA Medir el ciclo completo con la referencia Q3 cargada y decenas de cazadores mediante utilidades/bench_terreno_cazador.py y conexión entregada por D; registrar en specs/001-terreno-cazador/research.md mínimo/mediana/máximo y cumplimiento o incumplimiento de <20 ms sin red/renderizado. BLOQUEADA GR/E-D-MEDICION, no sustituir cripta oficial por sintética. Dep: T004, T045. [NFR-001, NFR-003, NFR-004; P1]

## Phase 7: Polish y cierre documental

**Objetivo:** trazabilidad y decisiones respaldadas. No se autoriza escribir archivos compartidos por enumerarlos aquí.

- [ ] T047 DOC Cerrar en specs/001-terreno-cazador/research.md las decisiones de A con problema, alternativas, complejidad, evidencia real, límites y desviaciones justificadas. Se permiten borradores parciales con G-DOC, pero checkbox pendiente hasta T001/T002/T003/T004/T028/T038/T046 finalizados y evidencia comprobable de todas las mediciones requeridas; no basta anotar resultados pendientes ni presumir cumplimiento de <20 ms. Dep: T001, T002, T003, T004, T028, T038, T046. [NFR-001, NFR-002, NFR-003, NFR-005, NFR-006; P1–P3]
- [ ] T048 DOC Cerrar en specs/001-terreno-cazador/quickstart.md comandos reales, requisitos externos y resultados reproducibles de suites e integración/medición oficial; separar experimentos de producción. Checkbox pendiente hasta todos sus prerrequisitos y evidencia real, incluidos T046 y contratos usados; un borrador o una referencia Q3 pendiente no es finalización. Dep: T017, T027, T037, T045, T046. [NFR-003, NFR-004, NFR-006; T1–T7, A1–A13, P1–P3]
- [ ] T049 DOC Cerrar en specs/001-terreno-cazador/tasks.md trazabilidad con prueba/log real, comando/fecha/resultado y estado por FR/NFR/escenario. Completar solo después de T047/T048 finales, sin medir cobertura por mera referencia a una tarea ni marcar una implementación sin evidencia; no exige publicar ni hacer Git. Dep: T047, T048. [NFR-006; T1–T7, A1–A13, P1–P3]
- [ ] T050 DOC Cerrar en specs/001-terreno-cazador/research.md un paquete local de A listo para traslado autorizado a DECISIONES.md y README.md, con fuentes, evidencia completa, límites y enlaces definitivos. Checkbox solo tras T047/T048/T049 finales y revisión de completitud; preparación provisional queda pendiente. Completar este paquete no significa haber actualizado/publicado los archivos compartidos, que siguen requiriendo autorización separada. Dep: T047, T048, T049. [NFR-001, NFR-003, NFR-006; P1–P3]
- [ ] T051 DOC Mantener desde ahora, con G-DOC y sin esperar Implement ni T049, specs/001-terreno-cazador/prompts-registro-local.md como índice/archivo textual verificable de solicitudes, respuestas de Clarify y correcciones; preservar textos, fecha contextual o falta de timestamp, herramienta y finalidad. Completar la consolidación solo tras comprobar todas las fuentes disponibles y declarar expresamente cualquier vacío; un vacío declarado sigue siendo pendiente de recuperación, no prompt inventado. Traslado a PROMPTS_LLM.md requiere autorización separada. Dep: ninguna. [NFR-006; trazabilidad transversal de T1–T7, A1–A13, P1–P3]

## Dependencies & Execution Order

G-DOC rige modificaciones documentales expresamente autorizadas; G0 y GA rigen código y ejecución de pruebas/benchmarks. Una tarea DOC que solicita resultados de pruebas espera esa evidencia: no puede generarla ejecutando código bajo G-DOC. Relaciones «Dep» son prerrequisitos de finalización; los gates externos son adicionales y nunca se satisfacen por ejecutar otra tarea de A.

```text
T005 → T006 → T007 → T008 ┐
           └→ T009 ──────┴→ T010
T010 → US1 (T011–T017) → integración temporal disponible
T010 → US2 núcleo (T019–T022, T026)
E-B-COSTOS + US1 → T013/T014; E-B-RANGO no bloquea esos movimientos
E-C-RUTA + núcleo → T023/T024; E-B-COSTOS/E-B-RANGO/E-C-DESPACHO + US1/núcleo → T025; T024/T025/T026 → cierre completo T027 → T028
US1 + cazador + entregas específicas E-* indicadas en cada tarea → US3 (T029–T038)
US2 núcleo → T039; US3 + T039 → US4 sintético (T040–T045)
T004 + T045 + GR/E-D-MEDICION → T046 (certificación oficial)
evidencia final completa → T047/T048 → T049 → T050; T051 se mantiene desde documentación sin esperar esa cadena
```

- Ningún consumidor depende de completar T003 globalmente: usa únicamente los E-* listados en su descripción. T003 completo solo es prerrequisito del cierre final T047.
- T001/T002 son esperas de evidencia, no instrucciones para que A cree la validación de B. T018 las consume. El núcleo puede diseñarse/probarse con datos válidos tras autorización específica sin cerrar Q1/Q2; integraciones esperan las entregas reales.
- US1 es el MVP. US2 núcleo se prueba sin US1, pero su conexión al motor depende de US1. US3 depende de ambos; no declarar todas las historias independientes ni asignarlas a B/C/D para acelerar.
- Los experimentos no son camino de ejecución de producción. Una adopción posterior requiere revisar plan y, si cambia reglas, spec antes del código; no tarea de integración implícita.
- Ninguna tarea obliga a A a editar red/, tipos.py, enemigos.py, historial.py, snapshots.py, main.py, bench.py, vista/ ni persistencia. Si su entrega falta, se registra el bloqueo y se coordina, sin sustitución unilateral.

## Parallel Examples

- **Foundational:** T007 en tests/test_grafo_terreno.py y T009 en tests/test_heap_rutas.py pueden prepararse tras T006; T008/T010 comparten modelo/rutas.py y se ejecutan secuencialmente.
- **US1:** T011 y T012 tienen igual prerrequisito y archivos diferentes; son la pareja marcada [P]. No paralelizar T013–T015 porque comparten modelo/juego.py.
- **US2:** T019 y T020 pueden prepararse después de T010. T021 modifica modelo/rutas.py y T022 depende de él; no son paralelos.
- **US3:** T029 y T030 pueden prepararse cuando se cumpla la unión de sus prerrequisitos y gates; archivos diferentes. T032/T035/T036 se serializan para proteger el motor.
- **US4:** T040–T044 comparten la utilidad y dependen unos de otros; no hay pareja [P] interna segura. Tras T045 puede prepararse un borrador de T048 con G-DOC, pero su checkbox exige T046 y las demás evidencias finales; no ejecutar pruebas y benchmarks simultáneamente si altera mediciones.

## Implementation Strategy

1. Mantener documentación solo bajo G-DOC. Antes de autorizar código/pruebas, revisar esta lista corregida mediante Analyze expresamente autorizado; el Analyze anterior no aprueba automáticamente estas correcciones. No ejecutar Implement mientras G0 no se libere.
2. Tras permisos y entregas pertinentes, construir soporte mínimo; entregar US1 con T6/T7 y regresiones como MVP.
3. Entregar búsqueda/cazador individual sobre datos válidos; después conectar motor conforme a acuerdos. Evitar añadir niebla/viaje/historia de compañeros.
4. Probar invalidación/eventos/restauración antes de usar reutilización para ahorrar trabajo.
5. Evaluar alternativas separadas y registrar evidencia; producción conserva la base aprobada hasta nueva revisión. Q3 bloquea solo afirmación oficial de rendimiento, no resultados sintéticos identificados como tales.
6. Documentar sin resultados fabricados. No ejecutar Git por instrucciones de plantilla; commits/publicación requieren autorización independiente.

## Matriz inicial de cobertura

Esta matriz indica tareas previstas, no cobertura ejecutada. SC-001–SC-006 se verifican mediante las pruebas/mediciones enlazadas.

| Requisito | Tareas principales | Escenarios |
| --- | --- | --- |
| FR-001 | T002, T007, T008, T011, T013, T018 | A1, A2, T6 |
| FR-002 | T011, T013, T014, T025 | A1, A2, T6, T3 |
| FR-003 | T011, T013, T014, T016 | A1, A2, T6 |
| FR-004 | T011, T016 | A2 |
| FR-005 | T012, T015, T033, T036 | T7 |
| FR-006 | T012, T015, T030, T034, T036 | T7, A7, A8, A12 |
| FR-007 | T001, T020, T022, T025 | A3, T1 |
| FR-008 | T008, T019, T021, T025, T026 | T1–T4, A4, A5 |
| FR-009 | T001, T019, T020, T021, T022 | T1, T2, T3, A4 |
| FR-010 | T009, T010, T019, T021, T026 | T4 |
| FR-011 | T011, T014, T016, T037 | A1, A13 |
| FR-012 | T020, T023, T024, T025, T031 | A5 |
| FR-013 | T029, T031, T032, T033, T038, T043 | T5, A6 |
| FR-014 | T006, T010, T026, T030, T034, T035 | A7, A8, A12 |
| FR-015 | T029, T030, T032, T036 | A8, A10 |
| FR-016 | T013, T014, T030, T036 | A9 |
| FR-017 | T015, T030, T033, T036 | T7, A11 |
| FR-018 | T031, T032, T034, T035, T038 | A12 |
| FR-019 | T003, T037 | A13 |
| FR-020 | AD-01–AD-03 (adenda, abajo) | A14–A18 |
| NFR-001 | T004, T040, T046, T047 | P1 |
| NFR-002 | T008, T010, T021, T039, T041–T043 | P2 |
| NFR-003 | T038, T040–T048 | P1–P3 |
| NFR-004 | T020, T023–T025, T045, T046 | A5, P1 |
| NFR-005 | T006–T010, T026, T039, T041–T043 | T4, A7, P2, P3 |
| NFR-006 | T001–T005, T017, T027, T028, T037, T038, T045, T047–T051 | Todos |

**Histórico:** la versión inicial reunía GBC/GC/GD en T003, aplicaba G0 a documentación y aceptaba cierres parciales T047–T050. Se conservan IDs, pero esas reglas fueron sustituidas el 2026-11-05 por entregables independientes, G-DOC y criterios de cierre con evidencia; no conservarlas como instrucciones activas.

**Segunda corrección documental, 2026-11-05:** el antiguo E-B-DATOS se sustituye por E-B-COSTOS y E-B-RANGO independientes; no es un gate activo. T027 incorpora T024 para cierre total. El reporte de B se conserva en research.md como comunicación, sin acreditar entregas ni cerrar Q1/Q2. Los datos sintéticos válidos del núcleo no requieren entregas integradas de B; conservan G0/GA y condiciones GB1/GB2. No se modifican los demás prerrequisitos ni se completa ninguna tarea.

**Balance:** 51 tareas: Setup 4, Foundational 6, US1 8, US2 10, US3 10, US4 8, Polish 5. Todas pendientes. Los gates y la evidencia son parte de su verificabilidad; las tareas bloqueadas no son ejecutables hasta liberarse sus condiciones.

**Balance vigente tras esta etapa:** 6 completadas (T005–T010), 45 pendientes. El balance anterior conserva el estado histórico antes de implementar; ningún checkbox adicional se modifica.

**Balance posterior al cierre de cobertura T7, 2026-11-06:** 7 completadas (T005–T010 y T012), 44 pendientes. Los balances anteriores son históricos. T015 conserva su verificación sin cambios, con cierre formal pendiente de T014; completar T012 no acredita E-B-COSTOS ni autoriza tareas posteriores.

**Balance posterior a verificación conjunta T017, 2026-11-06:** 8 completadas (T005–T012), 43 pendientes. Se consolida únicamente el cierre local de pruebas T011; T013–T017 tienen evidencia local satisfactoria pero sus casillas conservan condiciones de integración/prerrequisitos. No se completa T018 ni tareas de US2 y no se resuelven entregas externas.

**Balance posterior a T021, 2026-11-06:** 10 completadas (T005–T012, T019 y T021), 41 pendientes. No cambia el cierre condicionado de US1, Q1–Q3 ni entregas externas. Los balances anteriores son históricos; T020 y T022 permanecen pendientes.

## Adenda A–D — frontera temporal, fuera de US2

Estas actividades no renumeran T001–T051 ni cambian sus casillas. La autorización específica del 2026-11-06 permite AD-01, conservando los tres puntos pendientes del checklist. No libera producción ni acredita E-D-CAMBIOS.

- **AD-01 — Preparación autorizada:** especificar FR-020, A14–A18, y preparar `tests/test_frontera_temporal.py` con el motor real y fixture existente. Registrar resultados contra el motor anterior y el motivo de los fallos. No requiere Q1–Q3 ni datos integrados de B.
- [x] **AD-02 — Frontera del motor implementada localmente.** Con la enmienda confirmada en `26be407` y la autorización específica, el motor cierra el instante del turno del jugador dentro de la transacción existente. La extracción comprueba el límite antes de retirar cada raíz, incluso al descartar cancelados. Depende de AD-01. La implementación está pendiente de commit.
- [x] **AD-03 — Validación local de FR-020 completada.** Pasaron 11/11 pruebas de frontera, 99/99 regresiones y 10/10 pruebas de rutas. La corrida ampliada reprodujo cuatro incidencias de interfaz con el motor anterior. Los casos de red simulada y precarga que requerían `requests` pasaron en el entorno local del proyecto. Depende de AD-02. La aceptación de `historia` y su registro serializable quedan en el alcance de D y E-D-CAMBIOS. [Resultados de AD-03](quickstart.md#validación-local-ad-03).

**T016:** conservar movimiento inmediato, ausencia de ataques gratuitos, costos, activación y orden por secuencia. El subcaso costo 100 llama directamente a `ejecutar_ciclo()`; su aserción de que queda el enemigo de secuencia mayor tras extraer el turno del jugador sigue siendo válida para una extracción individual. Lo anterior es la interpretación de ese estado como decisión ya habilitada y procesar ese ataque recién al llamar a `ejecutar("esperar")`. No se modifican sus expectativas en AD-01: las nuevas pruebas ejercen `ejecutar()` desde la acción de movimiento y verifican que el daño se observe antes de devolver. En el caso de costo 250 no hay empate del jugador en la frontera; se conserva la cobertura previa.

**Evidencia histórica de AD-01, antes de implementar FR-020.** De las 11 pruebas nuevas, 7 pasaron y 4 reprodujeron la devolución anticipada. Las 99 regresiones existentes pasaron con las expectativas de entonces. [Comandos y resultados](quickstart.md#frontera-temporal-ad-01).

**Conciliación posterior a AD-02.** La primera corrida del motor nuevo dejó 95/99 regresiones aprobadas. Las cuatro restantes observaban la agenda, el daño o la regeneración antes de cerrar el instante. Las pruebas reconciliadas conservan las comprobaciones del intervalo de movimiento, daño, azar y retroceso. AD-03 verifica el alcance local de Persona A. T020 y T022 siguen pendientes, al igual que Q1–Q3 y E-D-CAMBIOS.
