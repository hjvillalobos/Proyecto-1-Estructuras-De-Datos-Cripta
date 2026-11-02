# Plan técnico propuesto

Python >= 3.11; MVC existente; sin dependencias nuevas para estructuras evaluadas. Este documento pertenece al diseño, no a las reglas de juego de spec.md.

## Constitución

Se conserva la constitución compartida 1.1.0 de main. Índices propios sin dict/set, heapq, bisect, collections ni bibliotecas de grafos. Búsqueda binaria y ordenamiento propios. Sin HTTP durante historia; sin vista en replay/bench/verificar; sin IDs de criptas en lógica. Especificación confirmada antes del código. Complejidades abajo son objetivos analíticos, todavía sin evidencia empírica.

## Decisión propuesta

### Primer incremento independiente

El núcleo recibe un estado histórico puro: campos de clave textual estable y valores inmutables (escalares o tuplas recursivas). Cada cambio conserva presencia y valor antes/después, para expresar creación y eliminación además de sustitución. No contiene objetos vivos, closures ni índices dict/set. El adaptador al estado del motor se implementará después.

Un arreglo ordenado propio de campos con búsqueda binaria permite leer claves; insertar/eliminar desplaza campos y cuesta O(numero de campos). No se promete actualización constante. Se valida una acción completa sobre solo los campos afectados antes de modificar el estado actual, sin copiar todo el mundo por acción.

Una acción registrada contiene sus cambios inmediatos, el reloj inicial/final y lotes de eventos ordenados por tiempo y secuencia. Cada acción ordinaria avanza el reloj; eventos dentro del intervalo tienen tiempo mayor al inicio y menor o igual al final. Los cambios inmediatos se observan para t mayor al inicio; en el instante inicial se devuelve el estado anterior a decidir. Si el motor produce eventos en el propio instante inicial, los entrega antes de publicar esa frontera, no como efectos futuros de la acción. Consultar #k identifica antes de la acción k. La adaptación del motor debe verificar estas precondiciones, no alterar el orden de eventos a escondidas.

Se almacenan bloques de hasta K acciones y una base al principio de cada bloque. La búsqueda binaria propia de los tiempos finales localiza la frontera; un máximo de K acciones, incluidas las parciales, se aplica sobre una copia independiente. Se expone el conteo reconstruido como evidencia estructural del límite, sin afirmar tiempos de rendimiento.

Recortar conserva un número dado de acciones completas, elimina el sufijo y permite continuar una rama. Las correcciones persistentes del pergamino se adjuntan a la frontera como cambios adicionales; al coincidir con un checkpoint se reemplaza esa base, sin añadir controles fuera de cadencia. Este incremento no escribe archivos ni conecta comandos del juego.

Reconstrucción hacia adelante aplicando deltas completos de todos los cambios reales, no reejecutando comandos contra red o mundo presente. Base inicial y copia de control cada K acciones completadas. Una copia contiene un estado reconstruible independiente, incluido azar, agenda y secuencias. Los deltas deben incluir cambios de eventos automáticos entre decisiones y dentro de un instante; un delta solo por comando resulta insuficiente para consultar cualquier t.

Historial segmentado en bloques de K acciones. Índice ordenado de checkpoints por frontera temporal y número de acción, con búsqueda binaria propia. Cada registro conserva tiempo y secuencia total para empates. Registros por eventos dentro de cada acción permiten detener reconstrucción en t sin aplicar eventos posteriores.

Una consulta localiza la última base que no supera su frontera, la copia a un estado de trabajo independiente y aplica los cambios hasta la frontera pedida. Para #k usa el límite anterior a la acción, no una aproximación solo por reloj. Nunca invocar mutadores de la partida viva.

## Recorte y memoria

El retroceso a una frontera mueve el final lógico de la cadena de bloques y del índice, y descarta solo sufijo afectado. Nuevas acciones sobrescriben o crean una rama desde ese límite; las consultas no acceden al sufijo eliminado. Liberar bloques retirados para que la memoria no crezca con futuros descartados. Diferenciar costo de localizar corte del costo inevitable de liberar los objetos descartados: no prometer O(1) de liberación total.

Con motor = acciones, S = tamaño de estado y integración = volumen de cambios, memoria esperada O(integración + (motor/K + 1)S), más índices. Ubicar checkpoint O(log(motor/K + 1)); reconstruir O(S + cambios de hasta K acciones). Copiar la base cuesta O(S): el límite K no implica por sí solo una consulta rápida. Eventos por acción pueden ser numerosos; medirlos.

## Módulos

- Nuevo `modelo/linea_tiempo.py`: índices, bloques, reconstrucción y recorte propios.
- `modelo/snapshots.py`: contratos compartidos de historia y persistencia. Acordar antes de editar con motor y conocimiento.
- `datos/guardado_binario.py`: nuevo formato, bloques de historia, validación de límites/versiones/CRC y lectura simétrica.
- `controlador/`: interpretación y coordinación de historia, mapa y viaje; presentación usa resúmenes filtrados.
- `main.py`: modos excluyentes, K y --hasta, rutas sin vista y verificación antes de juego.
- Replay/bitácora: movimientos individuales, comentarios, cargas y pergaminos reproducibles.
- `vista/`: presentación de mapa/costos/cazador y motivos; sin implementar reglas.
- `bench.py`: integrar mediciones integración y funciones entregadas por los demás.

