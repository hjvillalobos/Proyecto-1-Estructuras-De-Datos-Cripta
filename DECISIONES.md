# Decisiones de diseño

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

