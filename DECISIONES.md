# Decisiones de diseño

## Actualizacion tecnica: 2026-10-16

Esta seccion sustituye el pendiente de implementar --bench indicado en las
revisiones anteriores. No sustituye la redaccion final del equipo ni certifica
que todas las secciones de este documento cumplan por si solas el apartado 8.

### Integridad del acceso directo a salas (4.10)

- Problema: un indice danado podia apuntar a otra sala con CRC correcto y
  devolverla silenciosamente. El CRC del bloque no verifica la relacion con el indice.
- Alternativas: cargar todo para buscar la sala, o validar rango e identidad
  unicamente en el bloque localizado mediante busqueda binaria.
- Decision: conservar la segunda opcion. El bloque debe estar dentro de la zona
  de salas y su sala_id debe coincidir con el solicitado. La carga completa tambien
  verifica orden estricto del indice, duplicados, rangos e identidad de cada bloque.
- Complejidad: acceso directo O(log s) entradas mas O(b) bytes del bloque pedido;
  no lee global ni las otras salas. La carga completa sigue siendo O(s + bytes).
- Evidencia: pruebas con indice apuntando a otro bloque valido, offsets fuera de
  zona, longitud cero y duplicados; lectura directa sin invocar leer_todo.
- Limites: estas comprobaciones y CRC detectan corrupcion accidental; no son una
  firma criptografica ni garantizan autenticidad ante modificaciones coordinadas.
  No cambia el formato v3 ni invalida partidas v3 correctas.

### Finalizacion de entrada de consola (10.2)

Se conserva la vista de consola y se captura EOFError/KeyboardInterrupt alrededor
de pedir_comando, donde realmente se producen. Propagarlas daba un traceback;
capturarlas en toda la aplicacion podria ocultar fallos internos. La salida normal
del bucle conserva el cierre de sesion existente, sin acciones, tiempo ni puntajes
de abandono adicionales. Las pruebas inyectan ambos errores y comparan el estado
antes y despues. No se cambia la interfaz grafica.

### Mediciones por subsistema (5.3)

- Problema: medir solo busquedas no permite defender el costo de las otras
  estructuras ni la comparacion binario/JSON exigida por 4.10.
- Alternativas: cronometros dentro del juego normal o un arnes separado que
  invoque sus mismas primitivas. Se descartan los primeros para no introducir
  instrumentacion o dependencias en el modelo durante una partida.
- Decision: bench.py orquesta; utilidades/bench_juego.py prepara y valida cargas
  de ColaEventos, Inventario, HistorialRetroceso, ordenar, persistencia y Motor.
  Se conservan los benchmarks de cache binaria/lineal y recuperacion sin red.
- Agenda: extraer/reinsertar, con reprogramacion periodica y comprobacion del
  orden (tiempo, secuencia). Inventario: quitar/reinsertar un nodo conocido y
  recorrer en ambos sentidos. Historial: delta de rastro, reversion y consumo.
- Ordenamiento: tres estrategias sobre los mismos datos, sin modificar entrada;
  escenarios aleatorio, casi ordenado y comparacion costosa. Los umbrales siguen
  siendo heuristicos contrastables, no se afirman optimos en cualquier equipo.
- Persistencia: mismo EstadoGuardado, archivos temporales, bytes, escritura,
  carga completa y acceso directo binario; las lecturas se comparan con el estado.
- Complejidades del arnes: agenda O(k log e), inventario O(k) con nodo conocido,
  historial O(k) para la carga de un delta; ordenar conserva las cotas de sus
  algoritmos. Las preparaciones y validaciones finales quedan fuera del tiempo,
  salvo comprobaciones de orden y reversion propias de las cargas descritas.
- Limites: memoria y disco son cargas diferentes. No se afirma que el binario
  siempre sea mas rapido ni que un promedio bajo garantice todos los ciclos.
  Se informa la unidad por carga; ordenar mide microsegundos por lista.

### Evidencia local reproducible (Python 3.14.6, Windows)

Comando ejecutado, semilla predeterminada 20261001:

```powershell
python main.py --bench --capacidades 25 --operaciones 1000 --repeticiones 3 --tamanos 8 16 32 256 --eventos 256 --salas 100
```

| Carga | Promedio observado |
|---|---:|
| Agenda, 256 pendientes | 17.158 us/operacion |
| Inventario, 8 / 256 nodos | 1.612 / 1.636 us/operacion compuesta |
| Historial, registrar/revertir/consumir | 7.853 us/operacion compuesta |
| Orden aleatorio 256, insercion / fusion | 5980.211 / 970.211 us/lista |
| Casi ordenado 256, insercion / fusion | 119.989 / 671.378 us/lista |
| Comparacion costosa 256, insercion / fusion | 39594.267 / 4858.033 us/lista |
| Carga completa binaria / JSON, 100 salas | 1678.543 / 1328.623 us |
| Acceso directo a una sala binaria | 491.557 us |
| Tamano binario / JSON, mismo estado | 7385 / 17921 bytes |

El binario ocupa menos en esta muestra, pero JSON carga mas rapido: se conserva
el binario por el formato propio y acceso directo exigidos, no por una ventaja
universal de velocidad. Hubo otra suite en ejecucion durante esta medicion;
son datos orientativos y deben repetirse de forma aislada en la defensa.

El ciclo sintetico de esperar proceso 256 eventos de rearme por decision:
3000 ciclos medidos, promedio 4.121 ms, maximo 18.698 ms, ninguno >=20 ms.
Tambien se ejecuto:

```powershell
python main.py --bench --subsistemas ciclo --operaciones 100 --repeticiones 3 --paquete .cache/cripta --cripta cripta-01 --semilla 1916
```

En la sala inicial de ese paquete local: 300 ciclos de esperar, maximo 0.148 ms,
sin HTTP/renderizado ni precarga dentro del cronometro. Es una carga limitada:
no incluye una ruta completa de combate ni certifica una cripta desconocida.
Para ampliar evidencia, usar el mismo arnes y contrastar cargas/escala del curso.

## Revision integrada: 2026-10-14

### Fallos de juego y verificacion para defensa

El retroceso conserva deltas, no snapshots. Cada registro guarda tambien los
IDs de fichas en uso antes de la accion. Antes de aplicar sus deltas se preparan
las fichas del estado actual y del estado a restaurar; una falla de datos rechaza
el retroceso antes de consumir el pergamino o sacar el intervalo del historial.
No se hace una operacion de datos fallible despues de aplicar el retroceso.
La cache no se deshace. Estos IDs son metadatos de referencias, no copias de
actores, objetos, agenda ni estado del juego. Si la union de referencias no cabe
en una cache muy pequena, el retroceso falla sin alterar la partida.

El reinicio descarta errores pendientes de la sesion finalizada y muestra un
aviso persistente si falla la nueva sesion; permite volver al menu y reintentar
o salir. Las rutas de guardar/cargar/replay se interpretan como un argumento
completo, con espacios y barras Windows, opcionalmente entre comillas.

Verificacion local: 265 pruebas, con respuestas oficiales copiadas a directorios
temporales. Victoria y replay con estado final identico en las cuatro criptas:

| Cripta | Salas | Semilla | Vida final | Reloj final |
|---|---:|---:|---:|---:|
| cripta-01 | 6 | 1916 | 4 | 525 |
| cripta-02 | 20 | 20 | 25 | 3725 |
| cripta-03 | 40 | 20 | 20 | 8225 |
| cripta-04 | 50 | 20 | 17 | 10300 |

Una medicion exploratoria con contenido precargado, sin red ni renderizado,
cronometrando Motor.ejecutar con perf_counter_ns, dio maximos de 10.416, 7.776,
7.397 y 10.485 ms respectivamente. Incluye las acciones de la ruta y su replay
(20, 104, 224 y 278 ciclos). No es evidencia obtenida mediante --bench, no
certifica otras cargas ni sustituye la evaluacion de una cripta desconocida.

