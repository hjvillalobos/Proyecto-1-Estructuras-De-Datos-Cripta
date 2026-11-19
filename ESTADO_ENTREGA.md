# Estado vigente y trazabilidad de entrega

## Estado actual — 18 de noviembre de 2026

**Confirmación previa a la subida autorizada:** sintaxis de 226 fuentes Python correcta. Offline real confirmado en las cinco criptas con HTTP bloqueado: 02/03/04/06 inician, esperan y cierran; 05 se bloquea correctamente por no resoluble. [Salida](specs/004-linea-tiempo/evidencia-publicacion-offline-2026-11-18.txt). Se corrigió CD-07, una prueba que usaba el destino predeterminado con un catálogo falso; ahora usa almacenamiento temporal explícito. Cinco pruebas/8.858 s, OK con una omisión opcional de API; los hashes de 601 archivos y 41 directorios reales se conservan. [Evidencia de aislamiento](specs/004-linea-tiempo/evidencia-aislamiento-offline-2026-11-18.txt). Sin cambios de producción en CD-07; no se repite ni se suma la suite integral. [Índice de prompts de Parte II](PROMPTS_LLM.md#indice-parte-ii), con fechas históricas conservadas y solicitudes nuevas bajo el 18 de noviembre.

**Cierre CD-01..06 — correcciones y documentación:** regresión integral de producción, **905 pruebas/238.658 s, cero fallos/errores y cuatro omisiones opcionales**. [Salida íntegra](specs/004-linea-tiempo/evidencia-cierre-CD-2026-11-18.txt). Después se incorporaron dos pruebas nuevas de objetos inéditos, ejecutadas dentro de un conjunto de 17/14.170 s, OK sin omisiones; no se anuncia una suite integral de 907 ni se suman conjuntos. [Evidencia de criptas/objetos nuevos](specs/004-linea-tiempo/evidencia-objetos-ineditos-2026-11-18.txt). Copia sin cachés/partidas: 20/6.324 s, OK, reutilizando intérprete/dependencias instalados; [salida](specs/004-linea-tiempo/evidencia-copia-CD-2026-11-18.txt).

Se añadieron la comparación reproducible de bitácora y las decisiones heredadas de bitácora/ordenamiento, trazabilidad explícita de A/B/C/D y matriz vigente de errores. Se extrajo el mismo buffer a un módulo sin vista, conservando su importación anterior; el diagnóstico de fallo de grabación distingue inicio, acción, carga y orden de viaje. No cambia ninguna regla de partida. [Mediciones y decisiones](DECISIONES.md). Especificación/plan/tareas previos en `30d89a3` y `cf85272`; correcciones y evidencias de este cierre locales, sin nueva publicación en GitHub. El borrador de regularización y el archivo duplicado de reconstrucciones se retiraron; los textos completos están directamente en `PROMPTS_LLM.md`.

**Contenido inédito:** datos de una cripta nueva con identificadores dispersos, las siete clases de objetos con IDs nuevos y las acciones completas pasaron por verificador, precarga, motor y vista. Sin imagen local, los objetos muestran `?` en suelo/inventario/equipo, conservando nombre/estadísticas/acciones del catálogo. También pasan PNG corrupto, respaldo sin Pillow, selector con siete criptas, partida de 137 salas y guardado/replay inéditos. Esto acredita identificadores nuevos bajo el contrato; no asigna reglas inventadas a clases desconocidas ni garantiza datos arbitrariamente inválidos.

**Auditoría integral adicional de este chat:** 897 pruebas/281.220 s, cero fallos/errores y cuatro omisiones opcionales. Se ejecutaron aparte paquete oficial (2/4.504 s) y comparación de rutas (41/0.408 s), ambos OK; no se suman subconjuntos. Sin repetición de API real ni benchmarks. No se modificó producción. Por instrucción de Belén se completan los dos [prompts completos de la bitácora normal](PROMPTS_LLM.md), conservando sus fragmentos originales y señalando los añadidos. No se consideran originales recuperados ni se modifica el hecho histórico de `33d97ac`. Cambios documentales de esta revisión aún locales, sin nueva publicación.

**Revisión de replay, personajes y offline:** 42 pruebas dirigidas/37.095 s, OK sin omisiones, incluyendo la misma grabación renderizada con Tigre y Tigresa. Las cinco criptas disponibles se verificaron sin HTTP: 02/03/04/06 cargan todas sus salas y ejecutan una acción; 05 se bloquea por no resoluble. Cuatro presupuestos de procesamiento cumplidos: ciclo 10.652 ms, resolubilidad 8.733 ms, paso conocido 2.413 ms e historia K=50 2.0221 ms, con cero excesos en las muestras descritas. La medición visual de ambos personajes se registra por separado de esos límites. [Alcance, documentación y evidencias](specs/004-linea-tiempo/replay-offline-rendimiento-2026-11-18.md). Sin cambios de producción; la suite integral de 881 se conserva como ejecución anterior y no se suman los subconjuntos.

**Revisión posterior de Viajar:** 55 pruebas dirigidas/25.129 s, OK sin omisiones, más recorrido nativo 100→101→102 con reloj 1025→1525 y cancelación previa sin avance. Se añadió una regresión del botón y diálogo completos; no se requirieron cambios de producción. [Alcance y evidencia](specs/004-linea-tiempo/revision-viaje-2026-11-17.md). Las 881 pruebas siguientes corresponden a la suite integral anterior de ese incremento, no a una nueva suite de 882; los conjuntos no se suman.

**Publicación anterior al cierre CD comprobada:** `main` y `004-linea-tiempo` estaban publicados y sincronizados; la base publicada de esta revisión es `cb6a15c`. La entrega es únicamente [el enlace del repositorio](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta). El borrador de solicitud de regularización se retiró por instrucción de Belén; los prompts completos se conservan en `PROMPTS_LLM.md`. Código funcional verificado: `18691b9`; los cierres anteriores a CD añadieron documentación y regresiones sin cambiar producción. El cierre CD local descrito arriba añade el benchmark y corrige mensajes de error. Belén canceló la preparación del ZIP; se retiraron el paquete nuevo y sus archivos auxiliares, sin publicar ese artefacto.

Se completaron las verificaciones separadas de las opciones omitidas: [comparación histórica](specs/004-linea-tiempo/evidencia-cierre-comparacion-2026-11-17.txt), 41 pruebas/0.449 s; [copia limpia](specs/004-linea-tiempo/evidencia-cierre-copia-limpia-2026-11-17.txt), 20 pruebas/7.389 s; [paquete oficial](specs/004-linea-tiempo/evidencia-cierre-paquete-oficial-2026-11-17.txt), 2 pruebas/4.552 s; [API real](specs/004-linea-tiempo/evidencia-cierre-api-real-2026-11-17.txt), 1 prueba/88.401 s, cinco criptas en frío/caliente dentro de presupuesto. Todas terminaron en OK, sin omisiones en esas ejecuciones. Los conjuntos se solapan con la suite de 881 y no se suman para anunciar un total mayor.

**Proceso:** la recopilación de revisión cruzada queda documentada mediante registros de A/C y B/D y consulta de los PR originales. La constitución pide revisión cruzada; no exige dos aprobaciones formales de GitHub por cada PR. [Fuentes y alcance corregido](specs/004-linea-tiempo/revision-cruces-2026-11-17.md#cierre-documental-y-contraste-con-github). Los dos prompts orientativos solicitados están generados en `PROMPTS_LLM.md` como RP-A01/RP-A02, claramente identificados como reconstrucciones actuales. Se conservan los fragmentos originales y la excepción histórica de `33d97ac`; ninguna corrección actual los transforma en hechos distintos.

Actualización HU-02, ya publicada en `main`: Historia presenta el detalle de la referencia: reloj/acciones, resultado, derrotados, inventario histórico con nombres/clases/equipo, efectos, enemigos y mapa con nombres/salidas/costos/recuerdos. **Regresión integral de ese incremento: 881 pruebas en 280.978 s, cero fallos/errores y cuatro omisiones opcionales**. Ciclo con 30 cazadores: máximo 10.453 ms (0/60 sobre 20); paso conocido 2.421 ms (0/60 sobre 5); historia K=50, máximo 1.0886 ms (0/111 sobre 50). Compatibilidad de historias previas sin estadísticas adicionales comprobada, con «no registrado» en vez de valores actuales. [Informe, revisión nativa y evidencias](specs/004-linea-tiempo/historia-detallada-2026-11-17.md). La API real se verificó posteriormente en el cierre descrito arriba.

Antecedente HU-01 en `004-linea-tiempo`: Historia muestra contexto/rangos y la referencia consultada; informe centrado con botón de regreso visible. **100 pruebas dirigidas en 20.165 s, OK, sin omisiones**, con diálogo y controlador/motor reales, pureza y límites tras guardar/cargar; revisión nativa adicional. [Diagnóstico, evidencia y límites](specs/004-linea-tiempo/historia-ui-2026-11-17.md). En ese corte no se repitieron suite completa, API ni benchmarks; HU-02 incorpora la regresión y mediciones posteriores.

Regresión anterior: **873 pruebas en 382.968 s, cero fallos/errores, cuatro omisiones**, durante el incremento de Tigresa, referencia `7d712fa`. La ronda dirigida posterior de personajes y sonidos aprobó **20 pruebas en 34.540 s**. [Informe del incremento](specs/004-linea-tiempo/tigresa-2026-11-17.md) y [salidas originales conservadas](specs/004-linea-tiempo/evidencia-cierre-2026-11-17.txt). Estos resultados son ejecuciones anteriores conservadas y no se suman a las pruebas de HU-01/HU-02.

| Opción omitida en la suite integral | Verificación separada de cierre |
|---|---|
| Clase `tests.test_bench_escenarios_rutas.TestEscenariosRutas` | `python -m utilidades.verificar_conocimiento_rutas`: 41 pruebas/0.449 s, OK sobre las fuentes finales. [Salida](specs/004-linea-tiempo/evidencia-cierre-comparacion-2026-11-17.txt). La omisión de clase se registra una vez y no equivale a un solo método. |
| Dos métodos de `tests.test_criptas_api.TestPaqueteOficial` | Con `CRIPTA_PAQUETE_API`: 2 pruebas/4.552 s, OK. [Salida](specs/004-linea-tiempo/evidencia-cierre-paquete-oficial-2026-11-17.txt). |
| `tests.test_verificacion_entrega.TestApiRealEntrega` | Con `CRIPTA_API_REAL=1`: 1 prueba/88.401 s, OK; cinco criptas en frío/caliente dentro del presupuesto. [Salida](specs/004-linea-tiempo/evidencia-cierre-api-real-2026-11-17.txt). |

La suite integral conservó cuatro omisiones; todas esas opciones se ejecutaron y aprobaron después por separado. La tabla muestra su resultado vigente. Los subconjuntos se solapan y no se suman a las 881 pruebas de la suite.

**Revisión cruzada:** hay declaración del equipo y registros históricos concretos de revisión, además de las pruebas técnicas de Codex. El [informe de cruces](specs/004-linea-tiempo/revision-cruces-2026-11-17.md#registros-históricos-de-revisión-recuperados-en-git) identifica revisiones de C sobre la integración con A y de B sobre cambios de D, junto con aceptación técnica de A y aportes de integración. Se sustituye la conclusión anterior de ausencia total de registros. El cierre distingue revisión documentada y aprobación formal de GitHub, sin convertir esta última en un requisito adicional inexistente.

Las cuatro capacidades están integradas en la aplicación normal y publicadas en `main`. Defensa excluida. Los registros anteriores se mantienen identificados como antecedentes; sus notas de ramas y verificaciones pendientes no describen el estado publicado actual.

## Registros de validaciones anteriores

Actualización documental del 2026-11-17: [revisión de A↔C y B↔D](specs/004-linea-tiempo/revision-cruces-2026-11-17.md), 66 pruebas dirigidas/19.041 s, sin fallos, errores ni omisiones. Belén confirma que todos los integrantes hicieron pruebas y comprobaron el funcionamiento integrado; se incorporan referencias Git de los aportes de A/B/C/D y su integración. La declaración del equipo, la autoría Git y la ejecución de Codex se identifican por separado; los commits no prueban por sí solos aprobación previa de cada PR por ambos responsables. No sustituye las salvedades históricas ni añade esas 66 pruebas al total integral.

Regresión repetida el 2026-11-17 sobre `42ee527`: **863 pruebas en 213.337 s, cero fallos/errores, dos opciones omitidas**. La comparación histórica omitida se ejecutó aparte: 41 pruebas en 0.384 s, OK. Copia sin cachés ni partidas: 20 pruebas en 7.060 s, OK. La API real no se repitió en este corte. Logs locales en `.cache/revision-bugs-20261117/`; los conjuntos se solapan y no se suman. No se modificó código de producción.

Cierre posterior ERR-01: **863 pruebas en 239.241 s, cero fallos/errores, dos opciones omitidas con evidencia separada previa**. El paquete histórico se ejecutó en la suite. La comprobación de copia sin cachés pasó 20 pruebas en 9.357 s. Se corrigió la conservación del error principal al fallar guardado y limpieza de datos; se agruparon 92 evidencias y auxiliares locales en .cache/revisiones/. Constitución 1.1.0 y main intactos; no cambia el estado de los faltantes históricos.

Corte anterior del 2026-11-16: 858 pruebas, cero fallos/errores; las cuatro omisiones opcionales se ejecutaron por separado y aprobaron. Resultados de procesamiento en DECISIONES.md. Las anotaciones fechadas de specs/planes/checklists conservan sus cortes históricos; los encabezados de estado identifican la integración posterior. No se cambió la constitución 1.1.0. En ese corte no se habían identificado los registros de revisión del equipo. La declaración posterior de Belén y las fuentes históricas recuperadas se recogen en el estado actual y en el informe de cruces.

Rama `004-linea-tiempo`. Este documento distingue la entrega integrada de los registros fechados de desarrollo. Defensa excluida. Las cuatro capacidades funcionan desde la aplicación normal, con historia, conocimiento y persistencia conjuntos. Las anotaciones antiguas de entregas parciales no representan capacidades ausentes.

## Reglas e interpretaciones vigentes

RP-01..04 / VD-01: replay gráfico independiente desde menú y partida, controles visibles y fábrica con historia/cargas/retroceso; CLI conservada. Viajar usa diálogo temático con salas exploradas y cancelación sin mutación. **112 pruebas dirigidas en 41.511 s, OK**, más inspección nativa con datos temporales aislados. No se repitieron suite completa ni benchmarks. [Evidencia y límites](specs/004-linea-tiempo/replay-viaje-2026-11-15.md).

Seguimiento UX-01..03: elección cancelable de Salir/reinicio activo, ID/objetivo visible sin revelar salas desconocidas y acreditación de la puerta de salida desde sus extremos recíprocos compatibles. **188 pruebas dirigidas, OK**, más repetición de 8 casos UX tras ajuste de cierre durante carga. Victorias offline ordinarias en 02/03/04/06 y continuación del recorrido local de sala 20 a salida 18; daño observado descontado correctamente, sin modificar dificultad/API. No es una repetición de la suite completa ni de benchmarks. [Causas, evidencia y límites](specs/004-linea-tiempo/seguimiento-ux-2026-11-15.md).

Revisión RE-01..04 (15 de noviembre): corregida la apertura inversa de puertas recíprocas con metadatos de llave/cierre en un solo extremo; presentación/carga/historia coherentes. **834 pruebas en 244.140 s, OK (skipped=2)**; opciones aprobadas por separado: 41 pruebas de comparación histórica y API real de cinco criptas fría/caliente. Mapas publicados auditados: conexiones/costos válidos, 02/03/04/06 resolubles y 05 deliberadamente bloqueada. Objetos nuevos conservan ?, cazadores tienen animación común de reposo/daño, audio despacha WAV válidos desde otro CWD; audición física no verificada. [Matriz completa, corrección, evidencia y pendientes](specs/004-linea-tiempo/revision-entrega-2026-11-15.md). Las cifras siguientes pertenecen a incrementos anteriores.

Actualización VI-01..05: mapa gráfico con niebla que respeta conocimiento, selección/zoom/listado/viaje ordinario, y dibujos nuevos de sabueso, espectro y carcelero. **828 pruebas en 214.910 s, cero fallos/errores**, dos opciones separadas; API real repetida en cinco criptas, fría/caliente y dentro del presupuesto, OK en 87.563 s. Sin cambios en motor, red o datos; 152 composiciones con píxeles idénticos y firmas actualizadas. [Auditoría, trazabilidad y límites](specs/004-linea-tiempo/visual-api-2026-11-14.md). Las cifras RC-01/RF posteriores son antecedentes de sus respectivos incrementos.

- Terreno: costo ausente 100; datos declarados válidos positivos. El motor consume el contrato de datos; no inventa normalizaciones de valores malformados ni salidas inversas. Un `rango=null` explícito es ilimitado según la aclaración comunicada por el usuario; no se inventa un rango por defecto para un cazador sin ese campo.
- Antorcha: explora vecinas y revela nombre/salidas; las puertas solo se observan desde la posición ocupada. No hay observación de puertas remotas ni activación de contenido remoto. Q1 de C deja de ser un bloqueo técnico por la autorización e interpretación documentadas en IA-05.
- Resolubilidad: acumulación de llaves sin trayectoria única aceptada según aclaración registrada del 2026-11-02; se informa esa limitación. Normalización O(N log N), recorrido/diagnóstico lineales más reporte; evidencia empírica para el crecimiento aproximadamente lineal, sin afirmar O(N) total estricto.
- Referencia de medición local: paquete `cripta-06@f9ed9afa683d`, 300 salas. Los resultados corresponden a esa versión; no se inventa una enmienda que cambie los límites 20/200/50/5 ms. Los cazadores inyectados y el mapa completo se identifican como preparación experimental.
- Autorización: la usuaria permite mejorar A/B/C/D. Los límites de propiedad y permisos de las fases individuales quedaron superados para esta integración. Las revisiones del equipo se acreditan mediante su declaración y los registros identificados en el informe de cruces, dentro del alcance de cada fuente.

## Enunciado punto por punto, sin defensa

| Sección Parte II | Implementación / evidencia |
|---|---|
| 2.1–2.3, herramientas y constitución | README fija spec-kit v1.2.3/Codex; `.specify/`, `.agents/skills/` y constitución versionados. |
| 2.4–2.6, especificación, tareas y proceso | Cuatro carpetas de capacidades con spec/plan/tasks; matriz del Apéndice B abajo; PROMPTS_LLM y antecedentes Git. Salvedades históricas al final. |
| 3.1, terreno | `modelo/juego.py`, `modelo/rutas.py`; tests de costos y velocidad de terreno. |
| 3.2, cazador | `modelo/cazador.py`, rutas propias; pruebas de decisión, turnos, localidad y rutas. |
| 3.3, conocimiento | `modelo/conocimiento.py`, `modelo/partida.py`; pruebas de entrada, antorcha e historia. |
| 3.4, viaje | `modelo/viaje.py`, controlador; pruebas de detención y hechos reales de movimiento. |
| 3.5, verificación | `modelo/resolubilidad.py`, `red/verificacion.py`; pruebas sintéticas, offline e inicio bloqueado/forzado. |
| 3.6, historia | `modelo/linea_tiempo.py`, `modelo/partida.py`, persistencia y replay; pruebas por tiempo, ordinal, K, recorte, empates y carga. |
| 4.1–4.3, servicio | Cliente/precarga/catálogo, versiones, ubicaciones de llaves y presupuesto; pruebas de API y modo offline. |
| 5.1–5.2, rutas e invalidación | Dijkstra propio limitado, campo compartido ilimitado y descarte de derivados; bench terreno-cazador y parte-dos comparan alternativas/puertas cambiantes. |
| 5.3, mapa | Índices propios, actualizaciones locales y deltas reversibles; tests de secuencias y ausencia de copia completa al registrar eventos. |
| 5.4, resolubilidad | Incremental frente a recorrido repetido por llave; diagnóstico global y ciclos deterministas; bench incluye normalización/reporte. |
| 5.5, puntos de control | K=50; comparar 10/50/100/sin controles, consultas <=K acciones y recorte de sufijo; evidencia en DECISIONES. |
| 5.6, estructuras de Parte I | Bench terreno-cazador compara agendas e historiales con la carga nueva; parte-dos mide el ciclo integrado. |
| 6.1–6.3, límites/restricciones | Bench sin vistas/red; estructuras y ordenamientos propios. Fortalecimiento mide el heap anterior y optimizado con decisiones iguales. |
| 7.1–7.3, documentos y comandos | DECISIONES, PROMPTS, README, specs, mapa, viaje, historia y reporte inicial disponibles; consola y GUI probadas. |

## Los 23 casos obligatorios del Apéndice B

Rutas de esta tabla relativas a la raíz. La prueba indicada se ejecuta con `python -m unittest tests.NOMBRE_SIN_EXTENSION`. Las especificaciones conservan los escenarios y las tareas originales; IC y RF documentan su integración y fortalecimiento.

| Caso | Requisito / escenario / tarea | Código | Prueba |
|---|---|---|---|
| T1 sin ruta: espera 100 | A FR-008/009, T1, T020–022 | cazador/rutas | tests/test_decision_cazador.py |
| T2 fuera de rango: espera | A FR-009, T2, T020–022 | cazador/rutas | tests/test_turno_cazador.py |
| T3 menor costo, más salas | A FR-008, T3, T019–021 | rutas | tests/test_rutas_cazador.py |
| T4 empate por menor vecino | A FR-010, T4, T026 | rutas | tests/test_rutas_cazador.py |
| T5 cierre entre turnos | A FR-013, T5, T029/033 | rutas/juego/efectos | tests/test_validez_rutas.py, test_rutas_compartidas.py |
| T6 intervalo mínimo 1 | A FR-002/003, T6, T011/015 | juego | tests/test_costos_terreno.py |
| T7 velocidad durante tránsito | A FR-005/006, T7, T012 | juego/efectos | tests/test_velocidad_terreno.py |
| N1 destino sin explorar | C FR-007, C21, T018–019 | conocimiento_rutas | tests/test_conocimiento_rutas.py |
| N2 puerta recordada abierta | C FR-004/008/010, C23/C27, T018/022–024 | conocimiento/viaje | tests/test_conocimiento_rutas.py, test_controlador_viaje.py |
| N3 enemigos dormidos detienen | C FR-009/011, C28, IC-04 | juego/viaje/controlador | tests/test_controlador_ac_real.py, test_hechos_paso_motor.py |
| N4 antorcha sin activar vecinos | C FR-006, N4, IC-02 | partida/juego | tests/test_partida_completa.py, test_entrada_conocimiento_motor.py |
| N5 retroceso de exploración | C FR-014, C12/N5, IC-02 | conocimiento/historial | tests/test_partida_completa.py, test_conocimiento_historia.py |
| N6 retroceso último paso y parada | C FR-015, C29/N6, IC-04 | viaje/partida | tests/test_controlador_viaje.py, test_viaje.py |
| R1 llave autoencerrada y ciclo | B FR-005, AC-06, T015–016 | resolubilidad | tests/test_resolubilidad.py |
| R2 llave soltada por errante | B FR-003/010, AC-03, T005/010 | verificación/resolubilidad | tests/test_resolubilidad.py, test_verificacion_datos.py |
| R3 orden determinista | B FR-004/007, AC-04, T005/012 | resolubilidad | tests/test_resolubilidad.py |
| R4 bloqueo sin forzar | B FR-013 y D FR-016, AC-15, T025–026/IC-01 | aplicación/verificación | tests/test_modos_historia.py, test_verificacion_entrega.py |
| H1 rechazar futuro | D FR-001/020, H1, T004/006 | linea_tiempo | tests/test_linea_tiempo.py |
| H2 recorte tras pergamino | D FR-007, H2, T008/009/IC-03 | partida/linea_tiempo | tests/test_controlador_ac_real.py, test_historia_motor.py |
| H3 todos los eventos empatados | D FR-002, H3, T003/004/006 | juego/linea_tiempo | tests/test_frontera_temporal.py, test_historia_motor.py |
| H4 consulta sin efectos ni log | D FR-005, H4, T004/006 | controlador/linea_tiempo | tests/test_controlador_ac_real.py |
| H5 replay hasta después del fin | D FR-014, H5, T012/014 | replay_sin_vista | tests/test_modos_historia.py |
| H6 archivo P1 incompatible | D FR-012, H6, T008/011 | guardado_binario | tests/test_controlador_ac_real.py, test_persistencia_historia.py |

Los cuatro prefijos A/B/C/D identifican su carpeta de especificación. La cobertura de Parte I se conserva en las regresiones heredadas, incluyendo combate, inventario, efectos, cancelación, retroceso, caché, presupuesto, guardado y replay. Esta tabla no sustituye ejecutar las pruebas.

## Antecedente: cierre comprobado del fortalecimiento

Regresión de ese incremento: **818 pruebas en 181.531 s, cero fallos y cero errores**, dos omisiones opcionales con ejecución separada aprobada: comparación histórica (41 pruebas) y API oficial (cinco criptas, caché fría/caliente dentro de presupuesto). Copia limpia de fuentes sin datos locales mediante `python -m utilidades.verificar_copia_limpia`; no reinstala las dependencias. El resultado más reciente figura al comienzo del documento.

| Operación | Máximo final | Límite | Excesos |
|---|---:|---:|---:|
| Ciclo con 30 cazadores e historia/mapa, RC-01 | 11.931 ms | 20 ms | 0/600 |
| Paso de viaje conocido | 2.501 ms | 5 ms | 0/60 |
| Verificador completo | 7.855 ms | 200 ms | 0/10 |
| Historia K=50, 5.000 acciones | 0.9363 ms | 50 ms | 0/185 |

El heap redujo su mediana pareada de 4.3523 a 2.2538 ms, con decisiones iguales. El motor ahora permite IDs uint32 muy dispersos sin reserva proporcional al mayor ID; hay una partida completa automatizada con esos IDs. [Salidas completas, semilla y entorno](specs/004-linea-tiempo/fortalecimiento-mediciones.json), análisis y alternativas en DECISIONES.md. Las tablas de pruebas se solapan y no se suman.

## Salvedades históricas conservadas

Dos finales de prompts de A no se conservan íntegros y el commit histórico `33d97ac` reunió aclaración y código. Los textos completos reconstruidos por autorización de Belén se identifican como tales; no se presentan como originales recuperados ni se reescribe ese hecho. El PDF original local de Parte I está vacío; se conserva la extracción previa. Las mediciones no garantizan una calificación o cero bugs futuros. Resultados de fortalecimiento y reproducción en DECISIONES.md y README.md.

Actualización de publicación con A dff5882: suite 815, OK; integración específica 44, OK. El benchmark posterior registró un ciclo de 20.282 ms (1/60 sobre 20); repetido aisladamente dio 19.783 ms (0/60). Paso conocido 4.208 ms y repetición 2.341 ms, ambos bajo 5. Se conserva la variación como límite de rendimiento, sin ocultar la muestra excedida.


Estado posterior RC-01: eliminados los ordenamientos redundantes de historia. Cinco series pareadas de 120 ciclos por productor, historia/estado/azar iguales: mediana 11.436 → 4.435 ms; máximo optimizado 11.931 ms y 0/600 sobre 20 ms. Suite 818, cero fallos/errores, dos opciones con evidencia separada previa. Copia limpia 20 pruebas, OK. La advertencia de ciclo de la publicación anterior queda como antecedente medido; la optimización aporta margen en estas nuevas muestras, sin garantía absoluta de latencia bajo cualquier carga. El viaje no fue modificado y sus muestras auxiliares, incluida una de 5.168 ms, permanecen en [el registro completo](specs/004-linea-tiempo/ciclo-historia-mediciones.json).
