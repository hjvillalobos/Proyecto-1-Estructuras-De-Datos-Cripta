# Modelo de datos propuesto

Los nombres son orientativos hasta acordarlos con motor y conocimiento; no son APIs existentes.

| Entidad | Campos mínimos | Invariantes |
|---|---|---|
| Frontera | tiempo, secuencia total, ordinal de acción, fase antes/después | Orden determinista; distingue eventos y decisiones empatados |
| RegistroCambio | frontera, categoría, identidad, antes/después o información equivalente | Incluye creación/eliminación; sin referencias mutables al estado vivo |
| BloqueAcciones | ordinal inicial/final, registros de eventos, fronteras | Hasta K acciones; eventos localizables dentro del bloque |
| PuntoControl | frontera, estado completo independiente, azar, agenda y secuencias | Solo cada K acciones más base inicial; nunca posterior a consulta |
| IndiceHistoria | entradas ordenadas de controles y fronteras | Búsqueda propia; sufijo truncable |
| ResumenHistoria | reloj consultado, sala, estadísticas, inventario, efectos, enemigos locales, mapa conocido | Datos del pasado, sin revelar esqueleto remoto |
| HistoriaPersistida | versión, K, base, controles, cambios, límite de rama, identidad | Misma historia después de recargar |

## Estado completo a auditar

Jugador y estadísticas base/actuales; inventario en orden, equipo y selección cuando afecte el juego; efectos y expiraciones; enemigos, actividad, posición, vida y próximos turnos; puertas, cierres y aperturas; trampas y objetos; rastros; agenda con prioridades, cancelaciones y secuencias; generador aleatorio; reloj y turno; conocimiento con memoria de puertas; contadores de partida y condiciones de finalización. La lista debe contrastarse con exportar/importar actuales y con motor y conocimiento.

Una ficha estática puede referenciar datos inmutables fijados por versión. No se comparte ninguna estructura mutable con la partida viva. Los deltas de existencia deben poder reconstruir entidades ya eliminadas. Los registros preservan los órdenes observables que afecten determinismo.

## Transiciones

Inicio → base; acción/eventos → anexar cambios; completar K acciones → control; consulta → estado de trabajo descartable; pergamino → recorte y nueva rama; guardar → serialización vigente; cargar → validar completamente y sustituir; replay → reconstrucción determinista sin vista.


Decisiones de fronteras y retroceso: ver Assumptions de spec.md. Constituyen el contrato de esta capacidad; las otras capacidades deben adaptar sus productores antes de la integración real. No se requiere su implementación para probar el núcleo con cambios sintéticos.

Decisión adoptada: reconstrucción aislada hacia adelante, registro tipado por evento, índice ordenado propio y correcciones de rama. Fundamento: cierres no serializables y fronteras detectadas en el motor. Alternativas y evidencia empírica pendiente no bloquean implementar el experimento; sí bloquean afirmar rendimiento.


## Contratos implementados de exportación

`AccionHistorica`: inicio, fin, cambios inmediatos, eventos y correcciones persistentes de frontera. `HistoriaGuardada`: checkpoint_cada, estado_inicial (parejas clave/valor inmutables) y acciones vigentes. Exportar no comparte estados mutables. Importar verifica tuplas, K, campos, continuidad de tiempos, cambios anteriores y orden de eventos antes de devolver una instancia nueva. Checkpoints/presente se regeneran en carga a partir de la base y los registros; no se serializan copias redundantes por acción.
