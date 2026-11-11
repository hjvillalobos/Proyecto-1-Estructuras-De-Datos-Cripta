# Feature Specification: Terreno, cazador y validez de rutas

**Feature Branch**: `feature/motor-eventos`

**Feature ID**: `001-terreno-cazador` (independiente del nombre de rama)

**Created**: 2026-11-01

**Status al 2026-11-05**: Draft condicionado — Specify y primera ronda de Clarify documentados; Plan provisional y 51 tareas generados; dos revisiones Analyze realizadas. Se incorporan las correcciones documentales I1/I5/C2 de la segunda revisión. Q1–Q3 y contratos externos continúan pendientes. Esta actualización no autoriza código ni ejecución de pruebas, ni acredita una revisión posterior de estas últimas correcciones.

**Input**: Persona A solicita terreno ponderado, cazador y decisiones de ruta válidas, conservando las reglas de Parte I salvo cambios explícitos de Parte II. Texto íntegro de la solicitud: [registro pendiente](prompt-registro-pendiente.md).

**Adenda 2026-11-06.** FR-020 y A14–A18 documentan la decisión técnica de Persona A para compatibilidad con `historia <t>`, pendiente de validación de integración con Persona D. Esta etapa autoriza documentación y preparación de pruebas. La enmienda debe confirmarse en Git antes de modificar producción, conforme a la constitución IV. Q1–Q3 y los contratos externos siguen pendientes.

## Clarifications

### Session 2026-11-02

- Q: ¿Dispones de evidencia oficial o de un acuerdo documentado del equipo que precise los valores admitidos para rango y qué hacer si falta o es inválido? → A: Opción B: consultar al compañero B sobre el contrato oficial. Q1 permanece como dependencia externa pendiente de confirmación; no se define valor predeterminado, mínimo ni política para datos inválidos. Si B no dispone de una fuente suficiente, consultar al profesor.
- Q: ¿Dispones de una fuente oficial o acuerdo documentado que indique cómo tratar costos inválidos, diferentes entre sentidos o declarados solamente en un extremo? → A: Opción B: consultar al compañero B sobre el contrato oficial. Q2 permanece como dependencia externa pendiente de confirmación, igual que Q1. No se define una política de normalización o rechazo de costos inválidos, asimétricos o declarados en un solo sentido.
- Q: ¿Dispones de la identificación oficial de la cripta de referencia y de alguna enmienda del profesor al límite de procesamiento de 20 ms? → A: Opción B: no se dispone actualmente de esa evidencia. Q3 permanece como información externa pendiente de confirmación. Se conservan menos de 20 ms, ciclo completo entre decisiones del jugador, cripta de referencia cargada con decenas de cazadores, equipo local y exclusión de red y renderizado. No se inventa la cripta ni se afirma cumplimiento sin mediciones.

El usuario confirma que ya consultó a B sobre Q1 y Q2 y espera respuesta. Se han formulado y respondido tres preguntas sobre la disponibilidad de evidencia; ninguna de las tres dependencias externas se considera resuelta. Los acuerdos externos continúan pendientes. Los textos disponibles del chat y registros previos se reúnen en [registro local](prompts-registro-local.md), con fuentes y vacíos explícitos; PROMPTS_LLM.md no se modifica. Histórico: la primera ronda de Clarify quedó a la espera de evidencia, y luego el usuario autorizó Plan y Tasks provisionales, Analyze de lectura y correcciones documentales. Esas autorizaciones no equivalen a permiso de implementación ni resolución de Q1–Q3.

