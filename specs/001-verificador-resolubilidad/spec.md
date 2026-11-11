# Feature Specification: Verificador de resolubilidad

**Feature Branch**: `codex/verificador-resolubilidad`

**Created**: 2026-10-30

**Status**: Preparación documental revisada; C1 cerrado por aclaración del profesor comunicada por el usuario el 2026-11-02. Pendiente commit de especificación antes del código.

**Input**: User description: "Y genera la especificacion de mi nueva parte, el verificador de resolubilidad, definiendo primero que debe hacer y como se acepta, despues seguiriamos con las declaraciones, plan, tareas y codigo"

## Clarifications

### Session 2026-11-01

- Q: ¿Cómo se interpreta un mismo ID de llave en varias salas? → A: Son ubicaciones alternativas válidas; basta alcanzar una para obtener la llave una sola vez. No se rechazan por repetir el ID.
- Q: ¿Cómo se trata una llave requerida que no aparece en el listado? → A: Si el listado completo y válido corresponde a la versión analizada, la llave es imposible de obtener y sus puertas cerradas permanecen bloqueadas. El análisis continúa considerando rutas alternativas. Una descarga fallida, datos incompletos, archivos ausentes, versiones incompatibles o entradas inválidas producen una verificación no completada, no un dictamen negativo.

- Q: ¿Se exige una trayectoria única que reúna las llaves en mapas con salidas sin regreso? → A: No en el alcance adoptado. Se analiza la región alcanzable acumulando llaves y usándolas desde cualquier sala incorporada. En esta sesión era un supuesto provisional del equipo. La confirmación posterior se registra en la sesión 2026-11-02; no es una garantía de trayectoria única.

### Session 2026-11-02

- Q: ¿Podemos acumular llaves entre salas alcanzables sin exigir una trayectoria única? → A: Sí, según respuesta afirmativa del profesor comunicada por el usuario. C1 queda aprobado para este alcance; se conserva la limitación y AC-21.

## Alcance del dictamen

En esta especificación, «resoluble» significa que se cumple la condición de salida bajo el modelo de alcanzabilidad acumulada. Las llaves obtenibles se conservan globalmente y habilitan puertas desde cualquier sala ya alcanzada, sin exigir que el jugador pueda regresar físicamente a ella. Las conexiones mantienen su dirección: no se inventan salidas inversas.

En mapas con ramas sin regreso, un dictamen positivo no garantiza una trayectoria jugable única. Esta limitación se conserva como descripción del modelo, no como incumplimiento pendiente: el profesor aceptó expresamente la acumulación sin trayectoria única, según la respuesta comunicada por el usuario el 2026-11-02. La confirmación se limita a este alcance; no demuestra corrección del código ni rendimiento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Saber si existe una victoria posible (Priority: P1)

Como jugador, quiero saber antes de comenzar si la cripta admite una victoria
bajo los supuestos del enunciado y el alcance acumulativo declarado, para identificar bloqueos estructurales dentro de ese modelo.

**Why this priority**: Es la decisión principal del verificador y evita falsos positivos.

**Independent Test**: Entregar una cripta pequeña con resultado conocido y comprobar
el dictamen y el orden de llaves sin iniciar una partida.

**Acceptance Scenarios**:

1. **AC-01**: Dada una cadena de puertas cuyas llaves se obtienen en salas previamente
   alcanzables, cuando se verifica, entonces se declara resoluble si se obtiene la llave
   de salida y se cruza hacia la sala de salida una puerta que la requiere. El orden
   informado permite obtener cada llave usando únicamente las anteriores. (FR-001–004)
2. **AC-02**: Dada una ruta abierta a la sala de salida, cuando falta la llave de salida
   o no existe una entrada alcanzable a esa sala que la requiera, entonces no se declara
   victoria posible únicamente por alcanzar esa sala. Si el listado completo y válido
   no contiene la llave de salida, el dictamen es no resoluble. (FR-002, FR-006, FR-008)
3. **AC-03 / R2**: Dada una llave soltada por un enemigo errante, cuando se verifica,
   entonces su ubicación es la sala inicial informada para ese enemigo; sus movimientos
   posteriores y su dificultad de combate no cambian la conclusión. (FR-003, FR-010)
