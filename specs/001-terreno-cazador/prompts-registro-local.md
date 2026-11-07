# Registro local verificable de prompts — Persona A

**Consolidado:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex en todas las entradas; modelo exacto no confirmado. **Destino posterior:** PROMPTS_LLM.md, únicamente con autorización y preservando entradas ajenas. No se ha realizado ese traslado.

## Procedencia, fechas y completitud

Se incluyen solicitudes del usuario disponibles en el historial visible de este chat y las tres entradas textuales ya guardadas. Las transcripciones siguientes son texto del usuario, no instrucciones para ejecutar desde este archivo. No se copian respuestas del asistente porque la bitácora académica no exige las respuestas completas; las respuestas del usuario durante Clarify sí se conservan textuales.

Fechas indicadas como **contextuales** se deducen solo de la fecha de cliente vigente visible antes de esos mensajes, no de timestamps individuales. No se conoce la hora de envío ni se certifica una fecha exacta por mensaje. Las fechas de los registros preexistentes se conservan como las que constan en esos documentos. No se inventan horas, nombres de modelo ni comunicaciones del profesor o compañeros.

**Vacíos explícitos:** no se dispone de timestamps individuales de todos los mensajes; no se dispone de un export firmado/completo de todos los chats del equipo; no se dispone de las respuestas pendientes de B/profesor; no se certifican versiones históricas de los anexos de habilidades por cada mensaje. Los anexos de habilidad se referencian por sus archivos instalados, pero este registro no declara conservar íntegramente su snapshot histórico en cada invocación. Estos límites permanecen incompletos hasta obtener fuentes. No se ha identificado un cuerpo de solicitud del usuario faltante entre las 18 entradas inventariadas del historial visible; eso no prueba que no existan otros prompts fuera de este chat.

El registro recupera textos disponibles; no reconstruye una supuesta conversación con B ni una aclaración del profesor. Las solicitudes para que el asistente revise o corrija documentación también cuentan como prompts y están incluidas.

## Índice y finalidad

