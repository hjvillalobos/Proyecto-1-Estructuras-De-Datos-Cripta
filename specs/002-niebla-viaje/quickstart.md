# Comprobar el incremento I1

## I5: control de viaje (2026-11-10)

Ejecutar `python -B -m unittest tests.test_viaje -v` para las ocho pruebas del protocolo local. Ejecutar `python -B -m utilidades.verificar_conocimiento_rutas` para las 32 pruebas con rutas reales de A (sustituye el total de 23 indicado en la entrada histórica de I4). Hay casos compartidos; no sumar cifras como pruebas únicas.

Uso propuesto para el controlador: construir ControlViaje(planificador); iniciar(origen,destino); proponer() devuelve PasoViaje o None. Ejecutar un movimiento ordinario por separado; actualizar conocimiento y, tras cerrar eventos, entregar registrar_resultado(paso.numero, ResultadoPaso(...)). Consultar causas antes de ofrecer otro paso. No ejecutar en un bucle bloqueante de interfaz. Cancelar antes de aplicar pergamino/restauración; iniciar otra vez solo por orden expresa. Una propuesta cancelada no debe ejecutarse: el controlador debe comprobar que sigue pendiente antes de mover. El componente no puede deshacer un movimiento que un consumidor ejecute indebidamente tras cancelar.

El resultado exige posición, aceptación, daño ocurrido, entrada, enemigos al entrar y fin de partida. No son datos deducibles todos del booleano del callback actual de D. El contrato sigue pendiente de acuerdo; no hay conexión automática al juego, guardado o replay.

Desde la raíz del repositorio, después de implementar las tareas:

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_conocimiento -v
.\.venv\Scripts\python.exe -B -m utilidades.bench_conocimiento
```

Se espera que las pruebas comprueben mapa filtrado, memoria independiente y reconstrucción/reversión sin red ni vista. El benchmark local separado no sustituye la futura conexión a `--bench` de D ni acredita el límite del viaje.

El juego todavía no consume el componente. No aparecerá el mapa nuevo en la interfaz por ejecutar main. El contrato local está en data-model.md; la adaptación a A/D sigue en contracts/propuesta-integracion.md. Q1 no se implementa.

Validación realizada: 16 pruebas específicas pasan. El benchmark anterior se ejecutó; valores y entorno en baseline.md. `mapa_conocido()` devuelve datos inmutables, no la secuencia de líneas que espera la fachada de D: se conserva explícitamente esa frontera para su futura adaptación.

## Ampliación I2

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_conocimiento tests.test_conocimiento_secuencias tests.test_detencion_viaje -v
.\.venv\Scripts\python.exe -B -m tests.demo_conocimiento
.\.venv\Scripts\python.exe -B -m utilidades.bench_conocimiento
```

La demostración muestra cinco estados: inicio, puerta observada abierta, entrada a la vecina, puerta observada cerrada desde el otro extremo y restauración del inicio. Incluye una aserción de igualdad final. No solicita red, no guarda archivos ni modifica partida/puntajes. No se añadió interfaz gráfica.

Las 23 pruebas específicas pasan; una prueba recorre 64 combinaciones de hechos y otra 1000 operaciones deterministas. La decisión de detención no ejecuta ni mantiene un viaje: la futura integración deberá entregar hechos válidos y conservar la cancelación entre pasos. El benchmark añade memoria y proyección; no confundir la proyección completa con el cálculo de un paso.

## I3: comprobar compatibilidad con historia

```powershell
.\.venv\Scripts\python.exe -B -m utilidades.verificar_conocimiento_historia
```

Requiere Git y el objeto de D `02da6b6f159b28279e3fe7dc5177c97c16898f42` disponible localmente (obtener referencias mediante fetch si falta). El verificador copia archivos versionados concretos de D y archivos de trabajo de C a una carpeta única bajo .cache; no fusiona ni sobrescribe ramas. Ejecuta las 14 pruebas de historia y las cinco de conversión con los tipos reales. Debe terminar con 19 pruebas y cero omisiones; no hay dobles de LineaTiempo.

En una ejecución directa de discovery sobre la rama de C, la clase de pruebas de integración informa una omisión explícita si no existe modelo.linea_tiempo. Esa omisión no acredita integración: usar siempre el comando anterior para comprobarla. La copia conserva fuentes para inspección, no se versiona.

`campos_iniciales(mapa)` crea una base única. `convertir_cambios(lote)` produce tipos de D; requiere que esos tipos estén presentes y no registra acciones. Las claves propuestas conservan grado de conocimiento y recuerdos; no incluyen la proyección de nombres/salidas que espera el resumen visual. No conectar directamente a la interfaz ni al binario sin confirmar ese contrato con D.
# I4: verificación de rutas conocidas

Ejecutar `python -B -m utilidades.verificar_conocimiento_rutas` desde la raíz; añadir `--bench` para diagnóstico sintético. Requiere el objeto Git de A 9730482d4c6e33e5ba39e6eeb6f76d1f19b4220c. Copia únicamente rutas.py de A junto con los componentes de C a .cache. No conecta movimiento, no modifica ramas ni usa red. Las pruebas directas sin rutas.py informan omisión explícita; usar el verificador para acreditar este incremento.

Resultado comprobado: 23 pruebas sin omisiones (16 de conocimiento y siete nuevas de rutas, una con 60 grafos de semilla 927). Con A integrado, `PlanificadorConocido(mapa).consultar(origen, destino)` devuelve un paso propuesto o el motivo de no producirlo; no mueve al jugador. Conservar el planificador mientras viva el mismo mapa, incluso al revertir sus deltas. Reconstruirlo si se sustituye el mapa completo. No modificar el conocimiento durante una consulta.
