#!/bin/bash
# ===================================================================
# TidalAI Companion - Verificar y Habilitar Auto-Start
# Ejecutar en la Raspberry Pi para asegurar inicio automático
# ===================================================================

echo "=== TidalAI Companion - Configuración Auto-Start ==="
echo ""

# Verificar si el servicio existe
if [ ! -f ~/tidalai-companion/raspberry-pi/tidalai.service ]; then
    echo "[ERROR] Archivo tidalai.service no encontrado"
    echo "Asegúrate de haber transferido todos los archivos"
    exit 1
fi

echo "[1/4] Copiando archivo de servicio..."
sudo cp ~/tidalai-companion/raspberry-pi/tidalai.service /etc/systemd/system/

if [ $? -eq 0 ]; then
    echo "[OK] Archivo copiado"
else
    echo "[ERROR] No se pudo copiar el archivo"
    exit 1
fi

echo ""
echo "[2/4] Recargando systemd..."
sudo systemctl daemon-reload

echo ""
echo "[3/4] Habilitando inicio automático..."
sudo systemctl enable tidalai.service

if [ $? -eq 0 ]; then
    echo "[OK] Servicio habilitado para inicio automático"
else
    echo "[ERROR] No se pudo habilitar el servicio"
    exit 1
fi

echo ""
echo "[4/4] Iniciando servicio..."
sudo systemctl restart tidalai.service

if [ $? -eq 0 ]; then
    echo "[OK] Servicio iniciado"
else
    echo "[ERROR] No se pudo iniciar el servicio"
    echo "Verifica los logs con: sudo journalctl -u tidalai.service -n 50"
    exit 1
fi

echo ""
echo "========================================="
echo " Configuración completada"
echo "========================================="
echo ""
echo "Estado del servicio:"
sudo systemctl status tidalai.service --no-pager -l

echo ""
echo "El servicio se iniciará automáticamente al arrancar la Raspberry Pi"
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status tidalai.service    # Ver estado"
echo "  sudo systemctl restart tidalai.service   # Reiniciar"
echo "  sudo systemctl stop tidalai.service      # Detener"
echo "  sudo journalctl -u tidalai.service -f    # Ver logs en tiempo real"
echo ""
