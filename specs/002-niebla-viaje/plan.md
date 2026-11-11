# Plan técnico: incrementos I1 e I2 y pendientes de integración

**Rama:** `codex/002-niebla-viaje` · **Fecha:** 2026-11-08 · **Especificación:** [spec.md](spec.md)

## Resumen

**Alcance vigente I1 e I2:** se implementaron conocimiento básico, deltas locales y evaluación independiente de detención. Las restricciones generales de cierre que siguen en este documento corresponden a la capacidad completa. I1 tiene alcance aclarado en spec.md, diseño en data-model.md y tareas propias; no depende de Q1 ni de aceptar interfaces ajenas. Se usa la investigación ya realizada. Los índices de puertas reciben identificadores explícitos del llamador, sin deducirlos de extremos.

I1 administra conocimiento sin modificar el motor: exploración por entrada física, avistamiento, recuerdos de puertas observadas y cambios reversibles. I2 añade evaluación de detención, pruebas ampliadas y demostración. Mapa/historia, antorcha y viaje completo todavía requieren conexiones y acuerdos. Las decisiones de I1/I2 están implementadas; las propuestas de integración permanecen provisionales.

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
| Medición | Hay mediciones locales de I1/I2 en baseline.md; faltan mediciones integradas y el presupuesto del viaje. |
| Flujo y acuerdos | Revisión de aclaraciones abierta; Q1 y contratos impiden declarar aprobado el plan completo. |

**Estado de revisión:** el alcance independiente I1/I2 fue delimitado, documentado, revisado y autorizado antes de implementarse. Las tareas T001–T013 están terminadas dentro de ese alcance. Q1 y la aceptación de contratos siguen pendientes para los siguientes incrementos; no se consideran resueltos por autorización local.

## Organización y estado actual

| Archivo | Responsabilidad y estado |
| --- | --- |
| `modelo/conocimiento.py` | Implementado: índices, estados, observaciones y deltas del mapa. |
| `modelo/detencion_viaje.py` | Implementado: decisión local de detención, sin ejecutar viaje. |
| `modelo/viaje.py` | Coordinación de pasos y causas de detención, sin ejecutar eventos por su cuenta. |
| `modelo/historial.py`, `modelo/inventario.py` | Mantener retroceso y aportar registros de datos reconstruibles; modificación posterior al acuerdo C/A/D. |
| `tests/test_conocimiento.py` | Estados, memoria, filtrado y reversión. |
| `tests/test_viaje.py` | Rutas conocidas, condiciones de parada y cancelación. |
| `tests/test_conocimiento_historia.py` | Adaptación a tipos reales de D y reconstrucción. |
| `utilidades/bench_conocimiento.py` | Implementado: consultas, revelación, inversión, memoria y proyección; no mide cálculo de paso. |

Existen conocimiento, detención, adaptadores de historia y rutas, sus pruebas aisladas, la demostración y benchmarks locales. El viaje ejecutable sigue pendiente; historial e inventario existentes no se modificaron. `modelo/juego.py` y `modelo/rutas.py` se coordinan con A; controlador, snapshots y persistencia con D. No se crean versiones paralelas de sus tipos en C para aparentar integración.

## Diseño candidato

### Índices y conocimiento

Preparar una sola vez un arreglo de IDs ordenado mediante el ordenamiento propio y búsqueda binaria manual. Asociar cada ID a un índice compacto. Las salidas internas retienen índices ya resueltos, evitando búsquedas repetidas al revelar vecinas. El conocimiento ocupa arreglos separados de los datos descargados: desconocida, avistada o explorada, y memoria de puertas independiente del estado real.

Una consulta pública por ID cuesta O(log V); por índice interno O(1). Inicializar índices cuesta O((V+P+E) log(V+P) + suma de g·log g por sala), donde g es su grado; incluye ordenar IDs, resolver extremos/destinos y ordenar salidas. Memoria O(V+E+P). No se atribuye ese trabajo a una entrada normal. La actualización recorre solo las salas y salidas afectadas, O(R+A), donde R son salas procesadas y A sus salidas; se mide aparte cualquier traducción inicial de ID. No se recorre todo el mapa conocido para descubrir qué cambió.

La proyección de mapa puede recorrer el índice y costar O(V+E); es una consulta de presentación, no la operación de revelar ni la fuente que se reconstruye antes de cada paso. Si las mediciones justifican un índice adicional de salas conocidas se documentará antes de introducirlo.

