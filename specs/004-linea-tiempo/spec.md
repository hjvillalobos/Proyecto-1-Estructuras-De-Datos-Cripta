# Feature Specification: historia, persistencia y comandos de integración

> **Estado vigente de entrega:** las cuatro capacidades están integradas en `004-linea-tiempo`. Consultar [estado, trazabilidad y límites actuales](../../ESTADO_ENTREGA.md). Los balances y restricciones de autorización fechados anteriores son registros históricos, no bloqueos de la implementación actual. La revisión humana y los faltantes auténticos no se dan por resueltos mediante este aviso.


Responsabilidad: línea de tiempo e integración. Fuentes: enunciado §§3.6, 5.5, 6.1 y 7.3; reparto página 6. Estado: integrada en producción; aceptación y límites del cierre en integracion-completa.md. Rama: `004-linea-tiempo`. Creada: 2026-11-02.

## Objetivo y alcance

### VD-01 — diálogo de destino de viaje

El botón Viajar abre «Viajar a una sala», integrado con el tema oscuro/fantasía y botones Viajar/Cancelar. Ofrece únicamente salas exploradas de la proyección conocida; entrada numérica validada, mensaje claro sin revelar si un ID no permitido es avistado, desconocido o inexistente. Enter confirma solo un destino válido; Escape/X/cancelar conserva cola, viaje activo, estado, tiempo, archivos y log. La vista no busca rutas ni ejecuta movimiento: devuelve el ID al controlador, que conserva las reglas ordinarias de ir a. No se cambian diálogos de archivos ni la verificación inicial.

### RP-01..04 — replay gráfico independiente

- RP-01: Replay desde el menú o durante una partida gráfica abre otra ventana que reproduce los estados y acciones del log paso a paso, con inventario, mapa conocido, costos, efectos y animaciones ordinarias. Ofrecer pausa, velocidad y detener; no presentar el resumen textual de historia como repetición animada.
- RP-02: reconstruir con la fábrica completa y receptor de historia, respetando versiones, cargas incluidas en el log y pergaminos/recorte del pasado. Leer el log una vez al comenzar la reproducción; las acciones añadidas después no forman una reproducción en vivo. No anotar acciones de replay ni registrar puntajes o sobrescribir log/guardado.
- RP-03: proceso y sesión de datos separados de la partida original, con UUID/presupuesto propios y mismas opciones offline/caché/versiones. Cerrar o detener afecta solo la reproducción. Errores de versión, datos o acciones se informan en la ventana del replay, sin convertirlos en una partida distinta ni cerrar la original.
- RP-04: `--replay` y `--replay ... --hasta T` siguen sin instanciar vistas. Un modo explícito separado `--replay-grafico ARCHIVO` sirve a los botones de la GUI; no admite `--hasta` ni se mezcla con inicio/verificación. Comprobar ambas entradas GUI, controles, estado final/cargas/retroceso y rechazo de incompatibilidades; separar pruebas automáticas de inspección visual efectivamente realizada.

### UX-01..03 — abandonar y comprender el objetivo (seguimiento 2026-11-15)

- UX-01: Salir durante una partida gráfica ofrece Continuar, Reiniciar la misma cripta, Volver al menú y Cerrar el juego. Escape/cierre del diálogo equivale a Continuar. Cancelar conserva estado, viaje, cola, reloj, azar, guardado y replay; no es una acción del jugador. Reiniciar requiere elección explícita y prepara motor/precarga nuevos, misma cripta y política de semilla existente, sin sobrescribir guardados. El cierre de la ventana durante una partida activa usa esa elección; menú/replay/fin conservan sus cierres propios.
- UX-02: mostrar identidad de cripta y objetivo comprensible sin revelar salas desconocidas ni contenido remoto. Una cámara secundaria o el mayor ID no implica victoria. Si la sala de salida ya es conocida, puede identificarse; frente a su acceso explicar abrir con llave y luego cruzar. Llegar a una salida sin apertura acreditada explica cómo regresar al acceso, sin conceder victoria gratis.
- UX-03: contrastar población, activación y daño con datos reales y replay local de la usuaria sin modificar sus archivos. Comprobar victoria por llave/cruce en mapas resolubles y ambos extremos de una puerta recíproca cuando corresponda. No añadir enemigos ni aumentar daño/dificultad fuera del contrato. La comprobación automática y la inspección visual se reportan por separado.

