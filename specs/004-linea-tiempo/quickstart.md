# Guía de implementación y validación

Rama 004-linea-tiempo. 
## Preparación

Python >=3.11 y dependencias de requirements.txt. Desde raíz: `python -m unittest discover -v`. Si hay fallos gráficos, registrar cuáles y ejecutar por separado los módulos del núcleo indicados en baseline.md; no declarar aprobada la suite completa.

## Al implementar

Las pruebas del núcleo están en tests/test_linea_tiempo.py y
tests/test_persistencia_historia.py. Las pruebas del consumidor están en
tests/test_historia_motor.py, tests/test_modos_historia.py y
tests/test_comandos_integracion.py. Los escenarios de productor se prueban
con un doble hasta que el motor y el mapa entreguen sus interfaces reales.

Validar con una cripta obtenida del servicio o un fixture determinista: historia 0; varias acciones; historia #1; consulta futura rechazada; pergamino y consulta de rama; guardar/cargar e igualdad. No escribir IDs reales en la lógica.

Comandos implementados en el consumidor de D: `python main.py --checkpoint-cada 50`, `python main.py --replay partida.log --hasta 200`, `python main.py --verificar ID`, inicio no resoluble con/sin `--forzar`. Replay, verificación y benchmark no instancian vista. La verificación real
requiere el módulo entregado por B.

Usar aceptacion.md para casos H1–H6 y extras; bench con K 10/50/100 y sin controles, >=5000 acciones. Resultados medidos en DECISIONES.md.


## Primer incremento disponible: núcleo independiente

Desde la raíz:

```powershell
python -m tests.demo_linea_tiempo
python -m unittest tests.test_linea_tiempo -v
```

Demuestra movimiento, daño en evento intermedio, consulta antes de acción, recorte y nueva rama. No usa servidor, vista ni archivos de partida. API: EstadoHistorico, LineaTiempo.registrar_accion, consultar_t, consultar_accion y recortar. Registros en modelo/snapshots.py; implementación en modelo/linea_tiempo.py. Los valores son escalares finitos o tuplas inmutables y distinguen campo ausente de campo nulo. No pasar callbacks ni entidades vivas; un adaptador futuro capturará los datos del motor, agenda, azar y conocimiento.

Disponible: núcleo con datos sintéticos. Pendiente: motor real, resumen del juego, comandos historia, guardado binario y replay. Las claves de la demostración son fixtures, no datos de criptas concretas dentro del motor.


## Guardado del núcleo disponible

`python -m tests.demo_linea_tiempo` también muestra la codificación binaria, la igualdad después de cargar y la continuación desde lo cargado.

```powershell
python -m unittest tests.test_linea_tiempo tests.test_persistencia_historia -v
```

API en `datos/historia_binaria.py`: `codificar_historia(historia)` y `decodificar_historia(bytes)` trabajan en memoria; `guardar_historia(historia, ruta)` y `cargar_historia(ruta)` trabajan con archivo. `LineaTiempo.exportar()` produce HistoriaGuardada y `LineaTiempo.desde_guardado(registro)` construye una instancia validada e independiente.

El fragmento tiene versión propia CRLH 1; no abrirlo como partida CRPT. Al cargar regenera checkpoints cada K acciones, conserva correcciones de rama y valida estructura, CRC, valores y orden temporal. Guardar usa temporal único y reemplaza el destino al completar. El juego continúa usando su guardado previo; integrar formato 4, acceso a salas y comando de carga real sigue pendiente.

Estado de P1: el PDF proporcionado por ruta está vacío (0 bytes); no se ha podido contrastar su contrato original. Se mantuvo intacto el guardado actual.


## Revisar decisiones, prompts y errores

Las decisiones y sus alternativas están en DECISIONES.md; los prompts textuales y el uso de las respuestas en PROMPTS_LLM.md. La matriz de errores, recuperación y límites está en [errores.md](errores.md). Comprobación del núcleo: `python -m unittest tests.test_errores_historia tests.test_linea_tiempo tests.test_persistencia_historia -v`. Estas pruebas no requieren servicios ni interfaz; las de archivo necesitan permisos normales de escritura en temporales.
