# Extractor de Patrones - Modo Interactivo y Remoto

## 🎯 Nuevas Funcionalidades

### 1. Modo Interactivo

El script ahora puede hacer preguntas para mejorar la clasificación:

```bash
python tools/extract-patterns.py "C:\Users\alfredo\Desktop\tidal" \
    --interactive \
    --output extracted.txt
```

**Qué hace**:
- Muestra cada patrón clasificado como "unknown"
- Pregunta si la clasificación es correcta
- Permite corregir manualmente el tipo
- Aprende de tus correcciones

**Ejemplo de interacción**:
```
Patrón: slow 16 $ n "60 64 67 72" # s "supersaw"...
Clasificación automática: melody
¿Es correcta? (s/n/tipo): s

Patrón: s "noise" # gain 0.2...
Clasificación automática: unknown
¿Es correcta? (s/n/tipo): fx
```

### 2. Opciones Automáticas

```bash
# Añadir automáticamente al corpus
python tools/extract-patterns.py DIR --add-to-corpus

# Preguntar si re-entrenar después
python tools/extract-patterns.py DIR --auto-train

# Combinar todo
python tools/extract-patterns.py "C:\Users\alfredo\Desktop\tidal" \
    --interactive \
    --add-to-corpus \
    --auto-train
```

### 3. Ejecución Remota desde Raspberry Pi

**Configurar una vez**:

```bash
# En Raspberry Pi
cd ~/tidalai-companion/raspberry-pi
chmod +x extract-from-pc.sh

# Editar configuración
nano extract-from-pc.sh
# Cambiar:
# PC_IP="192.168.1.50"  # IP de tu PC
# PC_USER="alfredo"     # Tu usuario de Windows
```

**Ejecutar**:

```bash
# Desde Raspberry Pi
./extract-from-pc.sh
```

**Qué hace**:
1. ✅ Verifica conexión con tu PC
2. ✅ Copia archivos .tidal del PC a Raspberry Pi (vía SSH)
3. ✅ Extrae patrones localmente
4. ✅ Pregunta si añadir al corpus
5. ✅ Pregunta si re-entrenar modelo
6. ✅ Limpia archivos temporales

---

## 📋 Todas las Opciones

```bash
python tools/extract-patterns.py <directorio> [opciones]

Opciones:
  -o, --output FILE         Archivo de salida
  -f, --format FORMAT       corpus o favorites
  -i, --interactive         Modo interactivo (revisar unknown)
  -a, --add-to-corpus       Añadir automáticamente al corpus
  -t, --auto-train          Preguntar si re-entrenar después
```

---

## 🎯 Workflows Recomendados

### Workflow 1: Extracción Rápida (PC)

```cmd
cd C:\Users\alfredo\.gemini\antigravity\scratch\tidalai-companion
python tools\extract-patterns.py "C:\Users\alfredo\Desktop\tidal" -o extracted.txt
```

### Workflow 2: Extracción Interactiva (PC)

```cmd
python tools\extract-patterns.py "C:\Users\alfredo\Desktop\tidal" \
    --interactive \
    --add-to-corpus \
    --auto-train
```

Esto:
- Te pregunta por cada patrón "unknown"
- Te pregunta si añadir al corpus
- Te pregunta si re-entrenar

### Workflow 3: Extracción Remota (Raspberry Pi)

```bash
# Desde Raspberry Pi
cd ~/tidalai-companion/raspberry-pi
./extract-from-pc.sh
```

Esto:
- Accede a tu PC vía SSH
- Copia archivos .tidal
- Extrae patrones
- Pregunta qué hacer

---

## 🔧 Configuración SSH (Una Vez)

### En tu PC (Windows):

**1. Instalar OpenSSH Server**:
```powershell
# Como Administrador
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

**2. Permitir en Firewall**:
```powershell
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

**3. Configurar clave SSH desde Raspberry Pi**:
```bash
# En Raspberry Pi
ssh-copy-id alfredo@192.168.1.50
# Escribe tu contraseña de Windows
```

Ahora la Raspberry Pi puede acceder a tu PC sin contraseña.

---

## 💡 Ventajas del Modo Remoto

### ¿Por qué ejecutar desde Raspberry Pi?

1. **Automatización**: Puede ejecutarse periódicamente (cron)
2. **Integración**: Directamente añade al corpus y re-entrena
3. **Centralizado**: Todo el procesamiento en un solo lugar
4. **Siempre disponible**: La Raspberry Pi está siempre encendida

### Ejemplo de Automatización:

```bash
# En Raspberry Pi, añadir a crontab
crontab -e

# Ejecutar cada noche a las 2 AM
0 2 * * * /home/pi/tidalai-companion/raspberry-pi/extract-from-pc.sh >> /tmp/extract.log 2>&1
```

---

## 🐛 Troubleshooting

### Error: "No se puede conectar a PC"

**Solución**: Verifica IP y que OpenSSH Server esté activo en Windows

```powershell
# En PC
Get-Service sshd
```

### Error: "Permission denied"

**Solución**: Configura clave SSH (ver arriba)

### Error: "No se pudieron copiar archivos"

**Solución**: Verifica la ruta del directorio en `extract-from-pc.sh`

```bash
# Formato Windows en Git Bash
PC_TIDAL_DIR="/c/Users/alfredo/Desktop/tidal"

# O formato PowerShell
PC_TIDAL_DIR="C:/Users/alfredo/Desktop/tidal"
```

---

## 📊 Ejemplo Completo

```bash
# Desde Raspberry Pi
./extract-from-pc.sh

# Output:
=== Extractor Remoto de Patrones ===

[1/5] Verificando conexión con PC...
[OK] PC accesible

[2/5] Creando directorio temporal...
[OK] Directorio creado

[3/5] Copiando archivos .tidal desde PC...
Esto puede tardar un momento...
[OK] Archivos copiados

[4/5] Extrayendo patrones...
Encontrados 21 archivos .tidal
Procesando: oceano_profundo.tidal
...
Encontrados 230 patrones

Por tipo:
  bass: 97
  drums: 23
  fx: 30
  melody: 66
  percussion: 5
  unknown: 9

[OK] Guardado en examples/corpus/extracted_from_pc.txt

[5/5] Limpiando archivos temporales...
[OK] Limpieza completada

¿Añadir estos patrones al corpus base? (s/n)
s
[OK] Patrones añadidos al corpus

¿Re-entrenar el modelo ahora? (s/n)
s
[INFO] Re-entrenando modelo...
[OK] Modelo re-entrenado

=========================================
 Extracción completada
=========================================
```

---

**¡Ahora puedes extraer patrones de forma interactiva y remota! 🎵🤖**
