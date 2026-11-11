# Tareas de I1: conocimiento independiente

## I9: diagnóstico independiente ampliado

- [x] T035 Escribir pruebas de C40/C41, incluyendo detección de discrepancias (FR-008/010/014/017, PR-001 parcial).
- [x] T036 Añadir escenarios reproducibles y opción de ejecución aislada, sin modificar el modelo ni A/D (mismos requisitos).
- [x] T037 Ejecutar pruebas y mediciones, documentar límites y publicar en C (PR-001 parcial).

Análisis previo: escenarios, plan y tareas coinciden; no introducen reglas ni estructuras prohibidas. Q1 y revisión cruzada siguen abiertos fuera de I9. Documentación confirmada antes de código; T035 precede a T036 y T037 cierra la evidencia local.

## I8: rendimiento de rutas

- [x] T032 Escribir C37–C39 de equivalencia e invalidación (FR-008/010/014/017).
- [x] T033 Implementar revisión de conocimiento y reutilización en módulos de C, sin modificar A (mismos requisitos).
- [x] T034 Comparar primera búsqueda, pasos sucesivos y cambios de puerta; ejecutar regresión y publicar resultados (PR-001 parcial).

Especificación antes del código; pruebas antes de optimización; mediciones después de comprobar equivalencia. Sin cambios en contratos compartidos ni cierre de PR-001 por medias sintéticas.

## I7: inventario histórico

- [x] T029 Escribir C33–C36 contra inventario e historia reales (FR-020, FR-014/016 parciales).
- [x] T030 Implementar adaptador local sin cambiar módulos compartidos (FR-020).
- [x] T031 Ejecutar pruebas y regresión; documentar contrato breve y publicar C (FR-017/020).

Especificación antes del código; T029 precede a T030 y T031 verifica ambos. Integración al motor pendiente.

## I6: primera prueba con motor real y revisión de novedades

- [x] T026 Escribir C31/C32 con productor H3 y LineaTiempo reales en tests/test_viaje_motor.py (FR-009/011/016 parcial/017).
- [x] T027 Crear utilidades/verificar_viaje_motor.py con revisiones fijas y ejecutar pruebas propias/nuevas de B en copias separadas (SC-002/004 parciales).
- [x] T028 Documentar resultados, limitaciones y contrato pendiente; publicar solo C (SC-002/004 parciales).

Documentación antes de T026; T027 permite comprobarla; T028 después. No implica nuevas reglas del juego ni integración de la interfaz.

## I5: control local del viaje

- [x] T022 Escribir C26–C30 en tests/test_viaje.py antes de implementar (FR-007/009/010/011/012/015/017/018).
- [x] T023 Implementar modelo/viaje.py y validación atómica del protocolo, sin motor ni vista (mismos requisitos de T022).
- [x] T024 Probar secuencia con conocimiento y rutas reales de A en tests/test_conocimiento_rutas.py y ampliar verificador (FR-008/010/015 local).
- [x] T025 Ejecutar regresión, documentar evidencia/contrato y publicar en rama C (SC-002/004 parciales).

Dependencias: especificación confirmada antes de T022/T023; T022 antes de T023; T024 después; T025 cierra el incremento. Q1 y revisión cruzada siguen fuera de alcance.

Alcance autorizado: spec.md, apartado I1. La lista no representa toda la capacidad C. Q1, viaje, inventario, historia e integración siguen fuera de esta entrega.

## Preparación

- [x] T001 Cerrar alcance y revisar consistencia de `specs/002-niebla-viaje/spec.md`, `plan.md` y `data-model.md`; confirmar documentos antes del código (FR-001–005, FR-014, FR-017, PR-002).

## US1: mapa conocido

- [x] T002 [US1] Escribir casos C01–C04/C13/C14 en `tests/test_conocimiento.py`: estados, ausencia de filtraciones, IDs dispersos, puertas desde ambos extremos y entradas repetidas (FR-001–005, FR-017, PR-002).
- [x] T003 [US1] Implementar entradas inmutables, índices propios y validación en `modelo/conocimiento.py`, con restricciones de `data-model.md` (FR-001–005).
- [x] T004 [US1] Implementar entrada física, observación y proyección filtrada en `modelo/conocimiento.py`; no añadir antorcha ni conexiones a motor (FR-001–005, FR-017).

## US3: reversión local

