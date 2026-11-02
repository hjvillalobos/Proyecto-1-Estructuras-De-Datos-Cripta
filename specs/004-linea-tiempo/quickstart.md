# Guía de implementación y validación

Rama 004-linea-tiempo. 
## Preparación

Python >=3.11 y dependencias de requirements.txt. Desde raíz: `python -m unittest discover -v`. Si hay fallos gráficos, registrar cuáles y ejecutar por separado los módulos del núcleo indicados en baseline.md; no declarar aprobada la suite completa.

## Al implementar

Ejecutar tests/test_linea_tiempo.py, test_persistencia_historia.py, test_modos_historia.py y test_comandos_integracion.py mediante unittest. Estos archivos son entregables previstos en tasks.md y todavía no existen.

Validar con una cripta obtenida del servicio o un fixture determinista: historia 0; varias acciones; historia #1; consulta futura rechazada; pergamino y consulta de rama; guardar/cargar e igualdad. No escribir IDs reales en la lógica.

Comandos previstos tras implementar: `python main.py --checkpoint-cada 50`, `python main.py --replay partida.log --hasta 200`, `python main.py --verificar ID`, inicio no resoluble con/sin `--forzar`. No anunciar estos argumentos como disponibles antes de implementarlos. Replay/verificar/bench no instancian vista.

Usar aceptacion.md para casos H1–H6 y extras; bench con K 10/50/100 y sin controles, >=5000 acciones. Resultados medidos en DECISIONES.md.