### Cambios reversibles

Registrar por operación únicamente valores que cambian: estado anterior/posterior de sala, recuerdo anterior/posterior de puerta y metadatos necesarios. Revertir un lote invierte su orden. Si una operación vuelve a tocar un mismo campo, se pueden registrar cambios consecutivos sin construir una tabla de deduplicación prohibida. Memoria auxiliar O(D); aplicación e inversión O(D log(V+P)) por resolver el ID de cada cambio mediante búsqueda binaria, para D cambios registrados.

El retroceso actual conserva funciones. No se serializan: el plan final debe decidir cómo producir registros de datos en el mismo punto de mutación y reutilizarlos para retroceso/historia sin doble aplicación. Inventario requiere identidad, orden, cursor y equipamiento; la excepción de pergaminos se conserva. No se transforma cada acción en una copia completa del inventario o del mapa.

D ya admite escalares y tuplas inmutables mediante ValorHistorico y CambioHistorico; tiempo/secuencia pertenecen al contenedor de evento. El adaptador debe usar esa forma tras acuerdo, sin inventar un segundo formato binario.

### Rutas y viaje

Se reutiliza la búsqueda propia de A mediante fuente filtrada y consulta sin límite. Desde 33d97ac admite limite=None; I4 comprueba la fuente filtrada contra 9730482, conservando su lectura `arco.puerta.get("cerrada", False)` mediante una fachada sin diccionario. No se pasa el mapa real ni se sustituye ausencia de límite por un número enorme. La compatibilidad comprobada no equivale a integración del movimiento o aceptación del contrato completo por A.

C propone un paso; el controlador ejecuta un movimiento ordinario; el motor cierra el intervalo; C recibe hechos del paso y decide si continúa. Se debe poder procesar pergamino entre pasos. Se registra daño ocurrido, incluso si una curación posterior restaura la vida. D mantiene registro individual de movimientos y comentario de viaje. No se afirma que el callback booleano actual satisfaga estas necesidades.

### Antorcha

Revelar vecinas no activa contenido y no se propaga recursivamente. Q1 queda fuera de las decisiones adoptadas: no se fija la memoria de puertas remotas nunca observadas. La implementación de esa política y sus pruebas esperan respuesta.

## Entregas previstas y condiciones de cierre

1. **Conocimiento básico:** FR-001–005, parte independiente de FR-014 y FR-017. C01–C04, IDs dispersos y reversión local. Sin conexiones a archivos compartidos.
2. **Historia e inventario:** FR-014–016, C10–C11. Requiere acuerdo de lotes, correcciones de pergamino, estado completo y tipos de D.
3. **Antorcha:** FR-006, N4–N5. Requiere resolver Q1 y acuerdo de observaciones con A.
4. **Viaje:** FR-007–013, FR-015 y FR-017, N1–N3/N6 y C05–C09. Requiere ruta filtrada y resultado/cancelación acordados; verifica la regla de antorcha cuando intervenga.
5. **Integración y medición:** PR-001–003 y SC-001–004. Solo se cierra con código real de A/D, regresiones, trazabilidad y mediciones; pruebas aisladas no acreditan partida integrada.

I1 y la evaluación independiente de I2 están implementados conforme a tasks.md. Los puntos de historia, antorcha, viaje completo e integración de esta lista siguen pendientes. Una tarea local terminada no equivale a aceptación de la capacidad completa.

## Mediciones previstas

I10: antes de una búsqueda nueva, consultar el primer arco de la adyacencia ya filtrada de C. Si no existe, devolver sin_ruta. No añadir recorridos al caso que reutiliza etiquetas cerradas. El costo del rechazo queda en O(log V + grado del origen), sin nuevas estructuras ni cambios a A. Mantener las validaciones de origen/destino y llegada antes de este atajo; invalidar la referencia de caché antes de un nuevo intento. Comparar el cierre de puerta en la misma carga de I9 y revisar rutas alternativas, apertura y reversión.

I9 añade `utilidades/bench_escenarios_rutas.py`, ejecutado desde el verificador aislado existente. Genera cadenas, anillos con atajos y grafos dirigidos con costos positivos mediante Random con semilla. Usa listas, IDs dispersos y puertas explícitas; importa el adaptador anterior fijado en Git como comparación, sin modificar A. Cada resultado completo se compara fuera del intervalo medido. Las observaciones y reversiones también quedan fuera del tiempo de consulta. Separar cierres y reversiones para evitar mezclar búsquedas exitosas y sin ruta en una media. Preparación medida aparte; no incluye descarga, construcción del conocimiento ni renderizado. Pruebas pequeñas verifican reproducción, equivalencia y detección de resultados incorrectos. No cambiar código del juego solo para mejorar cifras.

