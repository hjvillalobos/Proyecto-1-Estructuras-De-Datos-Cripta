# Modelo de datos propuesto — provisional

**Fecha:** 2026-11-02. Derivado de [spec.md](spec.md); Q1/Q2 condicionan validación. No se modifica tipos.py ni snapshots.py. Estas entidades no son clases creadas.

**Actualización documental 2026-11-05:** E-B-COSTOS y E-B-RANGO separan suministro/acceso para integraciones, sin alterar estas entidades ni acreditar entregas. El [reporte de B sobre OpenAPI 1.1.0](research.md#comunicación-reportada-de-b-sobre-openapi-110) describe campos opcionales/nullables y valores enteros ≥1 cuando existen; no disponemos de fuente primaria verificable. Los invariantes de juego siguientes provienen del enunciado. Q1/Q2 siguen pendientes: no se convierte un null de rango/costo en un valor por defecto ni se inventa rechazo/normalización de inconsistencias. El mínimo reportado para rango es evidencia indirecta, no una regla nueva aprobada.

| Entidad | Campos conceptuales | Invariantes y relaciones |
| --- | --- | --- |
| Grafo preparado | identidad, IDs externos, índices densos, adyacencias, arcos entrantes opcionales | Un índice por sala, referencias resueltas en preparación, sin dict/set ni reserva por maxID. |
| Arco | origen, destino, dirección, costo, referencia a puerta | Ausente 100; declarado entero ≥1 y simétrico para datos válidos. Q2 abierta. No copiar estado real de puerta a una autoridad paralela. |
| Puerta real | identidad a acordar, estado, llave, cierre automático | Distinguir memoria de puertas de C; coherencia de ambos extremos pendiente de contrato. |
| Cazador activo | instancia, posición, vida, velocidad, evento, rango suministrado | Atacar primero si coincide con jugador; mínimo/default/invalidez de rango pendientes Q1. No extender tipo compartido unilateralmente. |
| Espacio de búsqueda | generación, distancias, primerID, posición heap, marcas | Arreglos preparados una vez; valor válido solo en generación vigente. |
| Frontera | índice y etiqueta | Heap propio y orden total; sin usar secuencias de eventos del juego. |
| Resultado | estado conceptual, primer vecino/dirección y costos solo cuando corresponden | Distinguir llegada, ruta válida y fracaso demostrado o limitado según [contrato propuesto](contracts/integracion.md). Una búsqueda acotada no inventa existencia ni distancia fuera del rango. |
| Modo de consulta | ACOTADA(limite) o SIN_LIMITE, fuente filtrada e identidad/revisión | SIN_LIMITE es propuesta para viaje de C; no elimina el filtro de conocimiento ni define un rango por defecto para cazador. |
| Cache derivado | grafo, época, origen, objetivo, modo/límite, resultado | Alternativas acotadas de última consulta o varias entradas por evaluar; coincidencia exacta, capacidad y reemplazo deterministas pendientes. No estado autoritativo ni persistido. |
| Evento semántico | tiempo, secuencia, tipo, referencia, cancelado, en_cola | API existente; nueva secuencia al reprogramar. |
| Cambio reversible | entidad/campo, anterior/nuevo, tiempo y orden | Registro serializable a acordar con C/D; callbacks no se transforman automáticamente en persistencia. |

## Transiciones propuestas

1. B entrega esqueleto/fichas; A construye representación e índices. Q1/Q2 impiden cerrar política fuera del contrato. No descargar contenido para buscar rutas.
2. Turno: comprobar vida/actividad, coincidencia con jugador, consultar grafo y decidir atacar/esperar/paso. El motor ejecuta, no la búsqueda.
3. Movimiento: posición inmediata, costo de arco para siguiente acción, activación/efectos heredados. C recibe observaciones sin revelar contenido anticipado.
4. Puerta: registrar cambios coherentes, modificar estado real y aumentar época; observación limitada según C. No consumir secuencia de evento por metadato del cache.
5. Velocidad: reajustar evento y secuencia; geometría permanece si no cambian puertas/objetivo.
6. Muerte/cancelación: no futuras acciones/daños cancelados. No inventar bloqueo de salas por actores.
7. Undo/rollback/carga: C/D restauran juego; A descarta derivados mediante época/identidad nueva. No restaurar cache antiguo. B conserva infraestructura fuera de retroceso.

## Validación y persistencia

- Q1: no mínimo/default ni política de rango inválido/ausente.
- Q2: no corrección/rechazo ni copia automática de costo entre sentidos.
- Q3: no cambia entidades; deja pendiente certificación de carga.
- D recibe estado semántico de actores, puertas, efectos, eventos, secuencias y azar; C aporta conocimiento/inventario. Formato y versión son de D con acuerdo del equipo.
- Heap de rutas, marcas, distancias y cache se reconstruyen. Construcción O(V+E) o mayor según índice se mide separadamente y no se repite/oculta en cada consulta.