4. **AC-04 / R3**: Dadas varias llaves obtenibles en distintos órdenes válidos, cuando
   se verifica diez veces la misma entrada, entonces se obtiene el mismo dictamen y
   el mismo orden válido en las diez ejecuciones. (FR-004, FR-007)
5. **AC-05**: Dadas varias puertas que requieren la misma llave, trampas y cierres
   automáticos en la ruta, cuando se verifica, entonces la llave puede reutilizarse
   y esos elementos no impiden por sí solos la resolubilidad. (FR-003)

### User Story 2 - Entender qué bloquea la cripta (Priority: P1)

Como jugador o integrante del equipo, quiero un reporte verificable de los bloqueos
y ciclos para entender una respuesta negativa.

**Why this priority**: Un dictamen negativo sin explicación no cumple el enunciado.

**Independent Test**: Analizar criptas sintéticas con una llave autoencerrada, una
cadena circular y una región desconectada; comparar el reporte con sus datos.

**Acceptance Scenarios**:

1. **AC-06 / R1**: Dada la llave de salida detrás de la única puerta que ella misma
   abre, cuando se verifica, entonces el resultado es no resoluble y señala la llave
   inalcanzable, la puerta bloqueada, su requisito, la ubicación y el ciclo concreto.
   (FR-005–007)
2. **AC-07**: Dadas una llave A accesible solo con B y una llave B accesible solo con A,
   ambas necesarias para la salida, cuando se verifica, entonces se informa el ciclo
   A → B → A con las puertas y ubicaciones que lo justifican. (FR-005–007)
3. **AC-08**: Dada una puerta hacia una región bloqueada y otra ruta abierta que permite
   obtener su llave, cuando se verifica, entonces no se reporta esa dependencia como un
   ciclo impeditivo; se considera la ruta alternativa. Esto también se cumple si el mismo
   ID tiene una ubicación accesible y otra detrás de la puerta que requiere esa llave:
   se acepta el listado, se obtiene la llave una sola vez y se permite abrir la puerta.
   (FR-001, FR-004, FR-005, FR-007)
4. **AC-09**: Dada una llave en una región desconectada, cuando se verifica y no se
   puede ganar, entonces se informa su inaccesibilidad sin inventar un ciclo ni una
   puerta fronteriza. La frontera puede estar vacía. (FR-005, FR-006)
5. **AC-10**: Dada una cripta ganable con llaves opcionales inaccesibles, cuando se
   verifica, entonces esas llaves no convierten el dictamen en no resoluble. También
   se mantiene el dictamen positivo si una puerta opcional requiere una llave ausente
   del listado completo y válido, pero otra ruta permite ganar. Si esa puerta es
   indispensable para ganar y no hay alternativa, el resultado es no resoluble y
   el diagnóstico identifica la llave sin ubicación conocida. (FR-002, FR-005, FR-008)

### User Story 3 - Verificar con datos válidos, en línea u offline (Priority: P1)

Como usuario, quiero que el resultado corresponda a la versión seleccionada y que
pueda obtenerse sin conexión cuando disponga de los datos completos.

**Why this priority**: Un análisis correcto sobre datos incompletos o mezclados no es fiable.

**Independent Test**: Preparar los mismos datos mediante una fuente simulada y una
copia local compatible; comparar resultados y contabilizar las solicitudes.

**Acceptance Scenarios**:

1. **AC-11**: Dadas las ubicaciones de llaves descargadas para una versión, cuando se
   repite la preparación con esa versión válida, entonces se reutilizan. Si cambia la
   versión, no se mezclan los datos antiguos con el nuevo esqueleto. (FR-008–011)
2. **AC-12**: Dada una preparación que necesita solicitar llaves y reintentar, cuando se
   ejecuta, entonces cada intento y consulta de versión consume presupuesto, el cliente
   conserva su identificador y las esperas no avanzan el reloj virtual. (FR-009)
3. **AC-13**: Dados todos los datos compatibles en almacenamiento local, cuando se
   solicita verificación offline, entonces produce el mismo resultado que con esos
   datos en línea y realiza cero solicitudes de red. (FR-011)
4. **AC-14**: Dados datos necesarios ausentes, corruptos o incompatibles, o un presupuesto
   insuficiente para completarlos, cuando se verifica, entonces se informa que no pudo
   completarse y se indica la causa; no se presenta una cripta desconocida como no
   resoluble ni como resoluble. Una descarga fallida y una entrada de llave sin `sala`
   obligatoria producen este resultado. En cambio, una llave requerida ausente de un
   listado completo y válido no impide completar la verificación. (FR-008, FR-011, FR-012)

