# Plan de aceptación y mediciones

La tabla vincula los escenarios de aceptación con sus requisitos y tareas.
Los resultados ejecutados y las dependencias pendientes se registran abajo.

| Caso | Requisito | Preparación y resultado esperado | Tarea |
|---|---|---|---|
| H1 | FR-001,020 | Reloj 100, historia 101: rechazo, estado intacto | T004, T006 |
| H2 | FR-007 | Ejecutar acciones, pergamino, nueva acción: historia refleja solo rama vigente | T008, T009 |
| H3 | FR-002 | Varios eventos en t, incluido uno que agenda otro en t: incluir todos antes de decisión | T003, T004, T006 |
| H4 | FR-005 | Comparar estado, RNG, log y retroceso antes/después de consultar: idénticos | T004, T006 |
| H5 | FR-014 | Replay termina en 100; --hasta 200: estado final y aviso, sin vista | T012, T014 |
| H6 | FR-012 | Archivo P1 formato 3: incompatibilidad explícita y original conservado | T008, T011 |
| R4 integración | FR-016 | No resoluble sin --forzar: reporte y no inicia; con --forzar permite inicio | T012, T015 |
| EX01 | FR-003 | #1 y #k antes de acción, especialmente si comparten reloj | T004, T006 |
| EX02 | FR-008,020 | K=0, negativo, texto; t negativo; #0 o inexistente: errores sin efectos | T004, T012, T013 |
| EX03 | FR-009,010 | K=1 y K=10; consultas junto a límites y entre eventos: <=K acciones reconstruidas | T004, T005, T006 |
| EX04 | FR-011 | Guardar/cargar antes/después de pergamino y checkpoint: igual historia, RNG y continuación | T008, T011 |
| EX05 | FR-017 | Sustituir constructores de vista por fallo deliberado: replay/bench/verificar terminan sin invocarlos | T012, T013, T014 |
| EX06 | FR-018,019 | Vista consume mapa de conocimiento; no revela salas desconocidas; cada paso viaje genera movimiento | T016, T017, T018 |
| EX07 | FR-011 | Archivo truncado, CRC inválido, offsets inválidos: error y partida activa intacta | T008, T011 |
| EX08 | FR-004,010 | Consulta entre decisiones reconstruye enemigos, efectos, puertas y conocimiento históricos correctos | T004, T006, T010 |

## Protocolo de bench integración

Semillas fijas y cargas comparables. Al menos 5 000 acciones; tamaños de estado y densidades de cambios diferentes; K 10/50/100 y reconstrucción desde inicio sin controles. Consultas al inicio/medio/final y junto a controles; medir localización y reconstrucción por separado y juntas. Comparar inversión desde presente cuando la captura permita esa alternativa. Medir recorte con prefijos crecientes y sufijo fijo; registrar liberación de memoria aparte.

Una repetición de calentamiento y al menos cinco repeticiones medidas, misma máquina y entorno. Registrar Python, sistema, CPU/RAM, semilla, acciones, eventos, volumen de cambios, copias completas, pico de memoria y bytes persistidos. Tiempos: media, mediana, p95, máximo y número de consultas >50 ms. El límite debe informarse por consulta, no ocultarse en un promedio. Separar red, preparación y renderizado. Verificar igualdad del resultado antes de aceptar una muestra.

Además del tiempo, instrumentar número de acciones reconstruidas para certificar el límite K. Medir historia de 10 000 o más acciones para estudiar crecimiento, sin sustituir el caso mínimo exigido. La referencia publicada y cualquier enmienda del profesor prevalecen.

## Plantilla de resultados (sin datos inventados)

| K | Acciones/eventos | Memoria pico | Búsqueda | Reconstrucción p95/máx | Total máx | Acciones reconstruidas máx | Correcto |
|---|---|---|---|---|---|---|---|
| 10 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| 50 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| 100 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Sin controles | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Puede superar K | Pendiente |

## Evidencia del incremento de D (2026-11-07)

