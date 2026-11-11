"""Exporta fuentes versionadas a .cache y prueba sin fusionar ramas."""
import io
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

REVISION_A = '9730482d4c6e33e5ba39e6eeb6f76d1f19b4220c'
REVISION_D = '02da6b6f159b28279e3fe7dc5177c97c16898f42'
REVISION_B = '694dcf64cb601bdcc252c67bf6d325314efaa9a3'


def exportar(raiz, revision):
    cache = raiz / '.cache'
    cache.mkdir(exist_ok=True)
    destino = Path(tempfile.mkdtemp(prefix='viaje-motor-', dir=cache))
    contenido = subprocess.check_output(['git', 'archive', '--format=zip', revision,
        'modelo', 'red', 'datos', 'utilidades', 'controlador', 'tests', 'main.py'], cwd=raiz)
    with zipfile.ZipFile(io.BytesIO(contenido)) as archivo:
        for entrada in archivo.infolist():
            ruta = PurePosixPath(entrada.filename)
            if entrada.is_dir() or ruta.suffix != '.py':
                continue
            if ruta.is_absolute() or '..' in ruta.parts:
                raise ValueError('Ruta inválida en archivo Git.')
            salida = destino.joinpath(*ruta.parts)
            salida.parent.mkdir(parents=True, exist_ok=True)
            salida.write_bytes(archivo.read(entrada))
    return destino


def main():
    raiz = Path(__file__).resolve().parents[1]
    copia = exportar(raiz, REVISION_A)
    for archivo in ('modelo/snapshots.py', 'modelo/linea_tiempo.py', 'modelo/errores_historia.py',
                    'controlador/resumen_historia.py'):
        (copia / archivo).write_bytes(subprocess.check_output(
            ['git', 'show', REVISION_D + ':' + archivo], cwd=raiz))
    for archivo in ('modelo/conocimiento.py', 'modelo/conocimiento_historia.py',
                    'modelo/conocimiento_rutas.py', 'modelo/detencion_viaje.py', 'modelo/viaje.py',
                    'tests/test_viaje_motor.py'):
        (copia / archivo).write_bytes((raiz / archivo).read_bytes())
    entorno = os.environ.copy()
    entorno['CRIPTA_SIN_AUDIO'] = '1'
    print(f'A={REVISION_A}; D={REVISION_D}; C=archivos de trabajo; copia={copia}', flush=True)
    resultado = subprocess.run([sys.executable, '-B', '-m', 'unittest',
        'tests.test_viaje_motor', 'tests.test_cambios_historicos_motor', '-v'], cwd=copia, env=entorno)
    if resultado.returncode or '--verificar-b' not in sys.argv[1:]:
        return resultado.returncode
    copia_b = exportar(raiz, REVISION_B)
    print(f'B={REVISION_B}; copia independiente={copia_b}', flush=True)
    return subprocess.run([sys.executable, '-B', '-m', 'unittest',
        'tests.test_entrega_datos_terreno', 'tests.test_verificacion_datos', '-v'],
        cwd=copia_b, env=entorno).returncode


if __name__ == '__main__':
    raise SystemExit(main())
