# 📓 Bitácora Detallada del Proyecto TidalAI Companion

> **Proyecto**: Sistema de generación de patrones TidalCycles con IA en Raspberry Pi 3B+
> 
> **Fecha de inicio**: 25 de enero de 2026
> **Estado**: Fase 32 Completada - Ecosistema Pro (v5.1.8)
> 
> **Objetivo**: Crear un ecosistema distribuido donde una Raspberry Pi actúa como "cerebro creativo", generando patrones musicales inteligentes para TidalCycles ejecutado en un PC principal.

---

## 📅 Día 1 - 25 de Enero de 2026

### 🌞 Sesión 1: Conceptualización y Arquitectura Distribuida (07:33 - 08:30)

#### 🎯 Objetivo Estratégico
Diseñar una arquitectura que desacople la generación de IA de la síntesis de audio, permitiendo que dispositivos de baja potencia (RPi 3) enriquezcan setups profesionales sin introducir latencia de audio.

#### 🔧 Decisiones Arquitectónicas Profundas

**1. El Paradigma de "Cerebro Remoto"**
La decisión más crítica fue separar el *runtime* de audio (SuperCollider/Tidal en PC) del *runtime* generativo (Python en RPi).
- **Problema de Latencia**: Correr modelos de ML en el mismo hilo que el motor de audio en una máquina limitada causa *buffer underruns* (glitches).
- **Solución**: La RPi opera asíncronamente. Envía órdenes OSC "fire and forget". Si la IA tarda 200ms en pensar, no importa; el audio en el PC sigue sonando perfecto.

**2. Protocolo de Comunicación: UDP vs TCP**
Elegimos **OSC sobre UDP** por razones específicas de música en tiempo real:
- **TCP (Reliability)**: Si un paquete se pierde, TCP detiene el flujo para retransmitir. En música, esto es fatal (jitter). Es mejor perder una nota que detener el ritmo.
- **UDP (Speed)**: Envío instantáneo. TidalCycles y SuperCollider están optimizados para recibir ráfagas de mensajes UDP.

**3. Stack Tecnológico Minimalista (Constraints de RPi 3B+)**
Con solo 1GB de RAM, no podíamos usar frameworks pesados (como Django o Transformers gigantes).
- **Backend**: Python puro + Flask (Microframework).
- **IA**: Markov Chains (Costo de memoria O(N) vs O(N^2) de Transformers).
- **Frontend**: Vanilla JS. Evitamos React/Vue para no requerir transpilación ni node_modules de 500MB en la RPi.

#### 🏗️ Estructura de Directorios (Mentalidad Scalable)
```
tidalai-companion/
├── raspberry-pi/          # EL CEREBRO (Python/AI)
│   ├── generator/         # Lógica pura de generación
│   ├── web/              # API e Interfaz (Estado del sistema)
│   └── logic/            # (Futuro) Controladores de Hardware
├── pc-side/              # EL MÚSCULO (Audio Engine)
│   ├── osc-receiver.scd  # El intérprete que "toca" los mensajes
│   └── bridge/           # Adaptadores para Haskell
└── docs/                 # La Memoria del Proyecto
```

---

### ☀️ Sesión 2: Implementación del Core (MVP1) (08:45 - 10:15)

#### 🎯 Objetivo Técnico
Levantar la infraestructura de comunicación completa. Lograr que un click en una web en la RPi haga sonar un bombo en el PC.

#### 💻 Desarrollo del Backend (Python)

**Desafío del Mapeo de Parámetros**:
El generador (`pattern_generator.py`) tuvo que resolver cómo traducir conceptos abstractos ("Densidad 60%") a código Tidal concreto.
- **Algoritmo de Densidad**: Implementamos una probabilidad ponderada. Si `density=0.8`, la probabilidad de insertar silencios (`~`) baja drásticamente.
- **Algoritmo de Euclides**: Usamos la notación `(3,8)` de Tidal. `gen_euclidean(k, n)` distribuye `k` golpes en `n` pasos lo más equitativamente posible. Esto garantiza ritmos "bailables" automáticamente.

**Cliente OSC (`osc_client.py`)**:
Implementamos reconexión automática y manejo de errores silencioso. Si el PC se desconecta, la RPi no crashea, simplemente loguea el error y sigue esperando.

