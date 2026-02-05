# 🍓 Configuración de Raspberry Pi 3B+ para TidalAI Companion

> Guía paso a paso para configurar tu Raspberry Pi desde cero

---

## 📋 Requisitos Previos

### Hardware Necesario
- ✅ Raspberry Pi 3B+
- ✅ Tarjeta microSD (mínimo 8GB, recomendado 16GB+)
- ✅ Fuente de alimentación 5V/2.5A (oficial recomendada)
- ✅ Cable Ethernet (opcional, para configuración inicial)
- ✅ Teclado y monitor (para configuración inicial) o acceso SSH

### Software Necesario (en tu PC)
- ✅ [Raspberry Pi Imager](https://www.raspberrypi.com/software/) - Para grabar el SO
- ✅ Cliente SSH (PuTTY en Windows, o terminal en Linux/Mac)

---

## 🚀 Paso 1: Instalar Raspberry Pi OS

### 1.1 Descargar Raspberry Pi Imager

**Windows:**
```powershell
# Descargar desde: https://www.raspberrypi.com/software/
# O instalar con winget:
winget install RaspberryPiFoundation.RaspberryPiImager
```

### 1.2 Grabar el Sistema Operativo

1. **Abrir Raspberry Pi Imager**
2. **Elegir OS**: 
   - Click en "Choose OS"
   - Seleccionar **"Raspberry Pi OS Lite (64-bit)"**
   - (Lite es suficiente, no necesitamos interfaz gráfica)

3. **Elegir Storage**:
   - Insertar tarjeta microSD en tu PC
   - Click en "Choose Storage"
   - Seleccionar tu tarjeta microSD

4. **Configuración Avanzada** (⚙️ icono de engranaje):
   - ✅ **Enable SSH**: Activar
   - ✅ **Set username and password**:
     - Username: `pi` (o el que prefieras)
     - Password: (elige una contraseña segura)
   - ✅ **Configure wireless LAN** (si usarás WiFi):
     - SSID: nombre de tu red WiFi
     - Password: contraseña de tu WiFi
     - Wireless LAN country: `ES` (España)
   - ✅ **Set locale settings**:
     - Time zone: `Europe/Madrid`
     - Keyboard layout: `es`

5. **Grabar**:
   - Click en "Write"
   - Confirmar (borrará todo en la SD)
   - Esperar ~5-10 minutos

6. **Finalizar**:
   - Cuando termine, extraer la SD
   - Insertar en la Raspberry Pi

---

## 🔌 Paso 2: Primer Arranque

### 2.1 Conectar la Raspberry Pi

**Opción A - Con monitor y teclado:**
1. Conectar monitor vía HDMI
2. Conectar teclado USB
3. Conectar cable Ethernet (opcional)
4. Conectar alimentación (último paso)

**Opción B - Headless (sin monitor):**
1. Conectar cable Ethernet al router
2. Conectar alimentación
3. Esperar ~2 minutos para que arranque

### 2.2 Encontrar la IP de la Raspberry Pi

**Método 1 - Con monitor:**
```bash
# Una vez iniciada sesión, ejecutar:
hostname -I
# Anota la IP que aparece (ej: 192.168.1.100)
```

**Método 2 - Desde tu PC (Windows):**
```powershell
# Escanear red local:
arp -a | findstr "b8-27-eb"
# Las Raspberry Pi tienen MAC que empieza con b8-27-eb o dc-a6-32
```

**Método 3 - Desde el router:**
- Acceder a la configuración del router (ej: 192.168.1.1)
- Buscar en "Dispositivos conectados" o "DHCP clients"
- Buscar "raspberrypi" o similar

### 2.3 Conectar vía SSH

**Desde Windows (PowerShell):**
```powershell
ssh pi@192.168.1.100
# Reemplazar 192.168.1.100 con la IP de tu RPi
# Contraseña: la que configuraste en el Imager
```

**Primera vez:**
```
The authenticity of host '192.168.1.100' can't be established.
Are you sure you want to continue connecting (yes/no)? yes
```

---

## ⚙️ Paso 3: Configuración Inicial del Sistema

### 3.1 Actualizar el Sistema

```bash
# Actualizar lista de paquetes
sudo apt update

# Actualizar paquetes instalados (puede tardar 10-15 min)
sudo apt upgrade -y

# Reiniciar
sudo reboot
```

**Nota**: Después del reboot, reconectar vía SSH.

### 3.2 Configurar IP Estática (Recomendado)

Para que la IP no cambie cada vez que reinicies:

```bash
# Editar configuración de red
sudo nano /etc/dhcpcd.conf
```

**Añadir al final del archivo** (ajustar según tu red):

```bash
# IP estática para TidalAI
interface wlan0  # o eth0 si usas cable
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

**Guardar y salir**:
- `Ctrl + O` (guardar)
- `Enter` (confirmar)
- `Ctrl + X` (salir)

**Aplicar cambios**:
```bash
sudo reboot
```

### 3.3 Configurar Hostname (Opcional)

Para identificar fácilmente la RPi en la red:

```bash
sudo raspi-config
```

- Navegar a: `1 System Options` → `S4 Hostname`
- Cambiar a: `tidalai`
- `Finish` → `Reboot`

Ahora podrás conectar con:
```bash
ssh pi@tidalai.local
```

---

## 📦 Paso 4: Instalar Dependencias

### 4.1 Instalar Python 3 y pip

```bash
# Verificar versión de Python (debería ser 3.9+)
python3 --version

# Instalar pip
sudo apt install python3-pip -y

# Verificar pip
pip3 --version
```

### 4.2 Instalar Git

```bash
sudo apt install git -y

# Verificar
git --version
```

### 4.3 Instalar Dependencias del Sistema

```bash
# Necesarias para algunas librerías Python
sudo apt install python3-dev build-essential -y
```

---

## 📥 Paso 5: Transferir el Proyecto a la Raspberry Pi

### Opción A - Usando Git (si tienes repositorio)

```bash
cd ~
git clone <url-del-repositorio>
cd tidalai-companion
```

### Opción B - Transferir desde tu PC

**Desde tu PC (PowerShell):**

```powershell
# Navegar al proyecto
cd C:\Users\alfredo\.gemini\antigravity\scratch\tidalai-companion

# Copiar a la Raspberry Pi usando SCP
scp -r raspberry-pi pi@192.168.1.100:~/tidalai-companion/
scp -r examples pi@192.168.1.100:~/tidalai-companion/
scp -r docs pi@192.168.1.100:~/tidalai-companion/
scp README.md pi@192.168.1.100:~/tidalai-companion/
```

**Verificar en la RPi:**
```bash
cd ~/tidalai-companion
ls -la
# Deberías ver: raspberry-pi, examples, docs, README.md
```

### Opción C - Crear directamente en la RPi

```bash
# Crear estructura
mkdir -p ~/tidalai-companion/raspberry-pi/{generator,web/{templates,static}}
mkdir -p ~/tidalai-companion/docs
mkdir -p ~/tidalai-companion/examples/corpus

# Luego copiar archivos uno por uno o usar nano para crearlos
```

---

## 🐍 Paso 6: Instalar Dependencias Python

```bash
cd ~/tidalai-companion/raspberry-pi

# Instalar dependencias
pip3 install -r requirements.txt

# Esto instalará:
# - flask
# - python-osc
# - numpy
# - markdown
# - weasyprint (puede tardar varios minutos en RPi)
```

**Nota**: La instalación de WeasyPrint puede tardar 5-10 minutos en la Raspberry Pi.

---

## 🔧 Paso 7: Configurar el Proyecto

### 7.1 Editar config.json

```bash
cd ~/tidalai-companion/raspberry-pi
nano config.json
```

**Actualizar las IPs**:

```json
{
  "raspberry_pi": {
    "ip": "192.168.1.100",     // ← IP de tu Raspberry Pi
    "flask_port": 5000
  },
  "pc": {
    "ip": "192.168.1.50",      // ← IP de tu PC (encontrar con ipconfig)
    "osc_port": 6010
  },
  "generator": {
    "default_tempo": 140,
    "default_density": 0.6,
    "default_complexity": 0.5,
    "default_style": "techno"
  }
}
```

**Guardar**: `Ctrl + O`, `Enter`, `Ctrl + X`

### 7.2 Encontrar IP de tu PC

**En tu PC (PowerShell):**
```powershell
ipconfig
# Buscar "Dirección IPv4" en tu adaptador de red activo
# Ejemplo: 192.168.1.50
```

---

## 🧪 Paso 8: Probar el Sistema

### 8.1 Probar el Generador de Patrones

```bash
cd ~/tidalai-companion/raspberry-pi/generator
python3 pattern_generator.py
```

**Deberías ver**:
```
=== TidalAI Pattern Generator - Ejemplos ===

1. Drums Techno (densidad: 0.7, complejidad: 0.6)
d1 $ sound "bd*6 sn*2 hh*12"
  # speed 1.15
  # room 0.21

2. Bass Ambient (densidad: 0.4, complejidad: 0.3)
...
```

### 8.2 Probar el Cliente OSC

```bash
cd ~/tidalai-companion/raspberry-pi/generator
python3 osc_client.py
```

**Deberías ver**:
```
=== TidalAI OSC Client - Test ===

Test 1: Enviando patrón de drums...
INFO - Patrón enviado a d1: sound "bd sn hh sn"...
```

**Nota**: Si tu PC no está escuchando OSC aún, verás los mensajes enviados pero no habrá respuesta (es normal).

### 8.3 Iniciar el Servidor Flask

```bash
cd ~/tidalai-companion/raspberry-pi/web
python3 app.py
```

**Deberías ver**:
```
=== TidalAI Companion Server ===
Iniciando en http://0.0.0.0:5000
OSC target: 192.168.1.50:6010
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.100:5000
```

### 8.4 Acceder desde tu PC

**En tu PC, abrir navegador**:
```
http://192.168.1.100:5000
```

**Deberías ver**: La interfaz web de TidalAI Companion 🎉

---

## 🔄 Paso 9: Configurar Inicio Automático (Opcional)

Para que el servidor Flask inicie automáticamente al arrancar la RPi:

### 9.1 Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/tidalai.service
```

**Contenido**:
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
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Guardar**: `Ctrl + O`, `Enter`, `Ctrl + X`

### 9.2 Activar el Servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable tidalai.service

# Iniciar el servicio ahora
sudo systemctl start tidalai.service

# Verificar estado
sudo systemctl status tidalai.service
```

**Deberías ver**: `Active: active (running)`

### 9.3 Comandos Útiles

```bash
# Detener el servicio
sudo systemctl stop tidalai.service

# Reiniciar el servicio
sudo systemctl restart tidalai.service

# Ver logs
sudo journalctl -u tidalai.service -f
```

---

## 🛡️ Paso 10: Configurar Firewall (Opcional)

```bash
# Instalar ufw (firewall)
sudo apt install ufw -y

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir Flask
sudo ufw allow 5000/tcp

# Habilitar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

---

## 🔍 Troubleshooting

### Problema: No puedo conectar vía SSH

**Soluciones**:
```bash
# Verificar que SSH está habilitado
sudo systemctl status ssh

# Si no está activo:
sudo systemctl enable ssh
sudo systemctl start ssh
```

### Problema: No encuentro la IP de la RPi

**Solución**:
```bash
# Conectar monitor y teclado
# Iniciar sesión
# Ejecutar:
hostname -I
```

### Problema: pip install falla

**Solución**:
```bash
# Actualizar pip
pip3 install --upgrade pip

# Instalar dependencias una por una
pip3 install flask
pip3 install python-osc
pip3 install numpy
```

### Problema: WeasyPrint no se instala

**Solución**:
```bash
# Instalar dependencias del sistema
sudo apt install libpango-1.0-0 libpangoft2-1.0-0 -y

# Reintentar
pip3 install weasyprint
```

### Problema: No puedo acceder a la interfaz web

**Verificar**:
```bash
# ¿Está corriendo el servidor?
ps aux | grep app.py

# ¿Está escuchando en el puerto correcto?
sudo netstat -tulpn | grep 5000

# ¿Firewall bloqueando?
sudo ufw status
```

---

## ✅ Checklist de Configuración

- [ ] Raspberry Pi OS instalado en SD
- [ ] SSH habilitado y funcionando
- [ ] IP estática configurada
- [ ] Sistema actualizado (`apt update && apt upgrade`)
- [ ] Python 3 y pip instalados
- [ ] Proyecto transferido a la RPi
- [ ] Dependencias Python instaladas (`requirements.txt`)
- [ ] `config.json` editado con IPs correctas
- [ ] Generador de patrones probado
- [ ] Servidor Flask iniciado
- [ ] Interfaz web accesible desde PC
- [ ] (Opcional) Servicio systemd configurado
- [ ] (Opcional) Firewall configurado

---

## 🎯 Próximos Pasos

Una vez completada la configuración:

1. **En tu PC**: Configurar SuperCollider (ver GUIA_USO.md)
2. **Probar flujo completo**: Generar patrón → Enviar vía OSC → Ejecutar en Tidal
3. **Experimentar**: Ajustar parámetros y explorar diferentes estilos

---

## 📚 Recursos Adicionales

- [Documentación oficial Raspberry Pi](https://www.raspberrypi.com/documentation/)
- [Raspberry Pi Forums](https://forums.raspberrypi.com/)
- [GUIA_USO.md](GUIA_USO.md) - Manual completo de uso
- [ARQUITECTURA.md](ARQUITECTURA.md) - Detalles técnicos

---

**¡Tu Raspberry Pi está lista para generar música! 🎵🍓**
