# CRIPTA

Proyecto de Estructuras de Datos II, Parte II. Python 3.11 o superior, arquitectura MVC y estructuras de datos propias. Terreno/cazadores, mapa conocido/viaje, resolubilidad e historia están integrados en `004-linea-tiempo`.

[Estado vigente y trazabilidad punto por punto](ESTADO_ENTREGA.md) · [Decisiones y mediciones](DECISIONES.md) · [Bitácora LLM](PROMPTS_LLM.md)

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

## Acciones y archivos

En consola: `mover N` (también S/E/O), `abrir E`, `atacar INSTANCIA`, `esperar`, `recoger INSTANCIA`, `usar INSTANCIA`, `equipar INSTANCIA`, `soltar INSTANCIA`, `inventario`, `mapa`, `ir a SALA`, `cancelar`, `retroceso`, `historia T`, `historia #K`, `guardar "archivo.bin"`, `cargar "archivo.bin"` y `salir`. La GUI ofrece los controles correspondientes y navegación del inventario. Cada enemigo/objeto se identifica por instancia.

El viaje usa solo conocimiento del jugador y se detiene por llegada, enemigos, daño o falta de ruta. Cada paso es un movimiento ordinario. Historia consulta sin alterar la partida. Guardado binario v4 conserva estado, azar, historia y conocimiento; versiones antiguas incompatibles se rechazan explícitamente.

Los datos descargados están en `--datos-dir` (por defecto `.cache/cripta`). Partidas, log de reproducción y puntajes normales están bajo `datos_generados/`; los nombres de guardado explícitos respetan la ruta indicada. Son archivos locales excluidos de Git. No borrar la copia de datos compatible necesaria para reproducir una partida.

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
python main.py --bench --subsistemas terreno-cazador --salas 40 --repeticiones 3
python main.py --bench --subsistemas resolubilidad --paquete .cache/entrega --cripta cripta-06 --repeticiones 10
python main.py --bench --subsistemas historia --operaciones 5000 --salas 100 --repeticiones 5
```

`parte-dos` incluye comparación pareada del heap anterior/optimizado con decisiones iguales, estrategias de rutas, puertas estables/cambiantes, ciclo con 30 cazadores y pasos sobre mapa conocido completo. La preparación queda fuera del intervalo medido. Las inyecciones sintéticas se identifican; no se presentan como población natural de la cripta. Los benchmarks no usan HTTP ni renderizado.

Opciones con preparación explícita:

```powershell
$env:CRIPTA_API_REAL='1'
python -B -X utf8 -m unittest tests.test_verificacion_entrega.TestApiRealEntrega -v
Remove-Item Env:CRIPTA_API_REAL
$env:CRIPTA_PAQUETE_API=(Resolve-Path '.cache/qa-paquete-p1').Path
python -B -X utf8 -m unittest tests.test_criptas_api.TestPaqueteOficial -v
```

El segundo comando requiere el paquete histórico completo de cuatro criptas; la API actual no garantiza conservar esos mapas. La suite ordinaria declara las omisiones cuando falta preparación. TEMP/TMP deben apuntar a una carpeta escribible. Las pruebas gráficas necesitan una sesión con Tk disponible.

Resultado final del fortalecimiento: **814 pruebas, cero fallos/errores**, dos omisiones opcionales verificadas aparte (comparación histórica y API real). El verificador de copia limpia prepara fuentes sin datos locales y reutiliza el intérprete/dependencias instalados. [Muestras completas y entorno](specs/004-linea-tiempo/fortalecimiento-mediciones.json).

## Proceso y documentación

Spec-kit **v1.2.3**, agente **Codex**, PowerShell. Configuración compartida en `.specify/` y habilidades en `.agents/skills/`. No repetir `specify init` sobre el repositorio.

```powershell
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.2.3
specify version
specify integration status
```

Para cambios de reglas: constitution → specify → clarify → plan → tasks → analyze → implement; confirmar especificación antes del código. Las interpretaciones deducibles se documentan como decisiones del equipo. Registrar prompts textuales y mediciones reales; no atribuir al profesor respuestas inexistentes. Las cuatro carpetas de `specs/` contienen requisitos, planes, tareas y antecedentes. [README histórico](README_HISTORICO.md) conserva notas de incrementos anteriores; el estado actual está en este archivo y ESTADO_ENTREGA.md.

Los resultados finales, salvedades históricas y límites de las mediciones figuran en DECISIONES.md. No se garantiza una nota ni ausencia absoluta de bugs. Defensa excluida de este trabajo.
