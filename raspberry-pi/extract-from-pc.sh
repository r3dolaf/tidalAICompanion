#!/bin/bash
# ===================================================================
# Extractor Remoto de Patrones TidalCycles
# Ejecutar desde Raspberry Pi para extraer patrones del PC
# ===================================================================

# Configuración
PC_IP="192.168.1.50"  # Cambiar a la IP de tu PC
PC_USER="alfredo"
PC_TIDAL_DIR="/c/Users/alfredo/Desktop/tidal"  # Ruta en formato Git Bash
RASPI_TEMP="/tmp/tidal_patterns"

echo "=== Extractor Remoto de Patrones ==="
echo ""

# Verificar conectividad
echo "[1/5] Verificando conexión con PC..."
ping -c 1 $PC_IP > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] No se puede conectar a $PC_IP"
    echo "Verifica que el PC esté encendido y en la misma red"
    exit 1
fi
echo "[OK] PC accesible"
echo ""

# Crear directorio temporal
echo "[2/5] Creando directorio temporal..."
mkdir -p $RASPI_TEMP
echo "[OK] Directorio creado"
echo ""

# Copiar archivos .tidal del PC a Raspberry Pi
echo "[3/5] Copiando archivos .tidal desde PC..."
echo "Esto puede tardar un momento..."

# Usar rsync si está disponible, sino scp
if command -v rsync &> /dev/null; then
    rsync -avz --include='*.tidal' --include='*/' --exclude='*' \
        ${PC_USER}@${PC_IP}:${PC_TIDAL_DIR}/ ${RASPI_TEMP}/
else
    # Fallback a scp (menos eficiente)
    scp -r ${PC_USER}@${PC_IP}:${PC_TIDAL_DIR}/*.tidal ${RASPI_TEMP}/ 2>/dev/null
fi

if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudieron copiar los archivos"
    echo "Verifica las credenciales SSH y la ruta del directorio"
    exit 1
fi

echo "[OK] Archivos copiados"
echo ""

# Ejecutar extractor
echo "[4/5] Extrayendo patrones..."
cd ~/tidalai-companion

python3 tools/extract-patterns.py $RASPI_TEMP \
    --output examples/corpus/extracted_from_pc.txt \
    --format corpus

if [ $? -ne 0 ]; then
    echo "[ERROR] Error extrayendo patrones"
    exit 1
fi

echo ""
echo "[5/5] Limpiando archivos temporales..."
rm -rf $RASPI_TEMP
echo "[OK] Limpieza completada"
echo ""

# Preguntar si añadir al corpus
echo "¿Añadir estos patrones al corpus base? (s/n)"
read -r response
if [ "$response" = "s" ]; then
    cat examples/corpus/extracted_from_pc.txt >> examples/corpus/patterns.txt
    echo "[OK] Patrones añadidos al corpus"
    
    # Preguntar si re-entrenar
    echo ""
    echo "¿Re-entrenar el modelo ahora? (s/n)"
    read -r response2
    if [ "$response2" = "s" ]; then
        echo "[INFO] Re-entrenando modelo..."
        # Aquí podrías llamar directamente a la API o reiniciar el servicio
        curl -X POST http://localhost:5000/api/retrain
        echo ""
        echo "[OK] Modelo re-entrenado"
    fi
fi

echo ""
echo "========================================="
echo " Extracción completada"
echo "========================================="
echo ""
echo "Archivo generado: examples/corpus/extracted_from_pc.txt"
echo ""
echo "Para re-entrenar manualmente:"
echo "  1. Abre http://192.168.1.147:5000"
echo "  2. Click '🔄 Re-entrenar Modelo'"
echo ""
