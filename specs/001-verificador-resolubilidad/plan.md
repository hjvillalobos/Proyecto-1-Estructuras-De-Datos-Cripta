# Implementation Plan: Verificador de resolubilidad

**Branch**: `codex/verificador-resolubilidad` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Estado**: Plan y tareas revisados documentalmente. C1 aprobado por aclaración del profesor comunicada por el usuario el 2026-11-02; pendiente commit de especificación antes de implementar.

## Summary

B preparará metadatos, esqueleto y ubicaciones de llaves de una misma versión y entregará un resultado independiente del motor y de la vista. D conectará inicio, `--verificar` y `--forzar`. Se conservan las ubicaciones alternativas y la distinción entre llaves imposibles de obtener y errores de información.

La propuesta usa arreglos, índices enteros, búsqueda binaria propia y cola sobre una lista. El recorrido incremental reactiva solo las puertas de cada llave recién obtenida. B1 queda resuelto para planificación mediante el supuesto acumulativo autorizado: no se certifica una trayectoria única. El profesor aceptó este alcance según confirmación comunicada por el usuario el 2026-11-02; C1 queda cerrado. Véase [research.md](research.md).

## Technical Context

- **Language/Version**: Python 3.11 o superior, exigido por P2. Codex y spec-kit v1.2.3.
- **Primary Dependencies**: biblioteca estándar y `requests>=2.31,<3` existente. Ninguna biblioteca nueva de grafos. `Pillow` pertenece a la vista y no se importa aquí.
- **Storage**: JSON por cripta y versión mediante `AlmacenLocal`, escritura temporal y reemplazo atómico existentes. No es guardado de partida.
- **Testing**: `unittest`, transporte falso y directorios temporales, siguiendo las pruebas existentes.
- **Target Platform**: entorno local, incluido Windows/PowerShell; análisis sin vista.
- **Project Type**: análisis puro, preparación de datos y contrato de resultado para D.
- **Performance Goals**: 200 ms en la mayor cripta publicada, incluyendo normalización, análisis y diagnóstico. Medir red y disco por separado, sin ocultar trabajo de cálculo fuera del total.
- **Constraints**: sin `dict`/`set` como índices, `heapq`, `bisect`, `collections`, bibliotecas de grafos ni ordenamientos automáticos. Sin cambios de entrada, reloj, conocimiento o azar de partida. Código nuevo sin comentarios.
- **Scale/Scope**: V salas, E salidas, K IDs distintos de llave y L ubicaciones; L puede superar K. Tamaño máximo publicado pendiente de medición.
- **Alcance B1**: cierre acumulativo aceptado por el profesor según confirmación transmitida por el usuario. Mantener dirección de salidas; el resultado declara que no certifica una trayectoria única.

## Constitution Check

| Principio | Revisión inicial |
|---|---|
| Estructuras propias | Propuesta conforme; la caché P1 no cambia. |
| Determinismo | Sin azar en análisis; direcciones N, S, E, O e IDs ordenados mediante implementación propia. |
| MVC | Análisis sin HTTP, vista ni juego; resultado estructurado para D. |
| Especificación antes que código | No se crea código. Commit de especificación previo a implementación. |
| Sin datos concretos | Datos reales del servicio; ejemplos sintéticos solo en pruebas. |
| Presupuesto | Reutilizar transporte; cada intento y consulta de versión cuenta. |
| Rendimiento con evidencia | Mediciones pendientes; no se declara cumplimiento. |
| Corrección FR-001–004 | C1 aprobado: AC-21 corresponde al alcance aceptado por el profesor, según comunicación del usuario del 2026-11-02. Corrección funcional pendiente de pruebas. |
| Costo FR-015 | Recorrido lineal; normalización con factores logarítmicos explícitos. Evidencia de escalamiento y aceptación del costo total pendientes. |

Revisión posterior al diseño: estructuras, separación, determinismo y presupuesto conformes como propuestas. C1 aprobado con la aclaración del profesor transmitida por el usuario; no se modifica la constitución ni se solicita una excepción. Rendimiento y corrección funcional siguen pendientes de implementación, pruebas y mediciones.

## Project Structure

### Documentation

`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/verificador.md` y `quickstart.md` están disponibles. `tasks.md` corresponde a la siguiente habilidad, no a esta fase.

### Source Code

Archivos previstos; no se crean ni modifican ahora:

| Archivo | Responsabilidad |
|---|---|
| `red/cliente_api.py` | Agregar `obtener_llaves(cripta_id)` mediante el transporte existente. |
| `red/validacion.py` | Validar ubicaciones y campos obligatorios sin exigir ID único entre ubicaciones. |
| `datos/almacen.py` | Agregar lectura/escritura de `llaves.json` bajo la versión de cripta. |
| `datos/offline.py` | Leer llaves de la versión seleccionada sin red. |
| `red/precarga.py` | Extraer preparación reutilizable de generales/esqueleto, sin descargar contenido inicial para verificar. |
| `red/verificacion.py` | Nuevo coordinador de adquisición, compatibilidad y errores esperados. |
| `modelo/resolubilidad.py` | Nuevo análisis puro y registros de resultado, con alcance acumulativo explícito. |
| `utilidades/ordenamiento.py` | Reutilizar `ordenar(..., algoritmo="fusion")`. |
| `utilidades/bench_resolubilidad.py` | Nueva medición reproducible y comparación con recorrido repetido. |
| `tests/test_resolubilidad.py` | Análisis, alternativas y diagnóstico. |
| `tests/test_verificacion_datos.py` | Red, versiones, persistencia, errores y offline. |
| `tests/test_bench_resolubilidad.py` | Igualdad lógica y conteos de trabajo, sin umbrales temporales frágiles. |

Los nombres nuevos son propuestas. D conecta `main.py`, presentación y `bench.py`; B entrega las funciones y pruebas. Terreno y cazadores quedan fuera de esta capacidad.

## Diseño adoptado

### Preparación

1. Reutilizar u obtener generales y configurar presupuesto antes de nuevas descargas.
2. Reunir todas las páginas, validar cantidades, IDs, destinos, sala inicial y salida. No interpretar fallo de descarga como listado vacío.
3. Reutilizar llaves de la versión o solicitar `/criptas/{id}/llaves`. Validar `id`, `sala` y `enemigo` opcional. Rechazar booleanos como IDs numéricos.
4. Cuando se descarguen datos, mantener generales, páginas y llaves nuevos en una lista privada en memoria, sin escribirlos aún en el almacén reutilizable ni actualizar `actual.json`. Comprobar versión antes y después y validar todo el conjunto; si cambia o falla la consulta final, descartar el lote privado y devolver verificación no completada. Solo tras esa comprobación publicar archivos con reemplazos atómicos existentes y actualizar `actual.json` al final. No se pretende una transacción atómica de varios archivos: si falla una escritura, puede quedar un subconjunto ya validado de la misma versión, y los lectores deben detectar faltantes sin declarar completitud. No sobrescribir una copia válida con datos no verificados. La garantía depende de que el servidor actualice versión al cambiar contenido; no se promete atomicidad no ofrecida por HTTP.
5. Una versión histórica usa archivos compatibles; no rellenar faltantes con datos actuales de otra versión. Offline nunca recurre a red.
6. Persistir llaves completas con el mecanismo atómico existente, conservando versiones antiguas. `llaves.json` es formato interno, no equivalencia afirmada con un paquete oficial aún no validado.
7. Convertir objetos JSON a registros/arreglos antes del análisis; JSON no se usa como índice estructural.

Actualmente `GestorPrecarga.preparar_cripta` inicia catálogo y descarga contenido inicial. Extraer su preparación común de esqueleto y preservar el inicio normal mediante regresiones. No llamar el flujo completo solo para verificar. La extracción debe permitir preparar sin persistir; no reutilizar una rutina que guarde generales o páginas antes de la comprobación final. La nueva ejecución offline de AC-23 debe comprobar el estado del disco, no solo el error de la ejecución anterior.

### Estructuras propuestas

Normalizar salas y llaves a índices densos de 0 a n-1. Ordenar IDs mediante fusión propia y buscar por búsqueda binaria propia; no reservar memoria hasta el mayor ID. Deduplicar llaves comparando elementos contiguos tras ordenar.

Cada sala tiene listas de salidas y ubicaciones; cada llave tiene ubicaciones y puertas pendientes. Marcas booleanas por índice. Cola con lista, `append` e índice de lectura, sin `pop(0)` ni `deque`. No se necesita AVL para índices estáticos.

El recorrido incremental marca cada sala al encolarla y procesa cada sala una vez. Al procesarla obtiene primero sus llaves en orden de ID y después examina sus salidas en N, S, E, O. Una llave nueva se registra una vez y activa sus puertas pendientes en orden de registro. Una puerta encontrada después de obtener su llave se habilita inmediatamente. El vaciado de pendientes se hace una sola vez por llave.

La victoria se comprueba al terminar: llave de salida obtenida y alguna entrada declarada hacia sala de salida, cuyo origen está alcanzado y cuyo requisito es esa llave. Esto cubre también una puerta abierta examinada antes de obtener la llave de salida. No basta marcar la sala de salida.

