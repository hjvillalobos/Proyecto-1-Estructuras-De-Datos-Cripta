
import json
import os
import struct
import zlib


from modelo.snapshots import (
    EstadoGuardado, MetaPartida, JugadorGuardado, ItemInventarioGuardado, EventoGuardado,
    SalaGuardada, PuertaGuardada, EnemigoGuardado, ObjetoGuardado, TrampaGuardada)
from utilidades.ordenamiento import ordenar

MAGIC = b"CRPT"
FORMATO_VERSION = 2          # contador de extras ampliado; los archivos viejos se rechazan

_ENCABEZADO = struct.Struct("<4sHHIQIQ")     # 4+2+2+4+8+4+8 = 32 bytes
_ENTRADA = struct.Struct("<IQI")             # sala_id, offset, longitud = 16 bytes
_U8, _U16, _U32 = struct.Struct("<B"), struct.Struct("<H"), struct.Struct("<I")
_I64, _F64 = struct.Struct("<q"), struct.Struct("<d")
_RNG = struct.Struct("<625I")                # estado interno del Mersenne Twister de Python


class ErrorGuardado(Exception):
    """Cualquier problema al leer/escribir un guardado (mensaje apto para mostrar al usuario)."""


class FormatoIncompatible(ErrorGuardado):
    """El archivo es de otra versión del formato del programa."""


class GuardadoCorrupto(ErrorGuardado):
    """Truncado, CRC incorrecto o estructura inválida."""


# Codificación: pequeñas clases que acumulan / consumen bytes con struct

class _Escritor:
    def __init__(self):
        self.b = bytearray()

    def u8(self, v):  self.b += _U8.pack(v)
    def u16(self, v): self.b += _U16.pack(v)
    def u32(self, v): self.b += _U32.pack(v)
    def i64(self, v): self.b += _I64.pack(v)
    def f64(self, v): self.b += _F64.pack(v)
    def booleano(self, v): self.u8(1 if v else 0)

    def texto(self, s):
        datos = s.encode("utf-8")
        self.u16(len(datos))            # struct.error si pasa de 65535 -> se traduce arriba
        self.b += datos


class _Lector:
    def __init__(self, datos):
        self.d = datos
        self.p = 0

    def _leer(self, st):
        try:
            v = st.unpack_from(self.d, self.p)
        except struct.error:
            raise GuardadoCorrupto("bloque truncado o dañado") from None
        self.p += st.size
        return v

    def u8(self):  return self._leer(_U8)[0]
    def u16(self): return self._leer(_U16)[0]
    def u32(self): return self._leer(_U32)[0]
    def i64(self): return self._leer(_I64)[0]
    def f64(self): return self._leer(_F64)[0]
    def booleano(self): return self.u8() != 0

    def texto(self):
        n = self.u16()
        crudo = self.d[self.p:self.p + n]
        if len(crudo) < n:
            raise GuardadoCorrupto("texto truncado")
        self.p += n
        return crudo.decode("utf-8")


def _con_crc(payload):
    return payload + _U32.pack(zlib.crc32(payload) & 0xFFFFFFFF)


def _verificar_crc(bloque, que):
    if len(bloque) < 4:
        raise GuardadoCorrupto(f"{que}: bloque demasiado corto")
    payload, crc = bloque[:-4], _U32.unpack(bloque[-4:])[0]
    if zlib.crc32(payload) & 0xFFFFFFFF != crc:
        raise GuardadoCorrupto(f"{que}: el CRC no coincide (archivo dañado)")
    return payload


# bloque GLOBAL 
def _codificar_global(e: EstadoGuardado):
    w = _Escritor()
    w.texto(e.meta.cripta_id)
    w.texto(e.meta.cripta_version)
    w.texto(e.meta.catalogo_version)
    w.i64(e.meta.semilla)
    w.i64(e.reloj)
    w.i64(e.siguiente_secuencia)
    w.u32(e.acciones_jugador)
    w.u32(e.enemigos_derrotados)

    version_rng, interno, gauss = e.rng_estado
    if len(interno) != 625:
        raise ErrorGuardado("rng_estado inválido: se esperaban 625 enteros")
    w.u8(version_rng)
    w.b += _RNG.pack(*interno)
    w.booleano(gauss is not None)
    w.f64(0.0 if gauss is None else gauss)

    j = e.jugador
    w.i64(j.sala_id)
    for v in (j.vida, j.vida_max, j.ataque, j.defensa, j.velocidad, j.tiempo_siguiente):
        w.i64(v)
    w.u16(len(j.inventario))
    for it in j.inventario:                      # el ORDEN real se conserva
        w.texto(it.instancia)
        w.texto(it.tipo)
        w.booleano(it.equipado)
    w.u32(len(j.extras))
    for v in j.extras:
        w.i64(v)

    w.u32(len(e.eventos))
    for ev in e.eventos:
        w.i64(ev.tiempo)
        w.i64(ev.secuencia)                      # el desempate determinista sobrevive al guardado
        w.texto(ev.tipo)
        w.texto(ev.objetivo)
        w.u8(len(ev.parametros))
        for v in ev.parametros:
            w.i64(v)
    return bytes(w.b)