| Caso | Evidencia del consumidor | Dependencia para aceptación real |
|---|---|---|
| H1, H4, EX01–EX03 | Consultas válidas e inválidas, estado/RNG/log iguales antes y después, límite K | Conectar productor del motor para repetir en partida |
| H2 | Recorte y corrección de inventario con productor de prueba, rama nueva | A/C producen retroceso y correcciones reales |
| H3, EX08 | Cambios empatados ordenados y resumen de sala, enemigos y mapa con fixture | A cierra el lote real y C entrega conocimiento |
| H5, EX05 | CLI sin constructores de vista, replay hasta t y después del final; replay simple con motor actual | A entrega los cambios para `--hasta` real |
| H6, EX04, EX07 | Carga interactiva rechaza v3; v4 conserva K, RNG, historia y continuación; CRC y offsets inválidos no restauran | A/C confirman la restauración conjunta real |
| R4 | Rechazo/inicio forzado, diagnóstico y exclusividad de CLI probados con el contrato de B | Integrar la entrega de B a esta rama |
| EX06 | Consola y botones GUI, mapa filtrado del fixture, viaje delegado y log de pasos; costo real de salida ponderada | C entrega mapa/viaje y A el cazador real |
| SC-003 | Cargas sintéticas de 5.000 y 10.000 acciones, cuatro variantes y comparación de dirección | Repetir con los productores y cripta de referencia |

El resultado del benchmark está en [DECISIONES.md](../../DECISIONES.md).
Los casos de contratos probados con fixtures quedan pendientes de
aceptación con los módulos del equipo. T003, T010 y el cierre integrado
T021 permanecen abiertos.

## H3 y R4 con datos offline (2026-11-08)

| Caso | Prueba y evidencia | Alcance pendiente |
|---|---|---|
| H3 · FR-002, FR-003 · T003, T004, T006 | En [`tests/test_historia_motor.py`](../../tests/test_historia_motor.py), el productor de prueba entrega dos cambios de vida en el mismo instante. La consulta por tiempo y `#2` coinciden con la vida posterior al lote, mientras la consulta anterior al lote conserva la vida inicial. Las 11 pruebas de frontera de A pasan por separado en `c99b56b`. | Ejecutar la prueba H3 con el motor real cuando exponga el productor. El fixture usa una salida sin costo declarado y compara `historia 99`, `historia 100` e `historia #2` con el estado del motor. |
| R4 · FR-015, FR-016 · T012, T015 | En [`tests/test_modos_historia.py`](../../tests/test_modos_historia.py), una cripta local de dos salas tiene la llave de salida detrás de su propia puerta. `--verificar` imprime el ciclo. El inicio normal informa el dictamen negativo y no crea bitácora. `--forzar` muestra el mismo dictamen antes de iniciar y genera la bitácora. | Comprobado en `004-linea-tiempo` sobre `a34d926` con las pruebas de D. |

```powershell
python -m unittest tests.test_historia_motor tests.test_modos_historia -v
```

La regresión seleccionada de D en `9ee56bf` con estas pruebas ejecutó
65 casos. Pasaron 62 y se omitieron R4 real por ausencia de B, H3 real por
ausencia del productor de A y una prueba gráfica por Tcl/Tk. La copia de
integración ejecutó las mismas pruebas más las 11 de frontera de A.
Pasaron 74 de 76, incluida R4 real. Se omitieron H3 real y la gráfica.

La preparación usa datos válidos de prueba y cero solicitudes a la API.
Según el enunciado §3.1, una salida sin costo declarado cuesta 100. Si el
costo está declarado debe ser entero positivo e igual en ambos sentidos.
La política de datos ambiguos de la API queda sujeta a la aclaración del
profesor. T003, T010 y T021 siguen abiertos.

### Regresión de salida y de vista

