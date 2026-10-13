# Recursos visuales

## Personaje animado

`jugador_acciones.png` es una hoja de 4 columnas y 2 filas, generada con imagegen
integrado usando jugador.png como referencia. No reemplaza el original. Primera
fila: cuatro pasos de carrera. Segunda: dos ataques y dos poses de caida. La vista
extrae las celdas y las escala con Pillow al cargar; no cambia los datos del juego.

Prompt de la version integrada: "Game developer sprite atlas, not an illustration collage. Canvas is 4 columns by 2 rows of identical rectangular cells. EIGHT SMALL isolated copies of the reference tiger-costume man, each only HALF of its cell width and 65 percent of its cell height, with HUGE EMPTY TRANSPARENT SPACING between all figures. Exact cell centers horizontally x=12.5%,37.5%,62.5%,87.5%. Top row feet y=45% of canvas; bottom row feet y=95%. Top row four different running stride poses facing right. Bottom row first two claw attack poses; bottom row third falling backward, fourth lying defeated. Same scale throughout. Full character in each cell; all tails and limbs stay well within own cell. Transparent alpha blank background with absolutely no haze or glow or shadows. Preserve orange tiger hood, face, belt, claws and tail. Hand-painted fantasy sprite. No text no lines. Generous empty transparent margins are essential."

Los PNG se resuelven por tipo de catalogo. Los objetos se muestran en el suelo
y en el detalle del inventario; los enemigos en la escena. Las trampas conservan
su texto de estado y un dibujo de respaldo cuando no existe PNG.

Antidoto y antorcha: archivos originales proporcionados por el usuario,
copiados sin editar, con transparencia RGBA.

Cinco recursos adicionales generados con la herramienta integrada imagegen
el 2026-10-13. Prompts:

- `itm_coraza_cuero.png`: Single isolated inventory icon for a fantasy dungeon game: a rugged leather cuirass, sleeveless chest armor with stitching and iron buckles. Hand-painted game illustration, strong clean silhouette, restrained detail, dark outline, readable at 26 pixels, centered complete object filling canvas, true transparent background, no scenery, no text, no border, no extra objects.
- `itm_llave_bronce.png`: Single isolated inventory icon for a fantasy dungeon game: a bronze medieval key, round bow and clearly readable teeth, warm gold metal. Hand-painted game illustration, strong clean silhouette, restrained detail, dark outline, readable at 26 pixels, centered complete object filling canvas, true transparent background, no scenery, no text, no border, no extra objects.
- `itm_llave_negra.png`: Single isolated inventory icon for a fantasy dungeon game: a black iron gothic key, diamond-shaped bow and clearly readable teeth, cool silver edge highlights. Hand-painted game illustration, strong clean silhouette, restrained detail, dark outline, readable at 26 pixels, centered complete object filling canvas, true transparent background, no scenery, no text, no border, no extra objects.
- `itm_pergamino_retroceso.png`: Single isolated inventory icon for a fantasy dungeon game: an ancient parchment scroll, curled ends, a luminous turquoise counterclockwise arrow symbol, no letters. Hand-painted game illustration, strong clean silhouette, restrained detail, dark outline, readable at 26 pixels, centered complete object filling canvas, true transparent background, no scenery, no text, no border, no extra objects.
- `trp_dardos.png`: Single isolated inventory icon for a fantasy dungeon game: a compact ancient stone dart trap mechanism with three visible steel darts. Hand-painted game illustration, strong clean silhouette, restrained detail, dark outline, readable at 26 pixels, centered complete object filling canvas, true transparent background, no scenery, no text, no border, no extra objects.