def _decodificar_global(payload):
    r = _Lector(payload)
    meta = MetaPartida(r.texto(), r.texto(), r.texto(), r.i64())
    reloj, sig_seq = r.i64(), r.i64()
    acciones, derrotados = r.u32(), r.u32()

    version_rng = r.u8()
    interno = _RNG.unpack_from(payload, r.p)
    r.p += _RNG.size
    hay_gauss = r.booleano()
    gauss = r.f64()
    rng = (version_rng, tuple(interno), gauss if hay_gauss else None)

    sala_id = r.i64()
    vida, vida_max, ataque, defensa, velocidad, t_sig = (r.i64() for _ in range(6))
    inventario = [ItemInventarioGuardado(r.texto(), r.texto(), r.booleano())
                  for _ in range(r.u16())]
    extras = [r.i64() for _ in range(r.u32())]
    jugador = JugadorGuardado(sala_id, vida, vida_max, ataque, defensa, velocidad,
                              t_sig, inventario, extras)

    eventos = []
    for _ in range(r.u32()):
        t, seq = r.i64(), r.i64()
        tipo, objetivo = r.texto(), r.texto()
        eventos.append(EventoGuardado(t, seq, tipo, objetivo, [r.i64() for _ in range(r.u8())]))

    return EstadoGuardado(meta, reloj, sig_seq, acciones, derrotados, rng,
                          jugador, eventos, [])


#bloque SALA
def _codificar_sala(s: SalaGuardada):
    w = _Escritor()
    w.u32(s.sala_id)
    w.i64(s.rastro)
    w.u8(len(s.puertas))
    for p in s.puertas:
        w.texto(p.direccion)
        w.booleano(p.cerrada)
    w.u16(len(s.enemigos))
    for en in s.enemigos:
        w.texto(en.instancia)
        w.texto(en.tipo)
        w.i64(en.vida)
        w.booleano(en.activo)
        w.i64(en.tiempo_siguiente)
    w.u16(len(s.objetos_suelo))
    for o in s.objetos_suelo:
        w.texto(o.instancia)
        w.texto(o.tipo)
    w.u16(len(s.trampas))
    for t in s.trampas:
        w.texto(t.instancia)
        w.texto(t.tipo)
        w.booleano(t.armada)
    return bytes(w.b)


def _decodificar_sala(payload):
    r = _Lector(payload)
    sala_id, rastro = r.u32(), r.i64()
    puertas = [PuertaGuardada(r.texto(), r.booleano()) for _ in range(r.u8())]
    enemigos = [EnemigoGuardado(r.texto(), r.texto(), r.i64(), r.booleano(), r.i64())
                for _ in range(r.u16())]
    objetos = [ObjetoGuardado(r.texto(), r.texto()) for _ in range(r.u16())]
    trampas = [TrampaGuardada(r.texto(), r.texto(), r.booleano()) for _ in range(r.u16())]
    return SalaGuardada(sala_id, rastro, puertas, enemigos, objetos, trampas)

# Escritura
def guardar_estado(estado: EstadoGuardado, ruta: str):
    """Escribe el estado completo en `ruta` (atómico). Devuelve el tamaño en bytes."""
    # El índice DEBE estar ordenado por sala_id para poder hacer búsqueda binaria.
    salas = ordenar(estado.salas, clave=lambda s: s.sala_id)
    for i in range(1, len(salas)):
        if salas[i].sala_id == salas[i - 1].sala_id:
            raise ErrorGuardado(f"la sala {salas[i].sala_id} aparece repetida en el estado")

    tmp = ruta + ".tmp"
    try:
        with open(tmp, "wb") as f:
            f.write(b"\x00" * _ENCABEZADO.size)              # reservamos el encabezado
            bloque_global = _con_crc(_codificar_global(estado))
            off_global = f.tell()
            f.write(bloque_global)

            indice = []
            for s in salas:
                bloque = _con_crc(_codificar_sala(s))
                indice.append((s.sala_id, f.tell(), len(bloque)))
                f.write(bloque)

            off_indice = f.tell()
            for entrada in indice:
                f.write(_ENTRADA.pack(*entrada))

            f.seek(0)                                        # ahora sí, el encabezado real
            f.write(_ENCABEZADO.pack(MAGIC, FORMATO_VERSION, 0, len(salas),
                                     off_global, len(bloque_global), off_indice))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ruta)
    except struct.error as exc:
        _borrar_silencioso(tmp)
        raise ErrorGuardado(f"un valor no cabe en el formato binario: {exc}") from exc
    except OSError as exc:
        _borrar_silencioso(tmp)
        raise ErrorGuardado(f"no se pudo escribir '{ruta}': {exc}") from exc
    return os.path.getsize(ruta)


def _borrar_silencioso(ruta):
    try:
        os.remove(ruta)
    except OSError:
        pass

