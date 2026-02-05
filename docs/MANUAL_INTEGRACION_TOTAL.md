# 📔 Manual de Integración Total: El Ecosistema TidalAI Companion Studio (V5.1)

Este manual constituye el recurso definitivo de ingeniería para el TidalAI Companion Studio. Detalla exhaustivamente la arquitectura, los componentes, la lógica algorítmica y los protocolos de comunicación que permiten a una Raspberry Pi actuar como el "Cerebro Creativo" de un entorno profesional de TidalCycles.

---

## 🚀 1. Arquitectura de Sistemas: El Modelo de Cómputo Distribuido

El sistema TidalAI no funciona como un plugin convencional (VST/AU), sino como una **Arquitectura de Microservicios Distribuidos**. El diseño se basa en el desacoplamiento físico y lógico entre la **Intención Creativa** y la **Síntesis de Audio**.

### 1.1 El Nodo Generativo (Raspberry Pi)
La Raspberry Pi 3B+ (o superior) es el centro neurálgico lógico. Corre un stack Linux Lite con un servidor Flask que gestiona:
- **Inferencia de IA**: Ejecución de cadenas de Markov para predecir secuencias.
- **NLP (Procesamiento de Lenguaje Natural)**: El motor del Oráculo que interpreta deseos semánticos.
- **Orquestación**: La fragmentación de patrones polifónicos en múltiples flujos de datos.

### 1.2 El Nodo de Síntesis (PC Principal)
El PC (Windows/Mac/Linux) es el "Músculo Sónico". No "piensa" la música; simplemente ejecuta instrucciones de bajo nivel recibidas vía red.
- **SuperCollider**: Motor de audio en tiempo real.
- **SuperDirt**: Cargador de samples y puente de efectos.
- **TidalCycles**: Capa de abstracción rítmica (Haskell) que interactúa con SuperDirt.

### 1.3 El Puente de Comunicación (OSC)
El protocolo **Open Sound Control (OSC)** sobre **UDP** es el pegamento. Elegimos UDP por su baja latencia; en música en vivo, es preferible perder un paquete ocasional que detener el flujo de audio esperando una retransmisión TCP.

---

## 🛠️ 2. Guía de Instalación en el PC (Audio-Side)

Para integrar la Raspberry Pi, el PC debe estar preparado para escuchar.

### 2.1 Descargas Requeridas
1.  **Chocolatey (Windows)**: Recomendado para gestionar dependencias. `choco install tidalcycles supercollider`.
2.  **SuperDirt Quarks**: Dentro de SuperCollider, ejecuta `Quarks.install("SuperDirt")`.

### 2.2 El Receptor de Red (`osc_receiver.scd`)
Este script es fundamental. Debe cargarse cada vez que inicies SuperCollider.
- **Función**: Traduce los mensajes `/tidal/pattern` enviados por la RPi en instrucciones ejecutables por SuperDirt.
- **Localización**: `C:\Users\tu-usuario\tidalai-companion\pc-side\osc_receiver.scd`.
- **Configuración de Puertos**: Asegúrate de que el firewall de Windows permita tráfico entrante en el puerto `57120` (UDP).

### 2.3 Librería de Samples
La IA conoce una serie de nombres de samples por defecto (`bd`, `sn`, `hh`, `cp`). Si tus samples están en una ruta personalizada, debes vincularla en SuperDirt:
```supercollider
~dirt.loadSoundFiles("C:/mis-samples/*");
```

### 2.4 El Kit de Instalación Portátil (Plug & Play) [NUEVO v3.0]
Para facilitar el despliegue en máquinas nuevas, el sistema ahora genera un **"Client Kit"** desde el panel de administración.
1.  **Generación Dinámica**: La Raspi empaqueta al vuelo los scripts más recientes y accesos directos.
2.  **Scripts Inteligentes**:
    *   `install_windows.ps1` (PowerShell): Detecta si falta Chocolatey, Git o Haskell e instala solo lo necesario. Si detecta una instalación válida, simplemente actualiza el archivo de arranque.
    *   `install_mac.sh` (Bash): Equivalente para macOS usando Homebrew.
