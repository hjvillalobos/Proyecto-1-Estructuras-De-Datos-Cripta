# Revisión de entrega — 15 de noviembre de 2026

## Alcance y fuentes

Revisión de Parte I y II, mapas publicados, presentación, contenido inédito, audio y rendimiento; correcciones autorizadas en `004-linea-tiempo`. Base: `7686b64`, árbol inicialmente limpio. Especificación de la corrección: `6309e20`, anterior al código.

Se reextrajo el PDF original local **Cripta - Parte II.pdf**, íntegro (331.633 bytes), y se contrastó con el texto previamente conservado. El PDF local de Parte I tiene **cero bytes**: se revisó la extracción conservada de 20 páginas; no se puede autenticar su identidad con el original vacío. Las referencias P1 siguientes están condicionadas a esa fuente. El listado y los datos actuales se consultaron con el cliente HTTP del proyecto, UUID y presupuesto ordinarios. No se modificó el contenido de los mapas del profesor.

Estados: **C** = comprobado en el alcance indicado, **I** = incumplimiento comprobado, **NV** = no verificable con las fuentes o intervención disponibles. C no significa una demostración para todas las entradas posibles.

## Hallazgos priorizados

1. **P2, corregido (RE-01): reapertura por el extremo sin metadatos.** En salidas recíprocas inequívocas, el servicio puede publicar llave/cierre en un solo descriptor. El cierre bilateral ya existente cerraba ambos, pero abrir desde el otro lado omitía la llave y el nuevo cierre. Dos pruebas nuevas fallaron antes del cambio: apertura admitida sin llave y ausencia de cierre programado. Ahora se respeta el atributo local y, si falta, el del único retorno. La validación de carga y la presentación usan la misma llave; el binario, la historia y el retroceso conservan el comportamiento. No se inventan retornos ni se normalizan estados iniciales asimétricos; las conexiones ambiguas siguen independientes.
2. **P2, histórico (I): bitácora/proceso incompletos.** Se conservan dos finales de prompts incompletos de A y el commit `33d97ac` reunió aclaración y código. Documentarlos no satisface retrospectivamente la exigencia de prompts íntegros y commits separados. No se inventan textos ni se reescribe el historial compartido.
3. **P2, límite de evidencia:** el paso conocido tuvo picos previos de 5,168/5,527 ms en otros incrementos. Las muestras nuevas se reportan por separado; un resultado bajo 5 ms no elimina esos antecedentes ni garantiza latencia absoluta.
4. **NV:** falta el original íntegro de Parte I, los finales originales de esos prompts y la evaluación/defensa humana. No se ha comprobado audición por los altavoces del equipo; sí despacho de audio y WAV válidos.

Una primera regresión de esta corrección detectó además una referencia local incorrecta en la comprobación de victoria introducida durante la edición. Se corrigió usando la sala de origen del movimiento; la selección de 24 pruebas pasó después. La ejecución interrumpida se conserva localmente como fallida, sin contarla como aprobación.

La siguiente regresión completa (834 tests) detectó 12 errores en los casos de transición visual: su preparación cambiaba las direcciones del esqueleto después de construir el índice estático. Ahora reconstruye ese índice después de cambiar la topología; conserva todas las aserciones de dirección, antorcha, animación y estado. La selección de 26 pruebas de transición/puertas/presentación pasó tras la corrección. No se captura ni se ignora la excepción de producción para ocultar una incoherencia del grafo.

## Matriz de Parte I

Rutas relativas a la raíz. La suite completa ejecuta estos módulos; los tests se solapan y sus cantidades no se suman.