Cargas deterministas con igual cantidad de salas reveladas y distintos tamaños de mapa total; registrar trabajo y tiempo para distinguir preparación de actualización. Comparar IDs compactos y dispersos. Medir consultas de salas/puertas, repetición de observaciones, cantidad de deltas y aplicación/inversión.

Para viaje: mapa completo de referencia, alternativas de costo distinto, empates y puertas recordadas que cambian tras observación. Medir cálculo completo del paso, incluida adaptación de fuente, sin red/renderizado. Incluir coste de preparación separado, sin ocultar reconstrucciones por paso. Repetir inventario e historial de P1 con la nueva carga. Documentar semilla, entorno, unidades, tamaño y resultados en DECISIONES.md solo después de ejecutar.

## Riesgos y alternativas

### I8: distancias reutilizables hacia un destino

Sustituye la decisión inicial de I4 de recalcular siempre. Mantener el buscador de A intacto. C prepara una segunda adyacencia transpuesta, conservando dirección, costo y puerta de cada arco; no supone simetría. Ejecutar buscar_ruta desde el destino en ese grafo y usar solo etiquetas cerradas de EspacioBusqueda. Para proponer el paso original, revisar sus salidas conocidas y minimizar costo del arco + distancia restante; desempatar por ID de vecina y costo del primer arco, como A. Todos los costos son positivos: los sucesores óptimos tienen menor distancia y ya están cerrados cuando se cierra el origen consultado.

ConocimientoMapa añade una revisión monotónica de invalidación, sin efecto sobre el estado de partida. Aumenta con cada escritura efectiva, incluso al aplicar/revertir; no se restaura a un número anterior tras rollback. Repetir una observación idéntica no la cambia. Cada planificador conserva un solo destino/revisión; reutiliza únicamente si el origen está cerrado en la generación vigente. Si no, recalcula con A. Invalidar la referencia antes de buscar para no aceptar datos de una excepción. No se persiste la caché ni se comparte entre mapas.

Preparación y espacio O(V+E); consulta reutilizada O(log V + grado), consulta nueva conserva costo de Dijkstra. Sin dict/set ni otro buscador. Medir frente al módulo de C anterior exportado de Git: primera búsqueda, pasos sucesivos y puerta cambiante. No atribuir la mejora de reutilización a búsquedas nuevas. Tests C37–C39 y oráculo previo; el límite oficial sigue pendiente del mapa de referencia integrado.

### I7: inventario histórico

Nuevo modelo/inventario_historia.py. Base inicial O(n); captura por operación O(1): nodo objetivo (cursor por defecto), extremos y vecinos inmediatos, más metadatos. terminar(nuevo=None) compara los mismos nodos y el nuevo de recoger, generando tipos históricos reales de D. No guarda callbacks en el lote ni cambia Inventario. Capturas temporales contienen referencias solo hasta terminar; sus valores anteriores son tuplas independientes. Captura de un solo uso.

Claves propuestas inventario_estado y inventario_nodo:<instancia>, distintas de inventario:<orden> que D usa para presentación. Metadatos: capacidad, tamaño, primero, último, cursor, arma, armadura. Nodo presente: tipo, ubicación, sala, encendida, anterior, siguiente. Ausencia indica nodo retirado. Identidades deben ser únicas y no cambiar; recoger devuelve el nodo nuevo que se entrega a terminar. Captura solo operaciones locales del contrato, no mutaciones arbitrarias concurrentes.

Descartado comparar dos snapshots completos por acción. No renumerar posiciones al equipar: cambiar enlaces evita deltas proporcionales al tamaño. Pruebas contra Inventario real y LineaTiempo real en copia aislada. Corrección de pergamino se prueba con la API recortar; la coordinación general del motor y la proyección visual siguen pendientes.

### I6: ensayo reproducible de motor y entrega B