#### 🎨 Desarrollo del Frontend (Glassmorphism UI)

Decidimos usar una estética **Cyberpunk/Glassmorphism** no solo por "cool factor", sino por usabilidad en entornos oscuros (clubs/estudios).
- **Contraste**: Textos blancos sobre fondos traslúcidos oscuros.
- **Feedback Inmediato**: Cada acción genera un flash visual o actualización de log. En live performance, saber que el sistema recibió el comando es vital.

#### 🔊 El Receptor SuperCollider (La Primera Barrera)
El script `osc_receiver.scd` inicial fue sencillo pero crucial. SuperCollider es un lenguaje orientado a objetos idiosincrásico.
- **Reto**: Recibir un string OSC y ejecutarlo. SC no tiene un `eval()` directo de seguridad para strings arbitrarios que vienen de la red.
- **Solución MVP**: En esta fase, solo imprimíamos el string en la consola para que el usuario lo copiara. La automatización real quedó relegada para fases posteriores por seguridad.

---

### 🌤️ Sesión 3: Inteligencia Artificial con Cadenas de Markov (11:00 - 13:00)

#### 🎯 Objetivo Cognitivo
Reemplazar el generador aleatorio por algo que "entienda" de música.

#### 🧠 Profundizando en el Modelo de Markov
No usamos una librería genérica. Escribimos `markov_model.py` desde cero para adaptarlo a la sintaxis de Tidal.
- **Tokenización Especializada**: 
  - Una cadena de texto normal separa por espacios.
  - Nuestro tokenizador entiende que `sound "bd*4"` es una unidad semántica diferente a `speed 2`.
  - Tratamos los bloques entre comillas como tokens atómicos para preservar la integridad de los micro-ritmos internos de Tidal.

**La Variable "Temperatura"**:
Implementamos un sistema de selección estocástica ponderada.
- **T < 1.0 (Frío)**: El modelo elige casi siempre la transición más probable (el camino más transitado). Resultado: Patrones repetitivos y seguros.
- **T > 1.0 (Caliente)**: Se aplana la distribución de probabilidad. El modelo se arriesga con transiciones inusuales. Resultado: Caos creativo.

#### 🤖 Automatización con Systemd
Para que el sistema sea un "appliance" real, debe encenderse solo.
- Creamos `tidalai.service`.
- Configuramos `Restart=always` con un delay de 5s. Esto hace que el sistema sea resiliente a fallos de red momentáneos al arrancar.

---

### 🌙 Sesión 4: Fase 3 - Visualización y Estabilidad Crítica (Suprema) (06:10 - Generada el 26 Enero)

#### 🎯 Objetivo Crítico
El sistema funcionaba, pero el receptor SuperCollider era inestable y "ciego". El usuario pidió un visualizador y arreglar los errores de sintaxis que impedían la compilación.

#### 🐞 La Saga del Debugging en SuperCollider (`osc_receiver.scd`)

Esta fue la sesión más técnica y compleja. SuperCollider tiene trampas sintácticas únicas.

**1. El Error `unexpected 'else'`**
- **Síntoma**: El intérprete lanzaba `ERROR: syntax error, unexpected 'else'`.
- **Causa Raíz**: En muchos lenguajes, `if (x) { ... } else { ... }` es una estructura de control nativa. En SuperCollider (sclang), `if` es un **método** de la clase Boolean.
- **La Trampa**: La sintaxis correcta es `condicion.if({true_func}, {false_func})` o `if(cond, {true}, {false})`.
- **El Fallo**: Yo estaba escribiendo bloques `if { ... }` seguidos de `else { ... }` al estilo C/Java. Sclang interpretaba el cierre de llave `}` como el fin de la instrucción y se encontraba un `else` huérfano después.

**2. La Solución "Nuclear": Aplanamiento Lógico**
En lugar de pelear con el anidamiento de llaves `{ { } }` que causaba el error `unexpected , expecting }`, opté por reescribir la lógica completa usando **Guard Clauses** secuenciales.

