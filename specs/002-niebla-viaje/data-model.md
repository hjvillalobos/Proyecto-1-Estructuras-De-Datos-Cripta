# Datos del incremento I1

Diseño local de C; no modifica tipos compartidos. Python 3.11+, dataclasses inmutables y tuplas de datos. Sin red, vista, archivos ni azar.

- `SalidaConocible(direccion, destino, costo, puerta=None)`: dirección no vacía, ID de destino entero no negativo, costo entero positivo, puerta opcional entera no negativa. None significa conexión sin puerta, no puerta sin observar.
- `SalaConocible(id, nombre, salidas)`: ID entero no negativo, nombre texto y salidas tupla; direcciones únicas dentro de sala.
- `PuertaConocible(id, extremo_a, extremo_b)`: identidad explícita, extremos existentes y distintos. No se deduce identidad por pareja de salas. Una salida con puerta debe conectar esos extremos.
- `CambioConocimiento(ambito, id, anterior, nuevo)`: ámbito sala o puerta. Estados de sala 0 desconocida, 1 avistada, 2 explorada. Memoria de puerta None sin observar, False abierta, True cerrada. Dato local adaptable posteriormente a tipos de D, no formato de guardado nuevo.
- Proyección: tupla de salas conocidas en orden de ID; cada registro `(id, estado, nombre_o_None, salidas)`; avistada omite nombre y salidas; explorada contiene salidas `(direccion, destino, costo, puerta, recuerdo)` ordenadas por dirección. El recuerdo de una conexión sin puerta es False. No se muestran habitaciones desconocidas ni contenido de ninguna sala.

Índices compactos propios construidos con `utilidades.ordenamiento.ordenar(..., algoritmo='fusion')`, búsqueda binaria manual y adyacencias resueltas al preparar. Consulta ID O(log V) u O(log P); entrada O(log V + grado), observación O(log P + log V), deltas O(D log(V+P)) por resolución de IDs estables. No se oculta ese costo como O(D).

Aplicación de lotes: validar tipo/ámbito/valores, comparar anterior esperado, aplicar secuencialmente y deshacer el prefijo aplicado si falla. Revertir recorre en orden inverso e intercambia anterior/nuevo. Esto conserva atomicidad sin copiar todo el mapa ni crear índices dict/set. No valida una historia externa completa; requiere misma definición del esqueleto. Solo la integración futura administra versiones.

`entrar(sala_id)` devuelve cambios de exploración/avistamiento. `observar_puerta(sala_id, puerta_id, cerrada)` devuelve cambio de memoria. `aplicar(cambios)` y `revertir(cambios)` usan lotes de tuplas. `estado_sala`, `recuerdo_puerta` y `mapa_conocido` son lecturas. `mapa_conocido` devuelve datos, no las líneas que espera la fachada de D: ese adaptador queda pendiente y no se instala en el motor.

## Datos locales de I2

`HechosPaso(llegada, recibio_dano, hubo_entrada, enemigos_al_entrar, ruta_disponible, cancelado)` exige seis booleanos explícitos; no acepta 0/1 como sustitutos. Es inmutable. `evaluar_detencion` produce `DecisionDetencion(causas)`, también inmutable; `continuar` es verdadero solo cuando la tupla de causas está vacía. Las causas son etiquetas internas para un futuro adaptador, no mensajes que se insertan en la vista. El registro no incluye vida final porque no permite deducir con fiabilidad si ocurrió daño.

## Adaptación propuesta I3

Sala desconocida se codifica como ValorHistorico(False); avistada/explorada como ValorHistorico(True, 1/2). Puerta no observada es ausencia; abierta/cerrada es ValorHistorico(True, False/True). Por eso False no puede confundirse con ausencia. Las claves llevan prefijos `conocimiento:sala:` y `conocimiento:puerta:` con ID no negativo. La base contiene cada puerta observada una sola vez, aunque aparezca desde ambos extremos.

Estos campos guardan estado dinámico, no nombres/salidas del esqueleto ni texto del mapa. Su restauración completa necesitará el esqueleto compatible y el adaptador de presentación acordado. La conversión acepta solo tuplas de CambioConocimiento y valida ámbitos, IDs y valores. Una entrada inválida no devuelve un lote parcial; no se modifica mapa ni historia al convertir.
# I4: consulta de ruta

`ConsultaRuta` es inmutable: estado textual, siguiente ID, dirección, costo del primer paso y costo total. Los cuatro últimos campos son None cuando no hay paso, salvo costo_total=0 para llegada. `PlanificadorConocido` pertenece a un ConocimientoMapa; usa índices estables, sin guardar posición, reloj ni ruta previa. La fuente filtrada lee los estados y recuerdos actuales también después de aplicar/revertir deltas. El esqueleto no cambia durante su vida útil; para otra cripta se construyen mapa y planificador nuevos.