Aclaración UX-03: la apertura con llave de una puerta física recíproca acredita ambos extremos compatibles; cruzar posteriormente hacia la sala de salida debe ganar sin exigir abrirla otra vez desde un lado específico. La acreditación conserva inversos, historia y binario; no se extiende a arcos ambiguos ni a puertas con llaves contradictorias. Se reproduce el fallo con apertura desde la sala de salida y regreso por la misma puerta, independiente de la confusión de sala20 del replay local.

El jugador puede consultar el pasado de su partida conservando intacto el presente y puede guardar y recuperar esa historia. Esta capacidad incorpora las entradas y presentaciones de capacidades realizadas por motor, verificador y conocimiento, sin duplicar sus reglas.

Queda fuera de esta capacidad implementar las rutas del cazador, el conocimiento del jugador, el viaje ni el algoritmo de resolubilidad. Sus interfaces y presentaciones sí forman parte de la trabajo de integración.

## Historias de usuario

US1, prioridad 1: como jugador quiero consultar un instante o el momento anterior a una acción para entender qué ocurrió sin alterar la partida.

US2, prioridad 1: como jugador quiero que retroceder descarte el futuro eliminado y que guardar/cargar conserve toda la historia vigente.

US3, prioridad 2: como evaluador quiero reproducir hasta un instante y verificar una cripta sin abrir interfaz interactiva.

US4, prioridad 2: como jugador quiero ver mi mapa conocido y utilizar viaje e historia desde la interfaz, con resultados comprensibles.

## Requisitos funcionales

| ID | Comportamiento exigido |
|---|---|
| FR-001 | Aceptar `historia <t>` para un instante entero válido desde el inicio hasta el reloj actual. Rechazar futuros interactivos. |
| FR-002 | Incluir todos los eventos con tiempo menor o igual a t. Si coincide con una decisión del jugador, mostrar el estado anterior a tomarla. |
| FR-003 | Aceptar `historia #k` y mostrar el estado inmediatamente anterior a la acción k. |
| FR-004 | Mostrar reloj, sala, vida, estadísticas, inventario, efectos activos, enemigos de esa sala con vida y mapa conocido históricos. |
| FR-005 | Consultar sin consumir tiempo, registrar acción, modificar partida, historial de retroceso ni estado aleatorio. |
| FR-006 | Mantener historia desde el inicio independientemente del retroceso limitado a cinco acciones. |
| FR-007 | Al usar pergamino, eliminar de la historia las acciones y eventos revertidos; el viaje no continúa por efecto de la consulta. |
| FR-008 | Permitir `--checkpoint-cada K` con K entero positivo; rechazar valores inválidos antes de jugar. |
| FR-009 | No conservar más de una copia completa por cada K acciones, además de la base inicial; fuera de ellas conservar solo cambios reconstruibles. |
| FR-010 | Cada consulta debe aplicar o deshacer cambios de como máximo K acciones del jugador; conservar lo necesario para reconstruir el azar cuando corresponda. |
| FR-011 | Guardar/cargar conserva historia completa vigente, conocimiento, configuración K y estado necesario para continuar determinísticamente. |
| FR-012 | Detectar el formato de P1 e informar incompatibilidad explícita o migración documentada; nunca cargarlo silenciosamente como P2. |
| FR-013 | `--replay partida.log --hasta t` presenta el mismo resumen histórico sin instanciar vista. |
| FR-014 | Si ese t excede el final del replay, presentar estado final y avisar que terminó antes. |
| FR-015 | `--verificar <cripta>` ejecuta únicamente la verificación y presenta el reporte sin instanciar vista. |
| FR-016 | Antes de jugar, presentar la verificación; si no es resoluble, impedir inicio salvo `--forzar`. |
| FR-017 | `--bench` y todo replay funcionan sin instanciar vista, conforme a la constitución. |
| FR-018 | Presentar solo el mapa conocido entregado por la capacidad de conocimiento; mostrar costos de salidas actuales y distinguir cazadores. |
| FR-019 | Aceptar `ir a <sala>`, delegar sus reglas y mostrar motivo de detención; cada paso consta como movimiento individual y la orden como comentario de depuración. |
| FR-020 | Rechazar sintaxis o referencias históricas inexistentes con mensaje claro y sin efectos sobre la partida. |

