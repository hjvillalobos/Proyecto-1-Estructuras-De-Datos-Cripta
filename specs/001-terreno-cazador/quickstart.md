# Guía de validación prevista — provisional

**Comandos portables:** ejecutar desde la raíz del proyecto con el entorno y dependencias preparados. Las ejecuciones originales registradas utilizaron Python 3.12.14 del runtime auxiliar de Codex; los comandos se muestran como `python -B -m unittest ...` para no depender de una ruta personal. Esta corrección editorial conserva todos los resultados históricos.

**Fecha:** 2026-11-02. No se ejecutó ningún test ni benchmark durante Plan. No hay implementación nueva ni suites T1–T7 creadas. Esta guía separa comandos existentes de escenarios futuros para no afirmar ejecutabilidad inexistente.

**Estado documental al 2026-11-05:** Plan provisional, 51 tareas y dos revisiones Analyze disponibles; correcciones documentales I1/I5/C2 de la segunda revisión incorporadas, sin nueva ejecución de habilidades. Ninguna tarea de implementación ejecutada por esta sesión. Q1–Q3 y contratos E-* pendientes. Mantener esta fecha de actualización separada de la fecha histórica de creación.

## Prerrequisitos

### Autorización limitada de fundamentos — 2026-11-05 (T005)

El usuario autoriza T005–T010 y sus pruebas, exclusivamente en modelo/rutas.py, pruebas nuevas de fundamentos y documentación de A. La spec está confirmada en 4ee04ff. Se verificaron I1 (E-B-COSTOS/E-B-RANGO independientes), I5 (T027 espera T024 para cierre total) y C2 (reporte indirecto de B, no verificación primaria). Esta revisión del alcance no ejecuta Analyze ni cierra Q1–Q3; G0/GA se liberan solo para estos fundamentos con datos válidos. Checklist de requisitos leído sin modificar: 13/16, tres pendientes. Las prohibiciones históricas de ejecución de este documento describen las fases anteriores.

Archivos autorizados ahora: tests/datos_terreno_cazador.py, tests/test_grafo_terreno.py, tests/test_heap_rutas.py y modelo/rutas.py. Fixtures locales: 0–128 salas con IDs dispersos, grado ≤4, conexiones recíprocas de igual costo positivo, puertas con estado inicial explícito y semillas 20261105/17. Se permite costo ausente (100 oficial); no se generan null, asimetrías ni datos inválidos. Sala y sus descriptores se reutilizan del contrato existente, sin simular servicios ni componentes ausentes. Sus diccionarios JSON son solo entrada, nunca índices/colas/cachés del algoritmo. Referencias de puertas se conservan sin implementar sincronización ni invalidación.

No se requiere ningún doble externo. Dobles de cliente HTTP, gestor de precarga, catálogo, historial o persistencia seguirían necesitando autorización adicional y no se crean. Las suites posteriores T011–T046 y utilidades/bench_terreno_cazador.py permanecen propuestas, sin autorización de escritura/ejecución en esta etapa.

Inventario de nombres de T005 (todos bajo tests/ salvo la utilidad): datos_terreno_cazador.py, test_grafo_terreno.py y test_heap_rutas.py se autorizan ahora. Permanecen futuros test_costos_terreno.py, test_velocidad_terreno.py, test_rutas_cazador.py, test_decision_cazador.py, test_contrato_rutas_c.py, test_validez_rutas.py, test_eventos_terreno.py, test_restauracion_rutas.py y test_localidad_rutas.py, y utilidades/bench_terreno_cazador.py. Las suites existentes de regresión se conservan sin edición y no se ejecutan como parte de estas tareas.

Comando limitado previsto: `python -B -m unittest tests.test_grafo_terreno tests.test_heap_rutas -v`. No ejecuta otras suites ni benchmarks y no crea bytecode. Se registrará el intérprete efectivo y el resultado real al terminar. El grafo resuelve IDs y vecinos en preparación; no hay aún búsqueda de rutas ni política de cazador. El heap ordena etiquetas por distancia, primer ID e ID de sala; la generación invalida auxiliares sin barridos de V. Finalizar una frontera pendiente se imputa a la consulta que la produjo antes de iniciar otra.

Python ≥3.11, entorno reproducible según README y dependencias del proyecto; Spec Kit 1.2.3/Codex para proceso. Antes de ejecutar pruebas en fase autorizada: comprobar rama/estado según reglas del usuario, disponer de permisos para archivos temporales de pruebas y no incluir datos locales. No instalar ni modificar dependencias por este documento.

La documentación puede actualizarse con autorización G-DOC, sin necesitar Implement. Código y ejecución de pruebas/benchmarks requieren permisos posteriores G0/GA, spec confirmada antes del código y revisión vigente de las correcciones; una edición documental no libera Q1/Q2 ni entregables E-*. Q3 pendiente no se convierte en referencia sintética oficial. Los borradores de cierre se permiten, pero T047–T050 solo se completan con sus prerrequisitos y evidencia final; el paquete local no significa actualización de DECISIONES.md/README.md.

