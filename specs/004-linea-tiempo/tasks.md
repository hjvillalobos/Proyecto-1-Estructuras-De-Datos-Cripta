# Tareas — línea de tiempo

- [x] VD-T01 Diálogo temático, selección explorada/validación, Enter/Escape/X y controlador sin mutación al cancelar; pruebas y evidencia (VD-01).

## Replay gráfico RP

- [x] RP-T01 Reconectar lanzador GUI y modo independiente, conservando CLI/hasta sin vista (RP-01/03/04).
- [x] RP-T02 Fábrica completa/historia, cargas/retroceso, costos/animaciones y errores/cierre (RP-01/02/03).
- [x] RP-T03 Probar menú/controlador, aislamiento de archivos/estado/sesión, controles y modos CLI; registrar evidencia/límites (RP-01..04).
- [ ] RP-T04 Publicar cambios validados en004-linea-tiempo y verificar remoto (RP-01..04).

## Seguimiento UX

- [x] UX-T01 Reproducir replay local, población/daño y victoria de mapas resolubles (UX-03).
- [x] UX-T02 Restaurar elección cancelable y reinicio de partida activa con pruebas de vista/controlador/aplicación (UX-01).
- [x] UX-T03 Mostrar ID y objetivo sin filtrar conocimiento; comprobar salida y regreso desde cámara secundaria (UX-02).
- [x] UX-T04 Ejecutar regresiones pertinentes, documentar evidencia/limitaciones y publicar en 004-linea-tiempo (UX-01..03).

Publicación UX comprobada: `d88c85656610dfffc4b98431fdbfba93e1d870ec` coincide con `refs/heads/004-linea-tiempo` en `git ls-remote`; avance ordinario, sin cambios en main ni ramas ajenas. Este registro documental se confirma después.

## Revisión de entrega RE (2026-11-15)

- [x] RE-T01 Reproducir apertura inversa sin metadatos, respetar llave/cierre y validar binario/retroceso y ausencia/ambigüedad de retorno (RE-01, IA-04).
- [x] RE-T02 Comprobar marcadores de objetos nuevos, sonidos con WAV reales y animación común de cazadores sin mutar el motor (RE-02/03, VI-01).
- [x] RE-T03 Auditar datos publicados/mapas y cubrir Parte I/II en matriz de evidencia, faltantes y severidad; conservar fuentes y prompts (RE-04, RF-03).
- [x] RE-T04 Ejecutar regresión y mediciones aisladas, publicar resultados y enviar cambios validados a 004-linea-tiempo (RE-01..04).

Publicación RE verificada: `10f5f78ebfeaab7fd65f1c0ae1f81fb097652b56` coincide con `refs/heads/004-linea-tiempo` mediante `git ls-remote`; push ordinario, sin modificar main ni ramas ajenas. El commit documental posterior registra ese resultado.

> **Estado vigente de entrega:** las cuatro capacidades están integradas en `004-linea-tiempo`. Consultar [estado, trazabilidad y límites actuales](../../ESTADO_ENTREGA.md). Los balances y restricciones de autorización fechados anteriores son registros históricos, no bloqueos de la implementación actual. La revisión humana y los faltantes auténticos no se dan por resueltos mediante este aviso.


Las marcas completadas incluyen el núcleo y los consumidores de D. La aceptación con productores reales de A, B y C se registra por separado.

## Incremento de aceptación MC-01 — 2026-11-13

- [x] Preparar el caso MC-01 en `tests/test_controlador_ac_real.py`: guardar,
  descubrir y explorar después, cargar recuperando motor/historia/mapa y
  continuar de forma determinista (FR-011, SC-004). Registrar el fallo actual
  sin skip ni expectedFailure y ejecutar la regresión seleccionada de D.
- [x] Repetir MC-01 con la conexión completa y sustituir DX-06 por carga incoherente sin publicación parcial. Cierre de T003/T010/T021 documentado en integracion-completa.md; los pendientes anteriores se conservan como historial.

## Preparación y fundamento

