# Plan técnico propuesto

## HU-02 — informe detallado

Añadir un formateador detallado separado de `resumir`, con fichas residentes y proyección del mapa reconstruida por conocimiento histórico sobre topología inmutable. Transmitir al formateador solo esas proyecciones. Añadir contador de acciones a la respuesta de consulta, calculado desde la frontera ya localizada. Registrar derrotados/resultado en un campo histórico adicional de tamaño constante, por diferencias; las historias antiguas sin ese campo conservan su esquema al cargar/continuar y se identifican como no registradas. Sin cambios del formato binario, reglas, reloj o azar. Presentación gráfica monoespaciada, secciones y desplazamiento. Validar privacidad, inventario, muerte/victoria, binario antiguo/nuevo, retroceso, pureza y regresiones; medir impacto del campo adicional con los benchmarks existentes. Análisis: MVC, estructuras propias y límites de reconstrucción conservados; no copiar mundo por acción ni consultar red.

## HU-01 — contexto de Historia (2026-11-17)

El controlador transmite a la vista los dos escalares de `linea_tiempo` (reloj y cantidad de acciones) al presentar el estado, mediante un método opcional de vista. La ventana recibe esos valores, muestra rangos, preselecciona una referencia válida por modo y valida sin consultar el modelo. El título del informe identifica tiempo u ordinal solicitado; el contenido conserva `resumen_historia`. Sin búsquedas/copias históricas adicionales por turno, sin cambio del motor, persistencia o API. Pruebas Tk del diálogo y recorrido botón→cola→controlador→informe con motor offline real, incluyendo pureza y cancelación. Análisis previo: implementa FR-001/003/005/020; no altera estructuras ni complejidad de reconstrucción y conserva MVC.

## Estado técnico vigente — 2026-11-16

ERR-01: adaptar AlmacenLocal al patrón de limpieza ya usado por la persistencia histórica. Conservar una excepción pública DatosNoDisponibles con causa original; añadir notas Python 3.11 si unlink falla durante recuperación. Tras os.replace exitoso, retirar la referencia al temporal. Probar reemplazo fallido más limpieza fallida, serialización inválida y éxito sin residuos usando archivos reales y fallos inyectados. Trabajo O(tamaño del JSON), sin nueva estructura evaluada, dependencia, vista o cambio de red.

Las cuatro capacidades están integradas. Los apartados fechados conservan las alternativas y entregas parciales de su momento; sus expresiones «propuesto», «pendiente» o «sin medir» no sustituyen este estado actual. La fuente de resultados finales es DECISIONES.md.

UI-01 usa el diálogo local ConsultaHistoria y delega al comando ordinario; valida tiempo >=0 y acción >=1 antes de encolar. UI-02 usa NieblaMapa sobre Canvas con geometría decorativa fija respecto del conocimiento; temporizador de presentación de 50 ms, opción sin movimiento y cancelación al destruir/cerrar. UI-03 consulta primero la caché de acciones, conserva como máximo ocho resultados y usa el respaldo de secuencias cuando falta atlas válido. Las firmas obligan a regenerar las composiciones al modificar sus fuentes; comparar píxeles contra la revisión anterior. Sin cambios de algoritmo evaluado, formato binario o dependencias. Consolidación posterior de cambios locales, no prueba retrospectiva del orden spec→código.

## VD-01 — destino con conocimiento parcial

El controlador atiende la petición de elegir destino antes de cancelar el viaje activo; entrega proyección/posición al diálogo y solo una aceptación llama al flujo existente de ir a. La vista filtra estado explorado antes de formar lista/detalle, muestra entrada numérica y error local sin revelar ID oculto, y conserva _en_menu/foco/cola al cancelar. Reutilizar tema, fondo y patrones de NombrePuntaje/SalidaPartida, sin acceder a modelo/red. Pruebas de teclado/cancelación/validación, privacidad y estado/log/viaje intactos. RP y VD se prueban como incrementos acotados, sin rediseñar otros diálogos.

## RP-01..04 — conexión de replay gráfico

