# TidalAI Companion - Documentación Completa

## 📚 Índice de Documentación

### 🚀 Guías de Inicio

- **[QUICKSTART.md](QUICKSTART.md)** - Configuración inicial rápida
- **[AUTO_START.md](docs/AUTO_START.md)** - Configurar inicio automático
- **[DEPLOY_AUTO.md](docs/DEPLOY_AUTO.md)** - Deploy automático desde Windows

### 📖 Manuales de Uso

- **[GUIA_USO.md](docs/GUIA_USO.md)** - Manual completo de la interfaz web
- **[MODELO_MARKOV.md](docs/MODELO_MARKOV.md)** - Documentación técnica del modelo IA
- **[EXTRACTOR_PATRONES.md](docs/EXTRACTOR_PATRONES.md)** - Extractor de patrones de tu proyecto
- **[BRIDGE_AUTOMATICO.md](docs/BRIDGE_AUTOMATICO.md)** - Integración con TidalCycles

### 🔧 Configuración

- **[CONFIGURACION_RASPI.md](docs/CONFIGURACION_RASPI.md)** - Configuración detallada Raspberry Pi
- **[BITACORA.md](docs/BITACORA.md)** - Registro de cambios y desarrollo

---

## ✨ Características Principales

### 🎵 Generación de Patrones Avanzada

**Dos Modos de Generación**:
- **Basado en Reglas**: Rápido y predecible
- **Inteligencia Artificial**: Creativo usando Markov Chains de orden 2

**Parametrización Total**:
- 5 tipos: Drums, Bass, Melody, Percussion, FX
- 5 estilos: Techno, Ambient, Breakbeat, House, Experimental
- Control de densidad, complejidad y tempo
- Temperatura de IA ajustable (0.1 - 2.0)

### 🚀 Herramientas Avanzadas (Fase 1-3)

Hemos implementado un conjunto completo de herramientas profesionales:

#### 1. Gestión de Patrones
- **Sistema de Presets** 💾: Guarda tus configuraciones favoritas. 5 presets incluidos.
- **Historial Completo** 📜: Guarda últimos 100 patrones, búsqueda en tiempo real.
- **Editor Inline** ✏️: Edita patrones generados directamente en la web.
- **Favoritos Inteligentes** ⭐: Categorización automática de tus preferidos.

#### 2. Creatividad y Producción
- **Generación por Lotes** 🎲: Genera 1-50 patrones simultáneamente para explorar ideas.
- **Morfador de Riffs** 🎛️: Interpolación estocástica entre dos patrones (híbridos musicales).
- **Templates de Canciones** 🎼: Genera estructuras completas para Techno, House, Ambient y Breakbeat.
- **Modo Jam Session** 🎵: El sistema "improvisa" y genera patrones continuamente.

#### 3. Análisis, Estética e Inteligencia (v5.1) 💎
- **Luxury Skin Engine** 🎨: Interfaz premium de cristal con 10 temas adaptativos.
- **Hydra Visuals Engine** ✨: Generación Visual WebGL reactiva al código Tidal en tiempo real.
- **Theory Engine** 📐: Validación musical automática para asegurar coherencia por género.
- **Latent Space Blender** 🌀: Mezcla géneros musicalmente con interpolación de parámetros.
- **Macro-Wave Orquestación** 🌊: Generación de ensambles completos multi-canal (d1-d8).
- **Auto-Cycle (Live)** 🔁: Re-envío automático sincronizado con BPM para live performance.
- **Análisis de Corpus** 📊: Visualiza estadísticas y mapas mentales (D3.js) de la IA.
- **Visualizador Centralizado** 📊: Timeline gráfica unificada para patterns y macros.
- **Backup Integral** 💾: Crea/restaura copias de seguridad de todo el sistema.

### 🌌 Control de Próxima Generación (Phase 10 & 11)

#### 🤖 El Oráculo (Natural Language Control)
Controla la IA mediante lenguaje natural. Escribe *"hazlo más denso y agresivo"* o *"que suene espacial y tribal"* y el sistema ajustará sliders, estilos y efectos automáticamente.

