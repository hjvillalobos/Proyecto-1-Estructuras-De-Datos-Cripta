# Es el documento donde todos irán anotando la justificación de sus estructuras de datos y alternativas descartadas.

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
