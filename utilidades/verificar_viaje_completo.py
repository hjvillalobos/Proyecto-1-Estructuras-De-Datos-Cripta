"""Ensayo I11 sobre entrega real de A; no fusiona ni cambia el motor local."""
from pathlib import Path
import os
import subprocess
import sys

from utilidades.verificar_viaje_motor import exportar

REVISION_A = '0b4f13a2f0104ed04ce944a0868ba6ad0584c62f'


def main():
    raiz = Path(__file__).resolve().parents[1]
    copia = exportar(raiz, REVISION_A)
    (copia / 'vista').mkdir(exist_ok=True)
    for nombre in ('vista/__init__.py', 'vista/bitacora_pantalla.py'):
        (copia / nombre).write_bytes(subprocess.check_output(
            ['git', 'show', REVISION_A + ':' + nombre], cwd=raiz))
    for nombre in ('modelo/conocimiento.py', 'modelo/conocimiento_rutas.py',
                   'modelo/viaje.py', 'modelo/detencion_viaje.py',
                   'tests/test_viaje_completo_motor.py'):
        (copia / nombre).write_bytes((raiz / nombre).read_bytes())
    entorno = os.environ.copy()
    entorno['CRIPTA_SIN_AUDIO'] = '1'
    print(f'A={REVISION_A}; C=archivos de trabajo; copia={copia}', flush=True)
    return subprocess.run([sys.executable, '-B', '-m', 'unittest',
        'tests.test_viaje_completo_motor', 'tests.test_hechos_paso_motor',
        'tests.test_conocimiento', 'tests.test_conocimiento_rutas', 'tests.test_viaje',
        '-v'], cwd=copia, env=entorno).returncode


if __name__ == '__main__':
    raise SystemExit(main())
