# Revisión del botón Viajar — 17 de noviembre de 2026

Base publicada: `95ba7b6`. Solicitud de Belén: corregir las contradicciones del estado documental y revisar Viajar, dejando fuera los dos puntos históricos indicados en la conversación. No se modifica código de producción, reglas, recursos ni formatos.

## Resultado

No se reprodujo un fallo del botón. **55 pruebas dirigidas en 25.129 s, OK, sin fallos, errores ni omisiones.** [Salida completa](evidencia-viaje-2026-11-17.txt). Incluyen selección de sala explorada, entradas inválidas y destinos no permitidos, cancelación con botón/Escape/cierre, conservación de estado y archivos al cancelar, recalcular rutas, memoria de puertas y detención por daño/enemigos/falta de ruta/llegada. Se mantienen las comprobaciones de carga, retroceso e historia integradas.

La regresión nueva `test_vd01_boton_dialogo_y_dos_pasos_reales_sin_teletransporte` pulsa el botón real, recorre el diálogo real con controlador/motor offline, cancela sin mutación y después viaja desde 100 hasta 102 pasando por 101. Comprueba el incremento de reloj de 250 por paso, la llegada, el aviso visible y los dos movimientos individuales del log. El primer intento de esta prueba buscaba el aviso en el registro de eventos; se corrigió para leer la banda visible `var_aviso`, donde la aplicación lo presenta. No fue un defecto de producción ni se cuenta el intento fallido como aprobado.

La selección anterior a la prueba nueva pasó 54 casos en 21.848 s. Se solapa con las 55 finales y no se suma a ellas ni a las 881 de la regresión integral previa. Esta revisión no repite suite completa, benchmarks ni API porque no cambia producción.

```text
python -B -X utf8 -m unittest tests.test_destino_viaje tests.test_controlador_viaje tests.test_viaje tests.test_detencion_viaje tests.test_viaje_motor tests.test_hechos_paso_motor tests.test_controlador_ac_real -v
```

Entorno: Python 3.14, Windows, Tk/Pillow disponibles, audio desactivado y TEMP/TMP en carpeta de ensayo escribible.

## Comprobación nativa

Se abrió una partida sintética aislada del fixture offline existente, sin tocar las partidas abiertas de la usuaria. Las salas se exploraron mediante movimientos ordinarios antes de la comprobación.

- Origen: sala 100, reloj 1025. Abrir Viajar mostró las salas exploradas 100/101/102 y señaló la posición actual.
- Escape cerró el diálogo conservando sala 100 y reloj 1025.
- Al reabrir, seleccionar 102 completó el campo de destino. El botón Viajar ejecutó los pasos 100→101→102; terminó en reloj 1525 y mostró «Viaje detenido: destino alcanzado».
- El aviso de detención se muestra en la banda sobre los controles; el registro inferior conserva los movimientos. No se espera un teletransporte ni la apertura automática de puertas.

Se cerró únicamente la ventana de ensayo. Los escenarios de peligro y puertas se verificaron en las pruebas automatizadas; no se atribuyen a la ruta nativa sin enemigos de este ensayo.

## Estado documental

`ESTADO_ENTREGA.md` distingue publicación comprobada, resultados vigentes y registros anteriores. Se retiran del encabezado vigente las afirmaciones «sin integración a main» y «API real sin repetir», y la tabla de opciones se actualiza con las ejecuciones de cierre ya conservadas. Los registros fechados anteriores mantienen su condición histórica. Los puntos históricos excluidos por Belén y el borrador local para el profesor no se modifican.
