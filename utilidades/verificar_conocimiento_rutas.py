"""Prueba aislada con rutas.py real de A, sin fusionar ni modificar ramas."""
from pathlib import Path
import subprocess
import sys
import tempfile

REVISION_A = '9730482d4c6e33e5ba39e6eeb6f76d1f19b4220c'


def main():
    raiz = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(
        ['git', 'rev-parse', REVISION_A + '^{commit}'], cwd=raiz, text=True).strip()
    cache = raiz / '.cache'
    cache.mkdir(exist_ok=True)
    copia = Path(tempfile.mkdtemp(prefix='integracion-rutas-', dir=cache))
    archivos_c = ('modelo/__init__.py', 'modelo/conocimiento.py', 'modelo/conocimiento_rutas.py',
                  'utilidades/__init__.py', 'utilidades/ordenamiento.py',
                  'utilidades/bench_rutas_conocidas.py', 'utilidades/bench_conocimiento.py', 'tests/__init__.py',
                  'tests/test_conocimiento_rutas.py', 'tests/test_conocimiento.py')
    for archivo in archivos_c:
        destino = copia / archivo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes((raiz / archivo).read_bytes())
    (copia / 'modelo/rutas.py').write_bytes(subprocess.check_output(
        ['git', 'show', revision + ':modelo/rutas.py'], cwd=raiz))
    print(f'A: {revision}; C: archivos de trabajo. Copia: {copia}', flush=True)
    resultado = subprocess.run([sys.executable, '-B', '-m', 'unittest',
                                'tests.test_conocimiento', 'tests.test_conocimiento_rutas', '-v'], cwd=copia)
    if resultado.returncode or '--bench' not in sys.argv[1:]:
        return resultado.returncode
    return subprocess.run([sys.executable, '-B', '-m', 'utilidades.bench_rutas_conocidas'], cwd=copia).returncode


if __name__ == '__main__':
    raise SystemExit(main())
