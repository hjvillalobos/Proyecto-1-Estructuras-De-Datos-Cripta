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
- Se verifican 1280x800 y 1100x760, incluyendo escenas pobladas, equipo y replay.

## Movimiento visual

- El menu de inicio usa los mismos colores, tipografia y recursos locales. Permite
  Jugar, Cargar partida, Replay, Puntajes y Salir con raton, flechas y Enter.
  Es una capa de vista temporal sin motor; sus callbacks se cancelan al salir.
  El indicador t=0 corresponde a una partida nueva, no a una simulacion activa.

- AnimacionEscena usa un solo callback de Tkinter cada 40 ms, sin acceder al modelo
  ni al azar. Respiracion de 1.5 px, entrada de sala de 18 px y reaccion breve al dano.
- Solo se mueven sprites: nombres, salud, controles y zonas de clic permanecen
  estables. Los objetos conservan su etiqueta de recogida.
- La casilla Animaciones permite desactivar el movimiento. Cambiar de sala,
  redimensionar, reiniciar o cerrar cancela el callback y libera sus referencias.
- No hay movimiento libre ni ataques automaticos. Las flechas siguen siendo
  acciones discretas entre salas; el reloj virtual solo pertenece al motor.