### User Story 4 - Usar el resultado antes de jugar (Priority: P2)

Como jugador, quiero consultar solo la verificación o recibir su resultado antes
de iniciar una partida. La conexión con las opciones de inicio corresponde a D.

**Why this priority**: Permite integrar el análisis de B sin duplicar sus reglas en la interfaz.

**Independent Test**: Entregar resultados conocidos al responsable del inicio y comprobar
la decisión de iniciar o bloquear; la prueba completa se realizará al integrar B con D.

**Acceptance Scenarios**:

1. **AC-15 / R4**: Dada una cripta no resoluble y sin `--forzar`, cuando se intenta jugar,
   entonces se muestra el reporte y no comienza la partida. (FR-013)
2. **AC-16**: Dada una cripta no resoluble con `--forzar`, cuando se intenta jugar,
   entonces puede iniciarse después de mostrar el diagnóstico, conservando el dictamen
   negativo. La opción no corrige los datos ni convierte el resultado en positivo. (FR-013)
3. **AC-17**: Dada la opción `--verificar <cripta>`, cuando se ejecuta, entonces solo se
   prepara y verifica esa cripta, se muestra el resultado y se termina sin instanciar
   la vista ni iniciar el motor de la partida. (FR-013, FR-014)
4. **AC-18**: Dada información completa descargada antes de jugar, cuando se verifica,
   entonces no se exploran salas del mapa del jugador, no se activan enemigos o trampas,
   no cambia la aleatoriedad de la partida y no avanza el tiempo virtual. (FR-014)

### User Story 5 - Comprobar el rendimiento con evidencia (Priority: P2)

Como integrante del equipo, quiero medir el costo de la verificación para justificar
que las criptas con muchas llaves no exigen repetir todo el trabajo por cada llave.

**Why this priority**: Es un requisito evaluado y necesita evidencia, no solo una afirmación.

**Independent Test**: Medir entradas reproducibles crecientes y la mayor cripta publicada,
con todos los datos disponibles antes del intervalo medido.

**Acceptance Scenarios**:

1. **AC-19**: Dadas cadenas crecientes de llaves, cuando se compara con la alternativa
   de recorrer otra vez la cripta por cada llave, entonces se obtienen los mismos
   dictámenes y órdenes válidos y se registran tiempos y trabajo realizado. (FR-015, SC-004)
2. **AC-20**: Dada la mayor cripta publicada, cuando se mide en el equipo local sin
   descargas ni renderizado, entonces se informa si la verificación completa, incluido
   el resultado o diagnóstico, cumple el límite de 200 ms. (FR-015, SC-003)

### Aceptación del alcance acumulativo

- **AC-21**: Dado Inicio con una salida abierta sin regreso hacia A que contiene K, y otra puerta desde Inicio hacia Salida que requiere K, siendo K la llave de salida, cuando se verifica, entonces el resultado es resoluble bajo alcanzabilidad acumulada. El reporte identifica ese modelo y no afirma que exista una trayectoria única. Si se elimina la ubicación de K del listado completo válido, el resultado es no resoluble. (FR-001, FR-002, FR-013)

### Escenarios adicionales de revisión

- **AC-22**: Dada una región desconectada de Inicio aun ignorando cerraduras, con una llave K en A, una salida abierta A→B y una puerta B→A que requiere K, cuando se verifica, entonces se informa desconexión y no se presenta la puerta de regreso como causa comprobada del bloqueo de K. Una relación circular encontrada, si se muestra, se distingue de una causa. (FR-005–007)
- **AC-23**: Dados datos válidos locales de V1 y una descarga durante la cual el servicio cambia a V2, cuando falla la comprobación final, entonces la verificación no se completa, el lote no se publica bajo V1 y la siguiente ejecución offline conserva los datos previos o informa los faltantes sin consumir el lote rechazado. Lo mismo aplica si falla la consulta final o se agota el presupuesto. (FR-008–012)

