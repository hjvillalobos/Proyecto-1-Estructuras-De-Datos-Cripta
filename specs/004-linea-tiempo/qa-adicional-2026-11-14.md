# Validación adicional — 2026-11-14

Alcance autorizado: completar revisión, pruebas opcionales y documentación; excluir la preparación de defensa. No se modificaron reglas de producción en este incremento. La evidencia acredita los escenarios indicados, no una nota ni ausencia absoluta de errores.

## Checklist comprobado

- [x] Comparación aislada de rutas contra revisiones reales de A/C: 41 pruebas, OK, 0.369 s. `python -B -X utf8 -m utilidades.verificar_conocimiento_rutas` prepara una copia temporal sin modificar ramas.
- [x] Cuatro criptas históricas: dos pruebas, OK, 2.806 s, con victoria/replay y revisión de salas, iconos y persistencia.
- [x] API real: cinco criptas publicadas, caché fría/caliente en procesos independientes; una prueba, OK, 89.501 s. Presupuesto y capacidad de 25 fichas respetados.
- [x] Partidas completas inéditas, semillas 37/509/821: una prueba con tres subcasos, OK, 1.759 s. IDs dispersos, costos variables, equipo, antorcha, enemigos, llave/puerta; guardar, retroceder, cargar, ganar y reproducir el log tras eliminar el archivo de guardado. Estado completo, azar y mapa coinciden; cero HTTP.
- [x] Inspección manual de la GUI nativa con cripta-06 oficial, semilla 42; cierre correcto del proceso.
- [x] Revisión de fuentes disponibles del enunciado y de los prompts históricos incompletos, conservando sus límites.
- [x] Registro de decisiones, prompts y reproducción. Defensa excluida.

El resultado de la regresión conjunta posterior se registra al final. Los conjuntos se solapan y sus cantidades no se suman.

## Paquete histórico

`.cache/cripta` contenía mapas y contenido histórico, pero el catálogo `be68d322d2f5` carecía de fichas. Se conservó esa fuente y se completó la copia `.cache/qa-paquete-p1` con fichas reales compatibles del catálogo publicado `4b9e75a42be5`: tres solicitudes de un presupuesto mínimo de nueve. Se recopilaron tipos de enemigos, objetos y trampas efectivamente referenciados y se utilizó `GestorCatalogo.precargar` para incluir dependencias.

Mapas: cripta-01 `fd58f7743b9e`, cripta-02 `8091a5cd8b7c`, cripta-03 `24d301ed6e9f`, cripta-04 `d6727c7f4950`. Se prueban mapas históricos y catálogo actual compatible; no se afirma haber recuperado las fichas originales perdidas.

El primer recorrido detectó un defecto del bot: acumulaba botín hasta llenar el inventario y trataba como fallo el rechazo válido del motor. Se corrigió la estrategia de prueba mediante acciones reales de soltar un objeto prescindible, conservando equipo/llaves, y dejando de acumular pociones sin espacio. Se mantienen capacidad y reglas del juego y las aserciones de victoria, persistencia y replay.

```powershell
$env:CRIPTA_PAQUETE_API=(Resolve-Path '.cache/qa-paquete-p1').Path
python -B -X utf8 -m unittest tests.test_criptas_api.TestPaqueteOficial -v
```

El paquete está fuera de Git. El comando requiere una copia completa compatible de las cuatro criptas: la API actual ya no anuncia cripta-01.

## Servicio publicado

Se sustituyó la lista fija antigua por el listado vigente. `tests.api_publicada` mantiene UUID/contador por proceso e incluye listado, verificación, motor completo, contenido y esperas. La fase caliente reutiliza el disco de la fría; ambas deben fijar las mismas versiones de mapa/catálogo.

| Cripta | Versión | Fría / presupuesto | Caliente / presupuesto | Dictamen |
|---|---|---:|---:|---|
| 02 | 52532a77ee04 | 13 / 23 | 3 / 23 | resoluble |
| 03 | f9186ac25124 | 16 / 42 | 3 / 42 | resoluble |
| 04 | 7074a17814ad | 17 / 52 | 3 / 52 | resoluble |
| 05 | 48bfa3b75055 | 14 / 25 | 3 / 25 | no_resoluble |
| 06 | f9ed9afa683d | 46 / 63 | 3 / 63 | resoluble |

Catálogo: `4b9e75a42be5`. La preparación directa del motor es QA de datos: no equivale a permitir el arranque normal de una cripta no resoluble. El bloqueo de aplicación y `--forzar` conservan sus pruebas propias. Este escenario tampoco es una partida hasta la victoria de estas cinco versiones actuales.

```powershell
$env:CRIPTA_API_REAL='1'
python -B -X utf8 -m unittest tests.test_verificacion_entrega.TestApiRealEntrega -v
Remove-Item Env:CRIPTA_API_REAL
python -B -X utf8 -m unittest tests.test_partida_generada -v
```

