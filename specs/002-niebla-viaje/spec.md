# Feature Specification: Niebla de guerra y viaje automático

**Feature Branch**: `codex/002-niebla-viaje`
**Created**: 2026-11-08
**Status**: I1 e I2 implementados y probados; I3 comprobado contra historia real de D e I4/I5 (rutas y control local de viaje) contra rutas reales de A en copias aisladas. Capacidad completa pendiente de Q1, ejecución del viaje en el juego, conexión al motor y revisión cruzada.

**Actualización de alcance I1:** el usuario autorizó implementar lo independiente de sus compañeros. Se cierra la aclaración del incremento de conocimiento básico descrito abajo; la capacidad completa continúa pendiente. La autorización posterior de I2 amplía ese alcance únicamente con las operaciones independientes indicadas en su apartado.
**Input**: Persona C según asignación confirmada por el usuario. Preparar su capacidad conforme a Parte II §§3.3–3.4, 5.3, 5.6, 6.1 y Apéndice B.

## User Scenarios & Testing

### I10: origen sin salida conocida transitable

Optimización local de FR-008/010/012/014/017, motivada por I9. C42: si el destino es distinto y el origen no tiene ninguna salida conocida transitable, responder sin ruta sin recorrer el resto del mapa. Incluye puertas cerradas/no observadas y vecinas no exploradas. Reabrir, explorar o revertir debe permitir consultar de nuevo sin conservar un rechazo obsoleto. Si origen y destino coinciden, se conserva llegada; una salida alternativa transitable no debe descartarse. No cambia las reglas ni acredita por sí solo PR-001.

### I9: diagnóstico de rutas con alternativas

Alcance autorizado: ampliar la evidencia de FR-008/010/014/017 y PR-001 sin cambiar reglas ni contratos compartidos. La copia local no contiene la cripta de 300 salas citada por D; no se sustituye por una carga sintética al certificar el requisito.

- C40: con semilla fija, mapas con alternativas y salidas dirigidas conservan el resultado de la búsqueda anterior en consultas nuevas, reutilizadas y posteriores a una observación/reversión.
- C41: la medición separa preparación, primera búsqueda, pasos sucesivos y recálculos por puertas; identifica tamaño, semilla, entorno, muestras, media y máximo. Rechaza cualquier diferencia de resultados y comprueba que consultar no cambie el conocimiento.

Aclaración local: el mapa completo conocido y las puertas abiertas son condiciones iniciales del diagnóstico, no reglas de exploración. Las puertas sintéticas tienen identidad explícita. No se interpreta la identidad de puertas de la API ni se implementa Q1. No se afirma cumplimiento de PR-001 sin referencia oficial e integración.

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
- I1 e I2 cuentan con alcance aclarado, plan, tareas, revisión de consistencia e implementación local. Eso no cierra las fases ni la aceptación de la capacidad completa; Q1 y acuerdos de integración siguen abiertos.

## Clarifications pendientes

### I8: reutilización segura de rutas

Optimización autorizada el 2026-11-10; conserva FR-008/010/014/017 y busca mejorar PR-001 sin cambiar reglas. Una ruta reutilizada debe coincidir con recalcular desde cero, incluidos costo y desempate. Todo cambio de conocimiento, aplicación o reversión invalida información previa. Las consultas no cambian la partida. Primera búsqueda, reutilización y cambios frecuentes se miden por separado; una media favorable de consultas reutilizadas no acredita el límite completo.

- C37: varios pasos hacia el mismo destino, con conocimiento estable, coinciden con búsqueda independiente, también en grafos dirigidos y con empates.
- C38: abrir/cerrar, explorar, aplicar y revertir cambios nunca reutiliza distancias obsoletas. Un lote rechazado conserva el estado y la corrección de consultas posteriores.
- C39: cambiar de destino, consultar un origen fuera de la región calculada o sufrir un fallo de búsqueda no reutiliza resultados incompletos.

### I7: datos históricos del inventario

**FR-020:** conservar identidad, tipo, orden, selección, equipamiento y estado encendido de los objetos al reconstruir inventario. Registrar solo cambios de la operación; no copiar todo el inventario por acción ni sustituir el retroceso existente.

Alcance aclarado: adaptador local, sin modificar inventario, motor ni historia de D. El registro histórico incluye pergaminos; la excepción de retroceso la aplica el motor mediante las correcciones de D. Capturar antes y terminar después de una sola operación de recoger, quitar, mover/equipar o seleccionar. No agrupar mutaciones independientes bajo una captura ni usarla como restauración del estado vivo.

