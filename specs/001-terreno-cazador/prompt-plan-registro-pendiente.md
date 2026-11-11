# Registro pendiente del prompt de Plan

- **Fecha:** 2026-11-02, America/Costa_Rica.
- **Herramienta:** aplicación Codex; modelo exacto no confirmado.
- **Uso:** preparar exclusivamente plan técnico provisional y documentos asociados de Persona A, manteniendo Q1–Q3 pendientes y sin cambios de código o configuración compartida.
- **Estado:** traslado a PROMPTS_LLM.md pendiente de autorización; no se modifican sus entradas. La solicitud siguiente se conserva textual, no como resumen. La habilidad adjunta es speckit-plan, ya instalada en el repositorio.

## Prompt íntegro

$speckit-plan

Continúa la planificación técnica de Cripta Parte II para la Persona A, funcionalidad `001-terreno-cazador`.

Antes de comenzar, lee la constitución vigente `.specify/memory/constitution.md`, la especificación `specs/001-terreno-cazador/spec.md` y los enunciados oficiales de Parte I y Parte II.

La primera ronda de Clarify terminó, pero Q1 (dominio y validación de rango), Q2 (costos inválidos y asimétricos) y Q3 (cripta de referencia y posibles enmiendas) permanecen pendientes. No inventes respuestas ni marques esas preguntas como resueltas.

**Objetivo:** generar un plan técnico provisional, documentando las decisiones que sí pueden fundamentarse con los requisitos confirmados y diferenciando claramente las dependencias externas.

Durante Plan:

1. Evalúa alternativas de estructuras de datos propias para representar y recorrer rutas de costo mínimo, incluyendo complejidad temporal y espacial.
2. Analiza búsquedas individuales y compartidas para múltiples cazadores, respetando que las consultas de rango pequeño no deben procesar innecesariamente toda la cripta.
3. Estudia alternativas de reutilización e invalidación de rutas frente a cambios de puertas, posición del jugador y otros eventos relevantes.
4. Justifica cómo asegurar el desempate por menor ID de la primera sala vecina entre rutas óptimas.
5. Revisa el motor y la agenda de eventos existentes para conservar determinismo, cancelaciones y reprogramación.
6. Define contratos de integración propuestos con B, C y D, sin modificar los módulos que les corresponden.
7. Diseña las pruebas T1–T7, regresiones de Parte I y mediciones obligatorias de rendimiento, sin afirmar resultados no ejecutados.
8. Respeta todas las prohibiciones académicas y la separación MVC.

**Restricciones sobre archivos:**

- Puedes crear o actualizar únicamente documentos técnicos dentro de `specs/001-terreno-cazador/`, incluidos `plan.md`, `research.md`, `data-model.md` y los artefactos que la habilidad requiera dentro de esa carpeta.
- Conserva `.specify/feature.json` apuntando a esta funcionalidad, sin versionarlo.
- No modifiques código Python, constitución, archivos de B, C o D, interfaz gráfica ni recursos visuales.
- No cambies la rama `feature/motor-eventos`.
- No ejecutes commits, push, pull, fetch, merge, rebase ni reset.
- No modifiques todavía `PROMPTS_LLM.md`; prepara el registro íntegro de este prompt dentro de la documentación de mi funcionalidad.
- Si la habilidad necesita escribir fuera de los archivos autorizados, detente y solicita aprobación antes de hacerlo.

**Resultado esperado:**

Genera el plan y sus documentos asociados según la habilidad, marcándolos como provisionales donde dependan de Q1–Q3.

Al finalizar, informa los archivos creados o modificados, las decisiones técnicas propuestas, sus alternativas y justificaciones, los acuerdos pendientes con los compañeros y cualquier bloqueo para avanzar a Tasks.

Ejecuta exclusivamente Plan. No avances a Tasks, Analyze ni Implement sin mi autorización.