# Lectura con acceso aleatorio
class ArchivoGuardado:
    """Abre un guardado y permite leer el bloque global o UNA sala sin leer el resto.

        with ArchivoGuardado("partida.sav") as g:
            meta = g.leer_global().meta          # verificar versión de cripta antes de nada
            sala = g.leer_sala(7)                # solo lee ~1 bloque + log2(n) entradas
    """

    def __init__(self, ruta):
        try:
            self._f = open(ruta, "rb")
        except OSError as exc:
            raise ErrorGuardado(f"no se pudo abrir '{ruta}': {exc}") from exc
        try:
            self._leer_encabezado(ruta)
        except Exception:
            self._f.close()
            raise

    def _leer_encabezado(self, ruta):
        crudo = self._f.read(_ENCABEZADO.size)
        if len(crudo) < _ENCABEZADO.size:
            raise GuardadoCorrupto(f"'{ruta}' es demasiado corto para ser un guardado")
        magic, version, _, n, off_g, len_g, off_i = _ENCABEZADO.unpack(crudo)
        if magic != MAGIC:
            raise ErrorGuardado(f"'{ruta}' no es un archivo de guardado de CRIPTA")
        if version != FORMATO_VERSION:
            raise FormatoIncompatible(
                f"el guardado usa el formato v{version} y este programa entiende "
                f"solo el v{FORMATO_VERSION}; no se puede cargar")
        tam = os.fstat(self._f.fileno()).st_size
        if off_i + n * _ENTRADA.size != tam or off_g + len_g > off_i:
            raise GuardadoCorrupto(f"'{ruta}' está truncado o tiene un encabezado inválido")
        self.n_salas, self._off_global, self._len_global, self._off_indice = n, off_g, len_g, off_i

    # -- bloques ---------------------------------------------------------------------------
    def _leer_bloque(self, offset, longitud, que):
        self._f.seek(offset)
        bloque = self._f.read(longitud)
        if len(bloque) != longitud:
            raise GuardadoCorrupto(f"{que}: lectura incompleta")
        return _verificar_crc(bloque, que)

    def leer_global(self) -> EstadoGuardado:
        """Meta, reloj, RNG, jugador y agenda. `salas` viene vacío."""
        return _decodificar_global(
            self._leer_bloque(self._off_global, self._len_global, "bloque global"))

    def _buscar_entrada(self, sala_id):
        """Búsqueda binaria sobre el índice EN DISCO. O(log n) lecturas de 16 bytes."""
        lo, hi = 0, self.n_salas - 1
        while lo <= hi:
            medio = (lo + hi) // 2
            self._f.seek(self._off_indice + medio * _ENTRADA.size)
            sid, off, ln = _ENTRADA.unpack(self._f.read(_ENTRADA.size))
            if sid == sala_id:
                return off, ln
            if sid < sala_id:
                lo = medio + 1
            else:
                hi = medio - 1
        return None

    def leer_sala(self, sala_id) -> SalaGuardada | None:
        """Devuelve la sala pedida o None si no está en el guardado."""
        hallada = self._buscar_entrada(sala_id)
        if hallada is None:
            return None
        off, ln = hallada
        return _decodificar_sala(self._leer_bloque(off, ln, f"sala {sala_id}"))

    def ids_salas(self):
        """Ids de todas las salas guardadas (lee solo el índice, no los bloques)."""
        self._f.seek(self._off_indice)
        crudo = self._f.read(self.n_salas * _ENTRADA.size)
        return [_ENTRADA.unpack_from(crudo, i * _ENTRADA.size)[0] for i in range(self.n_salas)]

    def leer_todo(self) -> EstadoGuardado:
        """Carga completa. Se hace con DOS lecturas grandes (zona de salas + índice) en vez de
        una búsqueda binaria por sala: cuando se quiere todo, el acceso aleatorio sobra."""
        estado = self.leer_global()
        inicio = self._off_global + self._len_global
        self._f.seek(inicio)
        zona = self._f.read(self._off_indice - inicio)
        indice = self._f.read(self.n_salas * _ENTRADA.size)
        if len(zona) != self._off_indice - inicio or len(indice) != self.n_salas * _ENTRADA.size:
            raise GuardadoCorrupto("lectura incompleta de las salas")
        salas = []
        for i in range(self.n_salas):
            sid, off, ln = _ENTRADA.unpack_from(indice, i * _ENTRADA.size)
            rel = off - inicio
            bloque = zona[rel:rel + ln] if rel >= 0 else b""
            if len(bloque) != ln:
                raise GuardadoCorrupto(f"sala {sid}: bloque fuera de rango")
            salas.append(_decodificar_sala(_verificar_crc(bloque, f"sala {sid}")))
        estado.salas = salas
        return estado

    def cerrar(self):
        self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()


def cargar_estado(ruta) -> EstadoGuardado:
    with ArchivoGuardado(ruta) as g:
        return g.leer_todo()


# ===========================================================================================
# JSON: solo existe para COMPARAR tamaño y tiempo contra el binario en --bench (§4.10)
# ===========================================================================================
def guardar_json(estado: EstadoGuardado, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(estado.a_dict(), f)
    return os.path.getsize(ruta)


def cargar_json(ruta) -> EstadoGuardado:
    with open(ruta, "r", encoding="utf-8") as f:
        return EstadoGuardado.desde_dict(json.load(f))