- C33: recoger, quitar y equipar desde el medio reconstruyen orden, identidad, selección y equipo antes/después (FR-020/016 parcial).
- C34: rechazo por capacidad no produce cambios; el lote incoherente es rechazado por D sin alterar historia (FR-020/017).
- C35: consumir un pergamino se representa como corrección al recortar, sin devolverlo ni modificar las reglas existentes de retroceso (FR-020/014 parcial).
- C36: capturar una operación local no recorre el inventario completo y los valores registrados no cambian al mutar después los objetos vivos (FR-020).

### I6: primera comprobación con motor real

Alcance del 2026-11-10, tras revisar los cambios remotos: comprobar el control de viaje con un movimiento ordinario real en el caso acotado H3 del guardián de A. No se modifica el motor ni se publica una fachada completa de viaje a partir de señales incompletas. FR-009/011/017 y FR-016 parcial.

- C31: con camino previamente explorado y un guardián en la primera sala de paso, el movimiento procesa eventos empatados, entrega su lote histórico y detiene el viaje antes del segundo paso. Historia conserva la vida anterior al ataque en t=99 y la posterior en t=100, junto con el conocimiento inicial de C. Consultar otra propuesta después de detenerse no cambia reloj ni contador.
- C32: si la historia rechaza el lote, el motor revierte su movimiento y el control se cancela sin aceptar un resultado ni ejecutar otro paso. La historia permanece intacta. El escenario usa el rechazo de validación esperado, no promete recuperación ante cualquier excepción.

Los datos del escenario son sintéticos y están separados de producción. Sus señales de daño se comprueban mediante el delta del ataque identificado en H3; esto no define un detector general que pueda omitir daño y curación dentro de un mismo evento. La entrega general de daño, enemigos al entrar y cambios de conocimiento sigue pendiente de acuerdo A/C/D.

### I5: control local del viaje por pasos

Autorizado por el usuario con «adelante»: iniciar, proponer un paso, recibir hechos y cancelar sin conectar motor/controlador todavía. FR-009–012/015/017/018 se verifican solo en esta coordinación local.

Aclaración: no se ejecutan movimientos ni retrocesos desde este componente. Cada propuesta espera un único resultado antes de permitir la siguiente. El resultado llega después del cierre del intervalo del motor y de actualizar el conocimiento. La cancelación invalida cualquier propuesta pendiente y solo una nueva orden explícita inicia otro viaje. El controlador debe cancelar antes de aplicar un pergamino entre pasos; C no consume el objeto ni revierte acciones. Los resultados tardíos, duplicados o incompatibles se rechazan sin modificar el control. Si un movimiento se rechaza sin entrada, se podrá volver a consultar desde el origen con observaciones actualizadas; no existe reintento automático. No se infiere daño de la vida final. Fin de partida impide continuar.

- C26: iniciar hacia destino no explorado rechaza; iniciar en el destino termina sin proponer movimiento. Proponer dos pasos sin resultado intermedio se rechaza (FR-007/009/012).
- C27: un resultado válido permite consultar el siguiente paso con conocimiento vigente. Una puerta recién observada cerrada causa ruta alternativa o detención sin ruta; no se abre por poseer llave (FR-010/012).
- C28: daño, entrada con enemigos, llegada o fin de partida detienen. Daño se conserva aunque haya curación posterior; causas coincidentes permanecen visibles (FR-011/018).
- C29: cancelar antes o después de un paso impide continuar; una respuesta anterior no reactiva un viaje cancelado ni uno reiniciado. La reversión externa no reinicia el viaje (FR-015 local/017).
- C30: resultados duplicados, de otro paso o con posición incompatible se rechazan sin alterar el estado. Consultar/proponer/cancelar no modifica mapa ni ejecuta acciones del motor (FR-009/017).

N3/N6 completos, replay, persistencia, antorcha y medición integrada permanecen pendientes. Estas reglas de coordinación no definen una nueva acción temporal del juego.

### Incremento I4: consulta de un paso sobre conocimiento

Autorizado el 2026-11-09: «Okay, sigamos con la otra parte», después de proponer rutas conocidas con el buscador de A. Incluye FR-007/008, la consulta de FR-010/012 y determinismo de FR-017; no ejecuta movimiento, antorcha, eventos ni un viaje completo.