3.  **Accesos Directos Web**: El kit incluye archivos `.url` ("TidalAI Dashboard" y "TidalAI Admin") que permiten abrir la interfaz de la Pi desde el PC sin necesidad de configurar DNS manualmente, apuntando a `http://tidal.local:5000`.

---

## 🍓 3. Guía de Configuración en la Raspberry Pi (Logic-Side)

La RPi es una "Caja de Herramientas Creativa" lista para usar (Appliance).

### 3.1 Stack Tecnológico
- **OS**: Raspberry Pi OS Lite (Minimalista, sin GUI).
- **Backend**: Python 3.9+ gestionado por **Gunicorn** para estabilidad en producción.
- **Persistence**: Archivos JSON (`history.json`, `favorites.json`, `presets.json`) para una base de datos ligera.

### 3.2 Servicio Systemd (`tidalai.service`)
El servidor arranca automáticamente al encender la Raspi. Puedes gestionarlo vía:
- `sudo systemctl status tidalai` (Ver estado).
- `sudo systemctl restart tidalai` (Reiniciar si añades nuevos modelos).

### 3.3 El Launcher Local (Windows Bridge)
El archivo `TidalAI-Launcher.bat` en tu PC es tu panel de control remoto. Permite:
- **Deploy**: Sincroniza tu código local con la Raspi vía SCP.
- **Cleanup**: Limpia caches y archivos basura.
- **Extract**: Alimentar a la IA con tus propios archivos `.tidal` para que aprenda tu estilo.

---

## 🧠 4. El Motor de IA: Cadenas de Markov de Orden Variable

A diferencia de modelos pesados de Deep Learning, TidalAI utiliza **Cadenas de Markov** optimizadas para latencia cero.

### 4.1 Entrenamiento (The Corpus)
El sistema lee el archivo `patterns.txt` (localizado en `examples/corpus/`).
1. **Tokenización Semántica**: El código Tidal se rompe en unidades lógicas (`sound`, `*`, `[`, `]`, `every`). Nuestro tokenizador está diseñado específicamente para NO romper la sintaxis musical.
2. **Matriz de Transición**: El sistema construye un mapa probabilístico de "qué viene después de qué".
3. **Persistencia**: Al guardar un "Favorito", la IA añade ese patrón al corpus y se re-entrena instantáneamente.

### 4.2 Temperatura y Estocasticidad
- **T=0.5**: Producción segura. La IA elige siempre la transición más probable.
- **T=1.2**: Producción arriesgada. La IA explora el 20-30% de transiciones menos probables, creando ritmos innovadores.

---

## 🤖 5. El Oráculo: Interpretación Semántica (Phase 10)

El Oráculo (`oracle_engine.py`) es el puente de lenguaje natural.

### 5.1 Mecánica de Interpretación
Cuando escribes *"Hazlo sonar más oscuro y tribal"*:
1. **Detección de Keywords**: Busca términos en su lexicón interno.
2. **Scoring de Intenciones**: `oscuro` -> Offset de filtro bajo. `tribal` -> Estilo 'drums' + Estilo 'techno' (o el asignado a tribal).
3. **Inyección de Tokens**: El Oráculo puede inyectar código Tidal directo (ej: `# lpf 500`) al final del patrón generado por la IA.

### 5.2 El Lexicón (Botón ❕)
Haz clic en el icono de información en el dock para ver la lista completa de palabras que el Oráculo "entiende". Se basa en diccionarios de pesos técnicos.

---

## 🚀 6. Orquestación Polifónica: Poly-Spread (V2.6)

Es la joya técnica del sistema. Convierte un solo patrón en una orquesta multi-pista.

