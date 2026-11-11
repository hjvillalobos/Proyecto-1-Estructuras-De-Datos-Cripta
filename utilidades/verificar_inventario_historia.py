"""Ensayo aislado de inventario de C con historia real de D."""
from pathlib import Path
import subprocess
import sys

from utilidades.verificar_viaje_motor import exportar, REVISION_D


def main():
    raiz = Path(__file__).resolve().parents[1]
    copia = exportar(raiz, REVISION_D)
    for archivo in ('modelo/inventario.py', 'modelo/historial.py', 'modelo/inventario_historia.py',
                    'tests/test_inventario_historia.py', 'tests/test_inventario.py', 'tests/test_historial.py'):
        (copia / archivo).write_bytes((raiz / archivo).read_bytes())
    print(f'D={REVISION_D}; C=archivos de trabajo; copia={copia}', flush=True)
    return subprocess.run([sys.executable, '-B', '-m', 'unittest',
        'tests.test_inventario_historia', 'tests.test_inventario', 'tests.test_historial',
        'tests.test_linea_tiempo', '-v'], cwd=copia).returncode


if __name__ == '__main__':
    raise SystemExit(main())
