# Estado vigente y trazabilidad de entrega

Rama `004-linea-tiempo`. Este documento distingue la entrega integrada de los registros fechados de desarrollo. Defensa excluida. Las cuatro capacidades funcionan desde la aplicación normal, con historia, conocimiento y persistencia conjuntos. Las anotaciones antiguas de entregas parciales no representan capacidades ausentes.

## Reglas e interpretaciones vigentes

- Terreno: costo ausente 100; datos declarados válidos positivos. El motor consume el contrato de datos; no inventa normalizaciones de valores malformados ni salidas inversas. Un `rango=null` explícito es ilimitado según la aclaración comunicada por el usuario; no se inventa un rango por defecto para un cazador sin ese campo.
- Antorcha: explora vecinas y revela nombre/salidas; las puertas solo se observan desde la posición ocupada. No hay observación de puertas remotas ni activación de contenido remoto. Q1 de C deja de ser un bloqueo técnico por la autorización e interpretación documentadas en IA-05.
- Resolubilidad: acumulación de llaves sin trayectoria única aceptada según aclaración registrada del 2026-11-02; se informa esa limitación. Normalización O(N log N), recorrido/diagnóstico lineales más reporte; evidencia empírica para el crecimiento aproximadamente lineal, sin afirmar O(N) total estricto.
- Referencia de medición local: paquete `cripta-06@f9ed9afa683d`, 300 salas. Los resultados corresponden a esa versión; no se inventa una enmienda que cambie los límites 20/200/50/5 ms. Los cazadores inyectados y el mapa completo se identifican como preparación experimental.
- Autorización: la usuaria permite mejorar A/B/C/D. Los límites de propiedad y permisos de las fases individuales quedaron superados para esta integración. No equivale a afirmar una revisión cruzada humana que no se realizó.

## Enunciado punto por punto, sin defensa

| Sección Parte II | Implementación / evidencia |
|---|---|
| 2.1–2.3, herramientas y constitución | README fija spec-kit v1.2.3/Codex; `.specify/`, `.agents/skills/` y constitución versionados. |
| 2.4–2.6, especificación, tareas y proceso | Cuatro carpetas de capacidades con spec/plan/tasks; matriz del Apéndice B abajo; PROMPTS_LLM y antecedentes Git. Salvedades históricas al final. |
| 3.1, terreno | `modelo/juego.py`, `modelo/rutas.py`; tests de costos y velocidad de terreno. |
| 3.2, cazador | `modelo/cazador.py`, rutas propias; pruebas de decisión, turnos, localidad y rutas. |
| 3.3, conocimiento | `modelo/conocimiento.py`, `modelo/partida.py`; pruebas de entrada, antorcha e historia. |
| 3.4, viaje | `modelo/viaje.py`, controlador; pruebas de detención y hechos reales de movimiento. |
| 3.5, verificación | `modelo/resolubilidad.py`, `red/verificacion.py`; pruebas sintéticas, offline e inicio bloqueado/forzado. |
| 3.6, historia | `modelo/linea_tiempo.py`, `modelo/partida.py`, persistencia y replay; pruebas por tiempo, ordinal, K, recorte, empates y carga. |
| 4.1–4.3, servicio | Cliente/precarga/catálogo, versiones, ubicaciones de llaves y presupuesto; pruebas de API y modo offline. |
| 5.1–5.2, rutas e invalidación | Dijkstra propio limitado, campo compartido ilimitado y descarte de derivados; bench terreno-cazador y parte-dos comparan alternativas/puertas cambiantes. |
| 5.3, mapa | Índices propios, actualizaciones locales y deltas reversibles; tests de secuencias y ausencia de copia completa al registrar eventos. |
| 5.4, resolubilidad | Incremental frente a recorrido repetido por llave; diagnóstico global y ciclos deterministas; bench incluye normalización/reporte. |
| 5.5, puntos de control | K=50; comparar 10/50/100/sin controles, consultas <=K acciones y recorte de sufijo; evidencia en DECISIONES. |
| 5.6, estructuras de Parte I | Bench terreno-cazador compara agendas e historiales con la carga nueva; parte-dos mide el ciclo integrado. |
| 6.1–6.3, límites/restricciones | Bench sin vistas/red; estructuras y ordenamientos propios. Fortalecimiento mide el heap anterior y optimizado con decisiones iguales. |
| 7.1–7.3, documentos y comandos | DECISIONES, PROMPTS, README, specs, mapa, viaje, historia y reporte inicial disponibles; consola y GUI probadas. |

## Los 23 casos obligatorios del Apéndice B

Rutas de esta tabla relativas a la raíz. La prueba indicada se ejecuta con `python -m unittest tests.NOMBRE_SIN_EXTENSION`. Las especificaciones conservan los escenarios y las tareas originales; IC y RF documentan su integración y fortalecimiento.

