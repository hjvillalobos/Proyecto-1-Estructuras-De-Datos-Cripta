# Feature Specification: historia, persistencia y comandos de integración

Responsabilidad: línea de tiempo e integración. Fuentes: enunciado §§3.6, 5.5, 6.1 y 7.3; reparto página 6. Estado: especificada; implementación pendiente. Rama: `004-linea-tiempo`. Creada: 2026-11-02.

## Objetivo y alcance

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

