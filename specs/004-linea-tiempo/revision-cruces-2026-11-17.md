# Revisión de cruces A↔C y B↔D — 17 de noviembre de 2026

## Resumen de la revisión

La integración examinada conecta los algoritmos de rutas de A con el conocimiento y el viaje de C, y el verificador y los datos de B con la aplicación, la persistencia y la historia de D. La revisión comprueba los contratos entre componentes: qué información recibe cada uno, qué cambios puede producir y qué debe conservar cuando una operación se rechaza, se cancela o se revierte.

La selección ejecutada reúne **66 pruebas en siete módulos**, con resultado **OK**, sin fallos, errores ni omisiones. Incluye casos de resultado esperado, entradas rechazadas, cambios de conocimiento, continuidad tras carga y reproducción de partidas. También se contrastaron las contribuciones e integraciones registradas en Git con la declaración de Belén sobre las pruebas realizadas por el equipo.

Actualización documental de cierre sobre `7d712fa`: se recuperaron registros históricos de revisión de C sobre la integración y de B sobre un commit de D, además de la aceptación técnica documentada por A. La sección «Registros históricos de revisión recuperados en Git» identifica sus fuentes, fechas y límites. Se conserva el resultado de las 66 pruebas sobre `42ee527`; no se atribuye una ejecución nueva a esta actualización.

El resultado respalda el funcionamiento de los cruces en los escenarios comprobados. La interpretación de cada evidencia, la reproducción y los límites se detallan en este informe.

## Guía de lectura

1. Identidad, alcance y método de la revisión.
2. Resultado técnico y análisis de los cruces A↔C y B↔D.
3. Matriz de trazabilidad entre requisitos, implementación y pruebas.
4. Distribución de las pruebas y procedimiento de reproducción.
5. Declaración del equipo, historial Git y conclusión.

## Identidad y alcance

Revisor técnico: Codex. Base inspeccionada: `42ee527` en `004-linea-tiempo`, con árbol inicialmente limpio. Esta revisión no cambia código, reglas, constitución ni historial Git. Fecha en America/Costa_Rica.

Responsables comunicados por la usuaria: A, Sebastián; B, Heifryl; C, Juan; D, Belén. Los nombres identifican las responsabilidades; no son firmas de aprobación de este informe.

El 17 de noviembre de 2026, Belén confirma que todos los integrantes hicieron pruebas y que comprobaron el funcionamiento de las partes al integrarlas. Esta declaración se complementa con el historial Git y la ejecución técnica documentada a continuación. La fecha corresponde al registro de la declaración, no a una fecha inferida de ejecución de las pruebas del equipo.

### Objetivos y criterios

La revisión busca comprobar que los componentes puedan usarse juntos desde los consumidores de la aplicación y que los resultados respeten las especificaciones. Se consideraron los siguientes criterios:

| Criterio | Pregunta de revisión | Evidencia utilizada |
|---|---|---|
| Contrato funcional | ¿El consumidor interpreta correctamente los resultados y errores del productor? | Inspección de adaptadores y pruebas de integración. |
| Información disponible | ¿El viaje utiliza únicamente conocimiento permitido, mientras el cazador consulta el estado real? | Fuente filtrada, pruebas de rutas y observaciones de puertas. |
| Coherencia temporal | ¿Cada paso ejecuta las reglas ordinarias y las consultas conservan el estado? | Hechos de movimiento, historia y bitácora de acciones. |
| Restauración conjunta | ¿Guardar, cargar y retroceder mantienen compatibles el estado físico, el conocimiento y la historia? | Pruebas de continuidad, recorte y cargas incoherentes. |
| Manejo de rechazo | ¿Un error o una cancelación evita publicar cambios parciales? | Casos negativos y comparación del estado antes/después. |
| Reproducibilidad | ¿Se conservan comandos, resultados y referencia de código? | Log de unittest, revisión `42ee527` e instrucciones de ejecución. |

Las afirmaciones se apoyan en tres fuentes identificadas: declaración del equipo, registros Git y ejecución técnica de Codex. Una fuente complementa a las demás dentro de su alcance; por ejemplo, la fecha de un commit establece cuándo se registró ese cambio, pero no cuándo una persona ejecutó una prueba.