## Requisitos no funcionales

- NFR-001: historia en como máximo 50 ms en una partida de al menos 5 000 acciones con K predeterminado, sin red ni renderizado, sujeto a enmiendas oficiales.
- NFR-002: memoria proporcional a cambios registrados más copias de control espaciadas por K; no una copia completa por acción fuera de esa política.
- NFR-003: localizar referencias históricas y recortar una rama no debe exigir recorrer toda la historia.
- NFR-004: misma cripta, semilla y acciones conservan resultados deterministas tras consultas y guardado/carga.

## Aceptación

La matriz detallada está en `aceptacion.md`. H1–H6 son etiquetas del reparto, no identificadores oficiales del enunciado. Cada una se enlaza con FR- y una futura prueba.

## Entidades del dominio

Partida, acción del jugador, evento, instante consultado, estado histórico, conocimiento del jugador, punto de control, cambio y rama vigente.

## Assumptions y clarificaciones de diseño

Decisiones adoptadas a partir del enunciado y el motor existente, sin atribuirlas a respuestas del profesor:

- Acciones vigentes numeradas desde 1; selección de inventario, consultas, rechazos y retroceso no crean ordinal nuevo. #1 representa antes de la primera acción aceptada.
- t entero >=0; #k existente >=1; K entero >=1. Errores sin efectos.
- En t se completan todos los eventos de ese instante antes de la decisión; #k distingue fronteras de acciones. El reloj del resumen es t, aunque el último evento haya ocurrido antes.
- Base inicial en t=0; controles al completar cada K acciones. La base inicial es necesaria para conservar el inicio.
- Retroceso elimina el sufijo vigente, preserva los efectos no reversibles del pergamino según P1 y los registra como corrección de la frontera restaurada. Los límites previos por tiempo/acción se resuelven sobre la rama actual corregida. El log conserva la orden de retroceso para reproducirla; la consulta nunca la registra.
- Cargar sustituye la historia por la del archivo; no mezcla ramas.
- Persistencia rechaza explícitamente P1. Consultas sin HTTP ni cambios en cachés de partida.
- --hasta requiere --replay; --verificar es excluyente con juego/replay/bench; --forzar no altera el reporte del verificador.

## Success Criteria

- SC-001: H1–H6 y los escenarios extra de aceptación tienen resultado definido y una prueba automatizada vinculada al finalizar implementación.
- SC-002: 100% de requisitos funcionales tienen tareas y casos de aceptación trazables.
- SC-003: consultas <=50 ms con >=5000 acciones y K elegido, sin red/renderizado; cada consulta reconstruye <=K acciones.
- SC-004: consultar, guardar/cargar y continuar preservan resultados deterministas y conocimiento de la rama vigente.

## Escenarios de aceptación por historia

