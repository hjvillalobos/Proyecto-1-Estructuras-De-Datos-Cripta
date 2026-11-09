# Feature Specification: Niebla de guerra y viaje automático

**Feature Branch**: `codex/002-niebla-viaje`
**Created**: 2026-11-08
**Status**: Borrador; pendiente de clarify y revisión cruzada. No autoriza implementación.
**Input**: Persona C según asignación confirmada por el usuario. Preparar su capacidad conforme a Parte II §§3.3–3.4, 5.3, 5.6, 6.1 y Apéndice B.

## User Scenarios & Testing

### User Story 1 - Consultar solamente lo conocido (Priority: P1)

Como jugador quiero distinguir lo explorado de lo que solamente he avistado, sin recibir información por una descarga anticipada.

**Why this priority**: El conocimiento determina tanto el mapa como las decisiones de viaje.
**Independent Test**: Comparar el conocimiento antes y después de entrar, observar y precargar, sin utilizar viaje automático.

**Acceptance Scenarios**:

- C01: Dada una partida nueva, al consultar el mapa en t=0, la sala inicial está explorada; los destinos de sus salidas están avistados salvo que ya estén explorados; el resto es desconocido. FR-001–003.
- C02: Dada una sala avistada, al consultar el mapa no se revelan su nombre, contenido ni sus propias salidas; de una desconocida no se revela información. FR-002–003.
- C03: Dada una puerta observada desde un extremo, al cambiar remotamente permanece el recuerdo anterior; al observarla desde cualquiera de sus extremos se actualiza el mismo recuerdo. FR-004.
- C04: Dados iguales conocimientos y diferentes contenidos precargados, las consultas muestran el mismo mapa y no avanzan el reloj. FR-003, FR-005.
- N4: Dada una antorcha encendida, al entrar se exploran las vecinas por salidas abiertas o cerradas, sin activar enemigos ni trampas de esas vecinas ni revelar su contenido. FR-006. Las salidas de esas vecinas permiten avistar otras salas, pero no desencadenan exploración recursiva.

### User Story 2 - Viajar por lo explorado (Priority: P2)

Como jugador quiero llegar a una sala explorada mediante movimientos ordinarios y detenerme cuando surja peligro o deje de haber ruta conocida.

**Why this priority**: Automatiza desplazamientos sin conceder conocimiento ni acciones adicionales.
**Independent Test**: Preparar conocimientos explícitos y contrastar cada paso con movimientos manuales equivalentes.

**Acceptance Scenarios**:

- N1: Dado un destino avistado o desconocido, al pedir `ir a <sala>` se rechaza sin consumir tiempo. FR-007.
- C05: Dadas rutas de diferente costo, se elige la suma mínima aunque implique más salas; entre primeros pasos óptimos se elige la vecina de menor identificador. Una ruta por una sala no explorada queda excluida aunque sea más barata. FR-008.
- C06: Dada una secuencia de pasos, cada paso consume el tiempo ordinario y procesa los eventos correspondientes antes del siguiente; la siguiente ruta utiliza el conocimiento vigente. FR-009–010.
- N2: Dada una puerta recordada abierta pero cerrada realmente, al observarla se actualiza el mapa y se recalcula. Si no queda ruta, se detiene sin tiempo adicional; si hay alternativa conocida, el siguiente cálculo la utiliza. FR-004, FR-010–012.
- N3: Dado un paso hacia una sala con enemigos dormidos, al entrar se activan conforme a P1 y el viaje se detiene. FR-011.
- C07: Dado un paso que entra en una sala con enemigos activos, o durante el cual se recibe daño, no se ejecuta otro paso. Una curación posterior no elimina el hecho de haber recibido daño. FR-011.
- C08: Dada una puerta cerrada y su llave en el inventario, el viaje no la abre; al llegar al destino se detiene, y si el destino es la sala actual no ejecuta un movimiento. FR-011–012.
- C09: Dado un viaje de varios pasos, la reproducción contiene cada movimiento individual y la orden como comentario; reproduce el resultado de esos movimientos con los mismos datos y semilla. FR-013, FR-017.