| Sección / obligación | Estado | Evidencia y límite |
|---|---|---|
| 2.1–2.2 salas, estadísticas e instancias desde datos | C | `red/precarga.py`, `modelo/juego.py`; `test_precarga_offline`, `test_verificacion_entrega`, `test_almacen_salas`. Cripta inédita de 137 salas y IDs uint32 dispersos. |
| 2.3 reloj, secuencia, costos y cambios de velocidad | C | `test_juego`, `test_costos_terreno`, `test_velocidad_terreno`, `test_frontera_temporal`. Movimiento sustituido por la regla de P2. |
| 2.4 activación inicial, dormidos y orden determinista | C | `test_enemigos`, `test_eventos_terreno`, `test_entrada_conocimiento_motor`; precargar o iluminar no activa contenido. |
| 2.5 movimiento, apertura y cierre | C | `test_puertas_reciprocas_d`, RE-01 nuevo, `test_trampa_letal_salida_sur`. Guardar/cargar, cierre y retroceso reales. |
| 2.6 combate, daño mínimo, muerte y botín | C | `test_muerte_enemigos`, `test_regresiones_juego`, `test_partida_generada`. Azar con semilla. |
| 2.7 inventario y siete clases de objetos | C | `test_inventario`, `test_correcciones_enunciado`, `test_equipo_visual`, `test_contenido_desconocido_gui`; RE-02 nuevo para marcador y WAV con IDs inéditos. Una clase semántica futura fuera del contrato requeriría reglas nuevas; un ID nuevo de una clase soportada no. |
| 2.8 guardián, errante y rastreador | C | `test_enemigos`, `test_rastro`, `test_eventos_terreno`; P2 añade cazador sin reemplazarlos. |
| 2.9 rastro, caducidad 400 y desempate por ID | C | `test_rastro`, `test_regresiones_juego`, `test_correcciones_enunciado`; índice propio. |
| 2.10 veneno, antídoto, regeneración, trampas y velocidad | C | `test_correcciones_enunciado`, `test_trampa_letal_salida_sur`, `test_trampas_antorcha_visual`. Daño letal detiene efectos posteriores. |
| 2.11 retroceso de cinco acciones y pergaminos excluidos | C | `test_historial`, `test_regresiones_juego`, `test_integridad_operaciones`, `test_historia_motor`; acciones fallidas no consumen pergamino. |
| 2.12 victoria, derrota y puntaje | C | `test_fin_partida`, `test_cumplimiento_integrado`, `test_puntajes_apagado`; llave acreditada y puntaje único por sesión. |
| 2.13 ejemplo | C | Recorridos históricos/victorias/replays en `test_criptas_api`; el ejemplo ilustrativo no fija datos para versiones nuevas. |
| 3.1–3.4 HTTP, UUID, 429, lotes y versiones | C | `test_cliente_api`, `test_catalogo`, `test_precarga_offline`, `test_sesion_datos`; API fría/caliente en cinco criptas. |
| 4.1 agenda propia y cancelación | C | `test_juego`, `test_historial`, `test_eventos_terreno`; bench agenda/terreno-cazador. |
| 4.2 precarga y esperas sin tiempo virtual | C | `test_precarga_offline`, `test_rendimiento_arranque`; preparación de entrada antes de confirmar movimiento. |
| 4.3 catálogo: resolver referencias sin repetición HTTP | C | `test_catalogo`, `test_entrega_datos_terreno`; caché/almacén por versión. |
| 4.4 caché 25, uso fijado, desalojo y disco | C | `test_cache`, `test_catalogo`, `test_correcciones_enunciado`; pruebas con capacidad 1 y presupuesto API. |
| 4.5 cursor, extracción local, equipar al frente y vistas ordenadas | C | `test_inventario`, `test_cumplimiento_integrado`; no recorrer desde cabeza para soltar el cursor. |
| 4.6 inversos sin copia física por acción | C | `test_historial`, `test_historia_motor`, `test_partida_completa`; memoria histórica por cambios/checkpoints en P2. |
| 4.7 rastreadores: consulta local y costo por actores | C | `test_rastro`, `test_enemigos`; estructuras propias y mediciones previas conservadas en DECISIONES. |
| 4.8 últimos 20 mensajes con memoria acotada | C | Buffer circular de `vista/bitacora_pantalla.py`; `test_correcciones_enunciado` y regresiones. |
| 4.9 dos ordenamientos, elección automática y sin sort/sorted | C | `utilidades/ordenamiento.py`, `test_inventario`, `test_bench_defensa`; bench ordenamiento con alternativas. |
| 4.10 binario propio, acceso a sala, incompatibilidad y JSON | C | `test_correcciones_enunciado`, `test_persistencia_historia`; bench guardado/guardado-historia. |
| 4.11 log append y replay determinista/versionado | C | `test_replay_directo`, `test_replay_reinicio`, `test_partida_generada`; replay incluso tras eliminar el guardado usado durante la partida. |
| 5.1 red y reporte de caché/presupuesto | C | Cinco criptas fría/caliente, tabla de abajo; intentos y reintentos contados, offline cero HTTP. |
| 5.2 ciclo <20 ms y 5.3 bench por subsistema | C | Benchmark de referencia, tabla temporal; modos sin vista y alternativas en `bench.py`. C limitado a cargas y equipo medidos. |
| 6 MVC y adaptadores offline | C | Modos `--bench`, `--replay --hasta`, `--verificar` sin vista; `test_modos_historia`, `test_comandos_integracion`, `test_cumplimiento_integrado`. |
| 7 estructuras propias | C | Inspección de modelo/red/datos/controlador y pruebas de heap/localidad/almacenes. Sin heapq, bisect, collections, networkx o sort/sorted en los problemas evaluados. JSON y diccionarios de presentación/fixtures no sustituyen índices propios. |
| 8 decisiones con alternativas, complejidad y mediciones | C | `DECISIONES.md`, planes y benchmarks. Se conservan límites y mediciones anteriores; no equivale a defensa humana. |
| 9 defensa y explicación por todo el grupo | NV | Requiere intervención y evaluación del grupo/profesor; no se prepararon materiales de defensa. |
| 10.1 README e instalación | C | README, requirements y verificación de copia limpia; esta última reutiliza dependencias instaladas. |
| 10.2 interfaz funcional mínima | C | Consola/GUI y regresión de comandos, equipo, inventario, guardado/carga y cierre; inspección nativa de inicio/mapa. |
| 10.3 todos los prompts textuales | I | Dos finales incompletos, documentados; las nuevas solicitudes indirectas se identifican como resúmenes. |
| 11 evaluación y 12 preguntas | NV | Son rúbrica/preguntas orientativas; no se asigna nota ni se inventan respuestas humanas. |
| Apéndice A contrato | C | Adaptadores y tabla API; versiones del paquete identificadas. |

