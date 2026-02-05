# 🚀 Guía Rápida de Configuración

> **Tu Raspberry Pi**: Usuario `pi` | Contraseña `raspi`

---

## 📝 Pasos Rápidos

### 1️⃣ Encontrar la IP de tu Raspberry Pi

**Opción A - Desde la Raspberry Pi (con monitor/teclado):**
```bash
# Iniciar sesión con: pi / raspi
hostname -I
# Anota la IP (ej: 192.168.1.100)
```

**Opción B - Desde tu PC (escanear red):**
```powershell
# En PowerShell:
arp -a | findstr "b8-27-eb dc-a6-32"
```

**Opción C - Desde el router:**
- Acceder a 192.168.1.1 (o la IP de tu router)
- Buscar "raspberrypi" en dispositivos conectados

---

### 2️⃣ Conectar vía SSH desde tu PC

```powershell
# Reemplazar 192.168.1.100 con la IP de tu Raspberry Pi
ssh pi@192.168.1.100

# Contraseña: raspi
```

---

### 3️⃣ Ejecutar Script de Configuración Automática

**En la Raspberry Pi (vía SSH):**

```bash
# Descargar y ejecutar script de setup
curl -o setup.sh https://raw.githubusercontent.com/.../setup.sh
chmod +x setup.sh
./setup.sh
```

**O copiar manualmente el script:**

```bash
# Crear el script
nano setup.sh

# Pegar el contenido del archivo setup.sh
# Guardar: Ctrl+O, Enter, Ctrl+X

# Dar permisos de ejecución
chmod +x setup.sh

# Ejecutar
./setup.sh
```

El script automáticamente:
- ✅ Actualiza el sistema
- ✅ Instala Python, pip, git
- ✅ Crea estructura de directorios
- ✅ Instala dependencias Python
- ✅ Crea config.json con tu IP

---

### 4️⃣ Transferir Archivos desde tu PC

**En tu PC (PowerShell):**

```powershell
# Navegar al proyecto
cd C:\Users\alfredo\.gemini\antigravity\scratch\tidalai-companion

# Ejecutar script de transferencia
.\transfer-to-raspi.ps1 -RaspiIP "192.168.1.100"

# (Reemplazar 192.168.1.100 con la IP de tu Raspberry Pi)
```

**O transferir manualmente:**

```powershell
# Archivos Python
scp -r raspberry-pi pi@192.168.1.100:~/tidalai-companion/

# Documentación
scp -r docs pi@192.168.1.100:~/tidalai-companion/
scp README.md pi@192.168.1.100:~/tidalai-companion/
```

---

### 5️⃣ Configurar IP de tu PC

**En la Raspberry Pi:**

```bash
# Editar configuración
nano ~/tidalai-companion/raspberry-pi/config.json
```

**Actualizar la IP de tu PC:**

```json
{
  "raspberry_pi": {
    "ip": "192.168.1.100",     // ← IP de tu Raspberry Pi (ya configurada)
    "flask_port": 5000
  },
  "pc": {
    "ip": "192.168.1.50",      // ← CAMBIAR: IP de tu PC
    "osc_port": 6010
  }
}
```

**Encontrar IP de tu PC:**
```powershell
# En tu PC (PowerShell):
ipconfig
# Buscar "Dirección IPv4"
```

---

### 6️⃣ Iniciar el Servidor

**En la Raspberry Pi:**

```bash
cd ~/tidalai-companion/raspberry-pi/web
python3 app.py
```

**Deberías ver:**
```
=== TidalAI Companion Server ===
Iniciando en http://0.0.0.0:5000
OSC target: 192.168.1.50:6010
 * Running on http://192.168.1.100:5000
```

---

### 7️⃣ Acceder desde tu PC

**En tu navegador:**
```
http://192.168.1.100:5000
```

**¡Deberías ver la interfaz de TidalAI Companion! 🎉**

---

## 🔧 Comandos Útiles

### En la Raspberry Pi

```bash
# Ver IP
hostname -I

# Editar configuración
nano ~/tidalai-companion/raspberry-pi/config.json

# Iniciar servidor
cd ~/tidalai-companion/raspberry-pi/web && python3 app.py

# Probar generador
cd ~/tidalai-companion/raspberry-pi/generator
python3 pattern_generator.py

# Ver logs del sistema
sudo journalctl -f
```

### En tu PC

```bash
# Conectar SSH
ssh pi@192.168.1.100

# Transferir archivos
scp archivo.py pi@192.168.1.100:~/tidalai-companion/

# Ver IP de tu PC
ipconfig  # Windows
ifconfig  # Linux/Mac
```

---

## ⚡ Inicio Automático (Opcional)

Para que el servidor inicie automáticamente al arrancar:

```bash
# En la Raspberry Pi:
sudo nano /etc/systemd/system/tidalai.service
```

**Contenido:**
```ini
[Unit]
Description=TidalAI Companion Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tidalai-companion/raspberry-pi/web
ExecStart=/usr/bin/python3 /home/pi/tidalai-companion/raspberry-pi/web/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Activar:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tidalai.service
sudo systemctl start tidalai.service
```

---

## 🐛 Troubleshooting Rápido

### No puedo conectar vía SSH

```bash
# Verificar que SSH está activo
sudo systemctl status ssh

# Si no está activo:
sudo systemctl enable ssh
sudo systemctl start ssh
```

### No puedo acceder a la interfaz web

```bash
# Verificar que el servidor está corriendo
ps aux | grep app.py

# Verificar puerto
sudo netstat -tulpn | grep 5000

# Reiniciar servidor
cd ~/tidalai-companion/raspberry-pi/web
python3 app.py
```

### Error al instalar dependencias

```bash
# Actualizar pip
pip3 install --upgrade pip

# Instalar una por una
pip3 install flask
pip3 install python-osc
pip3 install numpy
```

---

## 📚 Documentación Completa

- **[CONFIGURACION_RASPI.md](CONFIGURACION_RASPI.md)** - Guía detallada paso a paso
- **[GUIA_USO.md](GUIA_USO.md)** - Manual completo de uso
- **[ARQUITECTURA.md](ARQUITECTURA.md)** - Documentación técnica

---

**¡Listo para crear música con IA! 🎵🍓**
