"""Ensayo de desarrollo aislado con D versionado; no pertenece al juego.

No fusiona ramas, no modifica snapshots.py, no descarga ni ejecuta red.
Requiere que el commit de D esté disponible en el repositorio local.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

REVISION_D = '02da6b6f159b28279e3fe7dc5177c97c16898f42'


def main():
    raiz = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(
        ['git', 'rev-parse', REVISION_D + '^{commit}'], cwd=raiz, text=True).strip()
    cache = raiz / '.cache'
    cache.mkdir(exist_ok=True)
    copia = Path(tempfile.mkdtemp(prefix='integracion-conocimiento-', dir=cache))
    archivos_d = ('modelo/__init__.py', 'modelo/errores_historia.py',
                  'modelo/snapshots.py', 'modelo/linea_tiempo.py',
                  'tests/__init__.py', 'tests/test_linea_tiempo.py')
    archivos_c = ('modelo/conocimiento.py', 'modelo/conocimiento_historia.py',
                  'utilidades/__init__.py', 'utilidades/ordenamiento.py',
                  'tests/test_conocimiento.py', 'tests/test_conocimiento_historia.py')
    for archivo in archivos_d:
        destino = copia / archivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(subprocess.check_output(['git', 'show', revision + ':' + archivo], cwd=raiz))
    for archivo in archivos_c:
        destino = copia / archivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes((raiz / archivo).read_bytes())
    print(f'D: {revision}; C: archivos de trabajo. Copia: {copia}', flush=True)
    return subprocess.run([sys.executable, '-B', '-m', 'unittest',
                           'tests.test_linea_tiempo', 'tests.test_conocimiento_historia', '-v'],
                          cwd=copia).returncode


if __name__ == '__main__':
    raise SystemExit(main())