## GUI nativa

Inicio offline sobre `.cache/entrega-completa`, cripta-06, semilla 42. Directorio de trabajo temporal separado para preservar las partidas de la usuaria.

1. Menú/reporte de resolubilidad visibles; inicio en sala 141, vida 30, ataque 6.
2. Recoger/equipar daga: inventario, sprite y ataque 9 coherentes; reloj 75.
3. Guardar; mover al este: sala 142, vida 29, reloj 175, enemigo/salidas visibles.
4. Mapa: salas 141/142 exploradas; vecinas 121/122/161/162 avistadas, sin nombres ocultos.
5. Cargar desde la partida recupera sala 141, vida 30, reloj 75 y daga equipada.
6. Historia en tiempo 75: sala, estadísticas e inventario coherentes.
7. Volver al menú y cargar: nueva preparación recupera la misma partida.
8. Cerrar: salida 0, cero HTTP, ninguna ventana CRIPTA restante.

No se observaron controles recortados ni errores de disposición en estas pantallas. No se afirma inspección manual exhaustiva de todas las resoluciones, plataformas o diálogos; las demás regresiones automáticas se conservan.

La regresión conjunta detectó además una prueba de teclado intermitente: `test_cancelar_escape_y_cerrar_devuelven_vacio` podía quedar esperando el diálogo. El diagnóstico de pila situó la espera en `wait_window`; los cinco casos aislados pasaban. Antes de inyectar Escape/Enter, la prueba ahora procesa la transferencia de foco de Tk con `root.update()`. Se mantienen los eventos y sus aserciones reales; no se cierra el diálogo por un atajo que falsee el resultado. Los logs de diagnóstico se conservan como ejecuciones interrumpidas, no como aprobaciones.

## Fuentes y aclaraciones externas pendientes

- **PDF original de Parte I:** el archivo local en Descargas pesa cero bytes; el ZIP disponible del repositorio no contiene un PDF del enunciado. Se conserva el texto extraído previamente como referencia de auditoría, pero no puede autenticarse contra el PDF vacío. Hace falta un original íntegro del aula/profesor.
- **Dos finales de prompts de A:** Git `934eaff` y el registro actual contienen los mismos fragmentos incompletos. Se preservan literalmente en [Vacíos históricos](../001-terreno-cazador/prompts-registro-local.md#vacíos-históricos). Se necesita la conversación original íntegra para recuperar los finales. Las 77 entradas completas siguen conservadas.
- **Resolubilidad dirigida:** confirmar si se permite acumular llaves de regiones alcanzables aunque no exista un único itinerario que regrese entre ellas. Ese es el modelo declarado por la implementación; una respuesta negativa exigiría revisar contrato y pruebas.
- **Complejidad:** confirmar si la normalización O(N log N), separada del recorrido aproximadamente lineal, cumple la interpretación de la rúbrica. Los tiempos no prueban linealidad estricta.
- **Antorcha/puertas remotas:** confirmar si revelar una sala vecina debe mostrar estados de puertas no observados desde una sala ocupada. Se conserva la interpretación conservadora del equipo, sin activar contenido remoto.

Estas preguntas están preparadas para revisión del equipo; no fueron enviadas ni se presentan como respuestas oficiales. No se prepararon materiales de defensa.

## Evidencia local

Logs fuera de Git: `.cache/qa-final-comparacion-c.log`, `qa-final-preparacion-p1.log`, `qa-final-paquete-p1-corregido.log`, `qa-final-api-real.log`, `qa-final-partida-generada.log`, `qa-final-suite.log`. Las cifras/versiones relevantes se conservan aquí para revisión sin depender de temporales.

## Regresión final

Python 3.14.6, Windows 11: **810 pruebas en 217.145 s; OK (skipped=2), cero fallos/errores**. Ejecución con `CRIPTA_PAQUETE_API` apuntando al paquete histórico completo, `CRIPTA_SIN_AUDIO=1` y TEMP/TMP escribibles. Comando equivalente: `python -B -X utf8 -m unittest discover -s tests -t . -v`; se utilizó además un límite diagnóstico de 45 s por caso. Log: `.cache/qa-final-suite-corregida.log`.

Las dos omisiones corresponden a la comparación contra otra revisión de C (preparada y aprobada por separado: 41 pruebas, incluyendo sus tres casos comparativos) y a la API real (aprobada por separado sobre las cinco criptas). No quedan escenarios opcionales identificados sin ejecución, aunque sus condiciones de preparación siguen siendo optativas en la suite normal. No se suman estos conjuntos solapados.

La regresión de foco aislada pasó tres repeticiones: 15 pruebas, OK, 21.790 s; log `.cache/qa-final-dialogo-foco.log`. La primera suite y la repetición diagnóstica fueron interrumpidas por la prueba de foco, y se conservan como evidencia fallida/interrumpida, no como resultados verdes. No se eliminaron ni omitieron casos para obtener la aprobación final.
