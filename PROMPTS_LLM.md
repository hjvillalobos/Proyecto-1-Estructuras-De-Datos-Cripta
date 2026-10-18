# Bitácora de uso de LLM

Este archivo registra los prompts relacionados con el proyecto, conforme al apartado 10.3 del enunciado. Cada integrante debe agregar su propia entrada en el momento de usar un LLM.

## 2026-09-17

- **Herramienta/modelo:** Codex (GPT-5)
- **Prompt textual:** "Adjunto los PDFs del proyecto. Voy a desarrollar la Parte B ('Red, Cliente API y caché') en Python desde cero. Por favor, analiza mi sección y propón una hoja de ruta de alto nivel para que yo empiece a estructurar el código.
Durante el desarrollo, actuarás como mi revisor técnico: asegúrate de que mis avances cumplan los lineamientos del PDF (en especial el registro de prompts del LLM) y cuestiona cualquier mala decisión arquitectónica que yo tome."
- 
- **Uso de la respuesta:** Revisar el enunciado, identificar restricciones específicas para el rol B y definir exclusivamente el primer paso de implementación.

### 2026-09-18

- **Herramienta/modelo:** Codex (GPT-5)
- **Prompt textual:** "Ya creé el esqueleto de carpetas y los archivos correspondientes a mi parte del proyecto. Creé el repositorio en GitHub con mi rama features/cliente-api-mocks. Considero comenzar en cliente_api implementando lo del HTTP para interactuar con CRIPTA y la versión MOCK temporal que retorna diccionarios estáticos simulando respuestas JSON. Esto usando el contenido del enunciado del proyecto como ejemplo, tales como: Datos generales de una cripta, Esqueleto, Contenido de salas, Catálogo. Dame tu criterio."
- **Uso de la respuesta:** revisar el diseño inicial del cliente HTTP y del adaptador mock.

### 2026-09-19

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Aquí está mi implementación en Python de la clase ClienteApi que utiliza diccionarios estáticos del enunciado para simular las peticiones HTTP de datos generales, esqueleto, contenido y catálogo. ¿Está correcta la lógica de las funciones?"
- **Uso de la respuesta:** Identificar y corregir un error estructural en el diccionario base y en la lógica de filtrado de la función obtener_catalogo.


### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Ahora sigamos con el archivo catalogo.py. ¿Cómo hago la clase para revisar qué IDs faltan en la caché, pedirlos a la API en grupos de 10 y convertirlos en objetos FichaCatalogo?"
- **Uso de la respuesta:** Escribir la estructura de la clase GestorCatalogo para organizar las peticiones en lotes y mapear los JSON a los objetos del contrato.

### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Tengo que programar la tabla hash para la caché desde cero en Python, sin usar diccionarios (dict). Pensaba usar listas como si fueran arreglos estáticos en C++ y manejar las colisiones por encadenamiento. ¿Me ayudas con la estructura inicial y una función hash sencilla para llaves de texto?"
- **Uso de la respuesta:** Obtener la estructura base de la tabla hash usando listas nativas de Python para cumplir con las reglas del proyecto.


### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Necesito agregar una política de reemplazo (LRU) que controle que elementos deben salir de cache cuando este alcanza su capacidad máxima a la tabla hash previamente creada. Se debe verificar si el elemento se encuentra actualmente en uso, es decir si el ID tiene referencias activas ( en_uso > 0 ), esto con el fin de que el LRU no borre elementos que siguen vivos en el juego. Si dicho elemento tiene una referencia activa se debe pasar al siguiente y así sucesivamente hasta encontrar un elemento que no tenga esta particularidad. El método de orden será una lista doblemente enlazada, la implementación de la lista debe incluir una clase Nodo.  La misma será utilizada para llevar un control cada que vez que se inserta un ID. El fondo de la lista me dirá el candidato a ser eliminado."
- **Uso de la respuesta:** Escribir la lógica de desalojo en cache.py, implementando la clase NodoLRU para simular punteros, actualizando las funciones de búsqueda e inserción, y agregando un método para incrementar el contador de referencias.


### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Me gustaría revisar cómo se vería el archivo de pruebas (tests/test_cache.py) para confirmar que mi lista doblemente enlazada está desalojando el elemento correcto y respetando el contador de referencias activas."
- **Uso de la respuesta:** Crear casos de prueba automatizados usando unittest para validar la inserción, el desalojo estándar del elemento más antiguo y la protección de elementos bloqueados por el motor del juego.


### 2026-09-18
**Herramienta/modelo:** Claude (Anthropic, claude.ai) — Claude Sonnet 5

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Implementa la logica de los request en la funcion def _hacer_peticion_get manejando el error 429 con un tiempo de espera prudencial, ademas he completado las funciones actualizadas de cliente_api para usar la función central que maneja requests: obtener_datos_generales, obtener_esqueleto, obtener_contenido_salas y obtener_catalogo. Utilicé f-strings y join para los parámetros haciendo un llamado a la funcion _hacer_peticion_get previamente creada"
-  **Uso de la respuesta:** Validar la refactorización de las rutas, corrigiendo los endpoints /salas y /catalogo para coincidir con la especificación del servidor.
**Prompt textual**:

lee bien el enunciado paso a paso y la division de trabajo que mis compañeros y yo realizamos, dame el codigo por aca de la persona D que seria mi persona y que es lo que me toca, explicame y damelo comentado y sigue todo al pie de la letra.

Uso: generar la implementación inicial completa del módulo de la Persona D (ordenamiento, guardado binario, bitácora/replay, vista de consola, controlador, bench y main.py) y el contrato de dependencias con A, B y C.

### 2026-09-27
**Herramienta/modelo:** Claude (Anthropic, claude.ai) — Claude Sonnet 5

### 2026-10-01

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "No es posible el uso de tablas hash, siendo asi, que opciones de cambio tengo y por que ?"
- **Uso de la respuesta:** Comparar una búsqueda lineal, un arreglo ordenado y un árbol AVL como alternativas al índice hash de la caché, conservando la política LRU y la protección de fichas en uso.

### 2026-10-01

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Implementa un arreglo ordenado frente a búsqueda lineal en las mediciones y considera AVL si los resultados justifican su complejidad en el codigo"
- **Uso de la respuesta:** Sustituir el índice hash por un arreglo ordenado con búsqueda binaria, conservar y probar LRU, comparar contra búsqueda lineal con cargas reproducibles y documentar la evidencia y el criterio para evaluar AVL.
**Prompt textual**:
Mi parte del proyecto esta dividida en 3 ramas, ayudame visualizandndo si lo realicé de manera correcta para subir mis clases a la rama principal.

