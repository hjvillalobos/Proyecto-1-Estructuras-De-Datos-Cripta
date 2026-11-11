# Proyecto-1-Estructuras-De-Datos-Cripta

Diseño, implementación y evaluación de estructuras de datos en un juego de mazmorra dirigido por eventos.

## Preparación compartida de la Parte II

El equipo utiliza Codex con las habilidades de spec-kit v1.2.3 y scripts de
PowerShell. Las reglas comunes están en
[la constitución](.specify/memory/constitution.md), versión 1.1.0.
Los enunciados y las aclaraciones del profesor tienen prioridad.

### Preparar el entorno

Cada integrante necesita Git, PowerShell, acceso a Codex y Python 3.11 o superior
para el juego. Para instalar la herramienta de especificación necesita también
`uv`. El entorno de esta herramienta es independiente del entorno del juego.

Una vez integrada esta preparación en `main`, actualizar la copia local desde
esa rama y abrir la carpeta raíz del repositorio en Codex. No repetir `specify init`:
la configuración compartida ya está incluida en `.specify/` y las habilidades
están en `.agents/skills/`.

Instalar la versión acordada de la herramienta y verificarla desde la raíz:

```powershell
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.2.3
specify version
specify integration status
```

Si `specify` no se reconoce, ejecutar `uv tool update-shell` y abrir una nueva
terminal. La versión esperada es 1.2.3; el estado debe indicar `OK`, integración
predeterminada `codex` e integración instalada `codex`, sin archivos faltantes.
Si el resultado es diferente, revisar la configuración antes de reinstalarla.

### Flujo de trabajo por funcionalidad

La constitución es compartida; no se crea otra por integrante. Cada nueva
funcionalidad sigue estas habilidades en Codex, en este orden. Son instrucciones
para el agente, no comandos para pegar en PowerShell.

| Habilidad | Resultado que debe revisar el integrante |
| --- | --- |
| `$speckit-specify` | `spec.md`: comportamiento, requisitos y aceptación, sin adelantar la implementación. |
| `$speckit-clarify` | Aclaraciones que resuelven ambigüedades de la especificación. |
| `$speckit-plan` | `plan.md`: diseño, tecnologías, estructuras y cumplimiento de la constitución. |
| `$speckit-tasks` | `tasks.md`: tareas ordenadas y vinculadas con los requisitos. |
| `$speckit-analyze` | Revisión de coherencia entre especificación, plan y tareas. |
| `$speckit-implement` | Implementación y validación de las tareas revisadas. |

La especificación genera una rama y una carpeta de funcionalidad bajo `specs/`.
Cada integrante debe comprobar que trabaja en la rama y carpeta de su tarea.
La especificación debe estar revisada y confirmada en Git antes del código que
la implementa. Si cambia, confirmar primero su corrección en un commit separado.
Resolver los hallazgos críticos o altos del análisis antes de implementar.

Registrar los prompts textuales en [PROMPTS_LLM.md](PROMPTS_LLM.md), con fecha,
herramienta/modelo y uso de la respuesta. Las propuestas resumidas se identifican
como tales y no sustituyen el historial textual. Documentar las decisiones y
mediciones en [DECISIONES.md](DECISIONES.md), sin afirmar resultados no medidos.
El agente debe presentar los cambios documentales para autorización antes de
aplicarlos. Revisar el código y los resultados de las pruebas antes de integrar.

### Compartir la preparación

La rama de preparación es `preparacion-proyecto-parte-ii`. Su commit debe incluir
la configuración de `.specify/`, las habilidades de `.agents/skills/`, el README
y el registro de prompts. Revisar los archivos seleccionados antes de confirmar,
sin incorporar puntajes locales, configuración del IDE ni salidas generadas.
Después, publicar la rama y revisar su integración en `main`; los demás
integrantes actualizan su copia antes de comenzar sus funcionalidades.

Al completar esta documentación están preparados la constitución, la integración
de Codex y las habilidades. Quedan pendientes el commit y la integración en
`main`, y luego las especificaciones, planes, tareas y desarrollo de la Parte II.

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