### 6.1 El Algoritmo "Layer Splitter"
El método `get_layers()` en `PatternGenerator.py` fragmenta la música:
1. **Limpieza de Prefijos**: Elimina automáticamente rastros de `d1 $` o similares que la IA pueda haber inyectado por error.
2. **División de Sonidos**: Detecta bloques que empiezan por `sound`, `note`, `drum`, etc.
3. **Hereditario de Efectos**: Si pones `# room 0.8 # lock`, esos efectos se aplican a TODAS las pistas resultantes.
4. **Envío Secuencial**: El servidor dispara una ráfaga OSC: Pista 1 a `d1`, Pista 2 a `d2`, etc.

---

## 🎨 7. Experiencia de Usuario: Companion Studio Web

La interfaz está diseñada para inspirar en entornos de estudio oscuros.

### 7.1 Skin Engine Dinámico
- Siete temas estéticos (Cyberpunk, Midnight, DeepSea, etc.).
- El tema cambia automáticamente según el estilo musical activo (Techno, Ambient, House...).
- Implementado mediante **Inyección de Variables CSS (:root)** en tiempo real.

### 7.2 Partículas y Feedback Visual
- Fondo reactivo programado en **Canvas 2D**.
- Cada mensaje OSC enviado genera una explosión de partículas en la pantalla, dando confirmación física a la acción digital.

### 7.3 Mapa Mental (D3.js Graph)
- Representación topológica de los tokens de la IA.
- Arrastrable y escalable. Permite ver qué sonidos "viven cerca" de cuáles en el cerebro de la máquina.

### 7.4 Skins Adaptativos (Temas Emocionales) [NUEVO v3.0]
La interfaz muta cromáticamente según el género musical para inducir el estado mental adecuado:
- **Techno**: Neon Púrpura/Negro (Cyberpunk clásico).
- **Ambient**: Azul Profundo/Océano (Calma y focus).
- **House**: Fucsia/Dorado cálido (Soulful).
- **Breakbeat**: Gris Industrial/Ámbar (Urbano/Hormigón).
- **Experimental**: Blanco/Negro Alto Contraste (Laboratorio Clínico).
- **Glitch**: Rojo/Negro con efecto CRT (Tensión y error).

---

## 📡 8. Protocolo de Red y Seguridad

### 8.1 Comunicación OSC
- **Target IP**: La IP del PC (Configurable en Herramientas -> Red).
- **Puerto**: `57120` (UDP).
- **Payload**: `/tidal/pattern [canal, codigo]`.

### 8.2 Seguridad Local (SSH Keys)
Para evitar pedir contraseña en cada deploy o backup, usamos **RSA Keys**. Ejecuta `setup-ssh.bat` una sola vez para establecer la confianza entre Windows y la Raspberry Pi.

---

## 💿 9. Gestión de Datos y Backups

### 9.1 Sistema de Favoritos e Historial
- Se guardan los últimos 100 patrones automáticamente.
- Puedes marcar como **Favorito** para que la IA aprenda de ese patrón permanentemente.

### 9.2 Backup de Emergencia
Disponible en la pestaña Herramientas. Genera un ZIP que contiene:
- `history.json` (Tu viaje creativo).
- `favorites.json` (Tus mejores ideas).
- `markov_model.json` (El cerebro entrenado).

---

## 🔭 10. Hoja de Ruta Sugerida (Futuro del Studio)

1.  **Analizador de Audio Closed-Loop**: La IA "escucha" el audio final del PC para ajustar el volumen de sus capas automáticamente.
2.  **Generador de Estructura (Arreglista)**: Controlar la progresión de una canción de 5 minutos, no solo patrones sueltos.
3.  **Visuales Hydra**: Integración directa con Live Coding visual en el mismo navegador.

## 🧱 11. Estructura Macro-Temporal: The Structure Engine (Phase 16)
Este motor convierte la generación de loops en composición de canciones completas. No funciona a nivel de nota, sino a nivel de **Sección** (Intro, Verse, Build, Drop, Outro).

