# Script para verificar que el modo IA se está enviando correctamente

echo "=== Verificación del Modo IA ==="
echo ""

echo "1. Verificando archivo JavaScript..."
grep -n "use_ai" ~/tidalai-companion/raspberry-pi/web/static/app.js | head -5

echo ""
echo "2. Verificando archivo app.py..."
grep -n "use_ai" ~/tidalai-companion/raspberry-pi/web/app.py | head -5

echo ""
echo "3. Últimas 20 líneas del log del servidor:"
sudo journalctl -u tidalai.service -n 20 --no-pager

echo ""
echo "4. Para ver logs en tiempo real:"
echo "   sudo journalctl -u tidalai.service -f"
echo ""
echo "5. Para reiniciar el servidor:"
echo "   sudo systemctl restart tidalai.service"
echo ""
