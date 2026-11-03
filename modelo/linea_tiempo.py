"""Historia pura por deltas; integración con el motor pendiente.

Arreglos e índices binarios propios. Solo se retienen estados completos para
el presente y los checkpoints. Consultar crea un estado de trabajo independiente.
"""
from dataclasses import dataclass, replace

from modelo.errores_historia import (
    EntradaHistoriaInvalida, ReferenciaHistoricaInvalida, CambioHistoriaIncoherente,
)

from modelo.snapshots import (
    AccionHistorica, CambioHistorico, EventoHistorico, HistoriaGuardada, ValorHistorico,
)


def _entero(valor, minimo, nombre):
    if type(valor) is not int or valor < minimo:
        raise EntradaHistoriaInvalida(f"{nombre} debe ser un entero mayor o igual a {minimo}.")


def _cambios_validos(cambios):
    if type(cambios) is not tuple or any(type(c) is not CambioHistorico for c in cambios):
        raise EntradaHistoriaInvalida("Se requiere una tupla de cambios históricos.")


class EstadoHistorico:
    """Campos de identidad estable sobre un arreglo ordenado, sin tablas hash.

    Lectura O(log S); creación/eliminación O(S) por desplazamientos. Los valores
    son inmutables; copiar el arreglo no comparte ningún objeto mutable.
    """
    def __init__(self, campos=()):
        self._campos = []
        for clave, valor in campos:
            cambio = CambioHistorico(clave, ValorHistorico(False), ValorHistorico(True, valor))
            self.aplicar(cambio)

    def _posicion(self, clave):
        if type(clave) is not str or not clave:
            raise EntradaHistoriaInvalida("La clave histórica debe ser texto no vacío.")
        bajo, alto = 0, len(self._campos)
        while bajo < alto:
            medio = (bajo + alto) // 2
            if self._campos[medio][0] < clave:
                bajo = medio + 1
            else:
                alto = medio
        return bajo

    def _leer(self, clave):
        pos = self._posicion(clave)
        if pos < len(self._campos) and self._campos[pos][0] == clave:
            return self._campos[pos][1]
        return ValorHistorico(False)

    def obtener(self, clave):
        valor = self._leer(clave)
        if not valor.presente:
            raise KeyError(clave)
        return valor.valor

    def campos(self):
        return tuple((clave, dato.valor) for clave, dato in self._campos)

    def copiar(self):
        copia = EstadoHistorico()
        copia._campos = self._campos.copy()
        return copia

    def _asignar(self, clave, valor):
        pos = self._posicion(clave)
        existe = pos < len(self._campos) and self._campos[pos][0] == clave
        if existe:
            if valor.presente:
                self._campos[pos] = (clave, valor)
            else:
                self._campos.pop(pos)
        elif valor.presente:
            self._campos.insert(pos, (clave, valor))

    def aplicar(self, cambio):
        if type(cambio) is not CambioHistorico:
            raise EntradaHistoriaInvalida("Se requiere un cambio histórico.")
        if self._leer(cambio.clave) != cambio.anterior:
            raise CambioHistoriaIncoherente(f"El valor anterior no coincide para {cambio.clave}.")
        self._asignar(cambio.clave, cambio.nuevo)


@dataclass(frozen=True)
class ConsultaHistoria:
    reloj: int
    estado: EstadoHistorico
    acciones_reconstruidas: int


