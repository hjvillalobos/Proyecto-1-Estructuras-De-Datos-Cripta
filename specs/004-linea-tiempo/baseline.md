# Base de pruebas — 2026-11-02

Base Git: origin/main 03716b2; rama documental 004-linea-tiempo. Python del runtime Codex, sin cambios de código del juego.

1. `python -m unittest discover -v`: ejecución completa interrumpida después de atascarse en pruebas gráficas. Antes de interrumpir, test_redibujar_menu_crea_animacion_nueva_y_destruirlo_la_cancela registró FAIL y aparecieron mensajes Tcl de aplicación destruida. No hay resultado final válido de la suite completa; causa exacta del fallo gráfico no diagnosticada. No se afirma que sea un defecto del programa.
2. Núcleo seleccionado, primer intento aislado: 134 casos, 42 errores; acceso denegado a temporales y dependencia ausente. Ese resultado no mide corrección del motor.
3. Repetición fuera del aislamiento: 134 casos, 133 aprobados y 1 error de importación, `requests` no instalado para tests.test_cliente_api. Sin fallos de aserción entre los casos restantes. No equivale a suite completa aprobada.

Comando de la repetición:

```powershell
python -m unittest tests.test_juego tests.test_historial tests.test_inventario tests.test_enemigos tests.test_rastro tests.test_cache tests.test_catalogo tests.test_cliente_api tests.test_regresiones_juego tests.test_fallos_transaccionales -v
```

Para completar la base: preparar un entorno del proyecto con requirements.txt, repetir cliente API con requests disponible y diagnosticar la prueba gráfica en sesión interactiva. No se instaló ninguna dependencia global ni se alteraron pruebas existentes. Se puede comenzar el núcleo sintético; antes de integrar deben resolverse y registrarse estos resultados.

Evidencia textual local de esta sesión: `C:/Users/Belén/Documents/New project/tmp/pruebas-base-linea-tiempo.txt`, `pruebas-nucleo-linea-tiempo.txt` y `pruebas-nucleo-linea-tiempo-verificadas.txt` en la misma carpeta. Los logs no se incorporan como datos de juego al repositorio.
