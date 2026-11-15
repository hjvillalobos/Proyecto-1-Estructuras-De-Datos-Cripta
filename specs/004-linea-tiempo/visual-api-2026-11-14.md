# VI-01..05 — presentación y auditoría API

Incremento autorizado para `004-linea-tiempo`, sobre `origin/main@049a990`, con especificación confirmada en `defa0c4` antes del código. Defensa excluida. Sin cambios en `modelo/`, `red/` ni `datos/`.

## Presentación y aislamiento

Tres PNG RGBA locales: sabueso óseo, espectro acechador y carcelero errante. Se conservan los dibujos de rata/guardián y los datos de catálogo. Un cazador futuro sin PNG específico usa el sabueso como representación de comportamiento; los demás tipos desconocidos conservan el signo neutro. Nombres, instancias y vidas siguen visibles.

El mapa Canvas usa piedra oscura, verde, ámbar y niebla estática. Recibe solo `mapa_conocido()`, posición y destino; sin referencias al modelo o precarga. Es un esquema de conexiones, sin pretender coordenadas geográficas. Admite componentes, ciclos, arcos dirigidos e IDs dispersos. Exploradas muestran nombre/salidas; avistadas, solo `?` e ID; desconocidas no tienen nodo, cantidad ni posición. La niebla tiene formas fijas independientes del mapa real. Las puertas muestran el último recuerdo, que puede haber cambiado.

Selección, detalle de nombre completo, zoom, desplazamiento, centrado y listado. Viajar hacia una explorada devuelve `ir a ID`, encolado por la GUI después del modal. Consola y controlador ordinario conservados. Ordenamiento propio y búsqueda binaria: preparación O((V+E) log V), espacio O(V+E); disposición lineal tras resolver IDs. Dibujo al abrir, seleccionar o ampliar; sin animación de niebla, HTTP, activación de contenido ni trabajo añadido por evento del motor.

## Contrato vigente

