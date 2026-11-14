# Investigación técnica provisional

**Fecha:** 2026-11-02. **Estado:** análisis sin implementación ni benchmarks; Q1–Q3 no resueltas. Producir borradores condicionados fue autorizado expresamente.

## Fuentes

P1 oficial, 20 páginas: §§2.3–2.11, 4.1, 5–8 y apéndices. P2 oficial, 13 páginas: §§3.1–3.2, 5.1–5.2, 5.6, 6–7 y Apéndice B. Reparto, 8 páginas: Persona A e integración, subordinado a enunciados. Rutas de PDF en [spec.md](spec.md). [Constitución 1.1.0](../../.specify/memory/constitution.md), código existente y especificación. Investigación de rutas revisada por agente de lectura según la habilidad; no sustituye fuentes ni constituye medición.

## Incógnitas

| ID | Evidencia disponible | Estado |
| --- | --- | --- |
| Q1 | Parte II incluye rango entero en la ficha del cazador. B reporta Enemy.rango opcional/null, entero ≥1 si tiene valor, sin default ni obligación adicional para cazador; fuente primaria no disponible. El profesor confirmó, según el usuario, que un `null` explícito significa rango ilimitado. El tratamiento del rango ausente o inválido sigue pendiente. | PARCIALMENTE ACLARADA |
| Q2 | Parte II: costo ausente 100, declarado entero ≥1 y simétrico. B reporta Exit dirigido con costo opcional/null, entero ≥1 si tiene valor, sin default ni garantía de simetría; fuente primaria no disponible. El profesor confirmó, según el usuario, el costo 100 ante ausencia y la simetría. El costo `null`, los valores inválidos y los datos contradictorios siguen sin política confirmada. | PARCIALMENTE ACLARADA |
| Q3 | <20 ms y condiciones oficiales; falta identificación de referencia y enmiendas. | NEEDS CLARIFICATION |

## Comunicación reportada de B sobre OpenAPI 1.1.0

**Registro:** 2026-11-05, fecha contextual de esta corrección. **Procedencia:** mensaje del usuario que transmite la revisión realizada por el compañero B del OpenAPI oficial versión 1.1.0. No se dispone de la fecha original de comunicación de B, de una copia verificable del documento ni de sus fragmentos originales. No se consultó independientemente OpenAPI ni se ejecutaron validadores. En ese momento aún no se había comunicado una respuesta del profesor sobre Q1/Q2. Esta limitación no impide registrar evidencia parcial con autorización documental, pero impide presentarla como contrato verificado o aclaración definitiva.

| Elemento | Información comunicada por B, sin verificación independiente | Autoridad del enunciado y cuestión pendiente |
| --- | --- | --- |
| Enemy.rango | Opcional; admite null; con valor, entero ≥1; no hay valor predeterminado declarado ni obligatoriedad adicional para comportamiento cazador. | Parte II §3.2 incluye rango en la ficha del cazador. No asignar mínimo normativo, default ni conducta para rango ausente/null/inválido a partir del reporte; Q1 permanece abierta. |
| Exit y costo | Salidas descritas como dirigidas; costo opcional, admite null; con valor, entero ≥1; no se declara default ni garantía de simetría. | Parte II §3.1 fija costo ausente = 100 y costo igual en ambos sentidos. Una representación dirigida no elimina esa igualdad. No equiparar costo null con ausencia ni decidir sobre costos inválidos/asimétricos/unilaterales: Q2 permanece abierta. |

La ausencia reportada de restricciones en un esquema no deroga las reglas del juego ni demuestra por sí sola que los datos reales las incumplan. Se conserva FR-001 y la ficha de cazador de §3.2; no se adopta una política de normalización, rechazo, copia entre sentidos o fabricación de rango. E-B-COSTOS/E-B-RANGO requieren además evidencia independiente de suministro/acceso a datos válidos; ninguno se marca entregado por este reporte.

**Consultas pendientes:** al profesor, qué hacer con rango ausente o inválido y qué hacer ante costo null o datos inconsistentes con §3.1; a B, copia o fragmentos originales identificados de Enemy/Exit en OpenAPI 1.1.0 y contratos efectivos de acceso. Q3 conserva la referencia/enmiendas pendientes y <20 ms; esta comunicación no aporta evidencia de rendimiento.