Aclaración del alcance: origen y destino deben estar explorados. Destino inexistente o no explorado se rechaza sin revelar si existe. Origen inválido también se rechaza. Destino igual al origen produce llegada sin paso. Una puerta sin observación no es una puerta recordada abierta; queda excluida. Una salida sin puerta puede usarse si ambos extremos están explorados. Se consulta siempre el conocimiento vigente, también tras una reversión. No se decide Q1 ni se interpreta información de la API.

- C21 (N1, FR-007/012): destino avistado, desconocido o inexistente devuelve el mismo rechazo; origen igual a destino explorado devuelve llegada sin movimiento.
- C22 (C05, FR-003/008): un atajo por una sala no explorada queda excluido. Entre rutas conocidas se minimiza costo total, incluso con más pasos; los empates eligen la primera vecina de menor ID.
- C23 (N2 parcial, FR-004/008/010): puerta no observada o recordada cerrada no permite ruta; observarla abierta permite paso. Una observación posterior y su reversión cambian/restauran la consulta sin reconstruir la partida ni consultar el estado real.
- C24 (FR-008/017): ciclos, destinos desconectados, IDs dispersos y puertas paralelas conservan resultado válido y determinista. Costos grandes no introducen un límite artificial.
- C25 (FR-005/017): consultas repetidas y alternadas no cambian conocimiento ni crean acciones. Al revertir exploración deja de estar disponible una ruta que la necesitaba.

La comprobación de PR-001 permanece pendiente del mapa de referencia y del cálculo integrado. Se medirán cargas sintéticas como diagnóstico, separando preparación de consultas. Estos escenarios no acreditan N2 completo, N3 ni N6.

### Incremento I3: compatibilidad de conocimiento con historia

Autorizado el 2026-11-09: preparar y comprobar la conversión de cambios de conocimiento con la historia real de D, en un entorno aislado. No conectar el motor ni modificar los tipos de D.

- **FR-019**: Entregar el conocimiento inicial y sus cambios incrementales para que la historia conserve los estados anteriores y posteriores de salas y puertas. Distinguir una puerta nunca observada de una observada abierta. La conversión no modifica el conocimiento vivo ni registra acciones por sí misma.
- C18: una entrada revela una sala y avista su vecina; historia conserva el conocimiento inicial antes de la primera decisión y el actualizado después del paso. Tras registrar otra acción, la consulta anterior a esa segunda acción coincide con el cierre del primer paso.
- C19: un lote con cambios válidos de conocimiento seguido de un cambio incoherente es rechazado por historia sin alterar sus estados, reloj o número de acciones. Al revertir el lote local de C se recupera el conocimiento vivo previo; no se recorta historia por ese rechazo.
- C20: dos observaciones sucesivas de una puerta pueden reconstruirse en sus instantes respectivos; recortar una acción aceptada y revertir sus cambios locales conserva la frontera anterior.

El ensayo valida solamente conocimiento e historia. La reversión de reloj, agenda, azar y demás estado del motor sigue siendo responsabilidad de A. No demuestra guardado, interfaz, antorcha o viaje integrado. Los nombres de campos del adaptador son propuesta de C pendiente de aceptación por D; no se alteran los consumidores existentes.

### Incremento I2: pruebas, demostración y decisión de detención

Autorizado el 2026-11-09 para continuar trabajo independiente. No modifica la interfaz ni el estilo visual. Amplía C12/C13 con secuencias reproducibles, ciclos, componentes desconectados y puertas paralelas de identidad distinta. La demostración usa datos sintéticos separados del código del juego.

- **FR-018**: Evaluar, a partir de hechos explícitos de un paso, si el viaje debe detenerse por llegada, daño recibido, entrada con enemigos, ausencia de ruta conocida o cancelación. Conservar todas las causas coincidentes; su orden de presentación será fijo, sin prioridad que cambie la decisión. Esta evaluación no ejecuta movimientos ni retroceso y no modifica el conocimiento ni el reloj.
- C15: ante cualquiera de las causas de FR-018, el resultado impide continuar; sin ninguna causa permite continuar. Enemigos solo cuentan para esta condición si hubo entrada. Daño sigue siendo un hecho aunque la vida se recupere después.
- C16: causas simultáneas se conservan y el mismo conjunto de hechos produce el mismo resultado, sin mutar la entrada. Una cancelación suministrada impide continuar aunque también haya ruta. Un viaje cancelado no continúa automáticamente; la coordinación del viaje activo queda fuera de este incremento.
- C17: una secuencia larga de entradas/observaciones, reconstruida e invertida, coincide con un registro de referencia de prueba independiente. Dos puertas entre las mismas salas conservan recuerdos distintos; una región desconectada no se revela desde otra.
- **PR-004**: Medir memoria asignada al componente y tiempos de consulta de puertas y proyección, con carga/entorno/unidades documentados. La instrumentación de memoria y las mediciones de tiempo se ejecutan por separado. No se presenta como evidencia del límite de viaje completo.

