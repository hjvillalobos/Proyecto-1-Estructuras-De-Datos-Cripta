# Contratos de integración y frontera temporal A–D

**Fecha:** 2026-11-02. Documentación de Plan, no interfaces implementadas. [Modelo](../data-model.md), [requisitos](../spec.md). Nombres descriptivos revisables; ningún componente de B/C/D se considera disponible por aparecer aquí.

**Adenda 2026-11-06.** Persona A adopta la frontera temporal para compatibilidad con `historia <t>`. La validación de integración con Persona D y los entregables de la tabla siguen pendientes.

**Actualización documental:** 2026-11-05, I1. Cada fila siguiente es un entregable independiente. Registrar responsable, alcance exacto, fuente/evidencia y fecha antes de cambiar su estado; una propuesta o una solicitud enviada no equivale a aceptación. La tarea T003 consolida este registro, pero sus consumidores solo esperan sus filas concretas. No se requiere completar todas las filas para acreditar una sola. El estado de cada entrega figura en la tabla.

| ID | Responsable del acuerdo/entrega | Evidencia verificable requerida | Consumidores principales | Estado |
| --- | --- | --- | --- | --- |
| E-B-COSTOS | B con A | B debe demostrar cómo llegan al motor de A los costos válidos de las salidas, con identidad y versión de cripta verificables y sin HTTP durante la búsqueda. El profesor confirmó, según el usuario, que el costo ausente vale 100 y se asume simétrico. [Aclaración y límites de Q2](../research.md#aclaración-del-profesor-sobre-q2). La aceptación es independiente de E-B-RANGO. | T013, T014, T025 | Entrega de B confirmada el 2026-11-09. Consumo por el motor verificado para las entradas válidas probadas el 2026-11-11. Q2 sigue abierta. |
| E-B-RANGO | B con A | Suministro y acceso verificables al rango de cazadores, con identidad y versión, sin HTTP durante la búsqueda. B debe preservar tres estados: entero válido (límite inclusivo), `null` explícito (sin tope de costo) y campo ausente (tratamiento pendiente en Q1). También sigue pendiente el tratamiento de valores inválidos. Aceptación independiente de costos. | T025; no T013/T014 | Entrega confirmada para los datos válidos probados el 2026-11-09. |
| E-BC-PUERTA | B/C/A | Identidad de puerta, lectura de ambos extremos y coherencia de cambios reales. | T029, T032 | PENDIENTE |
| E-C-RUTA | C con A | Fuente filtrada, firmas/modos/estados de consulta y criterios de aceptación acordados. | T023, T024 y solo las extensiones filtradas que lo usen | PENDIENTE |
| E-C-DESPACHO | C con A | Punto de conexión del cazador, firma y conservación de decisiones existentes. | T025 | PENDIENTE |
| E-C-OBS | C con A | Observaciones de entrada/puertas/antorcha y sus efectos de conocimiento definidos por C. | T032 | PENDIENTE |
| E-C-UNDO | C con A | Uso acordado de historial/deltas y límites de reversión del motor. | T032, T034, T035 | PENDIENTE |
| E-D-CAMBIOS | D con A | Sobre reconstruible, identidades, tiempo/secuencia/azar y puntos de captura. | T035 | PENDIENTE |
| E-D-RESTAURA | D con A | Contrato y entrega utilizable de carga/restauración, sin exigir a A implementarla. | T034 | PENDIENTE |
| E-D-MEDICION | D con A | Función de A acordada, conexión sin vista entregada por D y evidencia de recepción. | T045, T046 | PENDIENTE |

Q1/Q2 y Q3 tienen registros de evidencia separados en research.md. A puede describir estos acuerdos con autorización documental; no puede aprobar por B/C/D, resolver preguntas oficiales ni implementar sus entregas.

**Corrección I1/I5/C2 posterior al segundo Analyze, 2026-11-05:** hay diez entregables independientes. E-B-COSTOS y E-B-RANGO sustituyen el entregable agrupado anterior; ambos estaban pendientes en esa fecha. Una comunicación sobre el esquema no acredita suministro/acceso efectivo. T027 necesita T024 para su cierre completo; una ejecución parcial del núcleo no completa el contrato de C ni la tarea.

## A–B: entrada de datos

**Evidencia de B del 2026-11-09.** Las dos [pruebas de entrega](../../../tests/test_entrega_datos_terreno.py) usan el cliente HTTP con transporte simulado, el almacén en disco y una reapertura con un cliente offline nuevo. Se comprueban la cripta `prueba`, su versión `v1` y la versión de catálogo `cat1`.

- **E-B-COSTOS.** El grafo de A recibe 250 en ambos sentidos del tramo con costo declarado y 100 en ambos sentidos del tramo con costo omitido. La página en disco conserva la omisión y el resultado se reproduce offline.
- **E-B-RANGO.** A puede consultar `catalogo.ficha_preparada(tipo_catalogo).atributos["rango"]`. Para una ruta de costo 350, la decisión del cazador es mover con rango 350 y esperar con rango 349. La consulta y la búsqueda se verificaron sin leer fichas de disco ni realizar HTTP, también después de reabrir la cripta.

Para reproducir ambas entregas desde la raíz del repositorio, ejecutar `python -m unittest -v tests.test_entrega_datos_terreno`. A revisa cada resultado de forma independiente. Q1 y Q2 siguen abiertas para los datos fuera de los casos verificados.

**Evidencia integrada de A del 2026-11-11.** T013 usa el motor real de A con el paquete de B `prueba` / `v1` / `cat1` reabierto offline. Los movimientos del jugador a velocidad 100 usan 250 para la salida con costo declarado y 100 para la salida sin el campo. La agenda programa `t=250` y `t=350`. T014 verifica por separado el consumo de ambos costos con un rastreador real y el fixture sintético offline de A. El primer turno conserva el intervalo inicial de 100 y los movimientos programan los siguientes turnos en `t=350` y `t=450`. Ambas pruebas verifican cero solicitudes HTTP. La evidencia cubre esas entradas válidas. El tratamiento de `costo=null`, valores inválidos y datos inconsistentes permanece abierto en Q2.

**Evidencia integrada de T025 del 2026-11-11.** El motor de A accede a fichas residentes mediante `GestorCatalogo.ficha_preparada()` y distingue el entero válido de `null` explícito, sin HTTP ni lectura de fichas de disco durante la decisión. En turnos reales se verificó persecución con rango 350, espera con 349 ante la misma ruta de costo 350 y persecución con `null` explícito por una ruta de costo 400. El tratamiento del rango ausente o inválido permanece pendiente en Q1. El despacho de A conserva la firma y el comportamiento del callback de C para guardián, errante y rastreador. E-C-DESPACHO sigue pendiente de confirmación de Juan. La prueba de puerta cerrada comprueba el estado del arco recorrido; la coherencia entre extremos sigue pendiente en E-BC-PUERTA.

- B provee esqueleto completo con versiones de cripta, IDs, conexiones y costos; fichas de enemigos y rango ya disponibles sin red dentro de rutas.
- Para datos válidos: costo ausente equivale a 100, declarado entero ≥1, igual en ambos sentidos; un rango entero válido limita el costo en forma inclusiva y un `null` explícito indica búsqueda sin tope de costo, según la [aclaración del profesor](../research.md#aclaración-del-profesor-sobre-q1). Q1 y Q2 conservan los casos pendientes de ausencia, invalidez o inconsistencia que correspondan.
- A recibe una vista de datos de juego; desconoce si origen fue HTTP u offline. B administra presupuesto, UUID, lotes, versiones, fichas retenidas y errores de adquisición.
- Salida ponderada propuesta: origen/dirección/destino/costo/referencia de puerta. Identidad de puerta entre extremos y sincronización deben acordarse antes del cache de A. A no copia unilateralmente el costo de un extremo al otro.
- Si cambia cripta/versión se reconstruye identidad del grafo; no reutilizar índices de una versión distinta.
- Pendiente con A y B: acordar cómo representar y reportar datos fuera de los casos válidos cubiertos por las pruebas.

**Comunicación de B sobre OpenAPI 1.1.0:** el usuario transmite que B encontró Enemy.rango opcional y nullable, entero ≥1 cuando tiene valor, sin default ni obligación adicional para cazador; Exit dirigido con costo opcional y nullable, entero ≥1 cuando tiene valor, sin default ni garantía de simetría declarados. No disponemos de copia verificable ni fragmentos originales: esto no es verificación independiente ni contrato aprobado. El [contraste y procedencia](../research.md#comunicación-reportada-de-b-sobre-openapi-110) mantiene la autoridad de Parte II §§3.1–3.2: costo ausente 100, igual en ambos sentidos y ficha de cazador con rango. El rango ausente o inválido sigue pendiente en Q1. El costo `null` y las inconsistencias siguen pendientes en Q2. El rango `null` explícito se rige por la aclaración del profesor y debe distinguirse del campo ausente.

## A–C: ruta y despacho

**Consulta conceptual propuesta:** fuente de grafo, origen, destino, modo de límite y contexto de validez. Los nombres siguientes describen un protocolo por acordar con C; no son interfaces aprobadas ni implementadas.

- `ACOTADA(limite)`: costo máximo explícitamente suministrado para una consulta de cazador con datos válidos; Q1 no queda resuelta por esta notación.
- `SIN_LIMITE`: ausencia explícita de tope de costo para «ir a», sin usar un entero enorme como falso infinito. No es el valor predeterminado del rango de un cazador. C entrega exclusivamente salas exploradas y arcos que recuerda abiertos; sin límite de costo no significa sin filtro de conocimiento. La búsqueda puede recorrer toda la región alcanzable de ese subgrafo y se evalúa con el presupuesto de «ir a» de la capacidad de C.

**Resultados propuestos, mutuamente excluyentes:**

| Estado conceptual | Condición verificable | Datos del resultado |
| --- | --- | --- |
| `LLEGADA` | Origen y destino son la misma sala admitida por la fuente. | Distancia 0, sin primer paso ni movimiento; no consumir tiempo. |
| `RUTA_VALIDA` | Se demuestra ruta óptima y, en modo acotado, distancia ≤ límite. | Primer vecino/dirección, costo del arco atravesado y costo total mínimo; desempate por menor ID del primer vecino. |
| `SIN_RUTA` | Se demuestra que el destino no es alcanzable en la fuente suministrada. | Sin paso; evidencia de búsqueda completa de la región alcanzable, sin ramas pendientes omitidas por límite, o certificado exacto vigente. |
| `SIN_RUTA_DENTRO_LIMITE` | Se agotó correctamente la búsqueda acotada sin alcanzar destino y hubo ramas excluidas por costo. | Sin paso; no existe ruta de costo ≤ límite. Existencia de una ruta más costosa: no determinada. |
| `FUERA_LIMITE` | Existe evidencia exacta vigente de una distancia mínima finita mayor que el límite. | Sin paso y distancia certificada > límite; no se obtiene mediante un recorrido global adicional para una consulta pequeña. |

Una búsqueda limitada por sí sola no siempre permite distinguir un destino desconectado de uno alcanzable fuera del rango. `SIN_RUTA_DENTRO_LIMITE` expresa precisamente esa incertidumbre; no debe etiquetarse como `SIN_RUTA` ni como distancia finita conocida. `FUERA_LIMITE` solo puede devolverse con evidencia suficiente ya disponible y válida, no por inventar una distancia o ampliar automáticamente la búsqueda. La implementación base no necesita producir ese estado para cumplir las reglas del cazador.

Para el cazador, `SIN_RUTA`, `SIN_RUTA_DENTRO_LIMITE` y `FUERA_LIMITE` se traducen en esperar con costo 100. La coincidencia con el jugador se resuelve como ataque antes de consultar rutas; `LLEGADA` no sustituye esa regla. Para el viaje de C, `LLEGADA` significa destino alcanzado y `SIN_RUTA` ausencia de ruta conocida en su fuente filtrada. La consulta no mueve actores, no programa eventos, no consume azar ni modifica el conocimiento.

Validación de contrato propuesta: origen=destino; ruta dentro del límite y exactamente igual a él; destino desconectado en modo sin límite; agotamiento acotado con ramas excluidas; y distancia certificada mayor al límite. En «ir a», comprobar que una ruta disponible solo por salas no exploradas o puertas reales que no se recuerdan abiertas nunca aparece como ruta válida. Estos son escenarios previstos, no pruebas implementadas ni permiso para añadir mocks.

- Para A: fuente del esqueleto completo y puertas reales actuales; independiente del contenido descargado.
- Para C: fuente distinta con solo salas exploradas y puertas recordadas abiertas. Identidad/revisión separada de la real. No filtrar solo al mostrar un resultado ya calculado sobre información prohibida.
- C conserva sus tres comportamientos. Propuesta de conexión: A detecta cazador en despacho propio y mantiene la firma actual de decidir_accion para los demás; revisar con C si conviene callback común antes de tocar enemigos.py. No modificarlo unilateralmente.
- El motor de A ejecuta el paso ordinario; el viaje de C llama acciones ordinarias, recibe resultado/daño/enemigos/motivo de detención y recalcula conforme a su propia spec.
- A emite entrada/observación de puerta/antorcha; C define cambios de conocimiento y sus deltas. Una antorcha revela esqueleto de vecinas, no activa su contenido.
- Pendiente: firma, tipos compartidos, observación desde ambos extremos, orden de notificaciones y tratamiento de rollback. No se implementan contratos nuevos de C en esta fase.

## A–D y C–D: cambios reconstruibles

Propuesta de sobre conceptual de cambio: identidad estable de entidad, campo u operación, valor anterior/nuevo, instante virtual y orden semántico. Debe cubrir posición, vida, efectos, puertas, eventos creados/cancelados/extraídos, secuencias y estado de azar donde corresponda. No entregar referencias Python/callbacks como si fueran persistibles.

- A instrumenta su motor; C entrega inventario/conocimiento. D define agregación, serialización, checkpoints y reconstrucción, sin deducir reglas del motor.
- **Decisión técnica de Persona A.** El estado de decisión en t debe reflejar el cierre de los eventos automáticos de t en orden tiempo/secuencia y dejar pendientes los de t+1. Si el jugador 10 precede al enemigo 11 en t=100, el daño se refleja antes de la siguiente decisión. En el orden inverso también se refleja. La derrota termina la partida antes de otra decisión. Queda pendiente validar que esta frontera corresponda al estado anterior a la acción en la línea de tiempo de D, conforme a P2 §3.6 y el Apéndice B. [FR-020 y A14–A18](../spec.md#frontera-temporal-del-jugador).
- **E-D-CAMBIOS sigue pendiente.** Queda por acordar la numeración de acciones, los puntos de captura, el formato serializable, el rollback/retroceso y el tratamiento de empates en la reconstrucción.
- C/D coordinan recorte tras pergamino; A invalida todo derivado de rutas al restaurar. Época del cache no es secuencia semántica ni se rebobina para identificar estados viejos como nuevos.
- D versiona formato de guardado; preservar o rechazar/migrar explícitamente formatos anteriores. No añadir campos a snapshots.py ni alterar persistencia desde A sin acuerdo.
- D recibe costo de salidas y tipo cazador para presentación; si necesita recurso gráfico debe consultarlo. A no genera ni reemplaza arte.
- D conecta funciones de medición de A a bench.py y revisa ejecución sin vista. El replay actual sin GUI instancia VistaConsola; no usarlo como certificación headless hasta revisión de D.

### Primer caso H3 con motor real

Parte II §3.6 y el Apéndice B exigen que la consulta por tiempo incluya todos los eventos hasta ese instante y preceda a la decisión que coincida con él. `historia #k` reconstruye el estado anterior a la acción `k`. La propuesta valida FR-006, FR-014, FR-018 y FR-020 en un caso acotado. No cambia reglas funcionales ni el estado pendiente de E-D-CAMBIOS y E-D-RESTAURA.

**Datos y aceptación.** Usar `motor_terreno()` con guardián y salida al este sin campo `costo` (100 según Parte II §3.1). Capturar la vida inicial `V0` en sala 100, ejecutar `mover E` como acción #1 y, al cerrar `t=100`, guardar como `V1` la vida observada tras el ataque. Con el contador preparado por la prueba H3, se procesa el turno del jugador con secuencia 10 antes del ataque del guardián de destino con secuencia 11. Ejecutar `esperar` como acción #2 para que su ordinal exista. Contrastar:

| Consulta | Reloj | Sala | Vida |
| --- | --- | --- | --- |
| `historia 99` | 99 | 101 | `V0`, sin daño del ataque de `t=100`. |
| `historia 100` | 100 | 101 | `V1`, con el daño de secuencia 11 aplicado una vez. |
| `historia #2` | 100 | 101 | `V1`, antes de aplicar `esperar` o sus eventos posteriores. |

**Interfaz acotada.** `proyeccion_h3()` captura valores inmutables de `sala = (id, nombre)` y `jugador = (vida, vida_max, ataque, defensa, velocidad)` para construir la base antes de la primera acción. `ejecutar(..., registrar_h3=receptor)` habilita explícitamente el productor de prueba para `mover` y `esperar`. El receptor recibe reloj inicial, reloj final, ordinal, cambios inmediatos y eventos en el orden del motor. Cada cambio contiene clave y valores anterior/nuevo. Cada evento contiene su tiempo y secuencia reales y una tupla de cambios, vacía si no altera la proyección. El adaptador de prueba construye los tipos de D y llama a `registrar_accion`, que deriva el ordinal de las acciones aceptadas. `modelo/juego.py` conserva tipos propios de A.

**Publicación y fallos.** D confirmó, según la comunicación del usuario, que `registrar_accion` valida todo el lote antes de aplicar cambios. Un `ErrorHistoria` de validación conserva el estado, reloj y ordinal de D, incluso si el lote comienza con un delta válido. A entrega el lote una sola vez, después de cerrar la frontera FR-020 y antes de `cerrar_turno()`. Si la validación falla, el rollback existente revierte el turno de A y su ordinal, descarta los mensajes y propaga el error sin recortar D. Las excepciones inesperadas también se propagan sin reintento. La garantía de D solo cubre rechazos de validación.

**Límites.** El adaptador de prueba consulta la línea de tiempo real de D sin activar `integrar_historia()` ni su guardado/carga. La proyección de sala y jugador sirve a las tres consultas del caso. El mapa, el inventario, los efectos, el recorte por pergamino, la carga y el flujo histórico completo quedan fuera del caso. Los acuerdos de proyección completa y restauración siguen pendientes. El fixture no requiere entregas nuevas de B o C.

## Criterios de acuerdo pendientes

Revisión cruzada A↔C y B↔D; equipo revisa tipos/guardado y determinismo. Ningún texto de este documento constituye consentimiento de los compañeros. Q1/Q2 requieren evidencia; Q3 requiere referencia oficial. Todos los cambios de archivos fuera del alcance de A siguen requiriendo autorización.