Pendientes de cumplimiento: ampliar --bench a todos los subsistemas de §5.3,
completar las secciones y mediciones de §8, comprobar el paquete offline del
curso y revisar que la bitacora LLM incluya todos los prompts del equipo.
El juego verificado no equivale a certificacion de la entrega completa.

Estas correcciones actualizan las rutas del motor; las mediciones antiguas y los
pendientes de las secciones originales no certifican por si solos el juego actual.

### Cursor del inventario (§4.5)

El GUI comunica la seleccion al controlador sin ejecutar una accion temporal ni
grabarla en replay. Seleccionar el ID que ya esta en el cursor retorna de inmediato;
soltar usa el nodo conocido y lo desconecta en O(1). Buscar un ID diferente puede
ser O(n), pero es una operacion de seleccion, no una nueva busqueda necesaria
para eliminar el objeto que ya se esta viendo. El ciclo completo tambien incluye
agenda y sincronizacion de fichas: no se afirma que todo el ciclo cueste O(1).

### Traslado de enemigos (§4.7)

Se descartaron buscar/eliminar en una lista convencional (O(n) por actor) y
mantener un indice hash (no permitido). EnemigosSala conserva un arreglo contiguo
y cada actor conoce su posicion. Extraer intercambia con el ultimo elemento y
agregar al destino actualiza la posicion, sin recorrer ni desplazar los restantes.
El delta guarda el indice extraido y restaura la posicion original al deshacer.
La activacion sigue ordenando IDs y la agenda sigue usando tiempo y secuencia.

Con Python 3.14.6, nueve repeticiones locales, excluyendo construccion y agenda:

| Actores trasladados | Mediana por traslado |
|---:|---:|
| 32 | 0.959 us |
| 512 | 0.954 us |
| 4096 | 0.977 us |

Estos resultados miden extraer/agregar, no el ciclo completo. Las pruebas tambien
prohiben recorridos y remove durante los traslados y verifican el orden restaurado.
El limite del diseño es que toda alteracion de la coleccion debe mantener los
indices; las primitivas del motor centralizan esas operaciones.

### Victoria y persistencia (§2.12, §4.10)

Llevar la llave o encontrar una puerta inicialmente abierta no demuestra que se
haya abierto correctamente. El motor conserva una lista de aperturas por sala y
direccion; abrir con la llave registra esa evidencia y su delta. La victoria exige
atravesar hacia la salida la puerta con la llave declarada y evidencia de apertura.
La llave no se consume, y el cierre automatico sigue impidiendo atravesarla.
El marcador se guarda en cada PuertaGuardada del formato binario v3. Los formatos
anteriores no permiten reconstruirlo con certeza, por lo que se rechazan.

### Frontera del adaptador (§6)

El motor solicita una transaccion de catalogo a la fuente de datos y prepara el
estado del juego por separado. El adaptador decide como aislar y confirmar su
cache bajo su propio candado; el motor ya no clona caches ni modifica sus nodos
o contadores. Los fallos descartan la transaccion y preservan la partida viva.
Las copias temporales corresponden a cargar, no al historial, que usa solo deltas.

## Parte B: red, catálogo, precarga y caché

Actualización: 2026-10-03.

Se utiliza la restricción adicional de no usar tablas hash en la lógica estructural. Los diccionarios se conservan únicamente como representación de respuestas JSON, atributos y reportes; no se usan como índices. La deduplicación y los registros de trabajo usan listas.

### 1. Precarga de salas (§4.2)

Se necesita cargar el esqueleto al inicio y disponer del contenido de una sala antes de confirmar la entrada del jugador.

Se consideraron dos alternativas:

- Descargar todo al inicio: simplifica la disponibilidad, pero aumenta la espera inicial y puede gastar solicitudes en salas que no se visiten.
- Descargar únicamente al entrar: evita trabajo anticipado, pero obliga a esperar durante cada exploración.

Se eligió una solución intermedia: descargar todas las páginas del esqueleto, de hasta 50 salas cada una, y anticipar el contenido de salas conectadas en lotes de hasta 10 IDs distintos. Se priorizan las salas cercanas con un recorrido por anchura y un orden fijo de direcciones.

Un solo hilo realiza la precarga anticipada. Los resultados se incorporan en un orden definido; si falta información necesaria, se espera antes de continuar. Descargar datos no activa enemigos ni modifica el reloj virtual.

Las salas, los IDs pendientes y el contenido incorporado se guardan en listas. Sus consultas son lineales; deduplicar m IDs mediante comprobaciones sucesivas puede costar O(m²). Es sencillo, aunque deberá revisarse si aumenta mucho el número de salas.

Las pruebas cubren varias páginas, límites por lote, contenido reutilizado y espera por datos necesarios. Falta medir la frecuencia real de estas operaciones y su efecto al integrar el motor.

### 2. Resolución del catálogo (§4.3)

El catálogo se consulta al preparar salas y al necesitar fichas de objetos, enemigos o trampas.

Se compararon estas alternativas:

- Solicitar cada ficha individualmente.
- Reunir IDs distintos y solicitar únicamente los faltantes en lotes de hasta 10.

Se eligieron los lotes para reducir solicitudes. Primero se consulta la caché y después el almacenamiento local de la misma versión. Solo se descarga lo que falta.

Los IDs se deduplican con una lista, sin usar set. También se revisan las dependencias del campo suelta, evitando repetir IDs o recorrer indefinidamente una dependencia circular. Las respuestas se validan y se devuelven en el orden solicitado.

La precarga guarda las fichas en disco sin llenar la caché con objetos que el juego todavía no utiliza. Las instancias FichaCatalogo se crean al necesitarlas.

Deduplicar m IDs puede costar O(m²). En una prueba con 31 IDs distintos se realizaron cuatro solicitudes de catálogo, con lotes de 10, 10, 10 y 1, además de la consulta de versión. Repetir la precarga no produjo nuevas solicitudes.

### 3. Caché y gestión de memoria (§4.4)

Se implementó CacheCatalogoOrdenado con dos estructuras que comparten los mismos nodos:

1. Un arreglo ordenado por ID para localizar fichas con búsqueda binaria propia.
2. Una lista doblemente enlazada para mantener el orden LRU.

La capacidad predeterminada es de 25 fichas y se configura con --cache-size. No se utilizan bisect ni métodos automáticos de ordenamiento.

Una búsqueda exitosa o una inserción mueve el nodo al frente del LRU. Para desalojar, se recorre desde la cola hasta encontrar una ficha con referencias == 0. Si todas están en uso, se lanza CacheSinEspacioError sin superar la capacidad.

El controlador debe mantener las referencias correspondientes a enemigos activos, inventario, objetos del suelo y trampas de la sala actual. Descargar una ficha no implica que esté activa.

#### Alternativas y elección

- Búsqueda lineal: fácil de implementar, pero revisa hasta n fichas por consulta.
- Arreglo ordenado con búsqueda binaria: reduce la búsqueda a O(log n), aunque insertar o eliminar requiere desplazar elementos.
- Árbol AVL: permite operaciones del índice en O(log n), pero exige alturas, rotaciones y balanceo.

Se eligió el arreglo ordenado por su sencillez y por los resultados medidos. Para 25 fichas, los desplazamientos son pequeños. AVL no se implementó ni se midió: no se afirma que sea más lento. Se considerará si las mediciones del juego muestran que muchas inserciones o una capacidad grande justifican esa complejidad. AVL tampoco elimina el recorrido LRU para encontrar fichas no protegidas.

#### Complejidad

Con n fichas residentes:

| Operación | Complejidad | Motivo |
|---|---|---|
| Buscar una ficha | O(log n) | Búsqueda binaria |
| Mover un nodo conocido al frente | O(1) | Cambio de enlaces |
| Insertar una ficha nueva | O(n) | Desplazamientos en el arreglo |
| Desalojar | O(n) | Recorrido de fichas protegidas y desplazamientos |
| Memoria del índice y LRU | O(n) | Ambas estructuras comparten nodos y fichas |

Estas cotas cuentan comparaciones de IDs; comparar cadenas también depende de su longitud. No describen el costo completo de preparar una sala ni de actualizar todas sus referencias.