**Evidencia parcial reportada después del segundo Analyze, 2026-11-05:** el usuario comunica la revisión de B sobre OpenAPI 1.1.0: Enemy.rango opcional/null, entero ≥1 si tiene valor, sin default ni obligatoriedad adicional para cazador; Exit dirigido con costo opcional/null, entero ≥1 si tiene valor, sin default ni garantía de simetría. No hay copia verificable ni fragmentos originales; no es verificación independiente ni respuesta del profesor. El [registro y contraste](research.md#comunicación-reportada-de-b-sobre-openapi-110) mantiene Parte II §3.1 (costo ausente 100 e igual en ambos sentidos) y §3.2 (ficha del cazador con rango). Al 2026-11-05 seguía pendiente el tratamiento de rango ausente, null o inválido en Q1, así como el de costo null e inconsistencias en Q2. Q3 no cambió con ese reporte. Después, el profesor confirmó, según el usuario, que un rango `null` explícito significa rango ilimitado. El campo ausente y los valores inválidos siguen pendientes en Q1. No se altera ningún FR por este reporte.

## User Scenarios & Testing *(mandatory)*

Los códigos T1–T7 son etiquetas del reparto para los siete casos de terreno y cazador del Apéndice B de Parte II; no son identificadores oficiales. Los ejemplos numéricos siguientes son escenarios sintéticos de aceptación, no datos de una cripta publicada. Cada futura prueba citará los requisitos indicados. Los escenarios definen resultados esperados; todavía no se han ejecutado pruebas.

### User Story 1 - Mover actores por terreno con costos distintos (Priority: P1)

Como jugador, quiero que el terreno determine cuánto tarda cada actor en volver a actuar, conservando el avance de eventos y los efectos de velocidad.

**Why this priority**: Es la base temporal de todos los movimientos, incluidos los de enemigos existentes.

**Independent Test**: Con salidas de distintos costos y actores de velocidades conocidas, comprobar la posición inmediata, la próxima acción y el orden de eventos sin introducir cazadores.

**Acceptance Scenarios**:

1. **A1**, **Given** una salida sin costo declarado y velocidad 100, **When** el jugador, un errante o un rastreador la atraviesa, **Then** el costo es 100 y su siguiente acción ocurre 100 unidades después. Repetir con costo 250: el intervalo es 250. La decisión del enemigo existente no cambia. (FR-001–FR-004, FR-011)
2. **T6**, **Given** una salida de costo 1 y un actor de velocidad 1000, **When** se mueve en t=20, **Then** ocupa inmediatamente el destino y su siguiente acción queda en t=21. (FR-002–FR-003)
3. **T7**, **Given** un movimiento de costo 250 a velocidad 100 programado desde t=0 hasta t=250, **When** en t=50 la velocidad cambia a 200, **Then** la próxima acción se reprograma en t=150 con secuencia nueva y el evento sustituido no produce otra acción. Repetir con ralentización y con terminación del efecto usando la misma fórmula. (FR-005–FR-006)
4. **A2**, **Given** dos extremos de una conexión con costo válido idéntico y actores de igual velocidad, **When** la atraviesan en sentidos opuestos, **Then** pagan el mismo costo; atacar y esperar siguen costando 100, usar/equipar/abrir 50 y recoger/soltar 25. (FR-001–FR-004)

### User Story 2 - Ser perseguido por un cazador (Priority: P1)

Como jugador, quiero que un cazador persiga mi posición por la ruta abierta más barata que alcance su rango, con resultados previsibles en los empates.

**Why this priority**: Define el nuevo comportamiento evaluado de esta capacidad.

**Independent Test**: En un mapa sintético con puertas y costos conocidos, situar un cazador activo y al jugador y comprobar su siguiente decisión y tiempo, sin requerir niebla ni viaje automático.

**Acceptance Scenarios**:

1. **T1**, **Given** cazador y jugador en salas diferentes sin ruta abierta, **When** llega su turno, **Then** espera con costo 100 y permanece en su sala. (FR-007–FR-009)
2. **T2**, **Given** una ruta mínima de costo 101 y rango 100, **When** decide, **Then** espera con costo 100. (FR-008–FR-009)
3. **T3**, **Given** una ruta de dos salidas de costo total 500 y otra de tres de costo total 300, ambas abiertas y rango 300, **When** decide, **Then** avanza un paso por la ruta de costo 300 y paga únicamente el costo de ese paso. (FR-008–FR-009)
4. **T4**, **Given** dos primeras vecinas de IDs 7 y 3 que permiten el mismo costo total mínimo dentro del rango, **When** decide, **Then** escoge la sala 3, incluso si su salida se enumera después o existen muchas rutas empatadas. (FR-010, FR-014)
5. **A3**, **Given** un cazador en la misma sala que el jugador, **When** llega su turno, **Then** ataca según las reglas de combate heredadas y no busca desplazarse ni aplica el límite de rango para decidir atacar. (FR-007, FR-017)
6. **A4**, **Given** una ruta mínima de costo exactamente igual a rango, **When** decide, **Then** avanza; nunca abre una puerta cerrada para acortar la ruta. (FR-008–FR-010)
7. **A5**, **Given** iguales esqueleto, puertas reales y posiciones, pero diferentes salas exploradas o contenidos descargados, **When** decide el cazador, **Then** obtiene la misma decisión y tiempo de siguiente acción, sin solicitar contenido para buscar la ruta. (FR-008, FR-012, NFR-004)

### User Story 3 - Mantener decisiones correctas cuando cambia la partida (Priority: P1)

Como jugador, quiero que cada persecución responda al estado vigente, aunque el sistema reutilice información de turnos anteriores.

**Why this priority**: Una ruta obsoleta cambia el resultado de la partida y rompe la reproducibilidad.

**Independent Test**: Comparar cada decisión con una referencia que calcule desde cero en ese instante, modificando puertas, posición del objetivo y eventos entre turnos.

**Acceptance Scenarios**:

1. **T5**, **Given** una ruta antes abierta, **When** una de sus puertas se cierra entre turnos, **Then** el siguiente turno usa otra ruta óptima abierta o espera si no existe una dentro del rango, exactamente como la referencia actual. (FR-008–FR-010, FR-013)
2. **A6**, **Given** una decisión previa, **When** antes del siguiente turno se abre una puerta que abarata el trayecto o el jugador cambia de sala, **Then** la decisión siguiente coincide con recalcular hacia el objetivo actual. (FR-013)
3. **A7**, **Given** una misma partida, **When** se repite con iguales versiones, semilla y acciones, incluidos empates, muertes, cancelaciones y reprogramaciones, **Then** coinciden decisiones, tiempos, secuencias y resultados observables; la latencia de datos no altera la simulación. (FR-006, FR-013–FR-014, FR-016–FR-017)
4. **A8**, **Given** eventos de puerta, efecto y actor con igual tiempo, **When** se ejecutan, **Then** se respeta su secuencia creciente y la decisión utiliza el estado dejado por los eventos anteriores. (FR-006, FR-013–FR-015)
5. **A9**, **Given** que el jugador entra en una sala con enemigos dormidos, **When** se confirma la entrada, **Then** se activan con costo inicial 100 y orden ascendente de ID de instancia; un enemigo activo que llegó desde otra sala continúa activo. Descargar o revelar una sala vecina no activa sus enemigos. (FR-015–FR-016)
6. **A10**, **Given** una puerta abierta por el jugador con llave y cierre automático, **When** el actor cruza y luego se cierra, **Then** permanece en destino y no vuelve a atravesarla mientras esté cerrada; abrir y cruzar son acciones distintas y la llave no se consume. (FR-015)
7. **A11**, **Given** eventos futuros de un actor que muere o de un efecto cancelado, **When** llega su tiempo, **Then** no producen acciones ni daño cancelado; regeneración y curación no superan la vida máxima, y las trampas se activan tras la entrada antes del siguiente evento. (FR-017)
8. **A12**, **Given** una acción reversible con movimiento, efectos y puertas, **When** se usa un pergamino, **Then** se restituyen el estado del motor, eventos, secuencias y azar anteriores, respetando la exclusión de pergaminos y el máximo de cinco acciones; si se repite la misma acción, conserva el resultado determinista correspondiente. La infraestructura de caché no se revierte. (FR-014, FR-018)
9. **A13**, **Given** un jugador en una sala y rastros vecinos de antigüedad conocida, **When** ejecuta una acción válida, **Then** se refresca el rastro pertinente según FR-019; un rastreador solo considera vecinas abiertas con rastro de menos de 400 unidades, desempata por menor ID y espera si no hay rastro fresco; un guardián sin jugador en su sala espera. (FR-011, FR-019)

### Frontera temporal del jugador

Parte I §2.3 (p. 4) fija el orden total por tiempo y secuencia. Parte II §3.6 (p. 6) define el estado de `historia <t>` después de todos los eventos ≤ t y antes de la decisión que corresponda en t. El Apéndice B (p. 13) incluye expresamente el empate. Persona A adopta FR-020 para que la siguiente decisión observe ese estado con el orden de eventos de Parte I. La validación con la línea de tiempo de Persona D está pendiente.

- **A14 — Ambos órdenes:** en t=100, jugador secuencia 10 y enemigo secuencia 11 se ejecutan en ese orden; se devuelve control después del ataque, con el daño ya aplicado. Con enemigo secuencia 10 y jugador secuencia 11, se ejecuta primero el ataque y luego el turno del jugador; la decisión también observa el daño. FR-006, FR-014, FR-020.
- **A15 — Derrota:** un ataque letal de secuencia 11 tras el turno 10 en t=100 deja la partida terminada antes de ofrecer otra decisión; rige la terminación inmediata de FR-017. FR-017, FR-020.
- **A16 — Cancelación y horizonte:** un evento cancelado en t no produce efecto. El primer evento vigente en t+1 queda pendiente, aunque haya cancelados entre él y el turno del jugador. FR-006, FR-017, FR-020.
- **A17 — Efectos:** los eventos de efectos en t respetan su secuencia. Si reprograman un turno todavía pendiente, se respeta FR-005 y se usa la ocurrencia nueva; un turno desplazado a t+1 no se ejecuta como parte de t. FR-005, FR-006, FR-020.
- **A18 — Continuidad:** en partidas activas idénticas, se observan los mismos efectos, consumo de azar y agenda al devolver el control. Dos decisiones consecutivas no difieren ni duplican un ataque que corresponda a la frontera anterior. FR-014, FR-018, FR-020.

La primera acción en t=0 y los costos conservan sus reglas. Esta adenda no implementa `historia`, su registro serializable ni la reconstrucción de D.

### User Story 4 - Conservar la fluidez con muchos cazadores (Priority: P2)

Como jugador, quiero que el procesamiento entre mis decisiones siga siendo ágil con decenas de cazadores, sin sacrificar decisiones correctas.

**Why this priority**: Es el presupuesto de procesamiento oficial bajo la nueva carga.

**Independent Test**: Medir cargas reproducibles sin red ni presentación y contrastar las decisiones con la referencia.

**Acceptance Scenarios**:

1. **P1**, **Given** la cripta de referencia cargada y decenas de cazadores activos, **When** se mide el ciclo completo entre decisiones del jugador, **Then** satisface NFR-001; no se confunde el ciclo con un único evento. (NFR-001, NFR-003)
2. **P2**, **Given** una región alcanzable dentro de rango que permanece igual, **When** aumenta la parte del mapa fuera de rango sin modificar esa región, **Then** la búsqueda de rango pequeño no recorre ni inicializa toda la cripta para cada consulta. (NFR-002)
3. **P3**, **Given** cargas de uno/muchos cazadores y rangos pequeños/grandes, **When** se comparan cálculo individual/compartido y reutilización/recálculo con puertas estables/inestables, **Then** se informa evidencia comparable y toda decisión conserva equivalencia con la referencia; se repiten las mediciones anteriores de agenda y ciclo. (NFR-003, FR-013)

### Edge Cases

- Costo ausente: 100. Costo declarado 1: intervalo mínimo 1. Costos inválidos o asimétricos: política pendiente, no se normalizan silenciosamente en esta especificación.
- Con rango finito, distancia igual a rango: avanzar; distancia superior: esperar. Con `rango=null` explícito, buscar sin tope de costo. Sin ruta abierta: esperar. Coincidencia de sala: atacar antes de evaluar desplazamiento.
- Ninguna salida abierta, rutas múltiples o puertas cambiantes: aplicar T1, T4 y T5 con estado real vigente.
- Movimientos, muertes y cambios de velocidad pueden modificar estado o programación: no se prescribe invalidación universal ni se permite reutilización que cambie decisiones.
- Cierre después de cruzar: no deshace movimiento. Cambio de velocidad: escala tiempo pendiente y recibe secuencia nueva, incluso en terreno costoso.
- Rango ausente o inválido: sin valor inventado; pendiente de Clarify.
- Contenido pendiente al mover al jugador: esperar su disponibilidad antes de confirmar entrada, sin avanzar reloj por espera real.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Toda salida DEBE usar costo 100 cuando falte el campo; un costo declarado DEBE ser entero ≥ 1 y el mismo en ambos sentidos. Fuente: P2 §3.1.
- **FR-002**: Todo actor que se mueve DEBE pagar el costo de la salida atravesada. Fuente: P2 §3.1.
- **FR-003**: La siguiente acción DEBE programarse en `reloj_actual + max(1, costo * 100 // velocidad)`; al moverse, el actor ocupa el destino al ejecutar la acción y no recibe ataques gratuitos. Fuentes: P1 §§2.3, 2.5; P2 §3.1.
- **FR-004**: Los costos distintos del movimiento DEBEN conservarse: atacar/esperar 100, usar/equipar/abrir 50, recoger/soltar 25. Fuente: P1 §2.3.
- **FR-005**: Al comenzar o terminar un cambio de velocidad con acción pendiente, el tiempo restante DEBE ser `max(1, (tiempo_siguiente - t) * velocidad_anterior // velocidad_nueva)` y sumarse a t. Fuentes: P1 §§2.3, 2.10.
- **FR-006**: Los eventos DEBEN ordenarse por tiempo y luego secuencia creciente; toda reprogramación DEBE recibir secuencia nueva e impedir que la ocurrencia sustituida actúe. La hora real y el orden de llegada de datos no determinan el orden de eventos. Fuente: P1 §2.3.
- **FR-007**: Un cazador que comparte sala con el jugador DEBE atacar antes de considerar movimiento. Fuente: P2 §3.2.
- **FR-008**: En salas diferentes, el cazador DEBE determinar el costo mínimo hasta el jugador actual sobre el esqueleto completo y solo salidas realmente abiertas, sin abrir puertas. Fuente: P2 §3.2.
- **FR-009**: Sin ruta abierta, el cazador DEBE esperar con costo 100. Con rango finito, DEBE esperar con costo 100 si el costo mínimo supera el rango. Si existe una ruta admisible, DEBE avanzar solo un paso óptimo y pagar el costo de la salida. Un `rango=null` explícito indica búsqueda sin tope de costo. Fuentes: P2 §3.2 y [aclaración del profesor comunicada por el usuario](research.md#aclaración-del-profesor-sobre-q1).
- **FR-010**: Entre vecinas v que satisfacen `costo(u,v) + distancia(v,jugador) = distancia(u,jugador)`, el cazador DEBE elegir la de menor ID. Fuente: P2 §3.2.
- **FR-011**: Guardián, errante y rastreador DEBEN conservar sus decisiones originales; errante y rastreador solo cambian el costo temporal de movimiento. Se conserva el desempate por ID y rastro fresco de menos de 400 unidades del rastreador. Fuentes: P1 §§2.8–2.9; P2 §3.1.
- **FR-012**: El resultado del cazador NO DEBE depender del conocimiento del jugador ni de qué contenido se haya descargado. Fuente: P2 §3.2.
- **FR-013**: Cada decisión DEBE ser equivalente a recalcular desde cero en ese instante; reutilizar información NO DEBE alterar el resultado tras cambios de puertas, objetivo, movimientos, muertes o velocidad. No se exige invalidar información que sigue siendo válida. Fuentes: P2 §§3.2, 5.2.
- **FR-014**: Con versiones de cripta y catálogo, semilla y acciones idénticas, DEBEN coincidir simulación y secuencia de llamadas al azar; esperar datos no avanza el reloj. Fuentes: P1 §§2.4, 2.6; constitución II.
- **FR-015**: Abrir y atravesar DEBEN seguir siendo acciones distintas; las llaves no se consumen, los enemigos no abren puertas y el cierre automático no desplaza actores. Fuentes: P1 §§2.5, 2.10 y Apéndice B.
- **FR-016**: Incorporar contenido NO DEBE activar enemigos; la entrada del jugador sí, incluida la sala inicial en t=0. Su primera acción usa costo 100; activaciones simultáneas se programan por ID de instancia ascendente. Enemigos ya activos permanecen activos al cambiar de sala. El jugador empieza con su primera acción en t=0 y no entra antes de disponer del contenido destino. Fuente: P1 §§2.4–2.5.
- **FR-017**: DEBEN conservarse combate y efectos de P1 §§2.6, 2.10: daño mínimo 1, vida limitada a vida máxima, muerte inmediata sin acciones futuras; veneno cada 80 durante 400 salvo cancelación, regeneración cada 200, antorcha por duración declarada, trampa inmediata tras entrada y rearme 300 salvo valor declarado, cierre según salida. Cancelar impide activaciones futuras. Guardianes, errantes y rastreadores no adquieren reglas de cazador.
- **FR-018**: Los cambios del motor DEBEN ser reversibles y reconstruibles para retroceso e historia, incluidos reloj, actores, puertas, efectos, eventos, secuencias y azar. Se conserva el retroceso de hasta cinco acciones, sin consumir tiempo, sin recuperar pergaminos ni revertir caché; historia y persistencia completas corresponden a otra capacidad. Fuentes: P1 §2.11; P2 §3.6.
- **FR-019**: DEBE conservarse el rastro actualizado en la sala inicial, destino del movimiento y en cada acción del jugador según P1 §2.9 y Apéndice B. La coordinación del rastro pertenece a C; esta capacidad conserva la conexión temporal.
- **FR-020**: Cuando se procese el turno vigente del jugador en t y la partida siga activa, el motor DEBE completar los eventos automáticos vigentes del mismo t por (tiempo, secuencia), incluidos los que se encolen en t durante el procesamiento, antes de solicitar otra acción. Los cancelados no actúan, ningún evento posterior a t se ejecuta anticipadamente y la partida terminada no ofrece otra decisión. P1 §2.3 establece el orden. P2 §3.6 y el Apéndice B definen el estado histórico. La frontera operativa es una decisión técnica de Persona A pendiente de validación de integración con D.

### Non-Functional Requirements

- **NFR-001 — Presupuesto temporal**: El ciclo completo entre dos decisiones consecutivas del jugador DEBE tomar menos de 20 ms en el equipo local con la cripta de referencia cargada y decenas de cazadores, excluyendo red y renderizado. Se conserva la redacción estricta de P1 §5.2, compatible con el límite 20 ms de P2 §6.1 y ≤20 ms de la constitución. Una enmienda oficial posterior debe revisarse antes de actualizar este requisito.
- **NFR-002 — Alcance del trabajo**: Para rango pequeño, el costo de decidir DEBE depender de la región dentro del rango y no del tamaño total de la cripta; no debe recorrerse ni inicializarse todo el mapa en cada consulta. Fuente: P2 §5.1.
- **NFR-003 — Evidencia**: DEBEN medirse uno/muchos cazadores, rango pequeño/grande, cálculo individual/compartido, reutilización/recálculo siempre y puertas estables/inestables. Las mediciones de agenda y ciclo de P1 DEBEN repetirse con la carga nueva; cargas sintéticas reproducibles por semilla. Los resultados reales y límites se documentarán sin afirmar mediciones aún no realizadas. Fuentes: P2 §§5.1–5.2, 5.6, 6.3, 7.1.
- **NFR-004 — Independencia**: La lógica de rutas y motor DEBE operar sin interfaz interactiva ni solicitudes de red dentro de la búsqueda, usando datos suministrados por los componentes correspondientes. No incorpora datos de criptas concretas. Fuentes: P1 §6; constitución III, V–VI.
- **NFR-005 — Cumplimiento académico**: Se mantienen estructuras y ordenamientos propios y todas las prohibiciones de P1 §7, P2 §6.2 y constitución I. Esta especificación no elige algoritmos, estructuras ni organización técnica; su elección y revisión corresponden al plan.
- **NFR-006 — Trazabilidad y proceso**: Cada escenario DEBE tener tarea y prueba o log que cite su requisito; especificación revisada y confirmada antes del código, correcciones de especificación en confirmaciones separadas previas, prompts textuales registrados sin alterar entradas anteriores. No se autoriza avanzar de fase con este borrador. Fuentes: P2 §§2.2–2.6; constitución IV y Flujo de Desarrollo.

### Key Entities *(include if feature involves data)*

- **Sala y salida**: Lugares conectados; una salida relaciona origen, destino, costo y puerta.
- **Puerta**: Estado real abierta/cerrada, llave requerida y posible cierre automático; distinto de lo recordado por el jugador.
- **Actor**: Jugador o instancia enemiga con vida, posición, velocidad y próxima acción.
- **Cazador**: Actor enemigo cuyo alcance se expresa mediante rango de costo y que persigue la posición actual del jugador.
- **Ruta candidata**: Secuencia de salidas abiertas con costo acumulado y primer paso; su validez se evalúa respecto del estado vigente.
- **Evento y efecto**: Ocurrencia temporal con secuencia de desempate y eventual cancelación; puede cambiar estado y programación.
- **Cambio reversible**: Información del juego necesaria para restituir o reconstruir el estado, sin prescribir representación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: T1–T7 y A1–A13 tienen pruebas reproducibles que satisfacen todos sus resultados esperados y citan los FR asociados; P1–P3 aportan evidencia de NFR-001–NFR-003. Estado actual: definidos, no ejecutados.
- **SC-002**: Todas las decisiones de cazador en las cargas comparadas coinciden con la referencia desde cero, incluidos empates y cambios de puertas u objetivo; cero diferencias admitidas.
- **SC-003**: Dos ejecuciones de cada escenario determinista producen idénticas decisiones, estados, tiempos y secuencias, sin diferencias debidas a latencia ni conocimiento del jugador.
- **SC-004**: El ciclo completo cumple NFR-001 con decenas de cazadores; la evidencia identifica equipo, carga y condiciones. No se afirma cumplimiento antes de medir.
- **SC-005**: Las mediciones de región pequeña y mapa exterior creciente verifican NFR-002 y documentan el trabajo realizado, además de tiempo, sin inventar un umbral numérico ausente en el enunciado.
- **SC-006**: Todos los escenarios conservan las reglas heredadas aplicables y la trazabilidad requisito → escenario → tarea → código → prueba, una vez completadas las fases autorizadas posteriores.

## Assumptions

- P1 significa el enunciado oficial de Parte I de 20 páginas; P2, el de Parte II de 13 páginas. Se leyeron íntegramente con sus apéndices. Los documentos originales permanecen en la ubicación proporcionada por el usuario; sus rutas no prescriben arquitectura del producto.
- Fuentes locales: `D:/Downloads/Primer Proyecto - Estructuras de Datos II 2026 (1).pdf`, `D:/Downloads/Cripta - Parte II.pdf` y `D:/Downloads/CRIPTA_Parte_II_Division_de_Trabajo.pdf` (8 páginas). Constitución vigente 1.1.0, sin modificaciones.
- Los enunciados oficiales prevalecen sobre el reparto; P1 sigue vigente excepto cambios expresos de P2. Persona A es el usuario; «B (tú)» identifica al autor del reparto.
- Para escenarios con datos válidos se dispone del esqueleto completo y datos de catálogo validados. Esto no autoriza fabricar datos, ignorar errores ni implementar dependencias ausentes.
- No se han aportado enmiendas posteriores ni identificado la cripta de referencia efectiva. Se conserva el presupuesto oficial; la certificación final queda pendiente de esa carga.
- Niebla, viaje automático, resolubilidad, historia, formato de guardado y presentación visual quedan fuera del desarrollo de esta capacidad, salvo los puntos de coordinación siguientes. No se modifican recursos visuales; D debe coordinar la presentación de costos y la distinción de cazadores exigida en P2 §7.3.

### Dependencias y límites de responsabilidad

| Responsable | Entrega o acuerdo pendiente | Efecto sobre esta capacidad |
| --- | --- | --- |
| B | Costos simétricos y rango validados, versiones y datos offline; confirmar contrato exacto de datos. | A no inventa valores, no hace HTTP en rutas ni implementa validación ajena. |
| C | Despacho del cazador conservando otras decisiones; observaciones y deltas del conocimiento y rastro. | A conecta eventos reales; C conserva inventario, historial, enemigos existentes y conocimiento. |
| A con C | Consulta de ruta restringible al conocimiento o separación justificada posteriormente. | «Ir a» no usa puertas reales desconocidas; compartir lógica no autoriza filtrar información. |
| D | Contrato de acciones, eventos, tiempos, secuencias, azar y cambios reconstruibles; presentación y mediciones integradas. | A instrumenta su motor; D implementa historia, guardado, replay e interfaz. |
| Equipo | Cambios de representaciones compartidas y contratos antes de su incorporación. | No se altera código compartido ni se incorpora un mock sin autorización. |

Los contratos nuevos no se consideran implementados ni aceptados. Las ubicaciones de código y archivos nuevos están propuestas en plan.md y tasks.md, sujetas a sus permisos de ejecución y límites de propiedad.

### Ambigüedades pendientes para Clarify

Clarify está autorizado. Las respuestas se revisan una por una antes de incorporarse; una consulta pendiente a B o al profesor no resuelve la regla de juego.

1. **Q1 — Rango del cazador**: aclaración parcial. El profesor confirmó, según el usuario, que `rango=null` explícito significa rango ilimitado. [NEEDS CLARIFICATION: tratamiento del campo ausente o de un valor inválido. Confirmar el contrato con B y, si no lo resuelve, con el profesor; no asignar valor por defecto.]
2. **Q2 — Costos inconsistentes**: [NEEDS CLARIFICATION: dependencia externa pendiente de confirmación con B, según respuesta del usuario del 2026-11-02. Confirmar en la fuente oficial el tratamiento de costos inválidos, diferentes por sentido o declarados solo en uno de los extremos. Se mantiene la exigencia de simetría sin definir normalización ni rechazo inventados.]
3. **Q3 — Referencia de rendimiento**: [NEEDS CLARIFICATION: información externa pendiente de confirmación oficial sobre identificación y versión de la cripta de referencia y posibles enmiendas. Se mantiene NFR-001, menos de 20 ms con las condiciones oficiales; no se afirma cumplimiento sin mediciones ni se selecciona una referencia ficticia.]

La mención del rastro por acción en P1 Apéndice B se conserva como exigencia adicional a §2.9, no como una regla que se elimina. P2 remite a una enmienda en §2.7 que no aparece en el documento recibido; se requiere verificar si existen aclaraciones posteriores antes de cerrar la referencia de rendimiento.