Inspección directa del [OpenAPI oficial](https://cripta-api.kad06a0zhgs84.us-east-2.cs.amazonlightsail.com/openapi.json), versión **1.1.0**, contrastado con cliente/precarga/catálogo. Copia consultada local: `.cache/api-visual-openapi.json`.

| GET publicado | Integración existente |
|---|---|
| `/v1/criptas` | Listado y selección |
| `/v1/criptas/{dungeon_id}` | Generales, versión y presupuesto |
| `/v1/criptas/{dungeon_id}/version` | Compatibilidad de cripta |
| `/v1/criptas/{dungeon_id}/salas` | Esqueleto paginado, salidas, puertas, costos |
| `/v1/criptas/{dungeon_id}/contenido` | Instancias de enemigos, objetos y trampas por lote |
| `/v1/criptas/{dungeon_id}/llaves` | Ubicaciones, incluidas las de enemigos |
| `/v1/catalogo/version` | Compatibilidad de catálogo |
| `/v1/catalogo` | Fichas por lote; atributos conservados |
| `/v1/catalogo/{catalog_id}` | Alternativa individual cubierta por la petición por lote, sin solicitudes innecesarias |

No hay endpoint de imágenes. No falta una ruta necesaria para las capacidades exigidas en los datos publicados inspeccionados. Se contrastaron comportamiento/rango, estadísticas, costos/puertas, objetos/equipo/efectos y llaves. Las siete clases de objetos ya están implementadas.

OpenAPI permite algunos opcionales/nulos más amplios que los datos conformes del enunciado: se conservan las interpretaciones vigentes de A, sin normalizar costos malformados ni inventar rango para un cazador sin ese campo. `rango=null` explícito sigue siendo ilimitado y costo ausente sigue siendo 100; no se declara soporte nuevo para datos contradictorios.

## API y contenido reales

`CRIPTA_API_REAL=1 python -B -X utf8 -m unittest tests.test_verificacion_entrega.TestApiRealEntrega -v`: **una prueba, 87.563 s, OK**, UUID por proceso, fases fría/caliente y presupuesto sin cambios. Catálogo `4b9e75a42be5`. Log local `.cache/mapa-visual-api.log`.

| Cripta | Versión | Fría / límite | Caliente | Dictamen |
|---|---|---:|---:|---|
| cripta-02 | 52532a77ee04 | 13 / 23 | 3 | resoluble |
| cripta-03 | f9186ac25124 | 16 / 42 | 3 | resoluble |
| cripta-04 | 7074a17814ad | 17 / 52 | 3 | resoluble |
| cripta-05 | 48bfa3b75055 | 14 / 25 | 3 | no resoluble |
| cripta-06 | f9ed9afa683d | 46 / 63 | 3 | resoluble |

Auditoría offline completa adicional mediante `GestorPrecarga.preparar_entrada` y fábrica normal: 300 salas de cripta-06, 75 enemigos, 36 cazadores; costos positivos y estadísticas enteras comprobados, cero HTTP. Cinco tipos encontrados: rata gigante, sabueso óseo, espectro acechador, guardián óseo y carcelero errante. Los cinco tienen ahora imagen.

## Validación

Siete casos en `tests/test_mapa_visual.py`: privacidad ante información oculta incluida por error, determinismo, IDs uint32 dispersos, ciclo de 1.000 salas, estado real inmutable/HTTP bloqueado, controles, viaje y transparencia/cache. Se conservan las pruebas existentes.

Inspección nativa: arranque offline normal, verificador, Jugar, botón Mapa y cierre sin avanzar t=0 ni añadir acciones al log. Una segunda ventana titulada **revisión de arte, sin partida** permitió ver juntos los tres enemigos y un mapa preparado de seis salas: selección, detalle, puertas, destino, zoom, listado y cierre. Esa preparación no se presenta como partida natural.

La primera regresión detectó la firma inválida de las composiciones tras modificar recursos (828 casos, dos fallos/nueve errores de composiciones, dos opciones omitidas). Log preservado `.cache/mapa-visual-suite.log`. Se regeneraron 152 composiciones con `python -m utilidades.preparar_visuales` para conservar su carga preparada. Comparadas contra Git: tamaño, modo y bytes de píxeles idénticos en las 152; cambia la firma de procedencia. Después pasaron los 14 casos de composiciones y mapa. No se debilitaron las pruebas ni la validación de firmas.

Regresión final: **828 pruebas en 214.910 s, cero fallos/errores, OK (skipped=2)**. Log local `.cache/mapa-visual-suite-final.log`. Opciones: comparación de revisiones históricas (ejecución anterior separada, 41 pruebas OK) y API real (repetida arriba). El paquete oficial histórico también se habilitó mediante `CRIPTA_PAQUETE_API`; sus pruebas pasaron. No se promete igualdad temporal exacta bajo cualquier carga del sistema.

## Copia limpia y rendimiento

Aceptación adicional desde copia de fuentes sin cachés ni partidas: `python -m utilidades.verificar_copia_limpia`, **20 pruebas en 6.476 s, OK**. Reutiliza el intérprete y dependencias instalados; este verificador no copia PNG ni sustituye la inspección gráfica anterior.

Repetición aislada RC-01, mismo equipo/paquete/semilla, cinco series alternadas de 120 ciclos por productor, 30 cazadores inyectados e historia/mapa completos; sin GUI, suite o HTTP concurrentes. Estado, historia y azar iguales en las cinco parejas. Anterior: mediana 11.7441 ms, máximo 94.1802 ms, 5/600 sobre 20. Optimizado vigente: mediana **4.1807 ms**, máximo **9.1013 ms**, **0/600 sobre 20**. El incremento visual no modifica el código de ese motor; la diferencia respecto a muestras anteriores no se atribuye al arte.

Se conserva una muestra auxiliar de viaje de **5.5273 ms**, 1/600 sobre 5 ms (anterior: máximo 3.3851 ms, 0/600). El planificador permanece intacto y el antecedente RC-01 ya contenía un pico de 5.168 ms; no se declara cumplimiento absoluto de la cota de viaje. Preparación pura del mapa de 1.000 nodos/arcos, 30 repeticiones: mediana 9.6051 ms y máximo 13.7702 ms, excluye dibujo Tk y no es latencia de evento. [Muestras completas, entorno y conteos](visual-mediciones.json).

## Trazabilidad

| Requisito | Código | Evidencia |
|---|---|---|
| VI-01 | PNG, recursos_graficos, escena | Alpha, cache, tipos y revisión de arte |
| VI-02 | mapa_visual | Privacidad, IDs, ciclos, dirigidas y listado |
| VI-03 | controlador._mapa, grafica.mostrar_mapa | Comando ordinario y destino explorado |
| VI-04 | Proyección aislada y modal estático | Estado igual, HTTP bloqueado, regresión y benchmark |
| VI-05 | Cliente/precarga/catálogo existentes | Nueve rutas, cinco criptas fría/caliente y contenido completo |

Prompts/procedencia en `PROMPTS_LLM.md` y `vista/recursos/README.md`.
