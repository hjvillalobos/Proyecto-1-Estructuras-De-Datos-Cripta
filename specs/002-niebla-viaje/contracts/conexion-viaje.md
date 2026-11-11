# Propuesta para conectar el viaje

10 de noviembre de 2026. Pendiente de acuerdo con A y D; no implementada.
Referencias revisadas: A 9730482, D 02da6b6 y C a1e0184.

## 1. Entrega del motor — A con C y D

Proponemos añadir a `ResultadoAccion` el campo opcional `hechos_paso`, con valor inicial `None`. Así se conservan `ok`, `mensaje` y las trampas que ya usa el controlador. Solo los movimientos entregan un `ResultadoPaso` de C:

| Dato | Momento de captura |
| --- | --- |
| posición y aceptación | Resultado final del movimiento; deben coincidir con `ok`. |
| entrada | Cuando el jugador cambia físicamente de sala. |
| enemigos al entrar | Tras cargar la sala, antes de activar enemigos y procesar sus eventos; incluye vivos dormidos. |
| daño recibido | Cuando disminuye la vida del jugador por ataque, veneno o trampa. Se conserva aunque después se cure. |
| partida terminada | Al cerrar el intervalo del motor. |

Los hechos se reinician por intento. Un movimiento rechazado conserva posición y no indica entrada. Un fallo de ejecución revierte el turno y no publica un resultado exitoso. La entrega ocurre después de los eventos empatados; no añade acciones, tiempo ni solicitudes HTTP. La comparación de vida inicial/final y el productor H3 no bastan para detectar todo el daño.

Archivos a revisar: `modelo/juego.py`, `modelo/efectos.py` y `modelo/snapshots.py`. A implementa o revisa la captura; D revisa la ampliación de su resultado; C comprueba su consumo con `ControlViaje`. Primera aceptación: movimiento normal, rechazo, guardián, trampa, veneno, daño seguido de curación y rollback. El comportamiento sin viaje debe conservarse.

## 2. Ejecución por pasos — C con D

Tras aceptar la entrega anterior, sustituir la conexión propuesta `viajar_hasta(destino, mover)` por el control por pasos que C ya tiene. D inicia el viaje y solicita una propuesta; ejecuta un único movimiento por `_accion_modelo`, conservando animación y replay, y comunica sus hechos a C antes de pedir otro paso.

El resultado completo debe quedar disponible sin romper los consumidores actuales del booleano de `_accion_modelo`. No ejecutar movimientos directamente desde un temporizador ni usar un bucle que bloquee la entrada. Entre pasos deben poder procesarse cancelación y pergamino. Antes de ejecutarla, comprobar que la propuesta sigue vigente; cancelar antes de restaurar o cambiar de partida. El mecanismo concreto de programación en consola y GUI lo revisa D.

La orden se registra como comentario y cada movimiento aceptado como acción. Al detenerse se muestran las causas de C. Mantener el estilo visual actual. Primera aceptación: viaje de dos pasos, llegada, puerta cerrada observada con alternativa, daño, enemigos y pergamino entre pasos.

## Dependencias que no cierra este acuerdo

Falta conectar el conocimiento al turno del motor, acordar identidad de puertas y agregar sus deltas al retroceso/historia. La antorcha conserva su aclaración pendiente. Estas tareas se coordinan por separado: aceptar los hechos del movimiento no significa que el viaje completo ya esté integrado.

**Confirmación necesaria:** A y D aceptan el campo opcional y quién lo implementa/revisa. Después se acuerda la ejecución por pasos de D. Hasta entonces, C conserva sus módulos y pruebas actuales sin cambiar los consumidores compartidos.
