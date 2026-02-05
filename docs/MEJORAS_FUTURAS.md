# 🚀 Hoja de Ruta: Futuro de TidalAI Companion

Este documento enumera ideas y conceptos para expandir las capacidades de la IA en futuras versiones del Companion Studio.

## ✅ Logros Recientes (Fase 1-11)
- [x] **El Oráculo**: Control semántico por lenguaje natural.
- [x] **Orquestación Polifónica**: Reparto automático de capas en canales Tidal.
- [x] **Riff Morphing**: Interpolación estocástica entre patrones.
- [x] **Adaptive Skin Engine**: 7 temas estéticos inmersivos.
- [x] **Partículas Bio-Reactivas**: Visualización dinámica Canvas 2D.
- [x] **Mapa Mental D3**: Visualización del cerebro Markov.
- [x] **Motor de Mutación Evolutiva**: Generación de variaciones orgánicas (Phase 17).
- [x] **AI Sample Scout**: Exploración inteligente y contextual de librerías (Phase 18).
- [x] **Síntesis Expandida**: Integración total de synths de SuperDirt.

## 1. Próximos Pasos (Fase 12+)

- [x] **El Arreglista Automático**: The Song Conductor (Phase 16).

### 🎙️ Analizador de Timbre Inyectado (Closed-Loop)
Análisis por FFT del sonido real para que la IA "escuche" el resultado.
- **Concepto**: Si el sonido resultante es demasiado brillante o saturado, la IA corrige el filtro (`# lpf`) o la ganancia automáticamente.

### 🤝 Multi-User Collaborative Jam (P2P)
Soporte para que varios músicos controlen diferentes canales (`d1`, `d2`) simultáneamente vía WebSockets.
- **Concepto**: Un "muro de sonido" colaborativo donde cada usuario es un instrumento.

## 2. Visión a Largo Plazo (The Outer Rim) 🌌

### 🧠 Transferencia de Estilo Neural (Audio-to-Tidal)
- **Idea**: Subes un loop de 16 segundos y la IA extrae su "huella rítmica" y "swing" para crear un nuevo corpus de Markov instantáneo.

### 🎮 Visualización Inmersiva 3D (Three.js/WebGL)
- **Idea**: Reemplazar el fondo de partículas 2D por un universo 3D generativo que muta geométricamente con cada "disparo" de la IA.

### 📡 Haptic Feedback Studio (Hardware GPIO)
- **Idea**: Conectar motores vibradores a la Raspberry Pi para sentir físicamente en tu cuerpo el pulso del Oráculo y el ritmo de los bajos.

### 🎥 Generador de Vídeo Sincronizado (Hydra Integration)
- **Idea**: El servidor enviará metadatos rítmicos no solo a TidalCycles, sino a motores de visuales en tiempo real para una experiencia audiovisual total.

## 2. Cerebro 2.0: Deep Generative Architecture (El Próximo Salto) 🧠

Aquí es donde la "magia" puede escalar de estadística básica a inteligencia real.

### 🏋️ Reinforcement Learning (RL) from User Feedback
Hacer que el botón de "Favorito" signifique algo matemáticamente.
- **Concepto**: Cada vez que guardas un patrón, el sistema ajusta los pesos de la Cadena de Markov.
- **Mecánica**: `Reward = +1` para transiciones usadas en favoritos. `Penalización` para patrones generados que el usuario descarta rápidamente (menos de 5s de reproducción).
- **Resultado**: El sistema aprende *tu* gusto específico con el tiempo.

### 🔮 Micro-Transformers (Small LLMs)
Reemplazar Markov con Atenció.
- **Concepto**: Entrenar un modelo Transformer muy pequeño (tipo NanoGPT) específicamente con código TidalCycles.
- **Ventaja**: Entiende contexto a largo plazo (e.g., "si abrí un paréntesis en el compás 1, debo cerrarlo en el 4 de forma lógica").
- **Reto**: Correrlo en Raspberry Pi con latencia baja (Cuantización a int8).

### 👹 Multi-Agent Debate (GAN-like)
Dos cerebros son mejor que uno.
- **Agente "Caos"**: Propone patrones muy locos y rotos.
- **Agente "Orden"**: Intenta corregirlos para que cumplan teoría musical básica.
- **El Juez**: Tú decides el balance con un slider "Temperature".

