# Guía de validación del verificador

Implementación de B realizada el 2026-11-02, después del commit de preparación `17dc4bc`. Están disponibles el análisis, la preparación HTTP/offline y las funciones de medición. La integración de D con el inicio del juego y el comando general de benchmark continúa pendiente.

## Entorno

Desde la raíz del repositorio, con Python 3.11 o superior y las dependencias de `requirements.txt` instaladas en el entorno del proyecto. Las pruebas nuevas usan `unittest`; no requieren bibliotecas de grafos.

## Pruebas de B

```powershell
python -m unittest tests.test_resolubilidad tests.test_verificacion_datos tests.test_bench_resolubilidad -v
python -m unittest tests.test_cliente_api tests.test_precarga_offline tests.test_sesion_datos tests.test_cache tests.test_catalogo -v
```

Ambas órdenes están disponibles y fueron ejecutadas. La segunda comprueba regresiones en preparación y estructuras existentes. La revisión ampliada ejecutó 176 pruebas: 175 aprobadas y una prueba opcional de API omitida. La consulta real de la cripta mayor y sus mediciones se ejecutaron por separado.

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

## Medición disponible desde Python

```python
from utilidades.bench_resolubilidad import medir_resolubilidad

for medicion in medir_resolubilidad([32, 64, 128], 10, 20261102):
    print(medicion.familia, medicion.salas, medicion.estrategia,
          medicion.promedio_ms, medicion.maximo_ms)
```

`medir_datos(datos, 10)` acepta una cripta ya preparada; `medir_preparacion_offline(carpeta, cripta_id, version_cripta, 10)` mide lectura local y validación por separado. No se denomina a ese segundo valor tiempo puro de disco: incluye deserialización y validación.

Ejemplo de preparación HTTP sin catálogo, contenido ni motor:

```python
from datos.almacen import AlmacenLocal
from red.cliente_api import ClienteApi
from red.verificacion import preparar_verificacion
from utilidades.bench_resolubilidad import medir_datos

cliente = ClienteApi()
try:
    datos = preparar_verificacion(cliente, AlmacenLocal(".cache/resolubilidad/real"), "cripta-06")
    mediciones = medir_datos(datos, 10)
    for medicion in mediciones:
        print(medicion.estrategia, medicion.promedio_ms, medicion.maximo_ms)
finally:
    cliente.cerrar()
```

El ID es un ejemplo de uso, no una condición incrustada en el algoritmo. El catálogo publicado puede cambiar. Las carpetas de caché son locales y no acompañan el repositorio.

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

Ejecutar familias N, 2N y 4N y comparar tiempos/conteos por fase según el protocolo de plan.md. El límite de 200 ms usa el total, incluyendo normalización y diagnóstico. C1 aprobado el 2026-11-02 por aclaración del profesor comunicada por el usuario. La especificación quedó confirmada en `17dc4bc` antes del código. Las pruebas de B y las mediciones ya se ejecutaron; la aceptación conjunta con D sigue pendiente.

## Cierre del diagnóstico de ciclos

Ejecutar AC-24 con dos grupos circulares y una ubicación alternativa dependiente del segundo; ambos ciclos y la alternativa deben quedar visibles. Ejecutar AC-25 con varias llaves/ciclos en un grupo: todos los integrantes y alternativas se conservan, aunque se muestre un único ciclo representativo. Validar cada condición pendiente del certificado contra entrada, y cada arco del ciclo contra una salida o ubicación real. Un recorrido de salas sin llaves no se reporta como ciclo de llaves. La explicación usa referencias compartidas, no un subreporte expandido por llave.


## Evidencia del 2026-11-02

Mayor cripta del listado consultado: `cripta-06`, versión `f9ed9afa683d`, 300 salas.
Dictamen: resoluble bajo alcanzabilidad acumulada. Diez muestras incrementales:
promedio 2,721 ms, máximo 3,586 ms, incluyendo normalización, recorrido y construcción
del resultado. En este caso positivo no se necesita diagnóstico de bloqueo;
los casos negativos y ciclos se midieron en las familias sintéticas.
Lectura local y validación: promedio 6,519 ms, cero solicitudes HTTP.

La adquisición inicial se midió aparte: 4.894,375 ms y 11 solicitudes contando
el listado, metadatos, versiones, seis páginas y llaves. Ese valor incluye descarga,
validación y escritura local; no representa latencia pura de red.
Las muestras, conteos, razones por fase y equipo están en [mediciones.json](mediciones.json).
El análisis del costo total O(N log N + salida) está en [DECISIONES.md](../../DECISIONES.md).
Los datos observados cumplen 200 ms para esa versión y equipo; no certifican otros
mapas ni el ciclo de juego de 20 ms. La evaluación académica del crecimiento
aproximadamente lineal se conserva pendiente.

Pendientes compartidos: T025, T026 y T030, más la revisión cruzada B↔D.
No usar `--verificar`, `--forzar` ni el subsistema `resolubilidad` del comando general
como si esta rama ya los hubiera conectado.
