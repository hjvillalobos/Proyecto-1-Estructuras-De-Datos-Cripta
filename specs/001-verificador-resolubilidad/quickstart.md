# Guía de validación prevista

Estos pasos corresponden a la implementación futura. No se ejecutaron ni se afirma que los módulos nuevos existan. Primero: tareas, análisis, revisión y commit de especificación; después código.

## Entorno

Desde la raíz del repositorio, con Python 3.11 o superior y las dependencias de `requirements.txt` instaladas en el entorno del proyecto. Las pruebas nuevas usan `unittest`; no requieren bibliotecas de grafos.

## Pruebas previstas de B

```powershell
python -m unittest tests.test_resolubilidad tests.test_verificacion_datos tests.test_bench_resolubilidad -v
python -m unittest tests.test_cliente_api tests.test_precarga_offline tests.test_sesion_datos tests.test_cache tests.test_catalogo -v
```

La primera orden solo estará disponible después de implementar los módulos propuestos. La segunda comprueba regresiones en preparación y estructuras existentes.

| Escenario | Resultado esperado |
|---|---|
| Cadena de llaves | Orden válido y determinista; resoluble si cumple condición de salida. |
| Llave de salida detrás de sí misma | No resoluble; frontera y testigo de ciclo concreto. |
| Mismo ID en ubicación accesible y otra bloqueada | Una obtención; no falso bloqueo. |
| Llave ausente en listado válido | Puerta bloqueada; dictamen según rutas restantes. |
| Falta archivo de llaves o versión incompatible | No completada; no sustituir por lista vacía. |
| Ciclo con alternativa externa bloqueada | Testigo acompañado por esa alternativa, sin afirmar causa única. |
| Ciclo de salas sin llaves | No inventar dependencia circular entre llaves. |
| Inicio hacia A sin regreso con K; puerta K desde Inicio a Salida | Resoluble bajo modelo acumulativo y limitación explícita, AC-21. |
| Mismos datos online y offline | Mismo resultado; cero red en offline. |

Cada prueba cita sus FR y AC. Repetir entradas diez veces para determinismo; verificar igualdad profunda de entrada antes/después y ausencia de llamadas a vista, reloj o azar de partida.

## Medición prevista tras integración con D

```powershell
python bench.py --subsistemas resolubilidad --tamanos 32 256 1024 --repeticiones 10 --semilla 20261101
```

La opción del subsistema todavía no existe. Comparar incremental y repetitivo con cadenas, ciclos y ubicaciones alternativas; comprobar igualdad de dictámenes y validez de órdenes antes de medir. Incluir normalización, diagnóstico y reporte en el total. Red y lectura de disco se miden aparte.

Medir además la mayor cripta publicada con datos locales completos, registrando ID, versión, tamaños y equipo. Informar todas las muestras, promedio, dispersión y máximo; no declarar aprobado el límite de 200 ms por cumplir solo el promedio.

## Aceptación conjunta con D

Probar `--verificar <cripta>` sin vista, inicio bloqueado ante resultado negativo y permiso solo con `--forzar`. Los errores de información bloquean incluso con esa bandera. Verificar que la presentación identifica el alcance acumulativo. Véase [contrato](contracts/verificador.md).

## Aceptación de correcciones

AC-22: preparar región desconectada con llave K y puerta de regreso que requiere K; esperar desconexión sin causa circular certificada. AC-23: simular cambio V1→V2 durante descarga, luego iniciar un cliente offline nuevo; no debe consumir respuestas rechazadas guardadas bajo V1. Repetir con fallo de consulta final y agotamiento de presupuesto.

Ejecutar familias N, 2N y 4N y comparar tiempos/conteos por fase según el protocolo de plan.md. El límite de 200 ms usa el total, incluyendo normalización y diagnóstico. C1 aprobado el 2026-11-02 por aclaración del profesor comunicada por el usuario. Antes del código sigue siendo obligatorio confirmar la especificación en Git; las pruebas y mediciones aún no se han ejecutado.

## Cierre del diagnóstico de ciclos

Ejecutar AC-24 con dos grupos circulares y una ubicación alternativa dependiente del segundo; ambos ciclos y la alternativa deben quedar visibles. Ejecutar AC-25 con varias llaves/ciclos en un grupo: todos los integrantes y alternativas se conservan, aunque se muestre un único ciclo representativo. Validar cada condición pendiente del certificado contra entrada, y cada arco del ciclo contra una salida o ubicación real. Un recorrido de salas sin llaves no se reporta como ciclo de llaves. La explicación usa referencias compartidas, no un subreporte expandido por llave.