- **AC-24**: Dado un ciclo A→B→A y una ubicación alternativa de A bloqueada por C, donde C está autoencerrada, cuando se verifica, entonces se informan ambos grupos circulares, la alternativa que depende de C y sus puertas/ubicaciones. No se omite el ciclo A→B→A ni se declara su puerta como única causa. (FR-005–007)
- **AC-25**: Dado un grupo conectado de dependencias con varios ciclos y varias llaves, cuando se verifica, entonces el reporte incluye todas las llaves implicadas, al menos un ciclo concreto del grupo y evidencia de todas las alternativas bloqueadas, sin duplicar una explicación completa por llave. (FR-005–007, FR-015)

### Edge Cases

- Llaves en la sala inicial, ninguna llave obtenible y varias llaves en una misma sala.
- Una llave abre varias puertas; obtenerla debe reconsiderar todas las posibilidades relevantes.
- Una llave tiene varias ubicaciones: basta una ubicación alcanzable; no todas son requisitos.
- Salas con identificadores no consecutivos, ciclos de salas y salidas de un solo sentido:
  se respetan las conexiones declaradas, sin inventar conexiones inversas.
- Llegar a la sala de salida por una puerta distinta, aun teniendo la llave de salida,
  no sustituye la condición de victoria exigida.
- Llaves opcionales inalcanzables y ciclos que tienen una vía alternativa de acceso.
- Una salida abierta se puede atravesar sin poseer la llave que pueda declarar.
- Una llave requerida ausente del listado completo y válido es imposible de obtener;
  sus puertas cerradas permanecen bloqueadas, sin impedir analizar otras rutas.
- Si falta la llave de salida en ese listado, no puede cumplirse la condición de victoria.
- Un listado vacío válido no equivale a una descarga fallida ni a un archivo ausente.
- Una salida hacia una sala inexistente o un dato de llave sin identificador o sala válida
  produce un error de datos, no un dictamen de resolubilidad.
- `--forzar` no suple datos ausentes ni hace válida una cripta mal formada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El verificador DEBE partir de la sala inicial y determinar todas las salas
  y llaves alcanzables a medida que se obtienen llaves, respetando las conexiones declaradas.
  DEBE acumular las llaves globalmente y habilitar con ellas salidas desde cualquier
  sala ya incorporada, sin exigir regreso ni una trayectoria única (AC-21).
- **FR-002**: DEBE declarar resoluble únicamente cuando pueda obtenerse `llave_salida`
  y habilitarse desde una sala alcanzada una entrada a `sala_salida` que requiere esa llave,
  bajo el modelo acumulativo declarado. No DEBE
  exigir obtener llaves opcionales para declarar una victoria posible.
- **FR-003**: DEBE aplicar los supuestos de §3.5: salidas abiertas transitables, cerradas
  transitables con su llave, llaves no consumibles, enemigos derrotables, llaves soltadas
  obtenibles en la sala inicial del enemigo y trampas y cierres automáticos no bloqueantes.
  No DEBE certificar supervivencia, recursos de combate ni una ruta de costo mínimo.
- **FR-004**: Para una cripta resoluble DEBE entregar un orden de las llaves obtenibles,
  sin repetir identificadores, en el que cada llave sea obtenible desde el inicio usando
  solo llaves anteriores. Debe contemplar rutas y ubicaciones alternativas. Varias
  entradas con el mismo ID son válidas: basta alcanzar una ubicación para obtener
  la llave una sola vez, sin exigir alcanzar las demás.
- **FR-005**: Para una cripta no resoluble DEBE entregar las llaves inalcanzables, sus
  ubicaciones conocidas y la frontera bloqueada: puertas cerradas adyacentes a la región
  alcanzable cuyo requisito aún no está disponible, con origen, destino y llave requerida.
  Si una llave requerida no figura en el listado completo y válido, DEBE indicarse
  que no tiene ubicación conocida, sin inventar una ubicación ni un ciclo.
- **FR-006**: DEBE explicar por qué no se satisface la condición de salida y distinguir
  falta de acceso a la llave, falta de acceso por una puerta adecuada y ciclos impeditivos.
  Un ciclo informado DEBE identificar las llaves y puertas concretas que lo justifican;
  no se inventan ciclos para regiones meramente desconectadas. Una relación circular
  encontrada no se presenta como causa comprobada de bloqueo sin evidencia de que
  las alternativas no permiten iniciar la obtención de las llaves implicadas.
  El reporte explica todas las alternativas no disponibles de cada llave inaccesible,
  distinguiendo ausencia de ubicación, desconexión y dependencias circulares con o sin
  otros bloqueos. No exige enumerar todos los ciclos posibles ni una causa mínima única:
  muestra ciclos concretos y conserva evidencia de las demás relaciones, sin presentar
  un ejemplo como si incluyera todas las llaves del grupo.