- **FR-017 · T019/T021.** La prueba de salida de
  [`tests/test_bench_historia.py`](../../tests/test_bench_historia.py) usa
  CP1252. Antes de la corrección fallaba al imprimir `σ`. Después de
  reemplazar el símbolo por una etiqueta, imprime la desviación estándar
  en milisegundos. En la copia con B, el comando siguiente terminó con
  código 0 y produjo 18 filas en CP1252, con resultados incrementales y
  repetitivos para tres familias de datos.
- **FR-017 · T019/T021.** La presencia de B hacía que el benchmark general
  intentara medir resolubilidad con parámetros de los otros subsistemas.
  B requiere al menos tres tamaños y diez repeticiones. La comparación
  se selecciona con `--subsistemas resolubilidad` y usa diez repeticiones
  si se omite el argumento. El comando general conserva sus cargas cortas.
- **EX06 · FR-018, FR-019 · T016/T017.** La prueba de
  [`tests/test_comandos_integracion.py`](../../tests/test_comandos_integracion.py)
  que acciona los botones Historia, Mapa y Viajar pasó al inicializar Tcl
  en el proceso de pruebas. En el Python empaquetado de Codex, Tcl no
  encontraba `init.tcl` hasta consultar su directorio de trabajo con
  `pwd`. En un Python con Tcl/Tk funcional, la prueba se puede ejecutar
  directamente con `unittest`. Usa datos de prueba para mapa y viaje.

```powershell
python main.py --bench --subsistemas resolubilidad --tamanos 8 16 32 --repeticiones 10 --semilla 20261108
python -m unittest tests.test_bench_historia tests.test_comandos_integracion -v
```

Con Tcl inicializado, pasaron 63 de 65 pruebas seleccionadas en la rama
local. Se omitieron H3 con el productor real y R4 con B. En la copia de
integración con `c99b56b` y `8b0742e`, pasaron 132 de 133 pruebas
seleccionadas, incluidas R4, la prueba gráfica, los casos de costos
válidos y las pruebas del verificador de B. La única omisión fue H3 con
el productor real.

La suite completa quedó sin certificar. Se interrumpió una corrida que
dejó de avanzar y el fallo de redibujado de la animación del menú se
reprodujo por separado en la rama local. La medición con el motor
instrumentado y la cripta de referencia sigue pendiente para T021.

### Repetición tras el PR #22

En la rama local sincronizada con `a34d926`, con las correcciones y pruebas
de D, pasaron 132 de 133 pruebas seleccionadas. Pasaron R4 con B real y la
prueba de los botones Historia, Mapa y Viajar con Tcl inicializado. Se
omitió H3 con el motor real por falta del productor de cambios históricos.
También se repitieron en CP1252 las dos rutas de benchmark. Resolubilidad
produjo 18 filas con diez muestras cada una y el benchmark general corto
terminó correctamente. Las cargas fueron sintéticas y offline.

```powershell
python -m unittest tests.test_modos_historia.ModosHistoriaTest.test_fr015_fr016_r4_cli_offline_con_verificador_real -v
python main.py --bench --subsistemas resolubilidad --tamanos 8 16 32 --semilla 20261108
```

### Paquete offline y datos incompletos

T021 vincula los casos de la CLI de D (FR-015 y FR-016) con los
requisitos de adquisición de B (FR-008 a FR-012, AC-13, AC-18 y AC-23).

| Caso | Evidencia |
|---|---|
| Descarga y verificación | El servidor de prueba entrega las llaves una vez. El paquete conserva las llaves y el contenido de esa versión, y `--verificar` lo analiza offline sin nuevas solicitudes. |
| Copia de versión explícita | El origen tiene v2 como actual y v1 disponible. La exportación offline de v1 incluye sus llaves y no copia los metadatos de v2. El cliente registra cero solicitudes. |
| Cambio de versión durante la descarga | El comando devuelve un error y el destino no publica las llaves ni los metadatos de la versión rechazada. |
| Paquete sin llaves | La exportación informa la carpeta consultada y no declara completo el paquete. `--verificar` informa verificación no completada. `--forzar` bloquea el inicio y no crea bitácora. |

```powershell
python -m unittest tests.test_modos_historia tests.test_precarga_offline tests.test_verificacion_datos -v
```

