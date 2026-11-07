"""Fragmento binario de historia, independiente del guardado de partidas CRPT.

No utiliza pickle, índices de bibliotecas ni acceso a la red. La carga valida
base y deltas construyendo una historia nueva; el controlador decide integrarla.
"""
import os
from pathlib import Path
import struct
import tempfile
import zlib

from datos.guardado_binario import ErrorGuardado, FormatoIncompatible, GuardadoCorrupto
from modelo.linea_tiempo import LineaTiempo
from modelo.snapshots import (
    AccionHistorica, CambioHistorico, EventoHistorico, HistoriaGuardada, ValorHistorico,
)

FIRMA_HISTORIA = b'CRLH'
VERSION_HISTORIA = 1
_CABECERA = struct.Struct('<4sHQI')  # firma, versión, longitud de payload, CRC32
_U32 = struct.Struct('<I')
_U64 = struct.Struct('<Q')
_F64 = struct.Struct('<d')
_PROFUNDIDAD_MAXIMA = 64


class _Escritor:
    def __init__(self):
        self.datos = bytearray()

    def u8(self, valor):
        self.datos.append(valor)

    def u32(self, valor):
        self.datos.extend(_U32.pack(valor))

    def u64(self, valor):
        self.datos.extend(_U64.pack(valor))

    def texto(self, texto):
        datos = texto.encode('utf-8')
        self.u32(len(datos))
        self.datos.extend(datos)

    def valor(self, valor, profundidad=0):
        if profundidad > _PROFUNDIDAD_MAXIMA:
            raise ValueError('Demasiados niveles de tuplas históricas.')
        if valor is None:
            self.u8(0)
        elif type(valor) is bool:
            self.u8(2 if valor else 1)
        elif type(valor) is int:
            self.u8(3)
            self.u8(1 if valor < 0 else 0)
            magnitud = abs(valor)
            datos = magnitud.to_bytes(max(1, (magnitud.bit_length() + 7) // 8), 'little')
            self.u32(len(datos))
            self.datos.extend(datos)
        elif type(valor) is float:
            self.u8(4)
            self.datos.extend(_F64.pack(valor))
        elif type(valor) is str:
            self.u8(5)
            self.texto(valor)
        elif type(valor) is tuple:
            self.u8(6)
            self.u32(len(valor))
            for elemento in valor:
                self.valor(elemento, profundidad + 1)
        else:
            raise ValueError('Tipo histórico no admitido.')

    def extremo(self, extremo):
        self.u8(1 if extremo.presente else 0)
        if extremo.presente:
            self.valor(extremo.valor)

    def cambios(self, cambios):
        self.u32(len(cambios))
        for cambio in cambios:
            self.texto(cambio.clave)
            self.extremo(cambio.anterior)
            self.extremo(cambio.nuevo)


class _Lector:
    def __init__(self, datos):
        self.datos = memoryview(datos)
        self.posicion = 0

    def tomar(self, cantidad):
        if cantidad > len(self.datos) - self.posicion:
            raise GuardadoCorrupto('Historia truncada: longitud fuera del fragmento.')
        inicio = self.posicion
        self.posicion += cantidad
        return self.datos[inicio:self.posicion]

    def u8(self):
        return self.tomar(1)[0]

    def u32(self):
        return _U32.unpack(self.tomar(_U32.size))[0]

    def u64(self):
        return _U64.unpack(self.tomar(_U64.size))[0]

    def cantidad(self, minimo=1):
        cantidad = self.u32()
        if cantidad > (len(self.datos) - self.posicion) // minimo:
            raise GuardadoCorrupto('Cantidad fuera de los límites del fragmento.')
        return cantidad

    def texto(self):
        return bytes(self.tomar(self.u32())).decode('utf-8')

    def valor(self, profundidad=0):
        if profundidad > _PROFUNDIDAD_MAXIMA:
            raise GuardadoCorrupto('Demasiados niveles de tuplas históricas.')
        etiqueta = self.u8()
        if etiqueta == 0:
            return None
        if etiqueta in (1, 2):
            return etiqueta == 2
        if etiqueta == 3:
            signo = self.u8()
            datos = self.tomar(self.u32())
            if signo > 1 or not datos or (len(datos) > 1 and datos[-1] == 0):
                raise GuardadoCorrupto('Entero histórico inválido.')
            magnitud = int.from_bytes(datos, 'little')
            if signo and not magnitud:
                raise GuardadoCorrupto('Entero histórico negativo sin magnitud.')
            return -magnitud if signo else magnitud
        if etiqueta == 4:
            return _F64.unpack(self.tomar(_F64.size))[0]
        if etiqueta == 5:
            return self.texto()
        if etiqueta == 6:
            return tuple(self.valor(profundidad + 1) for _ in range(self.cantidad()))
        raise GuardadoCorrupto('Etiqueta de valor histórico desconocida.')

    def extremo(self):
        presente = self.u8()
        if presente not in (0, 1):
            raise GuardadoCorrupto('Indicador de presencia inválido.')
        return ValorHistorico(bool(presente), self.valor() if presente else None)

    def cambios(self):
        return tuple(CambioHistorico(self.texto(), self.extremo(), self.extremo())
                     for _ in range(self.cantidad(minimo=6)))


def codificar_historia(historia):
    """Genera el fragmento completo en memoria sin modificar la historia."""
    if type(historia) is not LineaTiempo:
        raise ErrorGuardado('Se requiere una línea de tiempo.')
    try:
        guardado = historia.exportar()
        escritor = _Escritor()
        escritor.u64(guardado.checkpoint_cada)
        escritor.u32(len(guardado.estado_inicial))
        for clave, valor in guardado.estado_inicial:
            escritor.texto(clave)
            escritor.valor(valor)
        escritor.u32(len(guardado.acciones))
        for accion in guardado.acciones:
            escritor.u64(accion.inicio)
            escritor.u64(accion.fin)
            escritor.cambios(accion.cambios)
            escritor.u32(len(accion.eventos))
            for evento in accion.eventos:
                escritor.u64(evento.tiempo)
                escritor.u64(evento.secuencia)
                escritor.cambios(evento.cambios)
            escritor.cambios(accion.correcciones)
        payload = bytes(escritor.datos)
        return _CABECERA.pack(
            FIRMA_HISTORIA, VERSION_HISTORIA, len(payload), zlib.crc32(payload)) + payload
    except (ValueError, OverflowError, struct.error, UnicodeError) as error:
        raise ErrorGuardado(f'No se pudo codificar la historia: {error}') from error


def validar_fragmento(datos):
    """Comprueba la envoltura y devuelve el payload sin reconstruir la historia."""
    if not isinstance(datos, (bytes, bytearray, memoryview)):
        raise ErrorGuardado('Se requieren datos binarios para cargar la historia.')
    try:
        datos = bytes(datos)
    except ValueError as error:
        raise ErrorGuardado('No se pueden leer los datos binarios de historia.') from error
    if datos[:4] == b'CRPT':
        raise FormatoIncompatible('Un guardado de partida CRPT no es un fragmento de historia CRLH.')
    if len(datos) < _CABECERA.size:
        raise GuardadoCorrupto('Cabecera de historia truncada.')
    firma, version, longitud, crc = _CABECERA.unpack_from(datos)
    if firma != FIRMA_HISTORIA:
        raise GuardadoCorrupto('Firma de historia desconocida.')
    if version != VERSION_HISTORIA:
        raise FormatoIncompatible(f'Versión de historia no compatible: {version}.')
    payload = memoryview(datos)[_CABECERA.size:]
    if longitud != len(payload):
        raise GuardadoCorrupto('Longitud de historia incorrecta o bytes sobrantes.')
    if zlib.crc32(payload) != crc:
        raise GuardadoCorrupto('CRC de historia incorrecto.')
    return payload


def decodificar_historia(datos):
    """Valida versión, longitudes, CRC y coherencia antes de devolver estado."""
    payload = validar_fragmento(datos)
    try:
        lector = _Lector(payload)
        k = lector.u64()
        inicial = tuple((lector.texto(), lector.valor()) for _ in range(lector.cantidad(minimo=5)))
        acciones = []
        for _ in range(lector.cantidad(minimo=28)):
            inicio, fin = lector.u64(), lector.u64()
            cambios = lector.cambios()
            eventos = tuple(EventoHistorico(lector.u64(), lector.u64(), lector.cambios())
                            for _ in range(lector.cantidad(minimo=20)))
            acciones.append(AccionHistorica(inicio, fin, cambios, eventos, lector.cambios()))
        if lector.posicion != len(payload):
            raise GuardadoCorrupto('Bytes sobrantes dentro del fragmento de historia.')
        return LineaTiempo.desde_guardado(HistoriaGuardada(k, inicial, tuple(acciones)))
    except (ValueError, OverflowError, struct.error, UnicodeError) as error:
        raise GuardadoCorrupto(f'Contenido de historia incoherente: {error}') from error


def _ruta_historia(ruta):
    try:
        resultado = Path(ruta)
    except (TypeError, ValueError) as error:
        raise ErrorGuardado('La ruta de historia debe ser una ruta de archivo válida.') from error
    if '\0' in str(resultado):
        raise ErrorGuardado('La ruta de historia contiene un carácter nulo.')
    return resultado


def guardar_historia(historia, ruta):
    """Reemplaza el archivo solo después de codificar y escribir íntegramente."""
    datos = codificar_historia(historia)
    ruta = _ruta_historia(ruta)
    temporal = None
    error_principal = None
    try:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporal = tempfile.mkstemp(prefix=f'.{ruta.name}.', suffix='.tmp', dir=ruta.parent)
        with os.fdopen(descriptor, 'wb') as archivo:
            archivo.write(datos)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
        temporal = None
    except OSError as error:
        error_principal = ErrorGuardado(f'No se pudo guardar la historia en {ruta}: {error}')
        raise error_principal from error
    finally:
        if temporal is not None:
            # Solo el temporal único creado por esta llamada, nunca el destino.
            try:
                os.unlink(temporal)
            except OSError as error:
                mensaje = f'No se pudo eliminar el archivo temporal {temporal}: {error}'
                if error_principal is not None:
                    error_principal.add_note(mensaje)
                else:
                    raise ErrorGuardado(mensaje) from error
    return len(datos)


def cargar_historia(ruta):
    ruta = _ruta_historia(ruta)
    try:
        datos = ruta.read_bytes()
    except OSError as error:
        raise ErrorGuardado(f'No se pudo leer la historia en {ruta}: {error}') from error
    return decodificar_historia(datos)