#### Mediciones

Se comparan búsqueda binaria y lineal sobre el mismo arreglo ordenado y el mismo LRU. Así se aísla la estrategia de búsqueda; no se compara contra un arreglo desordenado con inserción al final.

La medición usa una caché nueva por repetición, calentamiento y orden alternado de estrategias. Se verifican los mismos conteos y el mismo orden LRU final. La preparación queda fuera del tiempo medido. Las cargas son sintéticas, no frecuencias observadas en una partida.

Medición local registrada durante la implementación, con Python 3.15.0a5 en Windows:

```powershell
python main.py --bench --capacidades 25 --operaciones 1000 --repeticiones 3 --escenarios mixta_90_10
```

| Medición | Promedio | Mínimo–máximo |
|---|---:|---:|
| Búsqueda binaria, 90 % aciertos y 10 % fallos | 0.591 µs/op | 0.571–0.610 |
| Búsqueda lineal, misma carga | 0.848 µs/op | 0.821–0.896 |
| Recuperación desde disco, carga separada | 200.222 µs/op | 192.249–206.353 |

En esa carga la estrategia lineal tardó aproximadamente 1.43 veces lo que tardó la binaria. La recuperación desde disco se midió por separado, forzando una recuperación por operación y verificando cero solicitudes de red.

Como referencia adicional, la medición del 2026-10-01 usó 10 000 operaciones, cinco repeticiones y semilla 20261001. En la mezcla 90/10 obtuvo:

| Capacidad | Binaria (µs/op) | Lineal (µs/op) |
|---:|---:|---:|
| 25 | 0.769 | 1.056 |
| 250 | 1.053 | 6.086 |
| 2500 | 1.915 | 72.466 |

Son ejecuciones con parámetros diferentes y no deben mezclarse como una misma muestra. Los resultados varían según el equipo y deben repetirse en el entorno de defensa.

Estas mediciones no demuestran todavía que el ciclo completo del juego cumpla el límite de 20 ms.

### 4. Persistencia y versiones

Se consideró guardar todo en un único archivo JSON o guardar registros separados por versión e ID. Se eligieron archivos separados para recuperar una ficha sin cargar todo el catálogo. La desventaja es manejar más archivos.

Las respuestas descargadas se guardan antes de utilizarlas como fichas residentes. Así, al desalojar una ficha de RAM, su copia local sigue disponible. La persistencia corresponde al gestor y al almacén, no a la clase de caché por sí sola.

La versión de la cripta y la del catálogo se administran por separado. Una copia local antigua puede utilizarse si está completa; si faltan datos y el origen tiene otra versión, se informa VersionIncompatible en lugar de mezclar versiones.

Cada escritura utiliza un archivo temporal y luego reemplaza el destino, para reducir el riesgo de dejar JSON incompleto. Esto no equivale a guardar una partida ni constituye una transacción de todo el paquete.

Las pruebas verifican recuperación tras desalojo sin red, reutilización después de reiniciar, separación de versiones y rechazo de archivos inválidos.

### 5. Cliente HTTP y presupuesto

Se centralizaron las solicitudes en ClienteApi en lugar de repetir su lógica en cada método.

Se mantiene un UUID de cliente durante la ejecución y se cuenta cada intento, incluidos consultas de versión, páginas y reintentos. Al conocer los metadatos se configura el presupuesto y se comprueba también lo consumido al iniciar.

El error 429 usa el tiempo indicado por reintentar_en y tiene un límite de reintentos. Las esperas son de tiempo real; no avanzan el reloj virtual. Las redirecciones automáticas están desactivadas para evitar solicitudes fuera del contador.

Las pruebas cubren encabezados, rutas, presupuesto, reintentos y respuestas inválidas.

### 6. Modo offline y pruebas

Se eligió ClienteOffline con los mismos métodos públicos que ClienteApi, en lugar de repartir condiciones de conexión por los gestores. Las pruebas usan un servidor falso inyectable; la ejecución offline usa archivos persistidos.

Esto permite reutilizar catálogo y precarga sin solicitudes HTTP. Si falta un archivo necesario, se informa DatosNoDisponibles.

El formato local ya se probó con paquetes generados por el proyecto. Falta comprobar su compatibilidad con el paquete oficial del curso cuando esté disponible.

### 7. Separación entre datos y estado del juego

La parte B prepara información; el motor mantiene el estado mutable de la partida. Ni la caché ni las descargas forman parte del historial de deshacer.

El contenido descargado describe el estado inicial de una sala. Al revisitarla, el motor no debe utilizarlo para recrear enemigos derrotados u objetos recogidos.

Queda por acordar con las partes A, C y D cuándo anticipar salas, confirmar entradas y actualizar referencias. Los componentes deben soltar las referencias a fichas que ya no utilizan para permitir liberar memoria.

### Pendiente de agregar

- Frecuencias de consulta, inserción y desalojo observadas en partidas reales.
- Medición del ciclo completo del juego y verificación del límite de 20 ms.
- Pruebas integradas de movimiento, revisitas, inventario, enemigos y referencias activas.
- Resultado de validar el paquete offline oficial.
- Acuerdos de integración con las partes A, C y D.

La última ejecución registrada de las pruebas de la parte B completó 67 pruebas correctamente. No sustituye las pruebas del juego integrado.

## Persona C — Estado del jugador (inventario, historial, rastro)

### Inventario (§2.7, §4.5)

**Problema.** El inventario necesita recorrerse hacia adelante y atrás desde la
posición actual, soltar el objeto que se está viendo sin importar en qué
posición esté, mover al frente el que se equipa, y mostrar vistas ordenadas
(peso/valor/nombre) sin alterar el orden real. Con `inventario_max` típicamente
pequeño (10-20 objetos), pero la operación de soltar se ejecuta cada vez que el
jugador tira algo, sin importar dónde esté parado el cursor.

**Alternativas consideradas.** Un arreglo (lista de Python usada como
arreglo) con un índice de cursor era la opción más simple, pero soltar un
objeto en medio del arreglo obliga a recorrer y desplazar todos los elementos
posteriores para cerrar el hueco: O(n) en el peor caso, y ese costo depende
directamente de la posición del objeto soltado, justo lo que el enunciado pide
evitar. La alternativa elegida fue una lista doblemente enlazada propia.

**Decisión.** Lista doblemente enlazada con centinelas vacíos (`cabeza`/`cola`,
el mismo patrón que usó Persona B en `red/cache.py`) y un puntero `cursor` que
apunta directo al nodo que se está viendo. `avanzar()`/`retroceder()` mueven el
puntero; `soltar_actual()` desconecta el nodo al que ya apunta `cursor` sin
recorrer nada más; `equipar_actual()` reubica ese mismo nodo justo después de
la cabeza. Las vistas ordenadas recorren la lista, arman una lista aparte y la
ordenan con `utilidades.ordenamiento.ordenar` (de Persona D), sin tocar la
lista enlazada original.

**Complejidad.** `avanzar`/`retroceder`/`soltar_actual`/`equipar_actual` son
O(1): ninguno depende de cuántos objetos haya en el inventario ni de en qué
posición esté el cursor, porque todos parten de un puntero directo al nodo, no
de una búsqueda. `recoger` es O(1) (se inserta al final, contra el centinela
`cola`). `vista_ordenada` es O(n log n) en el peor caso (o O(n) si el
inventario ya está casi ordenado), delegado al ordenamiento de Persona D.

**Evidencia empírica.** Con `soltar_actual()` sobre inventarios de distinto
tamaño (10, 1 000 y 50 000 objetos), midiendo con `utilidades.medicion.medir`
(mediana de 7 repeticiones, GC deshabilitado durante la medición):

| n     | frente (ms) | medio (ms) | final (ms) |
|-------|-------------|------------|------------|
| 10    | 0.0011      | 0.0009     | 0.0010     |
| 1 000 | 0.0011      | 0.0012     | 0.0011     |
| 50 000| 0.0050      | 0.0060     | 0.0062     |