La regresión seleccionada ejecutó 170 pruebas de D, resolubilidad,
sesión, precarga y cliente HTTP. Pasaron 169 con Tcl inicializado.
La única omisión fue H3 con el motor real, pendiente del productor.

### Benchmark de un paquete offline

La conexión de D para T030 usa `--paquete` y `--cripta` en el
subsistema `resolubilidad`. La prueba de FR-017 y AC-20 prepara dos
versiones locales y comprueba que la CLI mide la seleccionada sin red
ni vista. Registra lectura y validación por separado y muestra diez
muestras del análisis por estrategia. Con un paquete sin llaves,
la CLI devuelve un error y no ejecuta la carga sintética.

```powershell
python -m unittest tests.test_bench_historia tests.test_bench_resolubilidad -v
python main.py --bench --subsistemas resolubilidad --paquete .cache/cripta --cripta ID
```

La prueba acredita la conexión de la CLI. La medición de referencia se
registra en la actualización del 2026-11-09.

La regresión seleccionada pasó 171 de 172 pruebas, incluidas las de
resolubilidad, descarga, R4 y la vista. Solo se omitió H3 con el motor
real. La CLI también se comprobó en CP1252 con un paquete de siete
salas, cero solicitudes y diez muestras por fase y estrategia.

### Historia, guardado y replay de la misma partida (2026-11-09)

La prueba de FR-002, FR-011 y FR-013 ejecuta el movimiento y los comandos
de historia, guardado y carga en el controlador. Tras avanzar una
acción, `historia #2` coincide con el resumen por tiempo. Al cargar, la
consulta recupera el mismo resumen y el estado guardado coincide con el
original. El replay hasta el instante consultado vuelve a mostrarlo
sin vista y después de eliminar el binario, usando la carga registrada
en el log.

Con el productor de prueba, el recorrido pasa a t=250. Con el paquete
local del motor real se confirmó que el primer movimiento cierra t=100
y reduce la vida de 30 a 28. La prueba conjunta con el motor real se
omite hasta que exponga captura y restauración. El recorrido y las
comprobaciones están en [`tests/test_historia_motor.py`](../../tests/test_historia_motor.py).

```powershell
python -m unittest tests.test_historia_motor -v
```

En la regresión seleccionada pasaron 195 de 197 pruebas. Las dos
omisiones fueron las pruebas que requieren el productor real de A.

### Resolubilidad de referencia (2026-11-09)

