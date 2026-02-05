# TidalAI Bridge - Guía de Configuración para Ejecución Automática

## 🎯 Objetivo

Hacer que los patrones generados se ejecuten **automáticamente** en TidalCycles sin tener que copiarlos manualmente.

---

## ⚠️ Limitación Técnica

**Problema**: TidalCycles (Haskell) no permite ejecutar código dinámicamente de forma fácil por razones de seguridad. Evaluar strings como código Haskell requiere:
- Biblioteca `hint` (intérprete de Haskell)
- Compilación compleja
- Posibles problemas de seguridad

**Soluciones disponibles**:

---

## 🔧 Solución 1: Bridge con SuperCollider + Clipboard (Recomendada)

Esta es la solución más práctica y funciona bien para live coding.

### Paso 1: Configurar SuperCollider

Ejecuta este código en SuperCollider:

```supercollider
(
// Bridge que copia patrones al portapapeles
OSCdef(\tidalai_bridge, { |msg, time, addr, recvPort|
    var channel = msg[1].asString;
    var pattern = msg[2].asString;
    var fullPattern = channel ++ " $ " ++ pattern;
    
    // Mostrar en post window
    ("TidalAI → " ++ fullPattern).postln;
    
    // Copiar al portapapeles (requiere extensión Clipboard)
    // Si no tienes la extensión, instálala con:
    // Quarks.install("Clipboard");
    fullPattern.copyToClipboard;
    
    "✓ Patrón copiado al portapapeles".postln;
    "  Pega en TidalCycles con Ctrl+V y evalúa con Ctrl+Enter".postln;
    
}, '/tidalai/pattern');

"✓ TidalAI Bridge activo en puerto 6010".postln;
)
```

### Paso 2: Workflow

1. Genera patrón en la interfaz web
2. Click "📤 Enviar a Tidal"
3. El patrón se copia automáticamente al portapapeles
4. En TidalCycles: **Ctrl+V** → **Ctrl+Enter**

**Ventaja**: Solo requiere 2 teclas (pegar y evaluar)

---

## 🔧 Solución 2: Bridge con Archivo + Auto-reload

TidalCycles puede recargar archivos automáticamente.

### Paso 1: Configurar SuperCollider

```supercollider
(
// Bridge que guarda en archivo
OSCdef(\tidalai_file, { |msg, time, addr, recvPort|
    var channel = msg[1].asString;
    var pattern = msg[2].asString;
    var fullPattern = channel ++ " $ " ++ pattern;
    var filepath = Platform.userAppSupportDir +/+ "tidalai_current.tidal";
    
    // Guardar en archivo
    var file = File.open(filepath, "w");
    file.write(fullPattern ++ "\n");
    file.close;
    
    ("TidalAI → " ++ fullPattern).postln;
    ("✓ Guardado en: " ++ filepath).postln;
    
}, '/tidalai/pattern');

"✓ TidalAI Bridge (File) activo".postln;
("Archivo: " ++ (Platform.userAppSupportDir +/+ "tidalai_current.tidal")).postln;
)
```

### Paso 2: En TidalCycles

Crea un archivo `tidalai_loader.tidal` con:

```haskell
-- Cargar patrón desde archivo
-- Ejecuta esto manualmente cuando quieras cargar el último patrón
:script /ruta/a/tidalai_current.tidal
```

**Ventaja**: Patrones se guardan automáticamente  
**Desventaja**: Aún requieres ejecutar `:script` manualmente

---

## 🔧 Solución 3: Bridge Completo con Hint (Avanzado)

Para ejecución **totalmente automática**, necesitas un programa Haskell que use la biblioteca `hint`.

### Requisitos:
- Stack o Cabal
- Biblioteca `hint`
- Biblioteca `hosc` (OSC)
- Biblioteca `tidal`

### Instalación:

```bash
# Crear proyecto
stack new tidalai-bridge
cd tidalai-bridge

# Añadir dependencias a package.yaml:
dependencies:
  - base
  - tidal
  - hosc
  - hint
  - containers

# Compilar
stack build
stack exec tidalai-bridge
```

### Código (tidalai-bridge.hs):

Ver archivo `tidalai-bridge.hs` para el código completo.

**Ventaja**: Ejecución totalmente automática  
**Desventaja**: Complejo de configurar, requiere compilación

---

## 🎯 Recomendación

Para **live coding** (uso normal), recomiendo:

**Solución 1 (Clipboard)** si tienes la extensión Clipboard de SuperCollider:
- Genera patrón
- Click "Enviar"
- Ctrl+V en Tidal
- Ctrl+Enter

**Solución 2 (Archivo)** si prefieres guardar historial:
- Genera patrón
- Click "Enviar"
- `:script tidalai_current.tidal` en Tidal

Para **modo autónomo** (sin intervención), necesitarías la Solución 3, pero es mucho más complejo.

---

## 📝 Configuración Actual Recomendada

1. **Ejecuta en SuperCollider**:
   ```supercollider
   // Abrir: pc-side/tidalai-bridge.scd
   // Evaluar todo (Ctrl+A, Ctrl+Enter)
   ```

2. **Configura IP en Raspberry Pi**:
   ```bash
   nano ~/tidalai-companion/raspberry-pi/config.json
   # Cambiar "pc" → "ip" a tu IP
   sudo systemctl restart tidalai.service
   ```

3. **Workflow**:
   - Interfaz web → Generar patrón
   - Click "📤 Enviar a Tidal"
   - SuperCollider guarda en archivo
   - En Tidal: `:script ruta/al/archivo`

---

## 🚀 Próximos Pasos

Si quieres ejecución **totalmente automática**, puedo:

1. Crear el proyecto Stack completo con hint
2. Configurar compilación
3. Crear script de instalación

Pero ten en cuenta que es **significativamente más complejo** que las soluciones 1 y 2.

¿Qué solución prefieres probar primero?