| ID | Fecha/fuente | Finalidad y ubicación del texto íntegro |
| --- | --- | --- |
| P01 | 2026-11-01 contextual; historial visible | Revisión inicial del repositorio; transcripción debajo. |
| P02 | 2026-11-01 contextual; historial visible | Verificar invocación de habilidades/PATH; debajo. |
| P03 | 2026-11-01 contextual; historial visible | Fijar responsabilidad A y restricciones; debajo. |
| P04 | 2026-11-01 contextual; historial visible | Leer documentos oficiales/reparto y resumir aceptación; debajo. |
| P05 | 2026-11-01 según registro existente y fuente de texto pegado | Solicitud Specify íntegra en [registro previo, sección Solicitud original](prompt-registro-pendiente.md). No se reemplaza por resumen. |
| P06 | 2026-11-01 contextual; historial visible y registro previo | Excepción para feature.json; texto íntegro en [registro previo, sección Autorización posterior](prompt-registro-pendiente.md). |
| P07 | 2026-11-01 contextual, sin timestamp individual; historial visible | Invocación inicial de Clarify; debajo. La sesión registrada en spec posteriormente está fechada 2026-11-02, sin alterar retrospectivamente este contexto. |
| P08 | 2026-11-02 contextual; historial visible | Respuesta breve B a Q1, antes de interrupción; debajo. |
| P09 | 2026-11-02 contextual; historial visible | Reanudación explícita y confirmación de Q1 pendiente; debajo. |
| P10 | 2026-11-02 contextual; historial visible | Respuesta Q2 y continuar Clarify; debajo. |
| P11 | 2026-11-02 contextual; historial visible | Respuesta Q3, sin referencia oficial; debajo. |
| P12 | 2026-11-02 contextual; historial visible | Diagnóstico de lectura antes de Plan; debajo. |
| P13 | 2026-11-02 según registro existente | Prompt Plan íntegro en [registro de Plan](prompt-plan-registro-pendiente.md#prompt-íntegro). |
| P14 | 2026-11-02 contextual; historial visible | Revisar seis documentos de Plan; debajo. |
| P15 | 2026-11-02 contextual; historial visible | Autorizar las tres correcciones de Plan; debajo. |
| P16 | 2026-11-02 según registro existente | Prompt Tasks íntegro en [registro de Tasks](prompt-tasks-registro-pendiente.md#prompt-íntegro). |
| P17 | 2026-11-05 contextual; historial visible | Analyze de solo lectura; debajo. |
| P18 | 2026-11-05 contextual; historial visible | Autorizar corrección I1/C1/I2/I3/I4/D1 y recuperación fiel de prompts; debajo. |
| P19 | 2026-11-05 contextual; historial visible; Codex | Segunda revisión Analyze en lectura; texto íntegro añadido debajo. |
| P20 | 2026-11-05 contextual; historial visible; Codex | Corregir I1/I5/C2, separar costos/rango y registrar comunicación de B; texto íntegro añadido debajo. |
| P21 | 2026-11-05 contextual; historial visible; Codex | Implementación limitada T005–T010 y sus pruebas; texto íntegro añadido debajo. |
| P22 | 2026-11-05 contextual; historial visible; Codex | Preparar y ejecutar exclusivamente pruebas T011/T012 y fundamentos; texto íntegro añadido debajo. |
| P23 | 2026-11-05 contextual; historial visible; Codex | Corregir defectos auditados de pruebas/fixtures T011/T012 y registrar evidencia; texto íntegro añadido debajo. |

Los tres registros enlazados contienen texto íntegro, fecha/herramienta/finalidad y forman parte de este archivo lógico local. Se conservan físicamente sin sobrescribirlos. Para un traslado posterior se deben anexar sus textos, no solo los enlaces. Anexos de habilidades referenciados: ../../.agents/skills/speckit-specify/SKILL.md, ../../.agents/skills/speckit-clarify/SKILL.md, ../../.agents/skills/speckit-plan/SKILL.md, ../../.agents/skills/speckit-tasks/SKILL.md, ../../.agents/skills/speckit-analyze/SKILL.md. En P15 se adjuntaron además Analyze/Implement/Tasks como contexto; el cuerpo del usuario prohibía ejecutarlos y prevaleció. No se interpreta un anexo como autorización contraria al cuerpo.

## P01 — revisión inicial

```text
Necesito preparar este repositorio para desarrollar Cripta Parte II mediante GitHub Spec Kit 1.2.3.

Por ahora, realiza únicamente una revisión de lectura. No modifiques, crees ni elimines archivos, no ejecutes comandos que cambien el repositorio y no realices commits, merges ni push.

1. Confirma la ruta del repositorio y la rama Git actual.
2. Verifica que exista `.specify/memory/constitution.md` y resume sus principios.
3. Comprueba que estén disponibles las habilidades de Spec Kit en `.agents/skills/`.
4. Revisa `.specify/init-options.json` y `.specify/integration.json` para identificar la configuración existente.
5. Indica qué falta para comenzar el flujo de especificaciones, sin realizar cambios.

Debemos conservar la configuración y la constitución creadas por mis compañeros.
```

## P02 — habilidades y PATH

```text
Ya comprobé desde la terminal de PyCharm que GitHub Spec Kit 1.2.3 está instalado y funciona mediante `specify version`.

Quiero comprobar que puedes utilizar las habilidades de Spec Kit que ya existen en `.agents/skills/`.

Revisa específicamente la habilidad `speckit-specify` y dime cómo debo invocarla desde esta aplicación de Codex.

No ejecutes todavía la habilidad, no crees especificaciones, no modifiques archivos y no hagas commits ni push.

Confirma también si necesitas que el ejecutable `specify` esté disponible en tu PATH para utilizar las habilidades existentes.
```

## P03 — responsabilidad y restricciones de A

```text
Vamos a comenzar Cripta Parte II. Soy la **Persona A**, responsable de terreno, cazador, motor de eventos y validez de rutas.

Antes de iniciar Spec Kit, quiero establecer estas restricciones obligatorias para mi trabajo.

**1. Constitución y documentación**

- Lee íntegramente `.specify/memory/constitution.md` y respeta todas sus reglas.
- Consulta los requisitos de Cripta Parte I y Parte II disponibles en el repositorio. Si falta alguno de los enunciados, avísame antes de generar especificaciones.
- Respeta las restricciones académicas sobre estructuras propias, determinismo, MVC, rendimiento, documentación y trazabilidad.
- No modifiques ni regeneres la constitución.

**2. Archivos de mi responsabilidad**

- Mi trabajo se concentra en `modelo/juego.py`, `modelo/eventos.py` y `modelo/efectos.py`, exclusivamente en la lógica correspondiente a la Persona A.
- Los módulos `modelo/rutas.py` y `modelo/cazador.py` pueden proponerse como archivos nuevos si el plan técnico los justifica.
- Puedes consultar los demás archivos para comprender el proyecto, pero no modificarlos sin mi autorización.
- Si un archivo es compartido, identifica qué funciones pertenecen a otros integrantes antes de proponer modificaciones.

**3. Interfaz gráfica y recursos visuales**

- No modifiques la interfaz, imágenes, animaciones, sonidos ni diseños existentes.
- Si falta un recurso visual para una funcionalidad nueva, infórmame y explica qué se necesita. No reemplaces ni generes recursos sin consultarme.
- La integración visual debe coordinarse con el integrante responsable.

**4. Dependencias de mis compañeros**

- Si falta una clase, función, método, contrato o componente de B, C o D, avísame.
- Indica qué falta, a quién corresponde y cómo afecta mi trabajo.
- No implementes por tu cuenta funcionalidades asignadas a otros integrantes.
- Puedes proponer contratos o mocks para pruebas, pero solicita autorización antes de incorporarlos.

**5. Git**

- Trabaja exclusivamente sobre `feature/motor-eventos`.
- Antes de cualquier operación Git, comprueba la rama y el estado del repositorio.
- No crees ni cambies ramas, ni ejecutes pull, fetch, merge, rebase, reset, commit o push sin mi autorización.
- Si necesitas consultar cambios de mis compañeros, proponme primero los comandos y explica qué información obtendremos.
- No agregues archivos de `.idea/`, respaldos de puntajes ni otros archivos locales sin seguimiento.

**6. Flujo académico de Spec Kit**

- Respeta el orden constitution (ya existe), specify, clarify, plan, tasks, analyze e implement.
- Las especificaciones deben quedar confirmadas en Git antes de implementar código.
- Mantén la trazabilidad entre requisitos, escenarios de aceptación, tareas y pruebas.
- Registra los prompts utilizados en `PROMPTS_LLM.md`, sin modificar entradas existentes.
- No empieces a programar hasta que revisemos y aprobemos la documentación correspondiente.

**Por ahora trabaja únicamente en modo lectura.**

Revisa la constitución, el estado de Git, los archivos y dependencias de la Persona A. Confirma qué puedes modificar, qué debes dejar intacto y qué falta para comenzar `001-terreno-cazador`.

No ejecutes todavía ninguna habilidad de implementación ni crees archivos.
```

## P04 — documentos oficiales y reparto

Archivos mencionados en el mensaje: `D:/Downloads/Cripta - Parte II.pdf`, `D:/Downloads/CRIPTA_Parte_II_Division_de_Trabajo.pdf`, `D:/Downloads/Primer Proyecto - Estructuras de Datos II 2026 (1).pdf`. Cuerpo de la solicitud:

```text
Te adjunto los tres documentos que necesitamos para Cripta Parte II:

1. Enunciado oficial de Cripta Parte I.
2. Enunciado oficial de Cripta Parte II.
3. Propuesta de división de trabajo del equipo.

Yo soy la **Persona A** del reparto. La indicación «B (tú)» del documento corresponde al compañero que lo preparó, no a mí.

Lee los tres documentos completos, incluidos los apéndices.

Utiliza los enunciados oficiales para determinar los requisitos y el documento de división para identificar mis responsabilidades, archivos compartidos y dependencias de B, C y D.

La Parte II amplía la Parte I. Conserva las reglas originales salvo donde el segundo enunciado establezca cambios explícitos.

Contrasta los requisitos de terreno, cazador, rutas, determinismo, eventos, puertas y efectos con la constitución existente.

Prepara un resumen de los requisitos exactos de la Persona A, los casos de aceptación T1–T7 y las dependencias que debemos coordinar con mis compañeros.

Si hay contradicciones o información ausente, infórmame; no inventes requisitos.

Mantén el modo de solo lectura. No ejecutes todavía `$speckit-specify`, no crees archivos, no modifiques código, no cambies de rama y no hagas commits ni push.
```

## P05 y P06 — fuentes textuales preexistentes

P05 procede del adjunto local de Codex `Texto pegado.txt` (ruta de procedencia anonimizada), conservado en prompt-registro-pendiente.md. P06 se conserva en ese mismo registro. El texto íntegro no se duplica aquí para evitar dos copias editables divergentes. Las fuentes enlazadas son parte del registro y deben incluirse al exportarlo.

## P07 — Clarify inicial

```text
$speckit-clarify

Trabaja exclusivamente sobre la especificación existente `specs/001-terreno-cazador/spec.md` de la Persona A.

Lee nuevamente la constitución y utiliza los enunciados oficiales de Cripta Parte I y Parte II como autoridad principal.

Revisa las ambigüedades Q1 (rango del cazador) y Q2 (costos inválidos o asimétricos), además de cualquier otra ambigüedad que afecte los requisitos o escenarios de aceptación.

No inventes reglas que no estén respaldadas por los enunciados, el contrato HTTP oficial o acuerdos del equipo.

Cuando una respuesta dependa del compañero B o de una aclaración del profesor, indícame exactamente qué debo consultar y por qué. No marques esa ambigüedad como resuelta sin evidencia.

Antes de cambiar la especificación, preséntame las preguntas y las posibles respuestas respaldadas, para revisarlas una por una.

Mantén la rama `feature/motor-eventos`. No crees ramas, no modifiques código, la constitución, componentes de mis compañeros, interfaz ni recursos visuales.

No hagas commits, push, pull, fetch, merge, rebase ni reset.

No modifiques `PROMPTS_LLM.md`; conserva el registro textual de esta interacción para incorporarlo posteriormente.

Ejecuta únicamente Clarify. No avances a Plan, Tasks, Analyze ni Implement sin mi autorización.
```

## P08 — primera respuesta a Q1

```text
B
```

Esta respuesta apareció antes de una interrupción voluntaria del turno del asistente. Se conserva además de la confirmación siguiente, sin sustituirla.

## P09 — reanudación de Clarify

```text
Continuemos con `$speckit-clarify` para `001-terreno-cazador`.

Para Q1, selecciono la opción B: consultar al compañero B sobre el contrato oficial del campo `rango` del cazador.

No inventes un valor predeterminado, un mínimo ni una política para datos inválidos. Mantén Q1 identificada como dependencia externa pendiente de confirmación.

Continúa con Q2, sobre los costos inválidos, asimétricos o declarados en un solo sentido.

Quiero completar hoy toda la documentación previa a la implementación, pero sin inventar requisitos ni marcar como resueltas las cuestiones que dependen de B o del profesor.

Mantén la rama `feature/motor-eventos`. No modifiques código, interfaz, constitución ni archivos de otros integrantes. No hagas commits ni push.

Presenta la siguiente pregunta y espera mi respuesta antes de avanzar.
```

## P10 — respuesta a Q2

```text
B. Consultar al compañero B sobre el contrato oficial y mantener Q2 pendiente.

No inventes una política de normalización o rechazo de costos inválidos, asimétricos o declarados en un solo sentido.

Registra Q2 como dependencia externa pendiente de confirmación, igual que Q1.

Continúa revisando si existen otras ambigüedades dentro de Clarify y presenta las preguntas necesarias, una por una.

Mantén las restricciones acordadas: no modificar código, constitución, interfaz ni archivos de mis compañeros. No ejecutar commits, push ni operaciones de integración.

No avances a Plan, Tasks, Analyze ni Implement sin mi autorización.
```

## P11 — respuesta a Q3

```text
B. No dispongo actualmente de la identificación oficial de la cripta de referencia ni de una enmienda del profesor al límite de procesamiento.

Mantén Q3 documentada como información externa pendiente de confirmación.

Conserva el requisito de menos de 20 ms y las condiciones de medición establecidas en los enunciados oficiales. No inventes una cripta de referencia ni afirmes que se cumple el rendimiento sin haber ejecutado las mediciones.

Ya consulté al compañero B sobre Q1 y Q2 y estoy esperando su respuesta.

Continúa con las demás preguntas de Clarify, si existen. Mantén las restricciones sobre archivos y Git y no avances a Plan, Tasks, Analyze ni Implement sin mi autorización.
```

## P12 — diagnóstico de preparación de Plan

```text
Terminamos la primera ronda de Clarify de `001-terreno-cazador`.

Antes de continuar, revisa en modo de solo lectura qué partes del futuro Plan pueden prepararse con los requisitos ya confirmados y cuáles dependen de Q1, Q2 o Q3.

Consulta la constitución vigente y los documentos oficiales. Identifica las alternativas de estructuras de datos propias, las decisiones de diseño que habrá que justificar, las dependencias con B, C y D y las mediciones exigidas para mi funcionalidad.

No selecciones todavía una solución definitiva ni generes `plan.md`, `research.md`, `data-model.md` o `tasks.md`.

No modifiques archivos ni ejecutes otras habilidades de Spec Kit. Tampoco realices operaciones Git.

Presenta únicamente un diagnóstico de preparación para Plan, separando claramente lo confirmado de lo pendiente.
```

## P13 — fuente textual de Plan

Texto íntegro y metadatos en prompt-plan-registro-pendiente.md, enlazado en el índice. No se duplica ni sustituye por una versión resumida.

## P14 — revisión de los seis documentos de Plan

```text
Antes de continuar con Tasks, revisa en modo de solo lectura los seis documentos generados durante Plan para `001-terreno-cazador`.

Comprueba que:

1. No haya contradicciones con `spec.md`, la constitución ni los enunciados oficiales.
2. Las decisiones técnicas estén justificadas y sus alternativas documentadas.
3. No se asignen a la Persona A tareas que pertenecen a B, C o D.
4. Los contratos compartidos sean propuestas pendientes de coordinación, no modificaciones autorizadas.
5. `plan.md` esté completo y no haya perdido información necesaria durante su generación.
6. Q1, Q2 y Q3 permanezcan identificadas como pendientes.
7. Los documentos sean necesarios o útiles y no contengan duplicaciones excesivas.

No modifiques ningún archivo, no ejecutes Tasks ni otras habilidades y no realices operaciones Git.

Devuélveme un diagnóstico de preparación para Tasks, indicando cualquier problema que debamos corregir antes de continuar.
```

## P15 — tres correcciones de Plan

```text
Quiero corregir los tres puntos detectados en la revisión de Plan de la funcionalidad `001-terreno-cazador`, correspondiente a la Persona A.

Antes de modificar archivos, relee la constitución vigente y los documentos existentes de esta funcionalidad.

Autoriza únicamente ajustes documentales dentro de `specs/001-terreno-cazador/`.

**1. Contrato de rutas con C**

Actualiza `contracts/integracion.md` para distinguir explícitamente entre:

- Origen igual a destino: resultado de llegada, sin movimiento.
- Ruta válida: primer paso y costo correspondiente.
- Ruta inexistente o fuera del límite permitido: resultado diferenciado y verificable.

Documenta cómo podría solicitarse una búsqueda sin límite de rango para el viaje automático «ir a», respetando exclusivamente las salas exploradas y puertas recordadas abiertas.

Estas son propuestas de contrato pendientes de acuerdo con C; no las presentes como interfaces ya implementadas ni aprobadas.

**2. Implementación base y alternativas experimentales**

Aclara en `plan.md` y `research.md` que la búsqueda individual limitada es la base propuesta.

El cálculo compartido entre cazadores debe permanecer como alternativa de evaluación. No debe incorporarse automáticamente a producción ni utilizar umbrales de activación que todavía no estén respaldados por mediciones.

**3. Reutilización de rutas**

Aclara que una caché de última consulta es solo una de las alternativas y puede resultar poco representativa cuando varios cazadores alternan consultas.

La evaluación debe comparar diseños bajo cargas equivalentes, considerando tasas de acierto, memoria, invalidaciones, puertas estables e inestables y costos de mantenimiento.

No concluyas que la reutilización no conviene basándote únicamente en esa caché.

**Restricciones adicionales**

- Conserva Q1, Q2 y Q3 como pendientes.
- No inventes acuerdos con B, C o D.
- No modifiques la constitución, código Python, interfaz, recursos gráficos ni archivos compartidos.
- Conserva la rama `feature/motor-eventos`.
- No ejecutes commits, push, pull, fetch, merge, rebase ni reset.
- Si la corrección requiere modificar algo fuera de `specs/001-terreno-cazador/`, detente y solicita autorización.
- No ejecutes todavía `$speckit-tasks`, `$speckit-analyze` ni `$speckit-implement`.

Al terminar, indica exactamente qué archivos modificaste, qué aclaraste y qué dependencias siguen pendientes.
```

## P16 — fuente textual de Tasks

Texto íntegro y metadatos en prompt-tasks-registro-pendiente.md, enlazado en el índice. No se duplica ni se altera su fecha de creación.

## P17 — Analyze solicitado

```text
$speckit-analyze

Analiza la documentación existente de `001-terreno-cazador`, correspondiente a la Persona A de Cripta Parte II.

Revisa íntegramente la constitución vigente, `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/integracion.md`, `quickstart.md`, `tasks.md` y el checklist de requisitos.

Comprueba:

1. Consistencia entre los requisitos, el diseño técnico y las 51 tareas.
2. Trazabilidad de FR-001 a FR-019, NFR-001 a NFR-006 y escenarios T1–T7.
3. Cumplimiento de las prohibiciones académicas y del determinismo.
4. Dependencias correctamente asignadas a B, C y D, sin trasladar sus responsabilidades a A.
5. Posibles conflictos de propiedad de archivos, especialmente `juego.py`, `enemigos.py`, `tipos.py`, `snapshots.py`, `tests/` y `utilidades/`.
6. Que ninguna tarea bloqueada pueda ejecutarse como si su dependencia estuviera resuelta.
7. Que las alternativas experimentales no se confundan con obligaciones de implementación.
8. Que las pruebas y mediciones propuestas permitan comprobar los requisitos del profesor.
9. Que el registro de prompts esté preparado y no se haya perdido información obligatoria.
10. Cualquier contradicción, duplicación, tarea faltante o decisión técnica injustificada.

Q1, Q2 y Q3 siguen pendientes. El profesor todavía no ha respondido y no debes inventar respuestas ni marcar esos puntos como resueltos.

**Trabaja únicamente en modo lectura.**

No modifiques ningún archivo, no generes código, no ejecutes tareas de implementación, no hagas commits ni operaciones Git y no avances a Implement.

Devuelve un informe de hallazgos clasificados por gravedad, indicando los archivos y tareas afectados, qué debemos corregir y qué podemos mantener pendiente hasta recibir las aclaraciones oficiales.
```

## P18 — corrección de los seis hallazgos

```text
Quiero corregir los seis hallazgos I1, C1, I2, I3, I4 y D1 detectados por `$speckit-analyze` para `001-terreno-cazador`.

Autoriza únicamente modificaciones documentales dentro de `specs/001-terreno-cazador/`.

1. I1: separa las dependencias de T003 por entregables verificables de B, C y D. Cada tarea debe depender solamente de los acuerdos que realmente necesita. No des por aprobados contratos pendientes.
2. C1: prepara un registro local de todos los prompts de mi funcionalidad, incluidos Clarify y las correcciones documentales. Conserva fecha, herramienta, texto íntegro y finalidad. Recupera únicamente textos disponibles y verificables del historial; no reconstruyas ni inventes mensajes faltantes. Identifica explícitamente cualquier registro incompleto. No modifiques todavía PROMPTS_LLM.md.
3. I2: distingue autorización para actualizar documentación de autorización para implementar código y ejecutar pruebas. No elimines los controles de seguridad existentes.
4. I3: aclara criterios de finalización de T047–T050. Una preparación provisional no debe marcarse como cierre definitivo sin la evidencia correspondiente.
5. I4: distingue la reserva inicial O(V) de los costos totales de ordenamiento y resolución de conexiones documentados en research.md.
6. D1: actualiza las referencias de estado que hayan quedado desactualizadas en checklist, spec, plan o quickstart. Conserva Q1–Q3 pendientes y no borres información histórica necesaria.

**Restricciones:**

- No modificar código Python, constitución, archivos de compañeros, interfaz ni recursos visuales.
- No modificar archivos compartidos.
- Mantener `feature/motor-eventos`.
- No realizar operaciones Git.
- No ejecutar Tasks, Analyze ni Implement.
- No marcar ninguna tarea de implementación como completada.
- Si no puedes recuperar íntegramente algún prompt, informa cuál falta en lugar de inventarlo.

Al finalizar, indica los archivos modificados, los hallazgos corregidos y los pendientes que permanezcan.
```

## Comprobaciones para traslado posterior

Mantener esta lista abierta a nuevos mensajes, sin borrar entradas históricas. Antes del traslado: verificar acceso a los tres registros enlazados, incluir sus textos, no sustituir por resúmenes; conservar las etiquetas de fecha contextual; recuperar de fuente auténtica cualquier mensaje adicional que se detecte faltante; y solicitar autorización antes de modificar el archivo compartido. Declarar los vacíos restantes en el traslado, sin afirmar completitud fuera del historial disponible. Este documento no marca T051 ni ninguna tarea como completada.

## Ampliación posterior: P19 y P20

**Fecha contextual:** 2026-11-05, America/Costa_Rica; sin timestamps individuales. **Herramienta:** aplicación Codex, modelo exacto no confirmado. Las 18 entradas anteriores y sus textos se conservan; el índice ahora contiene 20 solicitudes. La nota inicial de ausencia de respuestas describe el estado de aquella consolidación: P20 aporta comunicación parcial de B transmitida por el usuario, sin mensaje original de B ni copia verificable de OpenAPI 1.1.0. La respuesta del profesor a Q1/Q2 y la evidencia Q3 siguen ausentes. No se certifica completitud fuera del historial visible ni de anexos históricos; no se incorpora el cuerpo de la habilidad adjunta como si fuera texto propio del usuario.

## P19 — segunda revisión Analyze

**Finalidad/uso:** revisar las correcciones anteriores en lectura; el informe identificó I1 residual, I5 y C2 y motivó P20. No autorizó implementación ni edición.

```text
$speckit-analyze

Realiza una segunda revisión de consistencia de la funcionalidad `001-terreno-cazador`, correspondiente a la Persona A.

La primera revisión encontró I1, C1, I2, I3, I4 y D1. Se aplicaron correcciones documentales, pero todavía no han sido verificadas mediante un nuevo Analyze.

Lee la constitución vigente, spec.md, plan.md, research.md, data-model.md, contracts/integracion.md, quickstart.md, tasks.md, checklists/requirements.md y prompts-registro-local.md.

Verifica especialmente:

1. Que I1, C1, I2, I3, I4 y D1 estén corregidos y que las correcciones no hayan introducido nuevas contradicciones.
2. Que cada consumidor de T003 dependa exclusivamente de las entregas externas que necesita.
3. Que las 51 tareas mantengan sus identificadores, dependencias válidas y trazabilidad FR/NFR.
4. Que el registro de 18 solicitudes conserve los textos efectivamente disponibles, identifique cualquier ausencia y no afirme estar completo sin evidencia.
5. Que se distinga claramente la autorización documental de la autorización de implementación, pruebas y mediciones.
6. Que las tareas de cierre no puedan marcarse completas con resultados provisionales.
7. Que Q1, Q2 y Q3 continúen pendientes donde corresponda, incorporando sin contradicciones la evidencia parcial recibida de B sobre OpenAPI 1.1.0.
8. Que se mantengan protegidos los módulos de B, C y D y que los experimentos no se conviertan automáticamente en código de producción.
9. Que no existan nuevas inconsistencias de formato, enlaces, marcadores o estados del checklist.

Trabaja exclusivamente en modo lectura.

No modifiques archivos, no ejecutes tareas, código ni pruebas, no realices operaciones Git y no avances a Implement.

Devuelve un informe con hallazgos clasificados por gravedad, indicando si la documentación está preparada para la siguiente etapa o qué correcciones siguen siendo necesarias.
```

## P20 — corrección I1/I5/C2 y comunicación reportada de B

**Finalidad/uso:** ajustar exclusivamente documentos de esta funcionalidad, conservar T001–T051 sin completar, y distinguir reglas del enunciado de evidencia indirecta de B y políticas pendientes. No se ejecutan habilidades ni pruebas y no se modifica PROMPTS_LLM.md.

```text
Quiero corregir los tres hallazgos restantes de la segunda revisión Analyze de `001-terreno-cazador`.

El profesor todavía no ha respondido a las consultas sobre Q1 y Q2. No debemos inventar sus respuestas ni seguir bloqueando las correcciones documentales por esa espera.

Autoriza únicamente modificaciones documentales dentro de `specs/001-terreno-cazador/`.

**I1 — Separar costos y rango**

Divide E-B-DATOS en dos entregables verificables e independientes:

- E-B-COSTOS: suministro y acceso a los costos de las salidas, versiones y datos válidos para el motor.
- E-B-RANGO: suministro y acceso al rango de los cazadores, versiones y datos válidos.

Actualiza las dependencias de las 51 tareas para que cada una espere únicamente el entregable necesario.

T013 y T014 deben depender de E-B-COSTOS, no de E-B-RANGO.

No marques ninguno como entregado sin evidencia y no consideres Q1/Q2 resueltas.

**I5 — Corregir dependencias de T027**

Agrega T024 como prerrequisito de la finalización completa de T027, porque T027 incluye la ejecución de `test_contrato_rutas_c.py`.

Distingue ejecución parcial de las pruebas de cazador de la finalización total de T027.

Conserva los identificadores T001–T051, sin crear ciclos.

**C2 — Incorporar evidencia reportada por B**

Registra como comunicación del compañero B, no como verificación independiente, la siguiente información de su revisión del OpenAPI oficial versión 1.1.0:

Esquema Enemy:

- `rango` es opcional y admite null.
- Cuando tiene valor, debe ser entero >= 1.
- No hay valor predeterminado declarado.
- No existe obligatoriedad adicional para comportamiento cazador.

Esquema Exit:

- Las salidas se describen como dirigidas.
- `costo` es opcional y admite null.
- Cuando tiene valor, debe ser entero >= 1.
- No se declara valor predeterminado ni garantía de simetría.

Esta información fue comunicada por B, pero no disponemos todavía de una copia verificable del documento OpenAPI ni de sus fragmentos originales. Indica explícitamente esa limitación.

Contrasta esta comunicación con Cripta Parte II §3.1 y §3.2:

- Costo ausente = 100.
- El costo es igual en ambos sentidos.
- La ficha del cazador incluye rango.

No sustituyas las reglas del enunciado por suposiciones sobre OpenAPI.

Conserva pendientes la política para rango ausente/null, costo null y datos inconsistentes.

Q3 también permanece pendiente.

**Restricciones**

- No modificar código, constitución ni archivos de B, C o D.
- No modificar PROMPTS_LLM.md.
- No ejecutar pruebas, benchmarks ni operaciones Git.
- No ejecutar Tasks, Analyze ni Implement.
- Conservar la rama feature/motor-eventos.
- No marcar tareas como completadas.

Al finalizar, informa los archivos modificados, los entregables nuevos, las dependencias corregidas y los bloqueos restantes.
```

## P21 — implementación limitada de fundamentos

**Fecha contextual:** 2026-11-05, America/Costa_Rica; sin timestamp individual. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Uso de la respuesta:** revisar constitución, documentos y permisos; implementar solo T005–T010 en el módulo aislado de rutas y pruebas nuevas; registrar 13 pruebas aprobadas y conservar Q1–Q3/entregas externas pendientes. La documentación compartida no se modifica; traslado posterior sigue pendiente de autorización. El índice se amplía a 21 entradas; no certifica totalidad de todas las interacciones: las solicitudes intermedias de diagnóstico Git, preparación/autorización del commit y diagnóstico de dependencias de B no se consolidan aquí en esta etapa limitada, y quedan pendientes de registro posterior. La habilidad adjunta speckit-implement es contexto instalado; no sustituye el texto propio siguiente ni amplía su alcance.

```text
$speckit-implement

Vamos a iniciar de forma controlada la implementación de `001-terreno-cazador`, correspondiente a la Persona A de Cripta Parte II.

Estamos en la rama `feature/motor-eventos`. La documentación provisional está protegida en el commit local `4ee04ff`.

Antes de modificar código:

1. Lee la constitución vigente y todos los documentos de `specs/001-terreno-cazador/`, especialmente `spec.md`, `plan.md`, `tasks.md` y `contracts/integracion.md`.
2. Revisa las correcciones más recientes de Analyze y confirma que los hallazgos I1, I5 y C2 estén reflejados correctamente.
3. Comprueba el estado de Git y que no existan cambios seguidos pendientes.
4. Identifica las tareas de fundamentos que puedan ejecutarse usando exclusivamente datos válidos, sin depender de Q1–Q3 ni de entregas externas.
5. Comprueba que las rutas y archivos que necesitarías modificar no pertenezcan a B, C o D.

**Alcance autorizado para esta primera implementación:**

- Únicamente las tareas T005–T010 de preparación y fundamentos, en el orden permitido por sus dependencias.
- Implementar estructuras de datos propias para índices, adyacencias y heap de rutas conforme al Plan.
- Crear las pruebas correspondientes y ejecutarlas.
- Utilizar exclusivamente grafos sintéticos con costos positivos, simétricos y datos válidos.
- Respetar las restricciones académicas: no utilizar dict, set, heapq, bisect, collections ni bibliotecas de grafos como sustitutos de estructuras propias.
- Mantener intacto el comportamiento existente del juego.

**Restricciones:**

- No implementar todavía T011–T051, terreno integrado, cazador conectado al motor, invalidación, historia ni interfaz visual.
- No modificar archivos de B, C o D, incluidos red/, datos/, modelo/enemigos.py, modelo/tipos.py, modelo/snapshots.py, vista/, main.py y bench.py.
- No modificar modelo/juego.py, modelo/eventos.py ni modelo/efectos.py en esta primera etapa.
- No integrar ramas de compañeros.
- No inventar políticas para rango ausente/null, costo null ni datos inconsistentes.
- No modificar constitución ni documentación compartida.
- No ejecutar operaciones Git de integración, commit o push.

Si alguna tarea requiere modificar archivos fuera de `modelo/rutas.py`, las pruebas nuevas de fundamentos o la documentación propia de A, detente y solicita autorización antes de escribirlos. Si una tarea depende de un acuerdo todavía pendiente, no la ejecutes.

**Al finalizar:**

- Indica exactamente qué tareas implementaste y cuáles siguen bloqueadas.
- Enumera archivos creados/modificados.
- Presenta resultados reales de las pruebas.
- Informa si se respetaron todas las restricciones.
- No avances automáticamente a US1, US2 ni otras fases.

No marques tareas como completadas sin pruebas o evidencia verificable.
```

## P22 — pruebas T011/T012 sin modificar el motor

**Fecha contextual:** 2026-11-05, America/Costa_Rica; hora individual y modelo exacto no confirmados. **Herramienta:** aplicación Codex. **Uso de la respuesta:** crear las dos suites, ampliar fixtures propios reutilizando ServidorFalso existente y componentes reales, ejecutar cuatro suites autorizadas y registrar 22 aprobadas/10 fallos pendientes de integración, sin completar T011/T012 ni modificar motor o estructuras anteriores. El registro se amplía a 22 entradas; conserva los límites y omisiones intermedias declarados en P21. Traslado a PROMPTS_LLM.md pendiente de autorización. La habilidad adjunta corresponde a speckit-implement instalado, sin ampliar el alcance del mensaje.

```text
$speckit-implement

Continúa la implementación de `001-terreno-cazador`, Persona A, exclusivamente con las tareas T011 y T012 de US1 (terreno y tiempos).

Las tareas T005–T010 están implementadas y cuentan con 13 pruebas aprobadas. Sus cambios locales todavía no tienen commit.

Antes de empezar, revisa el estado de Git, la constitución, spec.md, plan.md y tasks.md, y comprueba que las dependencias de T011 y T012 están satisfechas.

**Alcance autorizado:**

1. Crear `tests/test_costos_terreno.py` para T011, verificando con datos válidos el costo de movimiento, los intervalos, el mínimo de 1 y la conservación de los demás costos de acciones.
2. Crear `tests/test_velocidad_terreno.py` para T012, verificando cambios de velocidad a mitad del intervalo, cancelación/reprogramación y secuencia nueva según Parte I.
3. Utilizar fixtures existentes o ampliar exclusivamente `tests/datos_terreno_cazador.py` si es necesario.
4. Ejecutar las dos nuevas suites y las pruebas de fundamentos previamente aprobadas.
5. Distinguir los fallos esperados porque el motor todavía no integra costos variables de los defectos reales de las estructuras ya implementadas.

**Restricciones:**

- No modificar todavía `modelo/juego.py`, `modelo/eventos.py` ni `modelo/efectos.py`.
- No modificar archivos de B, C o D, interfaz gráfica ni recursos visuales.
- No implementar T013 ni ninguna tarea posterior.
- No inventar políticas para valores null, rangos ausentes o costos inconsistentes.
- No ejecutar merge, pull, fetch, push, commit, reset, clean ni stash.
- No modificar documentación compartida.

Puedes actualizar únicamente los documentos de Persona A necesarios para registrar los resultados reales y las tareas ejecutadas.

No marques T011 o T012 como completadas si sus criterios todavía fallan porque requieren código de T013–T015. En ese caso, informa qué pruebas están listas y qué implementación falta.

Al finalizar, muestra los archivos modificados y los resultados de las pruebas, distinguiendo las que pasaron de las que quedaron pendientes.
```

## P23 — corrección de pruebas y fixtures tras auditoría

**Fecha contextual:** 2026-11-05, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex. **Uso de la respuesta:** consultar enunciados y corregir exclusivamente los fixtures/pruebas T011/T012: reciprocidad con acciones completas, enemigos despachados por agenda, preparación de datos antes del motor y separación cola/ataque único. Resultado real final: 35 pruebas, 25 aprobadas, 10 fallos pendientes de costos y cero errores; sin completar T011/T012 ni modificar código de producción. El índice se amplía a 23 entradas inventariadas, conservando límites anteriores; la solicitud de auditoría de lectura inmediatamente anterior está disponible en el chat pero su transcripción queda pendiente de consolidación posterior, junto con las omisiones intermedias declaradas en P21. No se presenta esta entrada como prueba de completitud. PROMPTS_LLM.md permanece intacto.

```text
Quiero corregir los tres defectos confirmados por la auditoría de las pruebas T011 y T012 de `001-terreno-cazador`.

Antes de modificar archivos, revisa las reglas oficiales de Cripta Parte I y II, la constitución, `spec.md`, `plan.md`, `tasks.md`, las pruebas actuales y los métodos correspondientes del motor.

**Alcance autorizado: corregir exclusivamente las pruebas y los fixtures de T011/T012.**

1. Corregir la prueba de movimiento recíproco para que respete las decisiones y el reloj virtual del jugador. Utiliza `motor.ejecutar()` si su contrato permite representar correctamente ambos movimientos, o dos fixtures independientes preparados coherentemente. No fuerces eventos ni omitas el tiempo para hacer pasar las pruebas.
2. Corregir las pruebas de enemigos para que no presenten como turnos normales acciones ejecutadas antes de su evento programado. Preparar su comportamiento, posición y velocidad de forma coherente con la agenda. Distinguir claramente una prueba unitaria artificial de una integración real.
3. Separar los criterios de descarte de eventos cancelados de la verificación de una única ejecución semántica. Conservar las pruebas de cola como pruebas de cola. Para demostrar ejecución única, utilizar el motor y comprobar las acciones realmente procesadas. Si ello requiere una tarea posterior o integración aún no autorizada, documentar esa limitación sin fingir cobertura.
4. Revisar que los fixtures no dejen inconsistencias entre `_puertas_iniciales` y puertas actuales cuando la prueba pretenda verificar restauración. No agregar pruebas de restauración fuera del alcance.
5. Conservar los casos de costo 250, costo 1, intervalo mínimo 1, costo ausente 100 y T7.
6. No alterar resultados esperados para que coincidan con el comportamiento incorrecto del motor actual.

**Archivos autorizados:**

- `tests/test_costos_terreno.py`
- `tests/test_velocidad_terreno.py`
- `tests/datos_terreno_cazador.py`
- Documentación propia de A estrictamente necesaria para registrar la corrección y resultados.

**Restricciones:**

- No modificar `modelo/juego.py`, `modelo/eventos.py`, `modelo/efectos.py` ni `modelo/rutas.py`.
- No modificar código de B, C o D, interfaz, constitución ni documentación compartida.
- No implementar T013 ni tareas posteriores.
- No introducir nuevos mocks o bibliotecas prohibidas.
- No inventar políticas para Q1/Q2 ni afirmar cumplimiento de Q3.
- No hacer commits, push, pull, fetch, merge, rebase, reset ni clean.

Ejecuta las suites T011/T012 y fundamentos después de los cambios. Registra los resultados reales, incluidos los fallos que permanezcan porque todavía falta integrar costos variables.

No marques T011/T012 como completas mientras sus criterios no se cumplan.

Al finalizar, explica exactamente qué defectos corregiste, qué pruebas siguen fallando y qué evidencia demuestra ahora cada suite.
```

## P24 — implementación controlada de T013

**Fecha contextual:** 2026-11-05, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** texto íntegro de la solicitud actual disponible en el chat. **Finalidad y uso de la respuesta:** implementar exclusivamente costo de movimiento del jugador en Motor.mover con entradas válidas, reutilizando fórmula y agenda; ejecutar suites existentes y registrar evidencia. Resultado: 31/35 aprobadas, cuatro fallos de movimiento enemigo pendientes de T014, y 53/53 regresiones aprobadas antes y después. T013 implementada para datos válidos, con cierre integrado pendiente E-B-COSTOS. No se resuelven Q1–Q3, no se modifica PROMPTS_LLM.md ni se ejecuta T014. El inventario se amplía a 24 entradas, conservando las ausencias y límites de completitud ya declarados; no acredita un historial global completo.

```text
$speckit-implement

Continúa la implementación de `001-terreno-cazador`, Persona A, únicamente con T013: costo variable del movimiento del jugador.

Las pruebas T011/T012 fueron corregidas y la última ejecución reportó 25 aprobadas y 10 fallos relacionados con el costo fijo del movimiento. T005–T010 ya tienen sus pruebas aprobadas.

Antes de modificar código, revisa:

- Constitución vigente y enunciados oficiales de Cripta Parte I y II.
- `spec.md`, `plan.md`, `tasks.md` y `contracts/integracion.md`.
- `modelo/juego.py`, especialmente `mover()`, `_avanzar_actor()` y `calcular_intervalo()`.
- Las pruebas T011/T012 y los fixtures existentes.

**Autorización específica:**

1. Implementa exclusivamente T013 en la lógica de movimiento del jugador de `modelo/juego.py`.
2. Obtén el costo de la salida real utilizada por el jugador, antes de modificar su posición.
3. Para entradas válidas, utiliza costo declarado entero ≥1 o costo 100 si el campo está ausente, conforme a Parte II §3.1.
4. Conserva la fórmula oficial `max(1, costo_salida * 100 // velocidad)`.
5. Mantén el comportamiento existente de activación, efectos, puertas, agenda, rastro, azar y demás acciones.
6. No modifiques la fórmula de reprogramación de velocidad que ya pasó las pruebas aisladas.
7. Ejecuta las suites T011/T012 y fundamentos, identificando qué fallos corresponden todavía a T014, que no está autorizada.
8. Ejecuta las regresiones existentes pertinentes al movimiento del jugador si pueden ejecutarse sin modificar dependencias ni archivos ajenos.

**Restricciones estrictas:**

- No implementar T014 ni otras tareas posteriores.
- No modificar la lógica de movimiento de enemigos.
- No modificar `modelo/rutas.py`, `modelo/eventos.py`, `modelo/efectos.py` ni archivos de B, C o D.
- No tocar interfaz visual, historial ni persistencia.
- No inventar comportamiento para costo null, rango ausente o costos inconsistentes.
- No introducir estructuras o bibliotecas prohibidas.
- No cambiar pruebas esperadas para ocultar fallos.
- No ejecutar commits, push, pull, fetch, merge, rebase, reset ni clean.

Si T013 necesita cambios fuera de la rama específica de movimiento del jugador, explica por qué y solicita autorización antes de realizarlos.

Actualiza únicamente la documentación de Persona A necesaria para registrar los resultados.

Al finalizar, informa:

- Qué líneas o funciones cambiaste.
- Cuáles pruebas aprobaron y cuáles fallaron.
- Qué requisitos oficiales respaldan el cambio.
- Si se conservaron las regresiones.
- Si T013 puede marcarse completada con evidencia suficiente.

No avances automáticamente a T014.
```

## P25 — implementación controlada de T014

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** texto íntegro de la solicitud actual disponible en el chat; las instrucciones de la habilidad fueron aportadas a continuación por el usuario como contexto operativo, no como un nuevo requisito funcional. **Finalidad y uso de la respuesta:** integrar exclusivamente el costo del movimiento de enemigos existentes en la rama mover de Motor._ejecutar_turno_enemigo, usando salida de origen y datos válidos. Resultado: cuatro suites 35/35 y regresiones seleccionadas 53/53 aprobadas, cero fallos/errores; activación inicial 100 conservada. T014 implementada/verificada localmente, sin acreditar E-B-COSTOS ni resolver Q1–Q3. No se modifica PROMPTS_LLM.md ni se ejecuta T015. El inventario aumenta a 25 entradas, con las ausencias y límites de completitud previamente declarados; no afirma recuperación de textos faltantes ni completitud global.

```text
$speckit-implement

Continúa la funcionalidad `001-terreno-cazador` de la Persona A, exclusivamente con T014: integrar el costo variable del movimiento de enemigos existentes.

Estado confirmado:

- T005–T010: fundamentos implementados; 13 pruebas aprobadas.
- T011: 9/13 pruebas aprobadas.
- T012: 9/9 pruebas aprobadas, sin acreditar todavía T7 integral.
- T013: movimiento del jugador implementado y verificado con datos válidos.
- Regresiones existentes: 53 aprobadas antes y después de T013.
- Quedan cuatro fallos asociados al movimiento de errantes y rastreadores.

Antes de modificar código, revisa los enunciados oficiales de Cripta Parte I y II, constitución, spec.md, plan.md, tasks.md, las pruebas actuales y la implementación existente de `modelo/juego.py`.

**Alcance autorizado:**

1. Implementar únicamente T014 en la rama de movimiento de `_ejecutar_turno_enemigo()` dentro de `modelo/juego.py`.
2. Obtener el costo desde la salida real de la sala de origen antes de cambiar la posición del enemigo.
3. Para datos válidos, utilizar costo declarado entero ≥1 o costo 100 si está ausente, según Parte II §3.1.
4. Pasar ese costo a `_avanzar_actor()`, conservando la fórmula existente.
5. Mantener intacta la decisión de movimiento de errantes y rastreadores, así como la activación inicial con costo 100, ataques, esperas, efectos, agenda, rastro, puertas y azar.
6. No alterar `modelo/enemigos.py`, sus interfaces ni la lógica del cazador.
7. Verificar que los cuatro fallos pendientes de T014 desaparezcan sin modificar los resultados esperados de las pruebas.
8. Ejecutar nuevamente las cuatro suites de terreno, velocidad y fundamentos, además de las 53 regresiones previamente seleccionadas.
9. Revisar cualquier nueva regresión antes de dar por correcta la tarea. No modificar otras funcionalidades para ocultar fallos.

**Restricciones:**

- Solo se autoriza modificar la rama específica de movimiento enemigo en `modelo/juego.py` y la documentación propia de A necesaria para registrar evidencias.
- No modificar pruebas, fixtures, modelo/rutas.py, eventos.py, efectos.py, tipos.py, enemigos.py ni componentes de B, C o D.
- No implementar T015 ni tareas posteriores.
- No modificar la interfaz visual, historial o persistencia.
- No inventar políticas para costo null, rango ausente o datos inconsistentes.
- No ejecutar operaciones Git de escritura, integración o publicación.
- No afirmar cumplimiento de rendimiento sin mediciones.

Si se necesita modificar otro archivo o cambiar un contrato existente, detente y solicita autorización.

Al finalizar, informa los cambios exactos realizados, pruebas aprobadas/fallidas, regresiones, evidencia de conservación del costo de activación y cualquier condición pendiente.

No avances automáticamente a la siguiente tarea.
```

## P26 — verificación de T015 y revisión del diff T013/T014

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra disponible en el chat; instrucciones de la habilidad aportadas a continuación como contexto operativo. **Finalidad y uso de la respuesta:** revisar todas las líneas eliminadas/agregadas de T013/T014, verificar reprogramación existente y distinguir T7 parcial de integral. Resultado: velocidad 9/9 y regresiones 53/53, cero fallos/errores, sin defecto observado que exija modificar producción; documentación de evidencia y cobertura pendiente. T015 verificada en alcance probado, sin cierre global ni ejecución de T016. No cambia PROMPTS_LLM.md. Inventario de 26 entradas, con ausencias y límites de completitud previos conservados; no se reconstruyen mensajes faltantes ni se afirma completitud global.

```text
$speckit-implement

Continuemos con `001-terreno-cazador`, Persona A, exclusivamente con la verificación de T015.

T013 y T014 ya están implementadas para datos válidos. Las últimas ejecuciones reportaron 35/35 pruebas de terreno, velocidad y fundamentos y 53/53 regresiones aprobadas.

ANTES DE MODIFICAR CÓDIGO:

1. Revisa el diff completo de modelo/juego.py correspondiente a T013 y T014, incluyendo todas las líneas eliminadas (rojas) y agregadas (verdes).
2. Comprueba que solo se reemplazó el costo fijo por el costo de salida en el movimiento del jugador y enemigos.
3. Confirma que no se eliminaron reglas de activación, ataques, esperas, puertas, rastro, eventos, azar ni efectos.
4. Revisa los enunciados oficiales de Parte I y II, constitución, spec.md, plan.md y tasks.md.
5. Examina cambiar_velocidad(), \_avanzar_actor() y las pruebas de T7.

ALCANCE AUTORIZADO:

- Verificar T015 con el código actual.
- Ejecutar pruebas de reprogramación con aceleración, ralentización, intervalo mínimo y finalización del efecto.
- Comprobar cancelación del evento anterior, nueva secuencia y ausencia de acciones duplicadas.
- Ejecutar las regresiones pertinentes.
- Revisar qué falta para acreditar el escenario T7 completo.

RESTRICCIONES:

- Si la fórmula y la implementación existentes son correctas, NO modificar código de producción.
- Si encontrás un defecto real, documentá el caso, la evidencia y el cambio mínimo propuesto, pero pedí mi autorización antes de modificarlo.
- No modificar pruebas para ocultar fallos.
- No tocar B, C, D, interfaz, historial, persistencia ni archivos compartidos.
- No ejecutar T016 ni tareas posteriores.
- No inventar políticas para Q1–Q3.
- No hacer commits, push, pull, fetch, merge, rebase, reset ni clean.

Podés actualizar únicamente la documentación propia de A para registrar resultados verificados.

Al finalizar, presentá el diff revisado de T013/T014, las pruebas ejecutadas, sus resultados y si T015 requiere cambios reales o puede considerarse verificada dentro del alcance probado.

No avances automáticamente a otra tarea.
```

## P27 — cobertura integrada de T7 con eventos existentes

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra disponible en el chat; instrucciones de la habilidad aportadas como contexto operativo. **Finalidad y uso de la respuesta:** comprobar viabilidad y añadir tres cronologías integradas T7 con restaurar_velocidad de efectos iniciales coherentes, sin reloj manual ni acciones anticipadas. Resultado: velocidad 12/12, cuatro suites 38/38 y regresiones 53/53, cero fallos/errores; T012 completa en el alcance de datos válidos del jugador. No se implementa la cadena particular 250→150→225 ni un evento nuevo de aplicación diferida, no se modifica producción/fixture, no se ejecuta T016 ni se cierran Q1–Q3. PROMPTS_LLM.md permanece intacto. Inventario de 27 entradas, conservando ausencias y límites de completitud ya declarados; no se reconstruyen textos faltantes ni se afirma completitud global.

```text
$speckit-implement

Continúa con `001-terreno-cazador`, Persona A, exclusivamente para completar la cobertura de pruebas del escenario T7 de Cripta Parte II.

T013 y T014 están implementadas para entradas válidas. T015 fue verificada sin necesitar modificaciones de producción.

Antes de escribir, revisa la constitución, Parte I §2.3, Parte II §3.1 y Apéndice B, spec.md, plan.md, tasks.md, quickstart.md y los métodos reales del motor de eventos.

OBJETIVO:

Crear una prueba integrada de T7 que reproduzca una cronología completa, sin cambiar manualmente el reloj ni ejecutar acciones del jugador antes de su turno.

Debe comprobar, cuando el motor y sus eventos existentes lo permitan:

1. Movimiento real mediante salida de costo 250, velocidad 100, en t=0; siguiente turno previsto t=250.
2. Cambio de velocidad a 200 en t=50 por un evento procesado por el motor; nueva programación t=150.
3. Cancelación del evento anterior, nueva secuencia y una única acción semántica en el turno correspondiente.
4. Que el evento cancelado de t=250 no provoque una acción adicional.
5. Variantes de ralentización y terminación del efecto, conservando las fórmulas oficiales.

Primero comprueba si los tipos de eventos y mecanismos existentes permiten construir esos escenarios sin inventar una mecánica nueva.

Si alguna variante requiere introducir un tipo de evento nuevo, modificar reglas de producción o simular una acción ilegal, detente y explica el impedimento antes de modificarla.

ARCHIVOS AUTORIZADOS:

- tests/test_velocidad_terreno.py
- tests/datos_terreno_cazador.py, únicamente si se necesita ampliar el fixture válido.
- Documentación propia en specs/001-terreno-cazador/ para registrar resultados y límites.

RESTRICCIONES:

- No modificar modelo/juego.py, eventos.py, efectos.py, rutas.py ni otros archivos de producción.
- No alterar pruebas existentes para hacerlas pasar artificialmente.
- No introducir nuevos mocks de servicios o comportamientos inventados.
- No modificar archivos de B, C o D, interfaz, constitución o documentación compartida.
- No implementar T016 ni tareas posteriores.
- No ejecutar commits, push, pull, fetch, merge, reset ni rebase.
- No cerrar Q1–Q3 ni inventar contratos pendientes.

Ejecuta las pruebas autorizadas y las regresiones pertinentes.

Al finalizar, informa qué pruebas añadiste, qué eventos reales utilizaste, sus resultados, si T7 quedó íntegramente acreditado y cualquier cobertura todavía pendiente.

No avances automáticamente a otra tarea.
```

## P28 — verificación limitada de T016

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra disponible en el chat; instrucciones de la habilidad aportadas como contexto operativo. **Finalidad y uso de la respuesta:** reutilizar las pruebas de costos y añadir solo la cobertura faltante de ataques gratuitos/agenda/empates. Resultado: un nuevo método con dos subcasos, costos 14/14, velocidad 12/12, fundamentos 13/13 (39/39) y regresiones 53/53, cero fallos/errores. Sin cambios de producción/fixture ni expectativas existentes. T016 verificada localmente, casilla pendiente por cierre formal T014/T015; no se ejecuta T017 ni se cierran Q1–Q3. PROMPTS_LLM.md intacto. Inventario de 28 entradas, conservando ausencias y límites de completitud declarados previamente; no se reconstruyen mensajes ni se afirma completitud global.

```text
$speckit-implement

Continúa con `001-terreno-cazador`, Persona A, exclusivamente con T016 de US1.

Antes de modificar archivos, revisa la constitución, los enunciados oficiales de Parte I y II, spec.md, plan.md, tasks.md, el código actual y las pruebas existentes.

Objetivo: ampliar únicamente las pruebas necesarias para verificar que los costos de las acciones distintas de movimiento siguen siendo los oficiales y que mover conserva la posición inmediata sin provocar ataques gratuitos.

Comprueba:

- Atacar y esperar: costo 100.
- Usar, equipar y abrir: costo 50.
- Recoger y soltar: costo 25.
- Movimiento: costo real de salida y posición inmediata.
- Ausencia de ataques adicionales provocados por el movimiento.
- Conservación de la agenda y el orden de eventos en los escenarios probados.

Reutiliza los fixtures existentes y evita duplicar pruebas que ya acrediten exactamente el requisito. Si una comprobación necesita una situación adicional, justifica su necesidad y utiliza las reglas reales del motor.

Archivos autorizados:

- tests/test_costos_terreno.py
- tests/datos_terreno_cazador.py, únicamente si es indispensable.
- Documentos propios de specs/001-terreno-cazador/ para registrar evidencia.

Restricciones:

- No modificar código de producción.
- No alterar resultados esperados para ocultar fallos.
- No introducir mocks nuevos ni comportamientos inventados.
- No modificar archivos de B, C o D, interfaz o documentación compartida.
- No ejecutar T017 ni tareas posteriores.
- No realizar operaciones Git de escritura, integración o publicación.
- No cerrar Q1–Q3 ni asumir contratos externos pendientes.

Ejecuta las pruebas de costos, velocidad y fundamentos, además de las regresiones pertinentes.

Al finalizar, informa qué pruebas nuevas fueron necesarias, cuáles ya existían, los resultados reales y qué queda pendiente de US1. No marques T016 completada sin evidencia.
```

## P29 — verificación conjunta de US1, T017

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra actual del chat; instrucciones de la habilidad aportadas como contexto operativo. **Finalidad y uso de la respuesta:** corrida conjunta, revisión de diff/cobertura y separación de verificación local e integración de B. Resultado: 99/99 aprobadas (39 propias + 53 regresiones seleccionadas + 7 enemigos), cero fallos/errores/omisiones/fallos esperados, sin modificar Python. US1 funcionalmente verificada en escenarios válidos; T011 consolida cierre de pruebas, T013–T017 conservan condiciones formales de integración/prerrequisitos. No se ejecuta T018/US2 ni se resuelven Q1–Q3/E-B-COSTOS. PROMPTS_LLM.md intacto. Inventario de 29 entradas, con ausencias y límites de completitud anteriores preservados; no se reconstruyen textos faltantes ni se afirma completitud global.

```text
$speckit-implement

Continúa con `001-terreno-cazador`, Persona A, exclusivamente con T017: verificación conjunta de US1, terreno y tiempos.

Estado actual:

- T005–T010: fundamentos probados.
- T012: completada.
- T013/T014: movimiento ponderado implementado y verificado para datos válidos, pendiente de cierre integrado E-B-COSTOS.
- T015: reprogramación verificada sin cambios de producción, con cierre formal condicionado.
- T016: comprobaciones realizadas satisfactoriamente, con cierre formal pendiente.
- Última ejecución: 39/39 pruebas de terreno, velocidad y fundamentos, más 53/53 regresiones.

Antes de actuar, revisa la constitución, Parte I y II, spec.md, plan.md, tasks.md y quickstart.md.

**Objetivo exclusivo de T017:**

1. Ejecutar y verificar conjuntamente todas las suites de terreno, velocidad y fundamentos autorizadas.
2. Ejecutar las regresiones existentes pertinentes.
3. Confirmar la cobertura de T6 y T7, señalando las limitaciones que sigan presentes.
4. Verificar la conservación de costos de las demás acciones, activación inicial de enemigos, determinismo, secuencias y efectos.
5. Comprobar que las pruebas nuevas no oculten fallos mediante skips, expectedFailure o expectativas artificiales.
6. Revisar el diff completo de código de producción y confirmar que únicamente contiene los cambios autorizados en `Motor.mover()` y `_ejecutar_turno_enemigo()`.
7. Registrar resultados reales, requisitos cubiertos y limitaciones en la documentación propia de A.
8. Distinguir implementación local verificada de integración real con los datos de B.

**Restricciones:**

- Trabaja en modo de verificación, sin modificar código de producción ni pruebas.
- Si identificas un defecto, informa la evidencia y solicita autorización antes de corregirlo.
- No modificar archivos de B, C o D, interfaz ni recursos visuales.
- No ejecutar T018 ni tareas de US2.
- No marcar como resueltos Q1, Q2, Q3 o E-B-COSTOS.
- No realizar commits, push, pull, fetch, merge, rebase, reset ni clean.
- No modificar documentación compartida.

Puedes actualizar exclusivamente tasks.md, quickstart.md y prompts-registro-local.md de Persona A para registrar T017.

Al terminar, indica si US1 está funcionalmente verificada con datos válidos, cuáles tareas pueden cerrarse con evidencia y cuáles deben seguir condicionadas por contratos externos.

No avances automáticamente a US2.
```
