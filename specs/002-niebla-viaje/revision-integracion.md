# Revisión conjunta — 10 de noviembre de 2026

## Actualización del 12 de noviembre

La rama de C se actualizó de 62e457c a d796dae mediante avance directo desde `origin/004-linea-tiempo`, sin conflictos ni cambios en main. Incluye main a895d85 y los avances de A integrados por D hasta 53c9453. Los commits posteriores de A, 0b6f1c4 y f318757, no se incorporaron. Los módulos centrales de conocimiento, rutas, viaje e inventario histórico de C conservaron su contenido. Los puntajes locales se respaldaron y su SHA-256 permaneció igual.

Verificación en una exportación limpia de d796dae, Python 3.12.10 y `CRIPTA_SIN_AUDIO=1`: `python -B -m unittest discover -s tests -v` terminó con **753 pruebas en 100.664 s, OK, seis omisiones**. Dos requieren paquete oficial, una API real, dos el productor histórico completo del motor normal y una corresponde al conjunto de comparación de revisiones de C. Ese último conjunto se comprobó aparte con `utilidades.verificar_conocimiento_rutas`: **41 pruebas, OK, sin omisiones**. La selección de conocimiento, inventario histórico, controlador de viaje, presentación, entrada al motor, receptor H3 y restauración aprobó **90 pruebas**. Los conjuntos se solapan; no sumar sus conteos. Logs locales: `.cache/revision-integrada-20261112.log`, `.cache/revision-c-integrada-20261112.log` y `.cache/revision-rutas-20261112.log`.

La compatibilidad probada no equivale a viaje completo habilitado. D consume `ControlViaje` y `ResultadoPaso`; el motor normal aún no entrega `control_viaje` ni los hechos generales de movimiento. El conocimiento/historia de A sigue bajo activación explícita de prueba, y su preparación de conocimiento rechaza salidas con puertas. Identidad de puertas, observaciones, integración general y Q1 siguen pendientes de sus acuerdos. No se modificaron esos contratos ni código de compañeros durante esta revisión.

## Revisión anterior

Se ensayó la unión en `.cache/revision-integracion-20261110`, una copia local separada. No se modificaron main ni las ramas de los compañeros.

| Parte | Rama | Commit revisado |
| --- | --- | --- |
| A | feature/motor-eventos | 9730482 |
| B | codex/verificador-resolubilidad | 694dcf6 |
| C | codex/002-niebla-viaje | 3198f55 |
| D | 004-linea-tiempo | 02da6b6 |

## Conflictos al unir

Se partió de B y se añadieron A, D y C, en ese orden.

- A/B: dos filas de `specs/001-terreno-cazador/contracts/integracion.md`. Se conservaron los requisitos actualizados de A y la evidencia de B, todavía pendiente de revisión de A.
- D: `main.py`, `red/sesion.py`, `tests/test_criptas_api.py` y `PROMPTS_LLM.md`. En el ensayo se mantuvo la versión explícita de B, la preparación sobre el almacén destino y el diagnóstico offline de D. La prueba conserva la comprobación de B y la versión simulada de D.
- C: solo `PROMPTS_LLM.md`; sus módulos y pruebas se añadieron sin conflictos textuales. Se conservaron los bloques de ambas bitácoras. Falta revisar su orden y posibles duplicados antes de una integración definitiva.

## Pruebas

Comando, con `CRIPTA_SIN_AUDIO=1`: `python -B -m unittest discover -s tests -v`.

Primera corrida: 672 pruebas, 5 fallos, 3 errores y 5 omisiones. Los fallos/errores corresponden a seis métodos, contando subcasos. El tiempo registrado no se usa como medición de rendimiento: una prueba de reinicio entró en un ciclo de reintentos y terminó con MemoryError.

Se ajustó únicamente la preparación de esos seis casos en la copia: dimensiones del menú oculto, dobles de escena/sonido, paquete temporal para reinicio y ausencia explícita de llaves en los dos casos que la exigen. Se conservaron sus aserciones. Los seis pasaron en 2.423 s. El [parche propuesto](contracts/ajustes-pruebas-integracion.patch) contiene 12 líneas añadidas y 3 retiradas; no está aplicado a las ramas originales.

Repetición completa: **672 pruebas en 67.257 s, OK, con 5 omisiones**; 667 aprobadas. Dos omisiones requieren el paquete oficial, una requiere habilitar API real y dos siguen pendientes de captura/restauración histórica del motor. No se eliminaron pruebas ni se presentaron las omisiones como éxitos. Logs locales: `.cache/integracion-suite-20261110.log` y `.cache/integracion-suite-corregida-20261110.log`.

## Conexiones que faltan

| Responsables | Cambio necesario |
| --- | --- |
| A/C | Entregar daño ocurrido y enemigos al entrar; conectar conocimiento, observaciones y sus cambios al mismo turno del motor. |
| C/D | Conectar mapa y ControlViaje al controlador. El callback booleano actual no aporta todos los hechos y debe permitir cancelación entre pasos. |
| A/C/D | Agregar cambios de inventario/conocimiento al productor histórico y coordinar rollback, pergamino y restauración. El productor H3 actual solo cubre un caso acotado. |
| A/C y B | Conectar el despacho del cazador con sus datos y acordar identidad compartida de puertas. El motor sigue llamando al despacho previo. |

Los módulos de C existen y sus pruebas se ejecutan en la copia, pero el motor no los instancia. Tampoco expone todavía `conectar_historia` y la restauración completa que espera D. Por eso una fusión sin conflictos no habilita mapa, viaje e historia completos. La aclaración de antorcha y la medición integrada siguen pendientes.
