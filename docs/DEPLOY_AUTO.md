# TidalAI Companion - Guía de Deploy Automático

## 🚀 Script de Deploy Automático

He creado `deploy.bat` que automatiza completamente el proceso de actualización.

### Requisitos Previos

**Instalar PuTTY** (incluye `pscp` y `plink`):

```powershell
# Opción 1: Con winget
winget install PuTTY.PuTTY

# Opción 2: Descargar manualmente
# https://www.putty.org/
```

### Configuración Inicial (Una sola vez)

1. **Guardar credenciales SSH** para no tener que escribir contraseña:

```powershell
# Ejecutar una vez para guardar la clave del host
plink pi@192.168.1.147 exit
# Escribir "y" cuando pregunte y luego la contraseña
```

2. **Opcional: Configurar clave SSH** (para no escribir contraseña):

```bash
# En tu PC (PowerShell)
ssh-keygen -t rsa -b 4096
# Presiona Enter 3 veces (sin contraseña)

# Copiar clave a Raspberry Pi
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh pi@192.168.1.147 "cat >> ~/.ssh/authorized_keys"
```

### Uso del Script

**Simplemente ejecuta**:

```cmd
deploy.bat
```

El script automáticamente:
1. ✅ Verifica conexión con Raspberry Pi
2. ✅ Transfiere todos los archivos actualizados
3. ✅ Reinicia el servicio
4. ✅ Verifica que el servicio esté activo
5. ✅ Muestra la URL de la interfaz web

### Qué Archivos Transfiere

- `raspberry-pi/web/app.py`
- `raspberry-pi/web/templates/index.html`
- `raspberry-pi/web/static/app.js`
- `raspberry-pi/web/static/style.css`
- `raspberry-pi/generator/markov_model.py` (si existe)
- `raspberry-pi/generator/pattern_generator.py` (si existe)
- `examples/corpus/patterns.txt` (si existe)

### Después del Deploy

1. Abre `http://192.168.1.147:5000`
2. **Presiona Ctrl+Shift+R** para forzar recarga sin caché
3. ¡Listo!

### Solución de Problemas

**Error: "pscp no encontrado"**
- Instala PuTTY con winget o descárgalo manualmente

**Error: "No se puede conectar"**
- Verifica que la Raspberry Pi esté encendida
- Verifica la IP con `ping 192.168.1.147`

**Error: "Permission denied"**
- Verifica usuario y contraseña
- Configura clave SSH (ver arriba)

**El servicio no se reinicia**
- Ejecuta manualmente en la Raspberry Pi:
  ```bash
  sudo systemctl restart tidalai.service
  sudo journalctl -u tidalai.service -n 50
  ```

### Workflow Recomendado

1. **Edita archivos** en tu PC
2. **Ejecuta `deploy.bat`**
3. **Recarga la web** con Ctrl+Shift+R
4. **Repite** cuando hagas cambios

---

## 📝 Scripts Alternativos

Si prefieres usar PowerShell en vez de batch:

```powershell
# Ver: update-raspi.ps1 o update-favorites.ps1
.\update-raspi.ps1
```

Estos scripts usan `scp` nativo de PowerShell (requiere OpenSSH).

---

## 🔧 Personalización

Para cambiar la IP de la Raspberry Pi, edita `deploy.bat`:

```batch
set RASPI_IP=192.168.1.147  <- Cambia esto
set RASPI_USER=pi           <- O el usuario
```