### [2026-01-27] Sesión 13: Transparencia Musical y Agilidad UX
- **Transparencia Lógica**: El panel de razonamiento ahora muestra los cálculos internos de las reglas musicales (kicks, snares, densidad) cuando la IA no está activa.
- **Sincronización de Modos**: Corregido bug que enviaba 'use_ai' incorrectamente al backend.
- **Atajos Globales**: Implementado cierre de modales con tecla `Esc`.
- **Backend Hardening**: Corregido error de indentación en `pattern_generator.py`.
- Antes (Anidado - Propenso a error):
  ```supercollider
  if (esMelodia) {
      if (muchasNotas) { ... } else { ... }
  } else { ... }
  ```
- Ahora (Secuencial - Robusto):
  ```supercollider
  if (esMelodia) { ... };
  if (esRitmo) { ... };
  if (esSingle) { ... };
  ```
  Esto eliminó la ambigüedad sintáctica y hizo el código mantenible.

**3. Polifonía Real: Samples vs Notas**
El código anterior trataba todo igual. Ahora el receptor inspecciona el mensaje:
- Si detecta una lista de notas `["0", "3", "7"]`, dispara una ráfaga rápida (arpegio).
- Si detecta solo texturas, dispara un acorde o sample sostenido.

#### 📊 Visualizador de Audio (Web Audio API)

El visualizador (`phase3-features.js`) fue un desafío de integración frontend.

- **¿Por qué no recibir el audio del servidor?**
  Transmitir audio raw desde el PC a la RPi y luego al navegador vía WebSocket tendría una latencia de >500ms. Inviable para visualización rítmica.
  
- **La Solución Local**:
  Usamos la API del navegador `AudioContext` + `CreateAnalyser()`.
  El navegador captura el audio directamente de la tarjeta de sonido local (vía micrófono o "Stereo Mix").
  - **Resultado**: Latencia cero. El visualizador reacciona instantáneamente a lo que escuchan los oídos del usuario.
  
- **Estética Reactiva**:
  Implementé lógica de color condicional:
  - `state.patternType === 'drums'` → Barras Rojas/Fuego.
  - `state.patternType === 'bass'` → Barras Verdes/Matrix.
  - Esto refuerza la conexión visual con lo que está generando la IA.

#### 🏁 Estado Final del Proyecto (v1.0)
El sistema ha evolucionado de un simple script de Python a una suite completa de producción musical asistida por IA.
- **Robustez**: El backend se recupera de fallos.
- **Usabilidad**: Interfaz táctil, presets, historial.
- **Musicalidad**: Algoritmos euclidianos y modelos de Markov.
- **Feedback**: Visualización de audio en tiempo real y logs detallados.

---

## 🔮 Roadmap Futuro (Post-v1.0)

1. **Bridge Haskell Real**: Crear un binario en Haskell que use la librería `hint` para inyectar código directamente en el intérprete de Tidal, eliminando la necesidad de SuperCollider como intermediario de texto.
2. **RNN / LSTM**: Entrenar un modelo pequeño (TinyLlama o similar optimizado) en la RPi 5 para capturar estructuras musicales a largo plazo (intro, estribillo), algo que Markov no puede hacer bien.
3. **MIDI Input**: Permitir que el usuario "toque" el piano y la IA responda con un contrapunto en tiempo real.

---

## 📅 Día 2 - 26 de Enero de 2026

### 🚀 Sesión 5: El Renacimiento del Cerebro (v1.5) (09:00 - 11:15)

#### 🎯 Objetivo Evolutivo
Transformar la IA de un simple imitador a un agente con **gustos propios** y capacidad de introspección visual.

#### 🧬 Implementación de Selección Artificial (Phase 4)
No basta con generar; hay que saber elegir.
- **Función de Fitness Multidimensional**: Implementamos un evaluador en `evolutionary_trainer.py` que puntúa patrones basándose en métricas configurables por el usuario (Densidad, Variedad, Groove).
- **El Ciclo G/S (Generate/Select)**: La IA ahora puede generar 100 patrones en silencio, evaluarlos según el "gusto" configurado y solo guardar los "supervivientes". Esto garantiza que el corpus de la RPi evolucione hacia la excelencia musical sin intervención humana constante.

#### 🕸️ El Mapa Mental y la Transparencia (Phase 5)
Para que el usuario confíe en la IA, debe entenderla.
- **D3.js Force-Directed Graph**: Implementamos una visualización de grafos que mapea el modelo Markov. Ver los sonidos como nodos interconectados ayuda al músico a entender los "atajos mentales" que la IA ha aprendido de su corpus.
- **Live Thought Stream**: El "Monólogo Interno" fue la pieza final. Al exponer las probabilidades de cada token (y sus alternativas descartadas), convertimos la generación en un proceso educativo para el usuario.

