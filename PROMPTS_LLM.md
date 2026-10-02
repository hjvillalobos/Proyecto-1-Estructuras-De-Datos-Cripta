# Bitácora de uso de LLM

Este archivo registra los prompts relacionados con el proyecto, conforme al apartado 10.3 del enunciado. Cada integrante debe agregar su propia entrada en el momento de usar un LLM.

## 2026-09-17

- **Herramienta/modelo:** Codex (GPT-5)
- **Prompt textual:** "Adjunto los PDFs del proyecto. Voy a desarrollar la Parte B ('Red, Cliente API y caché') en Python desde cero. Por favor, analiza mi sección y propón una hoja de ruta de alto nivel para que yo empiece a estructurar el código.
Durante el desarrollo, actuarás como mi revisor técnico: asegúrate de que mis avances cumplan los lineamientos del PDF (en especial el registro de prompts del LLM) y cuestiona cualquier mala decisión arquitectónica que yo tome."
- 
- **Uso de la respuesta:** Revisar el enunciado, identificar restricciones específicas para el rol B y definir exclusivamente el primer paso de implementación.

### 2026-09-18

- **Herramienta/modelo:** Codex (GPT-5)
- **Prompt textual:** "Ya creé el esqueleto de carpetas y los archivos correspondientes a mi parte del proyecto. Creé el repositorio en GitHub con mi rama features/cliente-api-mocks. Considero comenzar en cliente_api implementando lo del HTTP para interactuar con CRIPTA y la versión MOCK temporal que retorna diccionarios estáticos simulando respuestas JSON. Esto usando el contenido del enunciado del proyecto como ejemplo, tales como: Datos generales de una cripta, Esqueleto, Contenido de salas, Catálogo. Dame tu criterio."
- **Uso de la respuesta:** revisar el diseño inicial del cliente HTTP y del adaptador mock.

### 2026-09-19

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Aquí está mi implementación en Python de la clase ClienteApi que utiliza diccionarios estáticos del enunciado para simular las peticiones HTTP de datos generales, esqueleto, contenido y catálogo. ¿Está correcta la lógica de las funciones?"
- **Uso de la respuesta:** Identificar y corregir un error estructural en el diccionario base y en la lógica de filtrado de la función obtener_catalogo.


### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Ahora sigamos con el archivo catalogo.py. ¿Cómo hago la clase para revisar qué IDs faltan en la caché, pedirlos a la API en grupos de 10 y convertirlos en objetos FichaCatalogo?"
- **Uso de la respuesta:** Escribir la estructura de la clase GestorCatalogo para organizar las peticiones en lotes y mapear los JSON a los objetos del contrato.

### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Tengo que programar la tabla hash para la caché desde cero en Python, sin usar diccionarios (dict). Pensaba usar listas como si fueran arreglos estáticos en C++ y manejar las colisiones por encadenamiento. ¿Me ayudas con la estructura inicial y una función hash sencilla para llaves de texto?"
- **Uso de la respuesta:** Obtener la estructura base de la tabla hash usando listas nativas de Python para cumplir con las reglas del proyecto.


### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Necesito agregar una política de reemplazo (LRU) que controle que elementos deben salir de cache cuando este alcanza su capacidad máxima a la tabla hash previamente creada. Se debe verificar si el elemento se encuentra actualmente en uso, es decir si el ID tiene referencias activas ( en_uso > 0 ), esto con el fin de que el LRU no borre elementos que siguen vivos en el juego. Si dicho elemento tiene una referencia activa se debe pasar al siguiente y así sucesivamente hasta encontrar un elemento que no tenga esta particularidad. El método de orden será una lista doblemente enlazada, la implementación de la lista debe incluir una clase Nodo.  La misma será utilizada para llevar un control cada que vez que se inserta un ID. El fondo de la lista me dirá el candidato a ser eliminado."
- **Uso de la respuesta:** Escribir la lógica de desalojo en cache.py, implementando la clase NodoLRU para simular punteros, actualizando las funciones de búsqueda e inserción, y agregando un método para incrementar el contador de referencias.


