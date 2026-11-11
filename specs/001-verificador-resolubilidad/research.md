# Investigación del verificador de resolubilidad

Fecha: 2026-11-01. Estado: decisiones documentadas y recomendaciones aplicadas; C1 cerrado con aclaración del profesor comunicada por el usuario el 2026-11-02. No se implementó ni se midió el verificador.

## Reutilizar red y persistencia

**Decisión:** ampliar `ClienteApi`, `ClienteOffline` y `AlmacenLocal`.

**Motivo:** `_hacer_peticion_get` ya cuenta intentos, conserva UUID y maneja 429. El almacenamiento ya separa versiones y reemplaza archivos mediante temporales. No existe todavía `obtener_llaves`.

**Alternativa rechazada:** cliente independiente, por duplicar presupuesto y mezclar análisis con adquisición.

## Separar verificar de iniciar partida

**Decisión:** extraer preparación común de generales/esqueleto en `GestorPrecarga`, conservando regresiones del inicio.

**Motivo:** `preparar_cripta` actualmente inicia catálogo, descarga candidatas y prepara la entrada inicial. No hace falta para verificar.

**Alternativa rechazada:** ejecutar todo y descartar contenido, por costo y acoplamiento innecesarios.

## Índices y cola

**Decisión propuesta:** arreglos ordenados mediante `utilidades.ordenamiento.ordenar` en modo fusión, búsqueda binaria propia y referencias enteras densas. Cola mediante lista e índice de lectura.

**Motivo:** los índices son estáticos durante la verificación. No hay beneficio demostrado de AVL. IDs dispersos no deben dimensionar arreglos por máximo ID.

**Alternativas rechazadas:** búsquedas lineales por arista pueden volverse cuadráticas; hash y colas de bibliotecas están prohibidos. Se contabiliza la normalización con factores logarítmicos, además del recorrido.

## B1: cierre incremental y conexiones sin regreso

**Decisión adoptada:** una sala se procesa una vez. Cada puerta cerrada encontrada espera en la lista de su llave; obtenerla reactiva solo esas puertas. Varias ubicaciones no duplican la llave.

**Ventaja:** evita un recorrido completo por llave y obtiene la frontera desde el análisis.

**Problema demostrado:** el inventario global puede unir recorridos incompatibles.

Ejemplo sintético:

- Inicio tiene salida abierta hacia A, sin regreso; A contiene K.
- Otra salida desde Inicio es una puerta cerrada que requiere K y lleva a Salida.
- K es la llave de salida y no tiene otra ubicación.
- El cierre incorpora A, obtiene K y abre la puerta desde Inicio.
- Un jugador que fue a A no puede volver a Inicio: no hay una trayectoria ganadora.

**Fuentes revisadas:** PDF original P1 §2.1 y §2.5 no garantiza expresamente regreso; copia textual P2 §3.5 exige poder ganar desde el inicio y §5.4 exige crecimiento aproximadamente lineal. El contrato OpenAPI revisado antes describe `Exit` como salida dirigida. La especificación también admite conexiones de un sentido.

**Resolución B1 autorizada:** el usuario solicita registrar y adoptar el cierre acumulativo con su limitación. AC-21 fija el resultado del ejemplo como resoluble bajo ese modelo. Se conserva como opción preferida con intención de consolidarla, no como regla confirmada oficialmente ni como garantía de trayectoria. No se asigna una probabilidad objetiva a su futura aceptación.

**Alternativas:**

1. Reversibilidad garantizada por las reglas: permite justificar el cierre bajo esa garantía y actualizar la especificación.
2. Cierre abstracto expresamente aceptado: requiere aclarar el criterio de aceptación.
3. Búsqueda exacta por posición e inventario: puede requerir hasta V multiplicado por 2 elevado a K estados. No se adopta porque no sustenta el objetivo aproximadamente lineal y complica el código.

## Diagnóstico de ciclos

