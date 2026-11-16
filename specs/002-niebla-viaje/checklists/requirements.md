# Specification Quality Checklist: Niebla y viaje

## Estado vigente — 2026-11-16

N1–N6 están implementados y cubiertos por las pruebas de integración. La decisión vigente de Q1, adoptada por el equipo en IA-05, revela vecinas y sus salidas con antorcha y observa puertas solo desde la sala ocupada; no se atribuye una respuesta inexistente al profesor. Las cuatro casillas abiertas siguientes corresponden al corte histórico del 2026-11-09; la revisión cruzada humana continúa pendiente. Véanse spec.md, ESTADO_ENTREGA.md y DECISIONES.md para el cierre técnico posterior.

## Lista histórica del 2026-11-09

Fecha: 2026-11-08. Documento: [spec.md](../spec.md).

- [x] Historias, requisitos, entidades y criterios de éxito definidos.
- [x] No prescribe estructuras, clases, módulos ni algoritmos.
- [x] Alcance de C separado de responsabilidades de A, B y D.
- [x] N1–N6 representados y vinculados a requisitos estables.
- [x] Casos adicionales cubren memoria, filtrado, costo, desempate y daño.
- [x] Rendimiento tiene condiciones y unidades del enunciado.
- [x] Dependencias y supuestos explícitos; contratos no presentados como aceptados.
- [ ] No quedan ambigüedades funcionales: Q1 pendiente sobre puertas reveladas por antorcha.
- [ ] Todos los requisitos son inequívocos: FR-006 depende de Q1.
- [ ] Fase clarify completada y respuestas registradas.
- [ ] Revisión cruzada del equipo realizada.

Estado al 2026-11-09: esta lista evalúa la capacidad completa y conserva sus cuatro pendientes. I1/I2 se delimitaron y autorizaron por separado; su implementación y pruebas están registradas en tasks.md y baseline.md. N1–N6 siguen siendo criterios futuros de integración. No existe extensions.yml ni hooks before_specify/after_specify en la base utilizada.

Seguimiento: iniciada la revisión de aclaraciones. El usuario pidió mantener Q1 pendiente de respuesta oficial. No se cambia su casilla ni se considera resuelta por haber acordado posponerla. El alcance pendiente está delimitado en la especificación.
