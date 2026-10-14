# Decisiones de diseño

## Revision integrada: 2026-10-14

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