Apéndice B de P1: inventario lleno/apertura sin llave (`test_juego`, `test_inventario`, RE-01); errante sin salidas y empate de rastro (`test_enemigos`, `test_rastro`); refresco del rastro (`test_regresiones_juego`); muerte con eventos futuros (`test_muerte_enemigos`); antídoto/cierre/regeneración/curación (`test_correcciones_enunciado`, `test_puertas_reciprocas_d`); contenido pendiente (`test_precarga_offline`); replay incompatible (`test_correcciones_enunciado`); pergamino que revierte recolección de otro pergamino (`test_regresiones_juego`, `test_integridad_operaciones`). Estado C para esos escenarios, condicionado a la extracción de P1.

## Matriz de Parte II

| Sección / obligación | Estado | Evidencia y límite |
|---|---|---|
| 1 propósito / continuidad P1 | C | Cuatro capacidades conectadas al arranque ordinario, consola/GUI/replay; P1 permanece en regresión. |
| 2.1 versión fijada y agente | C | README fija spec-kit v1.2.3 y Codex; `.specify/` y habilidades versionadas. |
| 2.2 una spec/plan/tasks por capacidad y flujo | C / NV | Cuatro capacidades y artefactos existentes; bitácoras/historial documentan fases. No puede certificarse cada invocación humana ausente de la fuente. |
| 2.3 constitución y principios | C | `.specify/memory/constitution.md` v1.1.0: estructuras, determinismo, MVC, datos externos, red, bench y spec previa. |
| 2.4 separación reglas/plan/tareas | C | Especificaciones funcionales, planes técnicos y tareas con requisitos; RE-01..04 preceden a este código. |
| 2.5 trazabilidad de escenarios/casos B | C | Matriz de 23 casos en `ESTADO_ENTREGA.md`, specs, tareas, implementación y tests citados. |
| 2.6 historial y bitácora íntegros | I | Excepción histórica `33d97ac` y dos finales de prompts; no reparables inventando historial. |
| 3.1 terreno, costo ausente100, fórmula/mínimo1 | C | `test_costos_terreno`, `test_velocidad_terreno`, `test_eventos_terreno`. Costos reales de ida/vuelta auditados. |
| 3.2 cazador: ataque/ruta/rango/menor vecino/conocimiento total | C | `test_decision_cazador`, `test_rutas_cazador`, `test_turno_cazador`, `test_localidad_rutas`. `rango=null` ilimitado conforme aclaración registrada; no default para ausente. |
| 3.3 conocimiento y antorcha, inversos/persistencia | C | `test_conocimiento`, `test_entrada_conocimiento_motor`, `test_partida_completa`, `test_mapa_visual`; GUI nativa con 1 explorada/3 avistadas a t=0. Puertas remotas mantienen interpretación conservadora IA-05, no respuesta atribuida al profesor. |
| 3.4 ir a: ruta conocida, pasos, paradas, log/retroceso | C | `test_viaje`, `test_controlador_viaje`, `test_controlador_ac_real`, `test_hechos_paso_motor`. No abre puertas automáticamente. |
| 3.5 verificación, orden de llaves, frontera/ciclo y forzar | C | `test_resolubilidad`, `test_verificacion_datos`, `test_verificacion_entrega`; cripta05 no resoluble y reporte concreto de ciclo. |
| 3.6 historia por tiempo/#k, sin efectos, retroceso/carga/replay | C | `test_linea_tiempo`, `test_historia_motor`, `test_persistencia_historia`, `test_modos_historia`; RE-01 también con historia/binario reales. |
| 4.1–4.3 costos/rango/llaves, versiones y presupuesto | C | `test_entrega_datos_terreno`, `test_verificacion_datos`; datos reales y fría/caliente. No se borran manualmente versiones para simular invalidación. |
| 5.1 búsquedas propias, localidad y muchos cazadores | C | Heap, generaciones, localidad con exterior creciente, alternativas individuales/compartidas y desempates. |
| 5.2 invalidación vs cálculo fresco y puertas estables/inestables | C | `test_validez_rutas`, `test_restauracion_rutas`, `test_rutas_compartidas`; bench parte-dos y terreno-cazador. |
| 5.3 mapa local, deltas reversibles y ruta conocida | C | `test_conocimiento_secuencias`, `test_conocimiento_rutas`, `test_partida_completa`; no se copia mapa completo por evento. |
| 5.4 resolubilidad incremental y diagnóstico | C / NV | Recorrido/diagnóstico incremental y alternativa repetitiva medidos. Normalización O(N log N) declarada: la aceptación de «aproximadamente lineal» para el total es interpretación a confirmar, no prueba de O(N) estricto. |
| 5.5 K, memoria, búsqueda, recorte y ≥3 alternativas | C | K10/50/100/sin controles; 5.000 acciones, tiempos/memoria y alternativa inversa en bench historia. |
| 5.6 repetir agenda/historial bajo carga nueva | C | Bench terreno-cazador y ciclo-historia, referencia anterior preservada e igualdad de estados/historia/azar. |
| 6.1 cuatro presupuestos | C en muestras | Tablas temporales; conservar excesos históricos. No garantiza cualquier hardware/carga. |
| 6.2 restricciones | C | Estructuras y ordenamientos propios en producción; no se introdujeron dependencias nuevas. |
| 6.3 escenarios bench y semilla | C | `bench.py`, `test_bench_escenarios_rutas`, `test_bench_resolubilidad`, `test_bench_historia`, `test_bench_terreno_cazador`. |
| 7.1 decisiones con enlaces/deriva/antes-después | C | DECISIONES y planes; RC-01/fortalecimiento/VI/RE preservan cambios y evidencia. |
| 7.2 estructura y comandos README | C | Constitution/spec/plan/tasks/DECISIONES/PROMPTS/README; verificar, forzar, checkpoint, hasta y aceptación documentados. |
| 7.3 interfaz mínima y costos/cazador | C | Mapa gráfico/listado, viajar e informes, historia, reporte inicial, costos y etiqueta Cazador. Tests de GUI y observación nativa. |
| 7.4 defensa y 7.5 calificación | NV | No sustituibles por tests ni por este informe. |
| 8 preguntas orientativas | NV | No exigen respuestas escritas; se conservan decisiones y evidencia técnica. |
| Apéndice A | C | Costos, rango y ubicaciones persistidos por sus versiones; pruebas de entrega de datos. |
| Apéndice B, 23 casos | C | Mapeo completo en `ESTADO_ENTREGA.md`; suite más comparación independiente de 41 casos. |

