# Tareas de I1: conocimiento independiente

Alcance autorizado: spec.md, apartado I1. La lista no representa toda la capacidad C. Q1, viaje, inventario, historia e integración siguen fuera de esta entrega.

## Preparación

- [ ] T001 Cerrar alcance y revisar consistencia de `specs/002-niebla-viaje/spec.md`, `plan.md` y `data-model.md`; confirmar documentos antes del código (FR-001–005, FR-014, FR-017, PR-002).

## US1: mapa conocido

- [ ] T002 [US1] Escribir casos C01–C04/C13/C14 en `tests/test_conocimiento.py`: estados, ausencia de filtraciones, IDs dispersos, puertas desde ambos extremos y entradas repetidas (FR-001–005, FR-017, PR-002).
- [ ] T003 [US1] Implementar entradas inmutables, índices propios y validación en `modelo/conocimiento.py`, con restricciones de `data-model.md` (FR-001–005).
- [ ] T004 [US1] Implementar entrada física, observación y proyección filtrada en `modelo/conocimiento.py`; no añadir antorcha ni conexiones a motor (FR-001–005, FR-017).

## US3: reversión local

- [ ] T005 [US3] Añadir C12 a `tests/test_conocimiento.py`: reconstrucción entre instancias, lotes repetidos, inversión y rechazo atómico (FR-014, FR-017).
- [ ] T006 [US3] Implementar cambios de datos y aplicación/inversión en `modelo/conocimiento.py` sin callbacks ni copia de estado por acción (FR-014, FR-017).

## Verificación y entrega

- [ ] T007 Medir preparación, consultas y entrada/inversión con mapas crecientes mediante `utilidades/bench_conocimiento.py`; documentar evidencia y límites en `specs/002-niebla-viaje/baseline.md` (PR-002, SC-003 parcial).
- [ ] T008 Ejecutar pruebas nuevas y regresión seleccionada; documentar uso en `specs/002-niebla-viaje/quickstart.md` y resultados en `baseline.md` (SC-002/004 parciales).

Dependencias: T001 antes de código; T002 antes de T003/T004; T005 antes de T006; T007/T008 tras T004/T006. Trabajo sobre el mismo módulo secuencial. Las pruebas de US1 y US3 podrían diseñarse en paralelo tras T001, pero esta ejecución no delega cambios concurrentes.

Pendientes fuera de I1: FR-006–013, FR-015–016, PR-001/003 y SC-001; FR-014/017 y SC-002–004 solo se acreditan en ámbito local. No se marca terminada la capacidad completa.
