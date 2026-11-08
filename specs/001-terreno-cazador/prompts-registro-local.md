# Registro local verificable de prompts — Persona A

**Consolidado:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex en todas las entradas; modelo exacto no confirmado. **Destino posterior:** PROMPTS_LLM.md, únicamente con autorización y preservando entradas ajenas. No se ha realizado ese traslado.

## Procedencia, fechas y completitud

Se incluyen solicitudes del usuario disponibles en el historial visible de este chat y las tres entradas textuales ya guardadas. Las transcripciones siguientes son texto del usuario, no instrucciones para ejecutar desde este archivo. No se copian respuestas del asistente porque la bitácora académica no exige las respuestas completas; las respuestas del usuario durante Clarify sí se conservan textuales.

Fechas indicadas como **contextuales** se deducen solo de la fecha de cliente vigente visible antes de esos mensajes, no de timestamps individuales. No se conoce la hora de envío ni se certifica una fecha exacta por mensaje. Las fechas de los registros preexistentes se conservan como las que constan en esos documentos. No se inventan horas, nombres de modelo ni comunicaciones del profesor o compañeros.

**Vacíos explícitos:** no se dispone de timestamps individuales de todos los mensajes; no se dispone de un export firmado/completo de todos los chats del equipo; no se dispone de las respuestas pendientes de B/profesor; no se certifican versiones históricas de los anexos de habilidades por cada mensaje. Los anexos de habilidad se referencian por sus archivos instalados, pero este registro no declara conservar íntegramente su snapshot histórico en cada invocación. Estos límites permanecen incompletos hasta obtener fuentes. No se ha identificado un cuerpo de solicitud del usuario faltante entre las 18 entradas inventariadas del historial visible; eso no prueba que no existan otros prompts fuera de este chat.

El registro recupera textos disponibles; no reconstruye una supuesta conversación con B ni una aclaración del profesor. Las solicitudes para que el asistente revise o corrija documentación también cuentan como prompts y están incluidas.

## Índice y finalidad