## Mapas y contenido publicados

Auditoría independiente de JSON completo descargado, con recorrido por llaves hasta punto fijo, además de validaciones normales. En las cinco versiones: cero destinos inexistentes, cero costos inválidos, cero diferencias de costo entre retornos, todos los arcos con retorno y ninguna ubicación de llave contradice el contenido de su sala. Para llaves de enemigos también se contrastó la instancia de origen; el catálogo normal valida su botín. Esto verifica las versiones indicadas, no mapas futuros.

| Cripta | Versión | Salas / salidas | Alcanzables con llaves | Resultado |
|---|---|---:|---:|---|
| 02 Catacumbas menores | 52532a77ee04 | 20 / 40 | 20 | resoluble |
| 03 Catacumbas medias | f9186ac25124 | 40 / 80 | 40 | resoluble |
| 04 Catacumbas profundas | 7074a17814ad | 50 / 100 | 50 | resoluble |
| 05 Cripta sellada | 48bfa3b75055 | 24 / 48 | 20 | no resoluble deliberada |
| 06 Cripta de referencia | f9ed9afa683d | 300 / 760 | 300 | resoluble |

Las criptas 02/03/04/05 tienen respectivamente 2/3/3/4 parejas con metadatos de puerta declarados en un solo lado; la 06 no tiene esas diferencias. Son datos del servicio, no conexiones inventadas por la vista. Motivaron RE-01. La 05 tiene dependencias circulares entre las llaves hierro/negra: el reporte muestra sus ubicaciones, la frontera y el ciclo. No se «arregla» volviéndola ganable ni se salta el bloqueo sin `--forzar`.