### 2026-09-21 (Persona C)

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pasé el enunciado completo, la división de trabajo del equipo (documento CRIPTA_Division_de_trabajo) y la documentación Swagger del API, aclarando que a mí me toca Persona C (inventario, historial de retroceso, rastro y enemigos), y le pedí que primero entendiera bien el proyecto antes de proponerme un plan.
- **Uso de la respuesta:** Entender el alcance completo de mi parte y armar el orden en que iba a implementar cada módulo (rastro -> inventario -> enemigos -> historial), verificado contra las secciones exactas del enunciado (§2.7-§2.9, §2.11, §4.5-§4.7).

### 2026-09-27 (Persona C)

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pedí implementar modelo/rastro.py, modelo/inventario.py, modelo/enemigos.py y modelo/historial.py según el plan que habíamos acordado, con pruebas unitarias, agregando solo la clase ObjetoInstancia a modelo/tipos.py de forma aditiva (idéntica a la que ya tenía Sebas en su rama) para no generar conflictos.
- **Uso de la respuesta:** Base de mis 4 módulos con 34 pruebas unitarias (unittest), todas corriendo correctamente.

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pedí revisar qué habían subido mis compañeros (a main y a sus ramas) y actualizar mi rama feature/estado-jugador sin romper nada de lo mío ni de lo de ellos.
- **Uso de la respuesta:** Fusionar los cambios de main (cliente HTTP real, ordenamiento, snapshots, vista, guardado binario) y traer utilidades/medicion.py de la rama de Belén, verificando en cada paso que las pruebas siguieran pasando. También cambié mi vista_ordenada del inventario para usar utilidades.ordenamiento.ordenar en vez de un ordenamiento propio, tal como lo pedía controlador/contrato.py.

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pedí ayuda para escribir las secciones de DECISIONES.md que me corresponden (inventario, historial, rastro), con evidencia real medida con --bench y no números inventados.
- **Uso de la respuesta:** Redactar las 3 secciones del Documento de Decisiones, con las mediciones reales que se obtuvieron corriendo utilidades/medicion.py sobre mis propios módulos.

Uso: repartir los archivos del módulo de D en las ramas de git del equipo, según sus dependencias internas y el orden correcto de merge.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Implementa ClienteApi para consultar el listado de criptas, datos generales, versiones, páginas del esqueleto, contenido de salas y catálogo. Mantén el mismo X-Cripta-Client-Id durante la ejecución. Cuenta cada intento contra el presupuesto, incluidos reintentos y consultas de versión. Maneja el error 429 usando reintentar_en, limita los reintentos y valida las respuestas. Las esperas de red no deben modificar el reloj virtual. Permite inyectar un transporte falso para las pruebas."
- **Uso de la respuesta:** Implementar el cliente HTTP, el control del presupuesto, los reintentos y las validaciones, permitiendo probarlo sin conexión real.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Implementa CacheCatalogoOrdenado con capacidad de 25 fichas, configurable. Usa un arreglo ordenado con búsqueda binaria propia y una lista doblemente enlazada LRU que compartan nodos. No uses bisect ni ordenamiento automático. Protege las fichas con referencias activas y desaloja la menos recientemente utilizada que tenga referencias == 0. Si ninguna puede salir, lanza CacheSinEspacioError sin superar la capacidad. Valida las actualizaciones de referencias."
- **Uso de la respuesta:** Implementar la caché con búsqueda binaria y reemplazo LRU, respetando la capacidad y protegiendo las fichas utilizadas por el juego.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Implementa AlmacenLocal para guardar el listado, metadatos, páginas, contenido y fichas en archivos JSON separados por versión e ID. Guarda las fichas descargadas para recuperarlas después de un desalojo sin repetir solicitudes. Administra por separado las versiones de cripta y catálogo y evita mezclar datos incompatibles. Usa archivos temporales antes de reemplazar el destino y reporta archivos ausentes o inválidos. No confundas este almacenamiento con el guardado de una partida."
- **Uso de la respuesta:** Implementar el almacenamiento local y la separación de versiones para reutilizar datos descargados y recuperar fichas desalojadas sin recurrir nuevamente a la red.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Agrega GestorCatalogo para buscar primero en memoria y después en disco, solicitando solo los faltantes en lotes de hasta 10 IDs distintos. Deduplica mediante listas y revisa las dependencias de suelta sin repetir descargas ni entrar en ciclos. Valida las respuestas y conserva el orden solicitado. Precarga en disco sin llenar la caché con fichas todavía inactivas. Permite retener, liberar y fijar referencias, y reporta aciertos, fallos, recuperaciones desde disco y solicitudes."
- **Uso de la respuesta:** Coordinar las consultas del catálogo entre caché, disco y API, resolver dependencias y administrar las referencias y métricas de uso.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Implementa GestorPrecarga para descargar todas las páginas del esqueleto, de hasta 50 salas por página, y cargar contenido en lotes de hasta 10 IDs distintos. Anticipa salas conectadas con listas y un recorrido por anchura de orden fijo. Reutiliza contenido válido, utiliza un solo hilo de precarga e incorpora los resultados de forma determinista. Si falta contenido necesario, espera antes de permitir confirmar la entrada. No actives enemigos ni avances el reloj virtual al descargar datos."
- **Uso de la respuesta:** Implementar la carga inicial y anticipada de salas, evitando solicitudes repetidas y separando la descarga de datos de las acciones del motor.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Necesito ClienteOffline con los mismos métodos que ClienteApi, leyendo los archivos locales sin realizar solicitudes HTTP. Informa claramente si faltan datos. Agrega al punto de entrada las opciones para listar, seleccionar cripta, configurar caché, seleccionar versiones, descargar contenido y trabajar offline. Mantén este punto de entrada como preparación de datos, sin implementar el motor. Deja explícita la validación pendiente del formato offline oficial."
- **Uso de la respuesta:** Incorporar el funcionamiento sin conexión y las opciones de ejecución de la parte B, dejando pendiente la integración con el motor y la verificación del paquete oficial.

### 2026-10-03

- **Herramienta/modelo:** Codex (GPT-6)
- **Prompt textual:** "Ahora Agrega pruebas de presupuesto, reintentos, validación, paginación, lotes, reutilización, versiones, referencias activas, LRU, persistencia y modo offline. Compara búsqueda binaria y lineal usando el mismo arreglo ordenado y LRU, con cargas reproducibles de consultas e inserciones. Mide por separado la recuperación desde disco y comprueba que no use red. Reporta promedios y variación. Considera AVL solo si los resultados justifican su complejidad; no afirmes que estas mediciones prueban el límite de 20 ms del juego completo."
- **Uso de la respuesta:** Crear pruebas automatizadas y mediciones reproducibles para validar la parte B, comparar las estrategias de búsqueda y evaluar la recuperación desde disco.