### Método aplicado

Se leyó la constitución vigente, la matriz de integración IA-01..09, los requisitos de las capacidades implicadas y los módulos que conectan sus interfaces. Se seleccionaron pruebas existentes que ejercitan esas conexiones, se ejecutaron con temporales escribibles y se conservó su salida. Finalmente se inspeccionaron autores, mensajes y archivos de commits relevantes para documentar la evolución de los cruces.

La selección combina pruebas locales de contrato con pruebas que usan motor, conocimiento, datos offline e historia reales. Algunos casos sustituyen la vista, la sesión o el reporte para aislar una regla; otros ejecutan CLI en subprocesos o conectan los componentes de producción. Por ello, la lista de pruebas especifica qué demuestra cada grupo, sin presentar todos los casos como partidas completas de extremo a extremo.

## Resultado técnico

**66 pruebas dirigidas en 19.041 s, cero fallos/errores y ninguna omisión.** Resultado limitado a los casos ejecutados; no sustituye la regresión integral ni acredita revisiones humanas históricas. No se repitieron API real, benchmarks o inspección gráfica.

| Cruce | Contrato inspeccionado | Evidencia ejecutada | Resultado |
|---|---|---|---|
| A↔C: información permitida y rutas | `modelo/conocimiento_rutas.py` filtra al expandir: solo salas exploradas y puertas recordadas abiertas; emplea el buscador propio de A. El caché se identifica por destino/revisión y se descarta antes de una búsqueda que podría fallar. | `tests.test_contrato_rutas_c`, `tests.test_conocimiento_rutas`: destinos inválidos, atajos ocultos, empate, puertas, reversión, invalidación y oráculo exhaustivo con semilla. | Aprobado en los casos ejecutados. |
| A↔C: movimientos y detenciones | `modelo/viaje.py` recibe hechos explícitos de entrada, daño y enemigos; el controlador ejecuta pasos ordinarios y cancela sin ejecutar un paso pendiente. | `tests.test_hechos_paso_motor`, `tests.test_controlador_ac_real`: daño aunque haya curación posterior, trampas, rechazo sin tiempo, entradas reales, cancelación y mapa. | Aprobado en los casos ejecutados. |
| B↔D: verificación e inicio | `controlador/verificacion.py` adapta el informe de B; permite iniciar con dictamen resoluble, o no resoluble con `--forzar`. Los datos insuficientes no se convierten en permiso. `controlador/aplicacion.py` consulta esa decisión antes de iniciar. | `tests.test_modos_historia`, `tests.test_verificacion_entrega.TestInicioVerificado`, `tests.test_verificacion_entrega.TestCriptaDesconocida`: inicio, CLI y cripta inédita de 137 salas. | Aprobado en los casos ejecutados. |
| B↔D: persistencia e historia | `controlador/partida_historica.py` valida frontera física/histórica y delega restauración conjunta; `modelo/partida.py` prepara y compara el estado antes de publicarlo. Formato incompatible o corrupto se rechaza explícitamente. | `tests.test_persistencia_historia`, `tests.test_controlador_ac_real`: binario, continuidad del azar, recorte por pergamino, carga inválida sin mutación y replay sin vista. | Aprobado en los casos ejecutados. |

Trazabilidad adicional: [matriz de integración IA-01..09](integracion-completa.md), [los 23 escenarios obligatorios](../../ESTADO_ENTREGA.md), [contrato de A](../001-terreno-cazador/contracts/integracion.md), [spec de C](../002-niebla-viaje/spec.md) y [spec de D](spec.md).

## Análisis del cruce A↔C: rutas, conocimiento y viaje

### Responsabilidades e información de entrada

A aporta el buscador de rutas y el motor que ejecuta las acciones. C aporta la representación de conocimiento, la consulta de rutas conocidas y la coordinación del viaje. Compartir el buscador exige mantener separadas sus fuentes de información: el cazador decide sobre puertas reales; el viaje decide sobre salas exploradas y puertas que el jugador recuerda abiertas.

