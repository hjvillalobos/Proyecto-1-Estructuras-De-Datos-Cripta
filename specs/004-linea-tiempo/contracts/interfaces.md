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