Crear tests/test_viaje_motor.py y utilidades/verificar_viaje_motor.py. Exportar fuentes Python de A 9730482 a carpeta ignorada; superponer únicamente tipos históricos/LineaTiempo de D 02da6b6 y módulos nuevos de C. Ejecutar motor_terreno de A con su productor registrar_h3, traducir a tipos reales de D y conservar la base de campos_iniciales de C. El adaptador permanece en la prueba: interpreta exclusivamente el caso conocido del guardián, no se usa como implementación general. Los hechos de entrada se contrastan con el fixture ya cargado; no se consulta contenido desconocido en producción.

Ante rechazo esperado, cancelar ControlViaje y contrastar estado exportado, reloj, azar y agenda de A y exportación de D antes/después. No activar integrar_historia ni guardado. Sin cambios a archivos compartidos. El verificador ofrece --verificar-b para exportar por separado fuentes de B 694dcf6 y repetir sus pruebas de entrega de terreno y preparación de verificación. Esto revisa los cambios recibidos, no fusiona B/A/D en una rama de entrega.

### I5: control sin bucle de ejecución

Crear modelo/viaje.py: ControlViaje recibe un planificador con consultar(origen,destino), reutiliza ConsultaRuta y evaluar_detencion. Estados inactivo, listo, pendiente, detenido. iniciar valida mediante consulta antes de cambiar estado y exige no tener propuesta pendiente; proponer consulta otra vez el conocimiento y reserva un PasoViaje inmutable (numero, origen, ruta). registrar_resultado exige el número vigente y ResultadoPaso (posicion, aceptado, recibio_dano, hubo_entrada, enemigos_al_entrar, terminado). Posición tras aceptación debe ser siguiente y hubo_entrada=True; rechazo conserva origen y no entrada. Todos los campos se validan antes de mutar. No se deduce posición desde mensajes ni daño desde vida.

El número de propuesta aumenta por instancia, nunca se reinicia entre viajes. Cancelar descarta pendiente; respuestas tardías fallan aunque se haya iniciado otro viaje. Una nueva orden explícita puede reemplazar un viaje listo/detenido, nunca un paso pendiente. Se conservan causas de evaluar_detencion y se agrega fin_partida si corresponde. Falta de ruta se decide al proponer, no mediante una segunda búsqueda al recibir resultado. No se calcula una ruta tras daño/enemigos. Memoria propia O(1), transiciones O(1) salvo iniciar/proponer, que incluyen la consulta de I4. Sin dict/set, cola, hilos, callbacks de movimiento, reloj ni copias del mapa.

Pruebas locales con planificador de prueba controlado para protocolo/errores; prueba adicional con conocimiento y buscador real de A en el verificador aislado de I4. No sustituir esas pruebas por un doble que finja integración. Mantener la propuesta de contrato de A/D explícita; no tocar sus consumidores.

### Incremento I4: fuente dinámica para el buscador existente

Crear `modelo/conocimiento_rutas.py` con `PlanificadorConocido(mapa)` y `consultar(origen, destino)`. Reutiliza `EspacioBusqueda`, `HeapRutas`, `ArcoTerreno` y `buscar_ruta` de A (9730482); no duplica Dijkstra ni modifica rutas.py. Importación diferida al construir el planificador. La base de C aún no contiene rutas.py; el ensayo copia ese archivo exacto de A a una carpeta ignorada.

Una fuente privada conserva los índices densos estables del esqueleto de ConocimientoMapa. Es almacenamiento interno, no conocimiento expuesto. Al iterar una adyacencia, solo entrega arcos si origen/destino están explorados y la puerta está recordada abierta o no existe. Los arcos se preparan una vez; una fachada de puerta sin diccionario responde get("cerrada", False) con False para esos arcos ya filtrados. No contiene referencias al estado real del motor. Los índices privados de C se leen desde su adaptador, bajo pruebas de compatibilidad; no se publican como API para A/D.

El planificador consulta grados antes de iniciar búsqueda, traduce IDs por búsqueda binaria propia y devuelve `ConsultaRuta(estado, siguiente, direccion, costo_paso, costo_total)`, inmutable. Estados: destino_no_explorado, origen_no_explorado, llegada, sin_ruta, paso. Sin paso, sus datos son None; llegada tiene costo_total=0. No conserva rutas calculadas, por lo que una restauración no necesita invalidar una caché. Las llamadas son secuenciales y el mapa no se muta durante una consulta.