En `modelo/conocimiento_rutas.py`, `_AdyacenciasConocidas` filtra los arcos durante la expansión. Un arco solo participa si sus extremos están explorados y, cuando hay una puerta, su recuerdo indica abierta. Esta separación impide que una ruta se beneficie de una sala todavía desconocida o de un cambio remoto de puerta que el jugador no observó.

`PlanificadorConocido.consultar()` distingue rechazo del origen o destino, llegada, ausencia de ruta y propuesta de paso. La consulta entrega la siguiente sala, dirección, costo del paso y costo total cuando existe ruta. Proponer un paso y ejecutarlo son operaciones separadas: el planificador calcula; el motor aplica la acción ordinaria.

### Validez de las rutas y cambios de conocimiento

El resultado depende tanto del destino como de la revisión del conocimiento. El caché usa esa pareja y solo reutiliza etiquetas cuando el origen ya está cerrado en el espacio de búsqueda correspondiente. Antes de una búsqueda nueva se descarta la clave publicada, de modo que una excepción no deje resultados parciales disponibles para la consulta siguiente.

Las pruebas examinan observación y reversión de puertas, exploración que habilita una ruta, consultas alternadas, grafos dirigidos y ausencia de salidas conocidas. También comparan costo y primer vecino con un oráculo que enumera caminos simples en 60 grafos pequeños generados con semilla 927. Esa comparación aporta una referencia independiente para los casos generados; no equivale a una demostración sobre todos los grafos posibles.

Un caso importante separa «no se encontró ruta dentro del límite» de «se conoce una distancia exacta superior al límite». Agotar una búsqueda acotada no demuestra una distancia desconocida. El contrato de A admite que esa búsqueda no produzca paso; el consumidor no debe convertir esa ausencia en información más precisa de la que se calculó.

### Ejecución de pasos y motivos de detención

`ControlViaje` coordina una propuesta pendiente y recibe `ResultadoPaso` con hechos explícitos: posición, aceptación, daño, entrada, enemigos al entrar y terminación. El controlador usa esos hechos para decidir la continuación. No necesita reconstruir el daño comparando únicamente la vida final con la inicial.

Esto importa cuando el jugador recibe daño y recupera vida durante el mismo procesamiento: la recuperación no borra el hecho de haber recibido daño. La selección ejecutada incluye ese caso y el daño de una trampa antes del turno siguiente. También comprueba la detención tras entrar en una sala con enemigos y la cancelación que impide ejecutar o registrar un paso pendiente.

### Ejemplos de comportamiento comprobado

| Situación | Resultado exigido | Comprobación utilizada |
|---|---|---|
| Hay un atajo que pasa por una sala no explorada. | Excluirlo de la ruta del jugador. | `test_atajo_desconocido_y_reversion_de_exploracion`. |
| Dos primeros vecinos conducen a rutas del mismo costo. | Elegir el vecino de menor identificador. | `test_empate_menor_vecina_no_orden_de_entrada`. |
| Cambia la observación de una puerta y después se revierte. | Consultar con el recuerdo vigente y recuperar el resultado anterior tras revertir. | `test_memoria_puerta_y_reversion_sin_cache_obsoleta`. |
| Se cancela el viaje antes de ejecutar su propuesta. | Conservar estado y acciones registradas. | `test_dx05_cancelar_viaje_real_no_ejecuta_ni_graba_paso`. |
| Un paso causa daño aunque la vida se recupere después. | Conservar el hecho de daño para decidir la detención. | `test_dano_no_se_deduce_de_la_vida_final`. |

## Análisis del cruce B↔D: verificación, datos e historia

### Del informe de resolubilidad a la decisión de inicio

B produce el resultado de verificación a partir de los datos de la cripta. D adapta ese resultado a los modos de ejecución y a su presentación. `controlador/verificacion.py` conserva la diferencia entre un dictamen positivo, un dictamen negativo y una verificación que no pudo completarse.

La decisión de inicio se expresa en `permite_inicio()`. Los casos ejecutados comprueban la siguiente tabla:

