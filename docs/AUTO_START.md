# TidalAI Companion - Guía de Auto-Start

## ✅ Asegurar Inicio Automático del Servicio

Para que el servidor TidalAI se inicie automáticamente al arrancar la Raspberry Pi:

### Método 1: Script Automático (Recomendado)

**En la Raspberry Pi**:

```bash
cd ~/tidalai-companion/raspberry-pi
chmod +x enable-autostart.sh
./enable-autostart.sh
```

Este script:
1. ✅ Copia el archivo de servicio a `/etc/systemd/system/`
2. ✅ Recarga systemd
3. ✅ Habilita el inicio automático
4. ✅ Inicia el servicio
5. ✅ Muestra el estado

---

### Método 2: Manual

**Paso 1: Copiar archivo de servicio**
```bash
sudo cp ~/tidalai-companion/raspberry-pi/tidalai.service /etc/systemd/system/
```

**Paso 2: Recargar systemd**
```bash
sudo systemctl daemon-reload
```

**Paso 3: Habilitar auto-start**
```bash
sudo systemctl enable tidalai.service
```

**Paso 4: Iniciar servicio**
```bash
sudo systemctl start tidalai.service
```

---

## 🔍 Verificar que Está Habilitado

```bash
# Ver si está habilitado
sudo systemctl is-enabled tidalai.service
# Debe mostrar: enabled

# Ver estado
sudo systemctl status tidalai.service
```

---

## 🧪 Probar el Auto-Start

**Reinicia la Raspberry Pi**:
```bash
sudo reboot
```

**Después del reinicio, verifica**:
```bash
sudo systemctl status tidalai.service
```

Debería mostrar:
- `Active: active (running)`
- `Loaded: loaded (...; enabled; ...)`

---

## 📋 Comandos Útiles

```bash
# Ver estado
sudo systemctl status tidalai.service

# Reiniciar servicio
sudo systemctl restart tidalai.service

# Detener servicio
sudo systemctl stop tidalai.service

# Deshabilitar auto-start (si quieres)
sudo systemctl disable tidalai.service

# Ver logs
sudo journalctl -u tidalai.service -n 50

# Ver logs en tiempo real
sudo journalctl -u tidalai.service -f
```

---

## ⚠️ Solución de Problemas

### El servicio no se inicia automáticamente

**1. Verificar que está habilitado**:
```bash
sudo systemctl is-enabled tidalai.service
```

Si dice `disabled`, ejecuta:
```bash
sudo systemctl enable tidalai.service
```

**2. Verificar errores en el servicio**:
```bash
sudo journalctl -u tidalai.service -n 100
```

**3. Verificar permisos**:
```bash
ls -la /etc/systemd/system/tidalai.service
# Debe ser propiedad de root
```

**4. Verificar que Python y dependencias están instaladas**:
```bash
python3 --version
pip3 list | grep Flask
```

---

## 📝 Contenido del Archivo de Servicio

El archivo `tidalai.service` contiene:

```ini
[Unit]
Description=TidalAI Companion Web Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/tidalai-companion/raspberry-pi/web
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Explicación**:
- `After=network.target`: Espera a que la red esté disponible
- `Restart=always`: Se reinicia automáticamente si falla
- `RestartSec=10`: Espera 10 segundos antes de reiniciar
- `WantedBy=multi-user.target`: Se inicia en modo multi-usuario (arranque normal)

---

## ✅ Checklist de Verificación

- [ ] Archivo `tidalai.service` copiado a `/etc/systemd/system/`
- [ ] `systemctl daemon-reload` ejecutado
- [ ] `systemctl enable tidalai.service` ejecutado
- [ ] `systemctl is-enabled tidalai.service` muestra "enabled"
- [ ] Servicio funciona: `systemctl status tidalai.service`
- [ ] Probado con reinicio: `sudo reboot`
- [ ] Después del reinicio, servicio está activo

---

## 🚀 Integración con Deploy Script

El script `deploy.bat` ya reinicia el servicio automáticamente después de transferir archivos. No necesitas hacer nada adicional para que los cambios se apliquen.

**Workflow completo**:
1. Editas archivos en tu PC
2. Ejecutas `deploy.bat`
3. El servicio se reinicia automáticamente
4. Recargas la web con Ctrl+Shift+R
5. ¡Listo!