#### 🛠️ Refactorización de la Raspberry Pi
- **Persistencia**: Añadimos `config_evolution.json` para que los ajustes de la IA sobrevivan a reinicios.
- **Threaded Training**: Implementamos un hilo de fondo en `app.py` que puede ejecutar la "Ronda Nocturna" de forma desatendida.

#### 🏁 Conclusión del Ciclo de Expansión
La TidalAI Companion es ahora un sistema completo de **Creatividad Computacional**. No solo genera código, sino que evoluciona su propio estilo basado en el feedback estético del usuario.

---

### 🌆 Sesión 6: Inmersión Sensorial y Morfado (v1.8) (11:30 - 11:50)

#### 🎯 Objetivo de Diseño
Cerrar la brecha entre el código puro y la experiencia estética. El usuario no solo debe usar la IA, debe *sentir* que está en un entorno reactivo.

#### 🧬 Riff Morphing (Interpolación de Markov)
Escribimos un algoritmo en `pattern_generator.py` para mezclar dos mundos.
- **Técnica**: Blending de distribuciones de probabilidad. En lugar de cambiar un string por otro, el sistema crea un nuevo modelo de Markov donde cada transición es una combinación ponderada de las dos fuentes. El resultado es un "hijo melódico" con ADN de ambos padres.

#### 🎨 Skin Engine y Partículas Bio-Reactivas
Transformamos el frontend estático en una **entidad dinámica**.
- **Theming via Root Variable Interpolation**: Implementamos un motor que detecta el estilo (Cyberpunk, DeepSea, etc.) y re-mapea el CSS en tiempo real con transiciones suaves.
- **Background Particle Burst**: Usamos Canvas 2D para un motor de partículas integrado. Hookeamos los eventos de la API para disparar pulsos visuales (`burst()`) coordinados con la generación de audio.

#### 🏁 Cierre de Laboratorio
El Companion Studio ha mutado de una herramienta técnica a una estación de trabajo artística inmersiva.

---
### 💎 Sesión 19-25: El Salto a Luxury v5 (27-28 Enero)
- **Visuales Hydra**: Integración de WebGL reactivo al código y parámetros musicales.
- **Glassmorphism UI**: Rediseño radical de la interfaz para un look "Dark Luxury".
- **Timeline Centralizada**: Visualización unificada de patrones mono y multi-pista.

### 📐 Sesión 26-28: Inteligencia Teórica y Macro-Wave (28 Enero)
- **Theory Engine**: Implementación de validación musical basada en reglas por género.
- **Rules Editor**: Interfaz para gestionar el "gusto" musical de la IA en tiempo real.
- **Macro-Wave**: Capacidad de generar ensambles completos (d1-d8) con un solo click.

### 🌀 Sesión 29-30: Latent Space y Estabilidad (28 Enero)
- **Latent Engine**: Mezcla vectorial de géneros (e.g., Techno-Ambient Hybrid).
- **Core Recovery**: Gran limpieza de `main.js`, eliminando 500+ líneas de código de compatibilidad heredado y estabilizando el núcleo modular.

### 🔁 Sesión 31-32: Auto-Cycle y Refinamiento UX (28 Enero)
- **Cycle Send**: Implementación del modo de re-envío automático sincronizado con BPM.
- **Segmented Mode Switcher**: Reemplazo del toggle anticuado por un selector de cristal premium para Solo/Macro.

---
**Fin de Bitácora - v5.1.8 (The Pro Ecosystem)**

---

## 📅 Día 3 - 27 de Enero de 2026

### 📦 Sesión 7: La Portabilidad Total (v3.0) (10:00 - 11:00)

#### 🛠️ Correcciones Críticas (Hotfixes)
Durante el despliegue detectamos y solucionamos dos bugs bloqueantes:
1.  **Sintaxis Rota en Floats**: La IA generaba `# speed 1 00` en lugar de `1.00`.
    - *Fix*: Implementamos un sanitizador regex `(\d+)\s+(\d{1,2})(?!\d)` en `pattern_generator.py` que detecta y repara estos "números partidos" antes de enviarlos a Tidal.
