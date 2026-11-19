# Historia: diagnóstico y claridad de consulta — 17 de noviembre de 2026

## Síntoma y diagnóstico

Belén indicó que Historia mostraba siempre la misma información tanto por tiempo como por acción. Se revisaron el botón, la cola de comandos, la consulta del controlador y la reconstrucción histórica. La partida abierta de la usuaria estaba en la pantalla de derrota; no se reinició ni modificó. Las comprobaciones visuales se hicieron en ventanas de una partida sintética aislada.

La reconstrucción offline de la bitácora local de 61 acciones produjo estados distintos: tiempos 1/2/3, sala 1 y vida 30/30; acción #10, sala 3 y ataque 9/defensa 4; tiempo final 5355, sala 18 y vida 0/30. Las tres primeras acciones también compartían sala/vida, aunque inventario/equipo y tiempo pueden diferir. No se modificó ni incorporó esa bitácora de usuario a la entrega.

No se reprodujo una referencia ignorada por el motor. Sí se identificó una falta de contexto: el diálogo no mostraba el tiempo actual ni el rango de acciones, por lo que valores pequeños por tiempo o primeras acciones podían aparentar un resultado fijo. Además, en la ventana real el informe podía aparecer desplazado y el área de texto ocultaba el botón para volver.

## Cambio HU-01

- El diálogo muestra tiempo actual y número de acciones de la rama vigente. Sugiere el tiempo actual o la última acción al cambiar de modo, muestra rangos y rechaza valores futuros/inexistentes sin cerrar la consulta.
- Explica que tiempo y número de acción son referencias diferentes y que dos instantes sin cambios pueden devolver el mismo estado. La consulta por acción conserva el estado justo antes de ejecutarla.
- El título del resultado identifica la referencia elegida. El informe se centra dentro de la pantalla y reserva espacio para «Volver a la partida».
- El controlador entrega solo dos escalares de contexto al actualizar la presentación; no se añade reconstrucción histórica por turno. No se modifican motor, reglas, datos, API ni formatos.

Especificación/plan/tareas HU-01 confirmados antes del código en `056535c`. Cambios en `004-linea-tiempo`; sin integración a main.

## Validación

**100 pruebas dirigidas en 20.165 s, OK, sin fallos, errores ni omisiones.** [Salida completa](evidencia-historia-ui-2026-11-17.txt). Incluyen cuatro regresiones nuevas con Tk real: sugerencias/rangos, inicio sin acciones y reapertura, botón→diálogo→cola→controlador→informe con motor offline real, y posición/botón visible del informe. El recorrido integrado comprueba que las consultas no alteran estado ni log y que los límites se actualizan al actuar y guardar/cargar. Cancelación y restauración del bloqueo del diálogo conservan las pruebas anteriores.

Comando desde la raíz, con Python 3.14, Tk/Pillow instalados, audio desactivado y TEMP/TMP escribibles:

```text
python -B -X utf8 -m unittest tests.test_consulta_historia tests.test_comandos_integracion tests.test_controlador_ac_real tests.test_frontera_temporal tests.test_modos_historia tests.test_linea_tiempo tests.test_persistencia_historia tests.test_conocimiento_historia tests.test_controlador_viaje -v
```

Comprobación nativa adicional: botón Historia, tiempo 200 → sala 101/vida 28/30; nueva consulta por acción #2 → tiempo 100/vida 29/30. Tras el ajuste de disposición se observó el informe centrado, con texto completo y botón de regreso visible. Las dos ventanas de ensayo se cerraron; la partida original no se cerró. Se verificó `git diff --check`.

No se repitieron suite completa, API ni benchmarks: este resultado es un subconjunto y no se suma a las 873 pruebas del incremento anterior. La comprobación no permite atribuir una causa única al síntoma original sin sus referencias exactas, ni afirma que todas las referencias deban devolver valores distintos.