### 2026-10-12

- **Herramienta/modelo:** Codex (modelo cambiado durante la sesion).
- **Prompt textual:** "en la rama vista-controlador corrijamos los bugs de el GUI todos los que encontraste y tambien sigue los principios SOLID, es decir, solamente corrige los bugs pero el codigo debe mantener la estructura que ya llevas"
- **Aclaracion del alcance:** "GUI y todos los bugs del motor".
- **Uso de la respuesta:** Corregir llaves y victoria, recogida y entrega de comandos del GUI, retroceso mediante deltas, agenda de eventos, equipo, efectos, guardado y rastro, conservando MVC y las estructuras propias. Agregar pruebas de regresion y comprobar la ventana real de Tkinter. Resultado: 167 pruebas automatizadas aprobadas.

### 2026-10-12

- **Herramienta/modelo:** Codex.
- **Prompt textual:** "Corrige estos 10 bugs en la rama vista-controlador, siguiendo el enunciado y los principios SOLID, sin cambiar la estructura actual del proyecto. Agrega pruebas para verificar las correcciones."
- **Uso de la respuesta:** Corregir botin de pergaminos al retroceder, versiones y cargas en replay, validacion previa de guardados, limite de salas, referencias de cache, pociones superpuestas, multiples trampas, puntajes y paginacion del GUI. Mantener los modulos MVC y agregar pruebas reproducibles sin red real.
- **Verificacion:** 188 pruebas aprobadas, incluidas 21 nuevas; paginacion comprobada con clics reales de Tkinter. Al medir ciclos se detectaron referencias circulares de turnos descartados y se corrigieron sin cambiar el historial por deltas. Una medicion puntual de 100 ciclos con 300 enemigos activos, cache caliente y sin red ni renderizado obtuvo mediana de 5,683 ms y maximo de 15,214 ms; no certifica el rendimiento de todas las criptas.

### 2026-10-13

- **Herramienta/modelo:** Codex (GPT-6).
- **Prompt textual:** "Si, esta bien haz esas mejoras. Tambien te doy estas imagenes, el personaje que esta vestido de tigre podria ser el jugador y la rata, de los enemigos, me gustaria implementarlos"
- **Uso de la respuesta:** Integrar los PNG proporcionados, mejorar escena, contraste, tipografia, inventario, costos visibles, trampas, agenda y mensajes de combate. Separar recursos, tema y dibujo dentro de la vista. Conservar reglas, semilla, reloj, MVC, guardado y replay.
- **Verificacion:** 201 pruebas aprobadas; comprobacion de imagenes, disposicion en ventanas normal y compacta, textos sin solapamiento en una sala poblada, clic real de recogida y victoria reproducida con semilla 1916 y 4 de vida.

### 2026-10-13: recursos adicionales

- **Prompt textual:** "puedes poner estas imagenes en el juego para pocion, daga, guardian oseo como lo hiciste con la rata y el jugador"
- **Uso:** Integrar tres PNG locales por tipo de catalogo; miniaturas de suelo e inventario, conservando MVC y sin modificar reglas.
- **Edicion de imagenes:** Herramienta integrada imagegen, una llamada por imagen proporcionada, fondo transparente. Prompt comun: "Remove only the background from the supplied image. Preserve the original subject, its exact design, colors, silhouette and details. Remove all white/gray checkerboard or white background and exterior shadow. Output a tightly framed standalone game sprite with real transparent alpha background, complete subject fully visible, no added text or objects."
- **Recursos:** `vista/recursos/itm_pocion_menor.png`, `itm_daga_oxidada.png`, `ent_guardian_oseo.png`.
- **Verificacion:** 203 pruebas aprobadas y captura de la ventana real de Tkinter con los tres recursos; canales RGBA transparentes verificados.

### 2026-10-13: completar iconos

- **Prompt textual:** "puedes implementar esas imagenes y tambien todas las demas, pero hazlas a tu gusto."
- **Uso:** Conservar las imagenes originales del antidoto y antorcha. Generar coraza, llaves, pergamino y trampa con imagegen integrado; prompts en vista/recursos/README.md. Resolver la imagen de trampa por tipo de catalogo sin cambiar reglas ni estructura MVC.
- **Verificacion:** 204 pruebas aprobadas, todos los PNG con transparencia RGBA y comprobacion visual de los siete recursos nuevos en Tkinter.

### 2026-10-13: replay y nueva partida

- **Prompt textual:** "puedes solucionar los problemas porfa y tambien implementar que cuando el jugador pierde preguntar si quiere jugar de nuevo"
- **Uso:** Validar tipos y codificacion de bitacoras; mostrar errores persistentes de replay; detener la sesion ante fallos de escritura indicando que la accion ya ocurrio y la grabacion esta incompleta. Preguntar tras derrota en GUI e iniciar un motor, cliente, catalogo y precarga nuevos, conservando la cripta y la semilla explicita si existe. Limpiar comandos, seleccion y animaciones de la vista.
- **Pruebas:** Casos de bitacora corrupta, fallo de escritura e inicio, dialogos, limpieza real de Tkinter y reinicio integrado offline.

### 2026-10-13: animacion visual

- **Prompt textual:** "dale hazlo mas vivo pero no rompas nada del enunciado"
- **Uso:** Respiracion de sprites, entrada de sala, reaccion al dano y movimiento sutil de objetos. Temporizador exclusivamente en la vista, cancelable y desactivable; sin tiempo virtual, azar, acciones ni reglas adicionales. Se conserva MVC y el control discreto por flechas.
- **Verificacion:** 214 pruebas aprobadas; estado completo del motor intacto tras animar; comandos de las cuatro flechas comprobados. Capturas reales en 1280x800 y 1100x760 y diferencias de pixeles entre fotogramas.

### 2026-10-13: integridad de operaciones

