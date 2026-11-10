# Comprobación inicial de C

## I5 — control local de viaje (2026-11-10)

Especificación confirmada antes del código en 2af6094. Aclaraciones de alcance: resultados únicos, cancelación persistente hasta nueva orden, rechazo sin reintento automático y hechos explícitos. Análisis de consistencia previo: C26–C30 cubiertos por T022–T025, sin conflictos críticos dentro del incremento; lista general 7/11 cumplidas, 4 pendientes por antorcha/revisión cruzada. Continúa la autorización del usuario para trabajo independiente. Sin extensions.yml ni hooks.

Primera ejecución de las pruebas falló por ausencia de modelo.viaje; después de implementar, ocho pruebas locales pasaron. El verificador aislado con A 9730482 ejecutó **32 pruebas en 0.559 s, OK, sin omisiones**: conocimiento, rutas y control. Incluye rechazo de movimiento, observación de puerta cerrada, selección de alternativa, cancelación, reversión externa y nueva orden expresa. Los resultados del movimiento se suministran en las pruebas; no se ejecuta el motor ni se acredita N3/N6 integrado.

Regresión seleccionada: comando de I4 más tests.test_viaje, **156 pruebas en 21.237 s, OK**, con CRIPTA_SIN_AUDIO=1. Son 148 anteriores y ocho nuevas; algunas aparecen en la prueba aislada, por lo que no se suman como casos únicos. Sin suite completa ni prueba gráfica. No se repitió benchmark: no se modificó búsqueda y sigue pendiente el límite de rendimiento documentado en I4.

La validación rechaza resultados duplicados, antiguos o incoherentes antes de mutar el control; un fallo de consulta conserva su estado. No se modifica reloj, mapa, inventario ni historial. No hay estructuras prohibidas ni dependencias nuevas. El controlador futuro debe evitar ejecutar propuestas canceladas y proporcionar los hechos del paso; el control no garantiza revertir acciones ajenas. Quedan pendientes contrato compartido, antorcha, guardado/replay y partida integrada.

Fecha: 2026-11-08. Base: 544090a, igual a origin/main tras fetch y avance directo. No contiene las implementaciones aún no integradas de las ramas de A/B/D.