- **FR-007**: Para una misma entrada DEBE entregar idéntico dictamen y orden de reporte,
  incluidas llaves, puertas y ciclos. Las dependencias deben reflejar obstáculos reales;
  una ruta alternativa accesible no puede generar un falso bloqueo.
- **FR-008**: La preparación DEBE reunir metadatos, esqueleto completo y ubicaciones de
  llaves de una misma versión de cripta, validarlos y distinguir una lista de llaves vacía
  válida de una respuesta o archivo ausente. Los datos del catálogo mantienen su versión propia.
  Los datos recién descargados no DEBEN publicarse como reutilizables antes de validar
  el conjunto y confirmar la versión final. Si cambia la versión o falla esa comprobación,
  se conservan las copias válidas previas y una ejecución posterior no reutiliza el lote rechazado.
  Una llave requerida que no aparece en ese listado completo y válido DEBE considerarse
  imposible de obtener, manteniendo bloqueadas las puertas cerradas que la requieren
  y continuando el análisis de rutas alternativas. Su ausencia no constituye por sí
  sola un error de datos ni demuestra que toda la cripta sea no resoluble.
- **FR-009**: Toda solicitud necesaria para preparar la verificación DEBE respetar el
  presupuesto y el identificador de cliente de la ejecución, incluidos reintentos y
  consultas de versión. La espera de datos no DEBE modificar el tiempo virtual.
- **FR-010**: Las ubicaciones de llaves DEBEN conservar el identificador de llave, la
  sala y, cuando exista, la instancia de enemigo que la suelta. Su validez y reutilización
  DEBEN estar asociadas a la versión de cripta, sin borrar manualmente copias antiguas.
- **FR-011**: La preparación offline DEBE usar exclusivamente datos locales compatibles,
  dar el mismo resultado lógico para los mismos datos e informar qué falta o es inválido.
- **FR-012**: DEBEN distinguirse tres resultados: resoluble, no resoluble y verificación
  no completada por error o datos insuficientes. Solo los dos primeros son dictámenes;
  nunca se inicia automáticamente una partida tras una verificación no completada.
  Descargas fallidas, archivos ausentes, datos incompletos, versiones incompatibles
  y entradas sin campos obligatorios DEBEN producir el tercer resultado. No DEBEN
  interpretarse como evidencia de que una llave sea imposible de obtener.
- **FR-013**: B DEBE entregar un resultado con información suficiente para que D muestre
  el reporte, bloquee el inicio negativo salvo `--forzar` y conecte `--verificar <cripta>`.
  El resultado DEBE identificar el modelo de alcanzabilidad acumulada y su limitación
  de trayectoria única; D debe mostrar este alcance junto al dictamen.
  Las opciones y la presentación se aceptan mediante pruebas de integración con D.
- **FR-014**: El análisis DEBE trabajar con los datos ya preparados, sin solicitudes de
  red ni dependencia de la vista o de una partida en ejecución. No DEBE modificar los
  datos de entrada, conocimiento del jugador, actores, tiempo o estado aleatorio.
- **FR-015**: El costo total DEBE crecer aproximadamente de forma lineal con salas,
  salidas y llaves. No se permite repetir el recorrido completo por cada llave; frontera
  y dependencias deben obtenerse del mismo análisis. La medición DEBE incluir la
  alternativa repetitiva y entradas sintéticas reproducibles por semilla.

### Key Entities *(include if feature involves data)*

- **Cripta versionada**: Identidad, versión, sala inicial, sala de salida y llave de salida.
- **Esqueleto**: Salas y conexiones con destino, estado inicial y requisito de llave.
- **Ubicación de llave**: Identificador, sala inicial y posible instancia de enemigo portador.
  Un mismo identificador puede tener varias ubicaciones alternativas.
- **Región alcanzable**: Salas a las que se puede acceder con las llaves obtenidas.
- **Frontera bloqueada**: Puertas que impiden ampliar esa región por falta de una llave.
- **Dependencia de llaves**: Necesidad de otras llaves para alcanzar una ubicación,
  teniendo en cuenta que pueden existir alternativas.