Listado actual: 02–06. La copia histórica conserva 01 «Osario menor»; el selector normal lee el listado del servicio y offline el del paquete elegido. Cripta sellada tiene 1 sabueso cazador, 8 ratas y 1 guardián; 4 antorchas. La referencia tiene 25 sabuesos y 11 espectros cazadores, 36 ratas, 2 guardianes y 1 carcelero; 1 antorcha. La niebla es funcionalidad del cliente sobre cualquier mapa, no una entidad enviada por la API.

La cartografía es un **esquema de conexiones**, no un plano que coloca N/S/E/O en sus posiciones cardinales. Etiquetas y detalle conservan dirección/costo reales; la vista no altera topología. Desconocidas sin nodo, avistadas con ?, exploradas con nombre y salidas; niebla decorativa estática. El botón permite seleccionar/zoom/listado/viaje ordinario. La inspección nativa comprobó apertura desde partida normal y cierre, sin avanzar t=0.

Los cazadores tienen ilustración y **animación común de reposo/reacción al daño**, no spritesheets propios de caminar o atacar. RE-03 comprobó desplazamiento del sprite y reacción al daño para sabueso, espectro y un ID inédito, conservación al apagar animaciones y estado del motor idéntico. RE-02 cargó una cripta nueva mediante fábrica/controlador/vista, mantuvo ? en suelo/inventario y despachó recoger/equipar/mover a WAV reales desde CWD ajeno, con backend espía asíncrono. No prueba audición física. Sonido se activa en la casilla Sonido; `CRIPTA_SIN_AUDIO=1` silencia las pruebas y la consola no tiene audio.