Para un mismo `n`, soltar al frente, al medio o al final cuesta prácticamente
lo mismo (la diferencia entre columnas es ruido de medición, no una tendencia),
que es la propiedad que pedía el enunciado. El leve aumento entre n=10 y
n=50 000 no viene de recorrer más nodos (`soltar_actual` no los recorre): es
el costo de construir un inventario de 50 000 objetos antes de medir, que deja
un heap de Python más grande y con peor localidad de caché. La operación en sí
sigue siendo un solo desenlace de puntero, independiente de `n`.

**Límites conocidos.** El diseño asume que `inventario_max` es pequeño (el
caso real del juego, con criptas que dan capacidades de 10-20). Si el juego
llegara a permitir inventarios de miles de objetos, la vista ordenada seguiría
costando O(n log n) por objeto de inventario mostrado, lo cual dejaría de ser
instantáneo para el jugador aunque las operaciones de navegación se mantengan
en O(1).

### Historial de retroceso / pergamino (§2.11, §4.6)

**Problema.** El pergamino debe revertir todo lo ocurrido entre la última
acción del jugador y la anterior (ataques, efectos, movimientos enemigos,
cambios de rastro, puertas, trampas), sin guardar copias completas del estado
del juego, permitiendo hasta 5 acciones de retroceso, y con la excepción de que
la cantidad de pergaminos nunca se restaura.

**Alternativas consideradas.** Guardar una copia completa del estado en cada
turno (serializar todo el juego en cada acción del jugador) es la opción más
simple de programar, pero está explícitamente prohibida por el enunciado y
además desperdicia memoria proporcional al tamaño completo del juego en cada
una de las 5 entradas del historial, sin importar cuántas cosas cambiaron
realmente en ese intervalo.

**Decisión.** Una pila manual de máximo 5 `RegistroTurno`, donde cada turno
guarda únicamente los deltas necesarios para deshacer ese intervalo: vida
anterior de los actores afectados, tiempo de rastro anterior de las salas
tocadas, qué eventos se crearon o cancelaron (para invertir con
`evento.cancelado`), y operaciones inversas de inventario. `usar_pergamino`
aplica esos deltas en orden inverso y, solo después, descuenta el pergamino sin
registrar ese descuento como delta (así la reversión nunca lo devuelve).

**Complejidad.** El costo de `usar_pergamino` es O(k), donde k es la cantidad
de cambios registrados durante ESE intervalo específico — no el tamaño total
del juego ni el número de salas de la cripta. Un intervalo corto y tranquilo
(pocos enemigos actuando) se revierte casi instantáneo; uno con muchos
enemigos rápidos actuando entre dos decisiones del jugador cuesta
proporcionalmente a esas acciones, que es exactamente lo que se necesita
revertir.

**Evidencia empírica.** Midiendo `usar_pergamino()` con turnos que registraron
distintas cantidades de deltas de vida:

| deltas en el turno | mediana (ms) |
|---------------------|--------------|
| 5                    | 0.0065       |
| 500                  | 0.0262       |
| 20 000               | 1.0105       |

El crecimiento es aproximadamente lineal con la cantidad de deltas
registrados, no con el tamaño de la partida: un turno con 20 000 deltas
(un caso extremo, muy por encima de lo que produce una cripta real entre dos
decisiones del jugador) tarda ~1 ms, y turnos normales (decenas de deltas)
tardan fracciones de milisegundo.

**Límites conocidos.** Si un solo intervalo entre dos decisiones del jugador
llegara a acumular decenas de miles de eventos (por ejemplo, muchísimos
enemigos muy veloces actuando repetidamente), el costo de revertir ese turno
específico crecería con esa cantidad. Esto no rompe el requisito de
rendimiento de §5.2 (que mide el costo de UN ciclo de eventos, no el de
revertir 5 turnos completos), pero es un límite real del diseño si en algún
momento se permitieran intervalos artificialmente largos.

### Rastro del jugador (§2.9, §4.7)

**Problema.** Cada sala debe recordar cuándo fue visitada por última vez, con
una frescura de 400 unidades, y la decisión de un enemigo rastreador debe
costar según el número de salidas de su sala (a lo sumo 4), nunca según el
tamaño de la cripta.

**Alternativas consideradas.** Usar un diccionario (sala_id -> tiempo) fue
descartado directamente porque el enunciado prohíbe `dict` como estructura de
búsqueda propia para los problemas evaluados en §4.

**Decisión.** Un arreglo (`list`, permitido como almacenamiento contiguo de
bajo nivel por §7) indexado directamente por el id de la sala. Marcar una
visita es escribir en esa posición; consultarla es leerla. La decisión de un
rastreador (`enemigos.decidir_accion` + `RegistroRastro.sala_mas_fresca`) solo
recibe como vecinas las salas conectadas por salidas abiertas de la sala
actual del enemigo (a lo sumo 4), nunca el mapa completo.

**Complejidad.** `marcar_visita`/`tiempo_de` son O(1): acceso directo por
índice. `sala_mas_fresca` es O(v), donde v es el número de vecinas recibidas
(máximo 4 en este juego, una por dirección), independiente de cuántas salas
tenga la cripta.

**Evidencia empírica.** Midiendo `sala_mas_fresca([...4 vecinas...])` sobre
criptas de distinto tamaño total:

| salas totales en la cripta | mediana (ms) |
|------------------------------|--------------|
| 100                           | 0.0058       |
| 10 000                        | 0.0062       |
| 1 000 000                     | 0.0074       |

El tiempo se mantiene esencialmente plano al crecer la cripta 10 000 veces (de
100 a 1 000 000 de salas); la pequeña variación es ruido de medición, no una
tendencia con el tamaño, porque la función solo toca las 4 posiciones de las
salas vecinas recibidas, nunca el arreglo completo.

**Límites conocidos.** El arreglo se dimensiona según el mayor id de sala
visto (con `_asegurar_capacidad`), así que una cripta con ids de sala muy
dispersos (por ejemplo, un id de 10 millones en una cripta de 20 salas)
reservaría memoria proporcional al id más alto, no a la cantidad real de
salas. No es un problema con las criptas del enunciado (ids consecutivos desde
1), pero sería un límite real si el API llegara a usar ids no consecutivos.

## Revision de arranque y cripta desconocida (2026-10-17)

Se conserva el trabajo anterior del repositorio. Esta revision modifica:

- El listado, la creacion de partidas y las acciones de la ventana ejecutan
  trabajo de datos en un trabajador. Tk procesa eventos y descarta comandos
  durante esa operacion; el controlador actualiza los widgets al terminar.
  Las acciones siguen siendo secuenciales y se graban despues de confirmarse.
  El cierre espera al trabajador antes de liberar la sesion. Durante la tarea
  se suspende la recoleccion ciclica automatica para que el trabajador no
  destruya objetos Tk; se restaura su estado anterior al finalizar.
- Los doce WAV originales se distribuyen preparados (625 KB en total). La
  copia conserva exactamente la senal sintetizada y mantiene la limpieza de
  temporales. Si falta un WAV, se usa la sintesis anterior. Con Python 3.14.6,
  la intro requirio aproximadamente 468 ms sintetizando y 4 ms copiando.
- El esqueleto usa un arreglo auxiliar ordenado con el algoritmo propio y
  busqueda binaria propia: validacion de duplicados O(n log n), consultas de
  salas O(log n), sin indice hash. Las paginas descargadas se guardan despues
  de validar el grafo; las paginas locales no se reescriben en cada arranque.
- La precarga termina inmediatamente si todas las salas tienen contenido.
  Consultar fichas residentes actualiza el LRU sin reconstruir las referencias
  de todos los actores. Se conservan capacidad, proteccion y carga de faltantes.
- El heap propio desplaza nodos hacia un hueco en vez de intercambiar dos
  posiciones en cada nivel. Conserva (tiempo, secuencia), cancelaciones y replay.

Validacion final: 399 pruebas, cero fallos y cero errores; una prueba de API
real omitida por requerir habilitacion explicita. Se activo el paquete local de
las cuatro criptas para probar las 116 salas, victoria, guardado y replay.
Tambien se completo una cripta sintetica de 137 salas con tipos nuevos,
enemigos de tres comportamientos, trampas, regeneracion y salida con llave.
El estado final del replay coincide con el de la partida.

