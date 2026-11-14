# Integración completa — 2026-11-14

Contrato IA-01..09 confirmado en eb28d24 antes del código. Producción integrada en f31662c y avances recientes de A incorporados mediante 3bedd4a (remoto f8e10ef). Sin cambios de main ni ramas ajenas: la rama de entrega es 004-linea-tiempo.

## Trazabilidad

| Criterio | Implementación | Evidencia |
|---|---|---|
| IA-01 / FR-018/019 | controlador/aplicacion.py, main.py, modelo/partida.py | CLI real y tests.test_modos_historia, test_controlador_ac_real |
| IA-02 / FR-004/007 | MotorPartida, inventario/conocimiento de C, LineaTiempo | test_partida_completa, test_historia_motor, test_controlador_ac_real |
| IA-03 / FR-011 | preparar y validar físico/conocimiento fuera del vivo, luego restaurar | MC-01, DX-06 incoherencia, test_fallos_transaccionales |
| IA-04 / PD-01..04 | extremos por topología única, inversos preservan presencia, exportación de A | test_puertas_reciprocas_d, test_restauracion_rutas |
| IA-05 | conocimiento local y deltas; antorcha solo revela esqueleto | test_partida_completa y test_entrada_conocimiento_motor |
| IA-06 | _CapturaPaso/_aplicar_dano de A; ControlViaje de C/D | test_hechos_paso_motor, DX-05 positivo, test_controlador_viaje |
| IA-07 | bench parte-dos y terreno-cazador, historial y verificador | test_rutas_compartidas, test_bench_terreno_cazador; mediciones anexas |
| IA-08 | sustituir límites superados por aceptación; conservar errores/atomicidad | MC/DX/PD, test_modos_historia y regresión completa |
| IA-09 | README, DECISIONES, PROMPTS y este documento | comandos reproducibles, resultados y límites declarados |

## Decisiones de integración

No se serializan callbacks ni copias físicas por acción. La historia almacena deltas puros; la base/checkpoints pertenecen a LineaTiempo. El productor recibe directamente los deltas locales de conocimiento, evitando proyectar todo el mapa por evento. El inventario compara sus nodos y preserva orden/equipo; una selección gratuita se reconcilia al producir la siguiente acción. La carga valida historia, frontera, inventario y conocimiento sobre una preparación independiente, incluidos derivados de rutas separados, antes de publicar.

La aplicación selecciona explícitamente `partida_completa=True`; los adaptadores y opciones de prueba anteriores se conservan para sus contratos acotados. No se habilita el productor parcial como motor final. Se adoptan los hechos de daño de A, capturados durante la acción, que no confunden curación posterior con ausencia de daño.

La puerta se empareja solo cuando la topología identifica un retorno único en ambos sentidos. Casos ambiguos o sin retorno no se emparejan por adivinar una dirección. La interpretación de puertas remotas con antorcha sigue siendo del equipo: revelar no equivale a observar desde una sala no ocupada.

## Reproducción

```powershell
$env:CRIPTA_SIN_AUDIO='1'
python -B -X utf8 -m unittest discover -s tests -v
python -B -X utf8 -m unittest tests.test_partida_completa tests.test_rutas_compartidas tests.test_controlador_ac_real tests.test_puertas_reciprocas_d tests.test_hechos_paso_motor tests.test_restauracion_rutas
python main.py --bench --subsistemas parte-dos --paquete .cache/entrega-completa --cripta cripta-06 --repeticiones 30
python main.py --bench --subsistemas terreno-cazador --salas 40 --repeticiones 3
python main.py --bench --subsistemas resolubilidad --paquete .cache/entrega-completa --cripta cripta-06 --repeticiones 10
python main.py --bench --subsistemas historia --operaciones 5000 --salas 100 --repeticiones 3
```

Si el entorno de ejecución restringe la carpeta temporal del sistema, configurar TEMP/TMP a una carpeta escribible antes de las pruebas. La API se consulta para preparar el paquete, nunca dentro de las mediciones offline.

## Alcance y límites

Las pruebas automáticas y los benchmarks no garantizan cero bugs ni una nota. No se inventan aclaraciones del profesor, revisión cruzada humana ni recuperación de prompts históricos incompletos de A. La resolubilidad mantiene el modelo documentado por B de alcanzabilidad acumulada y la normalización O(N log N); no se promete una trayectoria única en conexiones dirigidas sin regreso.

La suite contiene pruebas opcionales del paquete antiguo de cuatro criptas, API en vivo y comparación contra otra revisión. Sus omisiones se reportan separadamente, sin contarlas como éxitos. El paquete antiguo disponible está incompleto; la aceptación actual adicional usa el paquete oficial de referencia descargado del servicio.


## Resultado del cierre integrado

Python 3.14.6, Windows 11. Suite completa posterior a integrar A: **809 pruebas, OK, cuatro omisiones y cero fallos/errores**, en 176.630 s. Log local `.cache/integracion-final-con-a.log`. Últimas comprobaciones después de aislar también los derivados de la carga y conectar la CLI del benchmark de A: **40 pruebas, OK** en 4.830 s; limpieza del identificador de pergamino predeterminado: **15 pruebas, OK**. Los conjuntos se solapan y no se suman.

Omisiones: comparación opcional contra una revisión previa de C; dos pruebas con paquete antiguo de cuatro criptas no indicado; prueba opcional de API en vivo de esas cuatro criptas. No quedan omisiones del productor/restauración de producción. La comparación de C se había ejecutado separadamente con 41 casos aprobados durante la auditoría. No se altera una omisión para fingir éxito.

Se comprobó además el proceso real, sin dobles: `mapa`, `historia`, guardar, mover/esperar, cargar y replay en el paquete sintético; mapa, historia, guardar, esperar y cargar en la referencia oficial de 300 salas. La API entregó el paquete completo con 46 de 63 solicitudes. Los ficheros de datos se mantienen en `.cache/entrega-completa`, fuera de Git.

### Mediciones finales reproducibles

| Operación | Carga | Máximo observado | Umbral |
|---|---|---:|---:|
| Ciclo integrado | Referencia 300 salas, mapa completo, 30 cazadores inyectados, 30 ciclos | 10.789 ms | 20 ms |
| Paso conocido | Mismo esqueleto, todas las salas y puertas conocidas, primera consulta incluida | 4.323 ms | 5 ms |
| Verificación incremental completa | Referencia 300 salas, diez repeticiones | 11.777 ms | 200 ms |
| Consulta historia K=50 | 5.000 acciones sintéticas, 111 consultas | 0.7872 ms | 50 ms |

No hubo excesos en esas cargas. Las cifras no garantizan todos los equipos ni todas las criptas futuras. La topología/costos de la referencia se conservan; las puertas y la población de cazadores se controlan expresamente para el escenario de medición. No es una afirmación de que esos 30 actores estuvieran naturalmente activados al iniciar la cripta.

La comparación sintética inicial excedía 20 ms (máximo 421.942 ms); compartir el campo ilimitado y registrar solo deltas locales resolvió ese cuello en las cargas medidas. Los resultados completos, muestras del verificador, historia K=10/50/100/sin controles y evaluación de agendas de A están en [integracion-mediciones.json](integracion-mediciones.json). La alternativa sin controles supera 50 ms en varias consultas; no es la opción de producción.

Las decisiones finales se documentan también en DECISIONES.md. No se declara una calificación, revisión humana o respuesta oficial del profesor. Los vacíos históricos de prompts de A se conservan declarados y no se rellenan con textos inventados.