El lanzador de GUI usa Popen con modo explícito independiente y no devuelve stdout como informe; consola conserva subprocess.run con salida textual. El proceso hijo crea VistaGrafica y ReproductorReplay con fábrica completa más integrar_historia; todos los cierres liberan vista/precarga del hijo. Reutilizar ejecutar_tarea para carga/acciones de datos sin bloquear Tk y comprobar detener/cierre antes de presentar. No crear ControladorJuego ni BitacoraReplay.iniciar en reproducción. El archivo se lee una vez a memoria; no es streaming del log activo. Conservar controles/animación existentes y costos del descriptor en EstadoVista. Pruebas con partida completa y log de carga/pergamino, fábrica independiente, comparación exacta de estado e integridad de archivos; lanzador probado desde menú y controlador; CLI sin constructor de vista; widget Tk y captura nativa si la superficie permite inspección sin interferir con la usuaria. No modifica reglas o búsquedas ni justifica repetir todos los benchmarks.

## Seguimiento UX-01..03

Diálogo Tk local modal sin acceso al modelo, con _en_menu para bloquear entradas nuevas y conservar las ya encoladas al cancelar. Controlador consulta antes de cancelar viaje o cambiar ejecutando; comunica reinicio explícito a aplicación. Aplicación reutiliza renovación de sesión y política de semilla, sin pasar por selector ni guardar automáticamente. EstadoVista añade campos opcionales de presentación (ID/objetivo), sin tocar binario/historia; objetivo deriva del conocimiento y de las salidas observadas. Pruebas de cancelación con log/guardado/viaje iguales, cuatro elecciones, cierre/Escape, aplicación con motores nuevos, regresiones cercanas de menú/replay/viaje, población/daño/victoria reales. Análisis: no cambia reglas, azar, agenda, rutas ni benchmarks del motor; no requiere repetir benchmarks sin señal de regresión.

## Revisión RE-01..04 (2026-11-15)

Resolver extremos con el emparejamiento propio ya existente, una vez por apertura. Leer llave/cierre del descriptor usado y, solo si falta el atributo, del único retorno físico. No copiar ni normalizar descriptores, alterar búsqueda de rutas o agregar índices hash. Imputar el trabajo O(grado) a abrir, no a cada evento. Pruebas negativas sin llave, ciclo real de cierre/reapertura, binario/retroceso y conexiones no emparejables. Validar contenido nuevo con fábrica/controlador/vista reales, backend de audio espía y WAV reales desde CWD ajeno, y animación por coordenadas sin cambios de modelo. Matriz de Parte I/II y auditoría independiente de mapas, separando asimetrías del servicio de defectos propios. Ejecutar regresión, opciones separadas y benchmarks aislados antes del push ordinario a 004-linea-tiempo. El análisis previo conserva reglas IA-04 y las restricciones de estructuras/MVC; no atribuye la decisión de puertas remotas al profesor.

> **Estado vigente de entrega:** las cuatro capacidades están integradas en `004-linea-tiempo`. Consultar [estado, trazabilidad y límites actuales](../../ESTADO_ENTREGA.md). Los balances y restricciones de autorización fechados anteriores son registros históricos, no bloqueos de la implementación actual. La revisión humana y los faltantes auténticos no se dan por resueltos mediante este aviso.


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

### Manejo de errores del núcleo independiente

Los errores esperados del dominio se identificarán por clases en `modelo/errores_historia.py`: entrada inválida, referencia histórica inexistente/futura e incoherencia de cambios. Todas heredarán de ValueError para conservar compatibilidad. La consulta de un campo ausente mantiene KeyError; es distinta de un campo nulo.

La capa binaria mantiene ErrorGuardado, FormatoIncompatible y GuardadoCorrupto ya compartidos por datos. Las rutas inválidas y los tipos no binarios se traducen a ErrorGuardado con mensaje claro. La carga no altera una historia viva; registrar/recortar valida antes de mutar. Si falla la escritura se conserva el destino y se intenta limpiar su temporal; si falla esa limpieza, se añade una nota al error principal, sin ocultarlo ni borrar otro archivo. Errores inesperados de programación no se silencian con `except Exception`.

La matriz de errores y su comprobación se documentará en `errores.md`; el controlador deberá capturar las clases esperadas cuando se haga la integración real. Este incremento no simula que la interfaz ya los muestra.

