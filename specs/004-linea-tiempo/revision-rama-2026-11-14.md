> Revisión anterior al fortalecimiento RF-01..03. El riesgo por maxID y los tiempos de rutas descritos aquí fueron tratados después; consultar ESTADO_ENTREGA.md y la última sección de DECISIONES.md.

# Revisión de la rama y decisiones pendientes — 2026-11-14

Base revisada: `004-linea-tiempo`, HEAD `7887e26`. La entrega de A `f8e10ef` es antecesora de HEAD (`git merge-base --is-ancestor`, salida 0); fue incorporada mediante `3bedd4a`. No se modificó producción durante esta revisión.

## Contraste con el enunciado

Se extrajo nuevamente el PDF local íntegro `Cripta - Parte II.pdf`, 13 páginas. Su texto coincide con la extracción previa. La revisión usa sus reglas, las especificaciones versionadas y las aclaraciones ya registradas; no convierte decisiones del equipo en respuestas del profesor.

| Área | Comprobación en la rama |
|---|---|
| Terreno y cazadores, §§3.1–3.2, 5.1–5.2 | Costos variables, mínimo temporal, rango inclusivo, desempate por menor vecino, búsqueda propia, puertas actuales y descarte de derivados tras restauración. Suite de rutas, localidad, velocidad, hechos del paso y restauración incluida en la regresión. |
| Conocimiento y viaje, §§3.3–3.4, 5.3 | Mapa filtrado, recuerdos de puertas, antorcha sin activar contenido remoto, rutas sobre conocimiento y detención por entrada/enemigos/daño. Cada paso conserva acciones, eventos, historia y retroceso. |
| Resolubilidad, §§3.5, 5.4 | Recorrido incremental, diagnósticos de frontera/ciclos, resultado determinista, bloqueo salvo `--forzar`, modo exclusivo sin vista y datos offline. La acumulación sin trayectoria única ya estaba aceptada según la aclaración registrada del 2026-11-02. |
| Historia, §§3.6, 5.5 | Consultas por tiempo/acción, empates de eventos, ausencia de efectos sobre la partida, recorte tras pergamino, K configurable, persistencia conjunta e incompatibilidad explícita. |
| Restricciones y proceso | Revisión de usos de estructuras/ordenamientos prohibidos en modelo, controlador, datos, red y utilidades; no se encontró sustitución de las estructuras evaluadas por esas bibliotecas. La evidencia de proceso conserva las salvedades históricas indicadas abajo. |

## Validación ejecutada en esta revisión

Python 3.14.6, Windows 11, audio desactivado, TEMP/TMP escribibles y `CRIPTA_PAQUETE_API` apuntando a `.cache/qa-paquete-p1`. Regresión: **810 pruebas en 198.006 s, cero fallos, cero errores, dos omisiones opcionales**. Log: `.cache/revision-2026-11-14-suite.log`.

Las omisiones corresponden a la comparación con una revisión histórica y la API en vivo. Su evidencia separada anterior figura en `qa-adicional-2026-11-14.md`; no se afirma haberlas vuelto a ejecutar en esta revisión. Las cuatro criptas del paquete histórico y las partidas generadas sí quedaron incluidas en la suite actual.

Medición offline sin la suite concurrente, referencia local `cripta-06@f9ed9afa683d`, 300 salas:

| Operación | Carga | Máximo | Límite |
|---|---|---:|---:|
| Ciclo integrado | Historia, mapa completo, 30 cazadores inyectados, 30 ciclos | 16.664 ms | 20 ms |
| Paso de viaje conocido | Mapa completo, primera búsqueda incluida, 30 consultas | 4.381 ms | 5 ms |
| Verificador completo | Normalización, recorrido, diagnóstico y reporte; diez muestras | 9.369 ms | 200 ms |
| Historia K=50 | 5.000 acciones, 100 campos sintéticos, 111 consultas | 1.0117 ms | 50 ms |

Ciclo: media 3.636 ms, 0/30 excesos. Viaje: media 0.157 ms, 0/30 excesos. Verificador: media 7.683 ms, cero HTTP; su alternativa repetitiva se midió y contrastó en la misma ejecución. Rutas: `.cache/revision-2026-11-14-rendimiento.log`.

Historia: tres repeticiones, semilla 20261001, K=10/50/100 y sin controles. Máximos de consulta total: 0.2912 / 1.0117 / 1.7798 / 82.1470 ms; memoria retenida: 6.208.572 / 5.422.292 / 5.126.900 / 4.808.436 bytes. K=50 conserva como máximo 50 acciones reconstruidas y 0/111 consultas sobre 50 ms; sin controles hay 18/111 excesos. Estos datos mantienen la justificación del valor por defecto sin confundir las alternativas descartadas con producción.

Una ejecución preliminar simultánea con la suite produjo un paso de 7.518 ms (1/30 sobre 5 ms) y ciclo máximo 13.725 ms. Se conserva aquí ese resultado; repetir sin concurrencia permite medir el subsistema con menor interferencia, pero no garantiza el umbral bajo cualquier carga del equipo. Las cifras de esta tabla no sustituyen ese resultado ni garantizan todas las criptas futuras.

## Decisiones resueltas sin nuevas consultas

- Acumulación de llaves: aplicar la aclaración existente, sin repetir la pregunta.
- Antorcha: revelar nombre/salidas de vecinas; observar puertas desde la sala ocupada, conforme a la distinción de §3.3. Es una decisión del equipo respaldada por el texto y las pruebas.
- Complejidad del verificador: evaluar el crecimiento aproximadamente lineal con evidencia y la comparación exigida; conservar O(N log N + salida) como cota total. No se declara O(N) estricto ni una aceptación académica garantizada.

Se corrigió la sección de QA que presentaba estas decisiones como tres consultas externas obligatorias. No se enviaron mensajes al profesor ni a compañeros.

## Salvedades que no se resuelven inventando datos

- El PDF original local de Parte I está vacío; permanece la extracción previa como referencia, sin autenticación contra ese original.
- Dos prompts históricos de A tienen finales incompletos; se conservan sus fragmentos, sin inventar el texto faltante.
- A documentó que `33d97ac` reunió la aclaración de FR-009 y su implementación en un mismo commit. Eso no cumple la separación de commits exigida por §2.6. Un documento nuevo no cambia ese hecho; no se reescribe el historial publicado para ocultarlo.
- Los arreglos heredados del motor dependen del mayor ID, aunque el buscador use índices compactos. No se garantiza memoria proporcional solo al número de salas con IDs extremadamente dispersos.

Conclusión técnica: la regresión no detecta fallos funcionales y la ejecución aislada satisface los umbrales anteriores. No equivale a certificar ausencia absoluta de bugs, cumplimiento documental perfecto o una nota de 100.