Para guardar un paquete con esqueleto, llaves, contenido y catálogo de una
cripta, y comprobarlo sin conexión:

```powershell
python main.py --cripta ID --descargar-todo --datos-dir .cache/cripta
python main.py --offline .cache/cripta --verificar ID
```

La descarga verifica la versión de las llaves antes de dar el paquete por
completo. También puede copiarse un paquete local con
`--offline ORIGEN --cripta ID --descargar-todo --datos-dir DESTINO`. Si se
indica `--version-cripta`, la copia usa los datos de esa versión. Los
paquetes antiguos sin `llaves.json` requieren completar ese archivo con
los datos de la misma versión. Una verificación incompleta bloquea el
inicio incluso con `--forzar`.

Para descargar todas las criptas del listado y elegir cualquiera sin conexion:

```powershell
python main.py --descargar-todo --datos-dir .cache/cripta
python main.py --offline .cache/cripta --gui
```

Cada cripta usa una sesion y un presupuesto independientes. El UUID HTTP se
mantiene durante la ejecucion. Las respuestas quedan en la cache local ignorada
por Git; en otro equipo hay que descargarlas antes de jugar sin conexion.
La ruta predeterminada `.cache/cripta` se resuelve dentro del proyecto, aunque
se ejecute `main.py` desde otra carpeta. Una ruta personalizada se resuelve
desde la carpeta del comando; los errores offline indican la carpeta consultada.

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

El replay muestra el reloj virtual en el resumen y reporta los errores de
datos o de red. Los errores al preparar una partida se muestran en la interfaz
gráfica y permiten regresar al menú para reintentar o salir.

Con `--gui` aparece el menu de inicio: Jugar, Cargar partida, Replay, Puntajes y
Salir. Se navega con raton, flechas y Enter. No inicia la simulacion ni avanza el
reloj virtual. Una partida nueva empieza en t=0; cargar recupera el reloj guardado.
Replay reproduce la grabación automática en un proceso separado sin vista y
muestra su resumen en la ventana de juego. `--replay ARCHIVO` reproduce una
bitácora indicada por ruta y presenta el resumen en la terminal.

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


## Verificador de resolubilidad — Parte II

La implementación de B está disponible en `modelo/resolubilidad.py` y
`red/verificacion.py`. Usa listas, búsqueda binaria propia y recorrido incremental;
no emplea tablas hash como índices. Analiza alcanzabilidad acumulada, confirmada
por el profesor según lo comunicado el 2026-11-02. No garantiza una trayectoria
única cuando existen salidas sin regreso.

`verificar_resolubilidad(datos)` analiza registros preparados sin red ni disco.
`verificar_cripta(cliente, almacen, cripta_id, version_cripta=None)` prepara los
datos y devuelve `resoluble`, `no_resoluble` o `no_completada`. Una llave ausente
en un listado válido es un obstáculo; un archivo ausente, formato inválido o cambio
de versión impide completar la verificación. Las descargas nuevas se publican
solo después de validar el conjunto y confirmar su versión.

Ejemplo con datos locales previamente descargados:

```python
from datos.offline import ClienteOffline
from red.verificacion import verificar_cripta

cliente = ClienteOffline(".cache/resolubilidad/real")
resultado = verificar_cripta(cliente, cliente.almacen, "cripta-06")
print(resultado.estado)
print(resultado.limitacion)
print(resultado.causa)
```

Pruebas específicas:

```powershell
python -m unittest tests.test_resolubilidad tests.test_verificacion_datos tests.test_bench_resolubilidad -v
```

`utilidades/bench_resolubilidad.py` entrega `medir_resolubilidad`, `medir_datos` y
`medir_preparacion_offline`. La integración con D ofrece `--verificar`, `--forzar` y el benchmark de
resolubilidad. Los comandos están en la sección de D.
La revisión ejecutada aprobó 175 pruebas y omitió una prueba opcional existente.
Los comandos, los pendientes y las muestras están en la
[guía de validación](specs/001-verificador-resolubilidad/quickstart.md),
[DECISIONES.md](DECISIONES.md) y la
[evidencia de mediciones](specs/001-verificador-resolubilidad/mediciones.json).