## Aclaración del profesor sobre Q2

**Registro del 2026-11-09.** El usuario comunicó que el profesor confirmó dos reglas de Parte II §3.1: si falta el campo `costo`, se usa 100, y se asume el mismo costo en ambos sentidos de una puerta entre salas adyacentes. Sigue pendiente cómo tratar `costo=null`, valores inválidos y contradicciones entre descriptores. La aclaración posterior del usuario ratifica que la simetría es una condición de los datos de entrada. El motor consume el costo de la salida recorrida. La prueba `test_movimiento_reciproco_costo_250` verifica ambos sentidos con datos válidos; la evidencia de suministro figura en [E-B-COSTOS](contracts/integracion.md).

## Aclaración del profesor sobre Q1

**Procedencia:** aclaración del profesor comunicada por el usuario. Un valor `rango=null` explícito indica que el cazador busca sin tope de costo. Un entero válido conserva el límite inclusivo. Los casos de campo ausente y de valor inválido siguen pendientes. E-B-RANGO debe preservar la distinción entre esos estados y acreditar el acceso del motor al dato versionado sin HTTP durante la búsqueda. El registro integrado de [E-B-RANGO](contracts/integracion.md) acredita el acceso para entradas válidas. La prueba de turno con ruta de costo 400 verifica el caso ilimitado.

## Alcance oficial de Q1 y Q2

Parte II §3.2 (p. 4) exige el campo de rango en la ficha del cazador. La aclaración del profesor comunicada por el usuario establece el significado del valor `null` explícito. El enunciado no prescribe que A acepte fichas sin el campo ni define un valor de reemplazo para datos inválidos (T001, FR-007/FR-009).

Parte II §3.1 (p. 4) permite omitir el costo y fija 100 en ese caso. Cuando se declara, exige un entero ≥1 y el mismo costo en ambos sentidos. La aclaración comunicada por el usuario confirma esa simetría. Un costo `null`, inválido o contradictorio queda fuera de las entradas conformes. El enunciado no prescribe una reparación o un rechazo del motor para esas entradas (T002, FR-001).