### User Story 3 - Conservar y revertir el conocimiento (Priority: P1)

Como jugador quiero que retroceso, guardado e historia representen lo que conocía en cada momento.

**Why this priority**: El conocimiento es estado de partida, no información auxiliar de presentación.
**Independent Test**: Comparar conocimiento antes de una acción, después de ella, tras revertirla y después de guardar/cargar.

**Acceptance Scenarios**:

- N5: Dada una entrada con antorcha, al revertirla se restauran los estados anteriores de las salas reveladas y sus recuerdos modificados, conservando lo que ya se conocía previamente. FR-014.
- N6: Dado un viaje con pasos ejecutados, al usar el pergamino durante el viaje se revierte solo el último paso y no continúa automáticamente. Se conserva la excepción del pergamino de P1. FR-015.
- C10: Dado conocimiento con puertas recordadas de forma distinta a su estado real, guardar y cargar conserva esa distinción. Consultar historia devuelve el mapa del instante solicitado sin modificar la partida ni el historial de retroceso. FR-016.
- C11: Dadas acciones revertidas, la historia vigente excluye el conocimiento adquirido únicamente en ellas. El retroceso mantiene su límite de cinco acciones. FR-014–016.

### Edge Cases

- Destino inexistente: se trata como no explorado, sin revelar información adicional ni consumir tiempo (N1).
- Sala sin salidas conocidas o destino explorado desconectado: ausencia de ruta conocida (N2).
- Ciclos y rutas de igual costo: se conserva el mínimo y desempate en cada paso (C05).
- Revelación repetida: no borra conocimiento previo ni convierte la antorcha en exploración recursiva (N4, N5).
- Puerta observada desde ambos extremos: existe un único recuerdo coherente (C03).
- Daño seguido de curación dentro del paso: detención por daño recibido (C07).
- Puerta de una vecina revelada con antorcha, sin observación física previa: cuestión Q1 pendiente.

## Requirements

### Functional Requirements

Los identificadores FR son locales a esta capacidad y se citarán con el prefijo documental `002-niebla-viaje` para distinguirlos de otras especificaciones.

- **FR-001**: Distinguir salas exploradas, avistadas y desconocidas; explorar la inicial desde t=0 y las entradas físicamente.
- **FR-002**: Una sala explorada permite conocer nombre, salidas, costos y puertas según observaciones; una avistada revela solo existencia; una desconocida no revela información.
- **FR-003**: Avistar los destinos de salidas de salas exploradas sin degradar salas ya exploradas. La descarga y la precarga no alteran conocimiento ni habilitan información en mapa o viaje.
- **FR-004**: Observar puertas desde cualquiera de sus extremos y recordar la última observación; un cambio remoto no actualiza por sí mismo el recuerdo.
- **FR-005**: Ofrecer consulta del mapa conocido, con salas exploradas, salidas y avistadas, sin consumir tiempo virtual.
- **FR-006**: Al entrar con antorcha encendida, explorar las vecinas a través de salidas abiertas o cerradas, revelando su esqueleto y no contenido; no activar allí enemigos ni trampas ni encadenar exploración a más distancia. La información de puertas no observadas se resolverá en Q1.
- **FR-007**: Rechazar viaje a destino no explorado sin consumir tiempo.
- **FR-008**: Calcular el viaje exclusivamente por salas exploradas y salidas recordadas abiertas, minimizando suma de costos y desempatando por menor identificador de la primera vecina.
- **FR-009**: Cada paso debe ser un movimiento ordinario completo, con sus efectos, costo de tránsito y eventos entre decisiones conforme a las reglas vigentes.
- **FR-010**: Recalcular antes de cada paso con conocimiento vigente; incorporar observaciones de puertas cerradas antes de decidir la continuación.
- **FR-011**: Detener el viaje al llegar, al entrar en sala con enemigos activos o dormidos, al recibir daño o al no existir ruta conocida. Comunicar el motivo sin ejecutar pasos adicionales.
- **FR-012**: No abrir puertas durante el viaje aunque se tenga llave. La detención por falta de ruta tras observar puerta cerrada no consume tiempo adicional. Destino igual a sala actual no genera movimiento.
- **FR-013**: Registrar cada paso como movimiento individual y la orden de viaje como comentario de depuración.
- **FR-014**: Revertir cambios de conocimiento asociados a las acciones revertidas, conservando el conocimiento previo y el límite de cinco acciones del retroceso.
- **FR-015**: El pergamino durante un viaje cancela su continuación y revierte únicamente el último paso, respetando la excepción de reversión del pergamino de P1.
- **FR-016**: Conservar el conocimiento en guardado y reconstrucción histórica, incluida memoria de puertas; las consultas históricas no modifican la partida y las acciones revertidas dejan de pertenecer a la historia vigente.
- **FR-017**: Con iguales versiones de datos, semilla y acciones, producir iguales conocimientos, pasos y motivos de detención, independientemente del orden de descarga o de presentación.