class LineaTiempo:
    def __init__(self, estado_inicial, checkpoint_cada=50):
        _entero(checkpoint_cada, 1, "K")
        if type(estado_inicial) is not EstadoHistorico:
            raise EntradaHistoriaInvalida("Se requiere un estado histórico independiente.")
        self._k = checkpoint_cada
        self._actual = estado_inicial.copiar()
        self._controles = [estado_inicial.copiar()]
        self._bloques = []
        self._cantidad = 0
        self._reloj = 0

    @property
    def reloj(self):
        return self._reloj

    @property
    def cantidad_acciones(self):
        return self._cantidad

    @property
    def cantidad_puntos_control(self):
        return len(self._controles)

    @property
    def checkpoint_cada(self):
        return self._k

    def _accion(self, indice):
        return self._bloques[indice // self._k][indice % self._k]

    @staticmethod
    def _aplicar(estado, cambios):
        for cambio in cambios:
            estado.aplicar(cambio)

    @staticmethod
    def _iterar_cambios(accion):
        yield from accion.cambios
        for evento in accion.eventos:
            yield from evento.cambios
        yield from accion.correcciones

    @staticmethod
    def _validar_transaccion(estado, cambios):
        # Solo los campos tocados, incluida su ausencia. No copia el mundo.
        tocados = EstadoHistorico()
        for cambio in cambios:
            pos = tocados._posicion(cambio.clave)
            encontrado = (pos < len(tocados._campos)
                          and tocados._campos[pos][0] == cambio.clave)
            actual = tocados._campos[pos][1] if encontrado else estado._leer(cambio.clave)
            if actual != cambio.anterior:
                raise CambioHistoriaIncoherente(f"El valor anterior no coincide para {cambio.clave}.")
            entrada = (cambio.clave, cambio.nuevo)
            if encontrado:
                tocados._campos[pos] = entrada
            else:
                # Aquí una ausencia también es una entrada de transacción.
                tocados._campos.insert(pos, entrada)

    def registrar_accion(self, tiempo_final, cambios=(), eventos=(), *, correcciones=()):
        """Anexa una acción completa, validada antes de tocar la historia.

        Los efectos inmediatos se excluyen al consultar su instante de decisión.
        El productor debe entregar cerrado cada lote de eventos empatados.
        """
        _entero(tiempo_final, self._reloj + 1, "Tiempo final")
        _cambios_validos(cambios)
        _cambios_validos(correcciones)
        if type(eventos) is not tuple:
            raise EntradaHistoriaInvalida("Se requiere una tupla de eventos.")
        anterior = (self._reloj, -1)
        for evento in eventos:
            if type(evento) is not EventoHistorico:
                raise EntradaHistoriaInvalida("Se requiere un evento histórico.")
            orden = (evento.tiempo, evento.secuencia)
            if evento.tiempo <= self._reloj or evento.tiempo > tiempo_final or orden <= anterior:
                raise CambioHistoriaIncoherente("Los eventos deben estar ordenados dentro del intervalo de acción.")
            anterior = orden
        accion = AccionHistorica(self._reloj, tiempo_final, cambios, eventos, correcciones)
        self._validar_transaccion(self._actual, self._iterar_cambios(accion))
        self._aplicar(self._actual, self._iterar_cambios(accion))
        if self._cantidad % self._k == 0:
            self._bloques.append([])
        self._bloques[-1].append(accion)
        self._cantidad += 1
        self._reloj = tiempo_final
        if self._cantidad % self._k == 0:
            self._controles.append(self._actual.copiar())

    def _reconstruir_completas(self, cantidad):
        bloque = cantidad // self._k
        estado = self._controles[bloque].copiar()
        inicio = bloque * self._k
        for indice in range(inicio, cantidad):
            self._aplicar(estado, self._iterar_cambios(self._accion(indice)))
        return estado, cantidad - inicio

    def consultar_t(self, tiempo):
        _entero(tiempo, 0, "Tiempo")
        if tiempo > self._reloj:
            raise ReferenciaHistoricaInvalida("No se puede consultar un instante futuro.")
        # Primer intervalo que termina después de t: búsqueda binaria propia.
        bajo, alto = 0, self._cantidad
        while bajo < alto:
            medio = (bajo + alto) // 2
            if self._accion(medio).fin <= tiempo:
                bajo = medio + 1
            else:
                alto = medio
        estado, reconstruidas = self._reconstruir_completas(bajo)
        if bajo < self._cantidad:
            accion = self._accion(bajo)
            if tiempo > accion.inicio:
                self._aplicar(estado, accion.cambios)
                for evento in accion.eventos:
                    if evento.tiempo > tiempo:
                        break
                    self._aplicar(estado, evento.cambios)
                reconstruidas += 1
        return ConsultaHistoria(tiempo, estado, reconstruidas)

    def consultar_accion(self, numero):
        _entero(numero, 1, "Acción")
        if numero > self._cantidad:
            raise ReferenciaHistoricaInvalida("Esa acción no existe en la rama vigente.")
        estado, reconstruidas = self._reconstruir_completas(numero - 1)
        return ConsultaHistoria(self._accion(numero - 1).inicio, estado, reconstruidas)

    def recortar(self, acciones_conservadas, correcciones=()):
        """Descarta solo el sufijo; las correcciones sobreviven al retroceso.

        No limita la cantidad de retrocesos: ese permiso es responsabilidad
        del motor. Localizar la frontera es O(1), liberar el sufijo O(sufijo).
        """
        _entero(acciones_conservadas, 0, "Cantidad conservada")
        if acciones_conservadas > self._cantidad:
            raise ReferenciaHistoricaInvalida("No se puede conservar una acción inexistente.")
        _cambios_validos(correcciones)
        estado, _ = self._reconstruir_completas(acciones_conservadas)
        self._validar_transaccion(estado, iter(correcciones))
        self._aplicar(estado, correcciones)
        reloj = self._accion(acciones_conservadas - 1).fin if acciones_conservadas else 0
        bloques_enteros, resto = divmod(acciones_conservadas, self._k)
        if resto:
            del self._bloques[bloques_enteros][resto:]
        del self._bloques[bloques_enteros + bool(resto):]
        del self._controles[bloques_enteros + 1:]
        if correcciones and acciones_conservadas:
            indice = acciones_conservadas - 1
            accion = self._accion(indice)
            self._bloques[indice // self._k][indice % self._k] = replace(
                accion, correcciones=accion.correcciones + correcciones)
        if resto == 0:
            self._controles[bloques_enteros] = estado.copiar()
        self._actual = estado
        self._cantidad = acciones_conservadas
        self._reloj = reloj

    def exportar(self):
        """Contrato puro sin callbacks; no modifica ni expone estados mutables."""
        return HistoriaGuardada(
            self._k, self._controles[0].campos(),
            tuple(self._accion(i) for i in range(self._cantidad)))

    @classmethod
    def desde_guardado(cls, guardado):
        """Valida y reconstruye en una instancia nueva antes de devolverla."""
        if type(guardado) is not HistoriaGuardada:
            raise EntradaHistoriaInvalida("Se requiere un registro de historia guardada.")
        if type(guardado.estado_inicial) is not tuple or type(guardado.acciones) is not tuple:
            raise EntradaHistoriaInvalida("La base y las acciones deben ser tuplas.")
        for campo in guardado.estado_inicial:
            if type(campo) is not tuple or len(campo) != 2:
                raise EntradaHistoriaInvalida("Cada campo histórico debe ser una pareja clave/valor.")
        historia = cls(EstadoHistorico(guardado.estado_inicial), guardado.checkpoint_cada)
        for accion in guardado.acciones:
            if type(accion) is not AccionHistorica:
                raise EntradaHistoriaInvalida("Se requiere una acción histórica.")
            _entero(accion.inicio, 0, "Tiempo inicial")
            if accion.inicio != historia.reloj:
                raise CambioHistoriaIncoherente("La acción no continúa la historia vigente.")
            historia.registrar_accion(
                accion.fin, accion.cambios, accion.eventos, correcciones=accion.correcciones)
        return historia