| Estado de verificación | `--forzar` | ¿Inicia? | Interpretación |
|---|---|---|---|
| `resoluble` | No | Sí | Existe dictamen suficiente para permitir la partida. |
| `no_resoluble` | No | No | Se presenta el reporte y se bloquea el inicio. |
| `no_resoluble` | Sí | Sí | Se permite jugar por solicitud explícita. |
| `no_completada` | Sí | No | La bandera no convierte datos insuficientes en un dictamen. |

Además de la prueba aislada de esta decisión, la selección incluye CLI offline con verificador real y un caso de llave encerrada por la puerta que ella misma abre. También ejecuta la verificación de un paquete descargado y comprueba el rechazo de datos de llaves cuando cambia la versión.

El modo `--verificar` se prueba por separado para comprobar que no crea juego ni vista. El reporte negativo debe conservar información útil, como frontera bloqueada, ubicación de llaves y ciclo, cuando el verificador la proporciona. La ausencia del módulo o la falta de datos se presentan como imposibilidad de completar la verificación, evitando un diagnóstico negativo inventado.

### Guardado y restauración de un estado conjunto

La persistencia debe reunir estado físico, conocimiento e historia compatibles. En `controlador/partida_historica.py`, la exportación contrasta reloj y cantidad de acciones entre motor y línea de tiempo. Al cargar, se decodifica la historia y se valida de nuevo esa frontera antes de delegar la restauración conjunta.

En `modelo/partida.py`, `restaurar_estado_con_historia()` prepara una copia de los componentes necesarios, reconstruye el conocimiento y compara la proyección preparada con el final histórico. Una discrepancia se rechaza antes de publicar el estado sobre la partida viva. El objetivo observable es que una carga inválida no deje una combinación de posiciones antiguas, conocimiento nuevo o historia incompatible.

Los casos ejecutados comparan el estado antes y después de una carga rechazada, verifican la conservación de la bitácora y prueban una carga válida que elimina descubrimientos posteriores al guardado y permite continuar. La suite de persistencia también cubre corrupción, truncamientos, límites del formato y rechazo explícito de formatos incompatibles.

### Continuidad, retroceso y replay

Guardar y cargar debe conservar la información necesaria para continuar de forma determinista, incluido el estado aleatorio. La prueba `test_rng_guardado_como_valor_puro_continua_igual` verifica ese aspecto sin capturar el motor completo como referencia histórica.

El pergamino recorta la rama vigente: las acciones revertidas dejan de pertenecer a la historia reconstruible. La prueba integrada de retroceso comprueba ese recorte y la posibilidad de registrar una continuación nueva. Las consultas de historia se contrastan con el estado y los bytes de la bitácora para comprobar que no producen acciones ni mutaciones.

El replay se comprueba sin construir la vista y con operaciones de carga y retroceso en la secuencia. También se verifica que pedir un instante posterior al final produzca el estado final y un aviso explícito. Estos casos examinan la coherencia entre persistencia, línea de tiempo y aplicación; el rendimiento de consultas largas pertenece a las mediciones enlazadas en `DECISIONES.md`.

## Matriz de trazabilidad de la revisión

Los identificadores FR pertenecen a la especificación indicada en la primera columna. Se conserva esa referencia porque distintas capacidades utilizan numeraciones propias. IA identifica los criterios de integración documentados en `integracion-completa.md`.

