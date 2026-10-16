# Cripta: interfaz nativa

Aplicacion de escritorio Tkinter, en espanol. La escena permite decidir una accion
por vez; la simulacion usa tiempo virtual y los efectos visuales usan callbacks de
Tkinter. El aspecto nunca cambia estadisticas, costos, semillas ni reglas.

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
- El selector vive en `vista/selector_cripta.py`, usa una lista nativa accesible
  por teclado y muestra por separado salas y dificultad de la seleccion.
  Ocupa la ventana principal completa, sin ventana modal ni tablero visible
  detras. Enter o doble clic confirma; Volver y Escape regresan al inicio.
  No altera el reloj, la API, el modelo ni los identificadores de las criptas.

## Comportamiento

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