Para integración, T013/T014 esperan E-B-COSTOS sin esperar E-B-RANGO; T025 requiere ambos y E-C-DESPACHO. Tras autorización futura, una ejecución parcial de las pruebas del núcleo puede registrarse con suites omitidas/motivo, sin completar T027. Su cierre total exige T024/T025/T026, contratos/permisos aplicables y las tres suites incluidas en T027. La [comunicación de B](research.md#comunicación-reportada-de-b-sobre-openapi-110) es evidencia indirecta, sin copia primaria: no habilita pruebas que prescriban políticas de rango ausente/null, costo null o inconsistencias. El profesor sigue sin responder Q1/Q2; esto no impide registrar o corregir documentación autorizada.

## Comandos existentes para ejecución posterior autorizada

Desde raíz del proyecto, estas suites ya existen; pueden generar archivos temporales y por ello NO se ejecutaron en Plan:

```powershell
python -B -m unittest tests.test_juego tests.test_enemigos tests.test_rastro tests.test_historial
python -B -m unittest tests.test_regresiones_juego tests.test_integridad_operaciones tests.test_fallos_transaccionales
python -B bench.py --subsistemas agenda ciclo --sin-disco --eventos 256 --salas 100 --operaciones 10000 --repeticiones 5 --semilla 20261001
```

Las cifras del comando son una carga sintética de comparación propuesta, no la cripta oficial ni la cantidad exigida de cazadores. bench.py todavía no ofrece comparaciones de rutas/cazadores: el comando actual solo sirve como base histórica a volver a medir. La integración de nuevos subsistemas es de D con funciones de A, y se acordará sin inventar flags como si existieran.

## Diseño de nuevas pruebas T1–T7

Los nombres propuestos de suites y utilidades están en tasks.md (T006–T046); GA mantiene pendiente la autorización de sus rutas. Ninguna prueba se escribe ahora. Construir grafos sintéticos con arreglos propios, sin incorporarlos como datos reales del juego. Cada futura prueba cita FR/NFR y su tarea correspondiente. La existencia de tasks.md no acredita ejecución.

| Caso | Preparación sintética y acción | Resultado a comprobar | Requisitos |
| --- | --- | --- | --- |
| T1 | Cazador activo en sala diferente; ninguna ruta abierta | Esperar costo 100, sin cambiar posición ni abrir puertas | FR-007–009 |
| T2 | Mejor ruta costo 101, rango suministrado 100 | Esperar costo 100; caso de igualdad en A4 sí avanza | FR-008–009 |
| T3 | Camino de 2 arcos costo 500 frente a 3 arcos costo 300, rango 300 | Primer paso del camino de 300; cobrar solo el arco usado | FR-008–009 |
| T4 | Primeros vecinos 7 y 3 con igual costo total mínimo | Elegir 3 pese a orden de enumeración; incluir convergencias y costo inmediato mayor del vecino óptimo | FR-010,014 |
| T5 | Decidir, cerrar puerta real entre turnos, volver a decidir | Igual a referencia desde cero; probar alternativa y ausencia de ruta | FR-013 |
| T6 | Costo 1, velocidad 1000, movimiento en t=20 | Posición cambia ahora, próxima acción t=21 | FR-002–003 |
| T7 | Costo 250, velocidad 100, próxima acción 250; cambio en t=50 a 200 | Próxima acción t=150, nueva secuencia, sin ejecución duplicada; repetir ralentización y final de efecto | FR-005–006 |

## Regresiones y escenarios adicionales

- A1–A2: ausencia de costo=100 y costo válido en ambos sentidos; todos los actores y demás costos inalterados. No probar política de datos inválidos hasta resolver Q1/Q2.
- A3–A5: mismo cuarto ataca; igualdad de rango avanza; resultado independiente de conocimiento y contenidos descargados. Contar cero llamadas de red desde búsqueda mediante contrato aprobado, no mock añadido unilateralmente.
- A6–A8: apertura puede mejorar ruta; jugador cambia objetivo; muchos caminos empatados/ciclos positivos; eventos simultáneos ordenados por secuencia. Dos ejecuciones con igual semilla/versiones/acciones producen mismos estados y llamadas al azar.
- A9–A11: activación inicial/costo 100 e IDs ordenados; precarga no activa; puerta no desplaza actor al cerrar; muerto no actúa; antídoto cancela pulsos; regeneración y cura limitadas; trampa inmediata y rearme; intervalos de efectos heredados.
- A12: undo y fallo transaccional restauran eventos/identidades/contador/reloj/azar, excluyen pergaminos e infraestructura de caché y descartan derivados de ruta. C/D acuerdan persistencia sin que A implemente su historia.
- A13: rastro fresco <400 y desempate menor ID; rastro por acción; guardián espera sin jugador. Preservar decisiones de errante/rastreador, cambiando solo costo temporal.
- Puertas: probar observar/abrir/cerrar desde ambos extremos, incluidos cierres automáticos y rollback. Primero acordar representación con B/C; no dar por demostrada coherencia existente.
- Comparar con referencia independiente (selección lineal o enumeración de caminos simples en mapas pequeños), sin bibliotecas de grafos ni compartir el mismo heap para validar su propia corrección.
- Contrato propuesto con C: distinguir llegada sin movimiento, ruta válida, ausencia demostrada y agotamiento del límite sin inferir existencia fuera de él. FUERA_LIMITE requiere evidencia exacta vigente. Probar SIN_LIMITE solo sobre salas exploradas y puertas recordadas abiertas; no equivale a usar el grafo real completo. Los nombres y firmas requieren acuerdo con C antes de implementar.

## Matriz de mediciones obligatorias de A

| Eje | Comparaciones | Evidencia requerida |
| --- | --- | --- |
| Cazadores | Uno frente a muchos (decenas); mismo objetivo | Tiempo por decisión y ciclo completo; número de búsquedas |
| Rango | Pequeño/grande; región local fija con mapa exterior creciente | Salas/arcos examinados, inicialización/limpieza e índices, tiempo y memoria |
| Estrategia | Individual/compartida; heap indexado/repetidos y referencia lineal | Construcción, hits, fallos, reconstrucción, operaciones de heap y resultados iguales |
| Validez y reutilización | Recalcular siempre/última consulta/varias entradas acotadas; consultas repetidas y alternadas; puertas estables/inestables | Aciertos y fallos por reemplazo/invalidez, memoria residente/pico, invalidaciones, búsquedas ahorradas y costo total de mantenimiento, incluidas aperturas fuera del camino |
| Agenda P1 con carga nueva | Heap perezoso/candidato indexado; empates, cancelaciones y velocidad | N físico/válido, obsoletos, memoria y latencia al descartar acumulaciones |
| Integración | Ciclo entre decisiones, no evento aislado | <20 ms, sin red/renderizado y referencia oficial cuando Q3 se resuelva |

Las alternativas adicionales de heap/grafo son experimentos de diseño propuestos; los ejes oficiales uno/muchos, rangos, individual/compartido, reutilización/recálculo y estabilidad son obligatorios. Ningún experimento compartido puede ocultar violación de localidad. Un campo parcial ausente no prueba falta de ruta.

La base propuesta es individual limitada. El cálculo compartido se mide separado y no se activa automáticamente en producción; no hay umbrales aprobados. Para cachés usar exactamente las mismas consultas y cambios de estado en cada diseño, declarar sus capacidades y presupuestos de memoria y contar búsqueda de claves, inserción, reemplazo, liberación e invalidación. La caché de última consulta puede perder casi todos los resultados con cazadores alternados: un mal resultado suyo no demuestra que la reutilización en general no convenga.

## Protocolo de medición futuro

Preparar datos fuera de la región cronometrada de consulta, reportando por separado costo de preparación y memoria residente. Incluir dentro de consultas sus propias asignaciones, inicialización, limpieza, invalidación y reconstrucción. Medir invalidación lógica y costo físico de liberar/reutilizar capacidad. No excluir selectivamente el trabajo que hace mala una alternativa.

Usar cargas deterministas por semilla, mismos datos/acciones para cada estrategia, calentamiento documentado, repeticiones y variación (mínimo, mediana y máximo; número de repeticiones registrado). Registrar equipo, versión Python, tamaño, grado, rango y H; estos son controles experimentales propuestos, no nuevos umbrales oficiales. El reloj de medición real no decide eventos del juego. Medir tiempo y memoria en pasadas separadas si la instrumentación perturba resultados.

Reportar tablas inicialmente como «pendiente», nunca con números simulados. Mantener <20 ms y condiciones oficiales; Q3 impide certificar con una cripta sintética como si fuera oficial. Q1/Q2 bloquean pruebas de políticas de entrada todavía indefinidas.

## Cierre documental posterior

### Evidencia real de fundamentos T005–T010 — 2026-11-05

Intérprete efectivo: Python 3.12.14 del runtime auxiliar de Codex, invocado mediante su ejecutable absoluto local. Comando reproducible desde raíz con ese intérprete como `python`:

```powershell
python -B -m unittest tests.test_grafo_terreno tests.test_heap_rutas -v
```

Los argumentos usados fueron exactamente los del comando anterior; se omite la ruta personal del ejecutable. Resultado real final: **13 pruebas aprobadas, 0 fallos, 0 errores; 0.013 s según unittest**. Esa duración es la de la suite, no un benchmark ni evidencia del presupuesto <20 ms. Las primeras ejecuciones de T007/T009 fallaron por importación de módulo/clases aún inexistentes (paso rojo esperado); después de T008 pasaron cinco pruebas de grafo y tras T010 pasaron las trece finales.

Cobertura: índices densos y adyacencias para IDs dispersos; costo ausente 100 y explícito positivo simétrico; conservación de referencias y de la entrada; grafos vacío/aislado/cadenas; heap por distancia/primerID/ID de sala, mejoras por distancia y por primerID, sin duplicados; posiciones tras intercambios/extracciones; etiquetas/cierre/posiciones invalidados por generación sin cambiar arreglos residentes; finalización de frontera; dos secuencias de 700 operaciones (semillas 17/20261105) contra referencia lineal independiente.

Contrato interno implementado en modelo/rutas.py: `GrafoTerreno(salas)` recibe objetos Sala válidos del contrato existente, expone `ids`, `adyacencias` y `indice(id)`; cada ArcoTerreno conserva índices origen/destino, dirección, costo y referencia `puerta` al descriptor original. No es una nueva interfaz aprobada con B/C. No validar datos inconsistentes ni generar conexiones inversas. `EspacioBusqueda(ids)` conserva etiquetas/cierre/posiciones por generación; `HeapRutas(espacio)` ofrece iniciar, insertar_o_disminuir, extraer y finalizar. Cada espacio pertenece a una frontera; las etiquetas se consultan solo por métodos vigentes, nunca leyendo arreglos obsoletos. `None` como primerID es marcador interno de origen, no un rango/costo null ni un ID de juego inventado. Extraer no cierra automáticamente el nodo. Iniciar exige frontera vacía; finalizar descarta solo pendientes F en O(F), imputados a la consulta saliente, sin recorrer los V auxiliares.

La inspección de nuevas fuentes no encontró índices hash, sort/sorted, heapq, bisect, collections ni bibliotecas de grafos. Se reutilizan diccionarios solo como descriptores de entrada JSON de Sala; se construyen índices y heaps con listas propias. No se ejecutaron regresiones existentes, consultas HTTP, benchmarks ni acciones de juego. Se conserva el comportamiento del juego al no importar ni conectar este módulo desde el motor. T011–T051 no se ejecutan; Q1–Q3 y contratos externos siguen pendientes, checklist sin cambios. No hay hooks de implementación porque .specify/extensions.yml no existe.

Publicar resultados finales y límites en DECISIONES.md solo con autorización, enlazando spec/plan y explicando cambios de preferencia motivados por medición. Registrar prompts íntegros en la bitácora compartida posteriormente. Esta guía no crea tareas ni autoriza ejecución o modificación de módulos ajenos.

## Pruebas preparadas T011/T012 — 2026-11-05

Autorización posterior exclusiva para tests/test_costos_terreno.py, tests/test_velocidad_terreno.py, ampliación del fixture propio y registro documental. T006/T010 satisfechas; checklist sigue 13/16 sin editar. Los archivos locales de fundamentos no estaban confirmados y se conservan. No se modifican modelo/rutas.py, juego.py, eventos.py ni efectos.py. No se ejecuta T013 ni tareas posteriores.

El fixture motor_terreno reutiliza ServidorFalso de tests/datos_prueba.py sin sustituir sus métodos, AlmacenLocal temporal, GestorCatalogo/Precarga y Motor reales. Incorpora cuatro salas sintéticas y parametriza solo costos positivos simétricos, velocidades positivas y reloj inicial. No crea dobles nuevos ni hace HTTP real. El contexto cierra la precarga antes de limpiar el directorio temporal. Para distinguir causas, las pruebas de velocidad aisladas llaman _avanzar_actor con costo explícito; las integradas parten de mover, conservando el requisito real aunque falle. Los asserts de costos ausentes y acciones no móviles verifican el comportamiento actual sin ajustarlo al costo fijo.

Comando reproducible con Python 3.12.14 (se utilizó el ejecutable absoluto del runtime auxiliar de Codex, omitiendo aquí su ruta personal):

```powershell
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas -v
```

| Suite | Pruebas | Aprobadas | Fallos | Errores |
| --- | --- | --- | --- | --- |
| test_costos_terreno | 12 | 5 | 7 | 0 |
| test_velocidad_terreno | 7 | 4 | 3 | 0 |
| test_grafo_terreno + test_heap_rutas | 13 | 13 | 0 | 0 |
| Total | 32 | 22 | 10 | 0 |

Resultado final real: `FAILED (failures=10)`, salida 1, duración unittest 0.830 s. No se usa expectedFailure ni skip para esconder los criterios pendientes. El primer intento aislado produjo errores de permisos al escribir/limpiar temporales; tras autorización se repitió fuera del aislamiento. Esos errores ambientales no son defectos del producto ni forman parte del resultado final anterior. No se afirma rendimiento del motor con la duración de la suite.

Fallos de costos: jugador/errante/rastreador programan 100 en vez de 250 (tres pruebas); con costo 1, velocidad 1000 y t=20 programan t=30 en vez de t=21 (tres); ambos sentidos pagan 100 en vez de 250 (una). Corresponden a integración aún ausente en T013/T014. Pasan costo ausente=100 para los tres actores, fórmula de intervalo y costos heredados de atacar/esperar=100, usar/equipar/abrir=50 y recoger/soltar=25.

Velocidad: pasan aceleración aislada en t=50 de pendiente 250 a 150 (jugador y enemigo), ralentización a 450, mínimo 1 y fin de efecto en t=75 que lleva pendiente 150 a 225. Comprueban cancelación anterior, referencia/tipo, nueva secuencia, una sola ocurrencia vigente y descarte de eventos cancelados. Las tres variantes integradas de T7 (aceleración, ralentización y fin de efecto) fallan en la precondición de movimiento: pendiente inicial 100 en vez de 250. Sus verificaciones posteriores quedan listas pero todavía no acreditadas en ese contexto. No hay evidencia actual que justifique cambiar la fórmula existente en T015.

T011/T012 permanecen sin marcar, con pruebas listas y aceptación pendiente. Fundamentos mantienen 13 pruebas aprobadas; no se observaron regresiones en esas estructuras. No se ejecutan otras suites ni benchmarks, no se cierran Q1–Q3 ni acuerdos externos, y no se hace commit o integración. No existe .specify/extensions.yml para hooks de implementación.

## Corrección de pruebas tras auditoría — 2026-11-05

Se consultaron los PDF oficiales locales: Parte I §§2.3–2.5 (pp. 4–6: turnos, fórmula, nueva secuencia, activación y espera hasta próxima decisión), §2.8 y Apéndice B; Parte II §3.1 (p. 4) y Apéndice B (p. 12: costo por salida para todos los actores y casos T6/T7). Se releyeron constitución, spec/plan/tasks y los métodos del motor. No se cambian esas reglas, Q1/Q2 ni el requisito de rendimiento Q3. La evidencia de 32 pruebas anterior es histórica: la auditoría detectó tres defectos de construcción/cobertura que se corrigen aquí, sin alterar el motor.

1. **Fixture previo al motor:** crear_paquete existente genera el conjunto sintético; se parametrizan generales, ficha de enemigo y páginas en AlmacenLocal temporal, antes de crear_juego con ClienteOffline real. No hay nuevos mocks. Copias de motor, precarga y almacenamiento conservan costos/puertas coherentes; velocidad y comportamiento ya son definitivos cuando se activa el enemigo. _puertas_iniciales se captura con las puertas configuradas. Se agrega una prueba específica de esos invariantes, sin ejecutar restauración.
2. **Reciprocidad:** dos llamadas a ejecutar("mover", ...) procesan sus intervalos completos. Se comprueba que cada frontera deja al jugador sin evento pendiente, se registran dos acciones y se comparan incrementos del reloj con 250 por sentido. Ya no se cancela prematuramente la espera del primer movimiento.
3. **Enemigos:** se elimina la asignación de posición/comportamiento/velocidad sobre el estado activo y la llamada directa a _ejecutar_turno_enemigo. El jugador sale por una acción real y la agenda procesa el turno capturado, que debe salir de cola sin estar cancelado. Para costo 250 el turno de movimiento llega en t=100: siguiente esperado 350, observado 200; se conserva el intervalo exigido 250. Para T6 los actores rápidos esperan/atacan legalmente en t=10; el jugador sale entonces, y el enemigo se mueve cuando llega su turno en t=20. Si hace falta se usa otra acción esperar del jugador, sin saltar eventos. El siguiente instante esperado sigue siendo 21 y el observado es 30. Para el jugador se llega a t=20 con dos esperas reales antes de observar una única llamada local a mover en una frontera válida.
4. **Cola frente a semántica:** test_cola_descarta_cancelado_sin_afirmar_acciones_del_motor usa ColaEventos independiente y solo prueba extracción/cancelación. Ninguna prueba vacía la cola del motor omitiendo sus acciones para anunciar ejecución única. test_motor_procesa_un_solo_ataque_tras_reprogramar prepara un efecto sintético: enemigo con velocidad base 200, reducción mediante cambiar_velocidad a 100 en t=0, y restauración en t=50. ejecutar("esperar") procesa el fin en t=50, el ataque en t=75 y la decisión del jugador en t=100. Se comprueban daño de exactamente un ataque, estado del azar tras una sola tirada, descarte del turno antiguo de t=100, siguiente turno enemigo en t=125, unicidad del pendiente y limpieza del pendiente del jugador. No se afirma cobertura de uso de poción/inventario ni de todos los tipos de efectos.
5. **Límite unitario explícito:** los casos aislados y T7 parciales que colocan reloj=50 se declaran snapshots artificiales para evaluar la fórmula. Antes de hacerlo exigen que no exista ningún evento vigente con tiempo ≤50. No se presentan como historia reproducida ni como ciclo integrado completo. Las variantes se llaman test_t7_parcial_*. Conservar la precondición de movimiento de costo 250 mantiene sus tres fallos actuales; las comprobaciones posteriores todavía no acreditan T7 completo.

Mismo comando de cuatro suites del apartado anterior, con Python 3.12.14 y -B, ejecutado con acceso autorizado a temporales:

| Suite corregida | Pruebas | Aprobadas | Fallos | Errores |
| --- | --- | --- | --- | --- |
| test_costos_terreno | 13 | 6 | 7 | 0 |
| test_velocidad_terreno | 9 | 6 | 3 | 0 |
| Fundamentos | 13 | 13 | 0 | 0 |
| Total vigente | 35 | 25 | 10 | 0 |

Ejecución final de esa corrección: `FAILED (failures=10)`, salida 1, 1.440 s según unittest (no benchmark). Permanecen siete fallos de costo de movimiento —jugador, errante, rastreador, mínimo y reciprocidad— y tres precondiciones rojas de T7 parcial; no se rebajan expectativas ni se usan skips/expectedFailure. Los controles nuevos de agenda, fixture y ejecución única pasan. No se observaron defectos independientes en esos controles ni regresiones de fundamentos. T011/T012 siguen pendientes y ningún archivo de producción se modifica en esa corrección.

## Implementación limitada de T013 — 2026-11-05

Autorización posterior exclusiva del movimiento del jugador en modelo/juego.py, con datos válidos y pruebas existentes intactas. Se releyeron constitución, documentación de la funcionalidad, contratos y las reglas oficiales: Parte II §3.1 sustituye el costo fijo de movimiento por costo de salida entero ≥1, o 100 si el campo falta; Parte I §§2.3 y 2.5 conserva fórmula, posición inmediata y procesamiento de eventos hasta la próxima decisión. FR-001/002/003 respaldan el cambio; FR-004/016 requieren conservar otras acciones y activación. No se equipara null a ausencia, no se normaliza asimetría y no se añade política de invalidez.

En Motor.mover se captura costo_salida desde la salida de origen, antes de modificar posición, y se entrega a _avanzar_actor. No cambian calcular_intervalo, cambiar_velocidad, el orden de carga/deltas/activación/rastro/trampas ni _ejecutar_turno_enemigo. No se añaden estructuras o dependencias. E-B-COSTOS sigue sin entrega acreditada: esta evidencia usa exclusivamente el paquete sintético válido del fixture existente. No certifica entrada HTTP ni validación/precarga de B.

Comando de suites autorizadas (PowerShell, Python 3.12.14, -B, acceso autorizado a temporales):

```powershell
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas -v
```

| Suite tras T013 | Pruebas | Aprobadas | Fallos | Errores |
| --- | --- | --- | --- | --- |
| test_costos_terreno | 13 | 9 | 4 | 0 |
| test_velocidad_terreno | 9 | 9 | 0 | 0 |
| Fundamentos (grafo y heap) | 13 | 13 | 0 | 0 |
| Total | 35 | 31 | 4 | 0 |

Resultado real: `FAILED (failures=4)`, salida 1, 4.283 s reportados por unittest; no es medición de rendimiento. Pasan costo ausente 100, costo declarado 250, costo 1 con mínimo 1 desde t=20, reciprocidad con dos decisiones completas, posición inmediata y conservación de otros costos. Pasan las tres variantes parciales T7 (150, 450 y 225), las pruebas aisladas de reprogramación, la cola y el ataque único. Los snapshots parciales no prueban un ciclo completo con uso de poción ni permiten cerrar T7 integral o T015.

Fallos restantes, sin cambiar expectativas:

- test_errante_costo_250 y test_rastreador_costo_250: próximo instante observado 300, esperado 350. El jugador ahora espera legalmente hasta t=250; el enemigo se mueve en t=100 con costo fijo 100 y vuelve a atacar en t=200, dejando pendiente t=300. Con costo correcto 250, su próximo turno sería t=350 y ese ataque anticipado no ocurriría. Es una consecuencia observable de T014 pendiente, no un nuevo valor esperado.
- test_errante_minimo_uno_en_t20 y test_rastreador_minimo_uno_en_t20: observado 30, esperado 21. El movimiento enemigo en t=20 sigue usando 100 a velocidad 1000; T014 debe usar costo 1. No se modifica ese código.

Regresiones existentes, ejecutadas antes y después del cambio:

```powershell
python -B -m unittest tests.test_juego tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

53/53 aprobadas, cero fallos/errores y salida 0 en ambas ejecuciones (0.662 s antes, 0.605 s después según unittest). Cubren movimiento/rechazo, revisitas, puertas/llaves, activación al entrar/retroceso, rastro, azar, efectos, agenda y continuidad de guardado/restauración existentes, además de precarga anticipada fallida sin romper movimiento/replay. Son regresiones de comportamiento anterior con costo ausente, no prueba de historia/persistencia con costos nuevos ni certificación Q3. No se modifica ninguna suite ni dependencia.

T013 queda implementada y verificada en el alcance local válido autorizado, conservando casilla pendiente por E-B-COSTOS para el cierre integrado. T011/T012 no se marcan completas y T014–T051 no se implementan. Q1–Q3 y acuerdos externos siguen pendientes. No se ejecutan benchmarks ni operaciones Git de escritura. Solo se modifican Motor.mover y documentación propia (este registro, tasks.md y la entrada P24 del registro local); PROMPTS_LLM.md permanece intacto.

## Implementación limitada de T014 — 2026-11-06

Etapa posterior autorizada exclusivamente para datos válidos en la rama de movimiento de Motor._ejecutar_turno_enemigo. Se releen constitución, spec/plan/tasks, contratos, pruebas/fixture y reglas oficiales relevantes: Parte II §3.1 aplica costo de salida a todos los actores, mantiene las decisiones de errantes/rastreadores y los demás costos; Parte I §§2.3–2.5 conserva fórmula, agenda y primera activación con costo 100. T014 atiende FR-002/003/011/016 sin implementar cazador ni validación de entradas de B.

Cambio de producción limitado: salida = sala_actual.salidas[direccion], nuevo_id = salida["sala"], costo_salida = salida.get("costo", 100); esa lectura ocurre antes de extraer/cambiar posición del enemigo. Al terminar el movimiento se pasa costo_salida a _avanzar_actor. La decisión ya fue recibida del mismo callback existente; no se altera su firma, consumo de azar, elección de dirección, rastro, puertas, traslado entre listas ni registro reversible existente. No cambian calcular_intervalo, cambiar_velocidad, ataques, esperas ni activar_enemigos_de_sala. No se añaden estructuras/dependencias ni políticas sobre null/asimetría/invalidez.

Comandos reales (Python 3.12.14, -B, acceso autorizado a temporales; sin red real):

```powershell
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas -v
python -B -m unittest tests.test_juego tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

| Suite tras T014 | Pruebas | Aprobadas | Fallos | Errores |
| --- | --- | --- | --- | --- |
| test_costos_terreno | 13 | 13 | 0 | 0 |
| test_velocidad_terreno | 9 | 9 | 0 | 0 |
| test_grafo_terreno | 5 | 5 | 0 | 0 |
| test_heap_rutas | 8 | 8 | 0 | 0 |
| Cuatro suites | 35 | 35 | 0 | 0 |
| Regresiones seleccionadas previamente | 53 | 53 | 0 | 0 |

Ambas ejecuciones terminan en OK y salida 0: 35 pruebas en 1.385 s y 53 en 0.492 s según unittest. Esos tiempos son duración de suites, no benchmarks ni evidencia de cumplimiento de Q3. Los cuatro fallos previos de errante/rastreador desaparecen con expectativas intactas: costo 250 desde t=100 deja pendiente t=350; costo 1 a velocidad 1000 desde t=20 deja pendiente t=21. También pasan costo ausente 100, costos restantes, reciprocidad del jugador y las variantes parciales de T7. No aparecen regresiones nuevas en las 53 pruebas existentes de movimiento, revisitas, efectos, agenda, rastro, azar, puertas/llaves, retroceso y continuidad de estado; su cobertura y límites siguen siendo los indicados en T013.

**Activación inicial conservada:** activar_enemigos_de_sala continúa llamando _avanzar_actor(enemigo, _COSTO_ATACAR), cuya constante es 100; el orden por ID se mantiene. test_fixture_prepara_datos_y_agenda_antes_de_crear_el_motor verifica con terreno 250, enemigo de velocidad 500 y reloj 0 un primer turno en t=20, no t=50. Los casos de errante/rastreador con terreno 250 y velocidad 100 verifican el turno inicial t=100 antes de procesarlo. Esto respalda costo de activación 100 distinto del costo de movimiento, sin afirmar cobertura exhaustiva nueva de todas las activaciones simultáneas.

T014 está implementada y verificada para datos válidos en el alcance autorizado; su casilla conserva pendiente el cierre integrado E-B-COSTOS. No se acredita entrega de B, no se resuelven Q1/Q2 ni se certifica rendimiento Q3. T7 sigue parcial y no se ejecuta T015 ni ninguna tarea posterior. No se editan pruebas, fixtures, rutas.py, enemigos.py, eventos.py, efectos.py, tipos.py, constitución, interfaz, historia/persistencia ni archivos de compañeros. Solo se actualizan la rama de movimiento enemigo de juego.py y estos documentos propios: quickstart.md, tasks.md y prompts-registro-local.md (P25). PROMPTS_LLM.md sigue pendiente de traslado autorizado. No se realizan operaciones Git de escritura, integración ni publicación.

## Verificación de T015 sin cambios de producción — 2026-11-06

Alcance posterior autorizado: revisar diff T013/T014, verificar reprogramación existente y regresiones, registrar límites de T7. Se consultaron constitución, spec/plan/tasks, reglas de Parte I §§2.3 y 2.10, Parte II §3.1 y Apéndice B, cambiar_velocidad, _avanzar_actor, ejecutar_ciclo y pruebas existentes. Checklist 13/16, con Q1–Q3 abiertas; la autorización específica de verificación no resuelve esas preguntas ni aprueba contratos externos. Sin hooks: .specify/extensions.yml no existe antes ni después.

### Diff completo de juego.py revisado frente a HEAD

Los cuatro hunks siguientes incluyen todas las líneas eliminadas y agregadas. T013 aporta captura del costo y sustitución del argumento para el jugador. T014 separa la lectura existente del destino mediante la referencia salida, captura el costo y sustituye el argumento del enemigo. Balance: tres líneas eliminadas y seis agregadas; la lectura de destino se conserva semánticamente. No hay otras modificaciones de juego.py frente a HEAD.

```diff
@@ -197,6 +197,7 @@ class Motor:

         salida = self.salas[self.jugador.posicion_actual].salidas[direccion]
         id_destino = salida["sala"]
+        costo_salida = salida.get("costo", 100)

         if not self.contenido_cargado[id_destino]:
             sala_preparada = self.gestor_precarga.preparar_entrada(id_destino, self._ids_en_uso(id_destino))
@@ -219,7 +220,7 @@ class Motor:
         self.historial.registrar_inventario(lambda p=pos_anterior: setattr(self.jugador, "posicion_actual", p))
         self.jugador.posicion_actual = id_destino
         self._sincronizar_referencias()
-        self._avanzar_actor(self.jugador, _COSTO_MOVER)
+        self._avanzar_actor(self.jugador, costo_salida)
         self.historial.registrar_rastro(id_destino, self.registro_rastro.tiempo_de(id_destino))
         self.registro_rastro.marcar_visita(id_destino, self.reloj)

@@ -353,7 +354,9 @@ class Motor:
             self.atacar(enemigo, self.jugador)
         elif accion == "mover":
             direccion = dato
-            nuevo_id = sala_actual.salidas[direccion]["sala"]
+            salida = sala_actual.salidas[direccion]
+            nuevo_id = salida["sala"]
+            costo_salida = salida.get("costo", 100)
             lista_origen = self.enemigos_por_sala[id_sala]
             lista_destino = self.enemigos_por_sala[nuevo_id]
             indice = lista_origen.extraer(enemigo)
@@ -364,7 +367,7 @@ class Motor:
                     ld.extraer(e), lo.restaurar(e, i), setattr(e, "sala_actual", s)
                 )
             )
-            self._avanzar_actor(enemigo, _COSTO_MOVER)
+            self._avanzar_actor(enemigo, costo_salida)
         else:
             self._avanzar_actor(enemigo, _COSTO_ESPERAR)
```

No se eliminan activación inicial/orden por ID, ataques, esperas, puertas, rastro, carga previa, agenda, efectos ni llamadas al azar. Se conserva el código de estas reglas; las regresiones aportan evidencia dentro de sus escenarios, no demostración exhaustiva de todo el juego. No se modifican funciones de producción para esta verificación.

### Fórmula y evidencias de reprogramación

cambiar_velocidad captura evento/velocidad anteriores, conserva restante = max(1, (evento_viejo.tiempo - reloj) * velocidad_anterior // velocidad_nueva), cancela el anterior y programa uno nuevo del mismo tipo/referencia. programar_evento usa insertar de ColaEventos, que asigna secuencia creciente. extraer_minimo descarta cancelados; ejecutar_ciclo procesa restaurar_velocidad limpiando evento_velocidad y llamando a cambiar_velocidad. _avanzar_actor conserva calcular_intervalo(costo, velocidad), cuyo mínimo es 1. No se detectó discrepancia para entradas válidas en el alcance probado; no se propone cambio ni política de invalidez.

Comandos de esta verificación (Python 3.12.14, -B, acceso autorizado a temporales, sin modificar dependencias):

```powershell
python -B -m unittest tests.test_velocidad_terreno -v
python -B -m unittest tests.test_juego tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

Resultado real: velocidad 9/9 en 0.439 s, regresiones 53/53 en 0.414 s, ambos OK/salida 0, cero fallos y errores. Son 62 pruebas ejecutadas en esta etapa; los 35/35 de cuatro suites de T014 son evidencia histórica, no una nueva ejecución aquí. No se ejecutan benchmarks ni se afirma rendimiento.

| Cobertura actual en test_velocidad_terreno | Evidencia y límite |
| --- | --- |
| Aceleración aislada jugador/enemigo | Pendiente 250, snapshot t=50, velocidad 200: próximo 150. |
| Ralentización aislada | Mismo pendiente/snapshot, velocidad 50: próximo 450. |
| Intervalo mínimo | Reprogramación de una unidad conserva mínimo 1. |
| Fin del efecto | Después de acelerar en snapshot t=50, restaurar_velocidad se procesa realmente en t=75: próximo 225. |
| Cancelación/nueva secuencia | Helper comprueba anterior cancelado, nuevo objeto/tipo/referencia, secuencia mayor y único pendiente vigente. |
| Descarte de cola | Cola independiente extrae solo sustituto; no se presenta como acción ejecutada del motor. |
| Ejecución semántica única | Motor procesa restauración t=50, ataque t=75, decisión jugador t=100; vida y estado del azar equivalen a un ataque, turno antiguo cancelado fuera de cola y siguiente enemigo t=125. Escenario separado del movimiento costoso. |
| Tres variantes T7 parciales | Movimiento real costo 250 y snapshot posterior; verifican 150/450/225. No son cronologías completas. |

### Qué falta para T7 integral

Falta una prueba o log reproducible que una en la misma cronología: movimiento real de costo 250 desde t=0; cambio de velocidad en t=50 procesado como evento ordinario (sin asignación manual de reloj); siguiente turno en t=150 con nueva secuencia; y procesamiento posterior suficiente para comprobar acciones reales y que el turno sustituido de t=250 no produce otra acción. En la variante de ralentización, el antiguo t=250 debe quedar descartado antes del turno nuevo t=450; en fin de efecto, procesar restauración t=75 y turno t=225, con cancelación de ambos pendientes sustituidos. La comprobación debe contar acciones semánticas, no solo extracciones o igualdad de pendientes. No es necesario inventar una nueva mecánica de efectos: la preparación debe usar las reglas/eventos existentes y documentar cualquier efecto sintético de prueba.

Los casos actuales con snapshots no aportan ese recorrido completo, y la prueba de ataque único no lo sustituye al ser otro escenario. No se añade ninguna prueba/fixture en esta etapa, no se exige ni se inventa permiso de acción del jugador durante su intervalo, y no se declara un defecto de producción por esta ausencia de cobertura. La ampliación de cobertura queda pendiente de autorización de pruebas; no se ejecuta T016 ni tareas posteriores.

**Conclusión:** T015 verificada sin necesidad de cambio dentro del alcance probado. Casilla pendiente por cierre de prerrequisitos T012/T014 y cobertura integral aún no acreditada, sin afirmar Q1–Q3 ni entregas externas resueltas. Únicas modificaciones de esta etapa: quickstart.md, tasks.md y prompts-registro-local.md (P26). Se conservan intactos código de producción, pruebas/fixtures y archivos compartidos. PROMPTS_LLM.md no cambia. La rama sigue feature/motor-eventos y no se realizan operaciones Git de escritura.

## Cobertura integrada de T7 — 2026-11-06

Autorización posterior exclusiva para pruebas T7 y documentación propia. Se revisaron constitución, Parte I §2.3, Parte II §3.1/Apéndice B, spec/plan/tasks/quickstart y métodos del motor. Checklist conserva 13/16, con Q1–Q3 abiertas; la autorización no las resuelve. Se amplía solo tests/test_velocidad_terreno.py, sin editar pruebas previas ni fixture. No se modifican producción, contratos, historial o persistencia.

### Viabilidad y preparación válida

El único evento existente que cambia velocidad al despacharse es restaurar_velocidad. ejecutar_ciclo lo procesa limpiando evento_velocidad y llamando a cambiar_velocidad con la base de su referencia. Por tanto, se prueba el vencimiento de un efecto temporal cuya velocidad base coincide con la configuración del fixture. En t=0 se prepara mediante cambiar_velocidad el estado temporal y se programa su vencimiento en t=50, guardándolo en evento_velocidad. No se añade un tipo aplicar_velocidad ni se usa restaurar_velocidad como una orden arbitraria para iniciar/superponer efectos.

| Prueba nueva | Base del fixture / temporal durante movimiento | Pendiente inicial | Evento real en t=50 | Nuevo turno |
| --- | --- | --- | --- | --- |
| test_t7_integrado_aceleracion_por_fin_de_ralentizacion | 200 / 100 | 250 | restaurar_velocidad a 200 | 150 |
| test_t7_integrado_ralentizacion_por_fin_de_aceleracion | 50 / 100 | 250 | restaurar_velocidad a 50 | 450 |
| test_t7_integrado_fin_de_efecto_restaura_velocidad_base | 100 / 200 | 125 | restaurar_velocidad a 100 | 200 |

Las dos primeras cumplen movimiento a velocidad 100 en t=0 y pendiente t=250; la tercera usa aceleración temporal desde t=0 y calcula 50 + (125−50)×200//100 = 200. El caso de 250→150→225 permanece como prueba parcial anterior: la nueva cobertura de fin de efecto no afirma esa cadena exacta. El enunciado exige escalar el restante, no fija ese ejemplo como única variante de terminación. Introducir una aplicación diferida o efectos superpuestos para forzarla requeriría un mecanismo/contrato adicional, que no se incorpora.

### Cronología y evidencia semántica

El helper comprobar_t7_integrado usa motor_terreno existente con costo 250 y guardianes de velocidad 25 configurados antes de activarlos. Son datos sintéticos válidos; sus turnos iniciales t=400 dejan observar el vencimiento t=50 sin anticipar acciones enemigas. No se cambian posiciones/velocidades de enemigos activos ni puertas. El efecto temporal inicial se prepara sin avance de reloj y antes del movimiento, no se presenta como una acción de usar poción.

Se ejecuta una única llamada a mover("E") en la frontera inicial t=0 para observar posición inmediata y pendiente original. Es la acción real local del motor; no se presenta como una transacción ejecutar ni como prueba de historial. Desde allí se llama exclusivamente ejecutar_ciclo(decidir_accion) hasta recibir el nuevo turno del jugador, respetando todos los eventos intermedios. Ningún caso escribe reloj ni llama acciones del jugador mientras su turno está pendiente. La aserción de cancelación verifica identidad, tipo, referencia, nueva secuencia mayor que el evento anterior y que el vencimiento, único pendiente vigente y descarte perezoso del original.

Una vez recibido el turno real (t=150/450/200), ejecutar("atacar", id) produce un único daño al guardián de destino y exactamente una tirada del azar clonado como referencia. Su vida inicial debe ser mayor que el daño para evitar que la muerte oculte una duplicación. El reloj al regresar debe ser 200/650/300, respectivamente. Después se llama legalmente ejecutar("mover", "E") y se exige retorno en 325/1150/550, todos posteriores al tiempo cancelado. Se verifica posición 102, daño sin incremento en el objetivo anterior, evento antiguo cancelado y ya fuera de cola, y ningún turno vigente del jugador. Un turno antiguo que reapareciera interrumpiría ejecutar antes del instante esperado. La ralentización consume y descarta t=250 antes de recibir t=450; la aceleración continúa más allá de t=250 tras haber actuado en t=150.

El contador acciones_jugador registra dos acciones por ejecutar (ataque y movimiento posterior); mover local inicial no lo incrementa. Esto se declara expresamente, sin confundir ese contador con tres transacciones. La unicidad se acredita combinando llegada del turno, instantes de retorno, vida del objetivo, estado del azar y ausencia de pendientes, no solo extracciones de cola. Los guardianes conservan su comportamiento real; no hay callbacks/mocks nuevos.

### Ejecuciones reales

```powershell
python -B -m unittest tests.test_velocidad_terreno tests.test_costos_terreno tests.test_grafo_terreno tests.test_heap_rutas -v
python -B -m unittest tests.test_juego tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

Python 3.12.14, -B, acceso autorizado a temporales, sin red real. Cuatro suites: 38/38 (velocidad 12, costos 13, grafo 5, heap 8), 1.794 s según unittest, OK/salida 0. Regresiones seleccionadas: 53/53, 0.547 s, OK/salida 0. Cero fallos/errores; pruebas anteriores intactas. Tiempos de suites, no benchmarks ni certificación de Q3.

**Estado y límites:** se completa T012 por cobertura del escenario principal T7 y variantes válidas del jugador con agenda real. No se afirma cobertura integral del encadenamiento particular 250→150→225, activación de efectos durante un intervalo por una mecánica nueva, adquisición/uso de poción, historial/replay ni una cronología equivalente de movimiento enemigo; esas extensiones no se prueban aquí. La prueba aislada de aceleración de enemigo y sus pruebas de costo conservan su alcance previo. No se necesita cambiar producción para los casos implementados. T015 continúa verificada sin ajustes y pendiente de cierre formal de T014/E-B-COSTOS; completar T012 no resuelve acuerdos de B/C/D ni Q1–Q3. No se ejecutan T016 ni tareas posteriores ni operaciones Git de escritura. Registro del prompt actual P27, sin tocar PROMPTS_LLM.md.

## Verificación limitada de T016 — 2026-11-06

Se revisaron constitución, enunciados oficiales Parte I §§2.3–2.6 y Parte II §3.1, spec/plan/tasks, fixture y código actual. Checklist conserva 13/16 por Q1–Q3; la autorización específica de pruebas no acredita respuestas o contratos externos. Se reutiliza motor_terreno real, sin modificarlo ni introducir mocks o nuevos comportamientos. No se modifica producción ni los resultados esperados existentes.

**Cobertura ya existente, conservada sin duplicación:** test_demas_acciones_conservan_costos_de_parte_i ejecuta las siete acciones con terreno 250 y jugador de velocidad 100: atacar/esperar=100, usar/equipar/abrir=50, recoger/soltar=25, comprobando reloj y tiempo_siguiente. test_jugador_costo_ausente_100, test_jugador_costo_250 y test_jugador_minimo_uno_en_t20 comprueban posición inmediata, vida conservada en la llamada local y pendiente esperado. test_movimiento_reciproco_costo_250 usa dos decisiones completas; los casos de errante/rastreador, fórmula y fixture conservan su alcance. No fue necesario ampliar el fixture ni crear otra tabla de costos idéntica.

**Única prueba nueva:** test_movimiento_sin_ataques_gratuitos_respeta_agenda_y_empates. Se justifica porque la igualdad de vida inmediatamente después de mover no demuestra por sí sola que el intervalo posterior carezca de ataques adicionales o consumo extra del azar. Usa dos variantes de la misma situación, con guardianes reales y sus velocidades originales:

- Costo 250: mover una vez en t=0 deja al jugador en destino y pendiente t=250. Conserva el evento inicial del guardián de origen; activa el del destino en t=100, sin daño ni tirada de azar al salir/entrar. ejecutar_ciclo procesa exactamente origen100 (espera), destino100 (ataque), origen200 (espera), destino200 (ataque), jugador250. Después de cada evento se comprueban referencia, tiempo, secuencia en empates, vida de todos los actores, posición, estado completo del azar y siguiente evento enemigo con intervalo 100. El daño acumulado coincide únicamente con dos tiradas del guardián de destino.
- Costo 100: en t=100 el orden es origen, jugador, destino, según secuencias asignadas. Hasta recuperar la decisión no hay daño ni azar consumido; el turno del destino sigue pendiente, sin cancelar ni adelantarlo. Solo entonces ejecutar("esperar") procesa el ataque de destino en t=100 y el origen en t=200, devuelve la decisión en t=200 y deja al destino pendiente en ese mismo instante por su secuencia posterior. Vida/azar coinciden con un único ataque. No se afirma que los eventos empatados sean simultáneos ni que el destino deba atacar antes del jugador.

La llamada inicial mover es local y se efectúa en la frontera t=0; permite observar el estado inmediato sin consumir el intervalo. La espera posterior usa ejecutar únicamente tras recibir el turno. No se escribe reloj, no se asigna posición y no se vacía ni reordena la cola manualmente. Las comprobaciones de azar clonan Random con el estado actual: no cambian el generador del motor. El alcance no añade pruebas de historia, persistencia o coherencia bidireccional de puertas.

Comandos reales autorizados (Python 3.12.14, -B, acceso a temporales, sin red real):

```powershell
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas -v
python -B -m unittest tests.test_juego tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

| Ejecución T016 | Aprobadas | Fallos | Errores |
| --- | --- | --- | --- |
| Costos | 14/14 | 0 | 0 |
| Velocidad | 12/12 | 0 | 0 |
| Fundamentos (5 grafo + 8 heap) | 13/13 | 0 | 0 |
| Cuatro suites | 39/39 | 0 | 0 |
| Regresiones previamente seleccionadas | 53/53 | 0 | 0 |

Unittest reporta 1.660 s y 0.495 s, respectivamente, ambos OK/salida 0. Son tiempos de suites, no benchmarks ni certificación Q3. La prueba nueva cuenta como un método con dos subcasos. No hay fallos que ocultar, skips ni expectativas rebajadas.

**Pendientes de US1:** T016 verificada localmente con evidencia; se conserva su casilla pendiente porque T014/T015 todavía no tienen cierre formal. T013/T014 tienen implementación válida y T015 verificación sin ajustes, pero no se acredita E-B-COSTOS; T011 conserva su cierre pendiente de consolidación y condiciones de datos aunque sus 14 pruebas actuales pasan. T012 está completada para sus escenarios válidos. T017 requiere autorización posterior y su ejecución específica incluyendo tests.test_enemigos, no ejecutada en esta etapa; repetir suites bajo T016 no completa T017. T018 espera evidencia Q1/Q2 y prerrequisitos. Q3 y contratos externos siguen pendientes, sin cambiar el comportamiento para entradas null/inconsistentes. No se ejecutan T017 ni tareas posteriores ni operaciones Git de escritura. Solo se modifican test_costos_terreno.py y documentación propia: este registro, tasks.md y prompts-registro-local.md (P28); PROMPTS_LLM.md permanece intacto. No hay .specify/extensions.yml al comprobar hooks.

## Verificación conjunta de US1 — T017 — 2026-11-06

Etapa autorizada exclusivamente de verificación: constitución, enunciados Parte I/II y documentación vigente de la funcionalidad revisados antes de ejecutar. Se mantienen condiciones oficiales de costos, fórmula, activación y secuencias; checklist 13/16, Q1–Q3 abiertas. La autorización de esta corrida con datos válidos no equivale a cerrar aclaraciones ni contratos externos. No se modifica código de producción, pruebas o fixtures. Sin hooks antes/después: no existe .specify/extensions.yml.

### Ejecución única y resultado actual

```powershell
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas tests.test_juego tests.test_enemigos tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay -v
```

Python 3.12.14, acceso autorizado a temporales, sin red real. Resultado real: 99 pruebas en 1.888 s según unittest, OK/salida 0; 99 aprobadas, cero fallos, errores, skips, expected failures o unexpected successes. Es duración de suite, no benchmark ni certificación de rendimiento.

| Grupo | Cantidad aprobada |
| --- | --- |
| test_costos_terreno | 14 |
| test_velocidad_terreno | 12 |
| test_grafo_terreno | 5 |
| test_heap_rutas | 8 |
| test_juego | 15 |
| test_enemigos | 7 |
| test_regresiones_juego | 37 |
| Precarga fallida seleccionada de test_integridad_operaciones | 1 |
| Total conjunto | 99 |

Las 39 pruebas propias y las 53 regresiones previas se incluyen una vez, más las siete de enemigos requeridas por T017. La nueva corrida sustituye los resultados históricos como evidencia actual, sin borrarlos.

### Cobertura comprobada y límites

| Requisitos / escenario | Evidencia de las suites actuales | Límite |
| --- | --- | --- |
| FR-001/002/003; A1/A2 | Costos ausente 100, declarado 250 y 1; jugador/errante/rastreador; reciprocidad válida y posición inmediata. | Datos sintéticos positivos/simétricos. No se prueba validación HTTP ni costos null/asimétricos. |
| FR-002/003; T6 | Jugador, errante y rastreador a velocidad 1000, movimiento en t=20, pendiente t=21. Preparación del tiempo mediante acciones y agenda reales. | No cazador integrado ni dominio de rango. |
| FR-004 | Siete acciones con sus costos 100/50/25 sobre terreno 250; reloj y próximo turno comprobados. | No matriz exhaustiva de objetos/velocidades. |
| FR-005/006/017; T7 | Tres cronologías integradas de jugador: pendiente 250→150 y 250→450 con vencimiento t=50, y 125→200 por fin de aceleración; cancelación/nueva secuencia, daño/azar únicos y continuación más allá del tiempo cancelado. | Efecto temporal preparado coherentemente en t=0. La cadena particular 250→150→225 conserva cobertura parcial; no se prueba aplicación diferida/efectos superpuestos ni movimiento enemigo con toda esa cronología. |
| FR-003/006; ausencia de ataques gratuitos | Vida/azar intactos en movimiento local; cronología de origen/destino/jugador y desempates con costo 250/100. | La llamada local inicial observa estado inmediato y no acredita una transacción de historial. |
| FR-011 | Siete pruebas existentes de decisiones de guardianes/errantes/rastreadores, junto a sus pruebas de costo. | Sin nuevo comportamiento cazador; desempates de ruta son US2. |
| FR-016; A9 | Con terreno 250 y enemigo de velocidad 500, primer turno t=20; con velocidad 100, activación t=100. Fixtures incorporan contenido sin activar salas no visitadas; regresión de entrada/retroceso conserva activación. Código de activación por ID intacto. | No se afirma nueva prueba exhaustiva de múltiples activaciones simultáneas con IDs dispersos. |
| FR-006/014; determinismo en escenarios | Igualdad del estado de Random frente a tiradas previstas; secuencias/identidad de eventos en empates y reprogramación. Regresiones de retroceso/repetición de ataque y continuidad de guardado conservan eventos/azar. | No certificación global para toda cripta/latencia/acción posible. No se repite una corrida completa para inferir determinismo por mero resultado verde. |
| FR-017; efectos heredados | Regresiones de velocidad, veneno/antídoto, regeneración, antorcha, trampas/rearme, cierres y cancelación/muerte. | Escenarios existentes; no certifica todas las combinaciones de efectos con terreno variable. |
| NFR-006; trazabilidad | Pruebas nuevas referencian FR/escenarios; comandos/resultados actuales registrados. | Bitácora compartida pendiente de traslado autorizado; registro local conserva vacíos explícitos. |

### Revisión de diff y de pruebas

El diff completo de Python seguido por Git frente a HEAD tiene solo cuatro hunks en juego.py: seis líneas agregadas y tres eliminadas/sustituidas. Captura salida/costo antes de cambiar posición y sustituye _COSTO_MOVER por costo_salida en Motor.mover y _ejecutar_turno_enemigo. El diff íntegro está transcrito en la sección T015 anterior y sigue coincidiendo. No elimina activación, ataques, esperas, puertas, rastro, eventos, azar, efectos o registros reversibles. calcular_intervalo y cambiar_velocidad no cambian. Los archivos sin seguimiento rutas.py y pruebas/fixture son fundamentos/coberturas anteriores; rutas.py no es otro cambio de T013/T014 ni producción modificada por T017. No se confunde su ausencia de git diff con ausencia de archivo nuevo local.

Inspección AST de las cuatro suites nuevas y fixture: 14/12/5/8 métodos de prueba; sin decoradores skip/expectedFailure ni llamadas skipTest. Se revisan los asserts de costos/tiempos literales oficiales, identidad/secuencia, vida y estado del azar. No se detectan expectativas rebajadas para adaptarse al costo fijo anterior. Los snapshots parciales permanecen identificados; no se cuentan como cronologías integradas. Tampoco se interpretan extracciones de cola como ataques semánticos. El resultado de ejecución no reporta ninguna omisión ni fallo esperado. No se detectó un defecto que requiera modificación de código o pruebas.

### Estado de cierre y entrada de B

US1 está funcionalmente verificada localmente para los escenarios válidos ejecutados. Los fixtures utilizan paquete sintético y componentes offline/precarga existentes; prueban el consumo de campos válidos por el motor, no que una cripta HTTP real o la rama de B suministre versiones/costos correctos. E-B-COSTOS sigue PENDIENTE. No se normaliza null/asimetría ni se confirma Q1/Q2, y no se afirma rendimiento Q3.

T011 tiene evidencia suficiente para cerrar sus pruebas válidas y se consolida su checkbox; T012 y T005–T010 ya están completadas. T013/T014 tienen implementación local comprobada, pero conservan cierre integrado bloqueado por E-B-COSTOS. T015/T016 y la ejecución/verificación de T017 están cumplidas localmente, sin necesidad de ajuste; sus checkboxes conservan pendiente el cierre formal de sus prerrequisitos, sin convertir una cadena documental en un fallo funcional ni repetir pruebas sin motivo. T018 sigue bloqueada por evidencia Q1/Q2 y prerrequisitos; no se ejecuta. No se autoriza ni inicia US2.

Solo se actualizan tasks.md, quickstart.md y prompts-registro-local.md (P29). Se verifican huellas SHA-256 de los Python antes/después para acreditar que código y pruebas no cambian. Rama feature/motor-eventos conservada; no operaciones Git de escritura, integración o publicación. Constitución, PROMPTS_LLM.md y documentación compartida intactas.

## Revalidación y cierre de T015–T017

HEAD verificado: `5c67c8ddba78650968215aee9c4b920210adbfdc` en `feature/motor-eventos`. Desde la raíz del proyecto, con Python 3.14.5 del entorno virtual y acceso a carpetas temporales, se ejecutó:

```powershell
.venv/Scripts/python.exe -B -m unittest -v tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas tests.test_juego tests.test_enemigos tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay tests.test_frontera_temporal tests.test_entrega_datos_terreno 2>&1 | ForEach-Object { $_.ToString() } | Select-Object -Last 13; exit $LASTEXITCODE
```

Resultado: **114 aprobadas, 0 fallidas, 0 errores y 0 omitidas**. Incluye las 11 pruebas de FR-020 y las tres de entrega de datos de terreno.

| Tarea | Evidencia |
| --- | --- |
| T015 | Con T012 y T014 completadas, la agenda real verifica aceleración 250 → 150, ralentización 250 → 450 y expiración 125 → 200, con cancelación, secuencia nueva y una sola ejecución semántica. También se verifica el mínimo de un tick. |
| T016 | Ataque y espera cuestan 100; usar, equipar y abrir, 50; recoger y soltar, 25. El movimiento cambia de sala de inmediato y no provoca ataques gratuitos. T6 verifica que un movimiento de costo 1 a velocidad 1000 en t=20 programa t=21. |
| T017 | Pasaron las suites de costos, velocidad, juego y enemigos, junto con las regresiones de agenda y entrega offline. FR-020 conserva ambos órdenes de secuencia en el empate, resuelve el daño o la derrota antes de devolver la decisión, descarta cancelados y deja pendientes los eventos de t+1. |

Las pruebas existentes cubren los criterios oficiales de T7 mediante cronologías separadas. El ejemplo 250 → 150 → 225 tiene cobertura parcial: la aceleración en t=50 se invoca desde un estado unitario preparado y se procesa la expiración en t=75. No se ejecutó una prueba integral de esa cadena con activación y expiración por eventos ordinarios.

## Inicio de US2: pruebas iniciales T019 — 2026-11-06

HEAD 15adfcf en feature/motor-eventos, publicado; main permanece sin integrar. Autorización exclusiva para preparar/ejecutar pruebas iniciales del algoritmo sobre grafos sintéticos válidos, sin Dijkstra ni decisión de cazador. Se releen constitución, Parte II §3.2, spec/plan/tasks, contratos y estructuras. Checklist 13/16; ninguna pregunta externa se da por resuelta.

**Orden exacto:** T019 y T020 dependen de T006/T010, ya completadas. Esta etapa cubre solo T019 de rutas; T020 trata la política del cazador y queda pendiente. T021 implementará el algoritmo tras disponer de las pruebas T019 y el soporte T010; T022 necesitará además T020. No se ejecuta ninguna de esas implementaciones. Las pruebas rojas constituyen preparación TDD, no aceptación completa de T019.

**Sin bloqueo externo para preparar T019:** se suministran explícitamente límites enteros positivos y costos positivos/simétricos. No se prueba ausencia/null de rango, validación de datos inconsistentes, HTTP, conocimiento de C, puertas de ambos extremos cambiando durante partida ni integración de B/D. Q1/Q2 siguen abiertas para sus políticas y suministros; Q3 no impide pruebas funcionales sintéticas ni se resuelve por ellas. E-B-COSTOS/E-B-RANGO/E-C-RUTA/E-C-DESPACHO y demás acuerdos conservan sus estados. No se necesita incorporar main ni alterar la frontera temporal del motor.

### Contrato interno propuesto para preparar T021

La suite propone llamar buscar_ruta(grafo, espacio, frontera, origen_indice, destino_indice, limite) en modelo/rutas.py. GrafoTerreno, EspacioBusqueda y HeapRutas son los existentes; origen/destino se resuelven mediante indice antes de la consulta. Resultado interno de prueba: tupla (primer_indice, direccion, costo_paso, costo_total), o None cuando no se demuestra una ruta dentro del límite. Ese None no certifica desconexión frente a exceso de rango ni implica costo/rango null. No hay caso origen=destino ni modo sin límite en esta etapa. Firmas/estados compartidos de C permanecen pendientes de T023/T024; esto no los aprueba ni implementa.

T021 podrá usar el grafo ya preparado, arreglos con generaciones y heap indexado propios: iniciar consulta, filtrar arcos por el estado real de la puerta referenciada, mantener etiquetas (distancia, primerID), propagar ese primer ID y mejorar por menor distancia o menor primerID en empate. Con costos positivos, cerrar el destino solo con etiqueta definitiva permite respetar el desempate; podar candidatos por encima del límite y devolver costo del primer arco separado del total. El espacio/frontera se prepara una vez y la implementación deberá gestionar iniciar/finalizar sin barrer V por consulta. Este resumen sigue el Plan, no es código escrito ni demuestra complejidad/rendimiento empíricos. No usar dict/set, heapq, bisect, collections ni bibliotecas de grafos como sustitutos.

### Casos preparados

| Método de test_rutas_cazador | Resultado esperado, todavía no comprobado por algoritmo |
| --- | --- |
| test_t1_sin_ruta_abierta_por_puerta_cerrada | None ante única conexión cerrada. |
| test_destino_aislado_es_inalcanzable | None con destino desconectado. |
| test_t2_costo_101_supera_limite_100 | None, sin inventar distancia fuera del rango. |
| test_t3_tres_pasos_300_superan_dos_pasos_500 | Primer ID 3, dirección N, paso 100, total 300. |
| test_a4_costo_igual_al_limite_admite_ruta | Mismo resultado con límite exactamente 300. |
| test_puerta_cerrada_excluye_ruta_barata_pero_no_alternativa | Primera salida abierta hacia ID 7, paso 250, total 500. |
| test_t4_menor_primer_id_pese_a_orden_de_enumeracion | ID 3, paso 100, total 300; dos enumeraciones opuestas. |
| test_empate_elige_menor_id_aunque_su_primer_arco_cueste_mas | ID 3, paso 200, total 300; no elegir por costo del primer arco. |
| test_convergencia_propaga_mejora_del_primer_id | ID 3, paso 4, total 6 tras converger rutas empatadas. |
| test_ciclo_positivo_no_desvia_el_camino_minimo | ID 3, paso 4, total 5, sin recorrer un ciclo para abaratar. |

Se reutiliza crear_salas, sin modificar fixture ni producir datos reales. Todos los grafos son recíprocos de igual costo, con grado máximo cuatro, IDs dispersos y estados de puerta explícitos. No se implementa una referencia de búsqueda: comparación generativa/selección lineal pertenece a T026, no autorizada todavía. Tampoco se prueba aquí ataque/espera de T1/T2: corresponde a T020/T022, no a la búsqueda pura.

### Resultados realmente ejecutados

```powershell
python -B -m unittest tests.test_rutas_cazador -v
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas tests.test_juego tests.test_enemigos tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

Intérprete original Python 3.12.14 del runtime auxiliar de Codex; comandos mostrados de forma portable desde raíz. La nueva suite, sin necesitar temporales, ejecuta diez métodos y reporta once errores en 0.008 s, FAILED (errors=11)/salida 1. Todos son AttributeError en la llamada a rutas.buscar_ruta, todavía ausente: uno por cada caso y dos por el subtest de enumeración. Se construyen grafos/espacio/frontera reales antes de fallar; no se alcanza ninguna comparación de resultado de búsqueda. No se usa skip, expectedFailure, mock ni función sustituta para fingir algoritmo. Esta ausencia esperada de T021 no significa once defectos distintos ni once pruebas aprobadas.

Regresiones existentes, con acceso autorizado a temporales: 99/99 en 1.905 s, OK/salida 0, cero fallos/errores/skips. Conservan la evidencia de US1 y fundamentos; no demuestran corrección de Dijkstra ausente. No se ejecuta benchmark ni se afirma cumplimiento Q3.

T019 queda preparada pero pendiente de aceptación satisfactoria tras implementar T021; la siguiente tarea exacta del algoritmo es T021, previa autorización. No se marcan T019/T020/T021 completadas. Archivos de esta etapa: nuevo tests/test_rutas_cazador.py y actualizaciones de tasks.md, quickstart.md y prompts-registro-local.md (P30). Producción y pruebas/fixture previos permanecen intactos; ningún archivo de B/C/D ni evento/interfaz cambia. No se realizan operaciones Git de escritura, integración o publicación ni se incorpora main. PROMPTS_LLM.md permanece pendiente de traslado autorizado. No existe .specify/extensions.yml para hooks antes/después.

## Implementación limitada de T021 — 2026-11-06

Autorización posterior exclusiva para buscar_ruta en modelo/rutas.py y documentación propia. Se revisaron constitución 1.1.0, Parte II §3.2 (incluido desempate/conocimiento), spec/plan/tasks, contratos y las once comprobaciones de T019. Checklist 13/16; Q1–Q3 y entregas externas no se resuelven. La firma interna autorizada encaja con GrafoTerreno, EspacioBusqueda y HeapRutas actuales; no se modifica ninguna de esas interfaces ni la prueba T019.

### Implementación e invariantes

La única modificación de producción es la nueva función buscar_ruta y la cabecera del módulo, actualizada porque ya contiene búsqueda. Usa origen/destino como índices distintos del mismo grafo preparado; espacio y frontera asociados y frontera vacía antes de iniciar. No define llegada origen=destino ni modo sin límite, y no valida en nombre de B índices/datos/rangos inválidos. El contrato compartido con C permanece propuesto para T023/T024; None solo indica que no se obtuvo un paso admisible dentro del límite, sin certificar una distancia exterior.

frontera.iniciar aumenta la generación existente, sin reinicializar V entradas. La semilla de origen es distancia 0/primerID None. Cada extracción fija la mejor etiqueta del nodo, que se cierra; las relajaciones leen arco.puerta.get("cerrada", False) desde el descriptor real, omiten cerradas/nodos cerrados y no insertan costos superiores al límite. Igualdad con el límite sí se admite. En vecinos inmediatos, primerID es el ID externo del destino del arco; luego se propaga. insertar_o_disminuir conserva la mejor etiqueta (distancia, primerID) y HeapRutas añade ID de sala al orden total, sin azar ni ordenamientos nuevos.

Con costos positivos, todos los predecesores de una ruta óptima tienen distancia menor que su destino; por eso se procesan antes de cerrar ese destino, incluida una mejora de primerID por convergencia. Al cerrarlo se examinan solo las salidas del origen (grado acotado), se recupera el arco abierto al primer vecino elegido y su costo mínimo, y se devuelve (primer_indice, direccion, costo_paso, costo_total). No se copian caminos completos ni se reserva un arreglo nuevo por sala para reconstruirlos. Los grafos de T019 no tienen arcos paralelos; no se afirma haber probado un desempate entre direcciones equivalentes hacia el mismo vecino.

finally llama frontera.finalizar aun al retornar temprano; limpia solo los pendientes de la frontera y sus posiciones, imputados a esta consulta. No cambia el motor, agenda, azar, posición de actores, conocimiento o puertas. No hay nuevas importaciones ni estructuras prohibidas. Preparación del grafo sigue O(V log V + E log V), espacio O(V+E), fuera de consulta; el análisis de la consulta mantiene O((Vr+Er)log(Vr+1)) y limpieza O(F) con auxiliares O(V) reutilizados. Esto es análisis del diseño/código, no medición de localidad ni certificación temporal.

### Ejecuciones reales sin modificar expectativas

```powershell
python -B -m unittest tests.test_rutas_cazador tests.test_grafo_terreno tests.test_heap_rutas -v
python -B -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas tests.test_juego tests.test_enemigos tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

Comandos portables; intérprete original Python 3.12.14 del runtime auxiliar de Codex, -B. Primera ejecución sin temporales: 23/23 métodos aprobados en 0.011 s (10 de rutas con 11 casos, 5 de grafo, 8 de heap), OK/salida 0. Segunda, con acceso autorizado a temporales: 99/99 en 1.851 s, OK/salida 0. Cero fallos/errores/skips; los once AttributeError anteriores de T019 desaparecen sin modificar esa suite. Las 13 pruebas de estructuras están incluidas en ambos comandos; son 109 métodos únicos, no 122 distintos.

Control complementario realmente ejecutado, sin crear/modificar archivos de prueba: el grafo de alternativas de T019 se consulta tres veces sobre el mismo EspacioBusqueda/HeapRutas. 90→80 con límite 300 devuelve primer ID 3/N/paso100/total300; con límite 100 devuelve None; 80→90 con límite 300 devuelve primer ID 50/S/paso100/total300. Después de cada consulta se comprueba frontera vacía y mismos objetos de los cinco arreglos auxiliares; generación final 3. Resultado satisfactorio, salida 0. Es un control puntual de reutilización, no la referencia independiente/generativa de T026 ni pruebas de cambios de puertas/invalidez de US3.

La duración de unittest no prueba <20 ms: no se ejecuta benchmark y Q3 sigue pendiente. Tampoco se certifican aún localidad T039, equivalencia exhaustiva T026 o suministro/acceso efectivo de B.

### Estado y archivos

T019 y T021 verificadas/completadas para los escenarios válidos de núcleo autorizados. T020 no está preparada y no se implementa T022 ni modelo/cazador.py. No se conecta al motor o compañeros, no se incorpora main ni se cambia la frontera temporal. Permanecen pendientes Q1–Q3, E-B-COSTOS/E-B-RANGO/E-C-RUTA/E-C-DESPACHO y demás acuerdos. Archivos modificados en esta etapa: modelo/rutas.py y documentación propia tasks.md, quickstart.md, prompts-registro-local.md (P31). La suite T019 sin seguimiento procede de la etapa anterior y permanece intacta. No se realizan operaciones Git de escritura; constitución, PROMPTS_LLM.md, interfaz y restantes archivos de producción/pruebas se conservan.

## Preparación TDD de decisión del cazador — T020 — 2026-11-06

Autorización posterior exclusiva para tests/test_decision_cazador.py y documentación propia. Se revisan constitución, Parte II §3.2, spec/plan/tasks, contratos y buscar_ruta real. T020 depende de T006/T010, ambas completas; T021 también está verificada y se utiliza sin editar. A3 exige atacar antes de buscar al compartir sala; A5 exige basarse en esqueleto/puertas reales sin dependencia del conocimiento o contenido descargado. Rangos enteros positivos explícitos y costos válidos permiten preparar esos escenarios sin cerrar Q1–Q3. Checklist conserva sus pendientes y ningún contrato E-* se acredita.

### Propuesta interna y controles

La suite propone decidir_cazador(origen_indice, destino_indice, rango, consultar_ruta) en el futuro modelo/cazador.py. Devuelve (accion, direccion_o_None, costo_base): atacar/esperar con 100, o mover con dirección y costo del primer arco, sin ejecutar la acción. No cambia decidir_accion de C ni constituye contrato aprobado con B/C/D. La consulta inyectada solo recibe índices y límite; una clausura local instrumentada registra llamadas y delega en buscar_ruta real con GrafoTerreno/EspacioBusqueda/HeapRutas existentes. Se espera cero llamadas al coincidir y una al buscar. Esa sonda no fabrica caminos, no implementa la política y no es un nuevo mock de servicio.

| Método preparado | Regla / resultado esperado aún no comprobado |
| --- | --- |
| test_a3_compartir_sala_ataca_antes_de_consultar_rutas | Atacar, costo 100, cero consultas; rango positivo explícito 1. |
| test_ruta_admisible_devuelve_primer_paso_optimo_y_su_costo | Camino de dos pasos/200 frente a directo/500: mover N con costo de paso 100, no total 200. |
| test_t1_destino_desconectado_espera_con_costo_100 | Esperar, sin dirección, costo 100. |
| test_t2_costo_101_supera_rango_100_y_espera | Esperar con costo 100. |
| test_a4_distancia_igual_al_rango_permite_perseguir | Distancia/rango 200: mover N, paso 100. |
| test_unica_puerta_cerrada_impide_movimiento | Esperar 100 sin abrirla. |
| test_atajo_cerrado_no_impide_usar_alternativa_abierta | Ignorar atajo cerrado de costo 50 y seguir alternativa abierta de costo 200, pagando paso 100. |
| test_consulta_no_modifica_posiciones_azar_agenda_ni_puertas | Conservar exportación de estado, RNG, posiciones, identidad/tiempos/secuencias/cancelación/en_cola de eventos y puertas reales. |
| test_a5_misma_decision_sin_descargas_adicionales_de_contenido | Dos subcasos antes/después de descargar contenido: misma decisión y contadores/llamadas sin incremento durante consulta. |

Se reutiliza crear_salas sin modificarlo ni añadir un fixture. Para observar estado real, motor_terreno ejecuta primero un movimiento completo legal del jugador, separándolo del enemigo en t=250; entonces se consulta la política con sus posiciones reales. No se mueve/teletransporta al enemigo ni se cambia su comportamiento, velocidad o evento: se prueba la futura función pura sobre esos índices, no un turno de un cazador conectado al motor. Los auxiliares de rutas pueden cambiar sus generaciones; las observaciones protegidas son las del juego/puertas/agenda/azar, no esos derivados.

Para A5 se reutiliza ServidorFalso ya existente (ningún doble externo nuevo): una llamada explícita de preparación obtiene el esqueleto y, solo antes del segundo subcaso, otra obtiene el contenido de cuatro salas. La política no recibe ese servidor, contenido ni conocimiento; solo la consulta sobre el mismo grafo. Se comparan sus contadores y lista de llamadas antes/después de cada decisión, esperando cero descargas adicionales. No se afirma una prueba de integración con la red real, precarga/conocimiento de C o datos HTTP de B, ni una intercepción global de cualquier HTTP posible. El origen/rango del catálogo y conexión al motor siguen reservados a acuerdos/T025; no se añade campo rango a tipos.py. El valor None en la tupla indica ausencia de dirección, no una política para rango null.

### Ejecuciones reales y límites actuales

```powershell
python -B -m unittest tests.test_decision_cazador -v
python -B -m unittest tests.test_rutas_cazador tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas tests.test_juego tests.test_enemigos tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay
```

Comandos portables; intérprete original Python 3.12.14, -B y acceso autorizado a temporales. Nueva suite: nueve métodos/diez casos, diez errores en 0.082 s, FAILED (errors=10)/salida 1 por ModuleNotFoundError: modelo.cazador todavía no existe. La importación se hace por caso para que todos se enumeren; no hay skip/expectedFailure ni implementación provisional que falsee resultados. Las preparaciones se ejecutan pero no se alcanzan las comprobaciones de decisiones/ausencia de efectos posteriores a la llamada: no se acredita aceptación ni independencia de descargas por preparar un assert.

Rutas y regresiones existentes: 109/109 métodos en 2.026 s, OK/salida 0, cero fallos/errores/skips. Son diez métodos de T019 (once casos) y las 99 pruebas anteriores; incluyen las 13 de grafo/heap, sin contarlas dos veces. No se ejecuta benchmark ni se afirma rendimiento Q3.

T020 queda preparada, casilla pendiente hasta verificación satisfactoria tras T022. La siguiente tarea exacta es T022, implementar la decisión en modelo/cazador.py usando la búsqueda T021, previa autorización. No se crea ese módulo ni se ejecuta otra tarea; los comportamientos existentes de C permanecen intactos. Archivos nuevos/modificados de esta etapa: tests/test_decision_cazador.py, tasks.md, quickstart.md y prompts-registro-local.md (P32). Producción, pruebas/fixtures existentes, constitución y documentación compartida no cambian. No se incorpora main ni se realizan operaciones Git de escritura. Q1–Q3 y entregas externas siguen abiertas; PROMPTS_LLM.md espera traslado autorizado. No existe .specify/extensions.yml al revisar hooks antes/después.

## Frontera temporal AD-01

2026-11-06: preparación TDD de FR-020, sin tocar producción. Se reutiliza `motor_terreno` con motor/agenda reales. La sonda de prueba registra los eventos retornados por `ejecutar_ciclo` sin sustituir el despacho ni sus resultados. Los casos sintéticos preparan contador, vida inicial herida o efecto vigente en t=0 cuando corresponde; no cambian el reloj ni ejecutan acciones antes de un turno. No se prueba aún `historia` ni el registro de D.

```powershell
python -B -X utf8 -m unittest tests.test_frontera_temporal -v
python -B -X utf8 -m unittest tests.test_costos_terreno tests.test_velocidad_terreno tests.test_grafo_terreno tests.test_heap_rutas tests.test_juego tests.test_enemigos tests.test_regresiones_juego tests.test_integridad_operaciones.TestIntegridadOperaciones.test_precarga_fallida_no_rompe_movimiento_ni_replay -v
```

| Caso nuevo | Resultado histórico antes de AD-02 |
| --- | --- |
| A14: jugador 10, enemigo 11 | Falla: vida 30 al devolver en t=100; esperada 28. |
| A14: enemigo 10, jugador 11 | Pasa: ataque, turno, daño y azar en orden. |
| A15: ataque letal empatado | Falla: `terminado` es falso al devolver. |
| A16: futuro t+1 | Pasa: cierre de puerta en t=101 pendiente e intacto. |
| A16: cierre cancelado en t | Pasa: sin cierre ni adelanto de reloj. |
| A16/A17: cancelado posterior al turno | Pasa: restaurar velocidad sustituye turno enemigo t=100 por t=101; el nuevo queda pendiente sin ataque ni tirada. Protege contra ejecutar t+1 al descartar cancelados. |
| A17: fin de efecto en t | Pasa: ataque, restauración y turno en secuencia; enemigo reprogramado a t=150. |
| A17: reprogramar al jugador | Pasa: restauración en t=50, frontera vigente en t=75. |
| A18: dos decisiones sucesivas | Falla: vida 28 en t=200; esperada 26 por dos ataques. |
| A18: repetir con misma semilla | Falla: las dos ejecuciones coinciden, pero conservan un evento vigente en la frontera. |
| Control de API: un evento por `ejecutar_ciclo` | Pasa: el paso individual sigue dejando los demás en cola. |

Corrida histórica de AD-01: 11 pruebas en 0.581 s, 7 aprobadas, 4 fallos de aserción, 0 errores u omisiones, salida 1. Las 99 regresiones pasaron en 2.028 s, incluida T016 con su expectativa anterior. Los cuatro fallos reproducían el corte en `turno_jugador`. Las duraciones de unittest corresponden a la ejecución de las suites.

## Validación local AD-03

FR-020 aplica el orden por tiempo y secuencia de Parte I §2.3 y permite observar el estado previo a la decisión descrito para `historia <t>` en Parte II §3.6 y Apéndice B. La especificación quedó confirmada en `26be407`. En AD-02, el bucle del motor conserva el instante del turno vigente como límite y continúa el despacho en la misma transacción. La cola comprueba el límite en cada raíz antes de extraerla. `ejecutar_ciclo()` sin límite sigue procesando un evento vigente por llamada.

Los cuatro casos reconciliados se contrastaron con las trazas. Errante y rastreador programan t=21 al moverse en t=20. El ataque empatado en t=21 programa t=31. La sonda de costos llama una vez al método real, devuelve el mismo evento y registra ambos tiempos del movimiento en una lista local al caso. El fixture crea un motor nuevo por caso. T016 verifica ambos ataques con el daño derivado de dos tiradas, el estado final del RNG y el turno pendiente en t=300. La regresión de regeneración comprueba vida 18 tras los pulsos en t=50 y t=100, y mantiene la comprobación de vida 10 y agenda original al retroceder.

Corrida de AD-03 con el intérprete auxiliar y `unittest`, API real deshabilitada y sin paquete oficial opcional:

| Grupo | Resultado |
| --- | --- |
| `tests.test_frontera_temporal` | 11/11, incluidos ambos órdenes del empate, derrota, cancelaciones, efectos, reprogramación y RNG. |
| Las 99 regresiones del comando de AD-01 | 99/99, incluidos T016, T7, retroceso y el caso de precarga y replay. |
| `tests.test_rutas_cazador` | 10/10. |
| Descubrimiento adicional en `tests/`, excluidos los grupos ya ejecutados y T020 | 360 entradas de unittest. 350 aprobadas, 2 fallos, 5 errores y 3 omisiones. |
| `tests.test_cliente_api` y los dos casos de `TestOffline` que requieren `requests`, con el Python de `.venv` | 12/12. Sustituyen el error de importación del módulo y dos errores de precarga de la corrida anterior. |

Las tres omisiones corresponden a la API real y a dos pruebas del paquete oficial opcional. T020 queda excluida de la corrida de funcionalidades disponibles porque depende de T022 y de `modelo.cazador`.

Los cuatro resultados de interfaz restantes se reprodujeron con `modelo/juego.py` y `modelo/eventos.py` de `26be407` cargados en memoria y el mismo intérprete auxiliar:

- `test_redibujar_menu_crea_animacion_nueva_y_destruirlo_la_cancela`: misma instancia de animación tras redibujar.
- `test_reposo_preparado_conserva_pose_de_agarre_y_daga_contraria`: diferencia de píxeles.
- `test_refresco_de_inventario_no_borra_la_animacion_de_dano`: el fixture de `VistaGrafica` carece de `escena`.
- `test_menu_reproduce_intro_una_vez_al_mostrarse`: el fixture de `MenuInicio` carece de `canvas` y `_precarga_selector`.

Las sondas en memoria comprobaron que un evento insertado en t durante el despacho se procesa por secuencia, que los eventos vigentes y cancelados de t+1 permanecen en cola y que los mensajes se publican con el estado final del turno. Una excepción después del ataque empatado restauró reloj, vida, posición, RNG, contador, agenda e historial y dejó la publicación vacía.

AD-03 cierra la validación local de FR-020. La validación con la línea de tiempo de D, su formato serializable y E-D-CAMBIOS quedan pendientes. Q1–Q3 y T020/T022 conservan su estado.

## Cierre local de T020 y T022

T020 verifica el contrato interno de `decidir_cazador(origen_indice, destino_indice, rango, consultar_ruta)`. T022 lo implementa para datos válidos en `modelo/cazador.py` según Parte II §3.2. En la misma sala devuelve atacar con costo 100 y cero consultas. En salas distintas delega el rango inclusivo a T021. Si no hay paso admisible devuelve esperar con costo 100. Si lo hay, devuelve la dirección y el costo de la primera salida. T021 resuelve el desempate por menor ID de la primera vecina sobre el esqueleto y las puertas reales.

La corrida de cierre reemplaza el resultado inicial de preparación TDD de T020. Los casos verifican puertas, costo, rango, estado del motor y ausencia de descargas adicionales durante la decisión.

| Suite | Resultado |
| --- | --- |
| `tests.test_decision_cazador` | 9/9 métodos, incluidos los dos subcasos de A5. |
| `tests.test_rutas_cazador` | 10/10 métodos. |
| `tests.test_frontera_temporal` | 11/11. |
| Regresiones anteriores del comando de AD-01 | 99/99. |

Total: 129 métodos aprobados, con cero fallos, errores u omisiones. Se marcan T020 y T022 para el alcance local con entradas válidas. Q1–Q3 y los contratos externos siguen pendientes.

La corrida usa `buscar_ruta` de T021 en el árbol de trabajo. Esa función todavía falta en `HEAD` (`299079d`). La suite de decisión importa `buscar_ruta` directamente, así que el commit de T020/T022 debe quedar después de confirmar T019/T021.

## Validación local de T026

Los dos casos de `tests.test_rutas_cazador` comparan el costo mínimo total y el ID de la primera sala vecina con una enumeración independiente de caminos simples, sin usar el heap de producción. La cuadrícula uniforme tiene seis rutas óptimas empatadas y conserva el mismo resultado al variar el orden de las conexiones y de las salas.

En dos cuadrículas ponderadas se compararon 144 pares ordenados de salas distintas. Se verificaron puertas cerradas, destinos inalcanzables y límites inclusivos de costo. Para las rutas con costo mayor que 1 también se comprobó el rechazo con un límite una unidad menor.

Resultados de la ejecución de T026: 12/12 rutas, 9/9 decisión, 11/11 FR-020 y 99/99 regresiones. Total: 131 pruebas aprobadas.

## Validación local de T039

Con rango 4 y cinco salas alcanzables fijas, la prueba P2 amplía el mapa a 6, 69 y 8.197 salas. Prepara grafo, índices y arreglos antes de instrumentar cada consulta. La enumeración independiente de caminos simples confirma primer vecino 3, dirección N, costo del paso 2 y total 4. La consulta al destino exterior devuelve `None`.

En cada tamaño se observaron 4 extracciones, 4 accesos a adyacencias, 75 lecturas y 37 escrituras de auxiliares y 1 descarte final para el destino local. Para el destino exterior se observaron 5, 5, 81, 38 y 0, respectivamente. La revisión repitió los conteos y comprobó que la consulta sin sondas devuelve el mismo resultado. El pico de `tracemalloc` expresa bytes trazados de la consulta instrumentada y se registra por separado de los conteos de operaciones.

La reejecución de `tests.test_localidad_rutas`, rutas, decisión, FR-020 y las 99 regresiones del comando de AD-01 pasó 132/132 pruebas. T046 sigue pendiente de la referencia oficial Q3, la conexión de D y la medición del ciclo completo.

## Cierre documental local de T051

El [registro local](prompts-registro-local.md#corte-documental-en-p77) consolida 77 solicitudes íntegras hasta P77, con una fila por ID en orden de envío. Se verificaron 73 cuerpos en el registro y cuatro en los tres anexos. Se conservaron P01–P75 y los anexos, y se cotejaron P76 y P77 con el registro original de la sesión de Codex.

Los dos mensajes incompletos entre P48 y P33 conservan sus fragmentos literales y sus finales siguen pendientes de recuperación. La autorización de este cierre es posterior al corte y queda para el mantenimiento incremental. El traslado a `PROMPTS_LLM.md` sigue pendiente de autorización.