- **Resultado de verificación**: Dictamen, orden de llaves o diagnóstico de imposibilidad;
  si el análisis no puede completarse, causa y datos afectados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los cuatro casos R1–R4 del reparto, correspondientes al bloque
  Resolubilidad del Apéndice B, tienen el resultado exigido mediante AC-06, AC-03,
  AC-04 y AC-15. R4 requiere integración con D.
- **SC-002**: Todos los escenarios AC-01–AC-25 y casos borde cuentan con evidencia
  reproducible; no hay falsos positivos respecto del modelo acumulativo ni ciclos impeditivos falsos en
  las entradas de aceptación. Diez repeticiones de cada entrada producen igual resultado.
- **SC-003**: La verificación de la mayor cripta publicada tarda como máximo 200 ms
  en el equipo local, excluyendo adquisición de datos y renderizado. Se registran
  versión de cripta, equipo, repeticiones y variación; el promedio no oculta excesos.
- **SC-004**: La comparación con el recorrido repetitivo usa iguales entradas de
  cadenas de llaves de al menos tres tamaños crecientes y casos con ciclos. Se
  documentan tiempos y conteos de trabajo que permitan evaluar el crecimiento
  aproximadamente lineal, sin presentar una medición aislada como prueba de complejidad.
  Se distinguen preparación interna, recorrido, diagnóstico y reporte, incluyendo todos
  en el tiempo total. Se informan razones de crecimiento entre tamaños y trabajo por
  elemento; una fase con crecimiento superior al lineal se declara expresamente y
  se evalúa frente a FR-015, sin convertirla por redacción en cumplimiento automático.
- **SC-005**: En las pruebas offline hay cero solicitudes de red; en línea, los conteos
  de intentos coinciden con el presupuesto consumido. Ningún caso mezcla versiones.
- **SC-006**: El análisis aislado no cambia datos de entrada ni estado de partida;
  la verificación exclusiva no inicia la vista. La integración bloquea todos los
  dictámenes negativos sin `--forzar` y todos los análisis no completados.

## Assumptions

- Fuente utilizada: copia textual local «Enunciados_CRIPTA_Parte_II_para_Amazon_Q.md»,
  apartado «Cripta - Parte II», páginas 6–10 y 12–13: §3.5, §4.2–4.3, §5.4,
  §6.1–6.3 y apéndices A–B. También se consultó el reparto, Persona B, página 4.
  El nombre del archivo es histórico; el agente acordado sigue siendo Codex.
  El PDF original no está en su ubicación anterior; debe contrastarse esta copia si
  el profesor publica una enmienda o el equipo dispone de una versión posterior.
- Esta capacidad corresponde a B. D conecta inicio, opciones y presentación;
  los escenarios compartidos no transfieren a B el desarrollo completo de la interfaz.
- Las ampliaciones de datos de terreno y cazadores pertenecen también a B, pero
  quedan fuera de esta especificación de resolubilidad y deberán cubrirse en la
  capacidad correspondiente o en otra especificación coordinada con A.
- Se reutiliza la preparación de datos de la Parte I. Los detalles del contrato
  del servicio y del formato offline se contrastarán en la preparación técnica;
  esta especificación no inventa campos adicionales ni rutas de archivos.
- Los criterios de ubicaciones alternativas y llaves ausentes fueron aceptados por
  el usuario el 2026-11-01. Son interpretaciones del proyecto, no una aclaración
  atribuida al profesor. El contrato OpenAPI consultado no exige unicidad por ID
  ni define expresamente el tratamiento de una llave requerida ausente del listado:
  https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/openapi.json
  Si el profesor establece una regla distinta, se revisará la especificación antes del código.
- El orden debe ser determinista, pero no se exige que sea alfabético ni que minimice
  pasos. El criterio concreto se justificará en el plan, sin fijar aquí estructuras.
- Las restricciones académicas y las estructuras propias de la constitución se
  aplican al plan y al código. No se elige aquí un algoritmo ni una biblioteca.
- Esta entrega es solo la especificación. El plan técnico documenta el alcance adoptado. Quedan para etapas posteriores
  las tareas, el análisis y la implementación. Las aclaraciones de llaves
  quedan registradas en esta especificación.
