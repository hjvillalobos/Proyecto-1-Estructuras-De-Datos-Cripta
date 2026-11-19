# CRIPTA

Proyecto de Estructuras de Datos II, Parte II. Python 3.11 o superior, arquitectura MVC y estructuras de datos propias. Terreno/cazadores, mapa conocido/viaje, resolubilidad e historia están integrados en la entrega de `main`, desarrollada en `004-linea-tiempo`.

[Estado vigente y trazabilidad punto por punto](ESTADO_ENTREGA.md) · [Decisiones y mediciones](DECISIONES.md) · [Bitácora LLM](PROMPTS_LLM.md)

Revisión del 18 de noviembre: replay con Tigre/Tigresa renderizados, datos offline de las cinco criptas disponibles y cuatro límites de procesamiento comprobados. [Resultados, mediciones y condiciones](specs/004-linea-tiempo/replay-offline-rendimiento-2026-11-18.md).

## Instalación desde una copia limpia

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py --listar
python main.py --gui
```

La GUI requiere Tkinter; suele venir con Python para Windows. `requests` permite acceder al servicio y Pillow mejora la presentación de imágenes. Si PowerShell restringe la activación, ejecutar directamente `.\.venv\Scripts\python.exe` en lugar de `python`.

## Jugar y preparar modo offline

```powershell
python main.py --listar
python main.py --cripta ID --semilla 42
python main.py --descargar-todo --cripta ID --datos-dir .cache/entrega
python main.py --offline .cache/entrega --cripta ID --semilla 42
python main.py --offline .cache/entrega --cripta ID --gui
```

Sustituir `ID` por un identificador del listado. La descarga completa prepara mapa, contenido, catálogo y llaves compatibles; no está incluida en Git. Los ejemplos de medición usan una copia local de cripta-06 de 300 salas. El cliente mantiene un UUID por ejecución, cuenta intentos/reintentos y respeta el presupuesto declarado. Las esperas reales no avanzan el reloj virtual.

Antes de jugar se muestra la verificación. Una cripta no resoluble se bloquea salvo `--forzar`; datos insuficientes no se convierten en un dictamen negativo y bloquean el inicio incluso con esa bandera.

```powershell
python main.py --offline .cache/entrega --verificar ID
python main.py --offline .cache/entrega --cripta ID --forzar
python main.py --offline .cache/entrega --cripta ID --checkpoint-cada 50
```

## Presentación del mapa y enemigos

El botón **Mapa** abre una cartografía con niebla, salas conocidas, puertas recordadas y costos. Selecciona una sala para ver el detalle; usa `+`/`−`, barras de desplazamiento, **Centrar en ti** o **Ver listado / Ver mapa**. **Viajar a esta sala** está disponible para otra sala explorada y usa el viaje habitual. El mapa no revela contenido oculto ni avanza el tiempo al consultarlo; su disposición representa conexiones, no coordenadas geográficas.

Sabueso óseo, espectro acechador y carcelero errante tienen ilustraciones que acompañan los recursos existentes. Los PNG son locales y se cargan mediante la cache visual. Ese incremento visual conservó las reglas, tiempos virtuales, guardados y algoritmos del motor. [Auditoría de API y validación visual](specs/004-linea-tiempo/visual-api-2026-11-14.md).

Los cazadores usan movimiento suave en reposo y reacción al daño; no tienen secuencias propias de caminar/atacar. Los objetos de catálogo nuevos sin imagen local conservan el signo **?** en suelo, inventario y equipo; sus estadísticas y acciones siguen viniendo del servicio.

El sonido de la GUI depende de la acción, no del ID de cripta/objeto. Activa **Sonido** para oír pasos, objetos, combate y resultados; la consola no reproduce audio. Si ejecutaste pruebas silenciosas en la misma terminal, restaura el arranque normal con `Remove-Item Env:CRIPTA_SIN_AUDIO -ErrorAction SilentlyContinue` antes de lanzar la GUI. Las esperas no tienen un efecto sonoro propio. La reproducción también depende de Windows y del dispositivo de salida.

Al consultar el servicio el 15 de noviembre se publicaban cripta-02–06. Las dos nuevas son **Cripta sellada** (un sabueso cazador, no resoluble salvo entrada con `--forzar`) y **Cripta de referencia** (25 sabuesos y 11 espectros cazadores). La niebla funciona en cualquier cripta. **Osario menor** corresponde a un paquete histórico y ya no aparece en ese listado. El selector usa la respuesta del servicio o el listado del paquete offline elegido.

[Revisión completa del enunciado, mapas, corrección de puertas y límites de evidencia](specs/004-linea-tiempo/revision-entrega-2026-11-15.md).

## Acciones y archivos

En la portada puedes elegir **Tigre** o **Tigresa**. La elección es visual y se recuerda localmente; ambos usan las mismas reglas y estadísticas. El replay usa la apariencia seleccionada al abrir su ventana: la apariencia no está guardada en el log de acciones. Se comprobó la misma grabación con ambos personajes, incluyendo retroceso y carga, con estado final idéntico y archivos originales intactos.

En la GUI, **Replay** abre una ventana independiente con reproducción gráfica, pausa/continuar, velocidad y detener. Alternativa: `python main.py --offline .cache/entrega --replay-grafico datos_generados/partida.log` con datos compatibles. Lee el log al abrirlo; para incluir acciones posteriores hay que abrirlo de nuevo. `--replay` y `--hasta` conservan su modo sin vista. **Viajar** permite seleccionar una sala explorada o escribir su número en un diálogo temático; Cancelar, Escape o X conservan la partida. [Validación y límites](specs/004-linea-tiempo/replay-viaje-2026-11-15.md).

Durante una partida gráfica, **Salir** permite continuar, reiniciar esa cripta, volver al menú o cerrar el juego. Escape o cerrar el diálogo conserva la partida; reiniciar requiere elección explícita y no sobrescribe guardados. El encabezado muestra el ID de cripta y una orientación del objetivo respetando el mapa conocido. La salida no tiene por qué ser la sala con mayor número: debes abrir su acceso con la llave correspondiente y atravesarlo. [Diagnóstico del recorrido por sala20, enemigos/daño y validación](specs/004-linea-tiempo/seguimiento-ux-2026-11-15.md).

En consola: `mover N` (también S/E/O), `abrir E`, `atacar INSTANCIA`, `esperar`, `recoger INSTANCIA`, `usar INSTANCIA`, `equipar INSTANCIA`, `soltar INSTANCIA`, `inventario`, `mapa`, `ir a SALA`, `cancelar`, `retroceso`, `historia T`, `historia #K`, `guardar "archivo.bin"`, `cargar "archivo.bin"` y `salir`. La GUI ofrece los controles correspondientes y navegación del inventario. Cada enemigo/objeto se identifica por instancia.

