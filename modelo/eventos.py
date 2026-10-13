from modelo.tipos import Evento

class ColaEventos:
    """
    Cola de prioridad (heap binario mínimo) implementada a mano.
    Ordena por (tiempo, secuencia) para tener desempate determinista.
    """

    def __init__(self):
        self._datos = []       # lista que actúa como heap
        self._contador = 0     # secuencia creciente para desempates


    def _padre(self, i):
        return (i - 1) // 2

    def _hijo_izq(self, i):
        return 2 * i + 1

    def _hijo_der(self, i):
        return 2 * i + 2

    def esta_vacia(self):
        return len(self._datos) == 0

    def _es_menor(self, evento_a, evento_b):
        # Orden total: primero tiempo, si empatan, secuencia
        return (evento_a.tiempo, evento_a.secuencia) < (evento_b.tiempo, evento_b.secuencia)

    def _intercambiar(self, i, j):
        self._datos[i], self._datos[j] = self._datos[j], self._datos[i]


    def _sube(self, i):
        while i > 0:
            padre = self._padre(i)
            if self._es_menor(self._datos[i], self._datos[padre]):
                self._intercambiar(i, padre)
                i = padre
            else:
                break

    def _baja(self, i):
        n = len(self._datos)
        while True:
            izq = self._hijo_izq(i)
            der = self._hijo_der(i)
            menor = i

            if izq < n and self._es_menor(self._datos[izq], self._datos[menor]):
                menor = izq
            if der < n and self._es_menor(self._datos[der], self._datos[menor]):
                menor = der

            if menor == i:
                break

            self._intercambiar(i, menor)
            i = menor


    def insertar(self, tiempo, tipo, referencia):
        """
        Crea y agenda un nuevo evento. Devuelve el objeto Evento
        para que quien lo creó (juego.py, efectos.py) pueda guardar
        la referencia y cancelarlo/reprogramarlo después.
        """
        evento = Evento(
            tiempo=tiempo,
            secuencia=self._contador,
            tipo=tipo,
            referencia=referencia,
            cancelado=False,
            en_cola=True,
        )
        self._contador += 1
        self._datos.append(evento)
        self._sube(len(self._datos) - 1)
        return evento

    def extraer_minimo(self):
        """
        Saca y devuelve el evento válido (no cancelado) con menor
        (tiempo, secuencia). Descarta silenciosamente los cancelados
        que encuentre en el camino (invalidación perezosa).
        Devuelve None si la cola queda vacía sin encontrar ninguno válido.
        """
        while not self.esta_vacia():
            raiz = self._datos[0]
            ultimo = self._datos.pop()
            raiz.en_cola = False

            if self._datos:
                self._datos[0] = ultimo
                self._baja(0)

            if not raiz.cancelado:
                return raiz
            # si estaba cancelado, seguimos el ciclo y sacamos el siguiente

        return None

    def cancelar(self, evento):
        """
        Invalidación perezosa: no busca ni borra el evento del heap,
        solo lo marca. Se descarta cuando le toque salir en extraer_minimo().
        """
        evento.cancelado = True

    def reprogramar(self, evento_viejo, nuevo_tiempo):
        """
        Usado cuando cambia la velocidad de un actor y su próxima acción
        debe moverse en el reloj (§2.3). Cancela el evento viejo e inserta
        uno nuevo con el mismo tipo/referencia pero tiempo actualizado.
        """
        self.cancelar(evento_viejo)
        return self.insertar(nuevo_tiempo, evento_viejo.tipo, evento_viejo.referencia)
    def insertar_con_secuencia(self, tiempo, secuencia, tipo, referencia):
        """Para restaurar una partida: reinserta un evento con SU número de secuencia original."""
        evento = Evento(tiempo=tiempo, secuencia=secuencia, tipo=tipo,
                        referencia=referencia, cancelado=False, en_cola=True)
        self._datos.append(evento)
        self._sube(len(self._datos) - 1)
        return evento

    def reinsertar(self, evento):
        """Recupera un evento extraido conservando su identidad y secuencia."""
        if not evento.en_cola:
            evento.en_cola = True
            self._datos.append(evento)
            self._sube(len(self._datos) - 1)

    def pendientes(self):
        """Eventos vigentes (no cancelados), para guardar la partida."""
        return [e for e in self._datos if not e.cancelado]

    def proxima_secuencia(self):
        return self._contador

    def fijar_contador(self, valor):
        self._contador = valor