#### 🚀 Orquestación Polifónica (Poly-Spread)
El sistema detecta colisiones de sonido y las fragmenta automáticamente en canales contiguos (`d1`, `d2`, etc.), permitiendo composiciones multi-pista transparentes.

### 🤖 Modelo de IA

- **Markov Chains de Orden 2** (trigramas)
- **Corpus de 120+ patrones** con samples reales
- **Entrenamiento personalizable** con tus favoritos
- **Clasificación automática** de tipos
- **Validación automática** de sintaxis

### 🔍 Extractor de Patrones

- **Escaneo recursivo** de archivos .tidal
- **Clasificación automática** (96% precisión)
- **Modo interactivo** para correcciones manuales

---

## 🎯 Quick Start

### 1. Configuración Inicial (Windows)

```cmd
cd C:\Users\alfredo\.gemini\antigravity\scratch\tidalai-companion

# Configurar SSH sin contraseña
setup-ssh.bat
# Escribe "raspi" cuando pida contraseña
```

### 2. Deploy a Raspberry Pi

```cmd
deploy.bat
```

- Transfiere archivos automáticamente
- Reinicia servicio
- Verificación de estado

### 3. Usar la Interfaz Web

1. Abre `http://192.168.1.147:5000`
2. ¡Explora las nuevas pestañas y modales!

---

## 📁 Estructura del Proyecto

```
tidalai-companion/
├── raspberry-pi/
│   ├── generator/
│   │   ├── pattern_generator.py    # Generador principal (con Layer Splitter)
│   │   ├── markov_model.py         # Modelo de IA
│   │   ├── oracle_engine.py        # Motor de interpretación semántica
│   │   ├── theory_engine.py        # Validación musical por reglas
│   │   ├── latent_engine.py        # Navegación en espacio latente
│   │   └── structure_engine.py     # Director de orquesta (Conductor)
│   ├── web/
│   │   ├── app.py                  # API REST (Flask)
│   │   ├── templates/index.html    # Frontend único
│   │   └── static/
│   │       ├── js/                 # Nueva estructura modular
│   │       │   ├── core/           # Gestión de estado y suscripciones
│   │       │   ├── ui/             # Managers de la interfaz Luxury
│   │       │   └── modules/        # Red, Hydra, Conductor, etc.
│   │       └── v5-luxury.css       # Estilos premium optimizados
│   ├── presets.json                # Persistencia de presets
│   ├── history.json                # Historial persistente
│   └── song_templates.json         # Plantillas de canciones
├── pc-side/
│   └── osc_receiver.scd            # Receptor SuperCollider
├── examples/corpus/
│   └── patterns.txt                # Corpus base
└── docs/                           # Documentación técnica
```

---

## 🎯 Workflows Sugeridos

### Exploración Creativa
1. Cargar preset "Techno Agresivo"
2. Usar **Generación por Lotes** (20 patrones)
3. Seleccionar los mejores y **Añadir a Favoritos**
4. Usar **Comparador** para refinar variaciones

### Live Performance
1. Abrir **Jam Session**
2. Configurar canales d1, d2, d3
3. Duración: 15 min, Intervalo: 32s
4. Iniciar y tocar encima con tu guitarra/sinte

### Producción de Tracks
1. Abrir **Templates de Canciones**
2. Elegir "House Track"
3. Generar canción completa
4. Descargar `.tidal`
5. Importar en tu editor y finalizar

---

## 🔧 API REST

El sistema expone una API completa:

```
GET/POST /api/generate      # Generar patrón único
POST     /api/generate-batch # Generar múltiples
GET/POST /api/presets       # Gestión de presets
GET/POST /api/history       # Gestión de historial
GET      /api/corpus-stats  # Estadísticas
POST     /api/jam-session   # Control de jam
GET/POST /api/backup        # Backup y restore
POST     /api/export-tidal  # Exportar archivos
POST     /api/generate-song # Generar desde template
```

---

## 🛠️ Comandos Útiles

```cmd
# Deploy automático
deploy.bat

# Extractor interactivo
extract-patterns-interactive.bat

# Admin panel (si disponible)
admin.bat
```

---

## 📄 Licencia

Este proyecto es de código abierto. Ver LICENSE para detalles.

---

**¡Disfruta creando música con TidalAI Companion! 🎵🍓**