El viaje usa solo conocimiento del jugador y se detiene por llegada, enemigos, daño o falta de ruta. Cada paso es un movimiento ordinario. Historia consulta sin alterar la partida. Guardado binario v4 conserva estado, azar, historia y conocimiento; versiones antiguas incompatibles se rechazan explícitamente.

Historia muestra reloj/acciones, resultado, estadísticas, inventario en orden histórico, efectos, enemigos y mapa con nombres/salidas/costos/puertas recordadas. Los guardados anteriores que no registraban derrotados/resultado histórico muestran «no registrado» para esos datos, sin sustituirlos por valores actuales.

Para jugar o reproducir **offline**, descarga primero los datos completos y conserva las versiones de cripta y catálogo indicadas por el log o guardado. El modo offline no hace HTTP; informa los datos ausentes o incompatibles. Con los datos publicados comprobados, 02/03/04/06 cargan y 05 se bloquea correctamente por ser no resoluble. La existencia de 05 en el listado no significa que sea ganable.

Los datos descargados están en `--datos-dir` (por defecto `.cache/cripta`, excluida de Git). Partidas, log de reproducción y puntajes normales están bajo `datos_generados/`; los nombres de guardado explícitos respetan la ruta indicada. `datos_generados/` se excluye de nuevas entregas Git: los guardados y puntajes son archivos personales creados al jugar. Conserva tus archivos antes de reemplazarlos. No borrar la copia de datos compatible necesaria para reproducir una partida.

Los logs, mediciones y scripts auxiliares de revisiones locales se agrupan en `.cache/revisiones/`, fuera de Git. `INDICE.md` y `traslado-20261116.json` dentro de esa carpeta conservan la correspondencia de las rutas anteriores. Los paquetes de criptas conservan sus ubicaciones habituales.

```powershell
python main.py --offline .cache/entrega --replay datos_generados/partida.log
python main.py --offline .cache/entrega --replay datos_generados/partida.log --hasta 250
```

`--replay`, `--verificar` y `--bench` funcionan sin construir la vista interactiva. `--hasta` exige replay. Una versión de datos incompatible se informa; no se reproduce silenciosamente contra otra.

## Pruebas y mediciones reproducibles

