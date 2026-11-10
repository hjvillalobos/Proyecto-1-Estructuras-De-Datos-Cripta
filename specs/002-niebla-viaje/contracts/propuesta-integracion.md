# Propuesta de integración de C con A y D

Fecha: 2026-11-08. Estado: propuesta para revisión; no contrato aceptado ni implementación. Complementa la especificación, sin sustituir clarify, plan, tasks o analyze. Las firmas siguientes son candidatas de diseño y no funciones disponibles.

## Evidencia y límites

Se contrastaron los contratos de A en `origin/feature/motor-eventos` y de D en `origin/004-linea-tiempo` disponibles tras la última actualización de referencias. Los mensajes del grupo del 2 y 8 de noviembre confirman constitución compartida en main y documentación por capacidad. No constituyen aprobación de estas firmas. Las capturas de análisis son resultados reportados por terceros, no pruebas repetidas aquí.

Se utiliza la constitución compartida; no se propone otra. La duda de antorcha Q1 sigue abierta. C no convierte costos null en 100 ni corrige asimetrías por iniciativa propia. El desarrollo independiente podrá usar datos válidos del enunciado después de completar sus fases documentales.

## A → C: observaciones y resultado del paso

| Operación candidata | Entrada | Resultado y límites |
| --- | --- | --- |
| `registrar_entrada(observacion, contexto)` | Sala, nombre, salidas con costos válidos, puertas físicamente observadas, estado de antorcha; tiempo y orden del motor | C actualiza conocimiento y devuelve cambios. No activa contenido de vecinas. FR-001–006, FR-014. |
| `registrar_observacion_puerta(observacion, contexto)` | Identidad compartida de puerta, extremo ocupado y estado observado | Actualiza un único recuerdo desde cualquiera de los extremos. Un cierre remoto no es observación. FR-004. |
| Resultado de movimiento ordinario | Aceptado, origen/destino, entrada efectiva, daño ocurrido durante el paso, presencia de enemigos al entrar, partida terminada, tiempo de cierre | C decide continuación únicamente después del cierre del intervalo; daño es un hecho, no diferencia de vida final. FR-009–011. |

Identidad de puerta y correspondencia de extremos requieren acuerdo A/B/C; no se supone que dos extremos se identifican solamente ordenando IDs, pues podrían existir conexiones paralelas. A conserva propiedad del reloj y orden de eventos. Si falla una acción, debe acordarse cómo descartar sus cambios sin publicarlos como historia confirmada.

## C → A: búsqueda y despacho

Consulta candidata: `consultar_ruta(fuente_conocida, origen, destino, SIN_LIMITE)`.

- C suministra exclusivamente salas exploradas y salidas recordadas abiertas. No se busca sobre el mapa real para filtrar el resultado después.
- A devuelve `LLEGADA`, `RUTA_VALIDA` o `SIN_RUTA`; una ruta válida incluye primera dirección/vecina, costo del primer arco y costo total. El empate usa menor ID de primera vecina. FR-008.
- La fuente conocida necesita identidad y revisión independientes del estado real. Una restauración no debe permitir reutilizar una ruta de otro estado por coincidencia accidental de revisión. La estrategia concreta queda para el plan.
- La consulta no consume tiempo, azar ni solicitudes de red. A debe confirmar soporte de fuente filtrada y consulta sin límite; sus rutas actuales del cazador no se declaran suficientes sin esa comprobación.
- Propuesta de despacho: A reconoce al cazador en su motor; mantiene la llamada existente a los comportamientos de C para guardián, errante y rastreador. A/C revisan antes de modificar `enemigos.py`.

## C → D: mapa y control del viaje

Propuesta de núcleo: `consultar_mapa()` devuelve registros de salas exploradas y avistadas con solo información permitida. D formatea esos registros para consola/interfaz. Para compatibilidad con el consumidor actual de D, un adaptador puede ofrecer `mapa_conocido()` como líneas; ese formato de presentación no sustituye el estado reconstruible.

Propuesta de viaje por pasos:

1. `iniciar_viaje(destino)` valida destino explorado sin consumir tiempo.
2. `proponer_paso()` devuelve llegada, ausencia de ruta o dirección calculada con conocimiento vigente.
3. El controlador ejecuta exactamente un movimiento ordinario y registra ese movimiento.
4. `registrar_resultado_paso(resultado)` evalúa llegada, enemigos, daño y fin de partida antes de permitir otra propuesta.
5. `cancelar_viaje()` impide continuar; el pergamino usa el retroceso ordinario del último paso, no revierte todo el viaje.

**Diferencia a revisar con D:** su contrato propone `viajar_hasta(destino, mover)` y un callback que devuelve un booleano. Ese booleano por sí solo no informa daño seguido de curación, enemigos al entrar ni fin de partida. Hay que acordar un resultado enriquecido o una fuente explícita de esos hechos. También debe existir oportunidad de procesar el pergamino entre pasos: no implementar un bucle bloqueante que impida interrumpir el viaje. No se cambia su consumidor unilateralmente. FR-007–013, FR-015.

Si coinciden llegada, daño y enemigos, todas las causas deben quedar disponibles; el orden de presentación de un único motivo se acordará sin permitir otro movimiento por esa elección.

## C → A/D: conocimiento e inventario reconstruibles

Sobre candidato de cambio: ámbito, identidad estable, operación/campo, valor anterior, valor posterior, tiempo y orden del motor. Representación concreta y tipos admitidos se acuerdan con D. No contiene referencias a nodos vivos ni funciones de Python.

