# Cripta: interfaz nativa

Aplicacion de escritorio Tkinter, en espanol. La escena permite decidir una accion
por vez; la simulacion usa tiempo virtual y los efectos visuales usan callbacks de
Tkinter. El aspecto nunca cambia estadisticas, costos, semillas ni reglas.

## Rendimiento visual

Las dos orientaciones reutilizan una composicion de las ocho poses. El jugador
y el fondo originales se decodifican una sola vez por vista. Con equipo completo
no se genera primero otra variante intermedia del chaleco.
CacheVisual conserva hasta 128 PNG regenerables en la carpeta temporal
`cripta-visuales`, con secuencias agrupadas y alfa sin perdida. La firma incluye
ruta, tamano y fecha de los recursos y el codigo de composicion; al cambiar esos
datos se regeneran. Si falta permiso o hay corrupcion se compone normalmente.
Esta cache es de presentacion, no sustituye ni altera la cache de catalogo.
La espera de comandos procesa eventos nativos de Tk sin sondeo con sleep;
se conservan los 20 ms y todos los pasos de animacion existentes.
El temporizador programa el siguiente paso respecto a su instante previsto,
compensando el retraso de despacho y el costo del dibujo. Una pausa mayor que
un periodo reinicia la cadencia sin rafagas de callbacks ni saltos de pasos.

Las combinaciones de coraza, daga y antorcha, y las poses de pocion y antidoto,
se distribuyen como PNG sin perdida en `vista/recursos/composiciones`. Se generan
con `python -m utilidades.preparar_visuales`, conservando exactamente los pixeles
del compositor. La firma usa contenido y codigo, independiente de carpeta,
fechas y finales LF/CRLF. Un paquete ausente, corrupto o incompatible usa el
compositor original. Hay versiones nativas para cualquier tamano y copias a las
alturas habituales de 122, 165, 193 y 196 px. El paquete suma aproximadamente
51 MB de disco y no se carga entero en memoria.

Equipar o usar una antorcha prepara solo el reposo. No se anticipan ambas
orientaciones de las ocho poses al iniciar o cambiar equipo. Atacar y caer
cargan dos poses; correr carga cuatro, conservando sus duraciones y anclajes.
Las poses de beber se conservan tambien en la cache visual de disco.
Las caches retienen como maximo cuatro secuencias completas, ocho secuencias
de acciones, cuatro reposos con equipo y cuatro bebidas. Los tipos desconocidos
siguen usando los mismos respaldos; nada de esto modifica fichas ni estadisticas.

## Identidad

- Imagen del jugador con traje de tigre y rata proporcionadas por el usuario.
- Piedra verde grisacea, tinta oscura, oro para objetos, menta para vida y puertas
  abiertas, rojo para dano, azul para estadisticas y violeta para efectos.
- Los colores compartidos pertenecen a `vista/tema.py`.
- Georgia para titulos; Segoe UI para lectura; Consolas para tiempo virtual.
- Los personajes son el foco. La escena ocupa el espacio disponible y el inventario
  mantiene un ancho estable, con desplazamiento propio.
- El jugador se muestra al 70% de la altura anterior, tanto en reposo como en
  carrera, ataque y caida; el equipo y la sombra conservan sus anclajes.
- Sala, inicio y selector comparten `fondo_cripta_ilustrado.png`: piedra pintada,
  contornos de tinta, luz ambar izquierda y sombras carbon; no contiene puertas.
  La fuente separa pared y suelo al 58%; la sala reparte ambos planos al 50%
  para mantener mas suelo visible.
  El fondo anterior y la mamposteria quedan como respaldos locales.
- El tigre y su hoja de animacion originales permanecen intactos. La rata conserva
  su ilustracion, orientada hacia el jugador. `guardian_ilustrado.png` sustituye
  la presentacion realista del guardian. Objetos y trampa proceden de recortes
  verificados de `objetos_ilustrados.png`; sus PNG previos quedan como respaldo.
  El boton Jugar usa oro; las estadisticas conservan sus colores funcionales.
- Una entidad sin arte local usa un signo de pregunta neutro compartido por
  tamano, dibujado con Tk sin depender de Pillow. Escena, trampas, equipo e
  inventario mantienen nombre, instancia y datos del catalogo. La falta de PNG
  no define reglas ni cambia el tipo. Las imagenes conocidas siguen iguales;
  se recuerdan hasta 64 nombres ausentes para no repetir acceso a disco.
- El selector vive en `vista/selector_cripta.py`, usa una lista nativa accesible
  por teclado y muestra por separado salas y dificultad de la seleccion.
  Ocupa la ventana principal completa, sin ventana modal ni tablero visible
  detras. Enter o doble clic confirma; Volver y Escape regresan al inicio.
  No altera el reloj, la API, el modelo ni los identificadores de las criptas.