| Referencia | Obligación comprobada | Implementación principal | Prueba representativa ejecutada |
|---|---|---|---|
| C FR-007/012 | Rechazar destino no explorado y reconocer llegada sin movimiento. | `modelo/conocimiento_rutas.py` | `test_rechazo_destinos_y_llegada_sin_paso` |
| C FR-008/017 | Ruta por conocimiento permitido, costo mínimo y desempate determinista. | `modelo/conocimiento_rutas.py`, `modelo/rutas.py` | `test_oraculo_exhaustivo_semilla_fija` |
| C FR-004/010/014 | Observación y reversión invalidan resultados incompatibles. | Conocimiento y planificador conocido. | `test_memoria_puerta_y_reversion_sin_cache_obsoleta` |
| C FR-009/018; IA-06 | Un paso ordinario entrega hechos de daño y entrada. | Motor, `modelo/viaje.py`, controlador. | `test_dano_no_se_deduce_de_la_vida_final` |
| C FR-015; IA-06 | Cancelar evita continuar el viaje. | `controlador/controlador.py`, `modelo/viaje.py` | `test_dx05_cancelar_viaje_real_no_ejecuta_ni_graba_paso` |
| D FR-001/003/005 | Historia por tiempo o acción sin alterar partida ni log. | Resumen histórico, controlador y línea de tiempo. | `test_dx01_consultas_reales_son_puras_y_respetan_frontera` |
| D FR-007; IA-02 | El pergamino recorta la historia y permite una rama nueva. | Partida integrada y línea de tiempo. | `test_dx02_pergamino_recorta_historia_y_log_permite_nueva_rama` |
| D FR-011; IA-03 | Guardar/cargar conserva historia y permite continuar. | Adaptador histórico y persistencia binaria. | `test_dx02_comandos_guardar_cargar_y_continuar_con_historia_real` |
| D FR-011; IA-03 | Rechazar una carga incoherente sin estado parcial. | `modelo/partida.py` | `test_dx06_carga_incoherente_con_mapa_no_publica_estado_parcial` |
| D FR-012 | Detectar formatos incompatibles explícitamente. | `datos/guardado_binario.py`, historia binaria. | `test_p1_y_version_futura_rechazados_explicita` |
| D FR-013/014/017 | Replay hasta un instante sin vista y aviso al superar el final. | `controlador/replay_sin_vista.py` | `test_dx03_log_del_controlador_reproduce_carga_sin_archivo_ni_vista` |
| D FR-015; IA-01 | Verificar sin crear juego ni vista. | `main.py`, `controlador/verificacion.py` | `test_fr015_verificar_no_crea_juego_ni_catalogo_ni_vista` |
| D FR-016; IA-01 | Bloqueo/forzado según dictamen, sin forzar datos insuficientes. | Aplicación y adaptador del verificador. | `test_fr016_no_resoluble_solo_inicia_con_forzar`, `test_fr016_forzar_no_inicia_con_paquete_sin_llaves` |

La matriz selecciona ejemplos representativos. El inventario completo de los 66 casos y sus resultados está en el archivo de evidencia; la trazabilidad global del enunciado permanece en `ESTADO_ENTREGA.md`.

## Distribución y lectura de las pruebas

Los conteos siguientes se obtuvieron de los nombres de casos registrados en la salida aprobada de unittest. Los subcasos internos, como los 60 grafos del oráculo, no se contabilizan como pruebas adicionales.

| Módulo | Casos registrados | Aporte a la revisión |
|---|---:|---|
| `tests.test_contrato_rutas_c` | 2 | Interfaz del buscador y límites de la información de ruta. |
| `tests.test_controlador_ac_real` | 10 | Consumidor integrado: historia, carga, mapa, viaje y replay. |
| `tests.test_hechos_paso_motor` | 5 | Entrada, daño y hechos producidos por el motor. |
| `tests.test_conocimiento_rutas` | 14 | Fuente conocida, desempate, caché, reversión y oráculo. |
| `tests.test_modos_historia` | 15 | CLI, inicio verificado, datos y ejecución sin vista. |
| `tests.test_verificacion_entrega` — clases seleccionadas | 3 | Inicio e integración con datos e identificadores inéditos. |
| `tests.test_persistencia_historia` | 17 | Formato, continuidad, corrupción y restauración. |
| **Total** | **66** | **Todos aprobados; cero omisiones.** |

La prueba de cripta inédita de 137 salas examina eventos, victoria, guardado y replay con datos de prueba. Su propósito es detectar dependencia de mapas o identificadores habituales; no se presenta como una consulta nueva a la API del profesor.

### Criterios de interpretación del resultado

El resultado aprobado exige que unittest termine con código de salida cero y `OK`, sin errores, fallos u omisiones en esta selección. La ausencia de fallos observados respalda los escenarios ejecutados. No permite inferir ausencia de defectos en entradas no ensayadas, ni atribuir a esta ejecución los resultados de benchmarks o revisiones gráficas anteriores.