Conservar la primera ubicación que permitió obtener cada llave y la puerta que incorporó cada sala como evidencia del orden acumulativo. No usar esas evidencias como una ruta jugable única.

### Resultado

Proponer registro con estado `resoluble`, `no_resoluble` o `no_completada`, cripta y versión, orden de llaves, llaves inaccesibles con ubicaciones, frontera, ciclos justificados y causa de error. Contrato definido en [contracts/verificador.md](contracts/verificador.md), con alcance y limitación explícitos.

El coordinador captura errores esperados de red, presupuesto, disponibilidad, datos y versión. No oculta errores de programación. Una llave ausente de un listado completo válido no genera error de datos.

### Diagnóstico y costo

No deducir una dependencia obligatoria de una sola ruta ni confundir ciclos de salas con ciclos impeditivos de llaves. Conservar alternativas y evidencias. Para el diagnóstico se conserva un grafo de condiciones de tamaño lineal: nodos de sala, llave y paso por salida. El paso exige sala origen y, si está cerrado, su llave; una sala tiene como alternativas sus pasos entrantes y una llave sus ubicaciones. Registrar estas relaciones durante la normalización y reutilizarlas en el análisis.

Al terminar, excluir condiciones satisfechas. Calcular componentes fuertemente conexas mediante Kosaraju iterativo propio (dos recorridos, pila con lista, adyacencias directas e inversas). Se descartan componentes sin llaves y ciclos exclusivamente de salas. Para cada componente cíclica con llaves se extrae un testigo determinista que pase por una llave, conservando puertas y ubicaciones. Un recorrido interno con predecesores permite volver al nodo inicial; procesar cada componente una vez, sin enumerar todos los ciclos ni repetir el mapa por llave.

El diagnóstico completo combina un certificado del estado final con los ciclos encontrados. No depende de que una prueba aislada por componente logre explicar todas las causas.

1. **Certificado global del cierre.** Conservar los valores finales de todas las condiciones. Para cada sala no alcanzada distinta de Inicio, comprobar que todos sus pasos entrantes están deshabilitados. Para cada llave no obtenida, comprobar que todas sus ubicaciones están en salas no alcanzadas, o registrar que no tiene ubicaciones. Para cada paso deshabilitado, registrar qué requisitos no se cumplen (origen, llave o ambos). Inicio es una base satisfecha y no puede aparecer como requisito falso. Una condición OR sin alternativas representa ausencia, nunca un ciclo.
2. **Por qué ese certificado prueba el bloqueo.** Ninguna condición pendiente puede ser la primera en activarse: cada alternativa requiere otra condición pendiente o no existe. Por inducción sobre las activaciones, el conjunto pendiente permanece falso bajo el modelo acumulativo. El recorrido proporciona también evidencia de las condiciones verdaderas. Así se explica toda llave inaccesible, incluso cuando existen varias causas o varias componentes; no se necesita certificar cada SCC como causa autónoma.
3. **Separar desconexión.** Un único recorrido global ignorando cerraduras marca la accesibilidad estructural. Si una llave tiene todas sus ubicaciones fuera de esa región, informar desconexión. No atribuir esa ausencia de acceso a una puerta de regreso. Si unas ubicaciones están desconectadas y otras bloqueadas, conservar ambas explicaciones, sin descartar alternativas.
4. **Ciclos concretos.** Sobre condiciones pendientes ejecutar Kosaraju iterativo. Por cada componente cíclica que contenga llaves, elegir la llave de menor índice normalizado. Desde una arista interna de esa llave buscar un camino de regreso dentro de la componente y emitir el ciclo con los pasos, puertas y ubicaciones originales. Recorrer cada componente una sola vez para el testigo. Informar todas las llaves integrantes y todas las alternativas de adquisición mediante referencias al grafo de evidencia, sin duplicar el grafo por llave. Las componentes sin llaves no son ciclos de llaves.
5. **Clasificación precisa.** Una componente situada en región desconectada se clasifica como `ciclo_en_region_desconectada`, y no como causa de inaccesibilidad. Para las restantes, si todas las alternativas OR tienen algún requisito pendiente interno y cada paso AND tiene al menos un requisito pendiente interno, clasificar `bloqueo_circular_autonomo`. En otro caso, clasificar `dependencia_circular_con_bloqueos_externos` y enlazar las alternativas externas con sus requisitos falsos. Esta última categoría afirma que la relación circular existe y que hay bloqueos externos comprobados por el certificado global; no afirma que el ciclo sea inevitable ni la causa única. Ninguna clasificación cambia el dictamen calculado por el cierre.
6. **Cobertura sin enumeración exponencial.** Se reportan todas las componentes cíclicas con llaves, sus integrantes, un ciclo concreto por componente y la evidencia completa de sus alternativas. No se prometen todos los ciclos simples ni una causa mínima única. El autoencierro de R1 produce K→K y AC-07 produce A→B→A, acompañados por sus puertas y ubicaciones. Si una componente agrupa más ciclos, sus integrantes y relaciones permanecen en el certificado y no se omiten por elegir un solo ejemplo visible.