- [x] T005 [US3] Añadir C12 a `tests/test_conocimiento.py`: reconstrucción entre instancias, lotes repetidos, inversión y rechazo atómico (FR-014, FR-017).
- [x] T006 [US3] Implementar cambios de datos y aplicación/inversión en `modelo/conocimiento.py` sin callbacks ni copia de estado por acción (FR-014, FR-017).

## Verificación y entrega

- [x] T007 Medir preparación, consultas y entrada/inversión con mapas crecientes mediante `utilidades/bench_conocimiento.py`; documentar evidencia y límites en `specs/002-niebla-viaje/baseline.md` (PR-002, SC-003 parcial).
- [x] T008 Ejecutar pruebas nuevas y regresión seleccionada; documentar uso en `specs/002-niebla-viaje/quickstart.md` y resultados en `baseline.md` (SC-002/004 parciales).

Dependencias: T001 antes de código; T002 antes de T003/T004; T005 antes de T006; T007/T008 tras T004/T006. Trabajo sobre el mismo módulo secuencial. Las pruebas de US1 y US3 podrían diseñarse en paralelo tras T001, pero esta ejecución no delega cambios concurrentes.

Pendientes fuera de I1: FR-006–013, FR-015–016, PR-001/003 y SC-001; FR-014/017 y SC-002–004 solo se acreditan en ámbito local. No se marca terminada la capacidad completa.

## I2: ampliación independiente autorizada

- [x] T009 [US3] Añadir secuencias C17 con semilla fija y referencia independiente, ciclos, desconexión y puertas paralelas en `tests/test_conocimiento_secuencias.py` (FR-003/004/014/017).
- [x] T010 [US2] Escribir C15/C16 en `tests/test_detencion_viaje.py` y luego implementar función pura en `modelo/detencion_viaje.py` (FR-018).
- [x] T011 Preparar demostración reproducible con aserciones en `tests/demo_conocimiento.py`, sin vista nueva ni persistencia (FR-001–005/014).
- [x] T012 Ampliar medición separada de memoria, puerta y proyección en `utilidades/bench_conocimiento.py`; registrar resultados en `baseline.md` (PR-004).
- [x] T013 Verificar pruebas nuevas/regresión y actualizar `quickstart.md` y `baseline.md`, con límites de I2 (FR-017/018, PR-004).

T009 y T010 son independientes, pero cada prueba precede a su implementación. T011 utiliza I1 existente. T012 usa carga propia de medición; T013 depende de T009–T012. No modifica interfaz ni módulos de los demás integrantes.

## I3: conversión a historia real de D

- [x] T014 [US3] Escribir C18–C20 y validaciones de conversión en `tests/test_conocimiento_historia.py` (FR-019, FR-014/016 parciales).
- [x] T015 [US3] Implementar base y conversión en `modelo/conocimiento_historia.py`, con tipos reales de D e índices/ordenamiento propios (FR-019).
- [x] T016 Preparar ejecución aislada reproducible en `utilidades/verificar_conocimiento_historia.py` y documentarla en quickstart.md (FR-019, SC-004 parcial).
- [x] T017 Verificar rechazo atómico, reconstrucción y regresión local; registrar evidencia en baseline.md y actualizar propuesta de integración (FR-019).

Orden: documentación confirmada antes de T014/T015; T014 antes de T015; T016 permite comprobar ambas sin fusionar ramas; T017 después. No se modifica ningún archivo de A/D ni se añade captura automática al motor.

## I4: búsqueda por conocimiento con A

- [x] T018 Escribir C21–C25 en tests/test_conocimiento_rutas.py, con oráculo independiente reproducible (FR-003/004/007/008/010/012/017).
- [x] T019 Implementar modelo/conocimiento_rutas.py con fuente filtrada y buscador real de A (FR-007/008/010/012/017).
- [x] T020 Preparar utilidades/verificar_conocimiento_rutas.py y utilidades/bench_rutas_conocidas.py; comprobar fuente real sin modificar A ni certificar PR-001 con carga sintética (FR-008/017, PR-001 parcial).
- [x] T021 Ejecutar pruebas, regresión de C y diagnóstico; registrar alcance y resultados en baseline.md y quickstart.md (SC-001/002/003 parciales).

Orden: especificación confirmada antes de T018/T019; pruebas antes de implementación; T020 permite verificar T019; T021 después. La revisión clarify de I4 no encuentra reglas pendientes dentro de su alcance; Q1 y los acuerdos del viaje completo permanecen abiertos. No se modifica la lista general de calidad.