Medicion final con Python 3.14.6, una ejecucion de rutas y replay, sin HTTP:

| Cripta | Acciones | Media ms | p95 ms | Maximo ms | Acciones >=20 ms |
|---|---:|---:|---:|---:|---:|
| 01 (6 salas) | 21 | 2.14 | 5.82 | 9.49 | 0 |
| 02 (20 salas) | 105 | 0.83 | 3.05 | 6.28 | 0 |
| 03 (40 salas) | 225 | 0.75 | 2.22 | 34.20 | 1 |
| 04 (50 salas) | 279 | 0.65 | 2.25 | 23.78 | 1 |
| Sintetica (137 salas) | 280 | 9.94 | 38.82 | 53.70 | 29 |

La accion completa incluye lectura local y esperas de lotes pendientes. La
ruta automatica ejecuta movimientos sin tiempo de reflexion del jugador y
puede alcanzar al trabajador. El GUI ahora procesa eventos durante esas
esperas; esto mejora la respuesta de la ventana sin ocultar el costo de carga.
Separadamente, los maximos del ciclo de un evento fueron 0.094, 0.067, 0.155 y
0.185 ms en las cuatro criptas. La sintetica proceso 74 552 eventos, con media
0.021 ms y maximo 28.90 ms; dos eventos superaron 20 ms. Esta muestra no permite
certificar un limite estricto de 20 ms para toda cripta desconocida. Los tiempos
de pared incluyen interrupciones del sistema y recoleccion de memoria; no se
descartaron los picos. El script registra ambas escalas para evitar confundirlas.

Reproducir desde la raiz:

```powershell
$env:CRIPTA_SIN_AUDIO = "1"
$env:CRIPTA_PAQUETE_API = ".cache/cripta"
python -m unittest discover -v
python -m tests.medir_rendimiento --paquete .cache/cripta
```

Los datos completos estan en `.cache/rendimiento.json` y la salida de la suite
en `.cache/pruebas-rendimiento.txt` (archivos locales ignorados por Git).
El benchmark excluye Tk y audio. Un perfil previo con cache visual vacia
dedico aproximadamente 0.82 s al primer dibujo, incluyendo la preparacion de
ambas orientaciones del personaje; ese costo grafico inicial sigue existiendo.
El resultado tampoco mide latencia, reintentos o disponibilidad del servidor.

Para la prueba del profesor siguen siendo relevantes dos limites del contrato:
la cache no admite mas tipos simultaneamente protegidos que su capacidad
(25 por defecto), y los arreglos del motor reservan memoria segun el mayor ID
de sala. Los IDs muy grandes y dispersos requieren otra representacion del
motor; esta revision no cambia ese contrato. La prueba sintetica demuestra
generalizacion de contenido, no compatibilidad con datos arbitrarios fuera de
los limites y esquemas soportados.

## Objetos y acciones: eliminar composicion durante la partida

El perfil de un cambio a equipo completo con cache visual vacia dedico 1.578 s
al dibujo: 0.849 s al reposo y 0.720 s a preparar ambas orientaciones de ocho
poses. La mayor parte correspondia a transformaciones, mascaras y transferencias
de imagenes a Tk, no a modificar estadisticas del motor.

Se distribuyen 152 composiciones PNG sin perdida (51.25 MB de disco), generadas
con `python -m utilidades.preparar_visuales`. Incluyen los ocho estados visuales
de coraza/daga/antorcha, las ocho variantes de bebida y tamanos comunes. Los
originales permiten adaptar otras dimensiones sin repetir la composicion.
La firma comprueba arte y codigo; no depende de rutas, fechas o LF/CRLF. El
paquete no contiene mapas, fichas, dificultades ni datos de ninguna cripta.
Si falta o es incompatible, se mantiene el respaldo anterior. Incluir
`vista/recursos/composiciones` al distribuir el proyecto evita perder esta mejora.

La vista ya no prepara dieciseis poses al iniciar o cambiar equipo. Cada accion
obtiene solo las poses que utiliza: dos para ataque/caida y cuatro para carrera.
Mantiene indices, alfa, duraciones y anclajes. Las secuencias de acciones tienen
un limite de ocho entradas; las demas caches conservan sus limites anteriores.
Las bebidas tambien tienen persistencia visual, sin afectar el catalogo.

Validacion: 409 pruebas, cero fallos y errores, una prueba de API real omitida.
Se compararon pixeles de todas las combinaciones contra el compositor original,
incluyendo bebidas, antidotos, alfa y reflejos. Se comprobaron paquetes ausentes,
corruptos, firmas distintas, LF/CRLF, tipos desconocidos, guardado, retroceso y
replay. La auditoria estatica de interfaz no reporta hallazgos.

`python -m tests.medir_presentacion` mide 32 escenarios en 1100x760 y 1280x850,
primero con caches de aplicacion vacias y despues reutilizando recursos. Incluye
las combinaciones de equipo y bebidas, nueve objetos, recoger, soltar, atacar,
esperar, retroceso, cargar, desplazamiento, derrota y una sala poblada.

| Presentacion | Media ms | p95 ms | Maximo ms |
|---|---:|---:|---:|
| Primer uso (64 muestras) | 75.78 | 135.96 | 207.53 |
| Repeticion (64 muestras) | 24.35 | 29.50 | 46.90 |

Equipo completo: 63.90/77.30 ms en primer uso y 22.37/20.68 ms al repetir en
las dos ventanas. Atacar: 64.66/97.51 ms en primer uso y 19.61/20.12 ms al repetir.
Los picos restantes corresponden sobre todo al primer desplazamiento y a salas
pobladas. Las fotos Tk todavia tienen un costo de creacion; no se garantiza un
limite estricto de 20 ms para la presentacion.

Son mediciones de snapshots sinteticos con Python 3.14.6, no una medicion de HTTP
ni del motor. No incluyen la pausa intencional de las animaciones; en movimiento
se dibujan salida y llegada sin esa pausa. La cache del sistema operativo puede
estar caliente. El detalle esta en `.cache/presentacion.json` y la suite en
`.cache/pruebas-objetos.txt`. El script no genera partidas ni consume solicitudes.

## Medicion especifica de puerta a puerta

`python -m tests.medir_puertas` ejecuta 32 recorridos con callbacks reales de Tk:
cuatro direcciones, 1100x760 y 1280x850, sin equipo y con equipo completo,
primer uso y repeticion. Usa movimientos del motor en dos salas sinteticas y
verifica que sus 26 pasos visuales no alteran el estado posterior al movimiento.
No mide HTTP ni representa todas las salas posibles del servidor.

Se corrigio una deriva del temporizador: antes esperaba otros 20 ms despues de
cada callback, sumando el costo de dibujo y los retrasos de despacho de Windows.
Ahora agenda respecto al siguiente instante previsto. Ante una pausa larga
reinicia la cadencia sin rafagas ni saltos de pasos. Los diez pasos de salida y
dieciseis de entrada conservan su intervalo objetivo de 20 ms y su tiempo virtual.

Maximos observados por grupo, en milisegundos:

| Medicion | Primera vez, antes | Repetido, antes | Primera vez, despues | Repetido, despues |
|---|---:|---:|---:|---:|
| Dibujo de salida | 231.73 | 33.61 | 242.11 | 30.54 |
| Redibujo de llegada | 194.78 | 6.43 | 219.75 | 8.17 |
| Callback normal (sin redibujo de llegada) | 5.06 | 2.95 | 3.28 | 3.08 |
| Tiempo total, incluida la animacion | 1159.80 | 812.27 | 949.84 | 549.80 |

La mejora es de cadencia, no de creacion de bitmaps: el primer cruce conserva
pausas al cargar poses y dibujar una orientacion aun no utilizada. No se ocultan
esos picos. Al repetir, el peor recorrido queda cerca de los 520 ms previstos
para 26 pasos; los callbacks normales tardan aproximadamente 3 ms o menos.
La medicion de antes/despues son ejecuciones independientes, sujetas a variacion
del sistema operativo. Los maximos de distintas columnas pueden ser casos distintos.

