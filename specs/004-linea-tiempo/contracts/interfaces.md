# Contratos que integración propone al equipo

Contrato de diseño de esta capacidad; interfaces aún no implementadas. Los productores deberán adaptarse en las tareas T002, T003 y T010 antes de integrar.

## motor → integración: motor

Entregar base reconstruible y flujo ordenado de cambios con tiempo, secuencia y frontera de decisión. Incluir acciones aceptadas, eventos automáticos, puertas, efectos, enemigos, azar y agenda. El motor define orden de eventos empatados; integración lo preserva. Consultar no llama al motor vivo. motor instrumenta su subsistema; integración no deduce cambios comparando copias completas por acción.

Notificar frontera exacta posterior al retroceso y efectos que permanecen del pergamino. Confirmar la definición de antes de acción #k y la convención para varias decisiones con igual reloj.

## conocimiento → integración: conocimiento e inventario

Entregar cambios serializables de exploración, avistamiento y memoria de puertas, con información suficiente para aplicar y revertir. Entregar proyección de mapa conocido y resultado de viaje con siguiente paso/motivo de detención. conocimiento aplica reglas de viaje; cada paso usa acción ordinaria del motor. integración interpreta texto y muestra datos filtrados.

## verificador → integración: verificación y datos

Preparación entrega identidad/versiones y resultado independiente de la vista: resoluble; orden determinista de llaves, o llaves inalcanzables, frontera con llaves requeridas y sus ubicaciones, y ciclos concretos. verificador realiza análisis y controla solicitudes; integración conecta modos e imprime resultado sin fabricar dependencias. --forzar solo permite iniciar; no cambia el resultado del verificador.

## integración → equipo

Operaciones conceptuales: iniciar historia(base,K), registrar(cambios,frontera), consultar_t(t), consultar_accion(k), recortar(frontera), exportar/importar. Todas salvo registro/recorte/importación son lecturas de historia; ninguna consulta altera el juego. Resúmenes usan exactamente los mismos campos en consola y replay.

Errores diferenciados: sintaxis inválida, instante futuro, acción inexistente, incompatibilidad, corrupción y ausencia de datos históricos. Nunca modificar parcialmente la partida después de un error.

## Comandos

| Entrada | Resultado |
|---|---|
| historia 250 | Resumen tras eventos <=250, antes de decisión coincidente |
| historia #3 | Resumen antes de tercera acción vigente |
| mapa | Proyección filtrada de conocimiento; nombre definitivo a coordinar con interfaz |
| ir a 7 | Delegar viaje de conocimiento; ID ilustrativo, no dato de cripta codificado |
| --checkpoint-cada 50 | Configurar K positivo |
| --replay archivo --hasta 250 | Resumen sin vista; aviso si terminó antes |
| --verificar identificador | Solo reporte de verificador, sin vista |
| --forzar | Permitir inicio no resoluble tras reporte |

Los ejemplos son sintaxis, no capacidades ya disponibles.


Fronteras, errores y retroceso se rigen por Assumptions de spec.md. No quedan preguntas de diseño abiertas para desarrollar el núcleo; cualquier cambio posterior se especifica y confirma antes del código.


## API independiente ya disponible

`LineaTiempo.exportar() -> HistoriaGuardada`; `LineaTiempo.desde_guardado(registro) -> LineaTiempo`. Los registros son inmutables; la importación no cambia una instancia viva. `datos.historia_binaria` ofrece codificar/decodificar a bytes y guardar/cargar por ruta; comparte ErrorGuardado, GuardadoCorrupto y FormatoIncompatible con la capa de datos existente. El fragmento CRLH es distinto de una partida CRPT y no reemplaza su lector. El adaptador posterior debe incluir identidad/versiones y todos los campos necesarios del motor en el formato integrado.

## Protocolo de consumo implementado por D

Este protocolo se verificó con un productor de prueba y queda por confirmar
contra las interfaces de A y C:

- El motor entrega `estado_historico_inicial() -> EstadoHistorico` y
  `conectar_historia(linea)`. Una acción aceptada entrega tiempo de cierre,
  cambios inmediatos y eventos ordenados por tiempo/secuencia a
  `linea.registrar_accion`; la decisión se publica después de cerrar el lote.
  Una acción terminal instantánea usa `terminal=True`.
- El productor comunica una reversión confirmada con
  `linea.recortar(cantidad, correcciones)`. Las consultas de D solo leen.
- La proyección mínima contiene `sala = (id, nombre)`,
  `jugador = (vida, vida_max, ataque, defensa, velocidad)` y `efectos`
  como tupla de etiquetas. `inventario:<orden>` contiene instancia, tipo
  y equipamiento, y `enemigo:<instancia>` tipo, vida, máximo y comportamiento.
  Los campos `mapa:<id>` provienen del conocimiento filtrado. La marca
  `conocimiento` distingue un mapa vacío de un proveedor ausente.
- `restaurar_estado_con_historia(estado, linea)` confirma en una sola
  operación el estado del motor, el conocimiento y el receptor nuevo.
  D verifica versión, CRC, reloj y ordinal antes de invocarla.
- C expone `mapa_conocido()` como secuencia de líneas ya filtradas y
  `viajar_hasta(destino, mover)` que devuelve el motivo. El callback
  `mover(direccion)` devuelve si el paso fue aceptado. D registra cada
  paso en la bitácora y la orden como comentario.
- B expone `red.verificacion.verificar_cripta` y
  `utilidades.bench_resolubilidad.medir_resolubilidad`. D muestra el
  dictamen, las llaves, la frontera y el testigo de ciclo. Sin verificador
  se informa `no_completada`, distinto de un dictamen negativo.

La rama no contiene cambios de este incremento en el código del motor de A
ni en algoritmos de B o C.

## Consumo de C tras su integración (2026-11-10)

D acepta también la proyección estructurada de `ConocimientoMapa.mapa_conocido()`:
`(id, estado, nombre, salidas)`, con salidas `(direccion, destino, costo, puerta,
recuerdo)`. El controlador presenta solo los datos filtrados entregados por C;
las salas avistadas muestran únicamente ID y estado. No consulta el terreno
real para completar nombres, puertas ni salidas.

El resumen histórico consume `conocimiento:sala:<id>` y
`conocimiento:puerta:<id>` de C, además de las claves anteriores de D. Presenta
los recuerdos correspondientes al instante consultado, sin leer conocimiento
vivo. Como los deltas de C no incluyen nombres ni topología, la historia muestra
identificadores y estados. El inventario de C usa `inventario_estado` y
`inventario_nodo:<instancia>`: D sigue los enlaces históricos para conservar el
orden real, identifica equipo/cursor y rechaza enlaces incompletos o cíclicos.
Si existe este inventario, prevalece sobre la proyección anterior, incluso vacío.

D añade `ResultadoAccion.hechos_paso: ResultadoPaso | None = None` al final del
registro, conservando las llamadas posicionales existentes. El controlador
guarda el resultado completo en `ultimo_resultado_accion` y mantiene el retorno
booleano de `_accion_modelo`. Lo reinicia antes de cada intento para no reutilizar
hechos de un paso previo tras una excepción. Esto prepara el consumo de viaje;
no captura ni deduce hechos del motor.

Continúan pendientes de A/C la captura de daño ocurrido y enemigos al entrar,
el proveedor de conocimiento durante la partida y su publicación en el mismo
lote histórico del motor. La ejecución de `ControlViaje` entre comandos y la
restauración conjunta se validarán después de esa entrega. T003, T010 y la
aceptación integrada permanecen abiertas; este incremento verifica consumidores
de D con los módulos reales de C, no una partida completa.
