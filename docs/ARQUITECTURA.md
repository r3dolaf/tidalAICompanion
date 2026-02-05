# Arquitectura Técnica: TidalAI Companion

## Visión General

TidalAI Companion es un sistema distribuido que combina generación de música con IA en una Raspberry Pi 3B+ y ejecución de audio en un PC con TidalCycles, comunicándose en tiempo real vía OSC.

---

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         PC PRINCIPAL                             │
│                                                                  │
│  ┌──────────────────┐                  ┌──────────────────┐    │
│  │   Navegador      │                  │   TidalCycles    │    │
│  │   Web            │                  │   (Haskell)      │    │
│  │                  │                  │                  │    │
│  │  - Interfaz UI   │                  │  - Live coding   │    │
│  │  - Controles     │                  │  - Evaluación    │    │
│  │  - Visualización │                  │    de patrones   │    │
│  └────────┬─────────┘                  └────────┬─────────┘    │
│           │                                      │              │
│           │ HTTP                                 │ OSC          │
│           │ (192.168.x.x:5000)                  │ (interno)    │
│           │                                      │              │
│           │                              ┌───────▼─────────┐    │
│           │                              │  SuperCollider  │    │
│           │                              │                 │    │
│           │                              │  - OSC Server   │    │
│           │                              │  - Synth Engine │    │
│           │                              │  - Audio Output │    │
│           │                              └───────▲─────────┘    │
│           │                                      │              │
└───────────┼──────────────────────────────────────┼──────────────┘
            │                                      │
            │          Red Local (WiFi/Ethernet)   │
            │                                      │
            │                                      │ OSC
            │                                      │ (UDP 6010)
            │                                      │
┌───────────▼──────────────────────────────────────┼──────────────┐
│           │                                      │              │
│  ┌────────▼─────────┐                  ┌────────▼─────────┐    │
│  │   Flask Web      │                  │   OSC Client     │    │
│  │   Server         │                  │                  │    │
│  │                  │                  │  - Envío msgs    │    │
│  │  - API REST      │◄─────────────────┤  - Gestión       │    │
│  │  - WebSockets    │                  │    conexión      │    │
│  │  - Static files  │                  └──────────────────┘    │
│  └────────┬─────────┘                           ▲              │
│           │                                     │              │
│           │                                     │              │
│           │                          ┌──────────┴─────────┐    │
│           │                          │  Pattern Generator │    │
│           │                          │                    │    │
│           └─────────────────────────►│  - Generación      │    │
│                                      │  - Validación      │    │
│                                      │  - Formateo        │    │
│                                      └──────────┬─────────┘    │
│                                                 │              │
│                                                 │              │
│                                      ┌──────────▼─────────┐    │
│                                      │   AI Model         │    │
│                                      │                    │    │
│                                      │  - Markov Chains   │    │
│                                      │  - RNN/LSTM (opt)  │    │
│                                      │  - TF Lite (opt)   │    │
│                                      └────────────────────┘    │
│                                                                 │
│                      RASPBERRY PI 3B+                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Componentes del Sistema

### 1. Raspberry Pi - Backend

#### 1.1 Pattern Generator (`pattern_generator.py`)

**Responsabilidades**:
- Generar patrones TidalCycles sintácticamente válidos
- Aplicar parámetros de densidad, complejidad, tempo
- Validar sintaxis antes de enviar
- Mantener estado de generación

**Interfaz**:
```python
class PatternGenerator:
    def __init__(self, model=None):
        """Inicializar con modelo opcional (Markov/RNN)"""
        
    def generate(self, 
                 pattern_type: str,      # 'drums', 'bass', 'melody'
                 density: float,          # 0.0 - 1.0
                 complexity: float,       # 0.0 - 1.0
                 tempo: int) -> str:      # BPM
        """Generar patrón con parámetros"""
        
    def validate(self, pattern: str) -> bool:
        """Validar sintaxis Tidal"""
```

**Modos de generación**:
1. **Hardcoded**: Biblioteca de patrones predefinidos (MVP1)
2. **Markov**: Generación probabilística (MVP3)
3. **Neural**: RNN/LSTM (futuro)

---

#### 1.2 OSC Client (`osc_client.py`)