### Incremento independiente de persistencia histórica

Antes de cambiar el archivo de partida, `datos/historia_binaria.py` implementará un fragmento binario independiente con firma CRLH y versión de fragmento 1. No se anuncia como archivo de partida P2 ni sustituye el formato CRPT 3 existente. Al recibir CRPT, el lector de historia informa incompatibilidad explícita.

El contrato `HistoriaGuardada` contiene K, campos iniciales y acciones con sus tiempos, cambios, eventos y correcciones persistentes. Exportar conserva solo la rama vigente. Importar construye una línea nueva y valida todos los registros antes de entregarla; no muta una historia activa. Los checkpoints y el presente se regeneran determinísticamente a partir de base y deltas durante la carga, evitando duplicar copias completas dentro del fragmento. Esto conserva toda la información histórica; no promete carga aleatoria de checkpoints en disco.

Valores codificados por etiquetas explícitas: nulo, booleano, entero de precisión arbitraria, real finito, texto UTF-8 y tuplas recursivas. Se incluyen longitud y CRC del contenido y versión. Se rechazan truncamientos, bytes sobrantes, etiquetas/UTF-8 inválidos, profundidad excesiva, valores incoherentes, K inválido y acciones fuera de orden. Guardar usa temporal único en la misma carpeta y reemplazo al completar; si falla, se conserva el archivo anterior.

El formato integrado 4, acceso a salas y captura completa del motor siguen pendientes. El PDF P1 proporcionado el 2026-11-02 está vacío (0 bytes); no se da por revisado ese contrato heredado. El fragmento permite avanzar y comprobar ida/vuelta, continuación, azar sintético y recortes sin depender de los productores del motor.

Formato 4 elegido para esta rama: encabezado con identidad/versiones, K, frontera vigente y descriptor de bloques; estado actual, base inicial, controles y deltas con longitudes y comprobaciones. Mantener capacidades de acceso a salas de P1; revisar el enunciado completo P1 antes de cerrar el diseño del archivo. Validar truncamiento, offsets fuera del archivo, K inválido, fronteras desordenadas y referencias inconsistentes antes de reemplazar la partida activa. Escribir en temporal y reemplazar al finalizar correctamente.

## Rendimiento y alternativas

Comparar K 10/50/100 y reconstrucción desde inicio sin checkpoints solo como alternativa de medición; esta última no cumple el límite de reconstrucción para partidas arbitrarias. Medir también inversión desde actual como alternativa de dirección. No incorporar ambas direcciones a producción sin evidencia. Los resultados finales y elección de K van en DECISIONES.md.

## Dependencias y límites

### Preparación MC-01 desde D — 2026-11-13

Ampliar `tests/test_controlador_ac_real.py` con un caso positivo de FR-011
reutilizando su fixture offline real. Guardar después de la primera entrada,
avanzar a otra sala y cargar. Comparar el DTO leído del binario, el estado
exportado, la historia exportada (incluido K), el mapa estructurado y su
presentación; repetir el movimiento para comprobar continuación determinista.
El caso atraviesa un checkpoint y exige olvidar descubrimientos posteriores.

Solo se agregan aceptación y documentación de D. A conserva la conexión de
`restaurar_estado_con_historia`; con C debe incorporar el conocimiento inicial,
sus deltas y la reconstrucción validada. No se decide un nuevo esquema de
persistencia ni se quita la restricción del motor en este incremento. Un fallo
real se documenta como pendiente, conforme al criterio de puertas recíprocas.
No se añaden índices ni estructuras de producción, dependencias o agentes.

Contratos en `contracts/interfaces.md`; datos en `data-model.md`; tareas y pruebas en sus documentos. No está verificada la captura exhaustiva actual de motor y conocimiento. No se promete determinismo hasta probar restauración de agenda, secuencias, azar y conocimiento completos. No se ejecutaron pruebas de P1 ni benchmarks en esta preparación.


Decisiones de fronteras y retroceso: ver Assumptions de spec.md. Constituyen el contrato de esta capacidad; las otras capacidades deben adaptar sus productores antes de la integración real. No se requiere su implementación para probar el núcleo con cambios sintéticos.


## Investigación del motor actual y adaptación obligatoria

