# Historia detallada — HU-02, 17 de noviembre de 2026

## Resultado

El botón Historia presenta un informe ampliado a partir de la referencia suministrada por Belén: reloj y número de acciones, resultado, sala, vida/estadísticas, enemigos derrotados, inventario numerado en su orden histórico, efectos, enemigos vivos de la sala y mapa con totales de exploradas/avistadas y detalle de nombres, salidas, costos y puertas recordadas. La ventana usa texto monoespaciado y desplazable, más espacio y un botón de regreso que permanece visible. El resumen utilizado por replay y consola se conserva.

Los objetos muestran nombre de catálogo, tipo, instancia y clase, además de equipo/selección/antorcha encendida cuando corresponde. «Usos» solo aparece si la ficha de esa versión declara ese atributo; el modelo no conserva un contador de usos restante por instancia, por lo que no se inventa el «1» de la captura.

## Datos históricos y privacidad

- El número de acciones se calcula desde la frontera que ya localiza la consulta, incluyendo la distinción entre un tiempo y el estado anterior a una acción.
- Las partidas nuevas registran derrotados/resultado en el campo de tamaño constante `estadisticas_partida`, mediante diferencias. No se añaden copias completas por acción ni se cambia el formato binario.
- Al cargar una historia anterior sin ese campo, se conserva su esquema al continuar y el informe muestra «no registrado» para esas estadísticas. Nunca usa los valores actuales para completar el pasado.
- Inventario y enemigos se leen del estado reconstruido. Las fichas residentes aportan nombres/clases estáticos de la versión de la partida, sin HTTP; si una ficha no está disponible en memoria, se conserva el identificador del tipo.
- El mapa combina topología inmutable con los niveles y recuerdos de la consulta. Una sala avistada no revela nombre ni salidas; una desconocida no aparece. Las puertas muestran el recuerdo pasado, nunca el estado real actual.

Especificación, plan y tareas confirmados antes del código en `8b6c13a`. Rama `004-linea-tiempo`; main sin modificar.

## Validación

Suite completa: **881 pruebas en 280.978 s, OK, cero fallos/errores, cuatro omisiones opcionales**. [Salida completa](evidencia-historia-detallada-2026-11-17.txt). Las omisiones corresponden a la clase de comparación histórica, los dos métodos de paquete oficial y API real; no se presentan como aprobaciones de esta ejecución ni se suman resultados anteriores.

Cuatro casos HU-02 comprueban inventario/equipo pasado, privacidad de nombres y puertas, pureza, derrotados antes/después de combate real, conservación binaria y guardado/carga, continuación de una historia sin el campo nuevo y resultado independiente del vivo. Las pruebas existentes cubren retroceso, corrupción, fronteras, replay y recorrido completo del botón con Tk real. La prueba del productor anterior se adapta únicamente al mismo campo observable nuevo; conserva su algoritmo de diferencias como referencia.

Durante la preparación se descartaron dos corridas parciales al alinear el esquema observable del productor de referencia y el orden de la clave nueva. La primera detectó la ausencia del campo adicional en esa referencia. Ninguna corrida parcial se cuenta como aprobación ni se suma a las 881 pruebas finales.

Comando de la regresión, con Python 3.14, Tk/Pillow disponibles, audio desactivado y TEMP/TMP escribibles:

```text
python -B -X utf8 -m unittest discover -s tests -t . -v
```

## Rendimiento

Medición sin suite ni GUI concurrentes, semilla 20261001, paquete local `cripta-06`, 300 salas. Preparación experimental del benchmark existente: 30 cazadores, mapa conocido y puertas abiertas. No representa una partida natural ni incluye renderizado.

| Operación | Máximo | Límite | Excesos |
|---|---:|---:|---:|
| Ciclo con 30 cazadores e historia/mapa | 10.453 ms | 20 ms | 0/60 |
| Consulta de paso conocido | 2.421 ms | 5 ms | 0/60 |
| Historia K=50, 5.000 acciones, 300 salas | 1.0886 ms | 50 ms | 0/111 |

Heap anterior/actual: medianas 3.3546/2.0800 ms, decisiones iguales. [Salida del benchmark integrado](evidencia-historia-detallada-bench-2026-11-17.txt).

Historia K=50 conserva 101 controles y reconstruye como máximo 50 acciones en la carga medida. La comparación sin controles alcanzó 101.4697 ms y 36/111 excesos, por lo que sigue siendo una alternativa descartada. [Comparación completa K=10/50/100/sin controles e inversa](evidencia-historia-detallada-bench-consultas-2026-11-17.txt).

Revisión nativa final sobre una reconstrucción aislada del log local: consulta de tiempo 300 muestra acciones 7, sala 3, vida 30/30, daga equipada y llave en orden histórico, antorcha y mapa con cuatro salas exploradas y una avistada. Se observaron las secciones legibles, el desplazamiento y el botón para volver visible. La copia de ensayo se cerró; no se modificó la partida original ni se incluyó su log en la entrega.

```text
python main.py --bench --subsistemas parte-dos --paquete .cache/entrega-completa --cripta cripta-06 --repeticiones 60
python main.py --bench --subsistemas historia --operaciones 5000 --salas 300 --repeticiones 3
```

Las mediciones no garantizan tiempos absolutos en otros equipos. No se repitió API real ni se modificaron datos de criptas.