**Responsabilidades**:
- Enviar mensajes OSC al PC
- Gestionar conexión y reconexión
- Buffering de mensajes si es necesario
- Logging de comunicación

**Interfaz**:
```python
class OSCClient:
    def __init__(self, target_ip: str, target_port: int):
        """Configurar cliente OSC"""
        
    def send_pattern(self, 
                     channel: str,    # 'd1', 'd2', etc.
                     pattern: str):   # Código Tidal
        """Enviar patrón completo"""
        
    def send_param(self,
                   channel: str,
                   param: str,       # 'speed', 'cutoff', etc.
                   value: float):
        """Enviar parámetro individual"""
        
    def stop_channel(self, channel: str):
        """Detener canal específico"""
```

**Protocolo OSC**:
```
/tidal/pattern <channel:string> <pattern:string>
/tidal/param <channel:string> <param:string> <value:float>
/tidal/stop <channel:string>
```

---

#### 1.3 Flask Web Server (`app.py`)

**Responsabilidades**:
- Servir interfaz web
- Exponer API REST para control
- Gestionar estado de la aplicación
- Coordinar generador y cliente OSC

**Endpoints**:
```python
GET  /                      # Interfaz web
POST /api/generate          # Generar patrón
POST /api/send              # Enviar a Tidal
POST /api/config            # Actualizar config
GET  /api/status            # Estado actual
POST /api/mode              # Cambiar modo
```

**Request/Response Examples**:
```json
POST /api/generate
{
  "type": "drums",
  "density": 0.7,
  "complexity": 0.5,
  "tempo": 140
}

Response:
{
  "pattern": "d1 $ sound \"bd*4 sn*2 hh*8\"",
  "timestamp": 1706169195
}
```

---

#### 1.4 AI Model (`markov_model.py`)

**Responsabilidades**:
- Entrenar con corpus de patrones
- Generar nuevos patrones probabilísticamente
- Ajustar creatividad vs coherencia

**Interfaz**:
```python
class MarkovModel:
    def train(self, corpus: List[str]):
        """Entrenar con patrones de ejemplo"""
        
    def generate(self, 
                 seed: str = None,
                 length: int = 20,
                 temperature: float = 1.0) -> str:
        """Generar patrón nuevo"""
        
    def save(self, path: str):
        """Guardar modelo entrenado"""
        
    def load(self, path: str):
        """Cargar modelo"""
```

**Algoritmo**:
1. Tokenizar patrones Tidal (palabras clave, samples, operadores)
2. Construir cadenas de Markov de orden 2-3
3. Generar secuencias respetando sintaxis
4. Validar y corregir si es necesario

---

### 2. PC - Audio Engine

#### 2.1 SuperCollider OSC Receiver (`osc_receiver.scd`)

**Responsabilidades**:
- Escuchar mensajes OSC en puerto 6010
- Parsear y ejecutar patrones Tidal
- Logging de actividad
- Manejo de errores

**Implementación**:
```supercollider
(
// Configurar receptor OSC
OSCdef(\tidalPattern, { |msg, time, addr, recvPort|
    var channel = msg[1].asString;
    var pattern = msg[2].asString;
    
    // Log
    ("Received pattern for " ++ channel ++ ": " ++ pattern).postln;
    
    // Ejecutar en Tidal
    // (requiere integración con TidalCycles)
    
}, '/tidal/pattern');

OSCdef(\tidalParam, { |msg|
    var channel = msg[1].asString;
    var param = msg[2].asString;
    var value = msg[3].asFloat;
    
    ("Setting " ++ param ++ " = " ++ value ++ " on " ++ channel).postln;
    
}, '/tidal/param');

"OSC Receiver ready on port 6010".postln;
)
```

**Integración con TidalCycles**:
- SuperCollider puede ejecutar código Haskell vía `unixCmd` (limitado)
- Alternativa: usar `ghci` como REPL y enviar comandos
- Mejor opción: TidalCycles ya tiene soporte OSC, configurar para escuchar

---

#### 2.2 TidalCycles Configuration

**Archivo**: `BootTidal.hs` (modificado)

Configurar TidalCycles para aceptar patrones vía OSC:

```haskell
-- Añadir receptor OSC personalizado
import Sound.OSC.FD

-- Función para evaluar patrones recibidos
evalRemotePattern :: String -> String -> IO ()
evalRemotePattern channel pattern = do
    putStrLn $ "Evaluating: " ++ channel ++ " $ " ++ pattern
    -- Evaluar en el contexto de Tidal
    -- (requiere acceso al intérprete GHCi)
```

**Nota**: Esta es la parte más compleja de la integración. Alternativas:
1. Usar `tidal-listener` (si existe)
2. Crear bridge en Haskell que escuche OSC
3. Usar archivos temporales que Tidal carga automáticamente

---

### 3. Interfaz Web

#### 3.1 Frontend (`index.html` + `app.js`)

**Componentes UI**:

```
┌─────────────────────────────────────────────┐
│         TidalAI Companion                   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Modo de Operación                   │   │
│  │  ○ Sugerencias  ○ Autónomo  ○ Híbrido│  │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Parámetros                          │   │
│  │                                     │   │
│  │  Densidad:     [▓▓▓▓▓▓░░░░] 60%   │   │
│  │  Complejidad:  [▓▓▓▓░░░░░░] 40%   │   │
│  │  Tempo:        140 BPM              │   │
│  │  Temperatura:  [▓▓▓▓▓░░░░░] 0.5    │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Estilo Musical                      │   │
│  │  [Techno ▼]                         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Instrumentos                        │   │
│  │  ☑ Kick  ☑ Snare  ☑ Hi-hat         │   │
│  │  ☐ Bass  ☐ Synth  ☐ FX             │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Generar Patrón]  [Enviar a Tidal]       │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Patrón Generado                     │   │
│  │                                     │   │
│  │  d1 $ sound "bd*4 sn*2 hh*8"       │   │
│  │    # speed 1.2                      │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ Log de Actividad                    │   │
│  │                                     │   │
│  │  [07:33] Patrón generado            │   │
│  │  [07:33] Enviado a d1               │   │
│  │  [07:34] Modo cambiado a Autónomo   │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Tecnologías**:
- HTML5 + CSS3 (Flexbox/Grid)
- Vanilla JavaScript (sin frameworks pesados)
- Fetch API para comunicación con Flask
- CSS Variables para theming

---

## Flujo de Datos

### Escenario 1: Modo Sugerencias

```
1. Usuario ajusta parámetros en interfaz web
   ↓
2. Click "Generar Patrón"
   ↓
3. Frontend → POST /api/generate → Flask
   ↓
4. Flask → PatternGenerator.generate()
   ↓
5. PatternGenerator → AI Model (si está activo)
   ↓
6. Patrón generado → Flask → Frontend
   ↓
7. Usuario revisa patrón en interfaz
   ↓
8. Usuario click "Enviar a Tidal"
   ↓
9. Frontend → POST /api/send → Flask
   ↓
10. Flask → OSCClient.send_pattern()
    ↓
11. OSC Message → SuperCollider (PC)
    ↓
12. SuperCollider → TidalCycles
    ↓
13. 🎵 Audio output
```

---

### Escenario 2: Modo Autónomo

```
1. Usuario activa modo Autónomo
   ↓
2. Frontend → POST /api/mode {"mode": "autonomous"}
   ↓
3. Flask inicia loop de generación automática
   ↓
4. Cada N compases:
   ├─ PatternGenerator.generate()
   ├─ OSCClient.send_pattern()
   └─ Log → Frontend (WebSocket opcional)
   ↓
5. Usuario ajusta parámetros en tiempo real
   ↓
6. Próxima generación usa nuevos parámetros
   ↓