El reparto oficial (§Persona A, p. 3) sitúa la validación y normalización de datos en la coordinación A/B. El [registro de integración](contracts/integracion.md) delimita los datos que entrega B y consume A. Las preguntas originales de GB1/GB2 quedan registradas como casos de robustez fuera de la aceptación funcional de A. La [guía](quickstart.md#entradas-verificadas-de-terreno-y-rango) documenta las reglas y las pruebas para T018.

## Notación

V/E: salas/arcos; Vr/Er: salas/arcos examinados en región de rango y frontera inmediata; H: cazadores; N: eventos físicos, incluidos cancelados; C: cancelados antes del próximo válido. Grado ≤4. Los costos siguientes son análisis del diseño, no tiempos observados.

## R1 — Representación

**Decision:** proponer adyacencias con índices densos y referencias a puertas reales. IDs externos se ordenan con algoritmo propio y se traducen una vez mediante búsqueda binaria propia; consultas internas reciben índices resueltos. Si reciben IDs, agregar O(log V) para resolución inicial, sin ocultarlo ni repetirlo en cada arco.

**Rationale:** grado acotado y posible dispersión de IDs. Reserva e inicialización de arreglos de salas O(V); ordenamiento propio de IDs O(V log V); resolución de E conexiones mediante búsqueda binaria propia O(E log V). Preparación total O(V log V+E log V), espacio total O(V+E); una vez preparado, O(grado) para vecinos. La reserva O(V) no describe el costo total de preparación, ni debe repetirse por decisión. Medir preparación y consultas por separado.

**Alternatives considered:** matriz O(V²) espacio y barridos O(V) por vecino; representación actual por ID directo O(maxID+E), apropiada solo si densidad se verifica. No usar dict/set ni tablas hash como atajo; conservar caché ordenada de B.

## R2 — Búsqueda individual y desempate

**Decision:** Dijkstra lexicográfico con heap indexado propio, etiquetas (distancia, primerID) y marcas de generación para distancias, posición de heap y cierre. Prioridad total (distancia, primerID, ID_nodo), con marcador interno para origen que no sea un ID de juego inventado.

Cada vecino inmediato recibe su propio ID como primerID; las relajaciones posteriores heredan ese valor. Una etiqueta mejora al reducir distancia o, a igual distancia, primerID. No insertar candidatos cuyo costo exceda el rango suministrado. Parar al cerrar el objetivo o agotar candidatos permitidos. No copiar caminos completos en cada relajación.

**Corrección:** los costos estrictamente positivos hacen que todos los predecesores de una ruta óptima se procesen antes de cerrar el objetivo. A igual distancia al mismo nodo domina el menor primerID; a menor distancia domina ese prefijo al compartir sufijo. El objetivo definitivo tiene distancia mínima y primer vecino de menor ID. Ordenar solo vecinos o usar ID del nodo como desempate del heap no basta. No se usa random.

**Complejidad propuesta:** O((Vr+Er)log(Vr+1)) por consulta, O(Vr) heap y O(V) arreglos residentes preparados una vez. No limpiar V posiciones por consulta. La limpieza final de frontera es O(Vr), imputada a la búsqueda que la produjo; no cargar el trabajo de una consulta grande a una pequeña posterior. Enteros de generación sin reinicialización global periódica. Rango grande puede alcanzar O((V+E)log V).

| Alternativa propia | Tiempo | Espacio | Evaluación |
| --- | --- | --- | --- |
| Heap indexado/disminuir clave | O((Vr+Er)log(Vr+1)) | O(V) residente + O(Vr) | Base propuesta; mantener índices correctamente. |
| Heap con entradas repetidas | O((Vr+Er)log(Er+1)) | O(V) + O(Er) | Menos invariantes, más obsoletos; medir. |
| Selección lineal | O(Vr²+Er) | O(V) + O(Vr) | Referencia independiente y alternativa para cargas pequeñas. |
| Búsqueda por cada primer vecino, sin volver al origen | Hasta 4 búsquedas acotadas | Reutilizable | Desempate explícito; trabajo repetido. |
| BFS por cantidad de pasos | O(Vr+Er) | O(Vr) | No válida como solución general de costos variables. |

La referencia en mapas pequeños puede enumerar caminos simples con arreglos propios o usar selección lineal independiente; no compartir la misma implementación defectuosa para comprobarse a sí misma. No se declara una ganadora empírica.

## R3 — Cálculo compartido

**Decision:** la búsqueda individual acotada es la base propuesta. El cálculo compartido es una alternativa experimental separada; no se activa automáticamente en producción, ni siquiera por disponer de un campo válido. Su eventual incorporación requiere evidencia, revisión y autorización posteriores.

Distancias inversas desde jugador sobre arcos entrantes permiten campo completo en O((V+E)log V), espacio O(V+E). Cada cazador examina vecinos abiertos y escoge menor ID que cumple costo+dist(vecino)=dist(origen), comprobando rango: O(grado). Total compartido O((V+E)log V+H·grado), frente a suma de búsquedas individuales. El índice inverso se construye una vez; no inventar arcos ni simetría de estado a partir de simetría de costo.

**Límite de localidad:** truncar por rango alrededor del objetivo puede explorar una región enorme ajena al cazador. Por eso un fallo compartido no dispara un recorrido global para atender una consulta pequeña. Un campo ya válido puede reutilizarse; su construcción, invalidación y reconstrucción se contabilizan, no se esconden tras hits baratos. Campo parcial solo sirve cuando el origen está definitivamente resuelto; ausencia de dato no prueba ausencia de ruta.

**Alternatives considered:** individual siempre; inversa compartida completa; expansión compartida incremental; híbrido. Umbrales por H/rango dependen de medición y no pueden legitimar incumplir NFR-002. No se inventa un umbral numérico.

## R4 — Reutilización e invalidación

**Decision:** evaluar, sin elegir todavía un diseño definitivo de caché, un registro fijo de última consulta (sin dict) con identidad de grafo, época, origen, objetivo, rango y resultado; comparación O(1). Es una alternativa mínima, potencialmente poco representativa cuando varios cazadores alternan orígenes, objetivos o rangos. Sus fallos por reemplazo no demuestran que toda reutilización sea inconveniente. Campo compartido experimental aparte, acotado, sin activación automática ni caché ilimitado por actor.

Comparar al menos recálculo siempre, última consulta y un diseño de varias entradas con capacidad explícita por acordar. Candidatos propios: arreglo de capacidad M con búsqueda y reemplazo deterministas O(M), espacio O(M); o registro acotado por actor con acceso por índice preparado y memoria total O(H), contemplando alta/baja y liberación. M y la política de reemplazo no se fijan sin evaluación. Son candidatos documentales, no permiso para implementar almacenamiento de C/D ni tablas hash. Comparar con igual secuencia de consultas, semilla, mapa, actores y cambios de puertas; informar presupuesto de memoria para que una capacidad mayor no parezca una ventaja gratuita.

Reportar tasas de acierto y fallos por reemplazo/invalidez, bytes residentes y pico, invalidaciones, búsquedas ahorradas y tiempo total de consulta más mantenimiento (búsqueda de clave, inserción, reemplazo, liberación e invalidación). Incluir puertas estables e inestables y actores alternados, además de consultas repetidas al mismo origen. No extrapolar desde última consulta a todas las políticas, ni elegir una caché por aciertos sin contar su costo de mantenimiento.

Época monótona es metadato derivado, distinto de reloj y secuencias de eventos. Apertura/cierre efectivos invalidan conservadoramente resultados. Restauración, undo o rollback vacían derivados o cambian identidad/época sin reutilizar revisiones antiguas: evitar que un número restaurado coincida con un estado diferente. No guardar copias del cache en historial. La invalidación lógica O(1) no debe ocultar liberación física O(V) de grandes arreglos; medirla y preferir reutilización de capacidad sin barrido global.

| Cambio | Distancias | Ejecución |
| --- | --- | --- |
| Puerta abre/cierra | Invalida global conservadoramente | Evento por tiempo/secuencia; no desplazar actor ya cruzado. |
| Jugador cambia sala | Objetivo diferente | Movimiento y efectos ordinarios. |
| Cazador cambia sala | Clave de origen diferente; campo compartido podría servir | Pagar costo del arco. |
| Velocidad | No cambia costos geométricos | Reprogramar progreso y secuencia. |
| Otro actor mueve/muere | Sin bloqueo por ocupación en reglas confirmadas; revisar consecuencias indirectas | Muerto no actúa; puede dejar botín/efectos. |
| Conocimiento/antorcha | No cambia mapa real del cazador | C registra exploración. |
| Carga/retroceso/fallo | Descartar derivados | C/D restauran estado, reloj, secuencias y azar. |

**Alternatives considered:** recálculo siempre (referencia obligatoria); invalidación global de bajo costo lógico; selectiva con dependencias por arcos, memoria y pruebas adicionales. Comprobar solo que la ruta vieja sigue abierta no demuestra optimalidad: una apertura externa puede crear ruta mejor o empatada con primerID menor. Selectiva no elegida sin prueba y medición.

## R5 — Agenda y motor

**Decision:** conservar inicialmente heap de eventos propio y API de restauración; comparar contra heap indexado. Insertar O(log N), cancelar por referencia O(1), reprogramar O(log N); extraer tras C cancelados O((C+1)log N), no O(log eventos válidos) garantizado. Memoria O(N), incluidos obsoletos. El heap indexado elimina en O(log N), pero necesita mantener índices durante restauración y respetar identidad/secuencia.

El motor conserva única autoridad de secuencias semánticas. Lee costo del arco antes de mover y programa una sola próxima acción. Activación inicial sigue costando 100. Reutilizar distancia no reutiliza eventos ni tiempos pendientes. Callbacks de historial y restauración requieren pruebas de identidad/en_cola/contador. No se cambia infraestructura ajena por este análisis.

## Resultado de investigación

R1–R5 documentan las alternativas del plan. Q1 y Q2 tienen aclaraciones parciales registradas arriba. Q3 sigue pendiente. La evidencia posterior se recoge abajo y en [quickstart.md](quickstart.md).

### Búsqueda individual y límites (T028)

El contexto real prepara el grafo, el heap indexado y los arreglos una vez. Cada consulta usa una generación nueva, procesa etiquetas por costo total y primer ID, y descarta arcos cerrados o candidatos que excedan el límite inclusivo. El primer paso se obtiene al fijar la etiqueta del destino. Sin paso admisible, el resultado no distingue desconexión de distancia superior al límite. El contraste con enumeración de caminos simples consta en [T026](quickstart.md#validación-local-de-t026). Los conteos del fixture [T039](quickstart.md#validación-local-de-t039) son evidencia de localidad, sin equivalencia con una medición del ciclo completo. T028 espera el cierre de T027 y la evidencia de la fuente filtrada.

### Efectos sobre rutas y agenda (T038)

La tabla de R4 separa distancias de programación. La evidencia de T029/T033 confirma en pruebas locales que cambiar el objetivo o el estado de una salida cambia la consulta cuando corresponde, mientras que cambiar velocidad, ocupar una sala o matar al enemigo allí conserva las distancias si el grafo no cambia. T030 aporta el orden de eventos y T037 aporta A13. La aceptación bilateral y los cambios indirectos del mapa integrado siguen pendientes de T032.

En producción el contexto reutiliza sus arreglos sin guardar resultados entre consultas. La invalidación conservadora avanza la generación para que una etiqueta de una búsqueda anterior quede inaccesible. En carga, retroceso y rollback la agenda, sus secuencias y el RNG son estado semántico, mientras que las marcas de búsqueda son infraestructura derivada. Las pruebas de T031 y T034 verifican restauración y consultas posteriores. El rollback de `b1e78c8` invalida las marcas tras los inversos, conserva la identidad del evento pendiente y permite repetir la acción. El primer productor H3 se verificó bajo activación explícita de prueba. La conexión en la partida ordinaria y la regresión conjunta de T037/T038 constan en [la entrega integrada](tasks.md#cierre-de-la-entrega-integrada-de-a).

### Evaluación sintética y paquete local de entrega (T047/T050)

La evaluación publicada en `0396f60` conserva el algoritmo individual de producción y compara alternativas aisladas. La referencia lineal implementada recorre V etiquetas por selección, por lo que su costo es O(V·Vr + Er) para Vr vértices expandidos y Er arcos examinados. En el campo inverso de rango 100, los mapas de 128, 512 y 2048 salas expandieron cinco vértices cada uno, pero inicializaron 256, 1024 y 4096 celdas por reconstrucción. Ese costo O(V) limita su localidad aunque la consulta reutilizada sea barata. Las cachés FIFO de una y cuatro entradas y la agenda indexada son candidatos medidos en cargas sintéticas. La corrida de 24 cazadores del ciclo sintético conservó los 94 eventos procesados y el mismo estado final en ambas agendas. La equivalencia observada corresponde a esa carga.

Para el paquete local de entrega, las fuentes son [la especificación](spec.md), [el plan](plan.md), [la guía reproducible](quickstart.md#evaluación-sintética-de-rutas-y-agendas) y [la trazabilidad](tasks.md#evidencia-parcial-para-entrega). El índice local identifica los materiales para el traslado: la [reproducción de la partida integrada](quickstart.md#reproducción-de-la-entrega-integrada-de-a) para README.md y los análisis de alternativas, la [medición candidata](#ciclo-integrado-en-cripta-06-evidencia-para-t046) y las [interfaces verificadas](#interfaces-de-la-entrega-integrada) para DECISIONES.md. T050 espera T047–T049 y la revisión de completitud, incluidas las respuestas restantes de Q1/Q2 y la medición oficial Q3.

### Ciclo integrado en cripta-06 (evidencia para T046)

El 2026-11-14, sobre `af979bb`, se descargó `cripta-06@f9ed9afa683d` (300 salas) a un paquete temporal. Se cargó su esqueleto con `ClienteOffline` antes de medir. Se usó `medir_integracion(salas, 20261001, 30)` de la utilidad integrada con 30 cazadores inyectados, puertas abiertas para la carga y mapa completo. Entorno de medición: Python 3.14.5, Windows NT 10.0.19045, Intel64 Family 6 Model 165 Stepping 5.

Se registraron en memoria las lecturas de `perf_counter_ns` de la utilidad y se calcularon mínimo, mediana y máximo de los primeros 30 pares, que miden el ciclo completo. Los 30 pares siguientes corresponden a consultas de viaje y se excluyeron. Sin renderizado y con cero solicitudes HTTP durante la medición, el ciclo obtuvo **0,1343 / 1,4549 / 5,0997 ms** (mínimo, mediana y máximo). Los 30 ciclos observados quedaron por debajo de 20 ms. La corrida acredita esa carga y versión. T045 está cerrado con la conexión de medición integrada. T046 requiere T004 y una medición con la referencia y condiciones oficiales Q3.

### Interfaces de la entrega integrada

Constancia técnica sobre `980168a`, con la integración de D incorporada en `dff5882`. Las responsabilidades corresponden al reparto recogido en la [especificación](spec.md). Las pruebas acreditan el comportamiento descrito.

| Entrega | Interfaz y comportamiento verificable | Evidencia |
|---|---|---|
| E-C-RUTA (A/C) | C aporta `PlanificadorConocido.consultar(origen, destino)`, que entrega `ConsultaRuta` sobre salas exploradas y puertas recordadas abiertas. A aporta `buscar_ruta(grafo, espacio, frontera, origen_indice, destino_indice, limite)`. Un límite entero es inclusivo y `None` como resultado acotado indica que no se encontró paso admisible. | [Aceptación T023/T027](../../tests/test_contrato_rutas_c.py), `980168a`. |
| E-C-DESPACHO (A/C) | A despacha al cazador en `Motor._ejecutar_turno_enemigo(enemigo, decidir_accion_enemigo)`. Los otros enemigos conservan el callback de C con enemigo, sala, coincidencia con jugador, rastro, RNG y reloj. | [Turnos del cazador](../../tests/test_turno_cazador.py), `5c67c8d`. |
| E-BC-PUERTA (B/C/A; conexión integrada por D) | `Motor.extremos_puerta(sala, direccion)` comparte el cambio físico ante retorno único en ambos sentidos. A aportó el resolver topológico y D conectó apertura, cierre único y reversión bilateral. | [PD-01–PD-04](../../tests/test_puertas_reciprocas_d.py), `5494d79` y `f31662c`. |
| E-C-OBS y E-C-UNDO (C/A) | A emite entrada y observaciones en el flujo del motor. C produce lotes con `entrar(sala_id)` y `observar_puerta(sala_id, puerta_id, cerrada)`; el historial del turno conserva inversos que llaman a `revertir(cambios)`. D conectó la observación y los deltas a la partida ordinaria. | [Partida completa](../../tests/test_partida_completa.py) y [controlador real](../../tests/test_controlador_ac_real.py), `f31662c`. |
| E-D-CAMBIOS y E-D-RESTAURA (A/D) | A entrega los cambios del turno y descarta derivados de rutas al restaurar. D integra el productor sobre la frontera de eventos y `MotorPartida.restaurar_estado_con_historia(estado, historia)` prepara y valida estado, mapa e historia antes de publicar la carga. | [Receptor H3](../../tests/test_receptor_h3_d.py), [MC-01 y DX-06](../../tests/test_controlador_ac_real.py), `7daf808` y `f31662c`. |
| E-D-MEDICION (A/D) | A entrega la utilidad sintética de rutas y agenda; D conecta sus funciones `medir_rutas`, `medir_localidad`, `medir_agendas` y `medir_ciclo_motor` al subsistema sin vista `terreno-cazador`. | [Punto de entrada](../../bench.py), [pruebas](../../tests/test_bench_terreno_cazador.py) y [comandos integrados](../004-linea-tiempo/integracion-completa.md#reproducción). |