- **Prompt textual:** "corrige esos 3 bugs porfa, siguiendo el enunciado y los principios SOLID sin cambiar la estructura del proyecto, y agrega pruebas para verificarlos"
- **Uso:** Aislar errores de precarga anticipada sin perder el registro del movimiento. Validar reloj, estadisticas, azar, objetivos y parametros de eventos antes de cargar; preparar el estado y cache aisladamente y conservar referencias publicas al confirmar la carga. Validar registros de puntaje para descartar lineas semanticamente invalidas antes del ranking. Mantener MVC, reloj virtual, binario y retroceso por deltas; las copias temporales solo corresponden a la operacion de carga.
- **Verificacion:** Seis pruebas nuevas de regresion, incluyendo fallos de catalogo, carga valida con efectos, referencias de puertas y cache, movimiento reversible y registro de replay, y ranking con registros invalidos.

### 2026-10-13: menu de inicio

- **Prompt textual:** "hazlo si basado en el diseño del juego"
- **Uso:** Menu local con personaje e iconos existentes, Jugar, Cargar partida, Replay, Puntajes y Salir. Navegacion con flechas/Enter y raton. El menu no crea el motor ni consume tiempo virtual. Cargar conserva cripta, versiones, semilla y reloj y registra la base cargada en el replay. Mantener MVC y separar menu dentro de vista.
- **Verificacion:** Cinco pruebas nuevas: teclado y acciones del menu real, cancelacion de selector, carga inicial registrada, salida sin crear partida y versiones/semilla de carga. Capturas Tkinter en 1280x800 y 1100x760.

### 2026-10-13: errores de inicio y controles de replay

- **Prompt textual:** "arreglame todos los bugs que encontraste"
- **Uso:** Capturar errores de datos/red durante acciones y presentacion del replay, conservar visible su reloj virtual y permitir cerrar su ventana con Salir sin aceptar comandos de juego. Mostrar errores de preparacion de partida y volver al menu con cliente, catalogo y precarga nuevos para reintentar. Conservar las reglas y estructura MVC.
- **Verificacion:** 229 pruebas aprobadas, incluidas cuatro regresiones nuevas para errores de replay, reloj y cierre real de Tkinter, regreso al menu y reintento con precarga nueva.

### 2026-10-13: simplificar main

- **Prompt textual:** "dale si, hazlo pero no rompas nada"
- **Uso:** Extraer coordinacion de menu y partidas a controlador/aplicacion.py y propiedad de cliente, catalogo, precarga y cierre a red/sesion.py. Mantener argumentos, modos de consola/GUI, replay, descargas, semilla, cargas, reloj y reglas. Reducir main.py de 416 a 136 lineas sin cambiar los contratos del motor o de las vistas.
- **Verificacion:** 232 pruebas aprobadas; las 229 existentes conservan sus expectativas. Tres pruebas nuevas cubren renovacion independiente, preservacion del almacen y cierre del cliente cuando falla una precarga.

### 2026-10-13: fotogramas de acciones

- **Prompt textual:** "dale haslo pero sigue el enunciado y no rompas nada"
- **Uso:** Crear una hoja local de ocho poses basada en el personaje original mediante imagegen integrado. Carrera al cambiar de sala, ataque solo tras accion aceptada y caida al perder. Reutilizar el temporizador visual cancelable; no alterar motor, costos, reloj, azar ni formatos. Conservar jugador.png y respaldo sin Pillow.
- **Verificacion:** 235 pruebas aprobadas; fotogramas y respaldo comprobados, seleccion de acciones y final de secuencias. Capturas de carrera, ataque y caida en 1280x800 y 1100x760; diferencias de pixeles entre fotogramas, motor intacto y cola de comandos vacia.

### 2026-10-13: acciones fallidas y preferencias visuales

- **Prompt textual:** "podrias arreglarlos, respetando correctamente el enunciado"
- **Uso:** Revertir por deltas el intervalo de una accion que lanza una excepcion, restaurando reloj, azar, agenda, inventario y rastro. Diferenciar deltas exclusivos de fallo para no alterar la excepcion de pergaminos en el retroceso valido. Publicar mensajes de simulacion solo al aceptar la accion. Comunicar inicio rechazado al coordinador para regresar al menu con sesion nueva. Cancelar y omitir dano flotante al desactivar Animaciones.
- **Verificacion:** 239 pruebas aprobadas. Cuatro regresiones nuevas con variantes cubren fallos de cache antes y despues de eventos enemigos, pergaminos al recoger/soltar, carga rechazada y cancelacion de efectos Tkinter.

### 2026-10-14: cumplimiento integrado

- **Herramienta/modelo:** Codex.
- **Prompt textual (solicitud):** "puedes por favor resolver esos bugs para que el proyecto cumpla con el enunciado exitosamente"
- **Contexto del prompt:** Soltar el objeto seleccionado (§4.5), escalabilidad de rastreadores (§4.7), victoria (§2.12) y separacion MVC (§6).
- **Uso:** Reutilizar el cursor y sincronizar la seleccion gratuita del GUI. Implementar traslados por posicion conocida en un arreglo propio sin indices hash ni busquedas lineales por actor; revertir el orden por deltas. Exigir evidencia de apertura con llave de la puerta atravesada, conservarla en guardado v3 y rechazar estados antiguos ambiguos. Trasladar la transaccion de cache al adaptador, sin acceso a sus detalles internos desde el motor.
- **Verificacion:** 250 pruebas aprobadas, incluidas once regresiones nuevas. Partida offline con semilla 1916 termina en victoria, vida 4 y reloj 525; replay identico al estado original. Medicion local de nueve repeticiones para traslados de 32, 512 y 4096 actores: medianas 0.959, 0.954 y 0.977 us/traslado, excluyendo preparacion, agenda, red e interfaz. No certifica el limite de 20 ms del ciclo completo.

# 2026-10-14: cuatro criptas oficiales

Herramienta: Codex. Solicitud textual del usuario:

> dale implementa las 4 que estan en la API dejalas 100% funcionales, usa el mismo personaje vestido de tigre y si vienen enemigos diferentes creales el icono

Continuacion textual:

> sigue trabajando ya cambie el modelo

Uso: verificar las cuatro criptas reales con el cargador existente, mejorar
seleccion por teclado y cancelacion, bloquear comandos durante la seleccion,
descargar el listado completo con sesiones independientes y agregar pruebas.
Los contenidos oficiales solo referencian rata gigante y guardian oseo; ambas
imagenes ya existen. No se generaron enemigos, estadisticas ni salas adicionales.
Las partidas de prueba usan equipo, curacion y la apertura real de la salida;
el replay debe reproducir el mismo estado final. No se altero el balance.

# 2026-10-14: fondo y selector visual

Herramienta: Codex e image_gen integrado. Solicitud textual:

> puedes mejorar visualmente el proyecto la pantalla de inicio ponle como un fondo de ladrillos y tambien a la hora de escoger una de las 4 criptas, mejoralo

