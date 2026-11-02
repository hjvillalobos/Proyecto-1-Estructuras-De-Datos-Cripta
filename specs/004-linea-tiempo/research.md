# Alternativas y decisiones a validar mediante mediciones

| Problema | Alternativas | Propuesta y motivo | Evidencia necesaria |
|---|---|---|---|
| Reconstrucción | Reejecutar acciones, aplicar deltas, invertir deltas desde presente | Deltas hacia adelante: evita red y volver a decidir reglas; exige captura exhaustiva | Comparar dirección, igualdad de estados y tiempo |
| Índice temporal | Recorrido lineal, búsqueda binaria propia sobre índice ordenado | Búsqueda binaria propia: checkpoints se agregan ordenados y se recortan por sufijo | Búsquedas al inicio/medio/final con historias largas |
| Registro | Copia por acción, cambios por eventos | Cambios por eventos y fronteras de acciones para permitir t intermedio | Memoria frente a tamaño del mundo y número de cambios |
| Recorte | Recorrer todo, sufijos segmentados | Final lógico y liberación de sufijo | Medir prefijos crecientes con mismo sufijo retirado |
| K | 10, 50, 100, sin controles | 50 solo candidato, sin afirmación de optimalidad | Bench >= 5 000 acciones y variación |
| Compatibilidad | Migrar P1, rechazar explícitamente | Rechazar en primer incremento reduce ambigüedad | H6 y conservación del archivo original |

Fuentes primarias locales: enunciado Parte II y constitución compartida. No se realizaron experimentos. Tampoco se consultó documentación externa para afirmar detalles nuevos de spec-kit: el flujo utilizado como referencia es el ya versionado por el grupo.


Decisiones de fronteras y retroceso: ver Assumptions de spec.md. Constituyen el contrato de esta capacidad; las otras capacidades deben adaptar sus productores antes de la integración real. No se requiere su implementación para probar el núcleo con cambios sintéticos.

Decisión adoptada: reconstrucción aislada hacia adelante, registro tipado por evento, índice ordenado propio y correcciones de rama. Fundamento: cierres no serializables y fronteras detectadas en el motor. Alternativas y evidencia empírica pendiente no bloquean implementar el experimento; sí bloquean afirmar rendimiento.