2.  **Despliegue Incompleto**: `deploy.bat` ignoraba la carpeta `pc-side`.
    - *Fix*: Añadimos `scp -r .../pc-side` al script de despliegue para asegurar que los instaladores lleguen a la Pi.

#### 🎯 Objetivo: Plug & Play
El usuario necesitaba que la Raspberry Pi fuera un dispositivo autónomo capaz de configurar su propio entorno.
- **Client Kit Generator**: Creamos un endpoint `/api/admin/download-kit` que genera un ZIP dinámico.
- **Auto-Installers**: Desarrollamos `install_windows.ps1` y `install_mac.sh` que detectan dependencias y configuran SuperCollider automáticamente.
- **Accesos Directos Web**: Inyectamos `.url` files en el ZIP para acceso sin configuración de red.

#### 🎨 Sesión 8: Identidad Visual Completa (11:00 - 11:30)
Expandimos el motor de Skins Adaptativos para cubrir huecos estéticos.
- **House**: Nuevo tema "Warm Purple".
- **Breakbeat**: Nuevo tema "Urban Industrial".
- **Experimental**: Nuevo tema "High Contrast Lab".
- **Refactorización CSS**: Eliminación de duplicidades en `app.js` y consolidación de variables en `style.css`.

### 🏗️ Sesión 9: Planificación Arquitectura v4.0 (11:45 - 12:30)
Inicio de la fase de **Maduración del Producto**.
- **Refactorización**: Análisis del monolito `app.js` para su fragmentación.
- **Estructura propuesta**: `js/core` (Estado), `js/ui` (Manager), `js/modules` (API/Utils).

### 🛠️ Sesión 10: Gran Refactorización Modular (v4.0) (12:30 - 15:00)

#### 🎯 Objetivo Técnico
Desmontar el monolito `app.js` (>1500 líneas) en un sistema de módulos ES6 escalable, mantenible y testable.

#### 🔧 Logros de Ingeniería

**1. Arquitectura de Estado Centralizado**
Creación de `js/core/state.js` usando un patrón de observador simple. Esto permite que cualquier parte de la aplicación reaccione a cambios en el patrón actual o en la configuración sin acoplamiento directo.

**2. Desacoplamiento de Responsabilidades**
- **UI Manager**: Gestión única de referencias al DOM. Resolvimos el problema de "selectors recurrentes".
- **Network Module**: Abstracción total de la API. Cambiar de `fetch` a `axios` o `websockets` ahora solo requiere tocar un archivo.
- **Logger System**: centralización de notificaciones `toast` y logs de actividad.

**3. Sistema de Shims de Compatibilidad**
Para no romper el HTML cargado de atributos `onclick`, implementamos una capa de shimming en `main.js` que expone funciones internas al ámbito global (`window`). Es una solución puente elegante hacia un frontend 100% reactivo.

### 🧪 Sesión 11: Estabilización y Restauración de Funcionalidades (15:00 - 15:45)

#### 🎯 Objetivo Estratégico
Recuperar las herramientas de producción que quedaron inoperativas durante la migración modular (ReferenceErrors).

#### 🛠️ Implementaciones Críticas

**1. Módulos Híbridos de Características**
Transformamos los scripts heredados (`advanced-features.js`, `phase2-features.js`, `phase3-features.js`) en módulos ES6 reales.
- Se añadieron `import` explícitos de `state` y `elements`.
- Se corrigieron errores de sintaxis (`async export` → `export async`) que impedían la carga en navegadores estrictos.

**2. Restauración de Herramientas de Composición**
- **Song Templates**: Re-conectado el generador de estructuras completas.
- **Comparator**: Recuperada la UI de comparación de rifs.
- **Dock Tools**: Todos los botones del dock (History, Presets, Jam, Batch) vuelven a ser funcionales bajo el nuevo núcleo modular.

**3. Cache-Busting Agresivo**
Actualización de la versión en `index.html` a **v4.1.3**. En un sistema embebido como la RPi, el caché del navegador es el enemigo nº1 de las refactorizaciones JS. Esto fuerza una recarga limpia de la nueva arquitectura.

---
**Fin de Bitácora - v4.1.3 (The Modular Era)**