### 2026-09-20

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Me gustaría revisar cómo se vería el archivo de pruebas (tests/test_cache.py) para confirmar que mi lista doblemente enlazada está desalojando el elemento correcto y respetando el contador de referencias activas."
- **Uso de la respuesta:** Crear casos de prueba automatizados usando unittest para validar la inserción, el desalojo estándar del elemento más antiguo y la protección de elementos bloqueados por el motor del juego.


### 2026-09-22

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Implemente la logica de los request en la funcion def _hacer_peticion_get manejando el error 429 con un tiempo de espera prudencial, ademas he completado las funciones actualizadas de cliente_api para usar la función central que maneja requests: obtener_datos_generales, obtener_esqueleto, obtener_contenido_salas y obtener_catalogo. Utilicé f-strings y join para los parámetros haciendo un llamado a la funcion _hacer_peticion_get previamente creada"
-  **Uso de la respuesta:** Validar la refactorización de las rutas, corrigiendo los endpoints /salas y /catalogo para coincidir con la especificación del servidor.


### 2026-09-22

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Al probar la conexión HTTP real me da un error 400. Agregué un print de depuración y la respuesta del servidor dice: 'Invalid request: missing or malformed X-Cripta-Client-Id'. El encabezado que se va a enviar es {'X-Cripta-Cliente-Id': '0e56e27d-d6fd-43de-8b10-d6955e625f65'}."
-  **Uso de la respuesta:** Identificar y corregir un error tipográfico en la llave del diccionario del encabezado ("Cliente" en lugar de "Client") y validar la correcta generación de identificadores UUID4.


### 2026-09-22

- **Herramienta/modelo:** Gemini
- **Prompt textual:** "Necesito implementar el módulo de precarga (GestorPrecarga). Debe usar el ClienteApi para descargar los datos generales, el esqueleto de la primera página y el contenido de esas salas. Luego, debe extraer todos los IDs de objetos, enemigos y trampas de ese contenido, eliminar los duplicados, y enviarlos al GestorCatalogo para que los precargue en la tabla hash."
-  **Uso de la respuesta:** Implementar la clase GestorPrecarga en red/precarga.py para inicializar el estado del juego, coordinando las peticiones HTTP iniciales y el poblamiento de la memoria caché mediante inyección de dependencias.


### 2026-09-21 (Persona C)

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pasé el enunciado completo, la división de trabajo del equipo (documento CRIPTA_Division_de_trabajo) y la documentación Swagger del API, aclarando que a mí me toca Persona C (inventario, historial de retroceso, rastro y enemigos), y le pedí que primero entendiera bien el proyecto antes de proponerme un plan.
- **Uso de la respuesta:** Entender el alcance completo de mi parte y armar el orden en que iba a implementar cada módulo (rastro -> inventario -> enemigos -> historial), verificado contra las secciones exactas del enunciado (§2.7-§2.9, §2.11, §4.5-§4.7).

### 2026-09-27 (Persona C)

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pedí implementar modelo/rastro.py, modelo/inventario.py, modelo/enemigos.py y modelo/historial.py según el plan que habíamos acordado, con pruebas unitarias, agregando solo la clase ObjetoInstancia a modelo/tipos.py de forma aditiva (idéntica a la que ya tenía Sebas en su rama) para no generar conflictos.
- **Uso de la respuesta:** Base de mis 4 módulos con 34 pruebas unitarias (unittest), todas corriendo correctamente.

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pedí revisar qué habían subido mis compañeros (a main y a sus ramas) y actualizar mi rama feature/estado-jugador sin romper nada de lo mío ni de lo de ellos.
- **Uso de la respuesta:** Fusionar los cambios de main (cliente HTTP real, ordenamiento, snapshots, vista, guardado binario) y traer utilidades/medicion.py de la rama de Belén, verificando en cada paso que las pruebas siguieran pasando. También cambié mi vista_ordenada del inventario para usar utilidades.ordenamiento.ordenar en vez de un ordenamiento propio, tal como lo pedía controlador/contrato.py.

- **Herramienta/modelo:** Claude Code (Sonnet 5)
- **Prompt textual:** Le pedí ayuda para escribir las secciones de DECISIONES.md que me corresponden (inventario, historial, rastro), con evidencia real medida con --bench y no números inventados.
- **Uso de la respuesta:** Redactar las 3 secciones del Documento de Decisiones, con las mediciones reales que se obtuvieron corriendo utilidades/medicion.py sobre mis propios módulos.


