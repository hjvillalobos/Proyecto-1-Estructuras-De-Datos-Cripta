# Tareas de I1: conocimiento independiente

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

- [ ] T014 [US3] Escribir C18–C20 y validaciones de conversión en `tests/test_conocimiento_historia.py` (FR-019, FR-014/016 parciales).
- [ ] T015 [US3] Implementar base y conversión en `modelo/conocimiento_historia.py`, con tipos reales de D e índices/ordenamiento propios (FR-019).
- [ ] T016 Preparar ejecución aislada reproducible en `utilidades/verificar_conocimiento_historia.py` y documentarla en quickstart.md (FR-019, SC-004 parcial).
- [ ] T017 Verificar rechazo atómico, reconstrucción y regresión local; registrar evidencia en baseline.md y actualizar propuesta de integración (FR-019).

Orden: documentación confirmada antes de T014/T015; T014 antes de T015; T016 permite comprobar ambas sin fusionar ramas; T017 después. No se modifica ningún archivo de A/D ni se añade captura automática al motor.