Uso: fondo raster compartido, estilos de botones de menu, selector separado
en la capa vista, pruebas de imagen a sangre, falta de recurso, seleccion y
estado vacio. Se mantienen personaje, reloj, identificadores y reglas.

Prompt de imagen (image_gen integrado, fondo no transparente):

> Create a polished 2D fantasy game menu background, landscape 1536x1024. An old crypt wall of clearly visible rectangular weathered charcoal-gray masonry bricks with muted green patina and fine mortar joints. Straight-on elevation, subtle carved stone doorway arch on the far left behind where a character will stand, stone flagstone floor in bottom 18 percent. Readable mid-dark stone, varied gray and desaturated green, restrained warm torch illumination at far edges, no torches themselves. Center and right are a quiet uniform brick wall for cream/gold UI text overlay, no dramatic darkness, no gradients or abstract blobs. Hand-painted illustrated game environment matching a detailed fantasy character, crisp masonry texture. Full bleed background only, no text, no letters, no UI, no characters, no items, no borders.

Archivo integrado: `vista/recursos/fondo_ladrillos.png`. No reemplaza los sprites.

# 2026-10-14: auditoria y correcciones para defensa

Herramienta: Codex. Prompts textuales:

> puedes revisar si hay bugs a la hora de jugar? en las 4 criptas diferentes, fijate que el juego sea completamente funcional

> por favor corrige los fallos, ya que debo defender el proyecto a mi profesor, tambien despues de corregirlos dime si se puede ganar en las 4 criptas y fijate que tambien todo cumpla acorde al enunciado

Uso: reproducir fallos de retroceso, reinicio y rutas con espacios, corregirlos
sin snapshots para deshacer, agregar cinco pruebas de regresion, ejecutar la
suite y rutas de victoria/replay con respuestas oficiales locales y revisar
reglas, mediciones y documentacion contra el PDF del proyecto. La auditoria no
certifica los subsistemas de --bench que siguen pendientes ni una cripta futura.

# 2026-10-14: carrera y feedback visual con recursos existentes

Herramienta: Codex. Solicitud textual:

> me mejoras la animacion del proyecto para que se vea como un juego real, respetando el enunciado y usando lo que ya tenemos, no migres a pygame

Uso: reutilizar jugador_acciones.png, repetir los cuadros de carrera durante una
entrada suavizada, agregar embestida y efectos visuales temporales, conservar el
progreso al redibujar y verificar cancelacion y estado del motor sin cambios.
Todo permanece en la vista Tkinter; no se migra biblioteca ni se agrega movimiento
libre, colisiones, azar o tiempo real a la simulacion del juego.

# 2026-10-14: equipo visible y objetos recogidos

Herramienta: Codex. Solicitudes textuales:

> okay, necesito que hagas lo siguiente, que cuando el jugador recoja algun objeto o se ponga un chaleco que visualmente se vean sujetando el objeto, me entiendes?

> que me recomiendas?

> hazlo si, sigue el enunciado no rompas nada

Uso: mantener arma y coraza visibles mientras estan equipadas, sostener brevemente
el objeto recogido y volver al arma equipada. Se reutilizan PNG existentes y se
agregan anclajes visuales por pose; el modelo solo comunica tipos equipados en su
snapshot de presentacion. No se agrega tiempo, efecto, estado persistido ni HTTP.
Pruebas de soltar, retroceso, carga, seguimiento de poses, cancelacion y simulacion
intacta; capturas reales de reposo, carrera y recogida para revisar los anclajes.

# 2026-10-14: recorrido visual hasta las puertas

Herramienta: Codex. Prompt textual:

> Necesito que implementes algo. como bien ya el jugador se mueve pero permanece en el mismo lugar siempre. Puedes hacer que se mueva para meterse a las salas no que se quede ahi en el mismo lugar, osea que corra por todo lado, como un juego normal no que se quede ahi parado haciendo movimientos, para que se vea que entro a las salas y asi, no se si me entiendes?

Uso: salida hacia la puerta elegida y entrada visual en la siguiente sala,
trayectos con coordenadas cambiantes, orientacion de la carrera, sombra y equipo
vinculados, cancelacion de callbacks y pruebas de cuatro direcciones. Sin migrar
Tkinter, agregar libre movimiento, colisiones, acciones o modificar tiempo virtual.

# 2026-10-15: carrera y puerta de paso

Herramienta: Codex. Prompt textual:

> Okay me gusta la idea que estas haciendo pero visualmente siento que corre raro no se si lo puedes mejorar y no crees que esa puerta siempre ahi se ve fea? no es mejor que el jugador apenas se acerque a la sala se abra la puerta y cuando se pase a otra sala se cierre

Uso: alinear pies de fotogramas, mantener escala y velocidad, evitar destello al
entrar y mostrar hojas decorativas solo durante el paso. Pruebas de apertura,
cierre, limpieza, posicion inicial y simulacion intacta. Las cerraduras siguen
dependiendo del motor, sin apertura gratuita ni cambios al reloj virtual.

# 2026-10-15: acelerar recorrido y cierre

Herramienta: Codex. Prompt textual:

> dale hazlo y que la puerta se cierre mas rapido

Uso: reducir a la mitad salida, entrada y cadencia de carrera, sincronizar la
apertura y cerrar las hojas en 80 ms. Mantener el callback visual de 20 ms y
las reglas del motor. Actualizar pruebas de recorrido, cierre y estado intacto.

# 2026-10-15: corregir transiciones y primer recorrido

Herramienta: Codex. Prompt textual:

> arregla esos bugs y tambien visualmente vi que al principio es lento, la primera vez entrando a la primera sala, revisa que el jugador pase de sala en sala bien, sin ningun problema o bug, que el juego quede 100% funcional

Uso: bloquear paginacion durante salida, restaurar posicion y pose inmediatamente
al redimensionar, precargar las orientaciones de carrera en la sala inicial y
reutilizar la hoja decodificada. Pruebas de resize, paginacion, movimientos
consecutivos, precarga, cuatro direcciones y suite con las cuatro criptas.
La verificacion no constituye una garantia de ausencia total de defectos.

# 2026-10-15: revision integral y cuatro correcciones

Herramienta: Codex. Prompts textuales:

> puedes revisar paso a paso todo el proyecto para ver si tiene algun bug

Uso: revision por subsistemas, contraste con el enunciado, pruebas existentes y
reproducciones de fallos en puertas, cargas inconsistentes, versiones y cierre.