Preparación adicional O(V+E) tiempo/memoria, reservada una vez por mapa. Consulta O(log V + (Vr+Er) log(Vr+1) + grado(origen)), con Vr/Er de la región examinada; el filtrado examina las salidas de salas alcanzadas y no recorre todo el mapa antes de cada paso. Arreglos y heap propios de A; sin dict/set ni ordenamiento de biblioteca. No crea una lista de todas las rutas ni una copia del conocimiento por consulta.

Verificación: `tests/test_conocimiento_rutas.py` con C21–C25 y oráculo exhaustivo de caminos simples en grafos pequeños de semilla fija. `utilidades/verificar_conocimiento_rutas.py` prepara copia aislada con A versionado y ejecuta pruebas y mediciones sintéticas opcionales. `utilidades/bench_rutas_conocidas.py` mide preparación y consulta completa local en cadenas de tamaños crecientes; no certifica 5 ms ni sustituye --bench integrado. No cambia archivos compartidos del motor/vista ni reclama contrato aprobado.

### Incremento I3: adaptador histórico independiente

Crear `modelo/conocimiento_historia.py`. Sus funciones importan los tipos reales de D al invocarse; no recrean esos tipos ni alteran snapshots.py. La rama base aún no los incluye, por lo que su verificación se ejecuta contra archivos exactos de D en una carpeta temporal ignorada.

Claves propuestas: `conocimiento:sala:<id>` contiene grado 1/2; desconocida equivale a campo ausente. `conocimiento:puerta:<id>` contiene bool; sin observar equivale a campo ausente. No son las líneas `mapa:<id>` del resumen de D. No habilitar el marcador global `conocimiento` hasta contar con esa proyección de presentación acordada. Son estados reconstruibles internos, no la fachada gráfica ni un formato binario nuevo.

`campos_iniciales(mapa)` usa una proyección inicial única, ordena candidatos de puerta con el algoritmo propio y elimina duplicados por recorrido. Incluye solo salas conocidas y puertas observadas. Costo O(V+E+E log E) como cota; se ejecuta al iniciar historia, no por acción. `convertir_cambios(cambios)` traduce cada delta a CambioHistorico/ValorHistorico con presencia explícita, O(D) de tiempo y memoria (sin búsquedas en el mapa). Conserva orden y no registra nada. El motor es el único que agrega estos cambios a su lote temporal; C no llama registrar_accion en producción.

Prueba aislada: D en 02da6b6, exportado mediante git show sin modificar archivos del checkout; C desde los archivos de trabajo. Utilizar LineaTiempo real, no dobles. El ensayo contiene acciones/tiempos sintéticos explícitos y no certifica H3 real del motor. Publicación posterior del adaptador no significa aprobación de sus claves por el equipo.

### Ampliación I2 (2026-11-09)

Implementar `modelo/detencion_viaje.py` como función pura sobre un registro inmutable de hechos booleanos: llegada, daño, entrada, enemigos, ruta disponible y cancelación. Devolver registro inmutable con tupla de causas y propiedad continuar. Orden fijo: cancelación, daño, enemigos, llegada, sin ruta; se retienen todas las causas. Son etiquetas internas, no prioridades nuevas del juego. Costo O(1); no necesita índice, reloj, azar ni búsquedas. Alternativa descartada en este incremento: máquina de estados de viaje, pues requeriría acordar el ciclo del controlador. No se altera la función de rutas de A ni la fachada de D.

Ampliar pruebas con referencia independiente de arreglos de prueba, semilla fija y snapshots permitidos solo como oráculo de pruebas. Añadir `tests/demo_conocimiento.py`; escenarios fijos permanecen bajo tests. La demostración imprime estados y reversión con el formato de datos de C, no reemplaza la vista del juego.

Ampliar `utilidades/bench_conocimiento.py`: cadena con puertas explícitas; consultas y proyección con mapa totalmente conocido; tracemalloc para memoria viva/pico del constructor (esqueleto preparado antes), sin mantener instrumentación durante medidas de tiempo. El uso de tracemalloc es herramienta de medición, no estructura de la solución evaluada. Sin dependencias nuevas. Uso de memoria no equivale al tamaño de un archivo de guardado ni al consumo total del proceso.

Véase [research.md](research.md). No se solicita excepción a estructuras propias. El riesgo de comenzar conexiones antes de acordar sus datos es mayor que el de mantener temporalmente un módulo independiente. Este plan no promete ausencia de conflictos futuros ni cumplimiento de 5 ms sin mediciones.
