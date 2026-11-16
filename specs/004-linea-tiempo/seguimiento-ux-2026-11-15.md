# Seguimiento: enemigos, victoria y Salir

## Diagnóstico del recorrido local

El log local existente tiene 23 acciones, cripta 02@52532a77ee04. Reproducido en memoria con su semilla y versiones: jugador en sala 20, vida 30, defensa 2, cero enemigos activados/derrotados, llave negra aún no recogida. El log/guardado originales no se editaron; las pruebas usan archivos temporales. La salida real es sala 18, a través de 17N con itm_llave_negra. La llave está en sala 4. Sala 20 es una cámara secundaria con retorno O→19; desde 19, O→5. Volver por esa rama, recoger la llave y seguir hacia 17 permite abrir N y cruzar a 18.

No es Osario menor: el paquete histórico de cripta 01 tiene 6 salas, salida 6. El listado del servicio consultado en la revisión anterior anuncia 02–06; el selector utiliza ese listado o el del paquete offline elegido. La identidad visible de la partida ahora incluye el ID de cripta para reducir esta confusión. No se trata de ganar llegando al mayor número de sala.

## Población y daño

No hay generación aleatoria adicional de enemigos por el cliente. Las instancias proceden del contenido publicado y permanecen dormidas hasta entrar a su sala; precargar o iluminar no las activa. Una vez activos, conservan su programación y sus comportamientos. En el recorrido local solo se visitó la rama inicial/secundaria; los primeros enemigos de cripta 02 están a partir de sala 7.

| Paquete/versión publicada | Ratas | Guardianes | Sabuesos | Espectros | Carceleros | Total |
|---|---:|---:|---:|---:|---:|---:|
| 02@52532a77ee04 | 5 | 1 | 1 | 0 | 0 | 7 |
| 03@f9186ac25124 | 13 | 2 | 2 | 0 | 1 | 18 |
| 04@7074a17814ad | 18 | 2 | 3 | 0 | 1 | 24 |
| 05@48bfa3b75055 | 8 | 1 | 1 | 0 | 0 | 10 |
| 06@f9ed9afa683d | 36 | 2 | 25 | 11 | 1 | 75 |

Osario histórico: 2 ratas y 1 guardián. Son conteos del contenido completo de esas versiones, no un requisito de que aparezcan todos en el recorrido. La 05 permanece deliberadamente no resoluble.

La fórmula permanece `max(1, ataque + azar.randint(0,4) - defensa)`. La rata publicada tiene ataque3 y velocidad110; el jugador comienza con defensa 2 y la coraza añade2. Sin coraza, sus golpes son1–5; con defensa 4,1–3. Los recorridos de QA recogieron/equiparon equipo y usaron pociones mediante acciones ordinarias; terminar con vida alta no implica que se haya ignorado el daño. No se aumentó población, ataque, frecuencia ni dificultad.

## Fallos corregidos y comportamiento nuevo

- **UX-01, Salir:** el retorno inmediato al menú ya estaba en 705d452. No lo introdujo la última corrección de metadatos de puertas. El controlador ya no abandona ni cancela viaje antes de preguntar. Diálogo: Continuar jugando / Reiniciar esta cripta / Volver al menú principal / Cerrar el juego. Escape o X del diálogo cancela. Se conservan cola y foco al cancelar; no se escribe en guardado/replay ni se avanza el reloj. Cerrar la ventana de una partida activa solicita la misma elección, incluso si debe esperar a finalizar una carga.
- **Reinicio activo:** antes, aplicación solo reiniciaba tras derrota. Ahora acepta una solicitud explícita desde una partida en curso, renueva sesión/precarga/motor para la misma cripta y conserva la política de semilla existente (fija si se pasó --semilla; nueva si no). No guarda encima de archivos previos. No cambia las opciones de fin de partida/replay.
- **UX-03, victoria desde ambos extremos:** abrir con llave desde el lado de la sala de salida no acreditaba el acceso desde el otro extremo. Una prueba falló al volver a cruzar hacia la salida. Ahora la apertura acredita los extremos recíprocos compatibles de la misma puerta, con inversos y binario conservados; no se extiende a retornos ambiguos o llaves contradictorias. Entrar sin haber abierto con llave sigue sin conceder victoria. Este defecto era independiente de la sala 20 del log local.
- **UX-02, orientación:** EstadoVista añade ID y objetivo de presentación, sin cambiar binario ni historia. La GUI/consola indican explorar si la salida aún es desconocida; solo identifican la sala de salida cuando ya se conoce o está ante el jugador. Frente a su acceso explican abrir con llave y luego cruzar. Se conserva el conocimiento parcial, sin mostrar salas ocultas ni añadir consultas HTTP.

Especificaciones/planes previos al código: 0a98158; aclaración de acreditación: d95a58a. No se cambian reglas de combate ni datos del servicio.

## Comprobación

**188 pruebas dirigidas en 61,701 s, OK**: salida/objetivo, puertas recíprocas, cumplimiento integrado, partida completa/generada, historia y persistencia, controlador real, modos, enemigos/juego, reinicio/replay, menú/fin, viaje y transición/presentación. No se suman suites solapadas. Después del ajuste para encolar el cierre durante una carga, los 8 casos UX pasaron nuevamente en 4,042 s. No se repitieron las 834 pruebas ni todos los benchmarks: el alcance se validó con los módulos afectados y sus integraciones. Los resultados temporales de la revisión anterior conservan su fecha/alcance y no se presentan como una medición nueva de este incremento.

La primera selección de 158 detectó que el nuevo texto reducía el lienzo a 380 px en 1100×760, bajo la comprobación existente de 390. Se ajustaron márgenes, sin eliminar esa aserción; los9 casos de menú visual y la selección posterior de 188 pasaron. El diálogo se probó con una ventana Tk visible, cuatro elecciones, Escape/cierre, bloqueo de entradas y cola preservada. La preparación inicial con padre oculto se interrumpió al no poder transferir foco para Escape; no se cuenta como aprobación. No se afirma inspección visual manual completa del diálogo: el intento nativo aislado llegó al menú y se cerró sin interferir con otras ventanas en uso.

QA offline por acciones ordinarias (sin modificar estadísticas/salas/enemigos), usando conocimiento global únicamente para el bot de prueba, no para la vista/jugador:

| Recorrido | Acciones nuevas | Enemigos derrotados | Daño total comprobado | Vida final | Resultado |
|---|---:|---:|---:|---:|---|
| 02, semilla 20 | 44 | 7 | 20 | 28 | victoria en 18 |
| 03, semilla 20 | 84 | 18 | 48 | 26 | victoria en 34 |
| 04, semilla 20 | 105 | 24 | 61 | 29 | victoria en 42 |
| 06, semilla 42 | 117 | 13 | 36 | 30 | victoria en 160 |
| Copia del recorrido local, desde 20 | 48 | 7 | 51 | 30 | victoria en 18 |

Cada llamada real de aplicación de daño al jugador fue observada sin sustituir la regla y comprobada contra `vida_despues=max(0,vida_antes-dano)`. El total incluye trampas; las curaciones explican las vidas finales. La continuación local tuvo golpes de hasta7, sin coraza equipada. Cero HTTP en esos cinco recorridos. Los resultados son de esos recorridos/semillas, no una prueba de que cualquier estrategia gane o una garantía de cero bugs. [Resumen conservado](seguimiento-ux-evidencia.json).

Pruebas nuevas reproducibles: `python -B -X utf8 -m unittest tests.test_salida_objetivo -v`. Los paquetes de referencia se descargan con los comandos del README; los logs de trabajo/QA y el log de la usuaria no se incluyen en Git.