- [x] T001 Registrar y clasificar la base de pruebas en specs/004-linea-tiempo/baseline.md, sin confundir fallos heredados con cambios nuevos (FR-011, FR-017).
- [x] T002 Implementar contratos tipados serializables en modelo/snapshots.py: tiempo entero >=0, secuencia estable, acción desde 1, K >=1, registros independientes del estado vivo (FR-002, FR-003, FR-008, FR-010).
- [x] T003 Incorporar captura por evento y frontera de acción en modelo/juego.py y modelo/historial.py; conservar retroceso de cinco acciones y cerrar lote temporal antes de publicar decisión (FR-002, FR-006, FR-010).

## US1 — consultar el pasado (P1)

- [x] T004 [US1] Crear pruebas H1,H3,H4, EX01,EX02,EX03,EX08 en tests/test_linea_tiempo.py citando requisitos (FR-001, FR-002, FR-003, FR-004, FR-005, FR-020).
- [x] T005 [US1] Implementar registro segmentado, base inicial, checkpoints cada K y búsqueda binaria propia en modelo/linea_tiempo.py; sin snapshots por acción (FR-006, FR-009, FR-010).
- [x] T006 [US1] Reconstruir estado aislado por tiempo y ordinal en modelo/linea_tiempo.py, sin red ni mutación del motor/azar/cachés; <=K acciones (FR-001, FR-002, FR-003, FR-004, FR-005, FR-010, FR-020).
- [x] T007 [US1] Incorporar comando y resumen histórico en controlador/controlador.py y vista/consola.py (FR-001, FR-003, FR-004, FR-005, FR-020).

## US2 — conservar historia y corregir rama (P1)

- [x] T008 [US2] Crear pruebas H2,H6,EX04,EX07 en tests/test_persistencia_historia.py; verificar inventario de pergaminos, recorte, nueva rama y corrupción (FR-007, FR-011, FR-012).
- [x] T009 [US2] Recortar sufijo y registrar corrección persistente de pergaminos en modelo/linea_tiempo.py; liberar bloques descartados sin recorrer prefijo (FR-006, FR-007, FR-009).
- [x] T010 [US2] Conectar cambios de conocimiento e inventario mediante modelo/snapshots.py y productores del motor; incluir mapa recordado (FR-004, FR-007, FR-011).

Avance parcial de T010/T017/T018 (2026-11-10): el consumidor de D presenta la
proyección estructurada y los campos históricos reales de C. El inventario
conserva enlaces, orden, equipo y cursor; el mapa histórico usa solo recuerdos
del instante consultado. Se preparó `ResultadoAccion.hechos_paso` y acceso al
resultado completo en el controlador, conservando su retorno booleano. El
productor del motor, el viaje por pasos en la interfaz y la restauración
conjunta siguen pendientes. No se completa T010 por estas pruebas.

Validación: `tests.test_presentacion_conocimiento` agrega seis pruebas con
conocimiento/inventario de C, deltas, binario y recorte reales de D, ausencia
de HTTP y compatibilidad del resultado de acción. Regresión seleccionada de
15 módulos: 128 pruebas, 126 aprobadas y dos omisiones de historia con motor
real. No representa certificación de una partida integrada ni de toda la suite.
- [x] T011 [US2] Implementar formato binario 4 con historia, K, RNG y versiones en datos/guardado_binario.py; rechazar P1, validar límites/CRC y carga atómica (FR-008, FR-011, FR-012).

Incremento independiente dentro de T008/T011 (no completa el formato integrado):

- [x] T022 [US2] Definir exportación/importación tipada de rama vigente en modelo/snapshots.py y modelo/linea_tiempo.py; regenerar controles conservando K y correcciones (FR-007, FR-009, FR-010, FR-011).
- [x] T023 [US2] Probar igualdad de consultas, continuación, correcciones, RNG sintético, errores y rechazo CRPT en tests/test_persistencia_historia.py (FR-011, FR-012, FR-020).
- [x] T024 [US2] Implementar fragmento binario CRLH versionado y escritura atómica en datos/historia_binaria.py, sin modificar guardado de partidas (FR-011, FR-012).

- [x] T025 Clasificar errores esperados en modelo/errores_historia.py; normalizar fallos de entrada/archivo, preservar el error principal y verificar atomicidad en tests/test_errores_historia.py. Completar decisiones, prompts y matriz en specs/004-linea-tiempo/errores.md (FR-005, FR-011, FR-012, FR-020).

## US3 — modos sin vista y preparación de partida (P2)

