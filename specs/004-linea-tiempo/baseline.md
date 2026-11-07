# Base de pruebas — 2026-11-02

Base Git: origin/main 03716b2; rama documental 004-linea-tiempo. Python del runtime Codex.

1. `python -m unittest discover -v`: ejecución completa interrumpida después de atascarse en pruebas gráficas. Antes de interrumpir, test_redibujar_menu_crea_animacion_nueva_y_destruirlo_la_cancela registró FAIL y aparecieron mensajes Tcl de aplicación destruida. No hay resultado final válido de la suite completa; causa exacta del fallo gráfico no diagnosticada. No se afirma que sea un defecto del programa.
2. Núcleo seleccionado, primer intento aislado: 134 casos, 42 errores; acceso denegado a temporales y dependencia ausente. Ese resultado no mide corrección del motor.
3. Repetición fuera del aislamiento: 134 casos, 133 aprobados y 1 error de importación, `requests` no instalado para tests.test_cliente_api. Sin fallos de aserción entre los casos restantes. No equivale a suite completa aprobada.

Comando de la repetición:

```powershell
python -m unittest tests.test_juego tests.test_historial tests.test_inventario tests.test_enemigos tests.test_rastro tests.test_cache tests.test_catalogo tests.test_cliente_api tests.test_regresiones_juego tests.test_fallos_transaccionales -v
```

Para completar la base: preparar un entorno del proyecto con requirements.txt, repetir cliente API con requests disponible y diagnosticar la prueba gráfica en sesión interactiva. No se instaló ninguna dependencia global ni se alteraron pruebas existentes. Se puede comenzar el núcleo sintético; antes de integrar deben resolverse y registrarse estos resultados.

Evidencia textual local de esta sesión: `C:/Users/Belén/Documents/New project/tmp/pruebas-base-linea-tiempo.txt`, `pruebas-nucleo-linea-tiempo.txt` y `pruebas-nucleo-linea-tiempo-verificadas.txt` en la misma carpeta. Los logs no se incorporan como datos de juego al repositorio.


## Primer incremento de código — 2026-11-02

`python -m unittest tests.test_linea_tiempo -v`: 14 pruebas aprobadas. Incluye igualdad de resultados hasta 5000 acciones y conteo <=K; no mide latencia ni certifica el límite de 50 ms.

Regresión seleccionada fuera del aislamiento por acceso a temporales: `python -m unittest tests.test_linea_tiempo tests.test_juego tests.test_historial tests.test_inventario tests.test_enemigos tests.test_rastro tests.test_cache tests.test_catalogo tests.test_regresiones_juego tests.test_fallos_transaccionales -q`: 147 pruebas aprobadas, 5.255 segundos en esta ejecución. No incluye cliente API con requests ausente ni la suite gráfica completa.

`python -m tests.demo_linea_tiempo`: ejecución correcta. Son pruebas del núcleo y demostración, no una partida integrada ni benchmarks de producción.


## Persistencia independiente — 2026-11-02

31 pruebas de historia/persistencia, incluidas 17 de persistencia: ida/vuelta de valores y eventos, K, checkpoints regenerados, correcciones y rama vigente, continuación y random.Random de prueba; historia de 5000 acciones; DTO inválido; truncamientos, CRC, etiquetas, UTF-8, enteros, reales y conteos inválidos; profundidad; versión futura y CRPT; escritura/carga y fallo de reemplazo conservando destino.

Regresión seleccionada fuera del aislamiento: `python -m unittest tests.test_linea_tiempo tests.test_persistencia_historia tests.test_juego tests.test_historial tests.test_inventario tests.test_enemigos tests.test_rastro tests.test_cache tests.test_catalogo tests.test_regresiones_juego tests.test_fallos_transaccionales -q`: 164 pruebas aprobadas en 3.742 s. Duración de suite, no benchmark de historia. El primer intento aislado se detuvo al escribir temporales y se interrumpió; el resultado reportado corresponde al intento fuera del aislamiento.

No se certifican suite gráfica, red con requests ausente, guardado integrado ni límite de consulta de 50 ms.


## Manejo de errores — 2026-11-02

8 pruebas nuevas en tests/test_errores_historia.py: clases compatibles, entrada/referencia/incoherencia diferenciadas, atomicidad, campo ausente, ruta/tipo inválidos, corrupción/incompatibilidad, permisos y limpieza que preserva causa principal. Total de errores/historia/persistencia: 39.

Comando: `python -m unittest tests.test_errores_historia tests.test_linea_tiempo tests.test_persistencia_historia tests.test_juego tests.test_historial tests.test_inventario tests.test_enemigos tests.test_rastro tests.test_cache tests.test_catalogo tests.test_regresiones_juego tests.test_fallos_transaccionales -q`. Resultado fuera del aislamiento para temporales: 172 pruebas aprobadas, 4.813 segundos. Es duración de suite, no benchmark; suite gráfica y cliente API no incluidos.

## Incremento de integración D — 2026-11-07

Base de implementación: a7acb0e en 004-linea-tiempo. El registro del
diseño precede al código en ce72074 y 75c55d9. Se comprobó el checklist
de requisitos (8 completos) y se analizaron FR-001–FR-020 frente al plan
y la constitución. Se contrastaron §§2.11 y 4.10–4.11 de Parte I con la
transcripción existente del enunciado, además del PDF de Parte II.

La regresión seleccionada se ejecutó con Python 3.14.6, requests 2.34.2
y Pillow 12.3.0. Pasaron 202 pruebas de historia, guardado, comandos,
replay, motor, verificación de CLI, cache offline y cliente API. El
benchmark de guardado v4 se verificó después con 15 pruebas de medición
e integridad de archivos. Los casos reales y simulados están distinguidos
en aceptacion.md.

La ejecución completa por descubrimiento se interrumpió después de que
quedó sin avanzar en el diálogo Tk de nombre de puntaje. La continuación
por módulos permitió probar el resto. Quedaron el fallo ya documentado
de redibujo de menú y dos errores de fixtures antiguos que construyen
VistaGrafica sin escena y MenuInicio sin canvas ni precarga. También se
detectaron dos regresiones de prueba en rutas cortas de Windows y en el
nuevo flujo de verificación. Se ajustaron sus escenarios de CLI y pasaron
en la regresión de 202. El caso opcional con paquete oficial quedó omitido.
No se declara aprobada la suite completa ni la aceptación con A/B/C.