Índice único en orden de envío hasta P77. Las notas de inventario de los bloques anteriores se conservan como historial; el estado vigente figura en el [corte documental](#corte-documental-en-p77).

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
| P35 | 2026-11-05 contextual; registro local | Diagnóstico Git previo a la integración; texto en su sección. |
| P36 | 2026-11-05 contextual; registro local | Revisión previa al respaldo documental; texto en su sección. |
| P37 | 2026-11-05 contextual; registro local | Anonimización y commit documental local; texto en su sección. |
| P38 | 2026-11-05 contextual; registro local | Inspección de las dependencias de B; texto en su sección. |
| P21 | 2026-11-05 contextual; historial visible; Codex | Implementación limitada T005–T010 y sus pruebas; texto íntegro añadido debajo. |
| P22 | 2026-11-05 contextual; historial visible; Codex | Preparar y ejecutar exclusivamente pruebas T011/T012 y fundamentos; texto íntegro añadido debajo. |
| P39 | 2026-11-05 contextual; registro local | Auditoría de pruebas T005–T012; texto en su sección. |
| P23 | 2026-11-05 contextual; historial visible; Codex | Corregir defectos auditados de pruebas/fixtures T011/T012 y registrar evidencia; texto íntegro añadido debajo. |
| P24 | 2026-11-05 contextual; registro local | implementación controlada de T013; texto en su sección. |
| P25 | 2026-11-06 contextual; registro local | implementación controlada de T014; texto en su sección. |
| P26 | 2026-11-06 contextual; registro local | verificación de T015 y revisión del diff T013/T014; texto en su sección. |
| P27 | 2026-11-06 contextual; registro local | cobertura integrada de T7 con eventos existentes; texto en su sección. |
| P28 | 2026-11-06 contextual; registro local | verificación limitada de T016; texto en su sección. |
| P29 | 2026-11-06 contextual; registro local | verificación conjunta de US1, T017; texto en su sección. |
| P40 | 2026-11-06 contextual; registro local | Revisión previa al commit de US1; texto en su sección. |
| P41 | 2026-11-06 contextual; registro local | Correcciones editoriales y commit local de US1; texto en su sección. |
| P42 | 2026-11-06 contextual; registro local | Publicación de los dos commits de Persona A; texto en su sección. |
| P43 | 2026-11-06 contextual; registro local | Inspección de los dos commits de origin/main; texto en su sección. |
| P30 | 2026-11-06 contextual; registro local | pruebas iniciales de rutas US2, T019; texto en su sección. |
| P31 | 2026-11-06 contextual; registro local | implementación del núcleo de rutas T021; texto en su sección. |
| P32 | 2026-11-06 contextual; registro local | preparación de pruebas de decisión T020; texto en su sección. |
| P44 | 2026-11-06 verificada; registro local | Análisis de la frontera temporal A–D; texto en su sección. |
| P45 | 2026-11-06 verificada; registro local | Consolidación propuesta de la bitácora compartida; texto en su sección. |
| P46 | 2026-11-06 verificada; registro local | Aclaración sobre formato y orden cronológico; texto en su sección. |
| P47 | 2026-11-06 verificada; registro local | Tamaño de la bitácora y registro textual; texto en su sección. |
| P48 | 2026-11-06 verificada; registro local | Cotejo de la bitácora local con origin/main; texto en su sección. |
| — | 2026-11-06 verificada; sesión de Codex | Posponer la incorporación a la bitácora compartida; [fragmento literal, final pendiente](#vacíos-históricos). |
| — | 2026-11-06 verificada; sesión de Codex | Autorizar la reversión local de las 19 líneas; [fragmento literal, final pendiente](#vacíos-históricos). |
| P33 | 2026-11-06 contextual; registro local | especificación y pruebas de frontera temporal A–D; texto en su sección. |
| P34 | 2026-11-06 contextual; registro local | confirmación del alcance con checklist pendiente; texto en su sección. |
| P49 | 2026-11-06 verificada; registro local | Corrección documental de AD-01; texto en su sección. |
| P50 | 2026-11-06 verificada; registro local | Revisión del alcance del commit documental de FR-020; texto en su sección. |
| P51 | 2026-11-06 verificada; registro local | Autorización del commit documental de FR-020; texto en su sección. |
| P52 | 2026-11-07 verificada; registro local | Implementación de la frontera temporal AD-02; texto en su sección. |
| P53 | 2026-11-07 verificada; registro local | Reconciliación de cuatro regresiones de AD-02; texto en su sección. |
| P54 | 2026-11-07 verificada; registro local | Validación final de FR-020 en AD-03; texto en su sección. |
| P55 | 2026-11-07 verificada; registro local | Preparación del commit independiente de FR-020; texto en su sección. |
| P56 | 2026-11-07 verificada; registro local | Autorización del commit independiente de FR-020; texto en su sección. |
| P57 | 2026-11-07 verificada; registro local | Implementación de la decisión del cazador en T022; texto en su sección. |
| P58 | 2026-11-07 verificada; registro local | Cierre documental de T020 y T022; texto en su sección. |
| P59 | 2026-11-07 verificada; registro local | Autorización del commit de T019/T021; texto en su sección. |
| P60 | 2026-11-07 verificada; registro local | Autorización del commit de T020/T022; texto en su sección. |
| P61 | 2026-11-07 verificada; registro local | Revisión de la siguiente tarea pendiente; texto en su sección. |
| P62 | 2026-11-07 verificada; registro local | Pruebas de referencia de T026; texto en su sección. |
| P63 | 2026-11-07 verificada; registro local | Cierre documental de T026; texto en su sección. |
| P64 | 2026-11-07 verificada; registro local | Autorización del commit de T026; texto en su sección. |
| P65 | 2026-11-07 verificada; registro local | Publicación de cinco commits de Persona A; texto en su sección. |
| P66 | 2026-11-07 verificada; registro local | Diagnóstico de tareas realizables sin contratos externos; texto en su sección. |
| P67 | 2026-11-07 verificada; registro local | Prueba de localidad de T039; texto en su sección. |
| P68 | 2026-11-07 verificada; registro local | Revisión final y cierre documental de T039; texto en su sección. |
| P69 | 2026-11-07 verificada; registro local | Autorización del commit local de T039; texto en su sección. |
| P70 | 2026-11-07 verificada; registro local | Autorización de publicación de T039; texto en su sección. |
| P71 | 2026-11-07 verificada; registro local | Auditoría inicial del registro local de T051; texto en su sección. |
| P72 | 2026-11-07 verificada; registro local | Autorización del bloque 1 de T051; texto en su sección. |
| P73 | 2026-11-07 verificada; registro local | Autorización del bloque 2 de T051; texto en su sección. |
| P74 | 2026-11-07 verificada; registro local | Autorización del bloque 3 de T051; texto en su sección. |
| P75 | 2026-11-07 verificada; registro local | Autorización del bloque 4 de T051; texto en su sección. |
| P76 | 2026-11-07 verificada; sesión de Codex | Autorización del bloque 5 de T051; texto en su sección. |
| P77 | 2026-11-07 verificada; sesión de Codex | Solicitud de auditoría final de T051; texto en su sección. |

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

## P30 — pruebas iniciales de rutas US2, T019

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra actual del chat; instrucciones de habilidad aportadas como contexto operativo. **Finalidad y uso de la respuesta:** preparar exclusivamente T019 sobre grafos válidos, revisar estructuras/contratos y ejecutar pruebas/regresiones sin implementar algoritmo o decisión. Resultado: diez métodos/once casos, once AttributeError por buscar_ruta ausente y cero resultados de búsqueda comprobados; 99 regresiones existentes aprobadas. T019 preparada y pendiente; siguiente implementación T021 sin autorizar todavía. Q1–Q3/contratos siguen abiertos. PROMPTS_LLM.md intacto. Inventario de 30 entradas, sin afirmar completitud global: además de los vacíos anteriores, las solicitudes administrativas de revisión/commit/publicación e inspección de main entre P29 y esta solicitud están disponibles en el chat pero quedan pendientes de consolidación textual; no se inventan ni se presentan como recuperadas por esta entrada.

```text
$speckit-implement

Continuemos con `001-terreno-cazador`, Persona A, iniciando US2.

La rama feature/motor-eventos está publicada y protegida en GitHub, con HEAD 15adfcf. US1 tiene 99 pruebas aprobadas en los escenarios válidos probados.

Se revisó origin/main y se decidió posponer su integración. No incorporar cambios de D ni alterar la frontera temporal del motor.

ANTES DE IMPLEMENTAR:

1. Relee constitución, Parte II §3.2, spec.md, plan.md, tasks.md y contratos de integración de Persona A.
2. Identifica las primeras tareas exactas de US2 y sus dependencias.
3. Revisa las estructuras existentes de modelo/rutas.py, especialmente GrafoTerreno, EspacioBusqueda y HeapRutas.
4. Determina cómo implementar la búsqueda de menor costo y desempates utilizando únicamente esas estructuras propias, respetando las puertas realmente abiertas.
5. Comprueba si existe algún bloqueo real que impida comenzar con grafos sintéticos válidos sin resolver Q1–Q3.

EN ESTA ETAPA AUTORIZO ÚNICAMENTE:

- Preparar las pruebas iniciales del algoritmo de rutas de US2, según las tareas oficiales de tasks.md.
- Utilizar grafos sintéticos válidos para casos de costo mínimo, rutas alternativas, puertas cerradas, destino inalcanzable y desempate por menor ID del primer vecino.
- Ejecutar las nuevas pruebas y las regresiones pertinentes.

RESTRICCIONES:

- No implementar todavía Dijkstra ni la decisión del cazador.
- No modificar código de producción, modelo/juego.py ni modelo/enemigos.py.
- No modificar archivos de B, C o D.
- No modificar el orden de eventos ni la interfaz.
- No incorporar main ni otras ramas.
- No inventar políticas de rango ausente, null o costos inconsistentes.
- No realizar operaciones Git de escritura.
- Documentar únicamente los resultados de pruebas realmente ejecutadas y los bloqueos existentes.

Al finalizar, presenta los archivos modificados, pruebas preparadas, resultados y la siguiente tarea exacta para implementar el algoritmo. No avances automáticamente.
```

## P31 — implementación del núcleo de rutas T021

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra actual del chat; instrucciones de habilidad aportadas como contexto operativo. **Finalidad y uso de la respuesta:** implementar buscar_ruta únicamente en rutas.py con Dijkstra limitado/heap propio, sin cambiar T019 ni integrar cazador. Resultado: 23/23 métodos de rutas/estructuras (incluidos los once casos de T019), 99/99 anteriores y tres consultas complementarias de reutilización satisfactorias. T019/T021 cerradas para escenarios válidos de núcleo; Q1–Q3 y contratos abiertos, sin benchmark ni otras tareas. PROMPTS_LLM.md intacto. Inventario de 31 entradas, con vacíos y límites de completitud anteriores preservados; no se afirma recuperación de las solicitudes administrativas pendientes declaradas en P30 ni completitud global.

```text
$speckit-implement

Continúa con `001-terreno-cazador`, Persona A, exclusivamente con T021: implementar la búsqueda de rutas de costo mínimo utilizando las estructuras propias existentes.

Estado:

- Rama feature/motor-eventos.
- US1: 99 pruebas anteriores aprobadas.
- T019: diez métodos y once casos preparados en tests/test_rutas_cazador.py.
- Los once casos presentan AttributeError porque buscar_ruta todavía no existe.
- T020 y las decisiones del cazador no están implementadas.
- Q1–Q3 y los contratos externos siguen pendientes.

ANTES DE MODIFICAR:

1. Relee constitución, Parte II §3.2, spec.md, plan.md, tasks.md y contratos pertinentes.
2. Revisa GrafoTerreno, EspacioBusqueda y HeapRutas y sus interfaces reales.
3. Revisa las once comprobaciones de T019.
4. Confirma que la firma interna propuesta es compatible con las estructuras actuales.

IMPLEMENTACIÓN AUTORIZADA:

Implementa en modelo/rutas.py la función interna:

buscar_ruta(grafo, espacio, frontera, origen_indice, destino_indice, limite)

Para los escenarios válidos explícitos, debe devolver:\
(primer_indice, direccion, costo_paso, costo_total)

o None cuando no se encuentre una ruta admisible dentro del límite.

Requisitos:

- Utilizar Dijkstra con costos positivos y el heap indexado propio.
- Utilizar los índices y arreglos con generaciones existentes, evitando reinicializaciones completas innecesarias por consulta.
- Evaluar el estado real de las puertas al recorrer cada arco.
- Minimizar primero el costo total.
- En empate de costo total, seleccionar el menor ID del primer vecino.
- Propagar correctamente esa preferencia a través de convergencias.
- No depender del orden de enumeración de las salidas.
- No atravesar puertas cerradas.
- Permitir rutas de costo exactamente igual al límite.
- Evitar ciclos y no recorrer innecesariamente rutas superiores al límite.
- Mantener una consulta independiente del cazador, de la interfaz y del motor de eventos.

RESTRICCIONES:

- Modificar producción únicamente en modelo/rutas.py.
- No modificar tests/test_rutas_cazador.py ni sus expectativas.
- No modificar modelo/juego.py, modelo/enemigos.py, modelo/eventos.py ni otros archivos de producción.
- No implementar todavía modelo/cazador.py ni T020/T022.
- No usar dict, set, heapq, bisect, collections ni librerías de grafos como índices, caches o sustitutos de las estructuras propias, conforme a la constitución.
- No inventar comportamiento para rango ausente/null, costos inconsistentes ni contratos de B/C.
- No incorporar main ni modificar ramas ajenas.
- No ejecutar operaciones Git de escritura.

PRUEBAS:

1. Ejecuta tests.test_rutas_cazador y verifica los once casos.
2. Ejecuta tests.test_grafo_terreno y tests.test_heap_rutas para detectar regresiones de estructuras.
3. Ejecuta las 99 pruebas anteriores autorizadas.
4. Si una prueba falla, identifica la causa sin modificar automáticamente su expectativa.
5. No afirmar cumplimiento de rendimiento menor de 20 ms basándose en la duración de unittest.

Puedes actualizar únicamente la documentación propia de specs/001-terreno-cazador para registrar resultados y limitaciones.

Al finalizar:

- Mostrá el diff completo de rutas.py, incluyendo líneas eliminadas y añadidas.
- Informá resultados reales de pruebas.
- Explicá brevemente cómo se resuelven los empates y puertas cerradas.
- Indicá si T021 quedó verificada para datos válidos.
- No avances automáticamente a T020, T022 ni tareas posteriores.
```

## P32 — preparación de pruebas de decisión T020

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin hora individual ni modelo exacto confirmado. **Herramienta:** aplicación Codex, habilidad speckit-implement. **Fuente:** solicitud íntegra actual del chat; instrucciones de habilidad aportadas como contexto operativo. **Finalidad y uso de la respuesta:** preparar solo T020, con consulta de rutas real instrumentada localmente y fixtures existentes para observar estado/descargas. Resultado: nueve métodos/diez casos, diez errores por módulo modelo.cazador ausente; 109 pruebas existentes aprobadas. T020 preparada y sin completar, T022 no implementada ni autorizada por esta preparación. No hay nuevos mocks externos, cambios de producción/pruebas previas ni cierre de Q1–Q3/contratos. PROMPTS_LLM.md intacto. Inventario de 32 entradas, con los vacíos y límites anteriores preservados; no se afirma completitud global ni recuperación de solicitudes administrativas pendientes.

```text
$speckit-implement

Continuemos con `001-terreno-cazador`, Persona A, exclusivamente con T020: preparar las pruebas de decisión del cazador.

Estado actual:

- T019 y T021 completadas para grafos sintéticos válidos.
- buscar_ruta implementada en modelo/rutas.py.
- 23/23 pruebas de rutas y estructuras aprobadas.
- 99/99 pruebas anteriores aprobadas.
- T022 y modelo/cazador.py todavía no implementados.
- Q1–Q3 y contratos externos pendientes.

ANTES DE MODIFICAR:

1. Relee constitución, Parte II §3.2, spec.md, plan.md, tasks.md y contratos pertinentes.
2. Revisa la implementación real de buscar_ruta y el contrato interno actual.
3. Identifica las dependencias de T020 y los comportamientos oficiales de A3/A5.
4. Comprueba cuáles pruebas pueden realizarse con datos sintéticos válidos sin resolver Q1–Q3.

AUTORIZO EXCLUSIVAMENTE:

Crear tests/test_decision_cazador.py para preparar T020 mediante TDD.

Cubrir los siguientes escenarios, cuando estén respaldados por las reglas oficiales:

- Cazador y jugador en la misma sala: decisión de atacar antes de consultar rutas.
- Jugador en otra sala y ruta admisible dentro del rango: devolver el primer paso óptimo.
- Destino desconectado: esperar con costo 100.
- Ruta existente cuyo costo supera el rango: esperar con costo 100.
- Distancia exactamente igual al rango: permitir persecución.
- Puerta cerrada: no atravesarla.
- Consulta sin modificar posiciones, azar, agenda ni estado de las puertas.
- Ninguna descarga de contenido adicional para tomar la decisión.

Usar rangos enteros positivos explícitos y costos válidos. No definir comportamiento para rango ausente/null.

RESTRICCIONES:

- No implementar todavía modelo/cazador.py ni T022.
- No modificar modelo/rutas.py, modelo/juego.py, modelo/enemigos.py ni otros archivos de producción.
- No modificar pruebas existentes ni sus resultados esperados.
- No modificar componentes de B, C o D.
- No alterar eventos, interfaz ni historial.
- No introducir mocks externos sin justificación y autorización.
- No usar estructuras prohibidas por la constitución.
- No incorporar main ni otras ramas.
- No ejecutar operaciones Git de escritura.
- No inventar políticas sobre Q1–Q3 o contratos externos.

Ejecuta las nuevas pruebas para registrar su estado inicial esperado, además de las pruebas de rutas y las regresiones pertinentes.

Puedes actualizar únicamente la documentación propia de specs/001-terreno-cazador para registrar evidencia.

Al terminar, presenta los archivos modificados, los escenarios preparados, los resultados reales y la siguiente tarea exacta de implementación.

No avances automáticamente a T022 ni a otras tareas.
```

## P33 — especificación y pruebas de frontera temporal A–D

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin timestamp individual. **Herramienta/modelo:** aplicación Codex, habilidad speckit-implement; modelo exacto no confirmado. **Uso:** definir FR-020 y preparar AD-01. Los resultados se registran en quickstart.md. Se conserva P01–P32; esta ampliación no incorpora las otras solicitudes pendientes del historial ni modifica PROMPTS_LLM.md.

```text
$speckit-implement

Vamos a corregir la incompatibilidad temporal entre el motor de Persona A y la línea de tiempo de Persona D en Cripta Parte II.

Ya realizamos un análisis específico que identificó el problema: Motor.ejecutar() puede devolver el control al jugador cuando todavía hay eventos pendientes del mismo instante.

FUENTES OBLIGATORIAS:

- Cripta Parte I, §2.3.
- Cripta Parte II, §3.6 y Apéndice B.
- Constitución vigente de Spec Kit.
- specs/001-terreno-cazador/spec.md, plan.md, tasks.md y contratos.
- Código real de modelo/juego.py y modelo/eventos.py.
- Pruebas existentes, especialmente T016.

DECISIÓN DE INTEGRACIÓN A–D:

Adoptaremos una frontera temporal cerrada para la decisión del jugador.

Cuando se procese un evento turno_jugador en t, el motor debe completar los eventos automáticos pendientes del mismo instante t, respetando estrictamente el orden (tiempo, secuencia), antes de solicitar la siguiente acción del jugador.

No se debe procesar anticipadamente ningún evento de tiempo mayor que t.

Esta decisión no cambia el orden del heap ni da prioridad artificial a los enemigos. Cambia únicamente el momento de devolver el control al jugador.

PRIMERA ETAPA AUTORIZADA:

1. Revisa nuevamente las reglas oficiales y el análisis previo.
2. Actualiza exclusivamente los documentos propios de specs/001-terreno-cazador/ necesarios para especificar esta frontera temporal.
3. Registra el comportamiento esperado con jugador secuencia 10 y enemigo secuencia 11, ambos en t=100, y también el orden inverso.
4. Identifica y prepara las pruebas de regresión necesarias para:
   - Eventos del mismo instante.
   - Orden por secuencia.
   - Ataque enemigo y daño antes de solicitar la decisión.
   - Ataque letal antes de la decisión.
   - Eventos cancelados.
   - Efectos temporales y reprogramaciones.
   - Ausencia de procesamiento anticipado de t+1.
   - Continuidad del azar, agenda y determinismo.
5. Revisa la prueba T016 y explica qué expectativas pertenecen a la semántica anterior.
6. No cambies expectativas existentes sin documentar primero el motivo respaldado por la nueva especificación.
7. Identifica el cambio mínimo que después habría que implementar en juego.py.

RESTRICCIONES:

- No modificar todavía código de producción.
- No modificar archivos de B, C o D.
- No implementar todavía el registro serializable para D: su formato sigue pendiente de acuerdo.
- No modificar PROMPTS_LLM.md.
- No incorporar main ni otras ramas.
- No alterar las implementaciones de Dijkstra o del cazador.
- No ejecutar commits, push, pull, merge, rebase, reset ni clean.
- No ocultar fallos ni cambiar pruebas solo para hacerlas pasar.

Al terminar, presenta los documentos y pruebas modificados, los requisitos oficiales que los respaldan y el cambio mínimo propuesto en el motor.

No implementes todavía el cambio de producción. Espera mi autorización.
```

## P34 — confirmación del alcance con checklist pendiente

**Fecha contextual:** 2026-11-06, America/Costa_Rica; sin timestamp individual. **Herramienta/modelo:** aplicación Codex; modelo exacto no confirmado. **Uso:** continuar AD-01 con checklist 13/16, manteniendo Q1–Q3 y producción sin cambios.

```text
Sí, autorizo continuar exclusivamente con la documentación y preparación de pruebas para la frontera temporal del motor, según las instrucciones anteriores.

Condiciones:

1. Mantén sin completar los tres puntos pendientes de Q1–Q3.
2. No supongas respuestas a esas preguntas ni cambies su estado.
3. Revisa las reglas oficiales y distingue los requisitos del PDF de nuestra decisión de integración con Persona D.
4. Actualiza únicamente los documentos correspondientes de specs/001-terreno-cazador/ y prepara las pruebas necesarias.
5. No modifiques código de producción ni archivos de mis compañeros.
6. No modifiques PROMPTS_LLM.md ni incorpores cambios de main.
7. No ejecutes commit, push, merge, pull, rebase, reset ni clean.

Al finalizar, mostrame el diff de los cambios, las pruebas ejecutadas y el resultado de cada una.

No implementes todavía el cambio en Motor.ejecutar(). Espera mi autorización.
```

## Consolidación T051 — bloque 1

Este bloque añade nueve mensajes enviados por Persona A a la aplicación Codex. La fuente de cada transcripción es el mensaje del usuario en el historial visible de este chat. La fecha contextual se toma del tramo entre las entradas originales indicadas, sin timestamp individual verificable. El modelo exacto no está confirmado. El índice histórico anterior y P01–P34 se conservan íntegros.

### P35 — Diagnóstico Git previo a la integración

**Fecha contextual:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P20 y P21. **Uso:** Diagnosticar ramas, cambios y riesgos de integración de B, C y D.

```text
Necesito preparar la integración de los avances de mis compañeros B, C y D en mi rama `feature/motor-eventos`, antes de comenzar a implementar mi funcionalidad `001-terreno-cazador`.

Por ahora realiza ÚNICAMENTE un diagnóstico de Git, sin modificar archivos ni integrar ramas.

1. Comprueba la rama actual y el estado de trabajo mediante `git status`.
2. Identifica las ramas locales y remotas disponibles y cuáles corresponden a B, C y D.
3. Consulta las referencias remotas mediante `git fetch`, sin hacer merge, rebase, pull ni reset. No cambies la rama actual.
4. Compara mi rama con las ramas de cada compañero e identifica los commits que todavía no tengo.
5. Enumera los archivos modificados por cada rama, especialmente `modelo/juego.py`, `modelo/eventos.py`, `modelo/efectos.py`, `modelo/enemigos.py`, `modelo/tipos.py`, `modelo/snapshots.py`, `tests/`, `specs/` y archivos compartidos.
6. Detecta posibles conflictos y dependencias entre los cambios de B, C y D.
7. Comprueba que mis archivos de `specs/001-terreno-cazador/`, incluidos los no confirmados, estén protegidos ante una futura integración.
8. No descartes ni sobrescribas cambios locales. No ejecutes `git add`, commit, push, pull, merge, rebase, reset, clean, stash ni checkout.

Si Git necesita autenticación o hay alguna operación que pueda alterar archivos locales, detente e infórmame.

Al finalizar, presenta qué ramas están disponibles, qué trabajo podríamos traer de cada compañero, el orden de integración que recomiendas y los riesgos concretos.

NO integres todavía ninguna rama. Espera mi autorización.
```

### P36 — Revisión previa al respaldo documental

**Fecha contextual:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P20 y P21. **Uso:** Revisar los 12 archivos de Persona A y delimitar el commit documental propuesto.

```text
Necesito proteger mi documentación de la Persona A antes de integrar las ramas de B y D.

Trabaja exclusivamente en la rama `feature/motor-eventos`.

Primero, revisa los 12 archivos sin seguimiento de `specs/001-terreno-cazador/` y verifica que no contengan secretos, datos personales innecesarios, archivos generados irrelevantes o modificaciones a componentes de compañeros.

Después, prepara un commit LOCAL que incluya únicamente los archivos de `specs/001-terreno-cazador/`.

No incluyas `.idea/`, datos_generados/, respaldos de puntajes, `.specify/feature.json` ni archivos fuera de esa carpeta.

Antes de crear el commit, muestra:

- Lista exacta de archivos que incluirías.
- Resumen de los cambios.
- Si los documentos siguen condicionados por Q1–Q3.
- Mensaje propuesto de commit.

No ejecutes todavía `git add` ni `git commit`: espera mi autorización expresa después de revisar el contenido.

No ejecutes push, pull, fetch, merge, rebase, reset, clean, stash ni checkout. No modifiques archivos.
```

### P37 — Anonimización y commit documental local

**Fecha contextual:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P20 y P21. **Uso:** Anonimizar una referencia de procedencia y respaldar localmente los 12 archivos revisados.

```text
Autoriza corregir únicamente la referencia de procedencia de la línea 159 en `specs/001-terreno-cazador/prompts-registro-local.md`.

Sustituye la ruta absoluta que contiene mi usuario de Windows por una referencia relativa o anonimizada. Conserva íntegramente todos los prompts, fechas, herramientas y demás información relevante.

Después, crea un commit exclusivamente LOCAL con los 12 archivos de `specs/001-terreno-cazador/`.

Mensaje del commit:\
docs(persona-a): resguardar especificación y plan provisional de terreno y cazador

No incluyas `.idea/`, puntajes, respaldos, `.specify/feature.json` ni archivos externos a esa carpeta.

No ejecutes push, pull, fetch, merge, rebase, reset, clean ni stash.

Al finalizar, confirma el hash del commit, los archivos incluidos y el estado de Git. No comiences la implementación.
```

### P38 — Inspección de las dependencias de B

**Fecha contextual:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P20 y P21. **Uso:** Identificar qué datos y contratos de B estaban disponibles para US1 y US2.

```text
Mi documentación de Persona A ya está protegida mediante el commit local `4ee04ff`.

Ahora quiero determinar exactamente qué necesito del código de B para implementar `001-terreno-cazador` y cuáles de esas dependencias ya están disponibles.

Inspecciona exclusivamente en modo de lectura `origin/codex/verificador-resolubilidad`, utilizando las referencias Git ya descargadas.

Revisa los archivos relevantes de `red/`, `datos/` y `modelo/`, incluyendo el código existente en mi rama cuando sea necesario para comparar contratos.

Para cada dependencia de A, determina:

1. Qué dato o comportamiento necesito: costos de salida, rango del cazador, conexiones, estado de puertas, versiones y acceso local.
2. Si B ya lo implementó, lo implementó parcialmente o todavía no.
3. Archivo, clase, función y estructura exacta donde está disponible.
4. Cómo podría consumirlo mi motor sin modificar archivos propiedad de B.
5. Si para usarlo necesito integrar toda la rama, archivos específicos o si ya existe en mi rama.
6. Qué información o acuerdo falta solicitarle a B.

Distingue claramente entre la API HTTP, la precarga, el almacenamiento local y las reglas que corresponden al motor de A.

No confundas el verificador de resolubilidad de B con el suministro de datos que necesita el cazador.

No modifiques archivos, no ejecutes pruebas, no hagas commits ni operaciones Git que alteren ramas o archivos.

Entrega una tabla con el estado REAL de cada dependencia y una recomendación concreta sobre si necesito incorporar algún cambio de B antes de comenzar a implementar US1 y US2.
```

### P39 — Auditoría de pruebas T005–T012

**Fecha contextual:** 2026-11-05, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P22 y P23. **Uso:** Evaluar invariantes del motor, fidelidad de los fixtures y causas de los diez fallos.

```text
Además de la auditoría técnica de T005–T012, revisa específicamente las nuevas pruebas `tests/test_costos_terreno.py`, `tests/test_velocidad_terreno.py` y el fixture `motor_terreno`.

Comprueba que las modificaciones directas de reloj, posición del jugador, comportamiento de enemigos, velocidad y datos de salidas no violen invariantes del motor ni produzcan falsos resultados.

Verifica que dos llamadas consecutivas a `motor.mover()` representen un escenario permitido por su contrato, o identifica cómo probar ambos sentidos sin saltarse el tiempo virtual.

Comprueba que los diez fallos correspondan realmente a la integración pendiente de costos variables y que no oculten defectos independientes de las pruebas.

No modifiques archivos ni código. No ejecutes Implement ni operaciones Git.

Entrega hallazgos respaldados por funciones y reglas concretas, distinguiendo errores confirmados de riesgos potenciales.
```

### P40 — Revisión previa al commit de US1

**Fecha contextual:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P29 y P30. **Uso:** Revisar el alcance del commit de US1 a partir de los cambios y de la evidencia de T017.

```text
Quiero preparar un commit LOCAL del código y las pruebas verificadas de la Persona A antes de continuar con US2.

Estamos en `feature/motor-eventos`. La verificación conjunta T017 reportó 99/99 pruebas aprobadas.

Por ahora trabaja únicamente en modo de revisión.

1. Ejecuta git status y revisa el diff completo, incluyendo archivos nuevos sin seguimiento.
2. Identifica todos los cambios propios de A desde el commit 4ee04ff.
3. Confirma que modelo/juego.py solo contiene los cambios autorizados de T013/T014.
4. Revisa los archivos nuevos modelo/rutas.py y tests/ correspondientes a T005–T016.
5. Comprueba que la documentación actualizada conserve los resultados reales, las tareas pendientes y Q1–Q3 abiertas.
6. Comprueba que no se incluyan archivos de B, C o D, .idea/, puntajes, respaldos ni archivos generados irrelevantes.
7. Identifica cualquier problema que deba corregirse antes de confirmar los cambios.

Propón los archivos exactos para el commit y un mensaje adecuado que indique que US1 fue verificada con datos válidos, sin afirmar integración completa con B.

No ejecutes todavía git add, commit, push, pull, fetch, merge, rebase, reset, clean ni stash. No modifiques archivos.

Espera mi autorización después de mostrar el diagnóstico.
```

### P41 — Correcciones editoriales y commit local de US1

**Fecha contextual:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P29 y P30. **Uso:** Corregir el encabezado y los comandos históricos, y confirmar los diez archivos autorizados.

```text
Autoriza preparar y crear un commit exclusivamente LOCAL con los 10 archivos verificados de la Persona A.

Primero realiza dos correcciones editoriales:

1. En tests/test_costos_terreno.py, actualiza únicamente el encabezado desactualizado que indica «motor sin cambios» y pruebas «aún rojas». Debe reflejar el estado actual sin modificar funciones, pruebas ni expectativas.
2. En specs/001-terreno-cazador/quickstart.md, sustituye las rutas absolutas del intérprete que contienen mi usuario de Windows por comandos portables desde la raíz del proyecto, por ejemplo `python -B -m unittest ...`. Conserva los resultados históricos y aclara que las ejecuciones originales utilizaron Python 3.12.14. No borres evidencia ni alteres resultados.

Después verifica que el diff solo incluya esas correcciones editoriales y los cambios previamente revisados.

Prepara y crea un commit LOCAL únicamente con estos archivos:

- modelo/juego.py
- modelo/rutas.py
- tests/datos_terreno_cazador.py
- tests/test_costos_terreno.py
- tests/test_grafo_terreno.py
- tests/test_heap_rutas.py
- tests/test_velocidad_terreno.py
- specs/001-terreno-cazador/tasks.md
- specs/001-terreno-cazador/quickstart.md
- specs/001-terreno-cazador/prompts-registro-local.md

Mensaje del commit:

feat(persona-a): añadir fundamentos y verificar US1 con datos válidos

Cuerpo:

Implementar costos de movimiento y estructuras propias de rutas.\
Registrar 99 pruebas aprobadas y los límites de cobertura.\
Mantener pendientes E-B-COSTOS y Q1–Q3, sin acreditar integración con B.

Restricciones:

- Trabajar únicamente en feature/motor-eventos.
- No incluir .idea/, puntajes, respaldos ni .specify/feature.json.
- No modificar código de B, C o D.
- No modificar constitución, PROMPTS_LLM.md ni interfaz.
- No ejecutar push, pull, fetch, merge, rebase, reset, clean ni stash.
- No comenzar US2 ni ninguna otra implementación.

Antes de confirmar, comprobar que el índice contenga exactamente esos 10 archivos y que git diff --cached --check no reporte errores.

Al finalizar, indicar el hash del commit, los archivos incluidos y el estado de Git. No subir nada a GitHub.
```

### P42 — Publicación de los dos commits de Persona A

**Fecha contextual:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P29 y P30. **Uso:** Verificar alcance y destino y publicar el respaldo documental y US1.

```text
Autoriza exclusivamente publicar en GitHub los dos commits locales pendientes de la rama feature/motor-eventos.

Antes de publicar:

1. Confirma que seguimos en feature/motor-eventos.
2. Confirma que HEAD corresponde al commit 15adfcf35e3a08d748c94ad311151a16ee89a9ad.
3. Verifica que únicamente hay dos commits locales pendientes respecto de origin/feature/motor-eventos.
4. Confirma que los archivos .idea/, puntajes y respaldos siguen fuera del commit.
5. Comprueba que el destino sea origin/feature/motor-eventos.

Si todo coincide, ejecuta únicamente:

git push origin feature/motor-eventos

No hagas merge, rebase, pull, force push ni modificaciones de código. No cambies main ni las ramas de B, C o D.

Si Git rechaza el push o detectas diferencias inesperadas con el remoto, detente e informa sin intentar resolverlas automáticamente.

Al finalizar, proporciona el resultado del push y confirma la rama remota actualizada. No comiences US2 todavía.
```

### P43 — Inspección de los dos commits de origin/main

**Fecha contextual:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje del usuario en este chat, entre P29 y P30. **Uso:** Evaluar el impacto de los commits de main y el orden de integración antes de US2.

```text
Antes de comenzar US2, quiero revisar los dos commits nuevos de origin/main que todavía no están en feature/motor-eventos.

Trabaja únicamente en modo de inspección.

1. Ejecuta git fetch origin para actualizar las referencias remotas, sin modificar mi rama de trabajo.
2. Compara origin/main con feature/motor-eventos.
3. Identifica los commits nuevos de main, sus autores, mensajes y archivos modificados.
4. Determina si afectan modelo/juego.py, modelo/rutas.py, motor de eventos, modelos de enemigos, interfaces o dependencias necesarias para US2.
5. Identifica posibles conflictos con mis cambios de Persona A.
6. Recomienda si conviene integrar main ahora o posponerlo, explicando por qué.

No ejecutes merge, rebase, pull, cherry-pick, reset, clean, stash, commits ni push.

No modifiques archivos del proyecto ni comiences US2.

Al finalizar, presenta el diagnóstico y espera mi autorización antes de cualquier integración.
```

### Pendientes de recuperación o incorporación

Del inventario de la auditoría quedan 30 solicitudes o continuaciones fuera de este bloque: 7 entre P32 y P33 y 23 después de P34, incluida la solicitud de auditoría. Entre esas 30, los mensajes sobre posponer la consolidación compartida y autorizar la reversión local aparecen con un final posiblemente truncado. Su cierre textual queda pendiente de cotejo con la fuente original. Los otros 28 mensajes del inventario quedan para bloques posteriores.

La autorización de este bloque también es un mensaje enviado a Codex y queda para una etapa posterior, fuera del conteo de 39 solicitudes de la auditoría previa. Las propuestas de planificación o borradores que no se hayan enviado quedan fuera del índice de mensajes. T051 sigue pendiente.

## Consolidación T051 — bloque 2

Los cinco cuerpos se tomaron del registro original de la sesión de Codex y se cotejaron con el historial visible. Las fechas se verificaron a partir del timestamp de cada mensaje, convertido a America/Costa_Rica. El modelo exacto no está confirmado.

### P44 — Análisis de la frontera temporal A–D

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, entre P32 y P33. **Uso:** Contrastar el orden de eventos y los requisitos de historia para delimitar el cambio de Persona A.

```text
$speckit-analyze

Necesito revisar una posible incompatibilidad entre el motor de eventos de Persona A y la línea de tiempo de Persona D en Cripta Parte II.

IMPORTANTE: esta etapa es exclusivamente de análisis. No modificar código, pruebas, especificaciones ni documentación.

CONTEXTO:

- Trabajo en feature/motor-eventos.
- US1 tiene 99 pruebas aprobadas.
- US2 tiene Dijkstra implementado y pruebas de rutas aprobadas.
- Persona D solicita procesar todos los eventos del mismo instante antes de pedir la siguiente decisión al jugador.
- También solicita que A entregue un registro de eventos y cambios que permita reconstruir el historial.

VERIFICAR EN FUENTES OFICIALES:

1. Parte I §2.3: orden de eventos por tiempo y secuencia.
2. Parte II §3.6 y Apéndice B: significado de historia \<t>, especialmente cuando coinciden eventos y una decisión del jugador.
3. División oficial de responsabilidades A/D.
4. Constitución, spec.md, plan.md, tasks.md y contratos de integración.
5. Código real de modelo/juego.py, modelo/eventos.py, historial y pruebas actuales, especialmente T016.

ANALIZAR:

- Qué exige literalmente cada documento.
- Si realmente es obligatorio procesar todos los eventos empatados antes de solicitar la decisión del jugador, o si existe otra implementación que cumpla el historial sin alterar la semántica observable de la partida.
- Qué ocurre actualmente cuando turno_jugador tiene secuencia 10 y turno_enemigo secuencia 11, ambos en t=100.
- Qué comportamiento debería tener historia 100 según el enunciado.
- Qué pruebas actuales cambiarían y cuáles deben conservarse.
- Qué datos y cambios puede proporcionar A a D sin modificar archivos de D.
- Qué contrato concreto debemos acordar antes de implementar el registro.
- Qué cambios de requisitos exigirían actualizar primero la especificación bajo Spec Kit.

RESTRICCIONES:

- No modificar ningún archivo.
- No implementar todavía el ajuste de eventos ni el registro histórico.
- No alterar expectativas de pruebas para hacerlas pasar.
- No modificar trabajo de B, C o D.
- No incorporar main ni realizar operaciones Git de escritura.
- No comenzar nuevas tareas de US2.
- No asumir que la propuesta de D es obligatoria sin demostrarlo con el enunciado.

ENTREGAR:

1. Citas exactas de los apartados oficiales pertinentes.
2. Diagnóstico del comportamiento actual frente a lo exigido.
3. Diferencia entre requisitos explícitos e interpretaciones de implementación.
4. Recomendación mínima de cambio, solo si está justificada.
5. Pruebas que habría que crear antes de implementar.
6. Dependencias que requieren acuerdo con D.

No implementes nada hasta recibir autorización.
```

### P45 — Consolidación propuesta de la bitácora compartida

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, entre P32 y P33. **Uso:** Definir la comprobación previa, el alcance documental y las verificaciones para incorporar P01–P32.

```text
Necesito consolidar mis prompts de Persona A en el archivo oficial PROMPTS_LLM.md de Cripta Parte II.

Estamos trabajando en feature/motor-eventos.

IMPORTANTE: esta tarea es exclusivamente documental. No implementes el ajuste temporal del motor identificado en el análisis A/D ni continúes US2.

CONTEXTO:

- La versión actualizada de PROMPTS_LLM.md está en origin/main.
- Mi rama contiene una versión anterior de ese archivo.
- Mis prompts están registrados en specs/001-terreno-cazador/prompts-registro-local.md, con entradas identificadas hasta P32.
- También existen registros complementarios con textos completos de algunas entradas.
- Tengo cambios locales de US2 sin confirmar en Git.
- No quiero traer los puntajes ni los demás archivos de main.

FASE 1 — COMPROBACIÓN:

1. Confirma la rama, HEAD y git status.
2. Comprueba que PROMPTS_LLM.md no tenga modificaciones locales sin confirmar.
3. Consulta el archivo actualizado mediante git show origin/main.md.
4. Comprueba si origin/main sigue siendo la referencia remota más reciente disponible. No hagas fetch automáticamente.
5. Compara el documento compartido con la versión de mi rama.
6. Lee íntegramente prompts-registro-local.md y todos los registros complementarios referenciados.
7. Revisa el formato de PROMPTS_LLM.md y las exigencias de la constitución sobre trazabilidad.

Si hay modificaciones locales conflictivas en PROMPTS_LLM.md, archivos fuente faltantes o algún riesgo de sobrescribir información, detente antes de editar y presenta el problema.

FASE 2 — ACTUALIZACIÓN AUTORIZADA:

Si las comprobaciones anteriores son satisfactorias:

1. Utiliza exclusivamente el contenido actualizado de origin/main.md como base del archivo compartido en mi rama.
2. Conserva íntegramente todas las entradas existentes de los compañeros.
3. Incorpora los prompts auténticos de Persona A respetando el formato del archivo: fecha, herramienta/modelo, prompt textual completo y uso de la respuesta.
4. Utiliza los textos originales P01–P32, recuperando los complementarios P05, P06, P13 y P16 de sus fuentes reales.
5. Conserva las fechas conocidas y distingue expresamente las contextuales de los timestamps confirmados.
6. No inventes horas, modelos, prompts ni resultados ausentes.
7. Identifica las entradas incompletas y las solicitudes administrativas aún pendientes de consolidación.
8. Evita duplicar prompts existentes y señala cualquier entrada que no pueda incorporarse fielmente.

No borres ni modifiques las entradas de mis compañeros.

FASE 3 — VERIFICACIÓN:

- Comprueba que el contenido anterior de origin/main permanezca intacto.
- Informa cuántos prompts de A quedaron incorporados íntegramente y cuáles permanecen pendientes.
- Revisa el diff completo, incluyendo líneas eliminadas y agregadas.
- Ejecuta git diff --check.
- Confirma que únicamente PROMPTS_LLM.md cambió durante esta tarea.
- Confirma que modelo/rutas.py, tests/test_rutas_cazador.py, tests/test_decision_cazador.py y los demás cambios locales de US2 permanecen intactos.
- Conserva los archivos locales de prompts y la documentación Spec Kit como respaldo.

RESTRICCIONES:

- No ejecutar merge, pull, rebase, reset, clean ni stash.
- No modificar main ni las ramas de otros integrantes.
- No modificar archivos de código o pruebas.
- No modificar puntajes, interfaz ni documentación de otros integrantes.
- No hacer commit ni push todavía.
- No modificar el comportamiento del motor ni las especificaciones A/D.
- No eliminar documentos de specs.

Al finalizar, mostra el diagnóstico, los cambios realizados, el estado de Git y los pendientes. Espera mi autorización antes de confirmar o publicar.
```

### P46 — Aclaración sobre formato y orden cronológico

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, entre P32 y P33. **Uso:** Precisar cómo intercalar los prompts de Persona A conservando el formato y las entradas de los compañeros.

```text
ACLARACIÓN IMPORTANTE SOBRE EL FORMATO Y EL ORDEN:

- Respeta exactamente el formato y la estructura de PROMPTS_LLM.md, utilizando la versión actualizada de origin/main como referencia.
- Integra mis prompts de Persona A en orden cronológico por fecha, junto con los registros de los demás integrantes, no simplemente todos al final.
- Conserva el texto íntegro y la atribución de cada entrada de B, C y D, sin modificar su contenido.
- Si varios prompts tienen la misma fecha y no existe una hora verificable, conserva su orden original y no inventes horarios.
- Cuando una fecha sea contextual, identifícala como tal sin presentarla como fecha exacta.
- Antes de modificar el archivo, comprueba si las entradas existentes siguen un orden cronológico uniforme. Si no es así, no reordenes ni reescribas entradas ajenas automáticamente; informa cómo insertar las mías sin alterar su contenido ni atribución.
- No dupliques entradas ni elimines registros.

El objetivo es tener una sola bitácora compartida, organizada por fechas, con los prompts auténticos de todos los integrantes y sin perder información.
```

### P47 — Tamaño de la bitácora y registro textual

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, entre P32 y P33. **Uso:** Delimitar los campos obligatorios y pedir un cálculo previo del tamaño de la incorporación.

```text
Antes de continuar con la incorporación de mis prompts, quiero evitar que PROMPTS_LLM.md crezca innecesariamente.

Respeta el formato compartido y los requisitos académicos sobre registrar el prompt textual.

Para cada entrada de Persona A:

1. Conserva el prompt original completo cuando esté disponible; no lo sustituyas por un resumen presentado como texto literal.
2. Incluye únicamente fecha, responsable, herramienta/modelo, prompt textual y una explicación breve del uso de la respuesta.
3. NO copies las respuestas completas de Codex, informes extensos, tablas de resultados, análisis técnicos ni documentación duplicada de quickstart.md.
4. No dupliques instrucciones de habilidades o anexos que no formen parte del texto enviado por el usuario.
5. Mantén los prompts en orden cronológico, respetando los bloques existentes de los compañeros.
6. Si hay prompts repetidos o solicitudes que no correspondan al proyecto, identifícalos antes de incorporarlos; no elimines registros obligatorios automáticamente.
7. No inventes textos, fechas, modelos ni resultados.

Antes de escribir, informa cuántas entradas incorporarías y el tamaño aproximado que añadirían al archivo. Si resulta demasiado extenso, presenta opciones para reducir duplicaciones sin perder el registro obligatorio.

No hagas commit ni push todavía.
```

### P48 — Cotejo de la bitácora local con origin/main

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, entre P32 y P33. **Uso:** Verificar en lectura el contenido compartido y explicar el origen de las 19 líneas incorporadas.

```text
Antes de incorporar mis 32 prompts, quiero confirmar que PROMPTS_LLM.md de mi rama contiene íntegramente la versión actual de origin/main.

Trabaja únicamente en modo lectura.

1. Confirma que estoy en feature/motor-eventos.
2. Comprueba el hash actual de origin/main y el de main en GitHub, sin ejecutar fetch.
3. Compara el PROMPTS_LLM.md de mi carpeta de trabajo con origin/main.md.
4. Verifica que todas las entradas de mis compañeros estén presentes y sin modificaciones.
5. Explica exactamente qué 19 líneas incorporaste, mediante qué operación y si falta algún contenido de main.

No modifiques archivos, no hagas pull, merge, commit ni push.

Mostrame los resultados antes de continuar agregando mis prompts.
```

### Pendientes de recuperación o incorporación tras el bloque 2

Quedan 25 solicitudes o continuaciones de las 39 identificadas en la auditoría: 23 posteriores a P34, incluida la solicitud de auditoría, y las dos siguientes entre P32 y P33. Los originales disponibles en el registro de la sesión terminan en los mismos fragmentos que el historial visible:

- Solicitud de posponer la incorporación a la bitácora compartida. Final disponible: `Presenta únicamente e`.
- Autorización para revertir la incorporación local de las 19 líneas. Final disponible: `no tiene cambios locales pendient`.

Se conserva su orden de envío y su condición de textos incompletos. Las autorizaciones de los bloques 1 y 2 quedan para una etapa posterior y se cuentan aparte del inventario inicial. T051 sigue pendiente.

## Consolidación T051 — bloque 3

Se recuperan los diez primeros mensajes enviados por Persona A después de P34. La fuente es el registro original de esta sesión de Codex. Las fechas se verificaron a partir de los timestamps de los mensajes, convertidos a America/Costa_Rica. El modelo exacto no está confirmado.

### P49 — Corrección documental de AD-01

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Separar la decisión técnica de A de una aceptación formal de D y revisar el texto de P34.

```text
Revisé el resultado de AD-01. Las 11 pruebas nuevas y las 99 regresiones están documentadas. Antes de autorizar producción, necesito una corrección documental puntual.

1. Revisa contracts/integracion.md, plan.md y spec.md para distinguir una decisión de implementación de Persona A de un acuerdo formal con Persona D.

No afirmes que existe aceptación formal de D si no hay evidencia verificable. Conserva la frontera temporal como decisión técnica adoptada para compatibilidad con historia \<t>, pendiente de validación de integración.

2. No cambies el estado de E-D-CAMBIOS ni de los demás contratos pendientes.
3. Revisa P34 en prompts-registro-local.md. Comprueba si contiene accidentalmente notas sobre T020/T022 o resultados anteriores dentro del bloque de texto del prompt.

Si es así, separa esas notas del prompt original, conservando íntegramente el texto realmente enviado. No inventes ni reconstruyas contenido que no puedas verificar.

4. Comprueba que los enlaces Markdown de las adendas funcionen y que no existan secciones duplicadas accidentalmente.
5. Mantén las 11 pruebas nuevas sin alterar sus expectativas y conserva las 99 regresiones.
6. Ejecuta git diff --check y muestra un resumen exacto de las correcciones realizadas.

No modifiques producción, no toques PROMPTS_LLM.md ni los archivos de otros integrantes. No hagas commit, push, pull, merge, reset ni rebase.

Después de esta revisión, detente. No implementes todavía la frontera temporal.
```

### P50 — Revisión del alcance del commit documental de FR-020

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Verificar la sección IV de la constitución y delimitar el commit documental previo a AD-02.

```text
La revisión documental de FR-020 está aceptada para continuar con la preparación de AD-02.

Antes de implementar código, verifica literalmente qué exige la sección IV de la constitución sobre confirmar en Git las enmiendas a la especificación.

1. Identifica los archivos exactos que deben incluirse en un commit documental de FR-020.
2. Distingue los archivos modificados exclusivamente por esta corrección de los cambios anteriores de US2.
3. Comprueba qué modificaciones pendientes existen en cada archivo y evita incluir trabajos anteriores no autorizados.
4. Indica si es viable hacer un commit documental independiente sin incluir código de producción, pruebas del cazador ni documentación de otros trabajos.
5. No incluyas PROMPTS_LLM.md.
6. No hagas cambios adicionales ni ejecutes git add, commit, push, merge, pull, rebase, reset, restore o clean.

Mostrame el alcance exacto del commit propuesto y esperá autorización.
```

### P51 — Autorización del commit documental de FR-020

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Confirmar localmente los tres documentos autorizados de la enmienda.

```text
Autorizo crear exclusivamente el commit documental local de FR-020.

Rama obligatoria: feature/motor-eventos.

Archivos autorizados:

- specs/001-terreno-cazador/spec.md
- specs/001-terreno-cazador/plan.md
- specs/001-terreno-cazador/contracts/integracion.md

Procedimiento:

1. Verifica nuevamente que estamos en feature/motor-eventos y que el índice está vacío.
2. Confirma que los diffs de esos tres archivos siguen correspondiendo únicamente a la documentación de FR-020.
3. Prepara exclusivamente esos tres archivos con git add usando sus rutas exactas.
4. Revisa git diff --cached --stat y git diff --cached --check.
5. Comprueba que el índice contiene exactamente los tres archivos autorizados.
6. Crea el commit local con el mensaje:

docs(persona-a): especificar frontera temporal FR-020

7. Muestra el hash del nuevo commit, sus archivos incluidos y git status --short.
8. Confirma que los cambios pendientes de US2 siguen intactos.

No hagas push, pull, fetch, merge, rebase, reset, restore ni clean.

No modifiques código de producción, pruebas ni documentación adicional.

Después del commit, detente. No implementes todavía AD-02 hasta que revisemos el resultado.
```

### P52 — Implementación de la frontera temporal AD-02

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Implementar FR-020 y ejecutar la validación dentro del alcance autorizado.

```text
$speckit-implement

Autorizo implementar exclusivamente AD-02: frontera temporal FR-020.

La especificación ya fue confirmada mediante el commit local 26be4074f4e1ddd10449df164b1f1f43ebd2d5bf.

ALCANCE AUTORIZADO:

- modelo/juego.py
- modelo/eventos.py, únicamente si es indispensable para evitar extraer eventos posteriores al límite temporal.
- Ajustes mínimos a tests/test_frontera_temporal.py solo si se demuestra un error real en la prueba, nunca para ocultar un fallo.

REQUISITOS:

1. Respeta FR-020 y los escenarios A14–A18.
2. Al procesar el turno vigente del jugador en t, completa los eventos automáticos pendientes del mismo instante antes de devolver el control.
3. Conserva estrictamente el orden (tiempo, secuencia).
4. No ejecutes eventos posteriores a t, ni siquiera al descartar eventos cancelados.
5. Si el jugador muere durante ese instante, termina la partida sin ofrecer otra decisión.
6. Conserva el contrato de ejecutar_ciclo() sin límite: procesa un único evento.
7. Conserva la semántica de cancelaciones, reprogramaciones, efectos, RNG y restauración ante errores.
8. Evita cambiar las reglas de costos, Dijkstra, cazador o enemigos.
9. Mantén el procesamiento dentro de la transacción y la publicación diferida de mensajes existentes.

VERIFICACIONES OBLIGATORIAS:

- Ejecuta las 11 pruebas de tests/test_frontera_temporal.py.
- Ejecuta las 99 regresiones anteriores.
- Ejecuta también tests/test_rutas_cazador.py y tests/test_decision_cazador.py, distinguiendo los fallos esperados de T020 porque modelo/cazador.py todavía no existe.
- Comprueba que ningún evento futuro se consuma anticipadamente.
- Revisa git diff --check.
- Presenta los cambios exactos, los resultados y cualquier regresión detectada.

RESTRICCIONES:

- No modificar archivos de B, C ni D.
- No modificar PROMPTS_LLM.md.
- No modificar modelo/rutas.py ni sus pruebas.
- No implementar T022 ni crear modelo/cazador.py.
- No incorporar main ni otras ramas.
- No realizar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Preservar todos los archivos locales pendientes, incluidos .idea/ y los respaldos de puntajes.

Si surge una incompatibilidad que requiera ampliar el alcance, detenerse y explicarla antes de modificar otros archivos.

Al terminar, mostrar diff y resultados, y detenerse sin crear commit.
```

### P53 — Reconciliación de cuatro regresiones de AD-02

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Trazar los cuatro fallos y ajustar solo las expectativas atribuibles a FR-020.

```text
Revisé el resultado de AD-02. Autorizo continuar exclusivamente con la reconciliación de las cuatro regresiones que fallaron, pero primero debes comprobar que cada fallo se debe realmente al cambio de semántica de FR-020.

INSTRUCCIONES:

1. Examina las cuatro pruebas fallidas en su totalidad y contrástalas con FR-020, el orden (tiempo, secuencia) y el código implementado.
2. Verifica mediante trazas reales la secuencia de eventos, los tiempos, el daño, la regeneración, las reprogramaciones y el consumo de RNG cuando corresponda.
3. Comprueba que los resultados nuevos son correctos y que no existe un defecto en el motor.
4. Si cada fallo se explica exclusivamente por una expectativa antigua, autoriza actualizar únicamente las aserciones afectadas en:
   - tests/test_costos_terreno.py
   - tests/test_regresiones_juego.py
5. Conserva la intención original de las pruebas. No elimines casos, no debilites aserciones y no utilices skip ni expectedFailure.
6. Si alguna prueba revela un defecto real o una interpretación ambigua, detente y explícalo antes de modificarla.
7. Ejecuta las 11 pruebas de frontera temporal, las 99 regresiones antiguas y las 10 pruebas de rutas.
8. Verifica también el rollback, RNG, cancelaciones y que no se ejecuten eventos de t+1 anticipadamente.
9. Ejecuta git diff --check y presenta el diff exacto de las aserciones modificadas.

RESTRICCIONES:

- No modificar producción adicionalmente sin autorización.
- No modificar modelo/rutas.py ni implementar T022.
- No modificar archivos de B, C o D.
- No modificar PROMPTS_LLM.md.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore ni clean.
- Conservar intactos los cambios pendientes de US2 y los respaldos locales.

Detente al finalizar y presenta los resultados antes de continuar con AD-03.
```

### P54 — Validación final de FR-020 en AD-03

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Revisar la implementación, repetir pruebas y documentar la evidencia local.

```text
$speckit-implement

Continuemos exclusivamente con AD-03: validación final de FR-020 para Cripta Parte II.

AD-02 ya está implementada sin commit y la reconciliación de las cuatro regresiones produjo los siguientes resultados:

- Frontera temporal: 11/11.
- Regresiones anteriores: 99/99.
- Rutas del cazador: 10/10.

OBJETIVO:

Confirmar que FR-020 cumple su especificación, no introduce regresiones y puede cerrarse sin afectar US2 ni las responsabilidades de otros integrantes.

VERIFICACIONES:

1. Revisa el diff completo de modelo/juego.py y modelo/eventos.py frente a FR-020, A14–A18 y los requisitos aplicables de Parte I y Parte II.
2. Revisa las modificaciones de tests/test_costos_terreno.py y tests/test_regresiones_juego.py. Comprueba que ninguna aserción se debilitó o cambió únicamente para ocultar errores.
3. Confirma que la sonda temporal utilizada en test_costos_terreno.py no modifica los resultados del motor y queda aislada al caso de prueba.
4. Verifica los eventos empatados, cancelaciones, reprogramaciones, derrota, efectos, RNG, rollback y publicación diferida de mensajes.
5. Comprueba que ejecutar_ciclo() sin límite conserva su comportamiento de un evento.
6. Ejecuta las suites de frontera temporal, las 99 regresiones y las rutas del cazador.
7. Ejecuta las demás pruebas existentes que puedan ejecutarse sin funcionalidades todavía pendientes. Separa claramente fallos anteriores o esperados de regresiones nuevas.
8. Comprueba que los eventos con tiempo mayor que la frontera quedan sin ejecutar.
9. Ejecuta git diff --check y revisa el estado de Git.

DOCUMENTACIÓN:

Actualiza exclusivamente tasks.md y quickstart.md de Persona A para reflejar resultados verificados de AD-02 y AD-03. No marques AD-03 como completada si queda alguna comprobación sin resolver.

No marques T022 ni T020 como completadas. No inventes respuestas a Q1–Q3 y mantén pendiente E-D-CAMBIOS.

RESTRICCIONES:

- No modificar más código de producción ni pruebas sin autorización.
- No modificar archivos de B, C o D.
- No modificar PROMPTS_LLM.md.
- No modificar rutas.py ni implementar modelo/cazador.py.
- No incorporar main.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar intactos los cambios pendientes de US2 y los respaldos locales.

Al finalizar, presenta un informe preciso de las pruebas ejecutadas, posibles riesgos pendientes, archivos modificados y estado de las tareas. Detente sin crear commit.
```

### P55 — Preparación del commit independiente de FR-020

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Delimitar el cierre de AD-02 y AD-03 sin incorporar los cambios de US2.

```text
La validación local de AD-03 está aceptada.

Quiero preparar el cierre de FR-020 mediante un commit local independiente, sin publicarlo todavía.

PRIMERA ETAPA: SOLO LECTURA.

1. Confirma la rama feature/motor-eventos y el estado completo de Git.
2. Identifica todos los archivos modificados específicamente por AD-02 y AD-03.
3. Verifica los diffs de modelo/juego.py, modelo/eventos.py, tests/test_costos_terreno.py, tests/test_regresiones_juego.py y tests/test_frontera_temporal.py.
4. Revisa si tasks.md y quickstart.md mezclan cambios previos de US2 con AD-03.
5. Confirma que puede prepararse un commit separado de FR-020 sin incluir accidentalmente cambios pendientes de T019–T022.
6. Propón el conjunto exacto de archivos o fragmentos que deberían incluirse en ese commit y un mensaje de commit apropiado.

No ejecutes git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.

No modifiques archivos. Presenta el alcance propuesto y espera mi autorización.
```

### P56 — Autorización del commit independiente de FR-020

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Confirmar código, pruebas y fragmentos documentales de FR-020 en un commit local separado.

```text
Autorizo preparar y crear exclusivamente el commit local de FR-020 en feature/motor-eventos, con las siguientes condiciones.

ARCHIVOS COMPLETOS AUTORIZADOS:

- modelo/juego.py
- modelo/eventos.py
- tests/test_costos_terreno.py
- tests/test_regresiones_juego.py
- tests/test_frontera_temporal.py

ARCHIVOS CON SELECCIÓN PARCIAL:

- specs/001-terreno-cazador/tasks.md: únicamente la fila FR-020 y la adenda de frontera temporal AD-01–AD-03.
- specs/001-terreno-cazador/quickstart.md: únicamente las secciones «Frontera temporal AD-01» y «Validación local AD-03».

IMPORTANTE:

1. Confirma que la rama sigue siendo feature/motor-eventos y que el índice está vacío.
2. Prepara los cinco archivos completos usando sus rutas exactas.
3. Para tasks.md y quickstart.md, construye el contenido del índice a partir de HEAD más exclusivamente los fragmentos de FR-020 autorizados.
4. NO sobrescribas ni restaures las versiones de trabajo de esos documentos.
5. NO incluyas ni descartes modificaciones de T019–T022.

ANTES DEL COMMIT:

6. Revisa git diff --cached --name-status y git diff --cached --check.
7. Comprueba que el índice contiene exactamente los siete archivos autorizados.
8. Revisa el diff preparado completo de tasks.md y quickstart.md y demuestra que no contiene cambios previos de US2.
9. Comprueba que los archivos de trabajo conservan todos los cambios anteriores que quedaron fuera del índice.
10. Si existe cualquier ambigüedad al seleccionar los fragmentos, detente sin hacer commit y explica el problema.

Solo si todas las comprobaciones anteriores pasan, crea el commit local con este mensaje:

feat(persona-a): cerrar la frontera temporal del turno (FR-020)

DESPUÉS DEL COMMIT:

11. Muestra el hash, los archivos incluidos y git status --short.
12. Confirma que las modificaciones pendientes de US2, los registros de prompts y los respaldos siguen intactos.
13. Comprueba que no quedan diferencias pendientes de FR-020 por haber preparado parcialmente los documentos.

PROHIBIDO:

- Push, pull, fetch, merge, rebase, reset, restore, clean o stash.
- Modificar archivos de B, C o D.
- Modificar PROMPTS_LLM.md.
- Implementar T022 o modificar modelo/rutas.py.
- Crear commits adicionales.

Detente al terminar. No avances a otra tarea sin mi autorización.
```

### P57 — Implementación de la decisión del cazador en T022

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Implementar y verificar la decisión del cazador con el contrato interno de T021.

```text
$speckit-implement

Continuemos con Cripta Parte II, Persona A, exclusivamente con T022: implementar la decisión del cazador.

FR-020 quedó confirmada en los commits locales 26be407 y 299079d. No modificar esa implementación.

ANTES DE PROGRAMAR:

1. Verifica la rama feature/motor-eventos y el estado de Git.
2. Revisa el PDF oficial de Cripta Parte II, especialmente §3.2.
3. Revisa spec.md, plan.md, tasks.md y la constitución de Spec Kit.
4. Lee modelo/rutas.py, tests/test_rutas_cazador.py y tests/test_decision_cazador.py.
5. Confirma los contratos existentes de T021 y las expectativas exactas de T020.
6. Identifica cualquier contradicción entre pruebas, documentos y requisitos oficiales antes de escribir código.

IMPLEMENTACIÓN AUTORIZADA:

- Crear exclusivamente modelo/cazador.py para la función de decisión del cazador definida en T022.
- Si el cazador está en la misma sala que el jugador, elegir atacar.
- En otro caso, utilizar la búsqueda de menor costo de T021.
- Respetar el rango del cazador.
- Elegir la primera dirección de la ruta mínima, aplicando el desempate oficial.
- Esperar si no existe una ruta válida dentro del rango.
- No consultar niebla de guerra.
- No modificar posiciones, puertas, agenda ni RNG durante la consulta de decisión.

VERIFICACIÓN:

1. Ejecuta tests/test_decision_cazador.py.
2. Ejecuta tests/test_rutas_cazador.py.
3. Ejecuta las 11 pruebas de frontera temporal y las 99 regresiones anteriores.
4. Comprueba que el resultado del cazador coincide con el costo real de las puertas.
5. Revisa git diff --check.
6. Presenta el diff completo del archivo nuevo y los resultados.

RESTRICCIONES:

- No modificar modelo/juego.py, modelo/eventos.py ni modelo/rutas.py sin autorización.
- No modificar archivos de B, C o D.
- No modificar PROMPTS_LLM.md.
- No incorporar main.
- No alterar los respaldos locales ni otros cambios pendientes.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- No avanzar a T023 ni otras tareas.

Si surge alguna incompatibilidad que requiera modificar otros archivos, detente antes de hacerlo.

Al finalizar, presenta los resultados y espera revisión antes de cualquier commit.
```

### P58 — Cierre documental de T020 y T022

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P34. **Uso:** Validar resultados, actualizar la evidencia local y proponer el alcance del futuro commit.

```text
$speckit-implement

T022 fue implementada en modelo/cazador.py y sus pruebas pasaron.

Autorizo exclusivamente cerrar documentalmente T022 y preparar su commit local, sin ejecutarlo todavía.

1. Revisa nuevamente el alcance exacto de T022 en tasks.md y su correspondencia con Parte II §3.2.
2. Verifica que tests/test_decision_cazador.py y modelo/cazador.py corresponden a T020 y T022 respectivamente.
3. Comprueba que las pruebas de decisión, rutas, FR-020 y regresiones anteriores siguen pasando.
4. Actualiza únicamente las casillas de T020 y T022 que puedan justificarse con los resultados reales, junto con su evidencia en quickstart.md.
5. Conserva íntegramente los demás cambios pendientes de US2 y los registros locales de prompts.
6. Identifica el conjunto exacto de archivos y fragmentos para un commit independiente de T020/T022, indicando cualquier dependencia todavía sin confirmar de T019/T021.
7. Revisa git diff --check.

No hagas git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.\
No modifiques código de producción adicional.\
No modifiques PROMPTS_LLM.md ni archivos de compañeros.\
No avances a T023 ni otras tareas.

Presenta el alcance propuesto del commit y esperá autorización.
```

### Pendientes de recuperación o incorporación tras el bloque 3

Quedan 15 solicitudes o continuaciones de las 39 identificadas en la auditoría: 13 posteriores a P58, incluida la solicitud de auditoría, y los dos mensajes con final incompleto entre P32 y P33 señalados en el bloque 2. Las autorizaciones de los bloques 1, 2 y 3 quedan para una etapa posterior y se cuentan aparte del inventario inicial. T051 sigue pendiente.

## Consolidación T051 — bloque 4

Se recuperan los diez mensajes enviados por Persona A inmediatamente después de P58. La fuente es el registro original de esta sesión de Codex. Las fechas se verificaron a partir de los timestamps de los mensajes, convertidos a America/Costa_Rica. El modelo exacto no está confirmado.

### P59 — Autorización del commit de T019/T021

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Confirmar por separado las rutas del cazador y sus pruebas antes del commit de decisión.

```text
Confirmo que debemos crear primero el commit de T019/T021 y después el de T020/T022.

Por ahora autorizo exclusivamente preparar y crear el commit local de T019/T021, sujeto a las verificaciones siguientes.

1. Confirma la rama feature/motor-eventos y que el índice está vacío.
2. Revisa las dependencias reales de tests/test_rutas_cazador.py y de buscar_ruta() en modelo/rutas.py.
3. Comprueba que el diff de modelo/rutas.py corresponde íntegramente a T021, sin incluir cambios de otras tareas.
4. Prepara exclusivamente:

- modelo/rutas.py: únicamente el diff de T021.
- tests/test_rutas_cazador.py: archivo completo de T019.
- specs/001-terreno-cazador/tasks.md: solo los fragmentos de T019/T021 que todavía no están en HEAD.
- specs/001-terreno-cazador/quickstart.md: solo las secciones de T019/T021 que todavía no están en HEAD.

5. Usa selección parcial del índice para los documentos compartidos. No sobrescribas los archivos de trabajo.
6. Antes de hacer commit, verifica:

- Que el índice contiene exactamente los cuatro archivos autorizados.
- Que no incluye fragmentos de T020/T022.
- Que no incluye P33/P34 ni registros de prompts.
- Que git diff --cached --check pasa.
- Que las pruebas de rutas pasan con las dependencias preparadas.

7. Si alguna dependencia necesaria para T019/T021 falta en HEAD o no se puede separar con seguridad, detente sin crear commit y explícala.
8. Solo si todas las comprobaciones pasan, crea el commit local:

feat(persona-a): implementar rutas del cazador (T019/T021)

9. Después muestra el hash, archivos incluidos, diff resumido y git status --short.
10. Confirma que modelo/cazador.py, tests/test_decision_cazador.py, los cambios documentales de T020/T022, los registros locales de prompts y los respaldos permanecen intactos.

No hagas push, pull, fetch, merge, rebase, reset, restore, clean ni stash.\
No modifiques PROMPTS_LLM.md ni archivos de B, C o D.\
No avances todavía con el commit T020/T022.

Si hay cualquier ambigüedad sobre el contenido del índice, detente y solicita revisión antes de crear el commit.
```

### P60 — Autorización del commit de T020/T022

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Confirmar localmente la decisión del cazador, su prueba y la evidencia documental autorizada.

```text
Autorizo preparar y crear exclusivamente el commit local de T020/T022, ahora que T019/T021 quedó confirmado en el commit 2ef477bd1058a2ab942a00d8ce915ab4627e868a.

Rama obligatoria: feature/motor-eventos.

ARCHIVOS COMPLETOS AUTORIZADOS:

- modelo/cazador.py
- tests/test_decision_cazador.py

DOCUMENTACIÓN CON SELECCIÓN PARCIAL:

- specs/001-terreno-cazador/tasks.md: únicamente las filas y evidencias correspondientes a T020/T022.
- specs/001-terreno-cazador/quickstart.md: únicamente las secciones «Preparación TDD de decisión del cazador» y «Cierre local de T020 y T022».

VERIFICACIONES:

1. Confirma que seguimos en feature/motor-eventos y que el índice está vacío.
2. Verifica que HEAD contiene buscar_ruta() y las dependencias necesarias de T021.
3. Prepara los dos archivos completos y únicamente los fragmentos documentales autorizados.
4. No sobrescribas las versiones de trabajo de tasks.md ni quickstart.md.
5. Revisa git diff --cached --name-status, git diff --cached --check y el diff preparado completo.
6. Comprueba que el índice contiene exactamente los cuatro archivos autorizados.
7. Ejecuta las pruebas de decisión y rutas con las dependencias preparadas. Confirma que la suite pasa sin depender de cambios no incluidos en HEAD.
8. Si hay fragmentos mezclados o alguna dependencia no confirmada, detente antes de crear el commit.

Solo si todo es correcto, crea este commit local:

feat(persona-a): implementar la decisión del cazador (T020/T022)

DESPUÉS:

9. Muestra el hash del commit y sus archivos incluidos.
10. Comprueba que no quedan diferencias pendientes de T020/T022.
11. Confirma que los registros locales de prompts, US2 restante, .idea/ y respaldos no fueron modificados.
12. Muestra git status --short.

PROHIBIDO:

- Push, pull, fetch, merge, rebase, reset, restore, clean o stash.
- Modificar PROMPTS_LLM.md.
- Modificar archivos de B, C o D.
- Implementar otras tareas o modificar producción adicionalmente.

Detente después de crear el commit. No avances a la siguiente tarea sin mi autorización.
```

### P61 — Revisión de la siguiente tarea pendiente

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Identificar el siguiente trabajo de Persona A a partir de sus dependencias y archivos.

```text
Continuemos con Cripta Parte II, Persona A.

El commit local 27c7a4d confirmó T020/T022, y el índice quedó vacío.

Por ahora realiza exclusivamente una revisión de solo lectura:

1. Confirma la rama feature/motor-eventos y el HEAD actual.
2. Revisa íntegramente specs/001-terreno-cazador/tasks.md.
3. Identifica cuál es la siguiente tarea pendiente de Persona A, respetando el orden y las dependencias de Spec Kit.
4. Indica el identificador exacto, la descripción literal de la tarea y sus criterios de aceptación.
5. Revisa qué dependencias ya están confirmadas en Git y cuáles siguen pendientes.
6. Determina qué archivos sería necesario modificar y si alguno pertenece a otro integrante.
7. Señala si Q1–Q3 o E-D-CAMBIOS impiden realizar la tarea.
8. Confirma que la siguiente tarea no requiere incorporar main ni modificar el trabajo de otros integrantes.

No modifiques ningún archivo.\
No ejecutes git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.\
No modifiques PROMPTS_LLM.md ni los registros locales.

Presenta el análisis y espera mi autorización antes de implementar la siguiente tarea.
```

### P62 — Pruebas de referencia de T026

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Contrastar la búsqueda de rutas con una referencia independiente sobre grafos sintéticos.

```text
$speckit-implement

Continuemos con Cripta Parte II, Persona A, exclusivamente con T026.

La revisión de dependencias confirmó que T023–T025 siguen bloqueadas por contratos externos. T026 depende únicamente de T021, ya confirmado en Git.

ANTES DE EDITAR:

1. Confirma la rama feature/motor-eventos y el HEAD 27c7a4deddf400be6038f8379b95f9434bb7a0ff.
2. Revisa la descripción literal de T026 en tasks.md.
3. Revisa Parte II §3.2, FR-008, FR-010, FR-014 y NFR-005.
4. Lee la implementación actual de buscar_ruta() y las pruebas existentes de tests/test_rutas_cazador.py.
5. Confirma que los cambios pueden limitarse al archivo de pruebas indicado.

IMPLEMENTACIÓN AUTORIZADA:

Amplía exclusivamente tests/test_rutas_cazador.py con pruebas de referencia independientes para comprobar T026.

- Utiliza grafos pequeños válidos construidos con los arreglos del proyecto.
- Implementa únicamente dentro de la suite de pruebas una referencia independiente mediante selección lineal o enumeración de caminos simples.
- Contrasta costo mínimo total y primer ID vecino contra buscar_ruta().
- Incluye casos con múltiples rutas empatadas y diferentes órdenes de enumeración.
- Comprueba que los resultados son deterministas y que las rutas respetan puertas abiertas y costos válidos.
- No reproduzcas el mismo algoritmo ni reutilices el heap de producción como referencia.
- No uses conocimiento de otros integrantes ni datos de la API real.

VERIFICACIÓN:

1. Ejecuta tests/test_rutas_cazador.py completo.
2. Ejecuta tests/test_decision_cazador.py.
3. Ejecuta las 11 pruebas de frontera temporal y las 99 regresiones anteriores.
4. Si aparece una diferencia entre la referencia independiente y buscar_ruta(), investiga la causa y detente antes de modificar producción.
5. Ejecuta git diff --check.
6. Muestra el diff exacto y los resultados.

RESTRICCIONES:

- No modificar modelo/rutas.py, modelo/cazador.py, modelo/juego.py ni modelo/eventos.py.
- No modificar otras pruebas ni documentos todavía.
- No modificar PROMPTS_LLM.md ni el registro local de prompts en esta etapa.
- No modificar archivos de B, C ni D.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar intactos los archivos de .idea/ y los respaldos locales.

Al finalizar, presenta las pruebas añadidas, las comparaciones realizadas y cualquier discrepancia encontrada.

No marques T026 como completada ni crees un commit todavía. Espera mi revisión y autorización.
```

### P63 — Cierre documental de T026

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Registrar la cobertura y los resultados de T026 y proponer el alcance del commit.

```text
$speckit-implement

La implementación de T026 fue revisada y sus 131 pruebas relevantes pasan.

Autorizo exclusivamente el cierre documental de T026 y la preparación de su commit local, sin ejecutarlo todavía.

1. Confirma la rama feature/motor-eventos y el estado del índice.
2. Revisa la descripción original de T026 y confirma que las dos pruebas añadidas satisfacen sus criterios de aceptación.
3. Marca únicamente T026 como completada en specs/001-terreno-cazador/tasks.md.
4. Añade en quickstart.md una evidencia breve y verificable de T026:
   - Enumeración independiente de caminos simples.
   - Seis rutas óptimas empatadas.
   - Diferentes órdenes de conexiones y salas.
   - Comparación de 144 pares ordenados.
   - Puertas cerradas y límites de costo.
   - Resultados: 12/12 rutas, 9/9 decisión, 11/11 FR-020 y 99/99 regresiones.
5. No marques T023, T024 ni T025 como completadas.
6. Verifica qué fragmentos de tasks.md y quickstart.md corresponden únicamente a T026.
7. Propón el conjunto exacto de archivos o fragmentos para un commit independiente:
   - tests/test_rutas_cazador.py
   - tasks.md, solamente T026.
   - quickstart.md, solamente evidencia de T026.
8. Ejecuta git diff --check y presenta el diff y el estado de Git.

RESTRICCIONES:

- No modificar producción ni otras pruebas.
- No modificar PROMPTS_LLM.md ni el registro local de prompts.
- No modificar archivos de B, C o D.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Preservar .idea/ y los respaldos locales.

Al finalizar, presenta el alcance exacto del commit propuesto y espera autorización.
```

### P64 — Autorización del commit de T026

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Confirmar localmente las pruebas de referencia y los fragmentos documentales revisados.

```text
Autorizo preparar y crear exclusivamente el commit local de T026 en feature/motor-eventos.

HEAD esperado antes del commit: 27c7a4deddf400be6038f8379b95f9434bb7a0ff.

ARCHIVO COMPLETO AUTORIZADO:

- tests/test_rutas_cazador.py: exclusivamente el diff de T026 ya revisado.

DOCUMENTACIÓN CON SELECCIÓN PARCIAL:

- specs/001-terreno-cazador/tasks.md: únicamente marcar T026 como completada.
- specs/001-terreno-cazador/quickstart.md: únicamente la sección «Validación local de T026».

ANTES DEL COMMIT:

1. Confirma la rama, HEAD y que el índice está vacío.
2. Comprueba que los cambios de tests/test_rutas_cazador.py corresponden exclusivamente a T026.
3. Prepara los tres archivos autorizados, usando selección parcial para tasks.md y quickstart.md.
4. No sobrescribas los archivos de trabajo ni incluyas cambios ajenos.
5. Revisa git diff --cached --name-status, git diff --cached --check y el diff preparado completo.
6. Comprueba que el índice contiene exactamente esos tres archivos.
7. Verifica que las pruebas de T026 siguen pasando y que no existen dependencias sin confirmar en HEAD.
8. Si detectas cambios ajenos, una dependencia faltante o una selección parcial insegura, detente antes de crear el commit.

Solo si las verificaciones pasan, crea el commit local:

test(persona-a): contrastar rutas con una referencia independiente (T026)

DESPUÉS DEL COMMIT:

9. Muestra el hash, los archivos incluidos y el estado de Git.
10. Confirma que no quedan diferencias pendientes de T026.
11. Verifica que los registros locales de prompts, .idea/ y los respaldos de puntajes permanecen intactos.
12. Mantén T023, T024 y T025 pendientes.

RESTRICCIONES:

- No hacer push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- No modificar PROMPTS_LLM.md.
- No modificar archivos de B, C o D.
- No implementar otras tareas.
- No crear commits adicionales.

Detente al finalizar y espera mi revisión.
```

### P65 — Publicación de cinco commits de Persona A

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Verificar el alcance y el hash remoto antes de publicar los cinco commits autorizados.

```text
Quiero respaldar los cinco commits locales de Persona A en GitHub.

PRIMERO, SOLO LECTURA:

1. Confirma que estamos en feature/motor-eventos.
2. Verifica que el índice esté vacío.
3. Compara la rama local con origin/feature/motor-eventos.
4. Comprueba que los cinco commits pendientes pertenecen únicamente al trabajo autorizado de Persona A.
5. Verifica que el remoto no haya avanzado desde nuestra última referencia, usando git ls-remote sin hacer fetch.
6. Comprueba que el push no incluiría archivos sin seguimiento, respaldos ni cambios sin commit.

Solo si todas las verificaciones pasan, autorizo ejecutar exclusivamente:

git push origin feature/motor-eventos

Si el remoto avanzó, hay divergencia o aparece cualquier cambio inesperado, detente sin publicar y explícame el problema.

No ejecutes pull, merge, rebase, reset, clean, stash ni force push. No modifiques main ni PROMPTS_LLM.md.

Después del push, informa el hash remoto y el estado de Git. No avances a otras tareas.
```

### P66 — Diagnóstico de tareas realizables sin contratos externos

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Clasificar las tareas pendientes y determinar cuál podía ejecutarse con los prerrequisitos confirmados.

```text
Continuemos con Cripta Parte II, Persona A.

Los cinco commits anteriores ya están publicados en origin/feature/motor-eventos. El último commit confirmado es ec34f4eddbfca0ff43dcabe001e8f7e0b607c1d4.

OBJETIVO:\
Identificar las siguientes tareas de Persona A que podamos completar sin depender de entregas pendientes de B, C o D.

REALIZA ÚNICAMENTE UNA REVISIÓN DE SOLO LECTURA:

1. Confirma la rama feature/motor-eventos, HEAD, estado de Git e índice.
2. Lee íntegramente specs/001-terreno-cazador/tasks.md, la especificación, el plan y los contratos de integración.
3. Identifica todas las tareas originales T001–T051 que siguen pendientes.
4. Clasifícalas en:
   - Realizables ahora con las dependencias confirmadas.
   - Bloqueadas por entregables de B.
   - Bloqueadas por entregables de C.
   - Bloqueadas por entregables de D.
   - Bloqueadas por Q1–Q3 u otras condiciones.
5. Para cada tarea realizable ahora, indica su identificador exacto, descripción, dependencias, archivos afectados y criterios de aceptación.
6. Señala cuál conviene realizar primero, respetando el orden y las dependencias de Spec Kit.
7. Identifica cualquier tarea que pueda preparar pruebas o documentación sin implementar todavía una integración externa.
8. No marques tareas pendientes como completadas ni inventes contratos o valores predeterminados.
9. Distingue las tareas verificadas localmente de las formalmente cerradas.

RESTRICCIONES:

- No modificar archivos.
- No modificar PROMPTS_LLM.md ni los registros locales de prompts.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar intactos .idea/, respaldos de puntajes y cualquier otro archivo local.

Al finalizar, presenta un resumen de las tareas realizables, los bloqueos y la siguiente tarea recomendada.

Espera mi autorización antes de implementar cualquier cambio.
```

### P67 — Prueba de localidad de T039

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Implementar y verificar la prueba de localidad con grafos sintéticos y observación por consulta.

```text
$speckit-implement

Continuemos con Cripta Parte II, Persona A, exclusivamente con T039: prueba de localidad de la búsqueda.

La revisión de dependencias confirmó que T021 y T026 están completadas y publicadas en feature/motor-eventos. T039 no requiere contratos pendientes con B, C o D.

ANTES DE EDITAR:

1. Confirma la rama feature/motor-eventos, HEAD ec34f4eddbfca0ff43dcabe001e8f7e0b607c1d4 y el estado de Git.
2. Revisa la descripción literal de T039 en tasks.md, el escenario P2, FR-008, FR-010, NFR-002 y NFR-005.
3. Revisa modelo/rutas.py, el fixture sintético y las pruebas existentes.
4. Comprueba qué métricas pueden observarse sin modificar código de producción.
5. Si no es posible medir la expansión, las asignaciones y la limpieza por consulta de forma fiable con las interfaces actuales, detente y explica la limitación antes de modificar producción.

IMPLEMENTACIÓN AUTORIZADA:

Crear exclusivamente tests/test_localidad_rutas.py para T039.

- Construye una región alcanzable fija desde el origen y un rango pequeño.
- Amplía progresivamente el mapa exterior manteniendo idéntica esa región.
- Compara las rutas devueltas: costo mínimo, primer vecino, dirección y costo del paso.
- Comprueba que el trabajo de consulta permanezca localizado y no crezca con el exterior del mapa.
- Separa explícitamente la construcción inicial del grafo y sus arreglos del costo por consulta.
- Utiliza métricas reproducibles y observables; no inventes contadores de expansión o asignación.
- No reutilices el mismo algoritmo de producción como referencia independiente.
- No presentes tiempos de unittest como si fueran mediciones oficiales de rendimiento.
- No dependas de API real ni de archivos de otros integrantes.

VERIFICACIÓN:

1. Ejecuta tests/test_localidad_rutas.py.
2. Ejecuta tests/test_rutas_cazador.py y tests/test_decision_cazador.py.
3. Ejecuta las 11 pruebas de FR-020 y las 99 regresiones anteriores.
4. Si aparece un fallo, investiga su causa y detente antes de modificar producción.
5. Ejecuta git diff --check.
6. Presenta las métricas observadas, los resultados de pruebas y el diff del archivo nuevo.

RESTRICCIONES:

- No modificar modelo/rutas.py ni ningún otro código de producción.
- No modificar otras pruebas o documentos en esta etapa.
- No modificar PROMPTS_LLM.md ni el registro local de prompts.
- No modificar archivos de B, C o D.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Preservar .idea/, respaldos y archivos pendientes.

No marques T039 como completada ni avances a T040 todavía.

Al finalizar, presenta la evidencia y espera mi revisión antes de cualquier commit.
```

### P68 — Revisión final y cierre documental de T039

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión, después de P58. **Uso:** Repetir las pruebas y registrar el resultado de localidad, manteniendo pendiente la medición oficial.

```text
La evidencia inicial de T039 es satisfactoria: 132 pruebas aprobadas y conteos constantes entre mapas de 6, 69 y 8.197 salas.

Autorizo exclusivamente la revisión final de T039 y, si todas las comprobaciones pasan, su cierre documental. No autorices todavía commit.

1. Revisa íntegramente tests/test_localidad_rutas.py, incluidas las 142 líneas nuevas.
2. Verifica que la construcción del grafo y de los arreglos auxiliares ocurre fuera del tramo instrumentado por consulta.
3. Confirma que los contadores son reproducibles y que la instrumentación no modifica el resultado de buscar_ruta().
4. Comprueba que los grafos cumplen el contrato válido de costos positivos, puertas y conexiones.
5. Confirma que la referencia independiente de caminos simples no reutiliza Dijkstra ni el heap de producción.
6. Comprueba que se distinguen correctamente las métricas de operaciones y el pico de memoria de tracemalloc, sin presentar este último como número de asignaciones.
7. Repite la prueba y comprueba los resultados junto con las 131 pruebas anteriores.
8. Si se confirma todo, marca únicamente T039 como completada en tasks.md y añade una evidencia breve en quickstart.md, indicando explícitamente que T046 sigue pendiente.
9. Ejecuta git diff --check y presenta el diff, los resultados y el alcance exacto de un futuro commit local de T039.

No modifiques producción, las demás pruebas, PROMPTS_LLM.md ni los registros locales de prompts.\
No modifiques archivos de otros integrantes ni incorpores main.\
No ejecutes git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.

Si detectas un problema en la prueba, detente y explícalo antes de corregirla. Espera mi autorización para cualquier cambio adicional.
```

### Pendientes de recuperación o incorporación tras el bloque 4

Quedan 5 solicitudes o continuaciones de las 39 identificadas en la auditoría:

- 3 mensajes íntegros posteriores a P68, en este orden: autorización del commit local de T039, publicación de ese commit y solicitud de auditoría del registro local de T051.
- 2 mensajes con final incompleto entre P32 y P33, señalados en el bloque 2. Siguen pendientes de una fuente íntegra.

Por separado, quedan por incorporar las 4 autorizaciones de los bloques 1–4, enviadas después de la solicitud de auditoría y fuera del inventario inicial. T051 sigue pendiente.

## Consolidación T051 — bloque 5

Se incorporan siete mensajes consecutivos enviados por Persona A después de P68. Los cuerpos proceden del registro original de esta sesión de Codex. Las fechas se verificaron con los timestamps de los mensajes, convertidos a America/Costa_Rica. El modelo exacto no está confirmado.

### P69 — Autorización del commit local de T039

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización. **Uso:** Confirmar localmente la prueba de localidad y los dos fragmentos documentales revisados.

```text
Autorizo preparar y crear exclusivamente el commit local de T039 en feature/motor-eventos.

HEAD esperado: ec34f4eddbfca0ff43dcabe001e8f7e0b607c1d4.

ARCHIVO COMPLETO AUTORIZADO:

- tests/test_localidad_rutas.py: archivo nuevo de 142 líneas, revisado y validado.

DOCUMENTACIÓN CON SELECCIÓN PARCIAL:

- specs/001-terreno-cazador/tasks.md: exclusivamente marcar T039 como completada.
- specs/001-terreno-cazador/quickstart.md: exclusivamente la sección «Validación local de T039».

ANTES DEL COMMIT:

1. Confirma rama, HEAD y que el índice está vacío.
2. Verifica que los tres archivos conservan exactamente los cambios revisados.
3. Prepara los tres archivos, usando selección parcial del índice para tasks.md y quickstart.md.
4. No sobrescribas los archivos de trabajo ni incorpores cambios de otras tareas.
5. Comprueba que el índice contiene exactamente los tres archivos autorizados.
6. Revisa git diff --cached --name-status, git diff --cached --check y el diff preparado completo.
7. Confirma que no hay dependencias de producción sin confirmar en HEAD.
8. Si existe alguna diferencia inesperada, detente antes del commit.

Solo si todo está correcto, crea el commit local:

test(persona-a): verificar localidad de rutas (T039)

DESPUÉS DEL COMMIT:

9. Muestra el hash y los archivos incluidos.
10. Confirma que no quedan diferencias pendientes de T039.
11. Muestra git status --short y comprueba que el índice quedó vacío.
12. Verifica que los registros locales de prompts, .idea/ y los respaldos siguen intactos.
13. Mantén T046 y las tareas bloqueadas por contratos externos pendientes.

PROHIBIDO:

- Push, pull, fetch, merge, rebase, reset, restore, clean o stash.
- Modificar PROMPTS_LLM.md.
- Modificar código de producción o archivos de otros integrantes.
- Crear otros commits o avanzar a T040.

Detente después del commit y espera mi revisión.
```

### P70 — Autorización de publicación de T039

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización. **Uso:** Verificar el hash remoto y publicar el único commit autorizado de T039.

```text
Quiero publicar únicamente el commit local de T039 en origin/feature/motor-eventos.

Antes de publicar:

1. Confirma que estamos en feature/motor-eventos.
2. Comprueba que HEAD es 21be43aee00f1a503a69d0104c5882ee26a4a85d.
3. Verifica que el índice está vacío y que existe exactamente un commit pendiente de push.
4. Comprueba con git ls-remote que la rama remota no avanzó desde la última referencia conocida.
5. Confirma que el commit pendiente contiene únicamente los tres archivos de T039.
6. Verifica que los cambios sin commit, .idea/ y respaldos no formarán parte del push.

Solo si todo coincide, ejecuta:

git push origin feature/motor-eventos

Si existe divergencia o alguna diferencia inesperada, detente sin publicar.

No hagas merge, pull, rebase, reset, clean, stash ni force push. No modifiques main, PROMPTS_LLM.md ni archivos locales.

Después informa el hash remoto y el estado de Git. No avances a otras tareas.
```

### P71 — Auditoría inicial del registro local de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Solicitud inicial. **Uso:** Inventariar los prompts documentados y faltantes y evaluar las fuentes disponibles.

```text
Continuemos con Cripta Parte II, Persona A.

La rama feature/motor-eventos está sincronizada con origin/feature/motor-eventos en el commit 21be43aee00f1a503a69d0104c5882ee26a4a85d.

Quiero avanzar con T051, exclusivamente mediante una auditoría de solo lectura del registro local de prompts.

1. Revisa la descripción literal de T051 en tasks.md y cualquier requisito aplicable del proyecto sobre la bitácora de uso de LLM.
2. Lee completo specs/001-terreno-cazador/prompts-registro-local.md y sus archivos complementarios de prompts.
3. Identifica las entradas P01 en adelante existentes, sin asumir que el registro termina en P34.
4. Comprueba qué solicitudes enviadas a Codex están documentadas, cuáles faltan y cuáles podrían estar duplicadas.
5. Distingue fecha verificable de fecha contextual, y no inventes timestamps ni modelos.
6. Identifica entradas que contengan accidentalmente respuestas de Codex, explicaciones o textos que no correspondan al prompt original.
7. Propón las correcciones mínimas para consolidar el registro local, sin tocar la bitácora compartida.
8. Informa si T051 podría cerrarse con las fuentes disponibles o qué evidencia falta.

RESTRICCIONES:

- Solo lectura. No modificar archivos ni casillas de tasks.md.
- No modificar PROMPTS_LLM.md.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar intactos .idea/, respaldos y cualquier otro archivo local.

Presenta un informe con entradas verificadas, faltantes, duplicados y recomendaciones. Espera mi autorización antes de modificar el registro.
```

### P72 — Autorización del bloque 1 de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización y continuación. **Uso:** Recuperar nueve solicitudes intercaladas entre P20 y P30.

```text
Autorizo continuar con T051, exclusivamente mediante la consolidación del registro local de Persona A.

El análisis identificó P01–P34 y 39 solicitudes o continuaciones posiblemente faltantes.

PRIMERA ETAPA AUTORIZADA:

1. Conserva íntegramente P01–P34, sus identificadores y los tres anexos originales.
2. Recupera únicamente los textos literales verificables de las solicitudes faltantes.
3. Trabaja por bloques de máximo 10 solicitudes para facilitar la revisión.
4. Comienza con las solicitudes faltantes entre P20–P21, P22–P23 y P29–P30.
5. Incorpora cada mensaje recuperado con un identificador único, fecha verificable o contextual, herramienta/modelo conocido y explicación breve de su uso.
6. Conserva la secuencia histórica real. Como P01–P34 ya existen, puedes utilizar identificadores nuevos y un índice cronológico que muestre la ubicación original de cada entrada, sin renumerar ni alterar las anteriores.
7. No inventes prompts, respuestas, fechas, modelos ni finales de textos incompletos.
8. Cuando no exista una fuente íntegra, registra la ausencia en una sección de pendientes, sin presentarla como un prompt completo.
9. Diferencia solicitudes realmente enviadas a Codex de mensajes de planificación que nunca se enviaron.
10. No dupliques textos ya registrados.

ANTES DE FINALIZAR ESTA ETAPA:

- Muestra las entradas nuevas con su identificador y procedencia.
- Indica cuántas solicitudes se recuperaron íntegramente y cuántas siguen pendientes.
- Verifica que P01–P34 y los anexos permanecen intactos.
- Ejecuta git diff --check.
- No marques T051 como completada.

RESTRICCIONES:

- Modificar únicamente specs/001-terreno-cazador/prompts-registro-local.md.
- No modificar PROMPTS_LLM.md, tasks.md ni otros documentos.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- No modificar código de producción ni pruebas.
- Conservar .idea/ y respaldos.

Detente después del primer bloque para revisar los resultados antes de continuar.
```

### P73 — Autorización del bloque 2 de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización y continuación. **Uso:** Recuperar las solicitudes entre P32 y P33 y cotejar los dos finales truncados.

```text
La incorporación de P35–P43 queda aceptada para continuar con T051.

Autorizo exclusivamente el siguiente bloque de consolidación del registro local de Persona A.

1. Trabaja con las solicitudes faltantes situadas entre P32 y P33, respetando su orden histórico.
2. Incorpora únicamente los textos íntegros y verificables de solicitudes realmente enviadas a Codex.
3. Utiliza identificadores nuevos a partir de P44, sin renumerar ni modificar P01–P43.
4. Conserva las fechas verificables o contextuales y no inventes horas ni modelos.
5. Mantén la indicación de la posición histórica de cada entrada en el índice cronológico.
6. Para los dos mensajes cuyo final parece truncado, primero intenta cotejarlos con la fuente original disponible. Si no puedes recuperar el final exacto, no los registres como prompts íntegros; mantenlos señalados como pendientes.
7. No dupliques prompts ya registrados ni copies respuestas completas de Codex como si fueran solicitudes.
8. Añade únicamente las solicitudes de este bloque que puedan verificarse y detente después.

VERIFICACIONES:

- Confirma que P01–P43 y los anexos permanecen intactos.
- Actualiza el inventario de pendientes con el número real restante.
- Ejecuta git diff --check.
- Mantén T051 sin completar.

RESTRICCIONES:

- Modificar exclusivamente specs/001-terreno-cazador/prompts-registro-local.md.
- No modificar PROMPTS_LLM.md, tasks.md ni quickstart.md.
- No modificar código ni pruebas.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar todos los archivos locales y respaldos.

Presenta las entradas añadidas, su procedencia y los textos que hayan quedado pendientes de recuperar. Espera mi revisión antes de continuar.
```

### P74 — Autorización del bloque 3 de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización y continuación. **Uso:** Recuperar las primeras diez solicitudes posteriores a P34.

```text
La incorporación de P44–P48 queda aceptada para continuar con T051.

Autorizo exclusivamente el siguiente bloque de recuperación de solicitudes posteriores a P34, con un máximo de 10 entradas nuevas.

1. Conserva íntegramente P01–P48 y los tres anexos.
2. Recupera, en orden de envío, las primeras solicitudes posteriores a P34 que puedan verificarse literalmente en la sesión original de Codex.
3. Asigna identificadores nuevos a partir de P49 sin renumerar los existentes.
4. Incluye fecha verificable o contextual, herramienta/modelo y una nota breve de uso.
5. Distingue el texto realmente enviado de las respuestas de Codex.
6. No completes por inferencia los dos mensajes truncados entre P32 y P33; consérvalos pendientes.
7. Actualiza el índice cronológico y el inventario de solicitudes pendientes.
8. No dupliques entradas ya registradas ni incorpores mensajes que solamente fueron propuestos pero nunca enviados.

VERIFICACIONES:

- Confirma que las entradas P01–P48 y los anexos no sufrieron alteraciones.
- Ejecuta git diff --check.
- Mantén T051 pendiente.
- Presenta el listado de entradas nuevas, su procedencia y el número de solicitudes restantes.

RESTRICCIONES:

- Modificar exclusivamente specs/001-terreno-cazador/prompts-registro-local.md.
- No modificar PROMPTS_LLM.md, tasks.md ni quickstart.md.
- No modificar código de producción ni pruebas.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar intactos los archivos locales y respaldos.

Detente después de este bloque y espera mi revisión.
```

### P75 — Autorización del bloque 4 de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización y continuación. **Uso:** Recuperar las diez solicitudes inmediatamente posteriores a P58.

```text
La incorporación de P49–P58 queda aceptada para continuar con T051.

Autorizo exclusivamente el siguiente bloque de consolidación del registro local de Persona A, con un máximo de diez solicitudes posteriores a P58.

1. Confirma la rama feature/motor-eventos y conserva íntegramente P01–P58 y los tres anexos originales.
2. Recupera las siguientes solicitudes realmente enviadas a Codex, en su orden histórico, utilizando el registro original de la sesión como fuente.
3. Asigna identificadores nuevos a partir de P59, sin renumerar las entradas anteriores.
4. Registra el texto literal íntegro, la fecha contextual o verificable, la herramienta/modelo conocido y una nota breve sobre el uso.
5. Actualiza el índice cronológico, manteniendo la posición histórica correcta.
6. No inventes finales, fechas, modelos ni contenido.
7. Mantén pendientes los dos mensajes truncados entre P32 y P33 hasta encontrar una fuente íntegra.
8. Distingue los pendientes del inventario inicial de las solicitudes adicionales enviadas durante esta auditoría.
9. No dupliques entradas ni incluyas respuestas de Codex como si fueran prompts.

VERIFICACIONES:

- Confirma que P01–P58 y los anexos no cambiaron.
- Ejecuta git diff --check.
- Actualiza el número real de pendientes.
- Mantén T051 sin completar.

RESTRICCIONES:

- Modificar exclusivamente specs/001-terreno-cazador/prompts-registro-local.md.
- No modificar PROMPTS_LLM.md, tasks.md ni quickstart.md.
- No modificar producción ni pruebas.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Conservar intactos .idea/ y los respaldos locales.

Detente después de este bloque. Presenta las entradas nuevas, la procedencia de sus textos y las solicitudes pendientes antes de continuar.
```

### Pendientes de recuperación o incorporación tras el bloque 5

Del inventario inicial de 39 solicitudes, quedan 2 mensajes con final incompleto, ambos entre P32 y P33. El nuevo cotejo con el registro de la sesión devuelve los mismos finales disponibles que el bloque 2: `Presenta únicamente e` y `no tiene cambios locales pendient`. Siguen pendientes de una fuente íntegra.

Por separado, queda por incorporar la autorización del bloque 5, enviada después de P75 y fuera del inventario inicial. Las autorizaciones de los bloques 1–4 están registradas como P72–P75. T051 sigue pendiente.

## Corte documental en P77

### P76 — Autorización del bloque 5 de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Autorización y continuación. **Uso:** Recuperar los tres mensajes finales del inventario inicial y las cuatro autorizaciones de consolidación anteriores.

```text
La incorporación de P59–P68 queda aceptada para continuar con T051.

Autorizo exclusivamente el siguiente bloque de consolidación del registro local de Persona A.

PRIMERA PRIORIDAD:

Recupera y registra, si sus textos originales están íntegros y verificables:

1. La autorización del commit local de T039.
2. La autorización de publicación de T039.
3. La solicitud inicial de auditoría de T051.
4. Las cuatro autorizaciones posteriores correspondientes a los bloques 1–4 de consolidación.

Asigna nuevos identificadores a partir de P69, conservando su posición histórica en el índice y sin renumerar P01–P68.

CONDICIONES:

- Conserva íntegramente los textos realmente enviados a Codex.
- Registra fecha verificable o contextual y herramienta/modelo conocido.
- Incluye una nota breve sobre el uso.
- Distingue prompts originales de autorizaciones y continuaciones.
- No dupliques entradas existentes.
- No inventes contenido, fechas, modelos ni resultados.

SEGUNDA PRIORIDAD, SOLO LECTURA:

Revisa nuevamente los dos mensajes truncados entre P32 y P33. Si existe una fuente íntegra verificable, identifica sus finales exactos, pero no incorpores ni reconstruyas esos mensajes todavía.

VERIFICACIONES:

- Comprueba que P01–P68 y los tres anexos permanecen intactos.
- Actualiza el índice y el inventario de pendientes.
- Ejecuta git diff --check.
- Mantén T051 sin completar.

RESTRICCIONES:

- Modificar exclusivamente specs/001-terreno-cazador/prompts-registro-local.md.
- No modificar PROMPTS_LLM.md, tasks.md ni quickstart.md.
- No modificar código de producción ni pruebas.
- No incorporar main ni otras ramas.
- No ejecutar git add, commit, push, pull, fetch, merge, rebase, reset, restore, clean ni stash.
- Preservar intactos .idea/ y los respaldos locales.

Detente después de este bloque y presenta las entradas añadidas, las fuentes utilizadas y los pendientes reales antes de continuar.
```

### P77 — Solicitud de auditoría final de T051

**Fecha verificada:** 2026-11-07, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Procedencia:** mensaje de Persona A en el registro original de esta sesión. **Tipo:** Solicitud de revisión. **Uso:** Cotejar el índice, los cuerpos originales y los vacíos históricos para determinar cómo cerrar la consolidación local.

```text
La incorporación de P69–P75 queda aceptada para continuar con T051.

Antes de seguir agregando entradas, realiza exclusivamente una auditoría final de solo lectura.

1. Verifica que P01–P75 y los tres anexos contienen los textos previamente registrados sin alteraciones.
2. Revisa el índice cronológico completo y comprueba que cada entrada aparece una sola vez.
3. Identifica con precisión los dos mensajes incompletos entre P32 y P33 y registra qué parte literal está verificada.
4. Comprueba si existe una fuente original íntegra para esos mensajes. No reconstruyas finales mediante suposiciones.
5. Identifica la autorización del bloque 5 como solicitud posterior pendiente y cualquier otro mensaje realmente enviado a Codex hasta el momento de esta auditoría.
6. Distingue las omisiones históricas de los prompts nuevos que se seguirán generando durante el desarrollo.
7. Revisa el criterio literal de cierre de T051 y determina si permite declarar explícitamente los vacíos documentales o exige recuperar todos los textos.
8. Propón el procedimiento mínimo para mantener actualizado el registro sin reabrir repetidamente todo el inventario.

No modifiques ningún archivo, no marques T051 y no ejecutes operaciones Git de escritura.

No modifiques PROMPTS_LLM.md ni incorpores main.

Presenta el resultado y una recomendación concreta sobre cómo cerrar T051 de forma verificable.
```

### Vacíos históricos

Los siguientes fragmentos literales se cotejaron con los mensajes de la sesión original. La fuente disponible termina en el último carácter de cada bloque. Los finales siguen pendientes de recuperación.

#### Posponer la incorporación a la bitácora compartida

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Estado:** fragmento literal, final ausente.

```text
Antes de modificar PROMPTS_LLM.md, quiero ajustar la estrategia porque mis compañeros continuarán agregando prompts a main diariamente.

Por ahora NO incorpores P01–P32 al archivo compartido.

Conserva íntegramente prompts-registro-local.md y los registros complementarios como fuente de Persona A.

El objetivo es evitar mantener dos versiones divergentes de PROMPTS_LLM.md durante varios días.

1. Revisa el estado actual del archivo, incluyendo las 19 líneas de main que ya incorporaste.
2. Recomienda cómo dejarlo sin cambios propios pendientes, sin perder ni modificar ningún archivo ajeno o de US2.
3. Diseña un procedimiento para incorporar los prompts de A sobre la versión más reciente de main justo antes de su integración.
4. Explica cómo detectar y evitar duplicados de entradas ya publicadas.
5. No elimines ni modifiques PROMPTS_LLM.md sin autorización específica.
6. No ejecutes reset, restore, checkout, merge, rebase, pull, commit ni push.

Presenta únicamente e
```

#### Autorizar la reversión local de las 19 líneas

**Fecha verificada:** 2026-11-06, America/Costa_Rica. **Herramienta:** aplicación Codex; modelo exacto no confirmado. **Estado:** fragmento literal, final ausente.

```text
Autorizo exclusivamente revertir la incorporación local pendiente de origin/main en PROMPTS_LLM.md.

Antes de editar:

1. Confirma que estamos en feature/motor-eventos.
2. Comprueba que PROMPTS_LLM.md tiene únicamente el bloque de 19 líneas incorporado desde origin/main y las diferencias de líneas vacías ya identificadas.
3. Verifica que no existan otros cambios locales en ese archivo que deban conservarse.

Si todo coincide:

- Restaura exclusivamente PROMPTS_LLM.md para que sea idéntico a su versión en HEAD de feature/motor-eventos.
- No modifiques ningún otro archivo.
- No borres ni alteres prompts-registro-local.md ni los registros complementarios.
- Conserva intactos el código, las pruebas y la documentación pendiente de US2.

Después comprueba:

1. git diff -- PROMPTS_LLM.md debe estar vacío.
2. git status debe conservar los demás cambios locales existentes.
3. No se debe perder ninguna entrada de Persona A.

No ejecutes merge, pull, fetch, rebase, reset, clean, stash, commit ni push.

Al finalizar, informa exactamente qué se retiró y confirma que PROMPTS_LLM.md no tiene cambios locales pendient
```

### Mantenimiento posterior al corte

La consolidación local se cierra con 77 entradas íntegras hasta P77. Los dos vacíos históricos quedan abiertos para recuperación si aparece una fuente íntegra. La autorización del cierre documental se envió después de P77 y queda pendiente para el siguiente mantenimiento.

En cada mantenimiento se cotejan los mensajes nuevos desde el último corte, se conserva su texto literal y se añade una sola fila por identificador al índice. Se comprueba que la fila apunta al cuerpo o al anexo y se anota el nuevo corte. El traslado a PROMPTS_LLM.md requiere autorización separada.
