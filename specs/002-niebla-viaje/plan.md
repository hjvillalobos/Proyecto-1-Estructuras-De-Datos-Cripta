# Plan técnico provisional: conocimiento y viaje

**Rama:** `codex/002-niebla-viaje` · **Fecha:** 2026-11-08 · **Especificación:** [spec.md](spec.md)

## Resumen

**Alcance vigente I1:** tras la autorización del usuario se ejecuta únicamente conocimiento básico y deltas locales. Las restricciones generales de cierre que siguen en este documento corresponden a la capacidad completa. I1 tiene alcance aclarado en spec.md, diseño en data-model.md y tareas propias; no depende de Q1 ni de aceptar interfaces ajenas. Se usa la investigación ya realizada. Los índices de puertas reciben identificadores explícitos del llamador, sin deducirlos de extremos.

El primer incremento administrará conocimiento sin modificar el motor: exploración por entrada física, avistamiento, recuerdos de puertas observadas y cambios reversibles. Después se conectarán mapa e historia y, con los acuerdos correspondientes, antorcha y viaje. Este documento recoge decisiones candidatas y dependencias; no declara terminado el flujo de planificación.

## Contexto técnico

- Python 3.11 o superior; pruebas con unittest y dependencias actuales del proyecto. No se añade dependencia de ejecución.
- Modelo independiente de red, archivos y vista. C entrega datos; A coordina acciones y reloj; D presenta y persiste.
- Esqueleto completo disponible como infraestructura; se construyen índices internos sin conceder conocimiento al jugador.
- Tamaño general V salas, E salidas y P puertas, con identificadores potencialmente dispersos. No reservar memoria hasta el máximo ID.
- Meta: paso de viaje en máximo 5 ms bajo PR-001; revelación incremental bajo PR-002; repetir mediciones de inventario/retroceso bajo PR-003.
- Pendientes: Q1, identidad de puerta A/B/C, entrada y resultado de paso A/C, adaptación histórica C/D y búsqueda filtrada sin límite A/C.

## Revisión de la constitución

| Regla | Tratamiento |
| --- | --- |
| Estructuras propias | Arreglos de bajo nivel, búsqueda binaria y ordenamiento propios; sin dict/set como índices ni estructuras de biblioteca. |
| Determinismo | Identidad estable, orden del motor, desempate de ruta de A; el conocimiento no usa azar. |
| MVC y presupuesto | C no descarga datos ni lee/escribe archivos. No se incorporan esperas de interfaz al reloj. |
| Datos generales | El tamaño depende del esqueleto recibido, no de criptas conocidas ni del mayor ID. |
| Especificación previa | Existe commit documental bcb44b8. Los cambios posteriores de especificación deben confirmarse antes de su código. |
| Medición | Se definen cargas y límites; aún no hay resultados de Parte II de C. |
| Flujo y acuerdos | Revisión de aclaraciones abierta; Q1 y contratos impiden declarar aprobado el plan completo. |

**Estado de la puerta de control:** pendiente. El usuario pidió dejar Q1 abierta y continuar la preparación independiente. Esto no equivale a resolverla, aprobar contratos ni completar plan/tasks/analyze. No se generan tareas ejecutables de implementación hasta cerrar o delimitar formalmente el alcance admitido en el flujo del equipo.

## Organización prevista

| Archivo | Responsabilidad propuesta |
| --- | --- |
| `modelo/conocimiento.py` | Índices de salas/puertas, grados de conocimiento, observaciones y deltas del mapa. |
| `modelo/viaje.py` | Coordinación de pasos y causas de detención, sin ejecutar eventos por su cuenta. |
| `modelo/historial.py`, `modelo/inventario.py` | Mantener retroceso y aportar registros de datos reconstruibles; modificación posterior al acuerdo C/A/D. |
| `tests/test_conocimiento.py` | Estados, memoria, filtrado y reversión. |
| `tests/test_viaje.py` | Rutas conocidas, condiciones de parada y cancelación. |
| `tests/test_conocimiento_historia.py` | Adaptación a tipos reales de D y reconstrucción. |
| `utilidades/bench_conocimiento.py` | Consultas, revelación incremental y cálculo de paso. |

Los archivos propuestos aún no existen. `modelo/juego.py` y `modelo/rutas.py` se coordinan con A; controlador, snapshots y persistencia con D. No se crean versiones paralelas de sus tipos en C para aparentar integración.

## Diseño candidato

### Índices y conocimiento

Preparar una sola vez un arreglo de IDs ordenado mediante el ordenamiento propio y búsqueda binaria manual. Asociar cada ID a un índice compacto. Las salidas internas retienen índices ya resueltos, evitando búsquedas repetidas al revelar vecinas. El conocimiento ocupa arreglos separados de los datos descargados: desconocida, avistada o explorada, y memoria de puertas independiente del estado real.

