# Investigación técnica provisional

**Fecha:** 2026-11-02. **Estado:** análisis sin implementación ni benchmarks; Q1–Q3 no resueltas. Producir borradores condicionados fue autorizado expresamente.

## Fuentes

P1 oficial, 20 páginas: §§2.3–2.11, 4.1, 5–8 y apéndices. P2 oficial, 13 páginas: §§3.1–3.2, 5.1–5.2, 5.6, 6–7 y Apéndice B. Reparto, 8 páginas: Persona A e integración, subordinado a enunciados. Rutas de PDF en [spec.md](spec.md). [Constitución 1.1.0](../../.specify/memory/constitution.md), código existente y especificación. Investigación de rutas revisada por agente de lectura según la habilidad; no sustituye fuentes ni constituye medición.

## Incógnitas

| ID | Evidencia disponible | Estado |
| --- | --- | --- |
| Q1 | Parte II incluye rango entero en la ficha del cazador. B reporta Enemy.rango opcional/null, entero ≥1 si tiene valor, sin default ni obligación adicional para cazador; fuente primaria no disponible. Política ante ausencia/null/invalidez y conciliación pendientes del profesor. | NEEDS CLARIFICATION |
| Q2 | Parte II: costo ausente 100, declarado entero ≥1 y simétrico. B reporta Exit dirigido con costo opcional/null, entero ≥1 si tiene valor, sin default ni garantía de simetría; fuente primaria no disponible. El profesor confirmó, según el usuario, el costo 100 ante ausencia y la simetría. El costo `null`, los valores inválidos y los datos contradictorios siguen sin política confirmada. | PARCIALMENTE ACLARADA |
| Q3 | <20 ms y condiciones oficiales; falta identificación de referencia y enmiendas. | NEEDS CLARIFICATION |

## Comunicación reportada de B sobre OpenAPI 1.1.0

**Registro:** 2026-11-05, fecha contextual de esta corrección. **Procedencia:** mensaje del usuario que transmite la revisión realizada por el compañero B del OpenAPI oficial versión 1.1.0. No se dispone de la fecha original de comunicación de B, de una copia verificable del documento ni de sus fragmentos originales. No se consultó independientemente OpenAPI ni se ejecutaron validadores. En ese momento aún no se había comunicado una respuesta del profesor sobre Q1/Q2. Esta limitación no impide registrar evidencia parcial con autorización documental, pero impide presentarla como contrato verificado o aclaración definitiva.

| Elemento | Información comunicada por B, sin verificación independiente | Autoridad del enunciado y cuestión pendiente |
| --- | --- | --- |
| Enemy.rango | Opcional; admite null; con valor, entero ≥1; no hay valor predeterminado declarado ni obligatoriedad adicional para comportamiento cazador. | Parte II §3.2 incluye rango en la ficha del cazador. No asignar mínimo normativo, default ni conducta para rango ausente/null/inválido a partir del reporte; Q1 permanece abierta. |
| Exit y costo | Salidas descritas como dirigidas; costo opcional, admite null; con valor, entero ≥1; no se declara default ni garantía de simetría. | Parte II §3.1 fija costo ausente = 100 y costo igual en ambos sentidos. Una representación dirigida no elimina esa igualdad. No equiparar costo null con ausencia ni decidir sobre costos inválidos/asimétricos/unilaterales: Q2 permanece abierta. |

La ausencia reportada de restricciones en un esquema no deroga las reglas del juego ni demuestra por sí sola que los datos reales las incumplan. Se conserva FR-001 y la ficha de cazador de §3.2; no se adopta una política de normalización, rechazo, copia entre sentidos o fabricación de rango. E-B-COSTOS/E-B-RANGO requieren además evidencia independiente de suministro/acceso a datos válidos; ninguno se marca entregado por este reporte.

**Consultas pendientes:** al profesor, cómo conciliar la ficha de cazador con rango ausente/null y qué hacer ante costo null o datos inconsistentes con §3.1; a B, copia o fragmentos originales identificados de Enemy/Exit en OpenAPI 1.1.0 y contratos efectivos de acceso. Q3 conserva la referencia/enmiendas pendientes y <20 ms; esta comunicación no aporta evidencia de rendimiento.

## Aclaración del profesor sobre Q2

**Registro del 2026-11-09.** El usuario comunicó que el profesor confirmó dos reglas de Parte II §3.1: si falta el campo `costo`, se usa 100, y se asume el mismo costo en ambos sentidos de una puerta entre salas adyacentes. Sigue pendiente cómo tratar `costo=null`, valores inválidos y contradicciones entre descriptores. La simetría del costo no acredita que el estado abierto o cerrado esté sincronizado entre extremos. E-B-COSTOS sigue pendiente de que B demuestre el suministro versionado de costos válidos hasta el motor de A. Q1 (rango ausente, `null` o inválido) y Q3 (referencia de rendimiento) siguen abiertas.

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

R1–R5 son preferencias analíticas revisables; Q1–Q3 no resueltas, contratos no acordados y pruebas no ejecutadas. No se atribuyen datos medidos ni se declara gate final de Plan superado. La matriz de evidencia y pruebas está en [quickstart.md](quickstart.md).