## Verificación y rendimiento

Base previa a la corrección: 828 tests en 299,876 s, OK, dos opciones omitidas. Selección tras la corrección: 24 tests OK y luego 13 de puertas/contenido/animación OK. Comparación independiente: 41 tests en 0,435 s, OK. Copia limpia: 20 tests en 7,987 s, OK; reutiliza Python/dependencias y no sustituye instalar desde cero ni inspeccionar PNG.

API real repetida: 1 prueba con cinco criptas y dos fases en 88,555 s, OK, catálogo 4b9e75a42be5. Consumo fría/caliente: 02 13/3 de 23, 03 16/3 de 42, 04 17/3 de 52, 05 14/3 de 25, 06 46/3 de 63. Descargas independientes adicionales para inspección respetaron sus presupuestos y no se cuentan como la misma ejecución de partida.

Primera medición aislada de esta revisión, anterior a RE-01: referencia 06 de 300 salas, 30 cazadores inyectados/mapa completo, sin red/renderizado: ciclo máximo 14,595 ms (0/60 sobre 20); paso máximo 2,558 ms (0/60 sobre 5); verificador máximo 12,602 ms (60 repeticiones). Historia5000 acciones/K50, 111 consultas: máximo 1,2396 ms, 0 sobre 50; memoria 5.673.260 B. Se midieron también K10, K100, sin controles e inversa; la alternativa sin controles alcanzó77,2504 ms y no es el valor predeterminado.

Regresión final posterior a RE-01: **834 tests en 244,140 s, OK (skipped=2), cero fallos/errores**. Las dos opciones son comparación histórica y API real, aprobadas por separado arriba. No se suman sus cantidades a834.

Mediciones finales, Python3.14.6/Windows11, semilla20261001, sin suite/GUI/red concurrentes:

| Operación | Máximo | Límite | Muestras / excesos |
|---|---:|---:|---|
| Ciclo, referencia 06 y 30 cazadores inyectados/historia/mapa completo | 9,275 ms | 20 ms | 120 /0 |
| Paso conocido, mapa completo | 2,342 ms | 5 ms | 120 /0 |
| Verificación completa, referencia 06 de 300 salas | 12,586 ms | 200 ms | 120 /0 |
| Historia, 5.000 acciones yK50 predeterminado | 0,5745 ms | 50 ms | 111 /0 |

Historia K50 ocupa5.673.260 B en esta carga sintética de 300 campos y 101 controles; K10/100/sin controles también medidos. Sin controles llegó a63,8869 ms en consulta total (25/111 sobre 50): es una alternativa descartada, no el valor de producción. El heap vigente dio mediana1,8939 ms frente a3,0676 ms del anterior, con decisiones iguales. No se atribuye la variación temporal entre series a RE-01: este incremento corrige puertas, no cambia esos algoritmos.

Reproducción: `python main.py --bench --subsistemas parte-dos resolubilidad --paquete PAQUETE --cripta cripta-06 --repeticiones 120` y `python main.py --bench --subsistemas historia --operaciones 5000 --salas 300 --repeticiones 3`. PAQUETE debe contener esa versión compatible. [Salida completa de los benchmarks](revision-bench-2026-11-15.txt) y [resumen de evidencia/mapas](revision-evidencia-2026-11-15.json).

Logs de trabajo fuera de Git en `New project/tmp/revision-20261115-*`; mediciones anteriores y sus excesos permanecen en los artefactos versionados previos. No se suman suites solapadas, no se descartan muestras lentas ni se certifica ausencia de bugs futuros.

Publicación comprobada: push ordinario de especificación `6309e20` y corrección/informe `10f5f78`. `git ls-remote` devuelve `10f5f78ebfeaab7fd65f1c0ae1f81fb097652b56` para `refs/heads/004-linea-tiempo`, idéntico a HEAD en esa comprobación. Este cierre documental se confirma después; main y ramas ajenas no se modificaron.