> corrige esos 4 bugs porfa, siguiendo el enunciado y los principios SOLID sin cambiar la estructura del proyecto, y agrega pruebas para verificarlos

Uso: rechazar aperturas redundantes sin costo, conservar la acreditacion con
llave de la salida, validar unicidad y tipo de turnos y cierres al cargar,
propagar versiones solicitadas y reportar errores finales sin ocultar el error
original. Nueve pruebas focalizadas y suite completa, sin cambiar la estructura MVC.

# 2026-10-15: cierre del selector y ayuda al reiniciar

Herramienta: Codex. Instruccion recibida mediante delegacion autorizada, textual:

> La usuaria ahora autoriza explícitamente arreglar los dos fallos gráficos que acabas de reproducir. La restricción anterior de no modificar archivos queda levantada para estas correcciones: (1) cerrar la ventana principal con el selector de cripta abierto provoca que se reconstruya el menú sobre la ventana destruida; (2) reiniciar después de perder hace que la ayuda aparezca automáticamente porque no se restablece el estado de omisión. Implementa ambas correcciones en el proyecto real que ya inspeccionaste, respeta las instrucciones aplicables y verifica los dos escenarios con pruebas apropiadas. Mantén el alcance en estos dos fallos; no corrijas los hallazgos de consola o guardado corrupto. Devuelve un resumen breve en español de lo cambiado y de la validación, con cualquier limitación real.

Uso: salida controlada al cerrar durante la seleccion de cripta y restauracion de
la omision de ayuda automatica en cada reinicio. Dos regresiones con Tkinter real;
el boton de ayuda permanece operativo. Sin cambios de reglas ni de formato binario.

# 2026-10-15: selector integrado en la ventana principal

Herramienta: Codex. Solicitud de voz textual:

> Primero, que cuando la ventana que muestra las cuatro criptas, al fondo muestra como el juego vacío, preferiría mejor que cuando uno le de jugar, en la misma ventana salgan las cuatro criptas sin nada de fondo y ya cuando selecciona el usuario la cripta que se meta de una vez en el juego

Uso: sustituir la ventana separada del selector por una pantalla que cubre la
ventana principal; mantener las cuatro opciones, datos, Enter, doble clic, Volver
y Escape. Actualizar pruebas del selector sin cambiar la creacion del motor.

# 2026-10-15: escala del jugador y piedra calida

Herramienta: Codex. Solicitud de voz textual:

> Quisiera que el jugador, primero que no sea tan grande, siento que el jugador es muy grande, que sea un poquito más pequeño. También, el fondo de la sala se está feo. Quiero como algo más rocoso como, como café, como está en el inicio, algo así más encendido, no sé si podrías hacerlo por favor

Uso: reducir la escala del jugador al 82%, reutilizar la textura local de piedra
con luz calida y ajustar pared/suelo. Mantener anclajes, controles y reglas;
agregar pruebas de recursos, escala y simulacion intacta y revisar dos ventanas.

# 2026-10-15: efectos de sonido basicos

Herramienta: Codex. Solicitudes de voz textuales:

> Ay sí, podrías implementarlo

> , porfa. Así básico

Uso: efectos breves sintetizados para acciones aceptadas y victoria/derrota,
reproduccion asincrona con winsound, control de silencio y limpieza al cerrar.
Sin musica continua, dependencias nuevas ni cambios al reloj. Seis pruebas de
audio simulado, errores, silencio, recursos temporales e independencia del motor.

# 2026-10-15: melodia de inicio

Herramienta: Codex. Prompt textual:

> podrias ponerle como sonido de juego al inicio tambien, no solo en los movimientos

Uso: melodia corta sintetizada al mostrar el menu, asincrona y sujeta al control
de silencio. No se dispara desde el redibujado ni modifica el reloj virtual.
Pruebas del WAV, omision al silenciar y llamada unica al mostrar el menu.

# 2026-10-15: coherencia ilustrada y sonido tenebroso

Herramienta: Codex e imagegen. Prompts textuales del usuario:

> el sonido no puede ser mas de juego, como tenebroso, tomando de ejemplo plantas vs zombies o algo asi? obviamente no hagas el mismo sonido de ese juego pero me parece raro y visualmente el fondo y los enemigos y el jugador no encajan se ve raro

> dale hazlo respetando el enunciado

> deja el personaje de tigre cuidado lo desapareces

Uso: conservar tigre y animaciones originales; generar fondo pintado, guardian
ilustrado y hoja de objetos con luz y contornos comunes, dejando los anteriores
como respaldo. Se descarto una variante de hoja con halos; solo se integran
recortes verificados. Componer un motivo original en modo menor con campanas,
graves, eco y golpes de textura, sin copiar musica ni utilizar azar del modelo.
Pruebas de transparencia, seleccion de recursos, respaldo, audio y cuatro criptas.

# 2026-10-16: resultados y chaleco ajustado

Herramienta: Codex. Prompt textual del usuario:

> esta ventana de victoria o la de perdida visualmente esta muy basica hazla mejor y tambien note que cuando se equipa el chaleco no se lo pone bien si no como por encima

Uso: pantalla de resultado dentro de la ventana, con recursos locales existentes,
resumen sin cambios y reinicio de derrota integrado en el flujo actual. Ajuste
del chaleco al torso por pose mediante composicion visual en memoria, sin cambiar
los PNG del tigre, las reglas, las estadisticas ni las estructuras del modelo.
Pruebas de teclado, cierre, replay, reinicio, alfa, reflejo, caches y simulacion.

Solicitud posterior:

> y las estadisticas que sean un boton opcional que se pueda desplegar si el usuario quiere

Uso: ocultar el resumen inicialmente y agregar Ver/Ocultar estadisticas en la
misma pantalla. Conservar teclado, reinicio y resultado al desplegar, ocultar o
redimensionar; comprobar que no se encolan comandos de juego.

Solicitud posterior:

> el chaleco se le pone pequeño y tambien quiero que mejores la tabla que pregunta el nombre para puntajes se ve basica

Uso: ampliar la ropa sobre el torso en reposo y animacion, sin cambiar los PNG
originales ni las estadisticas. Entrada de nombre estilizada y centrada que
conserva el contrato anterior de confirmacion, cancelacion y nombre vacio.
Pruebas de cobertura, teclado, foco modal, cierre y ausencia de acciones del motor.

# 2026-10-16: sonido de botones y consulta de replay

Herramienta: Codex. Solicitudes de voz del usuario:

> ¿Podrías, por favor, ponerle sonido a los botones del juego cuando uno le da iniciar partida y cosas así

