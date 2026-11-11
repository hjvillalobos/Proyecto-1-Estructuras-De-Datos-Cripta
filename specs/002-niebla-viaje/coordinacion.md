# Preparación y acuerdos pendientes de C

Fecha: 2026-11-08. Estado: revisión documental, sin aprobación por otros integrantes.

## Base y alcance

Rama `codex/002-niebla-viaje` actualizada por avance directo a `origin/main` 544090a. Se preservaron 16 líneas locales de puntajes fuera de los cambios documentales. No se incorporaron las ramas de desarrollo de los compañeros.

Se mantiene explícitamente `specs/002-niebla-viaje` según el reparto acordado, sin generar el siguiente número automático de spec-kit. La preparación usa la habilidad versionada speckit-specify y la plantilla resuelta por el script del repositorio.

## Constitución y acuerdo del chat

La constitución publicada es 1.1.0, ratificada según su texto el 2026-10-22 y modificada el 2026-10-27. El texto aprobado que el usuario pegó tiene catorce principios y encabezado de propuesta 1.0.0 sin fecha. No son el mismo documento y no se modifica unilateralmente la constitución compartida.

Coinciden en estructuras propias, determinismo, MVC, especificación previa, datos generales, presupuesto de red y mediciones. El acuerdo del chat detalla además conocimiento, retroceso/historia, versiones, contratos compartidos y registro de todos los prompts; la versión publicada exige explícitamente registrar invocaciones propias de spec-kit. C conserva esas restricciones adicionales del usuario mientras se confirma qué texto representa el acuerdo vigente del equipo. No se inventa ratificación ni se afirma que las fechas fueron verificadas externamente.

## Entregables por acordar

| Tema | Interlocutor | Evidencia necesaria antes de integrarlo |
| --- | --- | --- |
| Rutas filtradas | A | Fuente solo explorada y puertas recordadas abiertas; consulta sin límite de rango; resultado y desempate compatibles. |
| Observaciones | A y B | Identidad de puerta entre extremos; entrada, cambios observables y antorcha; orden respecto de eventos. |
| Retroceso | A y D | Cambios reversibles, serializables y frontera del paso; excepción del pergamino y recorte histórico. |
| Mapa y viaje | D | Entrega filtrada y control entre pasos que permita interrupción; señales de daño/enemigos y razón de detención. |
| Inventario e historia | D | Cambios suficientes para reconstrucción y carga; no presentar funciones de reversión existentes como datos persistibles. |
| Enemigos | A | Mantener comportamientos anteriores de C y acordar punto de conexión del cazador. |

Referencias revisadas: `origin/feature/motor-eventos` 934eaff, contrato `specs/001-terreno-cazador/contracts/integracion.md`; `origin/004-linea-tiempo` a34d926, contrato `specs/004-linea-tiempo/contracts/interfaces.md`. A marca entregables de C pendientes. D propone `mapa_conocido()` y `viajar_hasta(destino, mover)`; su documentación indica validación con productor de prueba y confirmación pendiente con A/C. No se adoptan firmas únicamente porque ya exista un consumidor.

## Siguiente fase

Actualización tras mensajes del grupo aportados por el usuario: el equipo identifica expresamente la constitución de main como compartida. No se necesita otra constitución. Se preparó [una propuesta concreta de contratos](contracts/propuesta-integracion.md) que incluye inventario, además de conocimiento y viaje. Sus firmas son candidatas; la preparación no equivale a completar la fase plan ni a obtener aceptación de A/D.

Resolver Q1 y ejecutar clarify; acordar contratos concretos antes de implementar conexiones. Después preparar plan, tareas y análisis, y confirmar especificación en Git antes del código. La especificación actual puede revisarse sin elegir estructuras. No se atribuyen pruebas ni rendimiento de las ramas ajenas como verificados localmente.