- [x] T012 [US3] Crear pruebas H5,R4,EX05 y argumentos inválidos en tests/test_modos_historia.py con constructores de vista que fallen si son llamados (FR-008, FR-013, FR-014, FR-015, FR-016, FR-017, FR-020).
- [x] T013 [US3] Añadir K positivo, --hasta, --verificar y --forzar, validar exclusiones y separar rutas sin vista en main.py (FR-008, FR-013, FR-015, FR-016, FR-017, FR-020).
- [x] T014 [US3] Reproducir hasta frontera y emitir resumen común/aviso en controlador/replay.py y datos/bitacora_replay.py, conservando órdenes de retroceso/carga (FR-004, FR-013, FR-014, FR-017).
- [x] T015 [US3] Conectar reporte del verificador antes de iniciar en controlador/aplicacion.py; no implementar aquí el algoritmo de resolubilidad (FR-015, FR-016).

## US4 — presentación e integración de comandos (P2)

- [x] T016 [US4] Crear pruebas EX06 de mapa filtrado, costos, cazador y viaje en tests/test_comandos_integracion.py (FR-018, FR-019).
- [x] T017 [US4] Interpretar viaje/mapa y mostrar motivo, costos y comportamiento en controlador/controlador.py, vista/consola.py y vista/grafica.py; delegar reglas a productores (FR-018, FR-019).
- [x] T018 [US4] Registrar pasos como movimientos y orden como comentario en datos/bitacora_replay.py; no registrar consultas (FR-005, FR-019).

Incremento de D del 2026-11-10: el controlador ya consume `ControlViaje` real
de C por pasos. Inicia la orden sin mover, acepta comandos entre propuestas y
ejecuta cada paso por la ruta ordinaria de acción/animación/replay. Conserva
todas las causas y cancela antes de acciones manuales, pergamino, carga,
replay, salida y nueva orden. Detiene el intento ante falta/incoherencia de
hechos, excepciones o fallo de bitácora. La consola interactiva y la ventana
permiten continuación automática; la entrada inyectada usa Enter por paso.

`tests/test_controlador_viaje.py` prueba el consumidor con mapa, planificador
y control reales de C y hechos explícitos de un motor de prueba. Incluye
alternativa tras observar puerta cerrada, propuesta invalidada, rechazo sin
progreso, ausencia de hechos, fallo de replay y entrada/cierre de ventana.
No sustituye la aceptación con un motor de producción. Se mantienen abiertas
T003, T010 y T021 hasta disponer de los productores y la restauración completa.

La revisión de toda la suite detectó tres preparaciones incompletas de pruebas
de D: menú oculto sin dimensiones y dobles sin escena/precarga. Se completaron
sin retirar aserciones. Además, el menú cancela su callback de precarga al
destruirse, evitando ejecutarlo sobre un canvas destruido.

