#!/bin/bash
# Script de configuración rápida para TidalAI Companion
# Usuario: pi | Password: raspi

echo "=================================="
echo "TidalAI Companion - Setup Script"
echo "=================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paso 1: Actualizar sistema
echo -e "${YELLOW}[1/7] Actualizando sistema...${NC}"
sudo apt update
sudo apt upgrade -y

# Paso 2: Instalar dependencias del sistema
echo -e "${YELLOW}[2/7] Instalando dependencias del sistema...${NC}"
sudo apt install -y python3-pip git python3-dev build-essential

# Paso 3: Crear estructura de directorios
echo -e "${YELLOW}[3/7] Creando estructura de directorios...${NC}"
mkdir -p ~/tidalai-companion/raspberry-pi/{generator,web/{templates,static}}
mkdir -p ~/tidalai-companion/docs
mkdir -p ~/tidalai-companion/examples/corpus
mkdir -p ~/tidalai-companion/pc-side

# Paso 4: Crear archivo requirements.txt
echo -e "${YELLOW}[4/7] Creando requirements.txt...${NC}"
cat > ~/tidalai-companion/raspberry-pi/requirements.txt << 'EOF'
flask==3.0.0
python-osc==1.8.3
numpy==1.24.3
markdown==3.5.1
weasyprint==60.1
EOF

# Paso 5: Instalar dependencias Python
echo -e "${YELLOW}[5/7] Instalando dependencias Python (puede tardar varios minutos)...${NC}"
cd ~/tidalai-companion/raspberry-pi
pip3 install -r requirements.txt

# Paso 6: Obtener IP de la Raspberry Pi
echo -e "${YELLOW}[6/7] Obteniendo configuración de red...${NC}"
RASPI_IP=$(hostname -I | awk '{print $1}')
echo "IP de la Raspberry Pi: $RASPI_IP"

# Paso 7: Crear config.json con IP detectada
echo -e "${YELLOW}[7/7] Creando config.json...${NC}"
cat > ~/tidalai-companion/raspberry-pi/config.json << EOF
{
  "raspberry_pi": {
    "ip": "$RASPI_IP",
    "flask_port": 5000
  },
  "pc": {
    "ip": "192.168.1.50",
    "osc_port": 6010
  },
  "generator": {
    "default_tempo": 140,
    "default_density": 0.6,
    "default_complexity": 0.5,
    "default_style": "techno"
  }
}
EOF

echo ""
echo -e "${GREEN}=================================="
echo "Setup completado!"
echo "==================================${NC}"
echo ""
echo "Información importante:"
echo "  - IP de la Raspberry Pi: $RASPI_IP"
echo "  - Directorio del proyecto: ~/tidalai-companion"
echo ""
echo "Próximos pasos:"
echo "  1. Transferir archivos del proyecto desde tu PC"
echo "  2. Editar config.json y actualizar la IP de tu PC"
echo "  3. Iniciar el servidor Flask"
echo ""
echo "Comandos útiles:"
echo "  - Ver IP: hostname -I"
echo "  - Editar config: nano ~/tidalai-companion/raspberry-pi/config.json"
echo "  - Iniciar servidor: cd ~/tidalai-companion/raspberry-pi/web && python3 app.py"
echo ""