I2 aclara solamente estas operaciones independientes. Q1 y los contratos de motor/controlador/persistencia siguen pendientes. FR-018 prepara parte de FR-011/015, pero no acredita esos requisitos integrados ni N3/N6 por sí solo.

### Alcance aclarado del incremento I1

- Autorización textual: «okay, entonces hagamos todo lo que no dependa de mis compañeros o sea util y no les cause conflicto».
- Incluye FR-001–005 y FR-017, y la parte local de FR-014: estados, avistamiento, observación física de puertas, proyección filtrada y aplicación/inversión de cambios de conocimiento. PR-002 se comprueba con carga local; no certifica PR-001.
- Excluye antorcha (Q1), búsqueda y ejecución de viaje, cambios de inventario/historial existentes, guardado y conexiones reales con A/D. No declara completos N1–N6 ni FR-016.
- El componente recibe esqueleto y observaciones explícitas. No infiere estado real de puertas por precarga. La sala inicial se explora al construirlo y sus puertas se conocen solamente mediante observaciones suministradas desde esa sala.
- La entrada física explora la sala y avista destinos directos; repetirla no degrada estados. Una observación de puerta exige que la sala indicada sea uno de sus extremos y ya esté explorada. El llamador deberá garantizar ocupación actual; el componente no mantiene una segunda posición del jugador.
- Los cambios permiten reconstruir y revertir exactamente el conocimiento correspondiente a la secuencia de acciones. Un lote incompatible se rechaza sin dejar modificaciones parciales.
- C12: dados cambios de varias entradas y observaciones, aplicar cada lote sobre un estado equivalente produce el mismo mapa; invertirlos en orden contrario recupera el inicial. Un lote incompatible no modifica ese mapa. FR-014, FR-017.
- C13: dados IDs dispersos y mapas de tamaños crecientes, el almacenamiento depende de la cantidad de entidades; una entrada procesa solo su sala y salidas, además de búsquedas de identificadores. PR-002.
- C14: datos internos incompletos o contradictorios se rechazan antes de construir el componente; esta precondición local no define cómo B debe tratar null, asimetría u otros problemas de la API.

**Q1 — puertas de salas reveladas con antorcha.** [NEEDS CLARIFICATION: ¿qué información recibe el jugador sobre una puerta que pertenece a una vecina revelada por antorcha, pero cuyos extremos nunca ha ocupado? §3.3 exige exploración de la vecina y memoria de la última observación, pero define observación estando en un extremo. Confirmar si queda sin observación utilizable para viaje o si la antorcha también permite observar esa puerta; no asumir el estado real como recuerdo.]

Esta pregunta requiere aclaración del enunciado o referencia oficial; una preferencia técnica no la resuelve. La revisión obligatoria de clarify podrá identificar otros casos antes de cerrar el diseño.

### Seguimiento de Q1

El usuario indicó: «okay, entonces dejalo como pendiente». Q1 permanece abierta; no se adopta ninguna de las interpretaciones como regla del juego. La revisión de la sección 3.3 y del reparto de C no encontró una aclaración expresa para puertas cuyos extremos nunca ocupó el jugador. El texto extraído del enunciado `Cripta - Parte II (3).pdf` coincide con el de la copia anterior.

El caso pendiente se limita a una puerta entre una vecina revelada y otra sala, sin observación física previa. La puerta que conecta la sala ocupada con esa vecina sí se observa desde la posición actual conforme a FR-004.

Se puede continuar revisando y preparando el conocimiento por entrada física, avistamiento, memoria de puertas observadas y cambios reversibles. Las decisiones y pruebas sobre información de puertas remotas reveladas por antorcha quedan pendientes de respuesta oficial. Esto no declara completa la fase de aclaración ni autoriza omitir plan, tareas y análisis antes de implementar.


## Consolidación compartida — 2026-11-14

La autorización de la usuaria amplió el alcance a todas las partes. La integración de producción, las decisiones conservadoras de antorcha/puertas, los benchmarks de A conectados a la CLI y la aceptación del conjunto se documentan en [integracion-completa.md](../004-linea-tiempo/integracion-completa.md). Los balances, gates de autorización y pendientes de entregas anteriores son históricos; no se inventa una respuesta oficial para preguntas del profesor ni se cambian marcadores de checklists de revisión.