### 11.1 Lógica de Templating
Entiende diferentes arquetipos narrativos:
- **Standard**: Estructura de club de 5 minutos.
- **Extended**: Viaje progresivo con múltiples builds.
- **Quick Drop**: Estructura agresiva para demos rápidas.
- **Ambient Flow**: Progresión lineal sin clímax percusivo.

### 11.2 Modulación Dual (Bias)
Cuando el **Conductor** está activo, el sistema de generación entra en modo "Híbrido":
- **80% Autoridad**: El Conductor dicta el rango de Densidad y Complejidad objetivo.
- **20% Influencia**: Los sliders del usuario actúan como un sesgo (+/-) sobre ese objetivo, permitiendo "dirigir" sutilmente sin romper la estructura.

## 12. Honestidad Orquestal y Saneamiento (Phase 15)
...
## 12. Motor de Mutación Evolutiva (Phase 17)

En la versión 3.0, el sistema permite la **Evolución Orgánica** de los ritmos:
- **Botón 🧬 Mutar**: Toma el patrón actual y genera una variación ("hijo").
- **DNA Rítmico**: La mutación puede ser sutil (cambio de velocidad, filtros) o radical (rotación rítmica, cambio de samples similares), dependiendo del slider de Complejidad.

---

## 📂 13. Explorador Inteligente: AI Sample Scout (Phase 18)

Presentado en la V3.0, este módulo resuelve el problema de la parálisis de elección rítmica.

### 13.1 Indexación Taxonómica
El sistema no solo conoce los nombres, sino el **rol musical** de cada carpeta de samples:
- **Heurística de Nombres**: `bd`, `kick`, `stomp` -> Categoría **Kick**.
- **Synths (Super*)**: Identificación automática de sintetizadores de SuperCollider como `superpiano`, `superhex`, etc.

### 13.2 Panel de Sugerencias Contextuales
Al generar un patrón, el Studio escanea la librería extendida (`samples_v2.json`) y propone 6 sonidos alternativos que pertenezcan a la misma categoría que el sonido principal.
- **Acción One-Click**: Al pulsar una etiqueta, se ejecuta un reemplazo mediante **Regex** que mantiene intacta la estructura del patrón rítmico.

### 13.3 Síntesis Expandida
El generador ahora es **Híbrido**. Si seleccionas un synth de la familia `super*`, el sistema automáticamente conmuta de "Sample Mode" (índices 0-12) a "Synth Mode" (frecuencias MIDI), permitiendo melodías armónicamente precisas con texturas de síntesis FM, subtractiva o aditiva de SuperCollider.

---

## 14. The Intelligent Theorist: Validación Musical Automática (Phase 17)

Introducido en v4.3, el `TheoryEngine` valida patrones contra reglas musicales.

### 14.1 Arquitectura del Theorist
```python
class TheoryEngine:
    def __init__(self):
        self.rules = self._load_rules('theory_rules.json')
    
    def validate(self, pattern, genre):
        # Aplica reglas específicas del género
        for rule in self.rules[genre]:
            if not rule.check(pattern):
                return False, rule.message
        return True, None
```

### 14.2 Bucle de Validación con Reintentos
En `app.py`, el endpoint `/api/generate` implementa un **retry loop**:
1. Genera patrón con IA.
2. Valida contra `TheoryEngine`.
3. Si falla, reintenta hasta 3 veces con `temperature += 0.1`.
4. Retorna `validation_info` en JSON.

### 14.3 Tipos de Reglas
- **Hardcoded**: Funciones Python (e.g., `_rule_kick_on_one`).
- **Regex**: Expresiones regulares definidas en JSON (e.g., `"bd.*~"` para detectar bombos sincopados).