El tiempo de **19.041 s** corresponde al conjunto de pruebas, incluida su preparación. No es una medición del ciclo de eventos, del cálculo de rutas o de las consultas históricas; los presupuestos de esas operaciones se evalúan mediante `--bench` bajo sus condiciones documentadas.

## Decisiones de integración y protección frente a regresiones

| Decisión observable en la implementación | Problema que evita | Evidencia de conservación |
|---|---|---|
| Filtrar la fuente antes y durante la búsqueda conocida. | Obtener una ruta que aproveche información oculta. | Atajo desconocido y fuente filtrada. |
| Identificar resultados reutilizados por destino y revisión. | Reutilizar distancias tras cambiar o revertir conocimiento. | Observaciones, reversión y caché parcial fallida. |
| Entregar hechos explícitos del paso. | Omitir daño o enemigos por inferirlos de un estado final incompleto. | Daño con recuperación y entrada con enemigos. |
| Separar verificación incompleta de dictamen negativo. | Iniciar con datos insuficientes mediante `--forzar`. | Paquete sin llaves y módulo ausente. |
| Preparar y validar restauración conjunta. | Publicar un estado físico e histórico incompatible. | Cargas incoherentes sin mutación. |
| Conservar azar e historia como datos persistibles. | Divergencia al continuar o consultar después de cargar. | Continuidad del generador y recorrido binario. |

Estas decisiones describen el diseño ya implementado y revisado. Este documento amplía su explicación; no constituye una especificación nueva ni afirma que una explicación posterior pruebe el orden histórico del desarrollo.

## Alcance de las conclusiones y evidencias complementarias

Esta ejecución no midió de nuevo rendimiento, tráfico HTTP ni renderizado. Para esas áreas deben consultarse [decisiones y mediciones](../../DECISIONES.md), [estado de entrega](../../ESTADO_ENTREGA.md) y los informes fechados allí enlazados, conservando sus cargas, versiones y límites.

La verificación de resolubilidad mantiene la limitación documentada de alcanzabilidad acumulada: no garantiza una trayectoria única cuando existen salidas sin regreso. Las pruebas de integración comprueban que el informe y su limitación llegan al consumidor; no eliminan esa condición del algoritmo.

La ampliación documental conserva las dos salvedades históricas de proceso: finales de prompts que no están íntegros en las fuentes disponibles y el commit `33d97ac` que reúne aclaración e implementación. Su exposición se conserva en [el estado de entrega](../../ESTADO_ENTREGA.md). No cambian los resultados técnicos de las pruebas ejecutadas.

## Reproducción y evidencia

Python local 3.14, Windows. `TEMP` y `TMP` apuntaron a `.cache/revision-proceso-20261117/temporales`; audio desactivado y UTF-8 habilitado. Se reutilizaron las dependencias instaladas. Desde la raíz del proyecto:

```powershell
$env:PYTHONUTF8='1'
$env:CRIPTA_SIN_AUDIO='1'
$env:TEMP=Join-Path (Get-Location) '.cache/revision-proceso-20261117/temporales'
$env:TMP=$env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
python -B -X utf8 -m unittest tests.test_contrato_rutas_c tests.test_controlador_ac_real tests.test_hechos_paso_motor tests.test_conocimiento_rutas tests.test_modos_historia tests.test_verificacion_entrega.TestInicioVerificado tests.test_verificacion_entrega.TestCriptaDesconocida tests.test_persistencia_historia -v
```

[Salida completa de las 66 pruebas](evidencia-cruces-2026-11-17.txt). No sumar este subconjunto a las 863 pruebas de la regresión anterior como si fueran casos adicionales.

El primer intento nombró por error una clase inexistente, `TestVerificacionEntrega`: 64 casos contabilizados, un error de carga de pruebas. No fue una aprobación ni un defecto de producción. Se corrigió la selección y se ejecutó de nuevo completa. El intento inicial se conserva localmente en `.cache/revision-proceso-20261117/pruebas-cruces.txt`.

## Pruebas del equipo y contraste con Git

