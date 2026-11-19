# Replay, personajes, offline y rendimiento — 18 de noviembre de 2026

Base publicada: `cb6a15c`. La revisión no modifica producción, preferencias personales ni partidas de la usuaria. Se añade una regresión y se aclara la documentación.

## Replay con ambos personajes

**42 pruebas dirigidas en 37.095 s, OK, sin fallos, errores ni omisiones.** [Salida](evidencia-replay-personajes-2026-11-18.txt). Incluyen replay gráfico/CLI, pausa/velocidad/detención/reinicio, selector y animaciones de personajes, sesión de datos, inicio offline y las dos pruebas del paquete oficial histórico.

La nueva prueba `tests.test_replay_personajes` renderiza con Tk y recursos reales la misma grabación con Tigre y Tigresa. Reproduce seis acciones y siete estados, incluyendo recoger, mover, retroceso, esperar y carga; comprueba imágenes distintas, apariencia correcta en todos los pasos, estado final e inventario/historia equivalentes, ausencia de HTTP y conservación del log/guardado originales. Solo se evita la espera entre pasos y el modal final; el renderizado sí se ejecuta.

La apariencia es una preferencia visual local. El replay usa la selección vigente al abrirlo; no conserva una elección de personaje en el log. Esta es la semántica del incremento original, ahora descrita en README.

```text
python -B -X utf8 -m unittest tests.test_replay_personajes tests.test_replay_grafico tests.test_replay_reinicio tests.test_personajes.TestPreferenciaPersonaje tests.test_personajes.TestSelectorYAnimaciones tests.test_sesion_datos tests.test_modos_historia tests.test_criptas_api.TestPaqueteOficial -v
```

Requiere Tk/Pillow y `CRIPTA_PAQUETE_API` para el paquete histórico. TEMP/TMP escribibles y audio desactivado durante el ensayo. El conjunto se solapa con la suite integral anterior de 881; no se suman los conteos. No se repitió la suite integral porque no cambia producción.

## Datos offline disponibles

Se copió la caché actual a una carpeta de ensayo y se bloquearon las peticiones HTTP mediante una aserción. [Resultados por cripta](evidencia-offline-2026-11-18.json):

| Cripta | Dictamen | Comprobación |
|---|---|---|
| 02 | Resoluble | 20 salas cargadas y acción ordinaria aceptada. |
| 03 | Resoluble | 40 salas cargadas y acción ordinaria aceptada. |
| 04 | Resoluble | 50 salas cargadas y acción ordinaria aceptada. |
| 05 | No resoluble | Bloqueo normal esperado; no se inicia ni se alteran llaves/mapas. |
| 06 | Resoluble | 300 salas cargadas y acción ordinaria aceptada. |

Cero solicitudes de red en las cinco comprobaciones. El catálogo seleccionado en esta copia actual es compatible; el antecedente del 17 de noviembre sobre un puntero `cat1` describe otra condición de la caché de aquella fecha. Offline exige datos previamente descargados, completos y de las versiones correctas. El primer intento del script de auditoría no añadía la raíz del proyecto a `sys.path`; se corrigió antes de obtener estos resultados. No fue un fallo de la aplicación.

## Procesamiento

Python 3.14.6 en Windows, semilla 20261001. Mediciones secuenciales, sin suite ni GUI concurrentes, sobre `cripta-06@f9ed9afa683d`, 300 salas. Los 30 cazadores, puertas abiertas y mapa completo son la preparación experimental declarada del benchmark.

| Operación | Máximo medido | Límite | Excesos |
|---|---:|---:|---:|
| Ciclo integrado | 10.652 ms | 20 ms | 0/60 |
| Resolubilidad incremental completa | 8.733 ms | 200 ms | 0/60 |
| Consulta de paso conocido | 2.413 ms | 5 ms | 0/60 |
| Historia K=50, 5.000 acciones | 2.0221 ms | 50 ms | 0/111 |

[Benchmark integrado/resolubilidad](evidencia-rendimiento-2026-11-18.txt) · [Historia, valores de K y alternativas](evidencia-historia-rendimiento-2026-11-18.txt). La preparación offline tuvo máximo 30.135 ms y cero solicitudes. La alternativa sin controles conserva excesos (máximo total 101.9904 ms y 51/111 sobre 50 ms); no es la estrategia elegida.

```text
python main.py --bench --subsistemas parte-dos resolubilidad --paquete .cache/entrega-completa --cripta cripta-06 --repeticiones 60
python main.py --bench --subsistemas historia --operaciones 5000 --salas 300 --repeticiones 3
```

## Presentación y documentación

La medición visual se ejecutó después, con Tk oculto y caché visual aislada, conservando recursos y proveedor reales. [Datos de ambos personajes](evidencia-rendimiento-personajes-2026-11-18.json). Portada: primera carga 627.405/606.557 ms; alternar personajes con retratos en memoria 1.322/1.518 ms. Trabajo por tic, mediana 0.293/0.257 ms y máximos 3.042/2.680 ms. Las cachés mantienen sus límites. La preparación inicial de un grupo completo de equipo tiene medianas 787.945/573.271 ms; la reutilización en memoria, 0.050/0.036 ms.

La cadencia de callbacks no es exactamente 20 ms: sus máximos fueron 34.535/33.459 ms. La medición visual no certifica GPU, fluidez perceptiva o latencia absoluta del sistema. Los límites de la tabla anterior corresponden a procesamiento sin renderizado.

Se comprobaron 16 documentos principales (README, estado, decisiones, bitácora y spec/plan/tasks de las cuatro capacidades): 185 enlaces locales, ninguno roto antes de añadir este informe. Los enlaces nuevos se verifican también antes de publicar. README ahora explica selección cosmética, apariencia del replay, condiciones offline y detalle histórico, y marca el resultado de 828 pruebas como antecedente fechado. Los puntos históricos excluidos por Belén permanecen fuera de esta revisión.