- US1/P1: dado reloj 100, consultar 101 se rechaza (H1); dados eventos empatados, se incluyen todos (H3); consultar conserva estado/log/retroceso (H4). La prueba independiente usa cambios sintéticos con fronteras conocidas.
- US2/P1: dado un retroceso, consultar excluye el sufijo (H2); dado archivo P1, cargar informa incompatibilidad (H6); guardar/cargar conserva cada resumen vigente. Se prueba con una historia sintética serializada.
- US3/P2: dado replay que termina antes de t, mostrar final y aviso (H5); dada cripta no resoluble, impedir inicio salvo --forzar (R4 de integración). Se prueba con verificador y fuente de replay simulados, sin vista.
- US4/P2: dados datos de conocimiento, mapa oculta salas desconocidas; viaje se detiene con motivo y pasos individuales. Se prueba con contratos simulados y luego motor real.

## Edge Cases

K=1, controles exactos, t entre eventos, #0, negativos, acción inexistente, partida sin acciones, final anticipado, retroceso cruzando checkpoint, nueva rama, archivo corrupto y carga fallida. Resultados en `aceptacion.md` y contratos.

## Aceptación propuesta A–D: puertas recíprocas (2026-11-12)

Preparación de pruebas solicitada por D a partir de la propuesta comunicada de A;
no acredita una entrega del motor ni resuelve la compatibilidad de guardados antiguos.
Se conserva el formato binario actual y el objetivo de evento `sala:dirección`.

- PD-01: abrir una puerta recíproca abre ambos extremos y deja un solo cierre
  vigente. Guardar/cargar preserva ambos extremos incluso si la sala opuesta no
  tiene contenido cargado ni rastro, sin convertirla en explorada o cargarla.
- PD-02: guardar/cargar un cierre pendiente conserva tiempo, secuencia y contador;
  el evento restaurado cierra ambos extremos una sola vez.
- PD-03: retroceder la apertura restaura ambos extremos cerrados y elimina su
  cierre; retroceder un turno que contiene el cierre restaura ambos abiertos y
  el mismo evento pendiente. El pergamino conserva la excepción de Parte I.
- PD-04: continuar desde el archivo produce el mismo estado y azar que continuar
  sin cargar, comprobando además explícitamente el cierre de ambos extremos.

Pruebas de D con salas sintéticas, motor, historial y binario reales, sin HTTP.
No se sustituyen métodos de apertura/cierre para hacer pasar la aceptación.
Los fallos se registran como pendientes de A, sin omisiones ni expectedFailure.

## Aceptación D con entregas reales offline A/C (2026-11-12)

Incremento de aceptación de T003/T010/T021, sin activar en producción las
opciones `historia_para_pruebas` o `conocimiento_para_pruebas` del motor de A.

- DX-01: el controlador procesa movimiento y consultas temporales/ordinales con
  el productor histórico real, sin que consultar altere estado, azar o replay.
- DX-02: los comandos guardar/cargar usan v4, recuperan historia y permiten
  continuar; los archivos corruptos o P1 se rechazan sin registrar carga ni
  mutar la partida. Se conserva la excepción de pergaminos al retroceder.
- DX-03: el log generado por el controlador reproduce la rama posterior a una
  carga, incluso después de eliminar el archivo original, sin construir vistas
  ni realizar HTTP. La fábrica offline selecciona explícitamente el productor
  entregado por A; no sustituye la ejecución del motor.
- DX-04: el controlador presenta el mapa real de C actualizado por entradas
  físicas del motor. No revela salas desconocidas. El control de viaje real de
  C se inyecta por la interfaz existente de D sobre ese mapa.
- DX-05: cancelar antes de un paso no mueve ni graba una acción. Si el motor
  acepta un paso pero no entrega `hechos_paso`, D conserva el movimiento real
  grabado, cancela la continuación y no repite pasos; no deduce daño/enemigos.
- DX-06: el rechazo explícito de A al restaurar con mapa activo se presenta al
  usuario y conserva estado, mapa, historia y log. Esa prueba negativa no
  certifica persistencia conjunta ni completa T010.

La vista de prueba solo recibe la presentación; modelo, conocimiento, rutas,
control de viaje, historial, binario y replay son los componentes reales.

## Aceptación pendiente de carga conjunta del mapa — 2026-11-13