La completitud aquí significa explicar cada condición no satisfecha y conservar todas las alternativas y componentes con ciclos; no identificar todas las causas mínimas posibles. Una alternativa accesible hace verdadera la llave y la excluye del diagnóstico pendiente. Una llave ausente tiene cero ubicaciones y no genera una dependencia circular. AC-22 se explica por desconexión aunque haya un ciclo local. El caso de dos componentes donde una alternativa depende de otra queda explicado mediante referencias externas, sin degradar un bloqueo real a «no concluyente».

Con índices resueltos, cierre y certificado cuestan O(V + E + K + L); accesibilidad estructural y SCC también. El ciclo visible de cada componente se obtiene con un recorrido interno y las componentes son disjuntas. Las referencias externas se almacenan una vez por relación; no se expanden transitivamente al imprimir cada llave. El reporte compacto tiene tamaño lineal en condiciones y relaciones. Normalización O(N log N), recorrido y diagnóstico O(N), con N=V+E+K+L; contar longitud de IDs cuando corresponda. Se conserva el costo total de normalización y presentación del reporte en las mediciones.

### Protocolo de escalamiento

Usar N = V + E + K + L y registrar también longitud total de IDs y tamaño del reporte. Ensayar las mismas familias con N, 2N y 4N, manteniendo proporciones e IDs de longitud comparable. Medir diez o más repeticiones con promedio, desviación, mínimo y máximo. Informar para cada fase T(2N)/T(N), T(4N)/T(2N), tiempo/N y trabajo/N; para normalización informar también comparaciones/(N log2(max(2,N))).

Contadores de recorrido y diagnóstico deben corresponder a un número acotado de pasadas globales: cada sala se procesa una vez, cada salida se registra una vez y cada pendiente se activa como máximo una vez; SCC y certificación visitan nodos/relaciones una cantidad constante de veces. El trabajo del reporte se cuenta por elemento emitido. No hay umbral mágico de razón temporal que demuestre complejidad: variación se reporta y conteos/algoritmo sustentan la cota.

Normalización O(N log N), recorrido O(N), diagnóstico O(N + tamaño del reporte) y total O(N log N + tamaño del reporte). No denominar al total estrictamente lineal. FR-015 conserva su exigencia original; la aceptación de crecimiento aproximadamente lineal requiere revisar esta distinción con la evidencia y el criterio académico, no ocultar normalización. El límite de 200 ms aplica al total completo y no solo a un promedio o fase.

## Validación prevista

- AC-01–10: cadenas, llave autoencerrada, ciclos entre llaves, alternativas, regiones desconectadas, ausencia de llave opcional o indispensable y llave de salida ausente.
- AC-11–14: versiones, presupuesto, 429, JSON inválido, archivos ausentes, lista vacía válida, llave sin sala, destinos inexistentes y offline sin red.
- AC-15–18: integración con D, ausencia de vista y mutaciones. `--forzar` no suple errores de información.
- AC-19–20: al menos tres tamaños de cadenas y ciclos; entradas idénticas por semilla, diez repeticiones de determinismo y mediciones con promedio, mínimo, máximo y dispersión. Comparar dictámenes y validez de órdenes antes de tiempos.
- Contar visitas de salas/salidas y activaciones de pendientes. Registrar normalización, análisis, diagnóstico y total, incluyendo generación del reporte.
- Medir mayor cripta publicada con versión, equipo, tamaño y todas las muestras; no afirmar 200 ms si hay excesos o faltan datos.
- AC-21: confirmar dictamen acumulativo en ramas sin regreso y alcance explícito en el resultado y presentación de D.
- AC-22: desconexión con llave y puerta de regreso no certificada como causa circular.
- AC-23: tras rechazo por versión, una segunda ejecución offline no consume el lote rechazado.

## Complexity Tracking

No se autoriza excepción constitucional. B1 se resuelve mediante el alcance aprobado, no mediante búsqueda exponencial. El único algoritmo adicional al recorrido es el diagnóstico iterativo de componentes, necesario para no repetir búsquedas por llave. Se reutiliza el ordenamiento propio; no se introduce AVL. Tareas, análisis cruzado, commit previo y evidencia de rendimiento quedan pendientes.