---

### 🎨 Sesión 12: Re-arquitectura de Layout (v4.2) (12:00 - 13:00)
- **Diseño de 3 Columnas**: Movido el panel de pensamientos a una columna derecha dedicada para aprovechar pantallas panorámicas.
- **Log de Actividad Full-Width**: Reubicación del log en la base para mejor lectura de historial.
- **Grid Dinámica**: Ajustes de CSS para mantener la integridad en tablets y laptops.

### 📐 Sesión 13: Transparencia Lógica y Agilidad UX
- **Cálculo de Reglas**: Implementado feed de pensamientos cuando no se usa IA, mostrando cómo se eligen los samples y densidades.
- **Atajos Globales**: Implementado cierre de modales y paneles flotantes con la tecla `Esc`.
- **Backend Sync**: Corregida sincronización del modo de generación entre frontend y backend.

### 👁️ Sesión 14: El Ojo de la IA (Integración Hydra v1.0)
- **WebGL Live Canvas**: Integración de la librería `hydra-synth` debajo del editor de código.
- **Reactividad Musical**: Mapeo de Densidad, Complejidad y Estilo a parámetros WebGL.

### ⚡ Sesión 15: Hydra Reactive v2.1 (Full Parity)
- **Análisis de Código**: Hydra ahora "lee" el texto del patrón para variar la energía visual.
- **Suscripción de Estado**: Los visuales cambian instantáneamente al seleccionar un estilo en el dropdown.
- **Cobertura Total**: 10 estilos musicales con 10 algoritmos visuales dedicados.

### 🎛️ Sesión 16: Pulimentado Sensorial (v2.2)
- **Santísima Trinidad de Controles**:
  - `Inestabilidad Visual`: Control de ganancia para Hydra. De la calma a la epilepsia controlada.
  - `Persistencia`: Slider de "Decay" para crear estelas y ghosting visual.
  - `Fricción Musical`: Factor de caos (0-100%) que permite al generador "robar" samples de otros estilos y variar velocidades irracionalmente.
- **Cyberpunk 2.0**: Rediseño total del algoritmo visual para usar neón magenta/cyan y glitching agresivo.

### 🎻 Sesión 16: The Song Conductor (El Director de Orquesta)
Se ha implementado el motor de estructura macro-temporal que permite transformar loops en canciones completas.
- **Backend**: `structure_engine.py` gestiona estados (Intro, Verse, Build, Drop, Outro).
- **Control Dual**: Cuando el Conductor está activo, toma el control del 80% de la densidad/complejidad, dejando al usuario un 20% de influencia ("Bias").
- **UITimeline**: Nuevo panel flotante inferior con visualización de progreso y secciones coloreadas.
- **Acceso**: Botón dedicado 🎻 en el Dock.

### 📐 Sesión 17: The Intelligent Theorist (Constraint Logic)
El sistema ha adquirido conciencia teórica.
- **Theory Engine**: Nuevo módulo backend que aplica reglas estrictas por género (e.g., "Techno requiere bombo 4/4 constante").
- **Validation Loop**: `app.py` ahora reintenta hasta 3 veces si un patrón viola las reglas, antes de rendirse.
- **Judge UI**: Badge visual en el frontend que certifica si el patrón es ✅ "Theoretically Verified" o ⚠️ "Theory Violation".
- **Rules Editor (v4.3.1)**: Nueva interfaz para gestión dinámica de reglas.
    - JSON Rules: Backend modificado para cargar configuración de archivo.
    - Custom Regex: Capacidad de añadir reglas sobre la marcha (e.g. "Prohibido usar claps en Techno").

### 🌀 Sesión 18: Latent Space Navigation (Vector Interpolation)
El sistema ahora puede mezclar géneros matemáticamente.
- **Latent Engine**: Nuevo módulo que define vectores de parámetros por género (density, complexity, tempo, samples).
- **Interpolación Vectorial**: Mezcla lineal entre dos o más géneros (e.g., 70% Techno + 30% Ambient).
- **Blend UI**: Checkbox para activar modo blend, dos selectores de género y slider de mezcla.
- **Single Source of Truth**: Los géneros se leen desde `theory_rules.json` para mantener consistencia.

---
**Fin de Bitácora - v4.4.0 (The Hybrid Brain)**
