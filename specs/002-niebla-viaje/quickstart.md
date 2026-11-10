# Comprobar el incremento I1

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
