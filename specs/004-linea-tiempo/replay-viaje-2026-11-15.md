# Replay gráfico y destino de viaje — 2026-11-15

Especificaciones RP-01..04 y VD-01 confirmadas antes del código en fe87ebf y 8b01f2e.

## Causa y resultado

El lanzador de la GUI invocaba `--replay`, que reproduce sin vista y devuelve texto. Ahora menú y partida invocan `--replay-grafico` en un proceso independiente, con sesión, UUID y presupuesto propios. El log se lee una vez al iniciar; no sigue acciones añadidas después. La fábrica crea partida completa e historia para reproducir cargas y retrocesos. Se muestran estados, inventario, costos ponderados y animaciones. Pausa/continuar, velocidad y detener controlan la reproducción. Los errores se presentan en su ventana y producen salida 1. La barra ocupa el espacio de los controles de juego para evitar el recorte observado en la inspección nativa.

`--replay` y `--hasta` conservan la reproducción sin vista. Ejemplo gráfico, con rutas de un paquete y log compatibles:

```powershell
python main.py --offline .cache/entrega --replay-grafico datos_generados/partida.log
```

Viajar usaba el diálogo genérico de Windows. Ahora ofrece «Viajar a una sala», con tema oscuro, selección de salas exploradas, número editable, validación y botones Viajar/Cancelar. Recibe exclusivamente la proyección conocida; no consulta modelo ni red. Confirmar delega al viaje ordinario. Cancelar, Escape y X conservan estado, viaje activo, cola y archivos. Enter confirma; Enter sobre Cancelar cancela.

## Validación y límites

112 pruebas dirigidas en 41.511 s, OK: replay gráfico/directo, entradas de menú/controlador, historia/carga/retroceso, independencia de estado y archivos, CLI, destino/validación/cancelación, viaje, partidas completas/generadas, comandos, objetivo y presentaciones de mapa/menú. Registro local: replay-viaje-validacion-corregida.log. El test de comandos se ajustó al despacho `viajar`; Historia conserva su diálogo existente.

Inspección nativa con partida temporal aislada: diálogo oscuro, selección y cancelación; reproducción pausada, continuación, pasos gráficos y resumen final. Se detectó y corrigió el recorte de la barra. Las dos entradas del lanzador se verificaron automáticamente; no es una revisión exhaustiva de todas las resoluciones o combinaciones de ventanas.

No se repitieron la suite completa ni los benchmarks; las mediciones históricas no se atribuyen a este incremento. Se conservan reglas, dificultad, formatos de guardado y datos del servicio. El cambio previo de datos_generados/puntajes.jsonl queda fuera del commit. Hay que reiniciar una ventana abierta anteriormente para cargar el código nuevo.