**Decisión:** no proyectar automáticamente una dependencia obligatoria desde cada puerta a todas las llaves que aparecen detrás de ella. Una ubicación o ruta alternativa puede invalidarla.

**Diseño adoptado:** conservar alternativas y requisitos conjuntos. Alcanzar una entrada exige origen accesible y llave cuando está cerrada; salas y llaves se habilitan mediante cualquiera de sus alternativas.

Decisión final del diagnóstico: mantener el certificado global del cierre (todas las alternativas de una condición OR falsa siguen pendientes; cada paso AND falso tiene algún requisito falso) y usar Kosaraju solo para describir las relaciones circulares de ese certificado. Ninguna condición pendiente puede activarse primero, lo que prueba la inaccesibilidad bajo el modelo acumulativo. Las componentes permiten reportar ciclos, no sustituyen esa justificación.

Mostrar todas las componentes con llaves, integrantes, un ciclo concreto por componente y referencias a alternativas internas/externas. Distinguir bloqueo circular autónomo, dependencia con bloqueos externos y ciclo en región desconectada. Los externos se explican con el mismo certificado, sin exigir una prueba autónoma por SCC. Se conserva toda la evidencia sin enumerar todos los ciclos simples ni expandir cada dependencia por llave. AC-24 y AC-25 cubren la limitación del diseño anterior.

**Alternativas rechazadas:** recorrer toda la cripta por cada llave contradice §5.4; enumerar todos los ciclos simples puede ser exponencial; inventar ciclos por mera desconexión es incorrecto.

## Criterios aceptados y autoridad

**Decisión mantenida:** múltiples ubicaciones son alternativas; llave ausente de listado completo válido es imposible de obtener. Fallos de información impiden verificar.

El usuario comunicó «exacto» del profesor ante la pregunta compuesta. La respuesta respalda las ubicaciones alternativas, pero no distingue explícitamente las dos opciones sobre ausencia. El usuario pidió mantener el criterio acordado. No se atribuye al profesor una respuesta más específica.

## Validación y siguiente paso

**Decisión:** reutilizar `unittest` y entregar a D funciones de medición para la infraestructura de `bench.py`. Generadores sintéticos locales con semilla, sin afectar azar de partida.

Medir normalización, análisis y diagnóstico, total y conteos; disco/red aparte. Comparar primero resultado lógico y órdenes válidos frente al recorrido repetido. No afirmar cumplimiento sin evidencia.

B1 adoptado para planificación mediante autorización explícita, y confirmado después por el profesor según comunicación del usuario del 2026-11-02; C1 queda aprobado. Modelo de datos, contrato y guía de validación documentados. Siguen tareas, análisis de consistencia y commit de especificación antes del código. Una aclaración oficial incompatible obliga a revisar el alcance, no a ocultar el contraejemplo.

## Recomendaciones aplicadas tras speckit-analyze

C1: inicialmente pendiente; cerrado el 2026-11-02 por la respuesta afirmativa del profesor transmitida por el usuario. I1: sustituida la certificación incompleta por SCC por certificado global del cierre y descripción completa de componentes/alternativas. La prueba global explica todos los pendientes; no se promete enumeración de causas mínimas. U1: retener lote nuevo en memoria hasta comprobación final; probar ejecución posterior y conservar copias válidas. A1: normalización O(N log N), recorrido O(N), diagnóstico O(N + reporte); medir todo y mantener el requisito académico sin relajarlo por redacción.

## Cierre de C1 — 2026-11-02

El 2026-11-02 el usuario comunicó que el profesor respondió afirmativamente a «Podemos acumular llaves entre salas alcanzables sin exigir una trayectoria única ?». Se registra como aclaración del profesor transmitida por el usuario, no como comunicación consultada directamente. La aclaración sustituye el carácter provisional del alcance descrito en las decisiones históricas anteriores. No aprueba algoritmos, rendimiento ni tareas de implementación.
