# Comprobación inicial de C

Fecha: 2026-11-08. Base: 544090a, igual a origin/main tras fetch y avance directo. No contiene las implementaciones aún no integradas de las ramas de A/B/D.

Comando ejecutado con `CRIPTA_SIN_AUDIO=1`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_transicion_salas tests.test_inventario tests.test_historial tests.test_rastro tests.test_enemigos tests.test_regresiones_juego tests.test_juego tests.test_precarga_offline tests.test_sesion_datos -q
```

Resultado: 125 pruebas, 18.220 segundos, OK. Es una selección de regresión de la base; no es la suite completa, una prueba de la interfaz en ejecución ni evidencia de cumplimiento de Parte II. No se ejecutaron benchmarks.

Se verificó que el archivo local de puntajes contiene exactamente las entradas de HEAD seguidas de las 16 entradas locales conservadas. Respaldo adicional local y stash retenidos. Los puntajes no forman parte del trabajo documental de C.

Fases: specify en borrador; clarify pendiente; plan/tasks/analyze/implement no iniciadas. No se afirma que las propuestas de contratos estén aprobadas por otros integrantes.

## Incremento independiente I1

Estado posterior al registro inicial: alcance I1 aclarado y autorizado por el usuario, plan y ocho tareas revisados antes de implementar. Commit de documentación previo: `fa5418a`. Revisión de consistencia: FR-001–005, FR-014 local, FR-017 local y PR-002 cubiertos; sin tareas ajenas al alcance. El resto de requisitos permanece explícitamente fuera de I1. No se considera aprobada la integración por otros integrantes.

Se añadieron `modelo/conocimiento.py`, `tests/test_conocimiento.py` y `utilidades/bench_conocimiento.py`. No se modificó ningún módulo existente del juego. El modelo no importa motor, red, archivos, vista ni tipos históricos de una rama no integrada.

Pruebas: las pruebas iniciales fallaron por ausencia del módulo; después de implementarlo, las 16 pruebas nuevas y las 125 de regresión seleccionadas pasaron: **141 pruebas, 16.928 s, OK**. Se utilizó el comando inicial añadiendo `tests.test_conocimiento`. No es la suite completa ni una prueba de interfaz integrada. Revisión AST del módulo: sin dict/set, sorted ni list.sort; se reutiliza ordenamiento por fusión propio. `git diff --check` sin errores.

### Medición local reproducible

Comando: `python -B -m utilidades.bench_conocimiento`. Python 3.12.10, Windows-11-10.0.26300-SP0. Cadena sintética sin puertas, IDs separados por 1009; carga determinista sin azar (semilla no aplica), 2000 repeticiones por tamaño. Cada entrada procesa dos salidas y genera dos cambios. No incluye red ni renderizado. Tiempo de preparación separado; tiempos de operación son medias, no máximos garantizados.

| Salas | Preparación ms | Entrada µs | Inversión µs | Consulta µs |
| --- | --- | --- | --- | --- |
| 100 | 1.124 | 4.686 | 4.567 | 1.521 |
| 1000 | 13.561 | 5.212 | 5.560 | 1.991 |
| 10000 | 201.690 | 6.074 | 7.024 | 2.701 |

La prueba de localidad comprueba el mismo número de accesos al estado para una entrada de igual grado con 10 y 10000 salas e impide iteración global del estado durante esa operación. No se afirma tiempo constante: resolver un ID tiene costo logarítmico. La preparación y la proyección del mapa sí dependen del tamaño total. La integración de estas mediciones en `--bench` y DECISIONES.md queda para la entrega coordinada, sin atribuir ese trabajo como terminado.

### Límites de la entrega

Sin antorcha, viaje, guardado, integración histórica, modificación de inventario ni conexión al juego. Q1 sigue abierta. El llamador garantiza que una observación corresponde a la posición actual; el componente valida extremo y exploración, pero no duplica el estado de posición del motor. Los IDs de puertas son explícitos del adaptador, no una identidad inferida por C. Aplicar deltas requiere esqueleto compatible. La validación de ese contrato interno no decide las reglas de la API de B.