La mayor cripta del listado del servicio fue `cripta-06`, de 300 salas,
versión `f9ed9afa683d`. El benchmark offline midió diez muestras por
estrategia y cero solicitudes. El máximo incremental fue **16.140 ms**
frente al límite de **200 ms** de AC-20. El máximo de lectura y validación,
medido aparte, fue 36.503 ms. [Comando, equipo y muestras](../../DECISIONES.md#parte-ii--integración-y-mediciones-de-la-persona-d).

### Viaje por pasos y cierre de regresiones de D (2026-11-10)

Alcance autorizado: solo D. Se cambiaron controlador, entradas de consola/GUI,
limpieza de menú, pruebas y documentación. No se modificaron el motor de A,
algoritmos de C, datos ni verificador de B.

Se verificó el consumidor con `ControlViaje`, `PlanificadorConocido` y
`ConocimientoMapa` reales. Un motor de prueba suministra los hechos explícitos;
esto no sustituye una partida de producción. Los 18 casos nuevos de
`tests/test_controlador_viaje.py` cubren inicio sin movimiento, dos pasos y
llegada, causas simultáneas, destinos no admitidos, consultas intercaladas,
cancelación de propuestas, pergamino/carga/salida, ausencia e incoherencia de
hechos, excepciones y fallos de bitácora. También verifican alternativa tras
observar cierre, rechazo sin progreso, posición/proveedor reemplazados y entrada
automática/interrupción/cierre de ventana y consola.

La primera suite completa detectó tres casos de preparación de pruebas de D.
Se fijaron dimensiones del menú oculto y se completaron los dobles de escena y
precarga, conservando las aserciones originales. La comprobación de destrucción
detectó un callback de precarga que sobrevivía al menú; ahora se cancela al
destruirlo y se verifica que no queda pendiente.

Corrida final con Python 3.14.6, Windows y `CRIPTA_SIN_AUDIO=1`: **701 pruebas,
695 aprobadas, 6 omisiones y cero fallos/errores**, en 147.274 s. Se usó un runner
local de `unittest` con descubrimiento de `tests/`, salida por caso y un límite
de diagnóstico de 45 s por caso. Registro local:
`.cache/revision-d-viaje-suite-final.log`. Reproducción ordinaria:

```powershell
$env:CRIPTA_SIN_AUDIO='1'
python -X utf8 -m unittest discover -s tests -v
python -X utf8 -m unittest tests.test_controlador_viaje -v
```

Omisiones: comparación de escenarios de C que requiere preparar revisiones
reales (una clase); dos casos con paquete oficial opcional no indicado; API real
sin habilitación explícita; dos casos de historia con motor real pendientes del
productor/restauración. No se eliminaron pruebas ni se cuentan como aprobadas.

El resultado acredita la regresión y el consumidor de D. Permanecen abiertos
T003/T010 y la aceptación integrada de T021: el motor debe entregar el proveedor
de conocimiento/viaje, hechos del movimiento y captura/restauración histórica
completas. Los tiempos de esta corrida son duración de pruebas, no evidencia
de los umbrales de rendimiento del enunciado.

### Main integrado y receptor H3 de D (2026-11-10)

Base `2b347da` en `004-linea-tiempo`: contiene el cierre conjunto B/D de
T025/T026/T030/T031/T034 importado desde main. La regresión de integración
ejecutó 92 pruebas: 89 aprobadas y tres opcionales omitidas. El comando offline
de `cripta-06@f9ed9afa683d` reconoció 300 salas, diez muestras por estrategia y
cero solicitudes; máximo incremental 9.977 ms, preparación medida por separado.

Se añadió `ReceptorH3`, un consumidor de D para el productor optativo de
sala/jugador de A. Cuatro pruebas nuevas usan `motor_terreno()` real y
`LineaTiempo` real para comprobar consultas 99/100/#2, binario y aislamiento
de consultas. Un delta tardío incompatible hace rechazar el lote antes de
publicar la historia; el motor revierte el turno y puede ejecutar de nuevo la
acción #1. Se rechazan entradas mutables, orden incorrecto, ordinal/frontera
incompatibles y lotes repetidos. No se alteraron el motor ni los módulos B/C.

La primera corrida completa se detuvo por el límite de diagnóstico en
`test_main_reinicia_con_motor_y_precarga_nuevos`. La prueba de D usaba una
cripta de la caché de trabajo y, con la validación de B integrada, reintentaba
por datos ausentes. Se reemplazó esa dependencia por un paquete temporal completo,
conservando las aserciones sobre reloj, vida, inventario, motores y precargas
independientes. La regresión seleccionada posterior aprobó 28 pruebas.

Corrida final con Python 3.14.6 y `CRIPTA_SIN_AUDIO=1`: **709 pruebas, 703
aprobadas, seis omisiones y cero fallos/errores**, en 128.960 s. Registro local:
`.cache/revision-d-main-h3.log`. Se usó el mismo runner de descubrimiento con
límite de diagnóstico por caso descrito en la sección anterior. Reproducción:

```powershell
$env:CRIPTA_SIN_AUDIO='1'
python -X utf8 -m unittest discover -s tests -v
python -X utf8 -m unittest tests.test_receptor_h3_d tests.test_replay_reinicio -v
```

Se mantienen las seis omisiones documentadas anteriormente. En particular,
las dos pruebas de historia completa de partida siguen pendientes del productor
y restauración de A; el receptor optativo de sala/jugador no las reemplaza ni
habilita automáticamente `integrar_historia`. T003/T010 y la aceptación integral
de T021 permanecen abiertas. Todos los cambios de este incremento son de D y
se publican únicamente en `004-linea-tiempo`.

## Preparación de puertas recíprocas A–D, 2026-11-12

Se preparó `tests/test_puertas_reciprocas_d.py` para PD-01..04 de la
especificación, confirmados primero en `32b97f6`. No se cambió producción,
el formato binario ni los contratos de historia completa. La propuesta de A
todavía no está implementada en el motor de este árbol.

Python 3.14.6, temporales en una carpeta escribible y sin HTTP:

```powershell
python -B -X utf8 -m unittest tests.test_puertas_reciprocas_d -v
python -B -X utf8 -m unittest tests.test_regresiones_juego tests.test_receptor_h3_d tests.test_historia_motor
```

Suite nueva: **7 pruebas, 1 aprobada y 6 fallos de aserción; cero errores y
cero omisiones**. Es una entrega TDD deliberadamente pendiente; el descubrimiento
global también incluirá estos fallos hasta integrar la implementación de A.

| Caso | Resultado en la base actual |
| --- | --- |
| PD-01 apertura/carga con extremo no visitado | Falla antes de guardar: apertura unilateral. |
| PD-01 binario de estado bilateral preparado | Falla al cargar: extremo no visitado vuelve a cerrado. |
| PD-02 preservación de evento y estado | Pasa: tiempo, secuencia, contador y estado completo iguales. |
| PD-02 ejecución de cierre cargado | Falla: cierra solo un extremo. |
| PD-03 retroceso de apertura | Falla en la precondición bilateral; las aserciones de retroceso aún no se alcanzan. |
| PD-03 retroceso de cierre cargado | Falla en la precondición bilateral; las aserciones de retroceso aún no se alcanzan. |
| PD-04 continuación determinista | La igualdad de estados pasa, pero falla el cierre bilateral exigido. |

Los fixtures abiertos aíslan persistencia/cierre de la apertura pendiente; no
reemplazan métodos del motor. El caso de exportación prepara expresamente un
estado bilateral cambiado para reproducir la pérdida de una sala sin contenido
cargado ni rastro. No acredita que el productor actual abra ambos extremos.
La agenda contiene un único cierre; todavía no se comprueba la política de
guardados antiguos contradictorios o con dos cierres de la misma puerta física.

Regresión seleccionada: **50 pruebas, 48 aprobadas, dos omitidas y cero
fallos/errores** en 2.162 s. Las omisiones siguen siendo la captura y restauración
de historia completa del motor real. La suite nueva tardó 0.206 s; esas
duraciones de unittest no son mediciones de rendimiento del juego.

Pendiente de A: sincronizar apertura/cierre y conservar el extremo modificado
sin cargar ni explorar su sala; registrar ambos deltas y conservar la identidad
del cierre al retroceder. Pendiente de D: repetir esta aceptación al recibirlo.
No se cierran T003/T010/T021 por preparar estas pruebas.

Antes de publicar se consultó la rama remota y se incorporó `8bfe11a` mediante
el merge `1850722`, conservando los avances nuevos de A/C. El conflicto del
registro de prompts se resolvió conservando ambas entradas. Se repitieron las
siete pruebas nuevas: mismo resultado (1 aprobada y 6 fallos), en 0.087 s.
La regresión ampliada de la base integrada pasó **100 pruebas contabilizadas:
98 aprobadas, dos omitidas, cero fallos/errores**, en 13.331 s:

```powershell
python -B -X utf8 -m unittest tests.test_regresiones_juego tests.test_receptor_h3_d tests.test_historia_motor tests.test_eventos_terreno tests.test_restauracion_rutas tests.test_turno_cazador tests.test_cambios_historicos_motor
```

La entrega nueva de A incorpora captura/restauración históricas bajo activación
offline; las dos omisiones del flujo general siguen presentes. Estos resultados
no sustituyen la aceptación integral de producción ni la propuesta de puertas.

## Controlador de D con entregas reales de A/C — 2026-11-12

Especificación DX-01..06 confirmada en `43c0d2e`. Nueva suite:
`tests/test_controlador_ac_real.py`. Usa un paquete sintético construido por B,
cliente/precarga offline, motor histórico o mapa de A bajo sus opciones
explícitas de prueba, mapa/planificador/control de viaje de C y controlador,
binario e historial de D. Solo la vista se simula y se prohíbe HTTP.
No se parchean acciones, reglas, resultado de movimiento ni restauración.

```powershell
python -B -X utf8 -m unittest tests.test_controlador_ac_real -v
```

**9/9 pruebas aprobadas**, cero fallos, errores u omisiones, en 2.376 s con
Python 3.14.6. Duración de unittest, sin afirmación de rendimiento.

| Requisito | Evidencia desde el consumidor de D |
| --- | --- |
| DX-01 | `mover E`, `esperar`, `historia 99/100/#2`; vida antes/después del ataque empatado. Consulta conserva estado, RNG y bytes del log. |
| DX-02 | Comandos con ruta con espacios escriben v4 y recuperan estado/historia. Continuación coincide con la ejecución previa a cargar. |
| DX-02 | P1 y archivo truncado producen error de usuario, sin cambio de partida ni nueva carga en el log. |
| DX-02 | Pergamino recorta historia, se consume y permite nueva rama; replay conserva las órdenes. No acredita inventario histórico completo. |
| DX-03 | Replay del log escrito por el controlador, con carga embebida, coincide para 99/100/200 y avisa para 201; funciona sin archivo guardado original ni construir vistas. |
| DX-04 | Comando mapa presenta conocimiento actualizado por entrada física y oculta la sala desconocida. Consulta conserva partida y log. |
| DX-05 | Control de viaje real de C sobre mapa conocido del motor; cancelar antes del paso conserva estado/acciones y elimina propuesta. |
| DX-05, límite | Un paso aceptado se graba; ante `hechos_paso` ausente se cancela y no se repite. El error se verifica, no se inventan daño o enemigos. |
| DX-06, límite | Carga con mapa activo informa el rechazo explícito de A y conserva partida, conocimiento, historia y bytes del log. |

Pendientes de productores y coordinación: ampliar acciones históricas más allá
de mover/esperar/atacar; entregar hechos de paso; persistir/restaurar
conocimiento e inventario históricos y conectar el flujo de producción. La
conexión de prueba no se activa en la aplicación normal. T003/T010/T021
permanecen abiertas. Las pruebas PD de puertas conservan su estado de entrega
TDD pendiente; no se han ocultado para presentar una suite global aprobada.

Regresión completa del mismo árbol con Python 3.14.6, `CRIPTA_SIN_AUDIO=1`
y temporales escribibles:

```powershell
python -B -X utf8 -m unittest discover -s tests -v
```

**776 pruebas: 764 aprobadas, seis fallos, seis omitidas, cero errores**, en
178.575 s. Salida 1 por los seis casos PD de puertas ya documentados; no se
atribuyen a la integración DX ni se presentan como aprobados. Las omisiones
son: comparación opcional por revisiones de rutas (setUpClass), dos casos de
paquete oficial no indicado, dos casos de historia del motor normal aún sin
activación de producción y API real deshabilitada. Registro local reproducible:
`.cache/aceptacion-d-ac-real-2026-11-12.log` (salida generada no versionada).
No aparecieron fallos adicionales. Esta corrida no renueva mediciones de
rendimiento ni cierra los contratos pendientes.

## Carga conjunta del mapa conocido MC-01 — 2026-11-13

Precisión de FR-011 / SC-004 confirmada antes del código en `49db7f5`.
Se añadió a `tests/test_controlador_ac_real.py` el caso
`test_mc01_cargar_descarta_descubrimientos_posteriores_y_permite_continuar`.
Reutiliza la preparación offline DX con A/B/C/D reales y vista simulada.
No cambia motor, conocimiento, formato ni activación de producción.

| Etapa del caso sintético | Resultado actual |
| --- | --- |
| Entrar en 101; 102 avistada y 103 desconocida | Pasa por movimiento real. |
| Guardar en ruta con espacios y leer v4 | El DTO completo leído coincide con el exportado; esto no demuestra que la historia incluya el mapa. |
| Entrar en 102, atravesando K=2 | Pasa: 102 explorada y 103 avistada; mapa y estado distintos del guardado. |
| Cargar por el controlador | Falla: `No se pudo cargar: La restauracion H3 no admite el mapa conocido activo.` |
| Recuperar estado, historia/K, mapa y presentación guardados | Aserciones preparadas, aún no alcanzadas por el rechazo. |
| Registrar una carga y repetir movimiento sin conservar el futuro | Aserciones de continuación preparadas, aún no alcanzadas. |

Reproducción de la aceptación pendiente:

```powershell
python -B -X utf8 -m unittest tests.test_controlador_ac_real.ControladorACRealTest.test_mc01_cargar_descarta_descubrimientos_posteriores_y_permite_continuar -v
```

Una prueba, un fallo de aserción esperado por la integración pendiente, cero
errores u omisiones, en 0.732 s. No usa skip ni expectedFailure: el fallo queda
visible también en el descubrimiento general, además de los PD ya documentados.

Regresión seleccionada con Python 3.14.6, Windows, `CRIPTA_SIN_AUDIO=1` y
temporales en una carpeta escribible:

```powershell
python -B -X utf8 -m unittest tests.test_controlador_ac_real tests.test_persistencia_historia tests.test_presentacion_conocimiento tests.test_receptor_h3_d tests.test_fallos_transaccionales tests.test_restauracion_rutas tests.test_controlador_viaje tests.test_cambios_historicos_motor
```

**97 pruebas: 96 aprobadas y un fallo (MC-01); cero errores u omisiones**, en
16.771 s. La selección incluye los nueve casos DX anteriores y las regresiones
de binario, presentación, receptor H3, fallos transaccionales, restauración,
viaje y cambios históricos. Registro local no versionado:
`.cache/aceptacion-d-mc01-2026-11-13.log`. No se repitió la suite completa ni se
renuevan mediciones de rendimiento por este incremento de pruebas.

### Coordinación pendiente A/C/D

- A: conectar la restauración del conocimiento con el estado físico y la nueva
  historia, validando antes de modificar la partida viva. Levantar la
  restricción solo al completar esa conexión; quitarla sola no satisface MC-01.
- C: confirmar con A los datos reconstruibles del conocimiento y su aplicación.
  Ya existen `campos_iniciales` y `convertir_cambios` en
  `modelo/conocimiento_historia.py`, con claves propuestas de C; su existencia
  no implica un contrato aceptado ni que el motor los esté registrando.
- D: aportar esta prueba y repetirla cuando llegue esa conexión. El formato v4
  ya transporta historia, pero no se presume que cualquier guardado incluya el
  conocimiento. Revisar persistencia si el contrato acordado lo exige.

DX-06 conserva mientras tanto la evidencia negativa del rechazo sin publicación
parcial. Al implementar A/C la carga válida, sustituir ese caso negativo por
MC-01 y mantener las comprobaciones de cargas inválidas sin mutación. La
preparación de D está hecha; T003/T010/T021 y la restauración conjunta siguen
pendientes. No se afirma que el juego ya pueda cargar el mapa.


## Cierre conjunto 2026-11-14

Los límites negativos de MC-01/DX-06/PD descritos arriba son históricos y fueron superados por la integración completa autorizada. MC-01 pasa; DX-06 comprueba ahora rechazo de estado/historia incoherentes, conservando atomicidad; PD-01..04 pasan. El motor y el arranque normal conectan mapa, antorcha, inventario, historia, carga y viaje. [Trazabilidad, comandos, resultados y límites actuales](integracion-completa.md). Suite conjunta: 809 pruebas, OK, cuatro omisiones opcionales, sin fallos ni errores.
