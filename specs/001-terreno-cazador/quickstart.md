# Guía de validación prevista — provisional

**Fecha:** 2026-11-02. No se ejecutó ningún test ni benchmark durante Plan. No hay implementación nueva ni suites T1–T7 creadas. Esta guía separa comandos existentes de escenarios futuros para no afirmar ejecutabilidad inexistente.

**Estado documental al 2026-11-05:** Plan provisional, 51 tareas y dos revisiones Analyze disponibles; correcciones documentales I1/I5/C2 de la segunda revisión incorporadas, sin nueva ejecución de habilidades. Ninguna tarea de implementación ejecutada por esta sesión. Q1–Q3 y contratos E-* pendientes. Mantener esta fecha de actualización separada de la fecha histórica de creación.

## Prerrequisitos

Python ≥3.11, entorno reproducible según README y dependencias del proyecto; Spec Kit 1.2.3/Codex para proceso. Antes de ejecutar pruebas en fase autorizada: comprobar rama/estado según reglas del usuario, disponer de permisos para archivos temporales de pruebas y no incluir datos locales. No instalar ni modificar dependencias por este documento.

La documentación puede actualizarse con autorización G-DOC, sin necesitar Implement. Código y ejecución de pruebas/benchmarks requieren permisos posteriores G0/GA, spec confirmada antes del código y revisión vigente de las correcciones; una edición documental no libera Q1/Q2 ni entregables E-*. Q3 pendiente no se convierte en referencia sintética oficial. Los borradores de cierre se permiten, pero T047–T050 solo se completan con sus prerrequisitos y evidencia final; el paquete local no significa actualización de DECISIONES.md/README.md.