Verificación final del incremento: 701 pruebas descubiertas, 695 aprobadas,
6 omisiones y ningún fallo/error. Las 18 pruebas nuevas del viaje de D pasan.
La [evidencia y omisiones](aceptacion.md#viaje-por-pasos-y-cierre-de-regresiones-de-d-2026-11-10)
conserva los límites de integración y rendimiento; no completa T003/T010/T021.

## Medición y cierre

- [x] T019 Comparar K=10,50,100 y sin checkpoints; dirección, búsqueda, reconstrucción, memoria y recorte con >=5000 acciones en bench.py (FR-009, FR-010, NFR-001, NFR-002, NFR-003, SC-003).
- [x] T020 Añadir pruebas de igualdad del estado tras consulta, carga y continuación en tests/test_persistencia_historia.py (NFR-004, SC-004).
- [x] T021 Actualizar README.md, PROMPTS_LLM.md y DECISIONES.md con comandos, trazabilidad, mediciones reales y elección final de K; ejecutar regresiones y aceptación (FR-001–FR-020, NFR-001–NFR-004, SC-001, SC-002).

## Dependencias y estrategia

T001 → T002 → US1 sintética (T004–T006); T003 y T010 conectan los productores antes de la aceptación integrada. T009 puede probarse con cambios sintéticos sin T008 de persistencia binaria. US3 depende de US1 y persistencia para replay de cargas; bloqueo de inicio requiere contrato del verificador. US4 requiere productores de conocimiento y viaje. MVP: US1 con cambios sintéticos y pruebas H1/H3/H4. Luego incorporar captura real y persistencia. T019–T021 cierran aceptación, no preceden al núcleo.

Trabajo independiente posible: fixtures de US3 y US4 una vez fijados contratos; no editar main.py ni snapshots.py simultáneamente sin coordinación. Las tareas aquí se ejecutarán secuencialmente salvo decisión explícita del equipo.


Avance 2026-11-02: T002/T004–T006/T009 se verificaron en aislamiento con registros sintéticos. H1–H4 cubren el núcleo; su aceptación integrada requiere T003/T010 y comandos reales. La persistencia de T008/T011 sigue pendiente.


Avance de persistencia independiente 2026-11-02: T022–T024 completos. T008/T011/T020 permanecen pendientes para el guardado de partida integrado y captura real del motor. El fragmento CRLH conserva base y deltas; reconstruye checkpoints al cargar. El lector rechaza CRPT explícitamente, pero eso no certifica aún H6 mediante el comando de carga del juego.

Avance de errores 2026-11-02: T025 completada en el núcleo independiente. Contrato y pruebas documentados en errores.md; mostrar mensajes desde el controlador real sigue dentro de las tareas de integración pendientes.

Avance 2026-11-07: consumidor de historia, formato v4, replay sin vista,
verificación y presentación implementados para el protocolo propuesto.
Las pruebas de D y las dos cargas sintéticas de T019 tienen evidencia
reproducible. T003 y T010 conservan sus entregas de productores y T021
queda abierto para aceptación conjunta, límites con cripta de referencia
y medición integrada de la carga nueva sobre estructuras de Parte I.

Avance 2026-11-08. R4 y el benchmark de resolubilidad se verificaron con
B integrado tras el PR #22. [Evidencia de aceptación](aceptacion.md).
T021 sigue abierto para la aceptación de historia con A/C y las
mediciones de Parte I con la carga nueva. T003 y T010 siguen pendientes.

Avance de T021. La descarga incluye las llaves validadas de la versión
solicitada. Se cubren la verificación del paquete exportado, el cambio de
versión y el bloqueo con `--forzar` cuando faltan datos.
[Evidencia de aceptación](aceptacion.md#paquete-offline-y-datos-incompletos).

Avance de T021 y de la conexión de D para T030. El benchmark acepta un
paquete offline y reporta la preparación separada del análisis. Se
verificó la selección de versión y el rechazo de paquetes incompletos.
Quedan la revisión de B y la medición oficial.
[Evidencia de aceptación](aceptacion.md#benchmark-de-un-paquete-offline).

Avance del 2026-11-09. El recorrido conjunto de historia, guardado, carga
y replay pasó con el productor de prueba. La versión con el motor real
queda preparada para cuando A entregue la captura y la restauración.
Se midió AC-20 en la mayor cripta publicada, con un máximo incremental
de 16.140 ms. T021 conserva los pendientes de integración de A/C y las
mediciones de Parte I con la carga nueva.
[Pruebas y medición de referencia](aceptacion.md#resolubilidad-de-referencia-2026-11-09).

Actualización tras integrar main en `2b347da` (2026-11-10). La revisión conjunta
de B y D ya cerró T025/T026/T030/T031/T034 de la especificación de resolubilidad;
las notas anteriores de revisión pendiente describen estados históricos.
El detalle está en el apartado «Cierre de la integración B y D» de
`specs/001-verificador-resolubilidad/tasks.md`. Se repitió la regresión de
integración en este árbol: 92 pruebas, 89 aprobadas y tres omisiones opcionales.
El comando de `cripta-06` reconoce 300 salas, diez muestras por estrategia y
cero solicitudes.

Avance parcial de T003: `controlador/receptor_h3.py` consume el lote optativo
que A ya entrega para sala/jugador. Cuatro pruebas nuevas de D usan el motor
real, validan frontera/ordinal/orden, consultan 99/100/#2, recargan el fragmento
histórico y rechazan lotes inválidos sin publicación parcial. La integración
completa del motor y el guardado de partida siguen pendientes; no se elimina
la omisión de esos casos ni se completa T003 por este ensayo acotado.

Aceptación posterior al merge de main y al receptor de D: 709 pruebas,
703 aprobadas, seis omitidas y ningún fallo/error. Se hizo independiente de la
caché de trabajo la prueba de reinicio de D; conserva sus comprobaciones.
[Evidencia y límites](aceptacion.md#main-integrado-y-receptor-h3-de-d-2026-11-10).

Preparación A–D del 2026-11-12: siete pruebas de aceptación PD-01..04 para
puertas recíprocas, guardado/carga, cierre único, retroceso y continuación.
Una pasa y seis fallan por entrega bilateral/exportación todavía pendientes
del motor; no se omiten ni se marcan como fallos esperados. Las comprobaciones
de retroceso posteriores a la precondición bilateral aún no se alcanzan.
La regresión seleccionada conserva 48 aprobaciones y dos omisiones conocidas.
[Resultados y pendientes](aceptacion.md#preparación-de-puertas-recíprocas-ad-2026-11-12).
T003/T010/T021 permanecen abiertas; no hay modificación de producción ni formato.

Incremento DX-01..06 del 2026-11-12: nueve pruebas de D con controlador,
productor histórico real de A activado offline, datos B y mapa/control de viaje
reales de C. Pasan consultas puras, guardar/cargar/continuar v4, rechazo de
archivos inválidos, pergamino, replay sin vistas y sin archivo de carga original,
mapa tras entradas físicas y cancelación. También se verifican los límites
del productor: ausencia de hechos de viaje y rechazo de carga con mapa activo.
No se activan opciones de prueba en producción. Se actualizan README, plan y
DECISIONES con comandos/alcance reales. T003/T010/T021 siguen abiertas por
captura completa, inventario/mapa histórico, persistencia conjunta y aceptación
de producción/mediciones; este incremento sustituye parte de la evidencia con
dobles por evidencia de integración real, sin declarar cierre global.


## Integración completa — 2026-11-14

## Fortalecimiento RF-01..03 — trabajo vigente

## RC-01 — margen del ciclo integrado

## VI-01..05 — presentación autorizada

- [x] VI-T01 Crear sprite de cazador y mapa nativo con privacidad, disposición determinista y controles accesibles (VI-01/02/04).
- [x] VI-T02 Conectar la proyección filtrada a GUI y viaje ordinario, manteniendo consola y reglas (VI-02/03/04).
- [x] VI-T03 Auditar contrato y datos API, casos desconocidos/futuros, presupuesto y versiones (VI-05).
- [x] VI-T04 Probar privacidad/inmutabilidad, GUI real, regresiones y medir motor sin render; documentar prompts/evidencia (VI-01..05).
- [x] VI-T05 Confirmar cambios y publicar exclusivamente en 004-linea-tiempo (VI-01..05).

Análisis previo: incremento de presentación sobre FR-018/019. No cambia reglas ni formato binario, no introduce rutas de búsqueda de biblioteca, ni activa contenido para dibujar. La usuaria autoriza diseño visual a criterio del agente y publicación en su rama.

VI-T01..04 comprobadas: siete pruebas nuevas, suite 828 en 214.910 s sin fallos/errores (dos opciones identificadas), API real cinco criptas fría/caliente OK, copia limpia de fuentes 20 pruebas en 6.476 s OK. Tres ilustraciones nuevas y 152 composiciones con píxeles idénticos. Benchmark aislado con estado/historia/azar iguales: motor máximo 9.1013 ms y 0/600 sobre 20; conservar pico auxiliar de viaje 5.5273 ms, 1/600 sobre 5. Evidencia y límites en visual-api-2026-11-14.md y visual-mediciones.json.

VI-T05 comprobada: push ordinario de 51bf7fa a origin/004-linea-tiempo; ls-remote confirma 51bf7fafc55913191630e235495202774d0a301a. Main permanece en 049a990413ab536ba98acf948903cb57b30d17fc. Los cambios previos de A están incluidos, sin sobrescritura ni force-push.

- [x] RC-T01 Conservar referencia anterior y comprobar igualdad de proyecciones/deltas en movimiento, llegada, daño, muerte, inventario, efectos, reversión y carga (RC-01).
- [x] RC-T02 Reutilizar solo orden de referencias vigente; comparar campos fijos y enemigos sin reordenar por evento (RC-01).
- [x] RC-T03 Benchmark pareado de ciclos completos antes/después con estados finales iguales, repeticiones independientes y checkpoints. Regresión completa, documentación y prompts (RC-01).

- [x] RF-T01 Comparar heap/rutas antes y después sobre las mismas entradas, comprobar orden total y generaciones (RF-01).
- [x] RF-T02 Implementar almacenamiento compacto propio para IDs dispersos, conectar motor/mapa/rastro, probar persistencia, historia y replay sin renumeración (RF-02).
- [x] RF-T03 Consolidar estado actual y matriz de trazabilidad de los 23 casos obligatorios; preservar antecedentes y faltantes reales (RF-03).
- [x] RF-T04 Ejecutar regresión completa, comparaciones, benchmarks offline y arranque desde copia limpia; registrar muestras y límites en DECISIONES y prompts (RF-01..03).

Orden: especificación confirmada antes de código; RF-T01/RF-T02 antes de regresión final; RF-T03 antes de cierre RF-T04. La autorización actual permite cambios en A/B/C/D; no requiere consultas adicionales sobre decisiones técnicas deducibles.

- [x] IC-01 Puertas recíprocas y exportación de extremos no visitados (IA-04, PD-01..04).
- [x] IC-02 Mapa de producción, observaciones, antorcha e inversos (IA-01/05).
- [x] IC-03 Productor completo y carga conjunta validada (IA-02/03, FR-011, MC-01).
- [x] IC-04 Hechos reales y conexión de viaje/replay/CLI (IA-01/06).
- [x] IC-05 Regresiones, benchmarks comparativos, documentación y publicación (IA-07..09).


Cierre técnico 2026-11-14: IC-01..04 y T003/T010/T021 implementados y validados. La documentación histórica no constituye el estado actual; ver integracion-completa.md. IC-05 conserva el paso de publicación hasta verificar el remoto.

Publicación verificada 2026-11-14: integración y documentación 1c35819 enviadas mediante push ordinario a origin/004-linea-tiempo, incorporando f8e10ef de A. IC-05 completada.

## Aceptación adicional sin defensa — 2026-11-14

- [x] QA-01 Repetir comparación aislada de rutas con revisiones reales (41 pruebas).
- [x] QA-02 Completar copia compatible de datos históricos y verificar cuatro victorias/replays, salas y persistencia (dos pruebas).
- [x] QA-03 Verificar todas las criptas publicadas con caché fría/caliente, presupuesto y procesos independientes.
- [x] QA-04 Añadir partidas inéditas completas con tres semillas y replay sin archivo de guardado.
- [x] QA-05 Inspeccionar guardar/cargar, mapa, equipo e historia en GUI nativa.
- [x] QA-06 Documentar fuentes externas faltantes, consultas de interpretación, decisiones y prompts; excluir defensa y envío de mensajes.
- [x] QA-07 Cerrar regresión conjunta y verificar publicación ordinaria en 004-linea-tiempo.

Publicación comprobada: acd84db enviado mediante push ordinario a origin/004-linea-tiempo; suite 810, OK (skipped=2), opciones omitidas aprobadas por separado. Sin cambios en main ni ramas ajenas. La defensa queda excluida.

La recuperación del PDF original y de dos finales de prompts, así como las respuestas del profesor, requieren fuentes externas; no se marcan como resueltas por documentación. Ver qa-adicional-2026-11-14.md.


Cierre RF-01..03: especificación 5bccc94; suite final 814, cero fallos/errores, dos opciones aprobadas por separado. Copia limpia final: 20 pruebas en 6.775 s, OK. Las cuatro cargas de bench finales terminan correctamente, con muestras en fortalecimiento-mediciones.json; trazabilidad vigente en ESTADO_ENTREGA.md. Se conservan los faltantes históricos y no se afirma revisión humana ni nota.

RC-01 cerrado: 818 pruebas en 181.531 s, cero fallos/errores y dos opciones omitidas identificadas. Contraste exacto por evento y cinco series pareadas de 120 ciclos, estados/historia/azar iguales; máximo optimizado 11.931 ms, 0/600 sobre 20. Copia limpia 20 pruebas OK y CLI sintética ejecutada. Referencia y muestras versionadas; ver DECISIONES.md.
