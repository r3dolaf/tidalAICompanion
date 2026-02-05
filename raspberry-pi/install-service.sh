#!/bin/bash
# Script para configurar inicio automático de TidalAI Companion

echo "=================================="
echo "TidalAI - Configuración de Inicio Automático"
echo "=================================="
echo ""

# Copiar archivo de servicio
echo "[1/4] Copiando archivo de servicio systemd..."
sudo cp ~/tidalai-companion/raspberry-pi/tidalai.service /etc/systemd/system/

# Recargar systemd
echo "[2/4] Recargando systemd..."
sudo systemctl daemon-reload

# Habilitar servicio
echo "[3/4] Habilitando inicio automático..."
sudo systemctl enable tidalai.service

# Iniciar servicio ahora
echo "[4/4] Iniciando servicio..."
sudo systemctl start tidalai.service

echo ""
echo "=================================="
echo "Configuración completada!"
echo "=================================="
echo ""
echo "El servidor TidalAI se iniciará automáticamente al arrancar la Raspberry Pi."
echo ""
echo "Comandos útiles:"
echo "  - Ver estado:    sudo systemctl status tidalai.service"
echo "  - Ver logs:      sudo journalctl -u tidalai.service -f"
echo "  - Reiniciar:     sudo systemctl restart tidalai.service"
echo "  - Detener:       sudo systemctl stop tidalai.service"
echo "  - Deshabilitar:  sudo systemctl disable tidalai.service"
echo ""
