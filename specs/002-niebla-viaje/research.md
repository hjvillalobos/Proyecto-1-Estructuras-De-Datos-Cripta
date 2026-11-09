# Investigación técnica de C

Fecha: 2026-11-08. Estado: preparación del plan provisional. No resuelve Q1 ni sustituye acuerdos del equipo. Investigación local sobre código disponible; no medición de rendimiento.

## 1. Identificadores y actualización incremental

**Decisión candidata:** índice compacto de salas, ordenamiento y búsqueda binaria propios, conexiones traducidas una vez a posiciones internas.

**Motivo:** `RegistroRastro` usa directamente el ID y amplía hasta `sala_id + 1`. Copiar ese diseño al conocimiento haría depender la memoria del mayor ID. Un índice compacto ocupa espacio según la cantidad de salas; la descarga del esqueleto no habilita su consulta desde la vista.

**Alternativas:** búsqueda lineal por cada consulta, simple pero costosa; arreglo por ID, rápido solo bajo una cota útil del dominio; árbol propio, más complejidad para un conjunto de IDs estable; índice compacto, adecuado para preparar una vez y actualizar estados muchas veces. No se consideran dict/set/bisect ni ordenamientos de biblioteca.

**Costos:** consulta externa O(log V), interna O(1). Actualización O(R+A) si recibe referencias resueltas; con R identificadores arbitrarios por resolver cuesta O(R log V+A). Preparación, consultas y revelación se medirán por separado. No se afirma una actualización estrictamente O(R) si procesa salidas de esas salas.

## 2. Retroceso, fallos e historia

**Decisión candidata:** cambios de datos inmutables por campo u operación, con anterior/posterior y aplicación inversa por orden. No guardar estado completo por acción.

**Motivo:** `RegistroTurno` contiene `cambios` y `cambios_fallo`. El primero participa en pergamino; el segundo permite deshacer una acción fallida. No deben unificarse perdiendo la excepción de pergaminos. Hoy almacenan funciones y lambdas, no datos persistibles.

**Alternativas:** serializar callbacks, inviable como contrato estable; copiar estado por acción, contrario a las restricciones; derivar cambios comparando copias, introduce recorrido global y trabajo ajeno a D; registrar cambios en las primitivas de mutación, opción a concretar con A/D.

**Condición:** acordar publicación de lote, rollback y correcciones persistentes antes de modificar historial compartido. Registrar una mutación no debe ejecutarla nuevamente al enviarla a historia.

## 3. Inventario y restauración

**Decisión candidata:** conservar la lista propia y capturar altas, bajas y movimientos con identidad estable, vecinos/posición afectada, equipo y cursor cuando correspondan. No reemplazar el inventario para facilitar historia.

**Motivo:** existen primitivas de inserción, eliminación y movimiento. El guardado actual exporta instancia/tipo/equipado, pero restaura el cursor al principio; no acredita restauración exacta del cursor previo. Hay que distinguir el estado requerido para retroceso, guardado y resumen histórico antes de cambiar el formato.

**Pendiente concreto:** acordar con D si su proyección de inventario está destinada solo a presentación o también a restauración. Las claves por orden propuestas por D pueden necesitar borrar/actualizar posiciones desplazadas. No presentar ese adaptador como O(1) sin examinar su costo.

## 4. Compatibilidad histórica

**Decisión candidata:** adaptar datos de C a `ValorHistorico` y `CambioHistorico` de D; usar su contenedor `EventoHistorico` para tiempo/secuencia.

**Evidencia:** los valores aceptados por D son None, bool, int, str, float finito y tuplas recursivas. No se admiten listas, nodos ni registros arbitrarios. `presente=False` distingue ausencia de un valor presente que sea None. La proyección de líneas del mapa no sustituye ese estado reconstruible.

**Alternativa descartada:** crear un segundo formato histórico global en C. Implicaría reconciliar dos contratos y duplicar trabajo de D.

## 5. Reutilización de rutas

**Preferencia:** extender por acuerdo la búsqueda de A para aceptar fuente conocida y ausencia explícita de límite.

**Evidencia:** `buscar_ruta` consulta `arco.puerta.get("cerrada", False)` y aplica `candidata > limite`. Su contrato interno espera origen/destino diferentes y límite explícito. No cubre por sí mismo llegada ni el protocolo propuesto para C.

**Pendientes:** fuente filtrada antes de buscar, memoria de puerta independiente, revisión de fuente, casos origen=destino y sin ruta, y modo sin límite. No usar `None` donde actualmente se compara numéricamente ni un número enorme como sustituto. No se introduce otro buscador sin comparar primero adaptación y mediciones.

## 6. Viaje e interrupción

**Decisión candidata:** coordinación por pasos ordinarios con resultado explícito y oportunidad de procesar retroceso entre pasos.

**Motivo:** D devuelve un booleano desde el callback de movimiento. Ese dato no prueba ausencia de daño o enemigos. C necesita hechos del intervalo cerrado; la resta de vida inicial/final no detecta daño seguido de curación.

**Pendiente:** acordar con A señales y frontera, y con D el mecanismo de continuación para no bloquear la interfaz. Se pueden mantener fachadas compatibles, pero no ocultar un bucle ininterrumpible bajo el nombre existente.

## 7. Estado de investigación y evidencias faltantes

Resueltas para preparar el diseño: comparación de índices, restricciones de valores históricos y limitaciones de las interfaces publicadas. Pendientes: Q1 y acuerdos enumerados arriba. No se declara investigación completa de toda la capacidad.

La habilidad de planificación requiere detener el cierre del plan ante aclaraciones no resueltas. Se conserva un borrador útil y no se pasa a tareas ejecutables ni a implementación por el solo hecho de que exista `plan.md`.

Investigación delegada de solo lectura, exigida por la habilidad speckit-plan: revisión de historial, inventario, rastro, tipos y snapshots de D. No se modificaron módulos, no se ejecutaron pruebas ni se aprobó en nombre de otros integrantes.
