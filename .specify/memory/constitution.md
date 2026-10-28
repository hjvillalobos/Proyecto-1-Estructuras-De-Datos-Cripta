# CRIPTA Constitution

## Core Principles

### I. Estructuras de Datos Propias (NO NEGOCIABLE)

Las estructuras de datos de los problemas evaluados DEBEN implementarse a mano.
Está prohibido usar `dict`, `set`, `heapq`, `bisect`, `collections` (deque,
OrderedDict, defaultdict, Counter), `networkx` o cualquier biblioteca de grafos
o búsqueda de rutas como índice, caché o estructura principal en los problemas
de §5 del enunciado. Los ordenamientos DEBEN ser propios. La caché ordenada con
LRU y búsqueda binaria de la Parte I se conserva; no se sustituye por tabla hash.

### II. Determinismo (NO NEGOCIABLE)

La misma cripta, la misma semilla y la misma secuencia de acciones DEBEN producir
exactamente la misma partida en cualquier ejecución. Toda fuente de aleatoriedad
DEBE pasar por un generador con semilla controlada. Los puntos de control de
la línea de tiempo DEBEN incluir el estado del generador cuando se reconstruye
por simulación.

### III. Separación MVC

El motor, las reglas de tiempo virtual y el verificador de resolubilidad son
independientes de la vista. `--replay`, `--bench` y `--verificar` NO DEBEN
instanciar componentes de la vista. Los módulos de red, modelo y datos NO DEBEN
depender de la vista. La organización concreta de archivos se documenta en el plan técnico.

### IV. Especificación Antes que Código

Una especificación (`spec.md`) DEBE confirmarse en Git antes que cualquier cambio
de código que la implemente. Si durante la implementación se descubre que la
especificación estaba mal, se corrige primero la especificación en un commit
separado y luego el código. Una especificación desactualizada respecto del
programa entregado es un defecto del mismo tipo que código sin especificación.
El flujo obligatorio es: `constitution` → `specify` → `clarify` → `plan` →
`tasks` → `analyze` → `implement`.

### V. Cero Datos de Criptas Particulares en Código

Ningún dato de una cripta concreta (IDs, nombres de salas, ubicaciones de llaves,
estadísticas de enemigos) DEBE estar escrito en el código fuente. Todo dato de
cripta proviene del servicio web o de los archivos locales descargados.

### VI. Presupuesto de Red Respetado

Toda solicitud HTTP, incluidos reintentos y consultas de versión, DEBE contarse
contra `presupuesto_solicitudes`. El identificador de cliente UUID DEBE mantenerse
durante toda la ejecución. La precarga y el adaptador offline NO DEBEN revelar
al jugador información obtenida por haberla descargado anticipadamente.

### VII. Rendimiento Medido con Evidencia

Toda afirmación de rendimiento DEBE respaldarse con `--bench`. Los límites son:
ciclo de eventos ≤ 20 ms con decenas de cazadores activos; verificación de
resolubilidad ≤ 200 ms en la cripta más grande publicada; consulta `historia`
≤ 50 ms para partidas de al menos 5 000 acciones con el K por defecto; cálculo
de un paso de «ir a» ≤ 5 ms con el mapa conocido completo. Las criptas sintéticas
de `--bench` DEBEN ser deterministas por semilla.

## Reproducibilidad y Documentación Técnica

- Las tecnologías, versiones, dependencias, herramientas, agente y organización
  de archivos DEBEN documentarse en los planes técnicos correspondientes.
  Las restricciones tecnológicas impuestas por los enunciados siguen siendo
  obligatorias y DEBEN quedar identificadas como requisitos externos en esos planes.
- El README DEBE incluir las instrucciones necesarias para preparar el entorno,
  ejecutar el proyecto y reproducir sus pruebas y mediciones desde una copia limpia.
- Toda dependencia DEBE justificarse y respetar las restricciones académicas.
  Declararla en un archivo de dependencias no autoriza su uso en los problemas evaluados.
- La configuración compartida y los artefactos del proceso de especificación DEBEN
  versionarse. Las credenciales y los secretos NO DEBEN incorporarse al repositorio.
- El formato binario de guardado se versiona; los formatos anteriores DEBEN
  detectarse como incompatibles o migrarse explícitamente, nunca cargarse en
  silencio.

## Flujo de Desarrollo

- Cada capacidad nueva sigue el flujo spec-kit completo antes de implementarse.
- Cada requisito funcional tiene un identificador estable (FR-XXX).
- Cada caso del Apéndice B del enunciado DEBE aparecer como escenario de
  aceptación en alguna `spec.md` y tener al menos una prueba automatizada o
  `partida.log` que lo ejercite; la prueba cita el identificador del requisito.
- Cada invocación de un comando de spec-kit con texto propio se registra en
  `PROMPTS_LLM.md` con fecha, herramienta/modelo, texto original y uso de la
  respuesta.
- Los PRs se integran en incrementos pequeños con revisión cruzada (A↔C, B↔D).
- Las mediciones finales van en `DECISIONES.md`; el `plan.md` de cada capacidad
  puede enlazarse desde allí sin duplicar texto.

## Governance

Esta constitución tiene precedencia sobre las prácticas internas del proyecto,
sin sustituir ni contradecir los enunciados y las aclaraciones del profesor.
Toda enmienda DEBE:
1. Incrementar la versión según semver (MAJOR: principio eliminado o redefinido;
   MINOR: principio nuevo o ampliado; PATCH: aclaración o corrección de redacción).
2. Registrarse en `PROMPTS_LLM.md` si fue asistida por un LLM.
3. Confirmarse en Git con mensaje `docs: amend constitution to vX.Y.Z (motivo)`.

Todo plan (`plan.md`) y toda tarea (`tasks.md`) generados por el agente DEBEN
revisarse para detectar violaciones al Principio I antes de confirmarlos.
Si el agente propone `heapq`, `dict` como índice u otra estructura prohibida,
el grupo DEBE corregirlo en la fase de plan, no en la de implementación.

**Version**: 1.1.0 | **Ratified**: 2026-10-22 | **Last Amended**: 2026-10-27