## Comportamiento

- Al confirmar Jugar o Cargar, el inicio conserva su fondo, tigre y titulo con
  el texto Cargando y oculta sus botones. Permanece debajo del selector y durante
  las consultas; se retira despues de dibujar el primer estado completo. Nunca
  se expone el tablero vacio entre inicio, selector y partida. Volver o un error
  permiten mostrar otro menu; la capa anterior se libera sin acumular paneles.

- Cada instancia conserva su identificador aunque comparta imagen con otra.
- Enemigos sin imagen local tienen una representacion generica consistente.
- Imagenes en `vista/recursos/`: `jugador.png` y `<tipo_catalogo>.png`.
- `RecursosGraficos` solo resuelve archivos locales; no solicita datos al API.
- `EscenaCripta` solo dibuja snapshots y conecta acciones a la vista.
- Se muestran trampas, salud, equipo, efectos, costos y proximos sucesos observables.
- El inventario muestra el efecto del objeto seleccionado y deshabilita acciones
  incompatibles. Seleccionar, ordenar y cambiar de pagina no consume tiempo.
- Los mensajes del motor llegan al buffer circular existente de 20 entradas.
- Dano flotante y escalado de imagenes pertenecen exclusivamente a la vista.
- Sonidos breves de acciones aceptadas y fin de partida pertenecen a la vista.
  `Sonidos` encapsula winsound asincrono, WAV locales sintetizados y limpieza;
  no usa eventos del motor ni azar. La casilla Sonido permite silenciar y se
  conserva entre partidas. Sin backend o dispositivo, la partida sigue sin audio.
  Motivo de inicio original en modo menor, campanas inarmonicas, graves y eco
  finito. Pasos y puertas usan ruido filtrado y golpes amortiguados, no tonos
  puros. La sintesis no utiliza random ni grabaciones o melodias de otros juegos.
  Los botones de menus, selector, partida y dialogos emiten una campana breve
  al activar su comando, tambien mediante teclado. No suenan al pasar el raton
  ni estando deshabilitados. Se conserva el comando original y el control Sonido;
  enlazar dos veces un boton no duplica su efecto ni su accion.
- Se verifican 1280x800 y 1100x760, incluyendo escenas pobladas, equipo y replay.
- `FinPartida` reemplaza el aviso nativo de resultado por una pantalla completa
  con piedra, tigre, resultado y resumen real. No contiene un segundo motor.
  Derrota ofrece Jugar de nuevo y Terminar; Escape equivale a Terminar. La vista
  conserva esa respuesta para la consulta existente del controlador, sin repetir
  la pregunta. En replay solo permite cerrar la reproduccion. La capa bloquea
  comandos, limpia la cola y restaura foco/enlaces al cerrarse.
  Las estadisticas estan ocultas inicialmente; Ver/Ocultar estadisticas despliega
  el resumen en la misma pantalla y desplaza los botones principales sin taparlos.
  El despliegue conserva su estado al redimensionar y no crea acciones del motor.
- `NombrePuntaje` sustituye la entrada nativa del nombre por un dialogo centrado
  con piedra, titulo Georgia, campo de alto contraste y botones del menu.
  Enter confirma; Escape, Cancelar y la X devuelven texto vacio como antes
  (el controlador conserva Jugador como nombre predeterminado). El grab es local,
  se libera al cerrar y ninguna tecla pasa a la cola de acciones del juego.

## Movimiento visual

- El menu de inicio usa los mismos colores, tipografia y recursos locales. Permite
  Jugar, Cargar partida, Replay, Puntajes y Salir con raton, flechas y Enter.
  Es una capa de vista temporal sin motor; sus callbacks se cancelan al salir.
  El indicador t=0 corresponde a una partida nueva, no a una simulacion activa.
- Jugar abre un selector de criptas con nombre, salas y dificultad recibidos de
  la API o del paquete offline. Enter confirma y Escape/Volver cancelan. Ninguna
  tecla de seleccion entra en la cola de acciones. Las cuatro criptas conservan
  al jugador y los recursos compartidos; no se clonan vistas ni motores por nivel.

- AnimacionEscena usa un solo callback de Tkinter cada 20 ms, sin acceder al modelo
  ni al azar. Respiracion de 1.5 px, carrera de 640 ms con dos ciclos de cuatro
  poses (40 ms por cuadro de carrera), entrada direccional y reaccion al dano.
  El ataque combina poses y una embestida de 24 px; polvo y trazo de ataque son
  temporales y se eliminan al terminar o cancelar. No son objetos ni colisiones.
  Redimensionar conserva el progreso visual; ninguna animacion bloquea comandos.
