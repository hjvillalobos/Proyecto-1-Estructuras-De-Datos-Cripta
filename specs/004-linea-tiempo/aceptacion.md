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

La prueba acredita la conexión de la CLI. La aceptación del límite de
200 ms queda pendiente de repetir la medición con la mayor cripta
publicada y revisar el máximo del análisis incremental.

La regresión seleccionada pasó 171 de 172 pruebas, incluidas las de
resolubilidad, descarga, R4 y la vista. Solo se omitió H3 con el motor
real. La CLI también se comprobó en CP1252 con un paquete de siete
salas, cero solicitudes y diez muestras por fase y estrategia.