Revisión de código, 2026-11-02: RegistroTurno contiene lambdas referidas a objetos vivos; no serializarlas. exportar_estado aporta base útil pero restaurar consulta catálogo: historia usará estado puro y fichas inmutables de versión, nunca restaurador vivo.

El ciclo actual se detiene al extraer turno_jugador aunque existan eventos posteriores con igual tiempo. T003 debe garantizar el lote temporal completo de P2 para H3; el historiador no ejecuta eventos ocultamente sobre el presente. Revisar regresiones P1 al cambiar ese límite.

Retroceso restaura azar, secuencia y contador; después descuenta pergamino fuera de deltas. Recoger/soltar pergaminos tampoco se revierte. T009 necesita corrección de frontera y no solamente recortar. Si una corrección corresponde a una frontera con checkpoint, actualizarlo sin crear copias adicionales; las consultas resuelven la rama vigente corregida.

## Fases de entrega

Preparación y contratos → núcleo sintético → captura real → recorte/persistencia → modos sin vista → interfaz → mediciones/defensa. Tareas concretas en tasks.md. La integración real requiere entregas de motor, conocimiento y verificador; el núcleo sintético no depende de que estén terminadas.

K inicial elegido para desarrollo: 50. Es un parámetro configurable, no una conclusión de rendimiento. La elección definitiva debe revisarse con T019. Formato P2: 4, después de confirmar en esta rama que el actual es 3. Sin migración automática.

## Incremento de integración de D

El reloj de la consulta se toma del motor, con pruebas de salidas ponderadas y
eventos empatados. Una acción terminal puede completar sin avanzar el reloj:
la consulta por el instante de decisión conserva el estado previo y el
resumen final del replay posterior al fin usa el resultado de la partida.
El historial recibe proyecciones y cambios serializables en puntos de mutación
del motor, nunca copias de salas completas por acción. El estado vivo y el
conocimiento que pueda aportar su productor se guardan junto a la rama vigente.

Para la verificación se consume el módulo entregado por B y se mantiene su
distinción entre dictamen negativo y verificación incompleta. La presentación
de mapa y viaje se valida con un productor de prueba mientras no haya una
implementación de C disponible. No se alteran sus reglas ni se declara
aceptación integrada con C sin su implementación.

La captura de los productores permanece a cargo de A/C. D entrega un receptor
con inicio, acción completa, recorte y restauración. La adhesión al protocolo
se comprueba con dobles de prueba y se declara separada de la aceptación con
los productores reales. La CLI puede señalar que el verificador aún no está
disponible en esta rama, sin sustituir el algoritmo de B.

### Aceptación integrada offline de D — 2026-11-12

Los párrafos anteriores describen la preparación original. El verificador B
ya está integrado; se mantienen sus comprobaciones. Ahora se usa además el
productor histórico real de A bajo activación explícita offline, el mapa real
de C conectado por A y el control de viaje de C inyectado por la interfaz de D.
La fábrica de prueba se limita a elegir las opciones existentes de A; no
reemplaza acciones, eventos ni restauración. Se reutiliza el paquete sintético
de B con cliente offline y se bloquea HTTP. Solo la vista receptora se simula.

`tests/test_controlador_ac_real.py` verifica DX-01..06, incluidos comandos,
archivos v4, log generado por el controlador, replay sin vistas, consultas
puras y cancelación. Prueba por separado los límites actuales: `hechos_paso`
ausente y rechazo de restauración con conocimiento activo. No se habilitan
opciones de prueba en la aplicación normal ni se atribuye a esta aceptación
persistencia del mapa/inventario histórico o viaje automático completo.


## Plan de integración completa — 2026-11-14

### Fortalecimiento RF-01..03

### RC-01 — registro histórico de baja latencia

### VI-01..05 — presentación gráfica aislada