MC-01 concreta FR-011 y SC-004 desde D, dentro de T003/T010/T021. Usa la
activación offline de A/C existente; no agrega una capacidad ni habilita el
flujo de producción.

- Tras entrar físicamente en una sala, guardar por el controlador en formato
  v4 y comprobar que el lector real devuelve el estado y la historia guardados.
- Entrar en otra sala después del guardado: una sala avistada pasa a explorada
  y otra, antes desconocida, pasa a avistada. Verificar ambos cambios antes de
  intentar cargar, sin modificar directamente el conocimiento.
- Cargar por el controlador debe tener éxito y recuperar el estado físico,
  la historia vigente, K y el mapa exactos del guardado. La sala descubierta
  después debe volver a desconocida y la explorada después, a avistada; el
  comando `mapa` debe mostrar el mismo contenido que al guardar.
- El log debe registrar una sola carga aceptada. Repetir el movimiento desde
  lo cargado debe producir el mismo estado, historia y conocimiento que antes
  de cargar, descartando la rama posterior al guardado.

La prueba usa motor, conocimiento, controlador y archivo reales, sin HTTP ni
parches de reglas/restauración. El bloqueo actual de A debe producir un fallo
visible de MC-01, sin skip ni expectedFailure. DX-06 documenta el rechazo de la
entrega actual, no una regla permanente: al conectar A/C la carga válida, su
prueba negativa deberá sustituirse por MC-01; conservar las pruebas de carga
inválida sin mutación. Preparar esta aceptación no completa T010.



## Integración completa autorizada — 2026-11-14

### Fortalecimiento autorizado — RF-01..03

### RC-01 — margen del ciclo integrado

### RE-01..04 — revisión de entrega del 15 de noviembre

- RE-01: al reabrir desde cualquiera de los dos extremos de una puerta física recíproca inequívoca, respetar la llave y el intervalo de cierre automático publicados aunque esos atributos estén declarados únicamente en el otro extremo. No inventar retornos ni modificar los datos iniciales de salidas dirigidas o ambiguas. Si ambos extremos declaran un atributo, conservar el valor explícito del extremo usado; no normalizar datos contradictorios. Abrir sin llave se rechaza sin tiempo, historia o eventos; abrir con llave, cerrar, guardar/cargar y retroceder conservan la regla bilateral existente.
- RE-02: en una cripta con identificadores de catálogo inéditos, los objetos sin arte local mantienen el signo de pregunta en suelo, inventario y equipo. Sus acciones y sonidos dependen de clase/acción y no de identificadores conocidos; buscar recursos desde otro directorio de trabajo debe funcionar. Distinguir despacho de WAV válido y reproducción audible efectivamente comprobada.
- RE-03: sabueso y espectro usan la animación visual común (reposo y reacción al daño) sin modificar la simulación; desactivar animaciones conserva sus imágenes. No se exige inventar secuencias de fotogramas que el programa no tiene.
- RE-04: contrastar Parte II original y texto conservado de Parte I, mapas publicados y contenido, regresión y cuatro límites de procesamiento. Entregar una matriz con evidencia, límites y faltantes históricos. No certificar fuentes vacías, defensa humana, latencias absolutas o ausencia total de errores.

Escenarios RE-01: (a) sin llave y desde el extremo sin metadatos, rechazar sin mutación; (b) con llave, reabrir desde ese extremo y programar un cierre que cierre ambos lados; (c) cargar/revertir conserva estado y agenda; (d) sin retorno o con retorno ambiguo no hereda metadatos de una salida distinta. RE-02/03 se verifican sobre una cripta sintética nueva mediante fábrica, controlador y vista reales.

### VI-01..05 — mapa ilustrado y cazador