Validacion de este ajuste: 31 pruebas aprobadas de animacion, cadencia, puertas,
trampas y transicion de inicio; auditoria estatica sin hallazgos. El detalle de
los recorridos posteriores esta en `.cache/puertas.json`.


## Decisión de diseño: verificador de resolubilidad

Fecha: 2026-11-02. Usamos arreglos ordenados con búsqueda binaria propia para
convertir IDs a posiciones compactas. El recorrido usa una cola con lista e índice,
marcas de salas alcanzadas y puertas pendientes agrupadas por llave. Cada sala se
procesa una vez; obtener una llave habilita sus pendientes sin recorrer el mapa
completo de nuevo. El orden es determinista y se conserva la primera evidencia
de entrada a cada sala y obtención de cada llave.

Las ubicaciones repetidas de una llave son alternativas. Si no aparece en un
listado completo válido, no se puede obtener. Si faltan datos o la versión cambia,
el resultado es `no_completada`, sin presentar un diagnóstico parcial como hecho.
El criterio acumulativo fue aceptado por el profesor según lo informado por el
usuario: no exige una trayectoria única y esa limitación se incluye en el resultado.

Para explicar bloqueos guardamos un único grafo de condiciones: una sala o llave
puede tener alternativas; pasar una puerta cerrada requiere su origen y su llave.
Kosaraju iterativo identifica grupos circulares y muestra un ciclo concreto por
grupo. Se conservan todas las alternativas mediante referencias compartidas y se
distinguen bloqueo circular autónomo, dependencias con bloqueos externos y ciclos
en regiones desconectadas. Un ciclo encontrado no se presenta como causa única.

La preparación reutiliza el cliente y el almacén existentes. Las respuestas nuevas
quedan en memoria hasta validar el conjunto y confirmar la versión final. Después
se escriben páginas y llaves; los metadatos y `actual.json` se publican al final
cuando corresponde una versión nueva. La escritura es atómica por archivo, no
una transacción de todo el conjunto. El modo offline exige datos completos de la
versión seleccionada y no hace HTTP.

### Complejidad y comparación

Con N = salas + salidas + llaves + ubicaciones, la normalización cuesta O(N log N)
y el recorrido y diagnóstico O(N), más el tamaño del reporte. El total es
O(N log N + salida), considerando aparte el costo de comparar IDs de texto.
No se declara estrictamente lineal. FR-015 conserva pendiente la revisión académica
de crecimiento aproximadamente lineal con la evidencia disponible.

La referencia repetitiva vuelve a recorrer las salas después de obtener llaves;
solo pertenece al benchmark. En una cadena de 128 salas procesó 8.256 salas frente
a 128 del incremental. Los dos algoritmos se comparan después de validar dictámenes
y órdenes. El incremental no tiene por qué ganar en todas las muestras pequeñas.

Promedios de diez repeticiones, en milisegundos; semilla 20261102:

| Familia | Salas | Incremental | Repetitivo |
|---|---:|---:|---:|
| cadena | 32 | 0.365 | 0.512 |
| cadena | 64 | 0.786 | 1.320 |
| cadena | 128 | 1.779 | 3.927 |
| ciclo | 32 | 0.628 | 0.499 |
| ciclo | 64 | 1.170 | 1.140 |
| ciclo | 128 | 2.308 | 2.407 |
| alternativas | 32 | 0.514 | 0.675 |
| alternativas | 64 | 1.270 | 1.828 |
| alternativas | 128 | 2.602 | 4.821 |

### Cripta publicada y alcance de la evidencia

El listado consultado identificó `cripta-06` como la mayor: 300 salas, versión
`f9ed9afa683d`. Tiene 760 salidas y el verificador obtuvo cuatro llaves; el dictamen
fue resoluble. El benchmark incluye normalización, recorrido y construcción del
resultado; en un resultado positivo no se ejecuta diagnóstico de bloqueo.

| Estrategia | Promedio ms | Mínimo ms | Máximo ms | Desviación ms |
|---|---:|---:|---:|---:|
| incremental | 2.721 | 2.522 | 3.586 | 0.295 |
| repetitivo | 3.064 | 2.653 | 3.550 | 0.270 |

Muestras incrementales totales (ms): 3.585800, 2.539700, 2.596400, 2.679100, 2.672600, 2.715600, 2.618800, 2.707800, 2.521500, 2.577100.

La lectura local y validación se midieron aparte: promedio 6,519 ms y cero HTTP.
La adquisición inicial tardó 4.894,375 ms y consumió 11 solicitudes, incluido el
listado. Esa adquisición incluye validación y persistencia, no solo espera de red.

Equipo: Windows 11, Intel64 Family 6 Model 170 Stepping 4, GenuineIntel;
Python 3.15.0a5. Las muestras completas, mínimos, máximos, desviaciones, tamaños,
longitudes de IDs, conteos y razones temporales por fase están en
[mediciones.json](specs/001-verificador-resolubilidad/mediciones.json).

Las diez muestras del análisis real quedaron por debajo de 200 ms. Esto demuestra
el resultado observado en ese equipo y versión, no garantiza futuras criptas ni
el límite de 20 ms del juego completo. Los negativos se cubren con mediciones
sintéticas de ciclos. La integración del comando general de medición pertenece a D.

Validación ampliada: 175 pruebas aprobadas y una opcional omitida. Se probaron
además 60 mapas sintéticos contra un recorrido de referencia, certificados y
arcos contrastados con la entrada, ciclos de 1.600 salas sin recursión, cambios de
versión seguidos por una ejecución offline nueva y conservación de archivos previos.
Auditoría estática de los tres módulos nuevos: sin índices hash, ordenamientos
automáticos ni comentarios nuevos. No se modificaron `main.py` ni `bench.py`.
## Parte II — fragmento persistible de línea de tiempo (incremento independiente)

Especificación: [spec.md](specs/004-linea-tiempo/spec.md), FR-011/012. Diseño: [plan.md](specs/004-linea-tiempo/plan.md), sección de persistencia independiente. No es todavía la decisión final sobre el archivo integrado de partida.

Problema: preservar y reconstruir la rama vigente sin copiar el estado completo en cada acción y sin depender de los productores reales del motor. Alternativas: almacenar controles redundantes o guardar base y registros y regenerarlos al cargar. Decisión: fragmento binario versionado CRLH 1 con base y deltas; K y correcciones conservados; regeneración determinista de controles. Se mantiene el guardado CRPT del juego intacto. Se evita pickle y no se usan índices dict/set ni bibliotecas de estructuras prohibidas.

El tamaño del fragmento crece con la base y los registros, no con acciones por tamaño total del mundo. La carga recorre las acciones y aplica cambios, más copia del estado cada K acciones: no tiene el límite de K aplicable a consultas individuales. La búsqueda de campos es binaria propia; creación/eliminación puede desplazar el arreglo completo. Los valores repetidos grandes en deltas también ocupan espacio: no se afirma memoria óptima.

Evidencia de corrección, no de rendimiento: 31 pruebas de historia/persistencia aprobadas, 164 con regresión seleccionada; detalle en [baseline.md](specs/004-linea-tiempo/baseline.md). Incluye 5000 acciones y continuación del azar sintético. La decisión coincide con el plan de este incremento. No hay mediciones finales de latencia/memoria ni elección empírica definitiva de K.

Límites: acceso por salas, identidad/versiones de cripta y formato integrado 4 pendientes; el PDF P1 recibido estaba vacío y debe revisarse al estar disponible. Que el fragmento rechace CRPT no certifica la incompatibilidad mediante la carga interactiva del juego. No se atribuyen efectos reales del motor a registros sintéticos.


## Parte II — núcleo histórico y política de errores