## Persistencia

### Incremento independiente de persistencia histórica

Antes de cambiar el archivo de partida, `datos/historia_binaria.py` implementará un fragmento binario independiente con firma CRLH y versión de fragmento 1. No se anuncia como archivo de partida P2 ni sustituye el formato CRPT 3 existente. Al recibir CRPT, el lector de historia informa incompatibilidad explícita.

El contrato `HistoriaGuardada` contiene K, campos iniciales y acciones con sus tiempos, cambios, eventos y correcciones persistentes. Exportar conserva solo la rama vigente. Importar construye una línea nueva y valida todos los registros antes de entregarla; no muta una historia activa. Los checkpoints y el presente se regeneran determinísticamente a partir de base y deltas durante la carga, evitando duplicar copias completas dentro del fragmento. Esto conserva toda la información histórica; no promete carga aleatoria de checkpoints en disco.

Valores codificados por etiquetas explícitas: nulo, booleano, entero de precisión arbitraria, real finito, texto UTF-8 y tuplas recursivas. Se incluyen longitud y CRC del contenido y versión. Se rechazan truncamientos, bytes sobrantes, etiquetas/UTF-8 inválidos, profundidad excesiva, valores incoherentes, K inválido y acciones fuera de orden. Guardar usa temporal único en la misma carpeta y reemplazo al completar; si falla, se conserva el archivo anterior.

El formato integrado 4, acceso a salas y captura completa del motor siguen pendientes. El PDF P1 proporcionado el 2026-11-02 está vacío (0 bytes); no se da por revisado ese contrato heredado. El fragmento permite avanzar y comprobar ida/vuelta, continuación, azar sintético y recortes sin depender de los productores del motor.

Formato 4 elegido para esta rama: encabezado con identidad/versiones, K, frontera vigente y descriptor de bloques; estado actual, base inicial, controles y deltas con longitudes y comprobaciones. Mantener capacidades de acceso a salas de P1; revisar el enunciado completo P1 antes de cerrar el diseño del archivo. Validar truncamiento, offsets fuera del archivo, K inválido, fronteras desordenadas y referencias inconsistentes antes de reemplazar la partida activa. Escribir en temporal y reemplazar al finalizar correctamente.

## Rendimiento y alternativas

Comparar K 10/50/100 y reconstrucción desde inicio sin checkpoints solo como alternativa de medición; esta última no cumple el límite de reconstrucción para partidas arbitrarias. Medir también inversión desde actual como alternativa de dirección. No incorporar ambas direcciones a producción sin evidencia. Los resultados finales y elección de K van en DECISIONES.md.

## Dependencias y límites

Contratos en `contracts/interfaces.md`; datos en `data-model.md`; tareas y pruebas en sus documentos. No está verificada la captura exhaustiva actual de motor y conocimiento. No se promete determinismo hasta probar restauración de agenda, secuencias, azar y conocimiento completos. No se ejecutaron pruebas de P1 ni benchmarks en esta preparación.


Decisiones de fronteras y retroceso: ver Assumptions de spec.md. Constituyen el contrato de esta capacidad; las otras capacidades deben adaptar sus productores antes de la integración real. No se requiere su implementación para probar el núcleo con cambios sintéticos.


## Investigación del motor actual y adaptación obligatoria

Revisión de código, 2026-11-02: RegistroTurno contiene lambdas referidas a objetos vivos; no serializarlas. exportar_estado aporta base útil pero restaurar consulta catálogo: historia usará estado puro y fichas inmutables de versión, nunca restaurador vivo.

El ciclo actual se detiene al extraer turno_jugador aunque existan eventos posteriores con igual tiempo. T003 debe garantizar el lote temporal completo de P2 para H3; el historiador no ejecuta eventos ocultamente sobre el presente. Revisar regresiones P1 al cambiar ese límite.

Retroceso restaura azar, secuencia y contador; después descuenta pergamino fuera de deltas. Recoger/soltar pergaminos tampoco se revierte. T009 necesita corrección de frontera y no solamente recortar. Si una corrección corresponde a una frontera con checkpoint, actualizarlo sin crear copias adicionales; las consultas resuelven la rama vigente corregida.

## Fases de entrega

Preparación y contratos → núcleo sintético → captura real → recorte/persistencia → modos sin vista → interfaz → mediciones/defensa. Tareas concretas en tasks.md. La integración real requiere entregas de motor, conocimiento y verificador; el núcleo sintético no depende de que estén terminadas.

K inicial elegido para desarrollo: 50. Es un parámetro configurable, no una conclusión de rendimiento. La elección definitiva debe revisarse con T019. Formato P2: 4, después de confirmar en esta rama que el actual es 3. Sin migración automática.