- Solo se mueven sprites: nombres, salud, controles y zonas de clic permanecen
  estables. Los objetos conservan su etiqueta de recogida.
- El snapshot presenta los tipos de arma y armadura realmente equipadas.
  `equipo_visual.py` ancla sus imagenes al torso y a la mano del jugador, usando
  coordenadas artisticas de las poses existentes. Siguen carrera, ataque y dano.
  Al recoger un objeto se sostiene unos 45 pasos visuales; mientras tanto se
  oculta el arma dibujada, no su efecto real. Soltar, cargar, retroceder y reiniciar
  actualizan la apariencia desde el modelo. No se cambia el guardado ni la API.
  Con Animaciones desactivadas se conserva el equipo estatico y se omite el gesto.
- La coraza de cuero equipada usa su PNG como ropa, no el icono de inventario:
  se ajusta al torso en reposo y en los ocho fotogramas antes de reducir/reflejar
  la imagen. Conserva el alfa del tigre, su cabeza, brazos y piernas. El antebrazo
  adelantado queda delante de la ropa en el segundo ataque. Las variantes tienen
  caches acotadas; los PNG originales no se sobrescriben. Sin Pillow o sin el
  recurso se conserva la presentacion anterior como respaldo.
  La ropa en reposo cubre un 25% del ancho del recurso del tigre, hasta la cintura;
  las poses amplian un 20% el ancho y un 8% el largo de sus anclajes de torso.
- La daga conocida se compone con el sprite antes de reflejarlo: mango en la
  palma y orientacion propia por pose. La mano abierta se retira, incluidas sus
  garras, y se sustituye por el puno cerrado recortado de la carrera original;
  no se simula el cierre con una mascara circular sobre la mano abierta.
  El puno se gira hacia la muneca y queda delante del mango. En carrera se
  conservan los dedos cerrados de los propios cuadros. Las armas desconocidas
  conservan su imagen/anclaje de respaldo. El equipo prepara ambas orientaciones
  al cambiar para evitar trabajo extra al comenzar la siguiente carrera.
  Al recoger, la daga integrada permanece en el puno derecho y el objeto se
  sostiene brevemente en la izquierda, sin regresar al anclaje antiguo al acabar.
- Usar una pocion o antidoto aceptado transmite solo su instancia a la vista.
  La vista resuelve el ItemVista anterior, sin consultar o mutar el inventario.
  Una pose adicional de beber usa la animacion existente durante 32 pasos visuales;
  el antidoto colorea unicamente el liquido turquesa. Se mantiene la coraza y se
  oculta la daga durante el sorbo. No agrega acciones, consumos ni tiempo virtual;
  acciones rechazadas, otras clases de objetos y movimiento desactivado no beben.
  Replay recibe el mismo contexto visual sin cambiar archivos, reglas o selector.
- Rata: limite visual al 54% de la altura base del enemigo. En salas de hasta
  cuatro enemigos comparten el plano de apoyo del jugador; la sombra depende
  de la anchura real del recurso, no de la celda entera. Los paneles poblados
  conservan dos filas y paginacion. Tipos desconocidos mantienen el respaldo.
- Sur usa el carril izquierdo mientras haya enemigos, fuera de sus celdas y
  barras de vida; sin enemigos permanece centrado. Deja separacion respecto
  a la salud del jugador y a la franja de objetos. La posicion del control
  no cambia la direccion, el costo ni la animacion de atravesar una puerta.
- La casilla Animaciones permite desactivar el movimiento. Cambiar de sala,
  redimensionar, reiniciar o cerrar cancela el callback y libera sus referencias.
- No hay movimiento libre ni ataques automaticos. Las flechas siguen siendo
  acciones discretas entre salas; el reloj virtual solo pertenece al motor.
- Cada movimiento aceptado puede mostrar salida y entrada: 10 pasos visuales
  hasta la puerta de origen, cambio de escena y carrera desde el lado opuesto
  hasta un punto de llegada dependiente de la direccion. Se mantiene la escala
  durante el recorrido; hacia la izquierda se invierte la carrera.
  Sombra, equipo y etiqueta acompanian al jugador. No hay posiciones de combate,
  distancias, colisiones ni tiempo adicional en el modelo.
  La entrada dura 16 pasos: salida y entrada suman unos 520 ms con callbacks
  de 20 ms. La puerta cierra en 4 pasos (80 ms) y se retira al paso 12 de entrada.