Referencias: [spec.md](specs/004-linea-tiempo/spec.md), FR-001–FR-012 y FR-020; [plan.md](specs/004-linea-tiempo/plan.md); [matriz de errores](specs/004-linea-tiempo/errores.md). La decisión coincide con el plan documentado antes de este incremento; la aceptación dentro del juego sigue pendiente.

### Registro, consultas y recorte

Problema: consultar antes de una acción o entre eventos, conservando el presente y evitando una copia completa por acción. Se consideraron snapshots por acción (no permitidos fuera de la cadencia K), volver a simular comandos y aplicar cambios tipados sobre estado puro. Se eligieron cambios tipados, separados de los callbacks de retroceso P1, bloques de hasta K acciones y reconstrucción hacia adelante. Se registra presencia anterior/nueva para distinguir creación, eliminación y valor nulo. Las correcciones persistentes se adjuntan a la frontera recortada y actualizan un control existente si coincide con ella.

El índice de acciones se consulta por búsqueda binaria propia; localizar un campo en arreglo ordenado cuesta O(log(numero de campos)), mientras insertar o eliminar puede desplazar O(numero de campos). Consultar copia una base y aplica cambios de <=K acciones, pero su tiempo también depende del tamaño del estado y de los cambios. Recortar no recorre el prefijo; liberar el sufijo cuesta según los registros descartados. Los bloques usan arreglos básicos; no se introducen dict/set como índices ni bibliotecas de estructuras prohibidas.

Evidencia: pruebas por tiempo/ordinal, eventos empatados, consultas aisladas, creación/eliminación, errores atómicos, recorte/repetición y 5000 acciones. No se presentan esas pruebas como mediciones de tiempo o memoria; K=50 sigue siendo inicial, pendiente de bench.

### Errores del dominio y de archivo

Problema: permitir al controlador distinguir una entrada inválida, una referencia fuera de la rama, registros incoherentes y archivos incompatibles o dañados. Alternativas: un ValueError indiferenciado, valores centinela que el consumidor podría ignorar, captura genérica de todas las excepciones o clases específicas. Se eligieron clases del dominio derivadas de ValueError y las excepciones de archivo ya existentes en datos. Esto conserva compatibilidad y causas técnicas sin acoplar modelo a vista.

Registrar/recortar valida antes de mutar; cargar construye una instancia nueva; guardar reemplaza el destino al completar el temporal. Si falla también la limpieza, se añade una nota al error principal para conservar el diagnóstico original. Rutas y tipos de entrada inválidos tienen mensajes presentables; errores inesperados de programación no se silencian.

Evidencia: 8 pruebas nuevas de errores; 39 entre errores/historia/persistencia y 172 incluyendo regresión seleccionada, aprobadas. Casos y mensajes en errores.md; comando y alcance en baseline.md. No se afirma que el controlador ya maneje estos errores dentro del juego.

## Parte II · Integración y mediciones de la persona D

Referencias: [especificación](specs/004-linea-tiempo/spec.md),
[plan](specs/004-linea-tiempo/plan.md) y
[contrato](specs/004-linea-tiempo/contracts/interfaces.md).

**Captura y reconstrucción.** Se mantiene la decisión del plan de avanzar
desde la base o el punto de control más cercano anterior. Los productores
entregan cambios por acción y evento. El consumidor localiza la acción con
búsqueda binaria propia (O(log A)) y reconstruye como máximo K acciones.
El costo también depende del número de cambios por acción y del tamaño de
la base que se copia. El recorte reconstruye hasta el límite, aplica las
correcciones persistentes y libera el sufijo, sin recorrer el prefijo.

**Persistencia.** CRPT v4 conserva el índice ordenado de salas y añade un
descriptor de un bloque CRLH. El estado actual conserva identidad, versiones,
agenda y RNG. CRLH guarda K, base y deltas de la rama vigente. Al cargar se
regeneran los controles. Se prefirió esto a escribir también las copias de
control, que son derivables. El lector de partida detecta v3, longitudes
inválidas, corrupción y fronteras incoherentes antes de entregar la restauración
al productor. La escritura usa temporal único en el directorio de destino y
reemplazo atómico. Leer una sala continúa sin cargar la historia.

**Comandos y replay.** La consulta interactiva y el replay comparten un
formateador puro. Replay se ejecuta sin vista y no detiene la reproducción
por tiempo si el resto del log todavía contiene una carga o un posible
pergamino capaz de sustituir esa rama. Si la acción terminal ocurre en el
instante de decisión, la consulta exacta muestra el estado previo. Un replay
pedido después del fin muestra el estado final efectivo. El verificador
mantiene separado un dictamen negativo de una comprobación incompleta.

**Protocolo de medición.** Windows 11, AMD Ryzen 7 7730U, Python 3.12.14,
semilla 20261001, una pasada de calentamiento y cinco repeticiones.
37 instantes por repetición, con extremos y consultas reproducibles.
Se comparan resultados de cada consulta antes de aceptar una medición.
Los tiempos no incluyen red, archivos ni vista. Memoria retenida y pico
son asignaciones observadas por tracemalloc durante la construcción,
no el consumo total del proceso. El recorte descarta cinco acciones
en prefijos del 25 %, 50 % y final de la carga.

```powershell
python main.py --bench --subsistemas historia --operaciones 5000 --salas 256 --cambios-historia 2 --repeticiones 5 --semilla 20261001
python main.py --bench --subsistemas historia --operaciones 10000 --salas 128 --cambios-historia 3 --repeticiones 5 --semilla 20261001
```

| Acciones | K | Controles | Memoria B | Pico B | Consulta mediana / p95 / máx. ms | >50 ms | Máx. acciones |
|---:|:---|---:|---:|---:|---:|---:|---:|
| 5.000 | 10 | 501 | 6.310.928 | 6.523.072 | 0,0958 / 0,2114 / 1,1034 | 0/185 | 10 |
| 5.000 | 50 | 101 | 5.052.248 | 5.327.504 | 0,3199 / 0,9172 / 1,3961 | 0/185 | 50 |
| 5.000 | 100 | 51 | 4.965.136 | 5.240.392 | 0,6760 / 1,6518 / 2,0596 | 0/185 | 100 |
| 5.000 | Sin controles | 1 | 4.428.008 | 4.703.672 | 39,7454 / 77,3422 / 100,3585 | 67/185 | 5.000 |
| 10.000 | 10 | 1.001 | 15.081.760 | 15.616.024 | 0,1043 / 0,2935 / 0,3933 | 0/185 | 10 |
| 10.000 | 50 | 201 | 13.433.032 | 13.974.464 | 0,4197 / 1,1137 / 1,4751 | 0/185 | 50 |
| 10.000 | 100 | 101 | 12.970.400 | 13.511.832 | 0,8310 / 2,4120 / 2,9470 | 0/185 | 100 |
| 10.000 | Sin controles | 1 | 12.206.248 | 12.775.248 | 104,8145 / 183,3384 / 253,1964 | 139/185 | 10.000 |

K=50 usa 20 % menos memoria retenida que K=10 con 5.000 acciones, y su
p95 es 0,9172 ms. K=100 ahorra alrededor de 1,7 % adicional en esa carga
y reconstruye hasta el doble de acciones. Por eso se conserva K=50.
En las dos cargas, la búsqueda para K=50 tuvo p95 de 0,0308 y 0,0344 ms.
La reconstrucción medida por separado tuvo p95 de 0,9755 y 1,1854 ms.
El máximo de recorte con K=50 fue 0,8678 y 1,7655 ms. La alternativa
inversa desde el presente superó 50 ms en 68/185 y 132/185 consultas al
medirla junto a K=50. Para una misma carga, CRLH ocupó los mismos bytes
en las cuatro variantes: 586.434 con 5.000 acciones y 1.544.634 con 10.000.

Son mediciones de estructuras históricas con dos cargas sintéticas. La
segunda se ejecutó en el mismo equipo durante parte de las regresiones.
La medición con el motor instrumentado, el conocimiento real y la cripta
de referencia queda pendiente para evaluar su costo de captura y repetir
las mediciones de Parte I con la carga integrada.

