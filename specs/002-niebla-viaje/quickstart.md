# Comprobar el incremento I1

Desde la raíz del repositorio, después de implementar las tareas:

```powershell
.\.venv\Scripts\python.exe -B -m unittest tests.test_conocimiento -v
.\.venv\Scripts\python.exe -B -m utilidades.bench_conocimiento
```

Se espera que las pruebas comprueben mapa filtrado, memoria independiente y reconstrucción/reversión sin red ni vista. El benchmark local separado no sustituye la futura conexión a `--bench` de D ni acredita el límite del viaje.

El juego todavía no consume el componente. No aparecerá el mapa nuevo en la interfaz por ejecutar main. El contrato local está en data-model.md; la adaptación a A/D sigue en contracts/propuesta-integracion.md. Q1 no se implementa.
