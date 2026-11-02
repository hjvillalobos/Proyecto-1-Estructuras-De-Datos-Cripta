# Tareas — línea de tiempo

Todas pendientes de implementación. No se ha escrito código del juego.

## Preparación y fundamento

- [ ] T001 Registrar y clasificar la base de pruebas en specs/004-linea-tiempo/baseline.md, sin confundir fallos heredados con cambios nuevos (FR-011, FR-017).
- [ ] T002 Implementar contratos tipados serializables en modelo/snapshots.py: tiempo entero >=0, secuencia estable, acción desde 1, K >=1, registros independientes del estado vivo (FR-002, FR-003, FR-008, FR-010).
- [ ] T003 Incorporar captura por evento y frontera de acción en modelo/juego.py y modelo/historial.py; conservar retroceso de cinco acciones y cerrar lote temporal antes de publicar decisión (FR-002, FR-006, FR-010).

## US1 — consultar el pasado (P1)

- [ ] T004 [US1] Crear pruebas H1,H3,H4, EX01,EX02,EX03,EX08 en tests/test_linea_tiempo.py citando requisitos (FR-001, FR-002, FR-003, FR-004, FR-005, FR-020).
- [ ] T005 [US1] Implementar registro segmentado, base inicial, checkpoints cada K y búsqueda binaria propia en modelo/linea_tiempo.py; sin snapshots por acción (FR-006, FR-009, FR-010).
- [ ] T006 [US1] Reconstruir estado aislado por tiempo y ordinal en modelo/linea_tiempo.py, sin red ni mutación del motor/azar/cachés; <=K acciones (FR-001, FR-002, FR-003, FR-004, FR-005, FR-010, FR-020).
- [ ] T007 [US1] Incorporar comando y resumen histórico en controlador/controlador.py y vista/consola.py (FR-001, FR-003, FR-004, FR-005, FR-020).

## US2 — conservar historia y corregir rama (P1)

- [ ] T008 [US2] Crear pruebas H2,H6,EX04,EX07 en tests/test_persistencia_historia.py; verificar inventario de pergaminos, recorte, nueva rama y corrupción (FR-007, FR-011, FR-012).
- [ ] T009 [US2] Recortar sufijo y registrar corrección persistente de pergaminos en modelo/linea_tiempo.py; liberar bloques descartados sin recorrer prefijo (FR-006, FR-007, FR-009).
- [ ] T010 [US2] Conectar cambios de conocimiento e inventario mediante modelo/snapshots.py y productores del motor; incluir mapa recordado (FR-004, FR-007, FR-011).
- [ ] T011 [US2] Implementar formato binario 4 con historia, K, RNG y versiones en datos/guardado_binario.py; rechazar P1, validar límites/CRC y carga atómica (FR-008, FR-011, FR-012).

## US3 — modos sin vista y preparación de partida (P2)

- [ ] T012 [US3] Crear pruebas H5,R4,EX05 y argumentos inválidos en tests/test_modos_historia.py con constructores de vista que fallen si son llamados (FR-008, FR-013, FR-014, FR-015, FR-016, FR-017, FR-020).
- [ ] T013 [US3] Añadir K positivo, --hasta, --verificar y --forzar, validar exclusiones y separar rutas sin vista en main.py (FR-008, FR-013, FR-015, FR-016, FR-017, FR-020).
- [ ] T014 [US3] Reproducir hasta frontera y emitir resumen común/aviso en controlador/replay.py y datos/bitacora_replay.py, conservando órdenes de retroceso/carga (FR-004, FR-013, FR-014, FR-017).
- [ ] T015 [US3] Conectar reporte del verificador antes de iniciar en controlador/aplicacion.py; no implementar aquí el algoritmo de resolubilidad (FR-015, FR-016).

## US4 — presentación e integración de comandos (P2)

- [ ] T016 [US4] Crear pruebas EX06 de mapa filtrado, costos, cazador y viaje en tests/test_comandos_integracion.py (FR-018, FR-019).
- [ ] T017 [US4] Interpretar viaje/mapa y mostrar motivo, costos y comportamiento en controlador/controlador.py, vista/consola.py y vista/grafica.py; delegar reglas a productores (FR-018, FR-019).
- [ ] T018 [US4] Registrar pasos como movimientos y orden como comentario en datos/bitacora_replay.py; no registrar consultas (FR-005, FR-019).

## Medición y cierre

- [ ] T019 Comparar K=10,50,100 y sin checkpoints; dirección, búsqueda, reconstrucción, memoria y recorte con >=5000 acciones en bench.py (FR-009, FR-010, NFR-001, NFR-002, NFR-003, SC-003).
- [ ] T020 Añadir pruebas de igualdad del estado tras consulta, carga y continuación en tests/test_persistencia_historia.py (NFR-004, SC-004).
- [ ] T021 Actualizar README.md, PROMPTS_LLM.md y DECISIONES.md con comandos, trazabilidad, mediciones reales y elección final de K; ejecutar regresiones y aceptación (FR-001–FR-020, NFR-001–NFR-004, SC-001, SC-002).

## Dependencias y estrategia

T001 → T002 → US1 sintética (T004–T006); T003 y T010 conectan los productores antes de la aceptación integrada. T009 puede probarse con cambios sintéticos sin T008 de persistencia binaria. US3 depende de US1 y persistencia para replay de cargas; bloqueo de inicio requiere contrato del verificador. US4 requiere productores de conocimiento y viaje. MVP: US1 con cambios sintéticos y pruebas H1/H3/H4. Luego incorporar captura real y persistencia. T019–T021 cierran aceptación, no preceden al núcleo.

Trabajo independiente posible: fixtures de US3 y US4 una vez fijados contratos; no editar main.py ni snapshots.py simultáneamente sin coordinación. Las tareas aquí se ejecutarán secuencialmente salvo decisión explícita del equipo.