- VI-01: distinguir visualmente el cazador mediante ilustración coherente con el juego, incluida una representación por comportamiento cuando un tipo nuevo carezca de PNG específico. Conservar nombre/tipo/instancia y datos del catálogo; la ilustración no modifica entidades.
- VI-02: el botón Mapa de la GUI abre una cartografía gráfica de la proyección conocida: exploradas con nombre/salidas/costos y puertas recordadas, avistadas sin nombre ni contenido, desconocidas sin nodos, cantidad ni posición. Mostrar niebla decorativa sin inferir salas. IDs y topologías arbitrarias, incluidas salidas dirigidas y conexiones no geométricas, deben seguir representables.
- VI-03: seleccionar sala explorada permite emitir la orden ordinaria `ir a`, sin ejecutar movimiento desde el dibujo ni precalcular rutas con información real. Marcar posición y destino activo si son conocidos; no inventar un itinerario.
- VI-04: abrir, seleccionar, desplazar, ampliar y cerrar el mapa no cambia reloj, azar, eventos, conocimiento, inventario, historia ni log. La consola conserva su presentación textual. El mapa no solicita HTTP ni contenido; no se añade trabajo por evento del motor. Conservar acceso textual para mapas grandes y accesibilidad.
- VI-05: contrastar rutas/campos del servicio vigente con adaptadores y ejecutar API fría/caliente. No traer información a la vista por estar disponible en el servicio ni alterar presupuestos para completar decoración. Registrar resultados, diferencias y límites, sin afirmar igualdad temporal exacta en cualquier carga del sistema.

Optimizar el registro de cambios históricos sin cambiar las proyecciones, valores, tiempos, secuencias, consumo de azar, decisiones o formato persistido. Una reutilización del orden de enemigos debe detectar cambios de sala, identidad, pertenencia u orden de la colección; muerte, aparición, reversión, restauración y fallo de acción deben conservar resultados equivalentes al registro anterior. Medir ciclos completos con 30 cazadores e historia/mapa completos, incluyendo llegada de enemigos, combate y checkpoints; conservar máximos y excesos, no solo promedios.

- RF-01: conservar resultados, costos, secuencias y desempates al optimizar búsquedas. Comparar primeras consultas y reutilización con la misma entrada y semilla, incluyendo puertas cambiantes, antes de aceptar una mejora.
- RF-02: salas con identificadores no negativos muy separados deben permitir jugar, consultar historia, retroceder, guardar, cargar y reproducir sin reservar memoria proporcional al mayor identificador. Conservar los identificadores externos en la interfaz y los archivos; no renumerar la cripta observable.
- RF-03: la documentación vigente identifica cada caso obligatorio de Parte II, su requisito, tarea, implementación y prueba; separa evidencia actual de registros históricos y mantiene explícitos los faltantes auténticos. No se certifica ausencia absoluta de errores ni calificación.

La usuaria autoriza completar todas las partes y publicar en su rama. IA-01: mapa, viaje, historia y guardado disponibles desde consola/GUI y replay normales. IA-02: toda acción aceptada y sus eventos producen cambios históricos, incluyendo inventario, efectos y conocimiento; retroceso recorta y conserva la excepción de pergaminos. IA-03: cargar valida y recupera conjuntamente físico, historia, conocimiento y cursor, sin publicar parcialmente. IA-04: una puerta física recíproca abre/cierra ambos extremos con un cierre pendiente; exportar conserva extremos modificados sin explorar su contenido. IA-05: antorcha revela vecinas y sus salidas sin activar contenido; observación de puertas solo desde la posición ocupada. Esta última elección sobre puertas remotas es decisión conservadora del equipo, no aclaración atribuida al profesor. IA-06: cada movimiento entrega hechos reales de daño y enemigos presentes al entrar para detener viaje. IA-07: benchmarks reproducibles comparan rutas individuales/compartidas, reutilización/recálculo y mapa/viaje, además de la carga integrada; publican máximos e incumplimientos. IA-08: pruebas antiguas de ausencia de capacidades se sustituyen por aceptación positiva, conservando corrupción/atomicidad. IA-09: documentación, tareas y prompts reflejan resultados reales y pendientes externos, sin garantía de nota.