### 🧬 Algoritmos Genéticos Melódicos
Evolución Darwiniana para notas.
- **Concepto**: Generar 10 melodías, matar las 5 peores, cruzar las 5 mejores y mutar los hijos.
- **Uso**: Ideal para encontrar líneas de bajo o riffs de sinte que no se te hubieran ocurrido.

### 📐 Constraint Logic Programming (CLP) - The Theorist ✅ **COMPLETADO**
Normas estrictas sobre la probabilidad.
- **Concepto**: Usar un motor de lógica (tipo Prolog) para imponer reglas teóricas duras.
- **Ejemplo**: "Nunca pongas un Kick en el tiempo débil si el género es Dubstep". "La nota del bajo debe ser la fundamental o la quinta del acorde actual".
- **Implementación (v4.3)**: `TheoryEngine` con validación automática y reintentos.
- **Rules Editor (v4.3.1)**: Gestión dinámica de reglas desde la UI.

### 🌀 Latent Space Navigation (Interpolación Vectorial) ✅ **COMPLETADO**
Deslizarse entre géneros.
- **Concepto**: Mapear todos los patrones conocidos a un espacio vectorial 2D.
- **Mecánica**: Un slider que te permite estar "30% Rock, 70% House". La IA genera el código híbrido que existe matemáticamente entre esos dos puntos.
- **Implementación (v4.4)**: `LatentEngine` con interpolación lineal de parámetros.

### 🌍 World-Data Sonification (OSINT Music)
El cerebro conectado al mundo real.
- **Concepto**: La IA modifica los parámetros basándose en APIs externas en tiempo real.
- **Ejemplo**: Si el precio del Bitcoin cae, sube la Distorsión. Si llueve en tu ciudad (API clima), baja el Tempo y activa el filtro Low-Pass.

### 🐝 Hive Mind (Federated Learning)
Inteligencia Colectiva.
- **Concepto**: Si activas la opción, tu RPi envía (anónimamente) los pesos de tus patrones favoritos a un servidor central.
- **Resultado**: Tu IA se vuelve más lista aprendiendo de lo que le gusta a otros usuarios de TidalAI en el mundo.

## 3. Nuevos Conceptos Exploratorios (Fase 17+)

### 🤝 Party Mode (Jam Colaborativa Local)
Convertir la Raspberry Pi en un hub multijugador.
- **Concepto**: "Tú llevas el bajo, yo los drums". Diferentes usuarios se conectan desde sus móviles a la misma IP y controlan canales asignados (`d1`, `d2`) en tiempo real.
- **Tech**: WebSockets con gestión de roles y latencia.

### 🎙️ The Voice Commander (Vocal UI)
Evolución natural del Oráculo.
- **Concepto**: Dar órdenes verbales ("Sube la intensidad", "Muta el bombo", "Dame algo más Techno") usando la API de reconocimiento de voz del navegador.
- **Vibe**: Capitán de nave espacial.

### 🎹 Bridge Hardware (MIDI Out)
Romper la barrera digital.
- **Concepto**: Mapear canales de Tidal (`d1`) a salidas MIDI físicas de la Pi para controlar sintetizadores externos (Volca, Minilogue, Modulares).
- **Tech**: SuperCollider MIDIOut + Adaptador USB-MIDI.

### ❤️ Biometric Tempo (Biofeedback)
Música que respira contigo.
- **Concepto**: Conectar un sensor de pulso Bluetooth (o Apple Watch) y que el BPM del sistema se sincronice con tu ritmo cardíaco. Si te relajas, la música frena.

### 📻 Infinite Radio (Auto-Stream)
Dando vida propia al bot.
- **Concepto**: Un modo "Desatendido" donde la IA genera música 24/7 y la transmite automáticamente a un servidor Icecast/Shoutcast, creando una radio online infinita.

### 🎴 Physical Tokens (RFID/NFC)
Interacción tangible.
- **Concepto**: Pegar etiquetas NFC en objetos físicos. Al acercar una carta "Techno" a la Raspberry Pi, el sistema carga ese preset o estructura.

---
*TidalAI Future Lab - 2026*
