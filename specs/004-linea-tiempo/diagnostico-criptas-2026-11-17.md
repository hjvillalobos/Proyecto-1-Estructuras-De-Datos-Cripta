# Diagnostico de las criptas disponibles — 2026-11-17

Revision sin reparaciones de criptas. Fuente: listado y versiones locales de
`.cache/cripta`, copiados a una carpeta de ensayo. Se selecciono explicitamente
el catalogo ya existente `4b9e75a42be5`; la fuente tenia `cat1` como puntero activo,
que no contenia la ficha `itm_antorcha`. No se cambiaron mapas, llaves, reglas ni
el bloqueo de inicio de ninguna cripta. No hubo solicitudes de red.

| Orden visible | ID y nombre | Verificacion | Carga offline comprobada |
| --- | --- | --- | --- |
| 1 | cripta-02 — Catacumbas menores | Resoluble | Motor inicializado y contenido de las 20 salas cargado |
| 2 | cripta-03 — Catacumbas medias | Resoluble | Motor inicializado y contenido de las 40 salas cargado |
| 3 | cripta-04 — Catacumbas profundas | Resoluble | Motor inicializado y contenido de las 50 salas cargado |
| 4 | cripta-05 — Cripta sellada | No resoluble; inicio normal bloqueado | La copia tambien carece del contenido offline de sala 1 |
| 5 | cripta-06 — Cripta de referencia | Resoluble | Motor inicializado y contenido de las 300 salas cargado |

La cuarta NO es `cripta-04`: el listado disponible comienza por `cripta-02`.

## Explicacion para el profesor

Cripta sellada (`cripta-05`, version `48bfa3b75055`) no presenta un fallo de
compilacion. La aplicacion rechaza su inicio normal porque el verificador detecta
un bloqueo circular entre las llaves negra y de hierro. La llave de hierro esta
en sala 24 y la negra en sala 23, ambas inaccesibles con las dependencias actuales.
Entre las puertas bloqueadas estan 7 E hacia 22 (requiere hierro), 12 E hacia 24
(requiere negra) y 19 N hacia 20 (requiere negra). Se conservo este resultado y
no se habilito la cripta por la fuerza.

Ademas, al probar la preparacion directa del motor sin pasar por el permiso de
inicio, el paquete local responde «Offline: faltan datos para sala 1 de
cripta-05». Es un segundo problema de disponibilidad de esta copia; no significa
que la API actual carezca de esa sala. No se descargo ni reparo su contenido.

## Alcance real de las comprobaciones

Las otras cuatro inicializan el motor con semilla 42 y permiten cargar todo su
contenido local. Cripta-02 tambien se inicio y recorrio de sala 1 a sala 2 en la
GUI real con Tigre y Tigresa, sin red. El resultado «resoluble» es la prueba de
alcanzabilidad acumulada del proyecto; no demuestra una partida completa hasta
la victoria, supervivencia en combate ni una trayectoria unica cuando existen
salidas sin regreso. No se jugaron manualmente las cinco hasta el final ni se
consulto el servicio actual.

Resultados exactos, versiones y causas:
[diagnostico-criptas-2026-11-17.json](diagnostico-criptas-2026-11-17.json).