- Los fotogramas alinean los pies y el desplazamiento mantiene velocidad uniforme,
  con oscilacion leve. La entrada comienza en la puerta, sin destello en el destino.
  `PuertaVisual` aparece al acercarse, abre sus hojas y cierra tras la entrada;
  luego se retira. Es decorativa: no abre cerraduras ni modifica el cierre logico.
- `TransicionSalas` solo usa snapshots y el callback existente de AnimacionEscena.
  Restaurar un paso actualiza de inmediato posicion, fotograma, equipo y puerta,
  sin avanzar el reloj visual ni duplicar callbacks. La paginacion se ignora
  durante la salida para no dejar visible un snapshot de la sala anterior.
  La sala inicial prepara ambas orientaciones de carrera; la hoja RGBA se
  decodifica una vez por vista y se reutiliza al cambiar el tamano.
  Cargar, retroceder, una nueva accion o desactivar movimiento cancelan el recorrido
  anterior; redimensionar conserva su avance. Durante la salida no se aceptan clics
  sobre actores de la escena vieja; el teclado y los controles generales siguen
  disponibles. Con movimiento desactivado se muestra directamente la sala destino.
- El jugador tiene una hoja 4x2 de fotogramas: carrera (0-3), ataque (4-5),
  caida (6-7). El controlador anuncia solo acciones aceptadas; el replay usa
  el mismo aviso. No se infiere un ataque a partir de dano automatico.
- Las secuencias duran cientos de milisegundos reales sin bloquear comandos;
  un estado nuevo las reemplaza. La caida conserva la ultima pose. Sin Pillow,
  sin la hoja o con Animaciones desactivadas se conserva el dibujo original.
- Proporcion de sala: el tigre conserva sus recursos y equipo, con escala .70
  y altura maxima de 196 px. Los controles visuales comparten la fila de acciones;
  el registro muestra tres lineas con desplazamiento para liberar altura de escena.
  El fondo dedica la mitad de su altura al suelo, sin cambiar reglas ni geometria
  logica. Verificado en ventanas de 1100x760 y 1280x850.
- Las trampas tienen indicadores individuales y paginacion de ocho elementos.
  ResultadoAccion comunica sus activaciones reales a la vista y al replay;
  nunca se deducen del estado armado, que puede haber cambiado por el rearme.
  Dardos muestra proyectiles y las fichas desconocidas un pulso generico.
  Los efectos usan el callback de AnimacionEscena y se limpian al terminar,
  cargar o desactivar animaciones, sin ejecutar efectos del modelo.
- La antorcha activa se integra en el puno izquierdo del tigre, dejando la daga
  en el derecho. Reposo, carrera, ataque, caida y bebida conservan el agarre;
  el indicador de efecto del modelo determina cuando aparece y se apaga.
  Se componen los recursos existentes sin modificar los PNG originales.
  El mango es el pivote de giro; la llama se inclina hacia fuera del antebrazo,
  con direccion inversa al cruzar el brazo en ataque o durante la caida.
  El puno cerrado ocluye el mango y la limpieza de las garras respeta la cola:
  no borrar rectangulos alrededor de la mano. La antorcha sigue a la izquierda
  y la daga a la derecha, incluso al equiparlas simultaneamente.
- Puntajes usa una ventana modal propia de solo lectura, encabezado de piedra,
  tabla oscura con scroll en ambos ejes y estados de victoria/derrota en color.
  Conserva el ranking recibido y los IDs/versiones reales de cualquier cripta.
  Cerrar o Escape devuelve el foco sin encolar acciones ni alterar la partida.
- Replay en inicio y partida abre la grabacion automatica directamente, sin
  selector de archivos. El reproductor identifica "Ultima partida" sobre sus
  controles; un archivo explicito conserva el titulo "Partida guardada".
  Se mantienen aislamiento del motor, pausas y validaciones de integridad.
- Cargar partida abre directamente datos_generados/partida.bin, el mismo archivo
  que escribe Guardar, sin selector. Si falta, muestra un aviso y conserva el menu.
  La carga conserva las versiones, la semilla y el estado del guardado.
- La cache visual reutiliza tambien fondos e imagenes estaticas ya reducidas
  entre ventanas. Conserva LANCZOS, proporciones y pixeles; las marcas de los
  PNG y del codigo invalidan copias antiguas. El limite de 128 archivos sigue
  siendo independiente de las 25 fichas del catalogo. La primera preparacion
  puede costar mas que las aperturas con copias validas; no ocultar ese costo.

- Al finalizar una partida, victoria y derrota ofrecen Volver al menú principal
  y Terminar. Derrota conserva Jugar de nuevo. Volver limpia la presentacion
  y reutiliza el menu inicial para jugar o cargar; el replay conserva Cerrar replay.