Implementar ventana Tk Canvas, colores de piedra/ámbar/verde y niebla decorativa estática. Recibir solo tuplas de `mapa_conocido`, sala actual y destino conocido; sin referencia al modelo ni a precarga. Traducir IDs mediante índices ordenados y búsqueda binaria propia, distribuir por componentes y capas con grado acotado; separar nodos aunque conexiones no encajen en una cuadrícula. Mostrar arcos dirigidos, recuerdo de puerta, sala seleccionada y detalle textual. Dibujar solo al abrir/cambiar encuadre; no añadir animación al ciclo del motor. Viaje se emite por la cola normal después de cerrar el modal. Mostrar texto alternativo y desplazamiento/zoom. Cargar ilustración de sabueso generada con alpha mediante la cache visual existente, con respaldo por comportamiento para tipos futuros. Pruebas de privacidad con nombres/conexiones ocultas, IDs dispersos, ciclos y grafos dirigidos; GUI y API real. Comparar benchmark RC-01 sin vistas antes/después, separar tiempo de render del procesamiento.

Perfil del ciclo de 120 acciones: ordenar proyecciones y enemigos ocupa gran parte del costo. Conservar solo un orden de referencias de enemigos de la sala actual, con comparación por identidad de la secuencia antes de reutilizar; no almacenar sus vidas ni valores mutables en el derivado. Proyectar valores nuevos cada vez y filtrar muertos al producirlos. Comparar los tres campos fijos por posición y fusionar las colas de enemigos ya ordenadas; devolver triples directamente, sin construir cambios tipados que el receptor vuelve a construir. Inventario/mapa conservan sus deltas y el comparador general para cambios estructurales infrecuentes. Referencia anterior conservada para comprobar igualdad por evento y benchmark pareado. Auxiliar O(enemigos de la sala), sin tablas hash. Sin cambios de reglas ni esquema; el perfil instrumentado no certifica tiempos reales.

Decisión final RF-02: usar índice radix propio sobre dígitos de cuatro bits en los almacenes dispersos, en lugar de búsqueda binaria por acceso. Motivo: mantener la consulta de rastro independiente de V, con hasta ocho niveles para los IDs uint32 persistibles. Cada colección conserva su índice y valores compactos para una copia/restauración independiente sencilla; no se afirma compartir un único índice mutable. El caso denso conserva listas con un máximo de cuatro posiciones por sala. Longitud/iteración representan valores existentes; `limite_ids` expone por separado el límite lógico. Las pruebas de listas/deepcopy/IDs extremos y partida completa verifican este contrato.

Mantener el heap indexado propio y almacenar su clave total al mejorar una etiqueta; evitar reconstruir tuplas en cada comparación. Mantener las generaciones y limpiar solo la frontera tocada. Para IDs dispersos usar un almacenamiento propio con IDs ordenados, búsqueda binaria y valores compactos, compartiendo el índice entre colecciones del motor y rastro. En mapas densos conservar el acceso directo; elegir por densidad al preparar, nunca por una cripta particular. Recorrer IDs existentes en exportación/restauración. Validar equivalencia con la referencia previa, datos de IDs grandes y persistencia/replay reales. Consolidar estado documental al principio y añadir matriz de los 23 casos del Apéndice B. Análisis previo: RF-01 preserva FR de rutas; RF-02 no cambia reglas ni binario; RF-03 atiende §2.5/2.6/7.1. Sin estructuras prohibidas ni dependencia de vista/red. No se alteran checklists de revisión humana.

Reutilizar Motor y sus inversos; un productor de producción amplía la proyección H3 con inventario y conocimiento de C y genera diferencias ordenadas propias. No persistir copias físicas por acción. Compartir identidad de puerta por pareja de extremos recíprocos; no inventar conexiones inversas en salidas dirigidas. La antorcha procesa solo vecinos revelados; los recuerdos remotos quedan desconocidos. Preparar conocimiento fuera del vivo al cargar; validar proyección contra frontera histórica antes de restaurar. Mantener el formato v4 mediante campos históricos puros; ausencia de campos requeridos causa incompatibilidad explícita. Hechos de daño se capturan cuando ocurre, no comparando vida inicial/final. Pruebas primero con aceptación ya fallida MC/PD y nuevas pruebas de producción. Comparar alternativas en benchmarks sin activar optimizaciones sin evidencia. Ningún índice dict/set ni biblioteca restringida. Revisión de consistencia: IA-01..09 enlazan FR-004/007/011/013/018/019; las pruebas se ejecutarán con motor real y los límites se reportarán por carga.
