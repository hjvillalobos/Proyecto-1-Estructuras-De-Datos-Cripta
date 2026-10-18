# Proyecto-1-Estructuras-De-Datos-Cripta

Diseño, implementación y evaluación de estructuras de datos en un juego de mazmorra dirigido por eventos.

## Jugar con la interfaz grafica

```powershell
python -m pip install -r requirements.txt
python main.py --gui
```

Jugar abre el selector con las criptas publicadas por la API. La consulta del
2026-10-14 devuelve Osario menor (6 salas, dificultad 1), Catacumbas menores
(20, dificultad 2), Catacumbas medias (40, dificultad 3) y Catacumbas profundas
(50, dificultad 4). Todas conservan el jugador con traje de tigre. El selector
usa los datos recibidos, no genera salas ni modifica la dificultad del motor.
Enter confirma, Escape o Volver regresan al menu. `--cripta ID` sigue permitiendo
iniciar directamente la cripta indicada.

Inicio y selector comparten un fondo de ladrillos de piedra con el personaje
original. El selector resalta la cripta elegida y actualiza sus salas y dificultad.
Este cambio es exclusivamente visual; no modifica los turnos ni el reloj virtual.

La casilla Sonido activa o silencia efectos cortos de pasos, puertas, ataques,
objetos, retroceso, victoria y derrota. En Windows usa winsound de la biblioteca
estandar, sin Pygame ni dependencias adicionales. Los WAV originales preparados
en `vista/recursos/sonidos` evitan sintetizar audio al abrir el menu. Se copian
a una carpeta temporal que se limpia al cerrar; si faltan, se conserva la sintesis
como respaldo. Una melodia corta suena al abrir
el menu de inicio, sin repetirse al redimensionar: un motivo original tenebroso
con campanas, graves y eco. Pasos y puertas usan golpes y ruido amortiguado.
No se usan sonidos ni melodias de otros juegos. No hay musica continua. Si el
audio no esta disponible, el juego sigue sin sonido. Para pruebas silenciosas,
definir CRIPTA_SIN_AUDIO=1 antes de ejecutar la suite.

El tigre original y sus animaciones se conservan. El fondo pintado, el guardian
ilustrado y los objetos de `objetos_ilustrados.png` unifican el arte con contornos
de tinta y luz ambar. La rata conserva su ilustracion; los PNG anteriores quedan
como respaldo. Los objetos muestran miniaturas en el suelo y en el inventario.
Pillow conserva la transparencia y mejora el escalado; si no esta instalado,
Tkinter puede cargar los PNG con un escalado basico. Los enemigos sin imagen local
se muestran con una representacion generica, sin cambiar su tipo ni estadisticas.

El inventario muestra los efectos del objeto seleccionado; las acciones muestran
su costo temporal. Las imagenes del personaje con equipo y bebidas se distribuyen
preparadas, para evitar componerlas al equipar o usar un objeto. Si se modifica
el arte o el compositor, regenerarlas con `python -m utilidades.preparar_visuales`.
Sin ese paquete se mantiene la composicion original como respaldo. Para medir
primer uso y repeticion de equipo, bebidas, objetos, combate y desplazamiento
en la vista: `python -m tests.medir_presentacion` (detalle en `.cache/presentacion.json`).

La agenda contiene proximos sucesos observables y el registro
conserva los ultimos 20 mensajes de ataques, trampas y acciones. El dano flotante
es visual y no modifica el reloj virtual.

Con la cripta local descargada puede reproducirse esta partida de verificacion:

```powershell
python main.py --offline .cache/cripta --cripta cripta-01 --gui --semilla 1916
```

Ruta verificada para esa version y semilla: norte, norte, recoger y equipar la
coraza, norte, recoger y usar la pocion, recoger la llave negra, abrir este y
atravesar la puerta. Termina con 4 de vida. No garantiza resultados para otras
semillas o versiones de la cripta.

## Parte B

Incluye cliente HTTP, precarga por lotes, catálogo, caché ordenada con LRU, persistencia por versiones y un adaptador offline.

El punto de entrada integra el motor con consola o Tkinter, guardado y reproduccion mediante --replay.

`main.py` interpreta argumentos y selecciona el modo de ejecucion.
`controlador/aplicacion.py` coordina menu, carga inicial, reintentos y partidas.
`red/sesion.py` administra la creacion, renovacion y cierre de cliente, catalogo
y precarga. El motor y las reglas de tiempo virtual permanecen independientes.

### Requisitos y ejecución

Python 3.11 o superior. Para acceder al servidor:

```powershell
python -m pip install -r requirements.txt
python main.py --listar
python main.py --cripta ID --cache-size 25
```

Sustituir ID por una cripta del listado. Todas las solicitudes, incluidos reintentos y consultas de versión, consumen presupuesto.

Para guardar el contenido completo disponible de una cripta:

```powershell
python main.py --cripta ID --descargar-todo --datos-dir .cache/cripta
```

Para descargar todas las criptas del listado y elegir cualquiera sin conexion:

```powershell
python main.py --descargar-todo --datos-dir .cache/cripta
python main.py --offline .cache/cripta --gui
```

Cada cripta usa una sesion y un presupuesto independientes. El UUID HTTP se
mantiene durante la ejecucion. Las respuestas quedan en la cache local ignorada
por Git; en otro equipo hay que descargarlas antes de jugar sin conexion.

Verificacion opcional del paquete completo descargado, sin solicitudes HTTP:

```powershell
$env:CRIPTA_PAQUETE_API = ".cache/cripta"
python -m unittest tests.test_criptas_api -v
```

Incluye las cuatro selecciones, incorporacion de las 116 salas, cobertura de
imagenes, guardado/carga, una victoria por cripta y replay con estado final igual.
Las rutas de prueba no garantizan ganar con cualquier semilla o version.

La descarga respeta el presupuesto y puede detenerse si este se agota. Para usar después esos datos sin conexión:

```powershell
python main.py --offline .cache/cripta --cripta ID
```

El modo offline no necesita requests. Requiere que existan los archivos necesarios y utiliza el formato local del proyecto; falta verificar el paquete oficial del curso.

--version-cripta y --version-catalogo permiten seleccionar versiones locales. No se completan datos antiguos descargando información de una versión distinta.

### Caché e integración

CacheCatalogoOrdenado usa búsqueda binaria propia y una lista doblemente enlazada LRU, sin tablas hash como índices. Ambas estructuras comparten nodos. La capacidad predeterminada es 25.

GestorCatalogo coordina memoria y disco. Sus métodos retener, liberar y fijar_referencias permiten proteger fichas mientras el juego las utiliza. Si las fichas activas no caben, se informa CacheSinEspacioError; no se expulsan fichas protegidas ni se amplía el límite silenciosamente.

GestorPrecarga ofrece preparar_cripta, anticipar, incorporar_pendientes y preparar_entrada. El controlador debe esperar por los datos necesarios antes de confirmar un movimiento. La precarga no activa enemigos ni avanza el reloj virtual.

Al revisitar una sala se debe conservar el estado del motor: las respuestas originales no deben recrear objetos recogidos o enemigos derrotados. Esta integración queda pendiente con las otras partes.

### Pruebas y mediciones

La carga inicial y las acciones de la ventana ejecutan el trabajo de datos fuera
del hilo de Tk; mientras tanto la ventana procesa eventos y descarta comandos
nuevos para impedir acciones duplicadas. Los widgets se actualizan en Tk al
terminar. Cerrar espera la finalizacion del trabajo antes de cerrar la sesion.

Auditoria de las cuatro criptas locales y de una cripta sintetica de 137 salas,
con victoria, guardado y replay:

```powershell
python -m tests.medir_rendimiento --paquete .cache/cripta
```

Guarda `.cache/rendimiento.json`: separa la accion completa (incluye datos locales
y espera de precarga) del ciclo de un evento. Muestra medias, p95, maximos y
conteos de operaciones de al menos 20 ms. No mide HTTP ni certifica una cripta
desconocida arbitraria. La preparacion grafica inicial sigue teniendo un costo
propio; no debe confundirse con el rendimiento del motor.

Desde la raíz del repositorio:

```powershell
python -m unittest discover -v
python main.py --bench
python main.py --bench --capacidades 25 --operaciones 1000 --repeticiones 3 --escenarios mixta_90_10
```

Las pruebas usan respuestas simuladas y archivos temporales, sin acceder al servidor. La suite incluye regresiones de retroceso, carga, replay, efectos, cache, trampas y paginacion del GUI.
Verificacion del 2026-10-14: 250 pruebas aprobadas. Incluye seleccion de inventario sin tiempo virtual, traslados de enemigos sin busqueda ni desplazamiento lineal, victoria condicionada a la apertura correcta y transacciones de cache encapsuladas en el adaptador. Se conservan las regresiones de reloj, retroceso por deltas, guardado, replay, errores de datos, menu y animaciones.

El personaje usa fotogramas de carrera al cambiar de sala, ataque tras una accion
aceptada y caida al perder. Son secuencias visuales desactivables; no avanzan el
reloj ni bloquean el juego. Sin Pillow o sin la hoja de acciones se usa el PNG original.

El replay mantiene visible el reloj virtual, permite Salir y muestra errores de
datos/red sin continuar la reproduccion. Los errores al preparar una partida se
muestran en el GUI y permiten regresar al menu para reintentar o salir.