### 14.4 Rules Editor UI (Phase 17b)
Interfaz web para gestión dinámica:
- **API Endpoints**:
  - `GET /api/theory/rules`: Retorna configuración completa.
  - `POST /api/theory/toggle`: Activa/desactiva regla.
  - `POST /api/theory/add`: Añade regla custom.
- **Persistencia**: `theory_rules.json` se actualiza en tiempo real.

---

## 15. Latent Space Navigation: Interpolación Vectorial de Géneros (Phase 18)

Introducido en v4.4, permite mezclar géneros matemáticamente.

### 15.1 Arquitectura del Latent Engine
```python
class LatentEngine:
    def __init__(self):
        self.genre_vectors = {
            "techno": {"density": 0.8, "complexity": 0.6, "tempo": 140},
            "ambient": {"density": 0.3, "complexity": 0.4, "tempo": 90}
        }
    
    def blend_multiple(self, blend_config):
        # blend_config = {"techno": 0.7, "ambient": 0.3}
        result = {}
        for genre, weight in blend_config.items():
            vec = self.genre_vectors[genre]
            for param, value in vec.items():
                result[param] = result.get(param, 0) + (value * weight)
        return result
```

### 15.2 Integración con el Generador
En `app.py`, el endpoint `/api/generate` acepta un parámetro `blend`:
```python
if blend:
    latent_params = state.latent.blend_multiple(blend)
    density = latent_params["density_base"]
    complexity = latent_params["complexity_base"]
    tempo = latent_params["tempo_preference"]
```

### 15.3 Single Source of Truth
Los géneros disponibles se leen desde `theory_rules.json`, manteniendo consistencia entre `TheoryEngine` y `LatentEngine`.

### 15.4 Validación Ponderada
En modo blend, las reglas del Theorist se aplican según el peso:
- **Género dominante (>50%)**: Reglas obligatorias.
- **Género secundario (<50%)**: Reglas opcionales (advertencias).

---

## 💎 16. Luxury v5: Estética Inmersiva y Reactividad WebGL (Phase 19-25)

La versión 5.0 representa el salto a una interfaz de "Luxury Audio Software".

### 16.1 Hydra Visuals Engine
Integración profunda de **Hydra-Synth** (WebGL) directamente en el fondo del editor:
- **Reactividad**: Los visuales no son aleatorios; responden a la **Densidad** y **Complejidad** del patrón generado.
- **Cambio de Estilo**: Cada género musical activa un algoritmo visual dedicado (e.g., neones de glitch para Techno, ondas fluidas para Ambient).

### 16.2 Glass Segmented Control
Rediseño del selector de modo:
- **Solo**: Generación de un único canal (`d1`).
- **Macro**: Generación de ensambles polifónicos completos.
- **UI**: Uso de glassmorphism y sliders animados para una experiencia táctil premium.

---

## 🌊 17. Macro-Wave Orquestación (Phase 26)

El motor Macro-Wave permite generar una composición completa de forma instantánea.
1. **Análisis de Capas**: La IA genera simultáneamente bombos, bajos, melodías y percusiones.
2. **Distribución Inteligente**: El sistema asigna automáticamente cada parte a un canal OSC (`d1` a `d8`).
3. **Coherencia Estilística**: Garantiza que todos los instrumentos compartan el mismo ADN rítmico.

---

## 🔁 18. Modo "Auto-Cycle" (Cycle Send) (Phase 29)

Inspirado en el envío nativo de TidalCycles, este modo automatiza la pulsación musical.
- **Re-evaluación en Tiempo Real**: El patrón se re-envía al PC en cada ciclo (sincronizado con el BPM).
- **Sincronización Dinámica**: Si cambias el tempo en el Studio, el ciclo se ajusta automáticamente para mantener el groove perfecto.
- **Visualización**: El botón de envío pulsa rítmicamente para indicar que el sistema está "vivo".

---
**Manual de Integración Total - TidalAI Companion Studio**
*Documentación Oficial V5.1 - Enero 2026*