### Performance Requirements

- **PR-001**: Calcular un paso de viaje en máximo 5 ms con mapa conocido completo de la cripta de referencia, medido localmente sin red ni renderizado; registrar cualquier enmienda oficial.
- **PR-002**: La exploración incremental debe costar proporcionalmente a las salas reveladas, no al tamaño total del mapa conocido; medir consultas de estados y memoria de puertas.
- **PR-003**: Repetir las mediciones aplicables de P1 para inventario y retroceso bajo la nueva carga, documentando resultados y límites sin atribuir resultados pendientes como obtenidos.

### Key Entities

- **Conocimiento de sala**: identidad, grado de conocimiento e información permitida según ese grado.
- **Recuerdo de puerta**: estado observado más recientemente, compartido por ambos extremos, distinto del estado real remoto.
- **Viaje**: destino explorado, pasos ordinarios y motivo de detención.
- **Cambio de conocimiento**: diferencia atribuible a una acción o evento que permite restaurar y reconstruir lo conocido.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Los seis escenarios N1–N6 del reparto, correspondientes a los seis casos de niebla/viaje del Apéndice B, tienen evidencia automatizada o bitácora reproducible antes de declarar terminada la capacidad.
- **SC-002**: C01–C11 verifican límites de información, determinismo e integración; ninguna descarga cambia el mapa ni una decisión de viaje por sí misma.
- **SC-003**: Las mediciones demuestran PR-001–003 con carga, semilla, entorno y unidades declarados; no se extrapolan a mapas no medidos.
- **SC-004**: Retroceso, guardado/carga e historia conservan exactamente los conocimientos esperados en N5, N6, C10 y C11.

## Assumptions

- Fuentes: `Cripta - Parte II (1).pdf`, pp. 5–6, 8–9 y 12; reparto `CRIPTA_Parte_II_Division_de_Trabajo.pdf`, pp. 2, 5 y 8. Los códigos N1–N6 pertenecen al reparto, no son numeración oficial del profesor.
- El usuario confirma que le corresponde C, aunque el documento de reparto se dirige a B en su introducción.
- Continúan las reglas de P1 salvo modificación expresa. No se redefinen movimiento, activación, costo del pergamino ni orden temporal desde esta capacidad.
- Se depende de A para movimiento, eventos y observaciones; de B para datos válidos; de D para interfaz, persistencia y reconstrucción histórica. Los contratos todavía no están aceptados por todas las partes.
- El borrador no considera completadas clarify, plan, tasks, analyze, implementación ni pruebas de la capacidad.

## Clarifications pendientes

**Q1 — puertas de salas reveladas con antorcha.** [NEEDS CLARIFICATION: ¿qué información recibe el jugador sobre una puerta que pertenece a una vecina revelada por antorcha, pero cuyos extremos nunca ha ocupado? §3.3 exige exploración de la vecina y memoria de la última observación, pero define observación estando en un extremo. Confirmar si queda sin observación utilizable para viaje o si la antorcha también permite observar esa puerta; no asumir el estado real como recuerdo.]

Esta pregunta requiere aclaración del enunciado o referencia oficial; una preferencia técnica no la resuelve. La revisión obligatoria de clarify podrá identificar otros casos antes de cerrar el diseño.