| Caso | Requisito / escenario / tarea | Código | Prueba |
|---|---|---|---|
| T1 sin ruta: espera 100 | A FR-008/009, T1, T020–022 | cazador/rutas | tests/test_decision_cazador.py |
| T2 fuera de rango: espera | A FR-009, T2, T020–022 | cazador/rutas | tests/test_turno_cazador.py |
| T3 menor costo, más salas | A FR-008, T3, T019–021 | rutas | tests/test_rutas_cazador.py |
| T4 empate por menor vecino | A FR-010, T4, T026 | rutas | tests/test_rutas_cazador.py |
| T5 cierre entre turnos | A FR-013, T5, T029/033 | rutas/juego/efectos | tests/test_validez_rutas.py, test_rutas_compartidas.py |
| T6 intervalo mínimo 1 | A FR-002/003, T6, T011/015 | juego | tests/test_costos_terreno.py |
| T7 velocidad durante tránsito | A FR-005/006, T7, T012 | juego/efectos | tests/test_velocidad_terreno.py |
| N1 destino sin explorar | C FR-007, C21, T018–019 | conocimiento_rutas | tests/test_conocimiento_rutas.py |
| N2 puerta recordada abierta | C FR-004/008/010, C23/C27, T018/022–024 | conocimiento/viaje | tests/test_conocimiento_rutas.py, test_controlador_viaje.py |
| N3 enemigos dormidos detienen | C FR-009/011, C28, IC-04 | juego/viaje/controlador | tests/test_controlador_ac_real.py, test_hechos_paso_motor.py |
| N4 antorcha sin activar vecinos | C FR-006, N4, IC-02 | partida/juego | tests/test_partida_completa.py, test_entrada_conocimiento_motor.py |
| N5 retroceso de exploración | C FR-014, C12/N5, IC-02 | conocimiento/historial | tests/test_partida_completa.py, test_conocimiento_historia.py |
| N6 retroceso último paso y parada | C FR-015, C29/N6, IC-04 | viaje/partida | tests/test_controlador_viaje.py, test_viaje.py |
| R1 llave autoencerrada y ciclo | B FR-005, AC-06, T015–016 | resolubilidad | tests/test_resolubilidad.py |
| R2 llave soltada por errante | B FR-003/010, AC-03, T005/010 | verificación/resolubilidad | tests/test_resolubilidad.py, test_verificacion_datos.py |
| R3 orden determinista | B FR-004/007, AC-04, T005/012 | resolubilidad | tests/test_resolubilidad.py |
| R4 bloqueo sin forzar | B FR-013 y D FR-016, AC-15, T025–026/IC-01 | aplicación/verificación | tests/test_modos_historia.py, test_verificacion_entrega.py |
| H1 rechazar futuro | D FR-001/020, H1, T004/006 | linea_tiempo | tests/test_linea_tiempo.py |
| H2 recorte tras pergamino | D FR-007, H2, T008/009/IC-03 | partida/linea_tiempo | tests/test_controlador_ac_real.py, test_historia_motor.py |
| H3 todos los eventos empatados | D FR-002, H3, T003/004/006 | juego/linea_tiempo | tests/test_frontera_temporal.py, test_historia_motor.py |
| H4 consulta sin efectos ni log | D FR-005, H4, T004/006 | controlador/linea_tiempo | tests/test_controlador_ac_real.py |
| H5 replay hasta después del fin | D FR-014, H5, T012/014 | replay_sin_vista | tests/test_modos_historia.py |
| H6 archivo P1 incompatible | D FR-012, H6, T008/011 | guardado_binario | tests/test_controlador_ac_real.py, test_persistencia_historia.py |

Los cuatro prefijos A/B/C/D identifican su carpeta de especificación. La cobertura de Parte I se conserva en las regresiones heredadas, incluyendo combate, inventario, efectos, cancelación, retroceso, caché, presupuesto, guardado y replay. Esta tabla no sustituye ejecutar las pruebas.

## Cierre comprobado del fortalecimiento

Regresión final: **815 pruebas en 220.346 s, cero fallos y cero errores**, dos omisiones opcionales con ejecución separada aprobada: comparación histórica (41 pruebas) y API oficial (cinco criptas, caché fría/caliente dentro de presupuesto). Copia limpia de fuentes sin datos locales mediante `python -m utilidades.verificar_copia_limpia`; no reinstala las dependencias.

| Operación | Máximo final | Límite | Excesos |
|---|---:|---:|---:|
| Ciclo con 30 cazadores e historia/mapa | 14.017 ms | 20 ms | 0/60 |
| Paso de viaje conocido | 2.501 ms | 5 ms | 0/60 |
| Verificador completo | 7.855 ms | 200 ms | 0/10 |
| Historia K=50, 5.000 acciones | 0.9363 ms | 50 ms | 0/185 |

El heap redujo su mediana pareada de 4.3523 a 2.2538 ms, con decisiones iguales. El motor ahora permite IDs uint32 muy dispersos sin reserva proporcional al mayor ID; hay una partida completa automatizada con esos IDs. [Salidas completas, semilla y entorno](specs/004-linea-tiempo/fortalecimiento-mediciones.json), análisis y alternativas en DECISIONES.md. Las tablas de pruebas se solapan y no se suman.

## Salvedades históricas conservadas

Dos finales de prompts de A no se conservan íntegros y el commit histórico `33d97ac` reunió aclaración y código. No se inventan textos ni se reescribe ese hecho. El PDF original local de Parte I está vacío; se conserva la extracción previa. Las mediciones no garantizan una calificación o cero bugs futuros. Resultados de fortalecimiento y reproducción en DECISIONES.md y README.md.

Actualización de publicación con A dff5882: suite 815, OK; integración específica 44, OK. El benchmark posterior registró un ciclo de 20.282 ms (1/60 sobre 20); repetido aisladamente dio 19.783 ms (0/60). Paso conocido 4.208 ms y repetición 2.341 ms, ambos bajo 5. Se conserva la variación como límite de rendimiento, sin ocultar la muestra excedida.