| Ámbito | Información mínima propuesta | Verificación |
| --- | --- | --- |
| Sala | Identidad y estado anterior/posterior de conocimiento; información revelada que cambió | N4/N5; revelar dos veces no pierde lo que ya se conocía. |
| Puerta | Identidad y recuerdo anterior/posterior, diferenciando ausencia de observación | C03 y N2; estado real remoto no reemplaza memoria. |
| Inventario | Identidad de instancia, altas/bajas, posición u orden afectado, equipamiento y cursor cuando cambien | Reconstruir y revertir recogida, descarte y equipamiento conservando orden e identidad. |

Hallazgo en el código actual: `RegistroTurno` conserva funciones de deshacer, incluidas lambdas. Sirven para el retroceso en memoria, pero no son una entrega serializable a D. Se debe diseñar captura de datos de los cambios, sin copiar el inventario o mapa completos después de cada acción ni prometer que los callbacks existentes ya resuelven historia.

La excepción de pergaminos sigue vigente para retroceso. Su existencia y cambios sí deben poder representarse históricamente: A/C/D acuerdan qué correcciones sobreviven al recorte. El mismo cambio se aplica una sola vez al estado vivo; D reconstruye sobre estado independiente. FR-014–016.

La base inicial completa se entrega al iniciar historia; los cambios posteriores son incrementales. D conserva responsabilidad del formato binario y checkpoints. El adaptador de inventario debe contrastarse con sus claves propuestas `inventario:<orden>`: un cambio de posición no puede dejar entradas antiguas ni duplicar instancias. C aporta datos de estado; D decide su codificación y A coordina la restauración del motor.

## Casos de aceptación del contrato, todavía no ejecutados

| Caso | Resultado esperado | Requisitos |
| --- | --- | --- |
| Ruta real más corta por sala desconocida | No se usa; solo se elige ruta conocida válida | FR-003, FR-008 |
| Cierre remoto y posterior observación desde otro extremo | Recuerdo permanece hasta observación; después ambos extremos coinciden | FR-004 |
| Paso con daño y posterior curación | Detener aun si la vida final iguala la inicial | FR-011 |
| Pergamino entre dos pasos | Cancelar continuación, revertir solo último paso | FR-015 |
| Equipar objeto en posición intermedia y reconstruir antes/después | Identidad, orden, cursor y equipamiento coinciden con cada estado | FR-016 y continuidad de P1 |
| Revertir revelación que incluye salas previamente exploradas | Solo cambios de esa acción se invierten | FR-014 |

## Aceptaciones pendientes y siguiente entrega

### Actualización del 2026-11-09

A en 33d97ac ya permite `limite=None` en buscar_ruta. La limitación numérica descrita en la revisión del 8 de noviembre queda superada; la fuente filtrada sigue pendiente. D en 02da6b6 valida el lote completo antes de aplicarlo. Sus 14 pruebas se ejecutaron en copia aislada y pasaron. Los mensajes A/D aportados por el usuario acuerdan cerrar eventos empatados antes de registrar, y revertir el estado vivo del motor ante ErrorHistoria de validación sin recortar historia no modificada. Esta garantía no cubre cualquier excepción o fallo de infraestructura.

I3 propone claves `conocimiento:sala:<id>` y `conocimiento:puerta:<id>` para el estado interno histórico. No reemplazan `mapa:<id>` del resumen de D ni se presentan como nombres ya aceptados. Antes de conectar, D confirma claves/proyección y A incorpora los deltas en su lote, con rollback de conocimiento junto a reloj, agenda y azar. El adaptador convierte datos; no registra una segunda acción de C.

### Contraste con código disponible tras actualizar referencias

Revisión del 2026-11-08: D avanzó a `97ee910`, con paquetes offline y conexión del benchmark de resolubilidad. Su contrato de interfaces no cambió en ese incremento; T003, T010 y la aceptación conjunta siguen pendientes. Las ramas de A/B y main no recibieron novedades en esta consulta.

- En D, `Controlador._mapa` obtiene `mapa_conocido` del modelo y une las líneas devueltas. El adaptador de presentación propuesto debe conservar esa forma de consumo si se acuerda mantenerla.
- `Controlador._viaje` llama `viajar_hasta(destino, mover)`; `mover` devuelve un booleano. Se confirma en código la necesidad de coordinar las señales adicionales y el control entre pasos descritos arriba.
- D ya define `CambioHistorico(clave, anterior, nuevo)` con extremos `ValorHistorico`, y `EventoHistorico(tiempo, secuencia, cambios)`. El plan de C debe estudiar un adaptador a esos tipos, evitando crear un segundo formato incompatible. Los cambios de C no deben duplicar tiempo/secuencia si el contenedor de D ya los aporta. Queda pendiente contrastar los valores permitidos y el estado completo de inventario con las necesidades de restauración.
- A ofrece `buscar_ruta(grafo, espacio, frontera, origen_indice, destino_indice, limite)`. La consulta conceptual anterior no es esa firma implementada. Antes de reutilizarla hay que revisar cómo construir una fuente filtrada y representar ausencia de límite; no renombrar su función ni asumir compatibilidad por parecido.

No se fusionaron ramas, no se ejecutaron las pruebas de D y no se considera probado el funcionamiento conjunto a partir de esta lectura.

- A: confirmar entrada/puertas, señales de resultado, ruta filtrada y despacho.
- D: confirmar mapa estructurado/adaptador, viaje interrumpible y datos reconstruibles de inventario/conocimiento.
- A/B/C: confirmar identidad de puerta con datos válidos.
- A/C/D: confirmar publicación del lote, fallo de acción, retroceso y restauración.

Registrar respuesta, fecha y alcance por acuerdo. Ninguna fila se considera aprobada por la existencia de este documento. Tras aclarar reglas y cerrar interfaces, preparar plan/tareas/análisis y priorizar conocimiento básico con pruebas antes de viaje completo. No se necesita fusionar todas las ramas para revisar esta propuesta.