```powershell
$env:CRIPTA_SIN_AUDIO='1'
python -B -X utf8 -m unittest discover -s tests -t . -v
python -B -X utf8 -m utilidades.verificar_conocimiento_rutas
python -B -X utf8 -m utilidades.verificar_copia_limpia
python main.py --bench --subsistemas parte-dos --paquete .cache/entrega --cripta cripta-06 --repeticiones 60
python main.py --bench --subsistemas ciclo-historia --paquete .cache/entrega --cripta cripta-06 --repeticiones 5
python main.py --bench --subsistemas terreno-cazador --salas 40 --repeticiones 3
python main.py --bench --subsistemas resolubilidad --paquete .cache/entrega --cripta cripta-06 --repeticiones 10
python main.py --bench --subsistemas historia --operaciones 5000 --salas 100 --repeticiones 5
python main.py --bench --subsistemas bitacora --operaciones 100000 --repeticiones 5 --semilla 20261001
Remove-Item Env:CRIPTA_SIN_AUDIO -ErrorAction SilentlyContinue
```

`bitacora` compara el buffer circular real con una lista que desplaza los mensajes anteriores; valida el mismo sufijo de 20 y mide agregar y agregar/consultar, sin red ni vista. Informa memoria superficial de estructura/arreglo, excluyendo textos compartidos. La lista es una alternativa de medición, no el almacenamiento del juego. [Decisión, resultados y límites](DECISIONES.md).

`parte-dos` incluye comparación pareada del heap anterior/optimizado con decisiones iguales, estrategias de rutas, puertas estables/cambiantes, ciclo con 30 cazadores y pasos sobre mapa conocido completo. La preparación queda fuera del intervalo medido. Las inyecciones sintéticas se identifican; no se presentan como población natural de la cripta. Los benchmarks no usan HTTP ni renderizado.

`ciclo-historia` compara el productor histórico anterior y el optimizado, alternando el orden de ejecución: cinco series de 120 ciclos completos por versión, incluyendo combate y checkpoints. Comprueba igualdad del estado final, historia y azar. RC-01 redujo la mediana de ciclo de 11.436 a 4.435 ms; máximo optimizado 11.931 ms, 0/600 sobre 20 ms. [Muestras y límites](specs/004-linea-tiempo/ciclo-historia-mediciones.json).

Opciones con preparación explícita:

```powershell
$env:CRIPTA_API_REAL='1'
python -B -X utf8 -m unittest tests.test_verificacion_entrega.TestApiRealEntrega -v
Remove-Item Env:CRIPTA_API_REAL
$env:CRIPTA_PAQUETE_API=(Resolve-Path '.cache/qa-paquete-p1').Path
python -B -X utf8 -m unittest tests.test_criptas_api.TestPaqueteOficial -v
```

El segundo comando requiere el paquete histórico completo de cuatro criptas; la API actual no garantiza conservar esos mapas. La suite ordinaria declara las omisiones cuando falta preparación. TEMP/TMP deben apuntar a una carpeta escribible. Las pruebas gráficas necesitan una sesión con Tk disponible.

Antecedente de presentación VI-01..05, 14 de noviembre: **828 pruebas en 214.910 s, cero fallos/errores**, dos opciones omitidas (comparación histórica, aprobada previamente, y API real, repetida aparte: cinco criptas fría/caliente, 87.563 s, OK). Las 152 composiciones regeneradas conservan exactamente los píxeles anteriores y su carga preparada. [Informe de ese corte](specs/004-linea-tiempo/visual-api-2026-11-14.md). La última suite integral y verificaciones posteriores están en ESTADO_ENTREGA.md; los conteos de subconjuntos no se suman. Los resultados del fortalecimiento anterior se conservan en [sus muestras completas](specs/004-linea-tiempo/fortalecimiento-mediciones.json).

## Proceso y documentación

Spec-kit **v1.2.3**, agente **Codex**, PowerShell. Configuración compartida en `.specify/` y habilidades en `.agents/skills/`. No repetir `specify init` sobre el repositorio.

```powershell
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.2.3
specify version
specify integration status
```

Para cambios de reglas: constitution → specify → clarify → plan → tasks → analyze → implement; confirmar especificación antes del código. Las interpretaciones deducibles se documentan como decisiones del equipo. Registrar prompts textuales y mediciones reales; no atribuir al profesor respuestas inexistentes. Las cuatro carpetas de `specs/` contienen requisitos, planes, tareas y antecedentes. [README histórico](README_HISTORICO.md) conserva notas de incrementos anteriores; el estado actual está en este archivo y ESTADO_ENTREGA.md.

Los resultados finales, salvedades históricas y límites de las mediciones figuran en DECISIONES.md. No se garantiza una nota ni ausencia absoluta de bugs. Defensa excluida de este trabajo.