> No cambies código del replay, solo cambia el sonido

Uso: efecto corto asincrono al activar botones, conservando silencio y comandos.
Consulta de la seccion 4.11 del enunciado: exige reproducir el archivo indicado,
sin exigir que sea exclusivamente el ultimo ni un historial de cinco partidas.
No se modifica el flujo ni la persistencia del replay.

# 2026-10-16: agarre, bebidas y proporciones de enemigos

Herramientas: Codex e imagegen integrado. Solicitudes de voz del usuario:

> ¿Podrías mejorar el juego visualmente? Lo que quiero es como que cuando el jugador tenga una daga, la agarre bien con la mano, con las manos, o cosas así, que se vea bien o cuando se tome la poción se vea que se la está tomando. También, ¿no crees que las enemigos están muy grandes, como la rata? Quiero como que se vea más integrado, más bonito, es que aún siento que está un poco falso. No sé qué opinas

> Okay, perfecto, deja el juego visualmente muy bonito para que el usuario quede contento con el resultado

> Lo mismo con los antídotos también y así

Uso: componer la daga desde la palma y delante de la silueta, con dedos por
delante del mango; gesto local de beber para pocion y antidoto aceptados; rata
mas pequena, plano de apoyo y sombras consistentes. Conservar motor, estadisticas,
reloj y formato de replay. Las nuevas pruebas comparan simulacion tras la animacion.

Prompt inicial de imagegen, referencia jugador.png, transparencia real:

Create a production game sprite sheet DERIVED FROM the reference tiger-costumed human player. Keep exactly his recognizable orange tiger hood with ears, face, tiger-striped suit, cream belly, brown belt, tail, claw slippers, and dark ink/painterly illustration style. This is an ADDITIONAL potion drinking animation, not replacement character design. Output a wide transparent RGBA canvas with THREE equal-sized vertical cells in ONE horizontal row, no grid lines, no labels, no scenery, no shadow, no background pixels. In each cell show the full same character head to feet, same upright standing pose facing three-quarter right, identical scale, feet aligned on same baseline, same position centered within each third, generous 8% transparent padding on every edge, no overlap between cells. Left cell: right hand firmly grasps small rounded glass potion bottle with RED liquid at chest level, elbow bent. Middle cell: right hand lifts the SAME bottle to his lips, head slightly back, bottle tipped and he is visibly drinking; fingers wrap around bottle, elbow raised naturally. Right cell: lowers the same nearly-empty bottle back to chest level after drinking. LEFT hand stays down by his side in ALL cells, NO daggers, NO vest, no weapons, no extra props. Keep head, torso, feet and tail practically identical across the three cells, only change right forearm and bottle/head tilt. Bottle must be small relative to his head. Detailed hand-drawn fantasy game art coherent with original reference, NOT pixel art, no cartoon redesign. Clean TRUE transparency, crisp silhouette, no dark halos or glows.

Prompt de correccion con referencia a la primera hoja:

Fix this THREE-cell potion-drinking sprite sheet. KEEP the middle cell character exactly unchanged. It defines the pose and anatomy for all three frames. The problem: first and third cells currently hold the bottle in the OPPOSITE hand to the middle cell. Change ONLY the arm positions in FIRST and THIRD cells to match the middle cell's anatomical hands: the arm on the RIGHT SIDE OF THE IMAGE holds the bottle at upper chest height, elbow bent. The arm on the LEFT SIDE OF THE IMAGE hangs down relaxed just like the middle frame. In all three cells the potion must stay in the SAME right-side-of-image paw. Keep the character's scale, head, feet, torso, tail, clothing and face identical to the existing middle cell in each of the three cells. Same three-quarter-right tiger-costumed HUMAN, unchanged original identity. ONE row, THREE equal-width cells, transparent RGBA, no scenery, no text, no grid. Separate cells with clear transparent gutters and ensure every cell's tail and feet stay strictly inside its own third with 5% margin. Frame1 bottle full red at chest, Frame2 unchanged drinking at lips, Frame3 bottle nearly empty at chest. Crucial: left-side arm hangs down in ALL THREE frames, right-side arm holds potion in ALL THREE frames. No vest, no dagger. Keep painterly ink fantasy art, no halo.

Seleccion: la correccion no resolvio completamente el cambio de brazo lateral.
Solo se utiliza la celda central verificada; las otras dos no se animan.
Recurso final conservado en vista/recursos/jugador_beber.png, sin alterar los
PNG originales del personaje ni sus ocho poses anteriores.

# 2026-10-16: puno cerrado y verificacion de muerte

Herramienta: Codex. Prompt textual del usuario:

> necesito que integres bien la daga en la mano se la pone por encima, no cierrra el puño, tambien fijate si los enemigos se mueren correctamente o hay algun bug

Uso: sustituir las manos abiertas por el puno ya dibujado en la carrera original,
en lugar de conservar sus garras por encima del mango. Ajustar reposo, ataque y
caida sin editar los PNG; mantener el agarre al recoger otro objeto. Revisar la
muerte sin modificar reglas del motor: cancelacion de turno, ausencia de ataques
y regeneracion, botin unico utilizable, guardado/carga, retroceso y retirada visual.
Agregar regresiones para esos casos y conservar el motor al no reproducir un
fallo funcional de muerte en los escenarios comprobados.

# 2026-10-16: trampa letal y salida Sur

Herramienta: Codex. Prompt textual del usuario:

> arregla lo de las trampas y este bug mira que la rata esta como encima donde dice sur

Uso: no aplicar veneno despues de que el dano inicial de una trampa mate al
jugador; conservar su desarmado y rearme. Reservar un carril para el control Sur
cuando hay enemigos, sin tapar salud u objetos. Pruebas de veneno previo,
antidoto, muerte con varias trampas y salida visible/pulsable con distintas
cantidades de enemigos en tres tamanos de ventana. No se modifica el catalogo.

# 2026-10-16: animaciones de trampas y antorcha en mano

Herramienta: Codex. Prompt textual del usuario:

> puedes hacerle animaciones a todas las trampas y tambien que cuando el jugador use la antorcha la agarre con la mano como la daga

Uso: representar cada trampa con paginacion y animar sus activaciones reales,
incluido el caso de rearme antes del siguiente turno. Comunicar los identificadores
en ResultadoAccion al controlador y al replay, sin modificar tiempos ni dano.
Integrar la antorcha del catalogo en el puno izquierdo usando los recursos
existentes; conservar la daga derecha y todas las poses. La duracion visual
depende del efecto del modelo. Agregar pruebas de activacion, limpieza,
paginacion, silencio de animaciones, apagado, carga, retroceso y reflejo de poses.