Responsables de los cruces: Sebastián y Juan (A↔C), Heifryl y Belén (B↔D). Según la declaración de Belén, todos hicieron pruebas y comprobaron el funcionamiento conjunto. El historial local de `42ee527` contiene aportes de las cuatro personas, bajo sus nombres y alias de Git, y permite identificar los siguientes cambios concretos:

| Cruce | Referencias comprobadas en Git | Alcance observable |
|---|---|---|
| A↔C | `33d97ac`, Sebastián, 9 de noviembre: rango y pruebas del cazador; `9f5ce63`, Juan, 9 de noviembre: rutas conocidas con el buscador de A y `tests/test_conocimiento_rutas.py`; `3c97b7d` y `62e457c`, Juan, 10 de noviembre: reutilización de distancias y descarte de rutas sin salida conocida. | Contribuciones de A y C sobre el buscador compartido, su adaptación al conocimiento y sus pruebas. |
| B↔D | `8b0742e`, Heifryl, 2 de noviembre: verificador, pruebas y benchmarks; `9ee56bf`, Belén, 7 de noviembre: consumidores de historia, guardado, replay y adaptación de verificación; `694dcf6`, Heifryl, 9 de noviembre: llaves en descarga offline; `8b88125`, Heifryl, 10 de noviembre: integración del cierre del verificador de B y D. | Implementación del verificador, conexión con la aplicación y persistencia, y commit explícito de integración de B/D. |
| Integración del proyecto | `049a990`, Sebastián, 14 de noviembre: «Integrar CRIPTA Parte II en main (#34)». | Hito de integración de Parte II; la revisión técnica actual se realizó sobre `42ee527`, que incluye cambios posteriores. |

Los commits acreditan autoría registrada, contenido e integración. La participación en las pruebas se registra a partir de la declaración de Belén; Git por sí solo no identifica quién ejecutó cada prueba ni demuestra una aprobación previa de cada PR por ambos integrantes del cruce. Esta distinción delimita la evidencia respecto de la revisión cruzada exigida por la constitución 1.1.0.

## Registros históricos de revisión recuperados en Git

La búsqueda adicional del 17 de noviembre de 2026 examinó mensajes y cambios de commits ya presentes en la historia de `7d712fa`, junto con los informes y contratos versionados. No solo se contaron commits de implementación: se leyeron registros con referencia revisada, observaciones y resultados. Las fechas siguientes son las registradas en Git, con zona `-06:00`; los resultados son los declarados en esos registros originales, sin atribuir su ejecución a esta sesión.

| Cruce y dirección | Registro original | Alcance y resultado documentado |
|---|---|---|
| A↔C: C revisa la integración con A/B/D | Juan, [`a1e0184`](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta/commit/a1e0184), 10 de noviembre, 12:47. [Informe de C](../002-niebla-viaje/revision-integracion.md), sección «Revisión anterior». | Copia aislada con A `9730482`, B `694dcf6`, C `3198f55` y D `02da6b6`. Identifica conflictos, seis casos con preparación incorrecta y un parche propuesto. Repetición: 672 pruebas/67.257 s, OK, cinco omisiones. También señala conexiones aún pendientes en aquella fecha; no es una aprobación de integración completa. |
| A↔C: C revalida una integración posterior | Juan, [`8526e3c`](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta/commit/8526e3c), 12 de noviembre, 10:03. Mismo informe, «Actualización del 12 de noviembre». | Exportación limpia de `d796dae`: 753 pruebas/100.664 s, OK, seis omisiones; comparación de rutas, 41 pruebas sin omisiones; selección integrada, 90 pruebas. Registra las limitaciones pendientes de motor/viaje/historia de ese corte. Los conjuntos se solapan. |
| A↔C: A documenta aceptación técnica del contrato integrado con C | Sebastián, [`f9df7ab`](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta/commit/f9df7ab), 14 de noviembre, 07:10. [Contrato de A](../001-terreno-cazador/contracts/integracion.md), filas E-C-RUTA, E-C-DESPACHO, E-C-OBS y E-C-UNDO. | Registra el protocolo filtrado consumido por el planificador de C, adopta el despacho del cazador y relaciona observación/reversión con pruebas integradas. Acredita aceptación técnica documentada por A; el propio contrato distingue ese alcance de declaraciones personales de otros integrantes. |
| B↔D: B revisa inicio, datos y rendimiento integrados con D | Heifryl, [`7662353`](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta/commit/7662353), 10 de noviembre, 12:27. [Tareas de B](../001-verificador-resolubilidad/tasks.md), «Revisión de B del 2026-11-10». | T026 registra seis inicios y tres verificaciones en procesos nuevos con motor/controlador reales. T032 registra 162 pruebas: 161 aprobadas y una omitida. Señala defectos de presentación y del benchmark para D; no declara resueltos esos hallazgos en esa revisión. |
| B↔D: B revalida un commit concreto de D | Heifryl, [`4794a86`](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta/commit/4794a86), 10 de noviembre, 22:55. Mismo archivo, «Revalidación del commit de D `6de00bf` por B». | Confirma causa y leyenda de alcanzabilidad, diez repeticiones del benchmark, máximo incremental de 4.194 ms y cero solicitudes offline. Documenta conflictos y una prueba aún pendiente por el diagnóstico de ruta: 22 de 23 tras adaptar temporalmente dos paquetes negativos. |
| B↔D: integración posterior a la revalidación | Heifryl, [`8b88125`](https://github.com/hjvillalobos/Proyecto-1-Estructuras-De-Datos-Cripta/commit/8b88125), 10 de noviembre, 22:57. | Hito de integración del cierre de B y D posterior al registro anterior. El merge acredita incorporación de cambios; no se usa por sí solo para convertir la prueba pendiente de aquel ensayo en aprobada. Las pruebas integradas posteriores tienen sus propios resultados en este informe y en el estado de entrega. |

**Balance de evidencia.** Hay registros de revisión y hallazgos del equipo para ambos cruces, además de la declaración de Belén y la comprobación posterior de Codex. Por ello se corrige la conclusión anterior de ausencia total de registros. La dirección C→integración con A y B→D tiene informes concretos; A registra aceptación técnica de contratos con C. Los aportes e integración de D están identificados en la tabla anterior, sin inferir de ellos una aprobación personal de cada PR de B.

La constitución 1.1.0 exige revisión cruzada de PRs en incrementos pequeños. Estos registros permiten acreditar revisión del trabajo entre capacidades dentro de los cortes descritos; no permiten afirmar que cada PR fue aprobado antes de integrarse por ambos responsables. No se modifican casillas históricas ni se crean firmas o fechas retrospectivas. La consulta de revisiones de PR mediante la API de GitHub no pudo completarse por resolución DNS; no se afirma que falten aprobaciones en el servidor a partir de esa imposibilidad de consulta.

### Cómo comprobar las fuentes

Desde la raíz del proyecto, los siguientes comandos permiten contrastar autoría, fecha y contenido original, sin depender de que la API esté disponible:

```text
git show --format=fuller a1e0184 -- specs/002-niebla-viaje/revision-integracion.md
git show --format=fuller 8526e3c -- specs/002-niebla-viaje/revision-integracion.md
git show --format=fuller f9df7ab -- specs/001-terreno-cazador/contracts/integracion.md
git show --format=fuller 7662353 -- specs/001-verificador-resolubilidad/tasks.md
git show --format=fuller 4794a86 -- specs/001-verificador-resolubilidad/tasks.md
git show --format=fuller --stat 8b88125
```

## Conclusión

La integración cuenta con contribuciones trazables de A/B/C/D, confirmación de pruebas del equipo, registros históricos de revisión entre capacidades y una comprobación técnica reproducible de los cruces: 66 pruebas aprobadas sobre `42ee527`. La última regresión integral registrada, tras Tigresa, es de 873 pruebas con cuatro omisiones descritas en [el estado de entrega](../../ESTADO_ENTREGA.md); no se suman los conjuntos. La evidencia de revisión deja de figurar como totalmente ausente, conservando el límite sobre aprobaciones previas de cada PR y las salvedades históricas de prompts y orden de commits.