7. 🎵 Audio continuo con evolución
```

---

## Consideraciones de Rendimiento

### Latencia

**Objetivo**: < 50ms de latencia total

**Breakdown**:
- Generación de patrón: < 10ms (Markov) / < 30ms (RNN)
- Envío OSC: < 5ms (red local)
- Procesamiento SuperCollider: < 10ms
- Buffer de audio: ~10ms

**Optimizaciones**:
- Pre-generar patrones en background
- Usar UDP para OSC (no TCP)
- Minimizar validación en tiempo real
- Cache de patrones frecuentes

---

### Memoria (Raspberry Pi)

**Disponible**: ~700MB (de 1GB total, ~300MB para OS)

**Uso estimado**:
- Python runtime: ~50MB
- Flask: ~30MB
- Modelo Markov: ~10-20MB
- Modelo RNN pequeño: ~50-100MB
- Buffers y cache: ~50MB

**Total**: ~200-250MB → ✅ Viable

---

### CPU (Raspberry Pi)

**Specs**: 4x ARM Cortex-A53 @ 1.4GHz

**Carga estimada**:
- Flask (idle): ~5% CPU
- Generación Markov: ~10-20% CPU (burst)
- Generación RNN: ~30-50% CPU (burst)
- OSC client: ~1% CPU

**Estrategia**: Generación asíncrona para no bloquear servidor web

---

## Seguridad y Configuración

### Red Local

**Configuración recomendada**:
- IP estática para Raspberry Pi
- Firewall: permitir puertos 5000 (Flask) y 6010 (OSC)
- Opcional: VPN si se quiere acceso remoto

**Archivo de configuración** (`config.json`):
```json
{
  "raspberry_pi": {
    "ip": "192.168.1.100",
    "flask_port": 5000
  },
  "pc": {
    "ip": "192.168.1.50",
    "osc_port": 6010
  },
  "generator": {
    "default_tempo": 140,
    "default_density": 0.6,
    "default_complexity": 0.5
  }
}
```

---

## Extensibilidad

### Plugins de Modelos

Arquitectura permite múltiples modelos:

```python
class ModelInterface:
    def generate(self, **params) -> str:
        raise NotImplementedError

class MarkovModel(ModelInterface):
    # Implementación Markov
    
class RNNModel(ModelInterface):
    # Implementación RNN
    
class HybridModel(ModelInterface):
    # Combina múltiples modelos
```

---

### API para Control Externo

Otros programas pueden controlar TidalAI:

```bash
# Generar patrón desde línea de comandos
curl -X POST http://192.168.1.100:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"type":"drums","density":0.8}'

# Cambiar modo
curl -X POST http://192.168.1.100:5000/api/mode \
  -d '{"mode":"autonomous"}'
```

Esto permite integración con:
- MIDI controllers (vía script Python)
- Otros live coding tools
- Sistemas de automatización de shows

---

## Diagrama de Secuencia: Generación y Ejecución

```
Usuario    Frontend    Flask    Generator    OSC    SuperCollider    Tidal
  │           │          │          │         │           │           │
  │  Click    │          │          │         │           │           │
  ├──────────►│          │          │         │           │           │
  │           │  POST    │          │         │           │           │
  │           ├─────────►│          │         │           │           │
  │           │          │ generate()         │           │           │
  │           │          ├─────────►│         │           │           │
  │           │          │          │ AI      │           │           │
  │           │          │          ├────┐    │           │           │
  │           │          │          │◄───┘    │           │           │
  │           │          │◄─────────┤         │           │           │
  │           │◄─────────┤          │         │           │           │
  │  Display  │          │          │         │           │           │
  │◄──────────┤          │          │         │           │           │
  │           │          │          │         │           │           │
  │  Click    │          │          │         │           │           │
  │  "Send"   │          │          │         │           │           │
  ├──────────►│          │          │         │           │           │
  │           │  POST    │          │         │           │           │
  │           ├─────────►│          │         │           │           │
  │           │          │ send_pattern()     │           │           │
  │           │          ├────────────────────►│           │           │
  │           │          │          │         │  OSC msg  │           │
  │           │          │          │         ├──────────►│           │
  │           │          │          │         │           │  eval()   │
  │           │          │          │         │           ├──────────►│
  │           │          │          │         │           │           │
  │           │          │          │         │           │  🎵 Audio │
  │           │          │          │         │           │◄──────────┤
  │           │          │          │         │           │           │
```

---

## Conclusión

Esta arquitectura proporciona:
- ✅ Separación clara de responsabilidades
- ✅ Escalabilidad (añadir más modelos, más RPis)
- ✅ Baja latencia para uso en vivo
- ✅ Flexibilidad (múltiples modos de operación)
- ✅ Extensibilidad (API abierta, plugins)

El diseño modular permite desarrollo incremental y testing independiente de cada componente.