# 2026-10-16: correcciones y benchmark para defensa

Herramienta: Codex. Prompt textual del usuario:

> corrige todos los bugs incluido el bench y yo hare la documentacion, deja esos bugs arreglados respetando el enunciado y pon mas decisiones, deja el proyecto funcional

Uso: corregir cierre de entrada de consola y verificacion de identidad/rango
del indice binario; completar mediciones de agenda, inventario, historial,
ordenamientos, guardado binario/JSON y ciclos de eventos sin vista ni red.
Agregar regresiones y notas tecnicas reproducibles para que el equipo prepare
la documentacion final; conservar MVC, reglas, recursos y partidas v3 validas.

# 2026-10-16: verificaciones de entrega

Herramienta: Codex. Prompt textual del usuario:

> puedes hacer esas verificaciones que faltan y corregir cualquier fallo que encuentres respetando el enunciado, sin cambiar la estructura del proyecto? yo me encargo de la documentacion

Uso: instalar dependencias en un entorno virtual limpio, consultar API real con
cache fria y caliente en las cuatro criptas, verificar paquete recien descargado,
probar contenido sintetico de mayor escala y repetir mediciones de forma aislada.
Agregar regresiones y corregir la interrupcion al pedir el nombre del puntaje.
La prueba de API requiere habilitacion explicita para no hacer HTTP en la suite
normal. No se sustituye la documentacion final que preparara el equipo.

# 2026-10-16: separacion de llama y antebrazo

Herramienta: Codex. Solicitud recibida por delegacion autorizada de la usuaria:

> La llama se superpone con el antebrazo, y el mango no se distingue entre los dedos, pareciendo mano y antorcha fusionadas. Quiere que la mano agarre claramente el mango y la llama quede alejada del brazo.

Uso: ajustar el giro de la capa alrededor del mango en reposo, carrera, ataque,
caida y bebida; conservar palma, puno y PNG originales. Revisar capturas y agregar
una regresion geometrica de anclaje y orientacion, sin cambios del motor.

# 2026-10-17: fluidez sin cambios visuales

Herramienta: Codex. Prompt textual del usuario:

> puedes optimizarlo pero no cambies nada, me encanta como esta el proyecto ahorita, esta perfecto, solo quiero que no sea lento nada ams

Uso: reutilizar composiciones entre orientaciones, evitar preparaciones de ropa
reemplazadas inmediatamente y decodificaciones repetidas. Agregar cache temporal
PNG sin perdida, acotada, con invalidacion y recuperacion ante fallos. Procesar
entrada con eventos nativos sin cambiar pasos ni tiempos configurados de las
animaciones. Verificar pixeles, controles, visualizacion y regresiones del juego.

# 2026-10-17: contenido de criptas nuevas e icono neutro

Herramienta: Codex. Prompt textual del usuario:

> y podrias modificar el juego para que acepte una cripta nueva? es que mi profesor va a hacer eso, colocar una nueva cripta con diferentes enemigos, salas.. para ver si el proyecto aguanta.. No se pero puedes ponerle un signo de pregunta o una imagen neutra al juego por si mi profesor coloca alguna cosa desconocida o no se que opinas

Uso: verificar que selector, motor y catalogo acepten identificadores nuevos.
Unificar respaldo visual con signo de pregunta en escena, inventario, equipo y
trampas sin cambiar los datos ni las reglas. Agregar pruebas con siete criptas,
tipos nuevos, PNG ausente/danado, ausencia de Pillow y reutilizacion acotada.

# 2026-10-17: puno de antorcha y equipo desconocido

Herramienta: Codex. Solicitud del usuario por voz: revisar el respaldo con signo
de pregunta en los escenarios de contenido nuevo y corregir el puno de la
antorcha como el de la daga, manteniendo ambos objetos en manos distintas.

Uso: ampliar las pruebas de equipo nuevo con antorcha y poses, reemplazar el
borrado rectangular de la mano por una mascara localizada, alinear el mango
con la palma y comprobar las composiciones reflejadas sin cambiar el modelo.

# 2026-10-17: presentacion de puntajes

Herramienta: Codex. Solicitud del usuario por voz: mejorar la ventana blanca
que aparece al pulsar Puntajes, para que combine con el juego.

Uso: sustituir el aviso estandar por una tabla modal oscura con el fondo de
piedra existente, datos reales, scroll, estado vacio y cierre por teclado.
No cambiar el ranking ni los archivos de resultados. Agregar pruebas de
presentacion y del consumo de pociones y combate con identificadores nuevos.

# 2026-10-17: replay directo

Herramienta: Codex. Solicitud por voz: pulsar Replay sin buscar el archivo y
mostrar arriba que se reproduce la ultima partida.

Uso: abrir la bitacora automatica desde inicio y partida, preservar rutas
explicitas por consola y la validacion existente. Identificar la grabacion
predeterminada en el encabezado del reproductor. Probar ausencia de archivo,
grabacion incompleta, ruta explicita y ausencia de cambios en el modelo.

# 2026-10-17: optimizacion medida del inicio

Herramienta: Codex. Prompts textuales del usuario por voz:

> ¿Y cómo puedo mejorar el inicio? ¿O no se puede? Es que mi profesor también valora mucho el rendimiento

> Ok, te doy permiso a todo

Uso: perfilar menu y primera sala, comparar cargas de Tkinter y ampliar la
cache visual sin perdida a fondos e imagenes estaticas. Probar igualdad de
pixeles, invalidacion por cambios de PNG y respaldo para IDs nuevos. Cronometrar
apertura fria y preparada sin modificar reglas, imagenes originales ni el PDF.

# 2026-10-18: primer recorrido entre salas

Herramienta: Codex. Solicitud del usuario:

> sigue un poco lento

Uso: preparar los fotogramas de carrera de ambas orientaciones antes de pedir
comandos, usando equipo y antorcha actuales. Evitar convertir imagenes durante
el primer recorrido, sin cambiar reglas, pasos ni duracion de la animacion.
Comparacion local de tres muestras por variante a 1280x850: mediana del inicio
visual del primer movimiento de 244.22 a 25.43 ms sin equipo y de 192.77 a
20.59 ms con coraza, daga y antorcha. Dibujo de llegada cercano a 3 ms. Son salas
sinteticas, sin HTTP; el costo inicial se adelanta a la preparacion del juego.
Verificacion: 32 pruebas de transiciones, inicio, cadencia, gestos y vista pasan.