**Guardado v4 frente a JSON (Parte I §4.10).** Python 3.14.6, 256 salas,
5.000 acciones, K=50, misma semilla, cinco repeticiones tras calentamiento.

```powershell
python main.py --bench --subsistemas guardado-historia --operaciones 5000 --salas 256 --repeticiones 5 --semilla 20261001
```

| Formato | Bytes | Escritura media ms | Carga media ms | Lectura de una sala ms |
|---|---:|---:|---:|---:|
| CRPT v4 | 601.167 | 8,89 | 460,17 | 0,53 |
| JSON | 1.207.040 | 23,22 | 445,07 | No disponible |

Se comprobó la igualdad de datos y de historia reconstruida. JSON usa la
misma representación hexadecimal del fragmento que el log de replay.
La escritura v4 incluye sincronización a disco. La comparación de carga
incluye decodificar la historia en ambos formatos. En esta muestra el
binario ocupa cerca de la mitad y conserva la lectura directa de una sala.
La carga completa resultó similar y el JSON fue algo más rápido en esta
ejecución.

## Revisión de FR-015 del 2026-11-10

Las [series de escalamiento](specs/001-verificador-resolubilidad/mediciones.json) comparan diez muestras por tamaño. Al pasar de 32 a 64 y a 128 salas, el trabajo incremental por unidad de N se mantuvo en torno a 1,50 en cadenas, 9,19–9,24 en ciclos y 1,20 con ubicaciones alternativas. Los tiempos medios en ms fueron 0,365 / 0,786 / 1,779, 0,628 / 1,170 / 2,308 y 0,514 / 1,270 / 2,602 respectivamente. Esto respalda un crecimiento cercano al lineal en el recorrido para esas cargas. El tiempo total aumentó entre 1,84 y 2,47 veces al duplicar aproximadamente N. La normalización ordena e indexa en O(N log N), con un total O(N log N + tamaño del reporte). La evidencia de estas tres escalas respalda la observación empírica y deja abierta su aceptación académica para FR-015.

Se repitió la medición por la función de B con la copia offline de `cripta-06`, versión `f9ed9afa683d`, 300 salas. En diez muestras el incremental promedió 3,412 ms con máximo de 4,060 ms. La referencia repetitiva promedió 3,875 ms con máximo de 4,922 ms. Se observaron cero solicitudes HTTP. Las diez ejecuciones incrementales quedaron bajo 200 ms. El comando general aún requiere el ajuste de D para publicar esa serie y ejecutar con los valores predeterminados. [Reproducción](specs/001-verificador-resolubilidad/quickstart.md).

**Conexión del benchmark de resolubilidad (Parte II §6.3).** El comando
general conserva sus cargas cortas. La comparación incremental y
repetitiva se selecciona con `--subsistemas resolubilidad`, que usa diez
repeticiones por defecto. Así se respetan las condiciones del verificador
sin cambiar las cargas de los demás subsistemas. La salida expresa la
desviación estándar en milisegundos con una etiqueta compatible con
CP1252. La corrida de integración produjo 18 filas para tres tamaños con
diez muestras por fila. La carga valida la conexión de D con B y no
sustituye la medición de la mayor cripta publicada.
[Plan de D](specs/004-linea-tiempo/plan.md) y
[evidencia de aceptación](specs/004-linea-tiempo/aceptacion.md).

**Paquete offline para verificar (Parte II §§3.5, 4.2 y 4.3).** La CLI
reutiliza la preparación de B para validar el esqueleto y las llaves
antes de descargar el contenido. La precarga queda ligada a la versión
validada. Al exportar desde otro paquete local, el cliente lee esa versión
y D copia su archivo de llaves al destino. Así se usa la misma validación
y el mismo presupuesto que en el verificador, y se evita publicar el
lote de llaves si la API cambia de versión durante su adquisición.
Con un paquete incompleto, la descarga devuelve un error y el inicio se
bloquea aun con `--forzar`. Los ensayos usan datos de prueba, con
transporte simulado para la adquisición y el cliente real para el tramo
offline. [Especificación de D](specs/004-linea-tiempo/spec.md) ·
[Plan de D](specs/004-linea-tiempo/plan.md) ·
[Pruebas de aceptación](specs/004-linea-tiempo/aceptacion.md).

**Medición de resolubilidad con un paquete local (Parte II §6.1).** D
reutiliza la preparación y medición de B. Carga la cripta elegida,
fija su versión y reporta por separado lectura y validación frente al
análisis con datos ya preparados. Ambos algoritmos analizan la misma
entrada. El resultado identifica la versión y registra todas las
muestras y el máximo en milisegundos. Un paquete incompleto termina
con error. [Plan de D](specs/004-linea-tiempo/plan.md) ·
[Evidencia de aceptación](specs/004-linea-tiempo/aceptacion.md#benchmark-de-un-paquete-offline).

**Medición de referencia (2026-11-09).** El listado del servicio identificó
`cripta-06` como la mayor, con 300 salas. El paquete de la versión
`f9ed9afa683d` se preparó con 11 solicitudes de un presupuesto de 63.
El benchmark se ejecutó después sin red ni renderizado, en Windows 11,
AMD Ryzen 7 7730U y Python 3.12.14.

```powershell
python main.py --bench --subsistemas resolubilidad --paquete .cache/resolubilidad/d-referencia --cripta cripta-06 --version-cripta f9ed9afa683d --repeticiones 10
```

| Fase | Media ms | Mínimo ms | Máximo ms | Desv. estándar ms |
|---|---:|---:|---:|---:|
| Lectura y validación del paquete | 23.917 | 18.310 | 36.503 | 5.436 |
| Análisis incremental | 9.279 | 7.971 | 16.140 | 2.332 |
| Análisis repetitivo | 9.942 | 8.840 | 11.555 | 0.864 |

- Preparación (ms) `21.782, 22.409, 19.039, 23.681, 36.503, 29.989, 26.879, 21.501, 19.074, 18.310`
- Incremental (ms) `8.019, 9.508, 8.575, 8.560, 8.067, 8.222, 8.974, 8.756, 16.140, 7.971`
- Repetitivo (ms) `8.840, 9.360, 9.689, 9.915, 10.707, 8.890, 11.128, 11.555, 9.662, 9.678`

Los dos algoritmos dictaminaron `resoluble` para `N=1068`.
El máximo incremental de 16.140 ms cumple el límite de 200 ms
en la versión y el equipo medidos. Incluye normalización, recorrido,
diagnóstico cuando corresponde y construcción del reporte. La
preparación se muestra aparte. Queda pendiente la revisión cruzada
con B y la medición del ciclo integrado con cazadores.

## D: aceptación del controlador con A/C reales — 2026-11-12

Problema: las pruebas anteriores de D usaban un productor de contrato mientras
A ya había entregado captura/restauración H3 offline y conexión del mapa de C.
Se añadió `tests/test_controlador_ac_real.py` sobre motor, datos offline,
conocimiento, planificador, control de viaje, binario y replay reales. La vista
es receptora de prueba. Se verifica la frontera de eventos por los comandos del
controlador y no escribiendo a mano su bitácora.

Se conserva la activación explícita de prueba de A. Activarla globalmente en
la CLI sería prematuro: el productor solo admite mover/esperar/atacar, la
restauración rechaza conocimiento activo y el movimiento no entrega hechos de
viaje. D no infiere daño desde la vida final ni reconstruye el mapa a partir de
datos precargados. La alternativa elegida es aceptar lo entregado y verificar
también los límites con pruebas negativas, sin ampliar reglas de A/C.

Las nueve pruebas nuevas pasaron en 2.376 s con Python 3.14.6. Esto acredita
funcionamiento en los escenarios documentados, no un límite de rendimiento.
La consulta no altera estado/azar/log; cargas inválidas no publican cambios;
el replay conserva la carga embebida aunque se elimine su archivo original.
El viaje cancelado no mueve; ante hechos ausentes se registra el primer paso
real y se impide continuar. Con mapa activo, carga rechazada conserva partida,
mapa, rama histórica y log. Aceptación conjunta completa sigue pendiente.