Con `--gui` aparece el menu de inicio: Jugar, Cargar partida, Replay, Puntajes y
Salir. Se navega con raton, flechas y Enter. No inicia la simulacion ni avanza el
reloj virtual. Una partida nueva empieza en t=0; cargar recupera el reloj guardado.
Replay abre directamente la grabacion automatica y muestra "Ultima partida"
en el reproductor, sin pedir seleccionar un archivo. Si no existe, muestra un
aviso. `--replay ARCHIVO` conserva la reproduccion de otras bitacoras guardadas.

La escena incluye respiracion suave, entrada a salas y reaccion visual al dano.
La casilla Animaciones desactiva el movimiento. Estos efectos no consumen tiempo
virtual ni generan acciones; las flechas mantienen el movimiento por salas.

Al perder en el GUI se pregunta si se desea jugar de nuevo en la misma cripta.
Cada intento crea una partida y presupuesto de red nuevos. Una semilla indicada
con `--semilla` se conserva; en otro caso se genera otra. La bitacora de la nueva
partida reemplaza `datos_generados/partida.log`, como al iniciar una sesion normal.
Si falla la escritura de la bitacora, la sesion se detiene y se advierte que la
ultima accion ya se realizo pero la grabacion esta incompleta.

### Compatibilidad del guardado y replay

El formato binario actual es la version 3: conserva la evidencia de apertura con llave de cada puerta, ademas del soporte para mas de 253 salas cargadas. Los formatos 1 y 2 se rechazan con un mensaje de incompatibilidad; los archivos existentes no se borran ni se convierten automaticamente. Los logs antiguos que incluyen cargas sin esa evidencia tambien se rechazan, en vez de reproducir silenciosamente un estado ambiguo.

El GUI sincroniza el cursor al seleccionar un objeto. Soltar el objeto actual
reutiliza ese nodo, sin volver a buscarlo desde la cabeza. Seleccionar otro ID
puede requerir una busqueda, pero esa seleccion no consume tiempo virtual.

Los enemigos usan un arreglo por sala con posicion conocida por actor. Extraer
intercambia con el ultimo elemento y agrega al destino: O(1) por traslado.
Los deltas conservan el indice original para restaurar el orden al deshacer.

Cargar requiere la misma cripta y las mismas versiones de cripta y catalogo de la sesion actual. El replay solicita las versiones de su encabezado y puede usar copias historicas locales. Cada carga exitosa anexa su estado al log, por lo que la reproduccion no depende de conservar el archivo binario original. Esta base de carga no forma parte del historial de retroceso, que sigue utilizando deltas.

Una segunda pocion de velocidad sustituye y renueva el efecto temporal desde la velocidad base. Al terminar el efecto se recupera esa base. El GUI permite recorrer paginas de enemigos y objetos del suelo sin consumir tiempo virtual.

El benchmark compara búsqueda binaria y lineal sobre el mismo arreglo ordenado y LRU. Incluye aciertos, fallos y cargas con inserciones. La recuperación desde disco se mide por separado y verifica cero solicitudes de red. --sin-disco permite medir solo memoria.

La salida muestra promedios, mínimos, máximos y conteos. Las mediciones de disco utilizan archivos temporales; los resultados se muestran en consola. Por defecto se miden cache, recuperacion de fichas, agenda, inventario, historial, ordenamientos, guardado/carga y ciclo completo sintetico. No se instancia la vista ni se usa HTTP.

```powershell
python main.py --bench --capacidades 25 --operaciones 1000 --repeticiones 3
python main.py --bench --subsistemas ordenamiento --tamanos 8 16 32 256
python main.py --bench --subsistemas ciclo --operaciones 100 --repeticiones 3 --paquete .cache/cripta --cripta cripta-01 --semilla 1916
```

`--subsistemas` permite elegir cache, agenda, inventario, historial, ordenamiento, guardado y ciclo. `--eventos` configura los eventos pendientes de agenda y por ciclo sintetico; `--salas` configura el estado sintetico de guardado. `--sin-disco` omite recuperacion persistente y guardado; un `--paquete` explicito sigue leyendo datos locales. Paquete e ID de cripta deben indicarse juntos.

El ordenamiento compara insercion, fusion y seleccion automatica con entradas aleatorias, casi ordenadas y comparaciones costosas. Guardado compara el mismo estado en binario y JSON, con bytes y tiempos, mas lectura directa de una sala binaria. Cada carga valida su resultado y descarta una repeticion de calentamiento.

El ciclo mide cada llamada completa a `Motor.ejecutar("esperar")` y reporta el maximo y cuantos ciclos alcanzaron 20 ms. La preparacion queda fuera del cronometro; con paquete, el contenido se precarga antes. La carga sintetica procesa eventos de rearme; la carga local espera en la sala inicial y termina si acaba la partida. Estas cargas no certifican todas las rutas ni una cripta desconocida; repetir sin otras pruebas o aplicaciones intensivas durante la defensa.

Las decisiones y la evidencia están en [DECISIONES.md](DECISIONES.md). La bitácora y los prompts de referencia están en [PROMPTS_LLM.md](PROMPTS_LLM.md).
