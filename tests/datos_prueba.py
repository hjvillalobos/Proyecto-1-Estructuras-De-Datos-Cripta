from copy import deepcopy
from threading import Event

from datos.almacen import AlmacenLocal
from red.errores import PresupuestoAgotado


class ServidorFalso:
    def __init__(self, salas=23, presupuesto=100, version="v1", version_catalogo="cat1"):
        self.cantidad = salas
        self.version = version
        self.version_catalogo = version_catalogo
        self.solicitudes_realizadas = 0
        self.presupuesto_solicitudes = None
        self.llamadas = []
        self.presupuesto = presupuesto
        self.invertir = False
        self.omitir = False
        self.bloquear = False
        self.empezo = Event()
        self.continuar = Event()
        self.cerrado = False

    def configurar_presupuesto(self, limite):
        self.presupuesto_solicitudes = limite
        if self.solicitudes_realizadas > limite:
            raise PresupuestoAgotado("Presupuesto de prueba excedido.")

    def _contar(self, operacion, valores=()):
        if (self.presupuesto_solicitudes is not None
                and self.solicitudes_realizadas >= self.presupuesto_solicitudes):
            raise PresupuestoAgotado("Presupuesto de prueba agotado.")
        self.solicitudes_realizadas += 1
        self.llamadas.append((operacion, tuple(valores)))

    def listar_criptas(self):
        self._contar("lista")
        return {"criptas": [{"id": "prueba", "nombre": "Prueba",
                             "salas": self.cantidad, "dificultad": 1}]}

    def obtener_datos_generales(self, cripta_id):
        self._contar("generales")
        self.configurar_presupuesto(self.presupuesto)
        return {"id": cripta_id, "version": self.version, "salas_total": self.cantidad,
                "paginas": (self.cantidad + 49) // 50, "salas_por_pagina": 50,
                "sala_inicial": 100, "sala_salida": 100 + self.cantidad - 1,
                "llave_salida": "obj_0", "presupuesto_solicitudes": self.presupuesto,
                "inventario_max": 10,
                "jugador": {"vida_max": 30, "ataque": 6, "defensa": 2, "velocidad": 100}}

    def obtener_version_cripta(self, cripta_id):
        self._contar("version_cripta")
        return {"id": cripta_id, "version": self.version}

    def obtener_version_catalogo(self):
        self._contar("version_catalogo")
        return {"version": self.version_catalogo}

    def obtener_esqueleto(self, cripta_id, pagina=1):
        self._contar("pagina", [pagina])
        salas = []
        for i in range((pagina - 1) * 50, min(pagina * 50, self.cantidad)):
            salidas = {}
            if i:
                salidas["O"] = {"sala": 100 + i - 1}
            if i + 1 < self.cantidad:
                salidas["E"] = {"sala": 100 + i + 1}
            salas.append({"id": 100 + i, "nombre": f"Sala {i}", "salidas": salidas})
        return {"pagina": pagina, "total_paginas": (self.cantidad + 49) // 50, "salas": salas}

    def obtener_contenido_salas(self, cripta_id, salas_ids):
        self._contar("contenido", salas_ids)
        if self.bloquear:
            self.empezo.set()
            if not self.continuar.wait(5):
                raise RuntimeError("No se liberó la carga de prueba.")
        contenido = [
            {"sala": sala, "enemigos": [{"instancia": f"e-{sala}", "tipo": "enemigo"}],
             "objetos": [f"obj_{sala % 7}"], "trampas": []}
            for sala in salas_ids
        ]
        if self.invertir:
            contenido.reverse()
        if self.omitir:
            contenido = contenido[:-1]
        return {"contenido": contenido}

    def obtener_catalogo(self, ids):
        self._contar("catalogo", ids)
        entidades = []
        for clave in ids:
            if clave == "enemigo":
                entidades.append({"id": clave, "clase": "enemigo", "nombre": "Enemigo",
                                  "vida_max": 12, "ataque": 3, "defensa": 1, "velocidad": 100,
                                  "comportamiento": "guardián", "suelta": ["pocion"]})
            elif clave == "pocion":
                entidades.append({"id": clave, "clase": "pocion", "nombre": "Poción",
                                  "peso": 1, "valor": 2, "cura": 5})
            elif clave == "pocion_vel":
                entidades.append({"id": clave, "clase": "pocion", "nombre": "Poción de velocidad",
                                  "peso": 1, "valor": 3, "modificador_velocidad": 2.0, "duracion": 300})
            elif clave == "obj_0":
                entidades.append({"id": clave, "clase": "llave", "nombre": "Llave maestra",
                                  "peso": 1, "valor": 5, "abre": "obj_0"})
            else:
                entidades.append({"id": clave, "clase": "arma", "nombre": self.version_catalogo,
                                  "peso": 1, "valor": 3, "ataque_bonus": 1})
        if self.invertir:
            entidades.reverse()
        if self.omitir:
            entidades = entidades[:-1]
        return {"entidades": deepcopy(entidades)}

    def cerrar(self):
        self.cerrado = True


def crear_paquete(carpeta, salas=23):
    servidor = ServidorFalso(salas)
    almacen = AlmacenLocal(carpeta)
    almacen.guardar_lista(servidor.listar_criptas())
    generales = servidor.obtener_datos_generales("prueba")
    almacen.guardar_generales(generales)
    for pagina in range(1, generales["paginas"] + 1):
        almacen.guardar_pagina("prueba", servidor.version, servidor.obtener_esqueleto("prueba", pagina))
    for inicio in range(0, salas, 10):
        ids = list(range(100 + inicio, 100 + min(inicio + 10, salas)))
        for contenido in servidor.obtener_contenido_salas("prueba", ids)["contenido"]:
            almacen.guardar_contenido("prueba", servidor.version, contenido)
    almacen.guardar_version_catalogo(servidor.version_catalogo)
    ids = [f"obj_{i}" for i in range(7)] + ["enemigo", "pocion", "obj_0"]
    ids = list(dict.fromkeys(ids))  # deduplicar
    for ficha in servidor.obtener_catalogo(ids)["entidades"]:
        almacen.guardar_ficha(servidor.version_catalogo, ficha)
    return almacen