Una consulta pública por ID cuesta O(log V); por índice interno O(1). Inicializar índices cuesta O((V+E) log V) como cota de referencia; memoria O(V+E+P). No se atribuye ese trabajo a una entrada normal. La actualización recorre solo las salas y salidas afectadas, O(R+A), donde R son salas procesadas y A sus salidas; se mide aparte cualquier traducción inicial de ID. No se recorre todo el mapa conocido para descubrir qué cambió.

La proyección de mapa puede recorrer el índice y costar O(V+E); es una consulta de presentación, no la operación de revelar ni la fuente que se reconstruye antes de cada paso. Si las mediciones justifican un índice adicional de salas conocidas se documentará antes de introducirlo.

### Cambios reversibles

Registrar por operación únicamente valores que cambian: estado anterior/posterior de sala, recuerdo anterior/posterior de puerta y metadatos necesarios. Revertir un lote invierte su orden. Si una operación vuelve a tocar un mismo campo, se pueden registrar cambios consecutivos sin construir una tabla de deduplicación prohibida. Memoria y aplicación O(D), para D cambios registrados.

El retroceso actual conserva funciones. No se serializan: el plan final debe decidir cómo producir registros de datos en el mismo punto de mutación y reutilizarlos para retroceso/historia sin doble aplicación. Inventario requiere identidad, orden, cursor y equipamiento; la excepción de pergaminos se conserva. No se transforma cada acción en una copia completa del inventario o del mapa.

D ya admite escalares y tuplas inmutables mediante ValorHistorico y CambioHistorico; tiempo/secuencia pertenecen al contenedor de evento. El adaptador debe usar esa forma tras acuerdo, sin inventar un segundo formato binario.

### Rutas y viaje

Preferencia: reutilizar la búsqueda propia de A mediante fuente filtrada y consulta sin límite. La implementación publicada usa `arco.puerta.get("cerrada", False)` y compara contra un límite numérico: no basta pasarle el mapa real ni sustituir ausencia de límite por un número enorme. A/C deben acordar la extensión; si no resulta viable, documentar una alternativa antes de programar otro buscador.

C propone un paso; el controlador ejecuta un movimiento ordinario; el motor cierra el intervalo; C recibe hechos del paso y decide si continúa. Se debe poder procesar pergamino entre pasos. Se registra daño ocurrido, incluso si una curación posterior restaura la vida. D mantiene registro individual de movimientos y comentario de viaje. No se afirma que el callback booleano actual satisfaga estas necesidades.

### Antorcha

Revelar vecinas no activa contenido y no se propaga recursivamente. Q1 queda fuera de las decisiones adoptadas: no se fija la memoria de puertas remotas nunca observadas. La implementación de esa política y sus pruebas esperan respuesta.

## Entregas previstas y condiciones de cierre

1. **Conocimiento básico:** FR-001–005, parte independiente de FR-014 y FR-017. C01–C04, IDs dispersos y reversión local. Sin conexiones a archivos compartidos.
2. **Historia e inventario:** FR-014–016, C10–C11. Requiere acuerdo de lotes, correcciones de pergamino, estado completo y tipos de D.
3. **Antorcha:** FR-006, N4–N5. Requiere resolver Q1 y acuerdo de observaciones con A.
4. **Viaje:** FR-007–013, FR-015 y FR-017, N1–N3/N6 y C05–C09. Requiere ruta filtrada y resultado/cancelación acordados; verifica la regla de antorcha cuando intervenga.
5. **Integración y medición:** PR-001–003 y SC-001–004. Solo se cierra con código real de A/D, regresiones, trazabilidad y mediciones; pruebas aisladas no acreditan partida integrada.

Estas son entregas propuestas, no tareas ejecutadas. La lista formal de tareas y el análisis cruzado se prepararán al superar la puerta de control.

## Mediciones previstas

Cargas deterministas con igual cantidad de salas reveladas y distintos tamaños de mapa total; registrar trabajo y tiempo para distinguir preparación de actualización. Comparar IDs compactos y dispersos. Medir consultas de salas/puertas, repetición de observaciones, cantidad de deltas y aplicación/inversión.

Para viaje: mapa completo de referencia, alternativas de costo distinto, empates y puertas recordadas que cambian tras observación. Medir cálculo completo del paso, incluida adaptación de fuente, sin red/renderizado. Incluir coste de preparación separado, sin ocultar reconstrucciones por paso. Repetir inventario e historial de P1 con la nueva carga. Documentar semilla, entorno, unidades, tamaño y resultados en DECISIONES.md solo después de ejecutar.

## Riesgos y alternativas

Véase [research.md](research.md). No se solicita excepción a estructuras propias. El riesgo de comenzar conexiones antes de acordar sus datos es mayor que el de mantener temporalmente un módulo independiente. Este plan no promete ausencia de conflictos futuros ni cumplimiento de 5 ms sin mediciones.
