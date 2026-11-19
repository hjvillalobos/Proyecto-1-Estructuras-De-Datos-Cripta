"""RF-03: ejecutar aceptación headless sin cachés ni partidas del proyecto.

Reutiliza el intérprete y sus dependencias instaladas; no sustituye instalar
requirements.txt en un entorno nuevo. La copia temporal está fuera de Git.
"""
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    raiz = Path(__file__).resolve().parents[1]
    cache = raiz / '.cache'
    cache.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix='entrega-limpia-', dir=cache) as carpeta:
        destino = Path(carpeta)
        for modulo in ('modelo', 'controlador', 'datos', 'red', 'utilidades', 'vista', 'tests'):
            for fuente in (raiz / modulo).rglob('*.py'):
                copia = destino / fuente.relative_to(raiz)
                copia.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(fuente, copia)
        for nombre in ('main.py', 'bench.py', 'requirements.txt'):
            shutil.copy2(raiz / nombre, destino / nombre)
        resultado = subprocess.run(
            [sys.executable, '-B', '-X', 'utf8', '-m', 'unittest',
             'tests.test_partida_generada', 'tests.test_modos_historia',
             'tests.test_almacen_salas', '-v'], cwd=destino,
            capture_output=True, text=True, encoding='utf-8', timeout=120)
        texto = resultado.stdout + resultado.stderr
        evidencias = cache / 'revisiones'
        evidencias.mkdir(exist_ok=True)
        (evidencias / 'fortalecimiento-copia-limpia.log').write_text(texto, encoding='utf-8')
        print(texto)
        return resultado.returncode


if __name__ == '__main__':
    raise SystemExit(main())