Comando ejecutado con `CRIPTA_SIN_AUDIO=1`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_transicion_salas tests.test_inventario tests.test_historial tests.test_rastro tests.test_enemigos tests.test_regresiones_juego tests.test_juego tests.test_precarga_offline tests.test_sesion_datos -q
```

Resultado: 125 pruebas, 18.220 segundos, OK. Es una selección de regresión de la base; no es la suite completa, una prueba de la interfaz en ejecución ni evidencia de cumplimiento de Parte II. No se ejecutaron benchmarks.

Se verificó que el archivo local de puntajes contiene exactamente las entradas de HEAD seguidas de las 16 entradas locales conservadas. Respaldo adicional local y stash retenidos. Los puntajes no forman parte del trabajo documental de C.

Fases: specify en borrador; clarify pendiente; plan/tasks/analyze/implement no iniciadas. No se afirma que las propuestas de contratos estén aprobadas por otros integrantes.

## Incremento independiente I1

Estado posterior al registro inicial: alcance I1 aclarado y autorizado por el usuario, plan y ocho tareas revisados antes de implementar. Commit de documentación previo: `fa5418a`. Revisión de consistencia: FR-001–005, FR-014 local, FR-017 local y PR-002 cubiertos; sin tareas ajenas al alcance. El resto de requisitos permanece explícitamente fuera de I1. No se considera aprobada la integración por otros integrantes.

Se añadieron `modelo/conocimiento.py`, `tests/test_conocimiento.py` y `utilidades/bench_conocimiento.py`. No se modificó ningún módulo existente del juego. El modelo no importa motor, red, archivos, vista ni tipos históricos de una rama no integrada.

Pruebas: las pruebas iniciales fallaron por ausencia del módulo; después de implementarlo, las 16 pruebas nuevas y las 125 de regresión seleccionadas pasaron: **141 pruebas, 16.928 s, OK**. Se utilizó el comando inicial añadiendo `tests.test_conocimiento`. No es la suite completa ni una prueba de interfaz integrada. Revisión AST del módulo: sin dict/set, sorted ni list.sort; se reutiliza ordenamiento por fusión propio. `git diff --check` sin errores.

### Medición local reproducible

Comando: `python -B -m utilidades.bench_conocimiento`. Python 3.12.10, Windows-11-10.0.26300-SP0. Cadena sintética sin puertas, IDs separados por 1009; carga determinista sin azar (semilla no aplica), 2000 repeticiones por tamaño. Cada entrada procesa dos salidas y genera dos cambios. No incluye red ni renderizado. Tiempo de preparación separado; tiempos de operación son medias, no máximos garantizados.

| Salas | Preparación ms | Entrada µs | Inversión µs | Consulta µs |
| --- | --- | --- | --- | --- |
| 100 | 1.124 | 4.686 | 4.567 | 1.521 |
| 1000 | 13.561 | 5.212 | 5.560 | 1.991 |
| 10000 | 201.690 | 6.074 | 7.024 | 2.701 |

La prueba de localidad comprueba el mismo número de accesos al estado para una entrada de igual grado con 10 y 10000 salas e impide iteración global del estado durante esa operación. No se afirma tiempo constante: resolver un ID tiene costo logarítmico. La preparación y la proyección del mapa sí dependen del tamaño total. La integración de estas mediciones en `--bench` y DECISIONES.md queda para la entrega coordinada, sin atribuir ese trabajo como terminado.

### Límites de la entrega

Sin antorcha, viaje, guardado, integración histórica, modificación de inventario ni conexión al juego. Q1 sigue abierta. El llamador garantiza que una observación corresponde a la posición actual; el componente valida extremo y exploración, pero no duplica el estado de posición del motor. Los IDs de puertas son explícitos del adaptador, no una identidad inferida por C. Aplicar deltas requiere esqueleto compatible. La validación de ese contrato interno no decide las reglas de la API de B.

## I2 — 2026-11-09

Especificación confirmada antes del código en `e3e16a6`. Revisión previa: FR-018 cubierto por T010, PR-004 por T012, y C17 por T009. T011 demuestra requisitos de conocimiento existentes; T013 cierra verificación. Sin dependencias de integración nuevas; Q1 permanece abierta y no afecta esta función pura. La lista general de calidad mantiene sus pendientes de capacidad completa.

Resultado: **148 pruebas en 19.023 s, OK** (23 específicas y 125 de regresión seleccionadas). Primero se comprobó fallo de importación por módulo de detención ausente; después se implementó. La prueba C17 compara 1000 operaciones con referencia independiente de arreglos, semilla 20261109, reconstruye otra instancia e invierte todos los lotes. Las copias completas existen solo en el oráculo de prueba. C15/C16 recorren las 64 combinaciones de seis booleanos, conservando todas las causas. Se verificaron puertas paralelas y componentes desconectados.

Demostración ejecutada mediante `python -B -m tests.demo_conocimiento`; restauración final exacta comprobada por aserción. Sin archivos generados, GUI ni cambios en partidas. Revisión AST de ambos módulos: sin dict/set, sorted o list.sort. No se añadieron dependencias. No se afirma revisión exhaustiva de todos los posibles defectos ni suite completa del proyecto.

### Medición ampliada

Python 3.12.10; Windows-11-10.0.26300-SP0. Comando de benchmark indicado arriba. Cadena determinista con IDs separados por 1009; sin azar. Tiempos en ejecución sin tracemalloc activo, red ni renderizado. Las consultas de puerta usan 2000 repeticiones; proyección, 50, con mapa completo explorado. Medias de una ejecución local, no límites garantizados.

| Salas | Entrada µs | Inversión µs | Consulta sala µs | Preparación ms |
| --- | --- | --- | --- | --- |
| 100 | 5.532 | 5.508 | 1.747 | 1.462 |
| 1000 | 5.642 | 6.046 | 2.150 | 14.288 |
| 10000 | 7.933 | 8.784 | 3.305 | 226.147 |

| Salas | Memoria viva KiB | Pico KiB | Consulta puerta µs | Proyección ms |
| --- | --- | --- | --- | --- |
| 100 | 6.109 | 6.531 | 1.932 | 0.082 |
| 1000 | 148.766 | 149.125 | 3.722 | 1.120 |
| 10000 | 3442.211 | 3442.539 | 2.589 | 19.578 |

Memoria medida con tracemalloc exclusivamente durante la construcción del componente, sobre esqueleto ya creado. Representa asignaciones rastreadas durante ese intervalo; no incluye todo el esqueleto referenciado, memoria total del proceso ni archivo de guardado. La reutilización interna de memoria de Python puede influir en cargas pequeñas; no inferir proporcionalidad exacta de una sola ejecución. La proyección completa recorre el mapa y no debe reconstruirse por paso de viaje. Ninguna cifra acredita PR-001 ni las mediciones integradas de historia/inventario.

I2 entrega una decisión de detención aislada, no rutas ni el comando `ir a`. Integración con A/D, Q1, antorcha y persistencia siguen pendientes. El estilo gráfico del juego no se modificó.

## Revisión posterior y corrección documental — 2026-11-09

Se repitieron las 148 pruebas seleccionadas: 17.395 s, OK. Se verificó la secuencia de commits con especificación anterior al código, ausencia de modificaciones en módulos preexistentes del juego, restricciones de estructuras en los módulos nuevos y preservación de puntajes.

Se corrigieron encabezados y frases obsoletas del plan/especificación/lista de calidad para distinguir I1/I2 terminados de la capacidad completa pendiente. La aplicación/inversión cuesta O(D log(V+P)), no O(D); memoria auxiliar O(D). La preparación incluye también índices de puertas y ordenamiento de salidas. Son correcciones de documentación al comportamiento existente, sin cambios de reglas o código. Los detalles de función pura y responsabilidades del adaptador permanecen en documentos técnicos; la especificación expresa resultados observables.

Continúan pendientes la revisión cruzada, integración, Q1 y conciliación histórica completa de prompts. No se cambian casillas generales a cumplidas ni se presenta esta revisión local como aprobación del equipo.

## I3 — compatibilidad con historia de D (2026-11-09)

Especificación confirmada antes del código en `00110f4`. FR-019 tiene escenarios C18–C20 y tareas T014–T017; revisión de consistencia previa sin conflictos con el alcance independiente. Claves internas propuestas, no contratos aprobados de UI o persistencia. Se reutilizaron tipos y LineaTiempo reales de D; no se cambiaron sus módulos.

Verificador: `python -B -m utilidades.verificar_conocimiento_historia`. D fijado a `02da6b6f159b28279e3fe7dc5177c97c16898f42`; C desde archivos de trabajo. Resultado: **19 pruebas en 0.093 s, OK, sin omisiones**: 14 de D y cinco nuevas del adaptador. El intento previo a implementar no pudo copiar el adaptador porque aún no existía. La prueba comprueba estados dinámicos de mapa (grados de salas y recuerdos), no renderizado ni una partida integrada.

C18 comprobó exploración al cierre y consulta antes de la segunda acción. C19 comprobó rechazo tras cambios válidos, estado/reloj/contador histórico intactos y reversión local exacta sin recortar historia. C20 comprobó observaciones a t=50/t=150, consultas antes y después, recorte de acción aceptada y reversión local coherente. También se comprobó ausencia frente a puerta abierta y eliminación de duplicados en base inicial.

Regresión del checkout de C: **148 pruebas, 8.783 s, OK**. No incluye las cinco de integración, que se ejecutaron en la copia aislada. Una ejecución directa de esas pruebas sin D informa una omisión explícita y remite al verificador; no se contabiliza como integración exitosa. Revisión AST del adaptador sin dict/set, sorted o list.sort; ordenamiento propio. No se midió rendimiento de historia en este ensayo.

Pendiente: aprobar claves y proyección con D; incluir deltas en lote del motor y rollback completo con A. El adaptador no aporta reloj, agenda, azar, inventario ni binario. La garantía comprobada cubre los errores de validación esperados de D, no cualquier fallo de ejecución. Q1 y ruta sobre conocimiento siguen pendientes; ausencia de límite ya está soportada en A 33d97ac.
# I4 — rutas conocidas con A (2026-11-09)

Documentación confirmada en e2a1f61 antes del código. Revisión clarify del alcance independiente: entradas, rechazo sin filtrar existencia, llegada, puerta no observada y consulta tras reversión definidos; Q1 excluida. Análisis previo: cinco escenarios C21–C25 cubiertos por T018–T021, sin tareas ajenas ni conflictos críticos dentro de I4. La lista general conserva 7 casillas cumplidas y 4 pendientes, con autorización del usuario para continuar el incremento delimitado. Sin hooks de extensiones.

Se reutilizó rutas.py de A 9730482d4c6e33e5ba39e6eeb6f76d1f19b4220c, sin cambios. El adaptador lee arreglos privados del componente de C; la búsqueda recibe únicamente arcos admisibles. No consulta puertas reales ni construye diccionarios. Aún no se conecta a su motor ni a la interfaz de D.

Comando: `python -B -m utilidades.verificar_conocimiento_rutas --bench`. Resultado: **23 pruebas en 0.185 s, OK, sin omisiones**. Incluye siete pruebas nuevas, con 60 grafos comparados contra caminos simples exhaustivos (semilla 927), y 16 de conocimiento. La primera corrida detectó que el verificador no copiaba bench_conocimiento, requerido por una prueba de localidad existente; se añadió la dependencia y se repitió el conjunto sin debilitar pruebas.

Regresión seleccionada: comando inicial con las tres suites de conocimiento/secuencias/detención, **148 pruebas en 7.264 s, OK**. Las 16 pruebas de conocimiento aparecen también en la copia aislada: no sumar ambas cifras como casos únicos. No se ejecutó la suite completa ni una partida integrada.

Diagnóstico: Python 3.12.10, Windows-11-10.0.26300-SP0; cadena bidireccional fija, sin puertas ni azar, IDs separados por 7, todo explorado. Sin red/renderizado. Una consulta de calentamiento y 30 medidas de origen a extremo. Preparación corresponde solo al adaptador sobre conocimiento ya construido; la primera carga incluye importación de A.

| V | E | Preparación ms | Consulta media ms | Máximo ms |
| --- | --- | --- | --- | --- |
| 100 | 198 | 3.568 | 0.117 | 0.144 |
| 1000 | 1998 | 2.384 | 1.445 | 2.414 |
| 5000 | 9998 | 11.811 | 5.783 | 6.372 |

La carga de 5000 salas supera 5 ms. No es la cripta de referencia: PR-001 sigue sin acreditar, y deben medirse esa cripta y el cálculo integrado antes de cerrar rendimiento. No se incorporó todavía este diagnóstico a --bench compartido ni DECISIONES.md. La fuente es compatible técnicamente con A, pero el acuerdo de movimiento, observación, señales del paso y presentación sigue pendiente.
