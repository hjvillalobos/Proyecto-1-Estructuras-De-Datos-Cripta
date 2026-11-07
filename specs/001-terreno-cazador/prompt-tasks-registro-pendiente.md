# Registro pendiente — generación de Tasks

- **Fecha:** 2026-11-02, America/Costa_Rica.
- **Herramienta:** aplicación Codex; modelo exacto no confirmado.
- **Uso:** generar únicamente tasks.md provisional condicionado para Persona A, con requisitos/escenarios, dependencias externas y separación de base/experimentos. No ejecutar tareas.
- **Estado:** pendiente de incorporación autorizada a PROMPTS_LLM.md sin modificar entradas anteriores. No se modificó ese archivo compartido.

## Prompt íntegro

$speckit-tasks

Genera `tasks.md` para la funcionalidad `001-terreno-cazador`, correspondiente a la Persona A de Cripta Parte II.

Antes de comenzar, lee la constitución vigente, `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/integracion.md` y `quickstart.md`.

Utiliza únicamente los requisitos confirmados y el diseño provisional documentado.

**Organización de tareas:**

1. Divide la implementación en tareas pequeñas, verificables y ordenadas por dependencias.
2. Incluye la integración de costos variables de movimiento para todos los actores.
3. Incluye la búsqueda de rutas óptimas del cazador, el desempate por menor ID y el respeto del rango.
4. Incluye invalidación de rutas, determinismo y compatibilidad con el motor de eventos existente.
5. Incluye los casos T1–T7, regresiones de Parte I y mediciones de rendimiento.
6. Distingue claramente la implementación base de los experimentos comparativos. No conviertas alternativas experimentales en funcionalidades obligatorias.
7. Vincula cada tarea con los requisitos FR/NFR y escenarios correspondientes.
8. Incluye tareas de documentación de decisiones y registro de mediciones reales.

**Dependencias pendientes:**

- Q1: rango y validación, pendiente de B.
- Q2: costos inválidos o asimétricos, pendiente de B.
- Q3: referencia y posibles enmiendas de rendimiento.
- Contratos con C y D pendientes de coordinación.

Las tareas afectadas por estos puntos deben identificarse como bloqueadas o condicionadas, sin inventar respuestas.

**Protección del trabajo compartido:**

- Genera o modifica únicamente documentos dentro de `specs/001-terreno-cazador/`.
- No modifiques código Python, constitución, interfaz ni archivos de B, C o D.
- No modifiques `PROMPTS_LLM.md`; conserva el prompt íntegro para registrarlo posteriormente.
- Trabaja en la rama `feature/motor-eventos`.
- No crees ni cambies ramas.
- No ejecutes commits, push, pull, fetch, merge, rebase ni reset.
- Si la habilidad necesita modificar archivos fuera de la carpeta autorizada, detente y solicita autorización.

Genera exclusivamente las tareas documentales. No ejecutes ninguna tarea de implementación ni avances a Analyze o Implement.

Al finalizar, resume la cantidad de tareas, las dependencias pendientes y los archivos modificados.
