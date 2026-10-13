# Proyecto-1-Estructuras-De-Datos-Cripta

Diseño, implementación y evaluación de estructuras de datos en un juego de mazmorra dirigido por eventos.

## Jugar con la interfaz grafica

```powershell
python -m pip install -r requirements.txt
python main.py --gui
```

El jugador, las ratas, el guardian oseo, la pocion menor y la daga oxidada utilizan las imagenes locales de `vista/recursos/`. Los objetos muestran miniaturas en el suelo y al seleccionarlos en el inventario.
Pillow conserva la transparencia y mejora el escalado; si no esta instalado,
Tkinter puede cargar los PNG con un escalado basico. Los enemigos sin imagen local
se muestran con una representacion generica, sin cambiar su tipo ni estadisticas.

El inventario muestra los efectos del objeto seleccionado; las acciones muestran
su costo temporal. La agenda contiene proximos sucesos observables y el registro
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

Desde la raíz del repositorio:

```powershell
python -m unittest discover -v
python main.py --bench
python main.py --bench --capacidades 25 --operaciones 1000 --repeticiones 3 --escenarios mixta_90_10
```

Las pruebas usan respuestas simuladas y archivos temporales, sin acceder al servidor. La suite incluye regresiones de retroceso, carga, replay, efectos, cache, trampas y paginacion del GUI.
Verificacion del 2026-10-13: 203 pruebas aprobadas, carga real de los PNG, miniaturas y acciones de recogida verificadas, presentacion sin cambios en la simulacion y comprobacion de escenas normales y pobladas en Tkinter.

### Compatibilidad del guardado y replay

El formato binario actual es la version 2: permite guardar mas de 253 salas cargadas. Los archivos de formato 1 se rechazan con un mensaje de incompatibilidad; no se sobrescriben ni se convierten automaticamente.

Cargar requiere la misma cripta y las mismas versiones de cripta y catalogo de la sesion actual. El replay solicita las versiones de su encabezado y puede usar copias historicas locales. Cada carga exitosa anexa su estado al log, por lo que la reproduccion no depende de conservar el archivo binario original. Esta base de carga no forma parte del historial de retroceso, que sigue utilizando deltas.

Una segunda pocion de velocidad sustituye y renueva el efecto temporal desde la velocidad base. Al terminar el efecto se recupera esa base. El GUI permite recorrer paginas de enemigos y objetos del suelo sin consumir tiempo virtual.

El benchmark compara búsqueda binaria y lineal sobre el mismo arreglo ordenado y LRU. Incluye aciertos, fallos y cargas con inserciones. La recuperación desde disco se mide por separado y verifica cero solicitudes de red. --sin-disco permite medir solo memoria.

La salida muestra promedios, mínimos, máximos y conteos. Las mediciones de disco utilizan archivos temporales; los resultados se muestran en consola. Todavía falta medir el ciclo completo del juego.

Las decisiones y la evidencia están en [DECISIONES.md](DECISIONES.md). La bitácora y los prompts de referencia están en [PROMPTS_LLM.md](PROMPTS_LLM.md).
