# Entrada pendiente para PROMPTS_LLM.md

- **Fecha:** 2026-11-01 (America/Costa_Rica).
- **Herramienta/modelo:** aplicación Codex; modelo exacto no confirmado.
- **Propósito/uso:** generar exclusivamente el borrador Specify de 001-terreno-cazador y su checklist, manteniendo rama, constitución, código y documentación compartida intactos. Documentar ambigüedades para Clarify posterior.
- **Estado:** pendiente de incorporación autorizada a PROMPTS_LLM.md, sin sustituir entradas anteriores. Este archivo conserva la solicitud textual, no solo un resumen.

## Autorización posterior — texto íntegro

Autorizo crear `.specify/feature.json` como excepción específica para ejecutar la fase `$speckit-specify`.

Condiciones:

1. Su contenido debe apuntar exclusivamente a `specs/001-terreno-cazador`.
2. Puedes crear los documentos de especificación y checklist únicamente dentro de `specs/001-terreno-cazador/`.
3. No modifiques ningún otro archivo de `.specify/`, especialmente la constitución, scripts, plantillas o configuración compartida.
4. No modifiques código Python ni archivos de mis compañeros.
5. No modifiques `PROMPTS_LLM.md` todavía. Conserva el texto del prompt para su registro posterior.
6. No crees ni cambies ramas. Conserva `feature/motor-eventos`.
7. No ejecutes commits, push, pull, fetch, merge, rebase ni reset.
8. Si encuentras otro archivo obligatorio fuera de estas rutas, detente y solicita autorización.
9. Ejecuta exclusivamente la fase Specify. No avances a Clarify, Plan, Tasks, Analyze ni Implement.

Al finalizar, muestra los archivos creados, resume los requisitos documentados y confirma que no modificaste otros archivos.

También indícame si `.specify/feature.json` debe mantenerse local o versionarse, teniendo en cuenta que los otros integrantes desarrollarán funcionalidades diferentes en sus propias ramas. No lo agregues a Git automáticamente.

## Solicitud original — texto íntegro


$speckit-specify

Necesito crear la primera especificación funcional de **Cripta Parte II**, correspondiente a la **Persona A: Terreno, cazador y validez de rutas**, con el identificador propuesto `001-terreno-cazador`.

Ya revisamos los tres documentos adjuntos:
1. Enunciado oficial de Cripta Parte I.
2. Enunciado oficial de Cripta Parte II.
3. Documento de división de trabajo del equipo.

Utiliza estos documentos como fuentes, junto con la constitución vigente `.specify/memory/constitution.md`, versión 1.1.0.

Los enunciados oficiales tienen prioridad sobre el documento de reparto. Las reglas de Parte I siguen vigentes salvo cuando Parte II las modifica expresamente.

## 1. Alcance de la funcionalidad

### Terreno y costos de movimiento

- Cada salida entre salas puede declarar un costo de movimiento.
- Si el campo `costo` está ausente, su valor es 100.
- Si está presente, debe ser un entero mayor o igual a 1.
- Los costos de una conexión deben ser iguales en ambos sentidos.
- Los costos variables se aplican al jugador y a todos los enemigos.
- Las demás acciones conservan los costos establecidos en Parte I.

La fórmula oficial del profesor para programar la siguiente acción es:

`intervalo = max(1, costo * 100 // velocidad)`

`tiempo_siguiente = reloj_actual + intervalo`

Esta fórmula proviene de la sección 2.3 de Cripta Parte I. Debe conservarse, aplicando el costo real de la salida cuando la acción sea un movimiento.

También debe mantenerse la regla de reprogramación cuando cambia la velocidad de un actor mientras tiene una acción pendiente.

### Nuevo comportamiento: cazador

- Si el cazador comparte sala con el jugador, debe atacar.
- En caso contrario, debe buscar una ruta hacia la sala actual del jugador que minimice el costo total de movimiento.
- Solo puede considerar puertas realmente abiertas en ese momento.
- Utiliza el esqueleto completo de la cripta y el estado real de sus puertas.
- No depende de la niebla de guerra, del conocimiento del jugador ni del contenido descargado.
- Si no existe una ruta o el costo mínimo supera su rango, debe esperar con costo 100.
- Si el costo mínimo es igual a su rango, puede desplazarse.
- Si existe una ruta válida, debe avanzar solamente un paso y pagar el costo de la salida atravesada.
- Cuando varios primeros pasos permiten obtener el mismo costo mínimo, debe escoger la sala vecina con menor ID.
- El cazador no abre puertas cerradas.

### Validez y reutilización de rutas

- Cada decisión del cazador debe ser equivalente a calcular nuevamente la ruta óptima desde cero en ese instante.
- Considerar los cambios relevantes de puertas, posición del jugador, movimiento de actores, muertes, velocidad y demás eventos que puedan afectar la decisión o su programación.
- No asumir que absolutamente todos los eventos invalidan una ruta.
- Las búsquedas con rangos pequeños deben limitar el trabajo a la región pertinente, sin procesar innecesariamente toda la cripta.
- Las decisiones deben ser deterministas y reproducibles.

### Compatibilidad con Parte I

Conservar las reglas existentes de:

- Reloj virtual y desempate de eventos por tiempo y número de secuencia.
- Cancelación y reprogramación de eventos.
- Activación de enemigos al entrar el jugador a una sala.
- Puertas, llaves y cierres automáticos.
- Efectos temporales, cambios de velocidad y trampas.
- Comportamientos de guardianes, errantes y rastreadores.
- Reproducción determinista con la misma semilla, versión de cripta y acciones.
- Separación MVC y ausencia de dependencias de la interfaz o HTTP dentro del motor.

Los errantes y rastreadores deben conservar sus decisiones de movimiento, aplicando los nuevos costos temporales de las salidas.

## 2. Escenarios de aceptación obligatorios

Incluye los siete casos T1–T7 del documento de reparto, vinculándolos con los requisitos oficiales de Parte II:

- T1: Sin ruta abierta, el cazador espera con costo 100.
- T2: Si la ruta mínima supera el rango, espera con costo 100.
- T3: Prefiere una ruta de menor costo aunque atraviese más salas.
- T4: Ante varios primeros pasos óptimos, elige la vecina de menor ID.
- T5: Si una puerta se cierra entre turnos, decide correctamente según el estado actual.
- T6: Con velocidad alta y una salida de costo 1, el intervalo mínimo es 1.
- T7: Si cambia la velocidad durante una acción costosa programada, escala correctamente el tiempo restante conforme a Parte I y utiliza una nueva secuencia.

Añade los demás escenarios necesarios que estén respaldados por los enunciados, especialmente casos límite y requisitos de rendimiento.

## 3. Restricciones académicas

- Lee y cumple la constitución vigente; no la modifiques.
- La especificación debe describir QUÉ debe hacer el sistema, no CÓMO implementarlo.
- No selecciones todavía algoritmos, estructuras de datos, clases, módulos ni diseños técnicos. Esas decisiones corresponden a Plan.
- Define requisitos funcionales y no funcionales verificables y numerados.
- Mantén trazabilidad entre requisitos y escenarios de aceptación.
- Respeta las restricciones sobre estructuras de datos propias, determinismo y rendimiento.
- No inventes valores faltantes de rango ni políticas para datos inconsistentes. Documenta las ambigüedades para Clarify.
- Usa los límites de rendimiento establecidos por los enunciados sin afirmar resultados que aún no se hayan medido.

## 4. Límites de responsabilidad de la Persona A

Mis principales archivos de implementación, para fases posteriores, son:

- `modelo/juego.py`: únicamente la lógica del motor correspondiente a A.
- `modelo/eventos.py`: agenda y programación de eventos.
- `modelo/efectos.py`: integración de efectos que corresponda a A.

Los posibles módulos de rutas y cazador deberán justificarse posteriormente durante Plan.

No considero estos archivos propiedad exclusiva de A. Deben conservarse las funciones y contratos compartidos.

Los componentes de B, C y D son únicamente de consulta. No modifiques sus archivos, incluidas las partes compartidas de inventario, historial, datos, snapshots, controlador o interfaz.

Si detectas que falta una clase, función, contrato o dato de mis compañeros, informa qué falta, quién es responsable y cómo afecta mi trabajo. No lo implementes sin autorización.

No modifiques imágenes, recursos visuales, sonidos, animaciones ni la interfaz gráfica. Si alguna funcionalidad nueva necesita un recurso visual, notifícamelo antes.

## 5. Protección de Git y archivos

- Trabaja únicamente en la rama existente `feature/motor-eventos`.
- No crees ni cambies ramas, aunque la habilidad sugiera hacerlo automáticamente.
- No ejecutes `git add`, `commit`, `push`, `pull`, `fetch`, `merge`, `rebase` ni `reset`.
- No modifiques archivos de otros integrantes.
- No incluyas `.idea/`, archivos de respaldo ni datos locales sin seguimiento.
- Durante esta fase, crea o modifica únicamente archivos dentro de `specs/001-terreno-cazador/`.
- Si el identificador ya está ocupado o la habilidad no puede trabajar en la rama actual, detente y avísame antes de crear nada.
- Si la habilidad requiere escribir fuera de esa carpeta, detente y solicita mi autorización.
- No modifiques por ahora `PROMPTS_LLM.md`, porque es compartido. Prepara una entrada con el texto íntegro de este prompt, fecha, herramienta y propósito, para incorporarla posteriormente sin perder el registro obligatorio.
- No modifiques código Python ni configuraciones compartidas.

## 6. Resultado esperado

Ejecuta exclusivamente la fase Specify y genera, si la habilidad lo permite bajo estas restricciones:

- `specs/001-terreno-cazador/spec.md`
- El checklist de calidad correspondiente dentro de esa carpeta.

Al finalizar, informa:

1. Qué archivos creaste o modificaste.
2. Qué requisitos funcionales y escenarios de aceptación quedaron documentados.
3. Qué ambigüedades deben resolverse durante Clarify.
4. Qué dependencias identificaste con B, C y D.
5. Si se respetaron todos los límites de archivos y Git.

No avances a Clarify, Plan, Tasks, Analyze ni Implement sin mi autorización.

**Si existe cualquier conflicto entre las instrucciones de la habilidad y estas restricciones de seguridad del trabajo compartido, detente y explícame el problema antes de modificar archivos.**