## Parte II · Línea de tiempo (D)

La implementación de D recibe cambios serializables por evento, reconstruye
el pasado de forma aislada y usa `K=50` por defecto según las mediciones
sintéticas. Para una demostración autónoma de consultas, recorte y recarga,
ejecutar `python -m tests.demo_linea_tiempo`. El fragmento CRLH que usa el
núcleo es distinto del archivo de partida CRPT.
[Especificación](specs/004-linea-tiempo/spec.md) ·
[Plan](specs/004-linea-tiempo/plan.md) ·
[Decisiones y mediciones](DECISIONES.md) ·
[Manejo de errores](specs/004-linea-tiempo/errores.md)

```powershell
python main.py --cripta ID --checkpoint-cada 50
python main.py --verificar ID
python main.py --cripta ID --forzar
python main.py --replay partida.log --hasta 200
python main.py --bench --subsistemas historia --operaciones 5000 --salas 256 --repeticiones 5
python -m unittest tests.test_linea_tiempo tests.test_persistencia_historia tests.test_errores_historia tests.test_historia_motor tests.test_modos_historia tests.test_comandos_integracion tests.test_bench_historia -v
```

Durante el juego, `historia 200` consulta un instante y `historia #3` el
estado previo a la tercera acción. `mapa` muestra el mapa conocido, e
`ir a <sala>` muestra el motivo de detención del viaje. Los botones Historia,
Mapa y Viajar están disponibles en la interfaz gráfica. El replay, el
benchmark y la verificación por CLI funcionan sin crear vistas.

El guardado de Parte II usa CRPT v4. Conserva el estado actual y el bloque
histórico con su K y rama vigente. La entrada de carga de Parte II informa la
incompatibilidad de archivos v3. `--forzar` autoriza el inicio tras un
dictamen de cripta no resoluble. Una verificación incompleta impide iniciar.

Historia, mapa y viaje requieren los productores de A y C. En H3, D comprueba
con datos de prueba que la consulta por tiempo y por número de acción incluyen
el daño de los eventos empatados antes de la siguiente decisión. La prueba
con el motor real se omite hasta que este entregue los cambios históricos.

R4 se comprobó en `004-linea-tiempo` después de integrar el verificador de B.
El caso offline coloca la llave de salida detrás de su propia puerta.
`--verificar` muestra el ciclo, el inicio normal se bloquea y `--forzar`
permite iniciar conservando el dictamen. La prueba construye sus propios
datos y se ejecuta sin consultar la API.
[Contrato de integración](specs/004-linea-tiempo/contracts/interfaces.md) ·
[Matriz de aceptación y comandos de prueba](specs/004-linea-tiempo/aceptacion.md)

Con el módulo de B integrado, este comando compara el verificador
incremental con el repetitivo. La salida incluye la desviación estándar
en milisegundos y es compatible con CP1252. Al seleccionar
`resolubilidad`, se usan diez repeticiones si se omite `--repeticiones`.

```powershell
python main.py --bench --subsistemas resolubilidad --tamanos 8 16 32 --repeticiones 10 --semilla 20261108
```

Para medir una cripta de un paquete local, usar el mismo subsistema con
la carpeta y el ID. La salida indica la versión, las salas, el promedio,
el máximo, la dispersión y las muestras. La lectura y validación del
paquete se muestran aparte del análisis. Se puede fijar una versión
local con `--version-cripta VERSION`.

```powershell
python main.py --bench --subsistemas resolubilidad --paquete .cache/cripta --cripta ID
```

Para reproducir la comparación v4 y JSON de Parte I, usar
`python main.py --bench --subsistemas guardado-historia --operaciones 5000 --salas 256 --repeticiones 5`.