Para integración, T013/T014 esperan E-B-COSTOS sin esperar E-B-RANGO; T025 requiere ambos y E-C-DESPACHO. Tras autorización futura, una ejecución parcial de las pruebas del núcleo puede registrarse con suites omitidas/motivo, sin completar T027. Su cierre total exige T024/T025/T026, contratos/permisos aplicables y las tres suites incluidas en T027. La [comunicación de B](research.md#comunicación-reportada-de-b-sobre-openapi-110) es evidencia indirecta, sin copia primaria: no habilita pruebas que prescriban políticas de rango ausente/null, costo null o inconsistencias. El profesor sigue sin responder Q1/Q2; esto no impide registrar o corregir documentación autorizada.

## Comandos existentes para ejecución posterior autorizada

Desde raíz del proyecto, estas suites ya existen; pueden generar archivos temporales y por ello NO se ejecutaron en Plan:

```powershell
python -B -m unittest tests.test_juego tests.test_enemigos tests.test_rastro tests.test_historial
python -B -m unittest tests.test_regresiones_juego tests.test_integridad_operaciones tests.test_fallos_transaccionales
python -B bench.py --subsistemas agenda ciclo --sin-disco --eventos 256 --salas 100 --operaciones 10000 --repeticiones 5 --semilla 20261001
```

Las cifras del comando son una carga sintética de comparación propuesta, no la cripta oficial ni la cantidad exigida de cazadores. bench.py todavía no ofrece comparaciones de rutas/cazadores: el comando actual solo sirve como base histórica a volver a medir. La integración de nuevos subsistemas es de D con funciones de A, y se acordará sin inventar flags como si existieran.

## Diseño de nuevas pruebas T1–T7

Los nombres propuestos de suites y utilidades están en tasks.md (T006–T046); GA mantiene pendiente la autorización de sus rutas. Ninguna prueba se escribe ahora. Construir grafos sintéticos con arreglos propios, sin incorporarlos como datos reales del juego. Cada futura prueba cita FR/NFR y su tarea correspondiente. La existencia de tasks.md no acredita ejecución.

| Caso | Preparación sintética y acción | Resultado a comprobar | Requisitos |
| --- | --- | --- | --- |
| T1 | Cazador activo en sala diferente; ninguna ruta abierta | Esperar costo 100, sin cambiar posición ni abrir puertas | FR-007–009 |
| T2 | Mejor ruta costo 101, rango suministrado 100 | Esperar costo 100; caso de igualdad en A4 sí avanza | FR-008–009 |
| T3 | Camino de 2 arcos costo 500 frente a 3 arcos costo 300, rango 300 | Primer paso del camino de 300; cobrar solo el arco usado | FR-008–009 |
| T4 | Primeros vecinos 7 y 3 con igual costo total mínimo | Elegir 3 pese a orden de enumeración; incluir convergencias y costo inmediato mayor del vecino óptimo | FR-010,014 |
| T5 | Decidir, cerrar puerta real entre turnos, volver a decidir | Igual a referencia desde cero; probar alternativa y ausencia de ruta | FR-013 |
| T6 | Costo 1, velocidad 1000, movimiento en t=20 | Posición cambia ahora, próxima acción t=21 | FR-002–003 |
| T7 | Costo 250, velocidad 100, próxima acción 250; cambio en t=50 a 200 | Próxima acción t=150, nueva secuencia, sin ejecución duplicada; repetir ralentización y final de efecto | FR-005–006 |

## Regresiones y escenarios adicionales

- A1–A2: ausencia de costo=100 y costo válido en ambos sentidos; todos los actores y demás costos inalterados. No probar política de datos inválidos hasta resolver Q1/Q2.
- A3–A5: mismo cuarto ataca; igualdad de rango avanza; resultado independiente de conocimiento y contenidos descargados. Contar cero llamadas de red desde búsqueda mediante contrato aprobado, no mock añadido unilateralmente.
- A6–A8: apertura puede mejorar ruta; jugador cambia objetivo; muchos caminos empatados/ciclos positivos; eventos simultáneos ordenados por secuencia. Dos ejecuciones con igual semilla/versiones/acciones producen mismos estados y llamadas al azar.
- A9–A11: activación inicial/costo 100 e IDs ordenados; precarga no activa; puerta no desplaza actor al cerrar; muerto no actúa; antídoto cancela pulsos; regeneración y cura limitadas; trampa inmediata y rearme; intervalos de efectos heredados.
- A12: undo y fallo transaccional restauran eventos/identidades/contador/reloj/azar, excluyen pergaminos e infraestructura de caché y descartan derivados de ruta. C/D acuerdan persistencia sin que A implemente su historia.
- A13: rastro fresco <400 y desempate menor ID; rastro por acción; guardián espera sin jugador. Preservar decisiones de errante/rastreador, cambiando solo costo temporal.
- Puertas: probar observar/abrir/cerrar desde ambos extremos, incluidos cierres automáticos y rollback. Primero acordar representación con B/C; no dar por demostrada coherencia existente.
- Comparar con referencia independiente (selección lineal o enumeración de caminos simples en mapas pequeños), sin bibliotecas de grafos ni compartir el mismo heap para validar su propia corrección.
- Contrato propuesto con C: distinguir llegada sin movimiento, ruta válida, ausencia demostrada y agotamiento del límite sin inferir existencia fuera de él. FUERA_LIMITE requiere evidencia exacta vigente. Probar SIN_LIMITE solo sobre salas exploradas y puertas recordadas abiertas; no equivale a usar el grafo real completo. Los nombres y firmas requieren acuerdo con C antes de implementar.

## Matriz de mediciones obligatorias de A

| Eje | Comparaciones | Evidencia requerida |
| --- | --- | --- |
| Cazadores | Uno frente a muchos (decenas); mismo objetivo | Tiempo por decisión y ciclo completo; número de búsquedas |
| Rango | Pequeño/grande; región local fija con mapa exterior creciente | Salas/arcos examinados, inicialización/limpieza e índices, tiempo y memoria |
| Estrategia | Individual/compartida; heap indexado/repetidos y referencia lineal | Construcción, hits, fallos, reconstrucción, operaciones de heap y resultados iguales |
| Validez y reutilización | Recalcular siempre/última consulta/varias entradas acotadas; consultas repetidas y alternadas; puertas estables/inestables | Aciertos y fallos por reemplazo/invalidez, memoria residente/pico, invalidaciones, búsquedas ahorradas y costo total de mantenimiento, incluidas aperturas fuera del camino |
| Agenda P1 con carga nueva | Heap perezoso/candidato indexado; empates, cancelaciones y velocidad | N físico/válido, obsoletos, memoria y latencia al descartar acumulaciones |
| Integración | Ciclo entre decisiones, no evento aislado | <20 ms, sin red/renderizado y referencia oficial cuando Q3 se resuelva |

Las alternativas adicionales de heap/grafo son experimentos de diseño propuestos; los ejes oficiales uno/muchos, rangos, individual/compartido, reutilización/recálculo y estabilidad son obligatorios. Ningún experimento compartido puede ocultar violación de localidad. Un campo parcial ausente no prueba falta de ruta.

La base propuesta es individual limitada. El cálculo compartido se mide separado y no se activa automáticamente en producción; no hay umbrales aprobados. Para cachés usar exactamente las mismas consultas y cambios de estado en cada diseño, declarar sus capacidades y presupuestos de memoria y contar búsqueda de claves, inserción, reemplazo, liberación e invalidación. La caché de última consulta puede perder casi todos los resultados con cazadores alternados: un mal resultado suyo no demuestra que la reutilización en general no convenga.

## Protocolo de medición futuro

Preparar datos fuera de la región cronometrada de consulta, reportando por separado costo de preparación y memoria residente. Incluir dentro de consultas sus propias asignaciones, inicialización, limpieza, invalidación y reconstrucción. Medir invalidación lógica y costo físico de liberar/reutilizar capacidad. No excluir selectivamente el trabajo que hace mala una alternativa.

Usar cargas deterministas por semilla, mismos datos/acciones para cada estrategia, calentamiento documentado, repeticiones y variación (mínimo, mediana y máximo; número de repeticiones registrado). Registrar equipo, versión Python, tamaño, grado, rango y H; estos son controles experimentales propuestos, no nuevos umbrales oficiales. El reloj de medición real no decide eventos del juego. Medir tiempo y memoria en pasadas separadas si la instrumentación perturba resultados.

Reportar tablas inicialmente como «pendiente», nunca con números simulados. Mantener <20 ms y condiciones oficiales; Q3 impide certificar con una cripta sintética como si fuera oficial. Q1/Q2 bloquean pruebas de políticas de entrada todavía indefinidas.

## Cierre documental posterior

Publicar resultados finales y límites en DECISIONES.md solo con autorización, enlazando spec/plan y explicando cambios de preferencia motivados por medición. Registrar prompts íntegros en la bitácora compartida posteriormente. Esta guía no crea tareas ni autoriza ejecución o modificación de módulos ajenos.
