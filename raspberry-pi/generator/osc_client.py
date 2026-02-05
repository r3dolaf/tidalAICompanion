"""
TidalAI Companion - OSC Client
Cliente OSC para enviar patrones TidalCycles al PC.
"""

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import logging
from typing import Optional
import time


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OSCClient:
    """
    Cliente OSC para comunicación con TidalCycles/SuperCollider.
    
    Maneja el envío de patrones y parámetros vía OSC sobre UDP.
    """
    
    def __init__(self, target_ip: str = "127.0.0.1", target_port: int = 6010):
        """
        Inicializar cliente OSC.
        
        Args:
            target_ip: IP del PC que ejecuta TidalCycles
            target_port: Puerto OSC (default: 6010)
        """
        self.target_ip = target_ip
        self.target_port = target_port
        self.client = None
        self.connected = False
        
        self._connect()
    
    def _connect(self):
        """Establecer conexión OSC"""
        try:
            self.client = udp_client.SimpleUDPClient(self.target_ip, self.target_port)
            self.connected = True
            logger.info(f"OSC Client conectado a {self.target_ip}:{self.target_port}")
        except Exception as e:
            logger.error(f"Error conectando OSC client: {e}")
            self.connected = False
    
    def send_pattern(self, channel: str, pattern: str) -> bool:
        """
        Enviar patrón completo a TidalCycles.
        
        Args:
            channel: Canal Tidal (ej: 'd1', 'd2', etc.)
            pattern: Código Tidal completo
        
        Returns:
            True si se envió correctamente, False si hubo error
        """
        if not self.connected:
            logger.warning("OSC client no conectado, intentando reconectar...")
            self._connect()
            if not self.connected:
                return False
        
        try:
            # Enviar mensaje OSC
            self.client.send_message("/tidal/pattern", [channel, pattern])
            logger.info(f"Patrón enviado a {channel}: {pattern[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando patrón: {e}")
            self.connected = False
            return False
    
    def send_param(self, channel: str, param: str, value: float) -> bool:
        """
        Enviar parámetro individual a un canal.
        
        Args:
            channel: Canal Tidal (ej: 'd1')
            param: Nombre del parámetro (ej: 'speed', 'cutoff', 'room')
            value: Valor del parámetro
        
        Returns:
            True si se envió correctamente
        """
        if not self.connected:
            logger.warning("OSC client no conectado, intentando reconectar...")
            self._connect()
            if not self.connected:
                return False
        
        try:
            self.client.send_message("/tidal/param", [channel, param, value])
            logger.info(f"Parámetro enviado: {channel}.{param} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando parámetro: {e}")
            self.connected = False
            return False
    
    def stop_channel(self, channel: str) -> bool:
        """
        Detener un canal específico.
        
        Args:
            channel: Canal a detener (ej: 'd1')
        
        Returns:
            True si se envió correctamente
        """
        if not self.connected:
            logger.warning("OSC client no conectado, intentando reconectar...")
            self._connect()
            if not self.connected:
                return False
        
        try:
            self.client.send_message("/tidal/stop", [channel])
            logger.info(f"Canal detenido: {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo canal: {e}")
            self.connected = False
            return False
    
    def stop_all(self) -> bool:
        """
        Detener todos los canales (d1-d9).
        
        Returns:
            True si se enviaron todos los mensajes
        """
        success = True
        for i in range(1, 10):
            if not self.stop_channel(f"d{i}"):
                success = False
        return success
    
    def send_custom(self, address: str, *args) -> bool:
        """
        Enviar mensaje OSC personalizado.
        
        Args:
            address: Dirección OSC (ej: '/custom/message')
            *args: Argumentos del mensaje
        
        Returns:
            True si se envió correctamente
        """
        if not self.connected:
            logger.warning("OSC client no conectado, intentando reconectar...")
            self._connect()
            if not self.connected:
                return False
        
        try:
            self.client.send_message(address, list(args))
            logger.info(f"Mensaje personalizado enviado: {address} {args}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje personalizado: {e}")
            self.connected = False
            return False
    
    def test_connection(self) -> bool:
        """
        Probar conexión enviando mensaje de ping.
        
        Returns:
            True si la conexión funciona
        """
        try:
            self.client.send_message("/tidal/ping", ["test"])
            logger.info("Test de conexión enviado")
            return True
        except Exception as e:
            logger.error(f"Test de conexión falló: {e}")
            return False
    
    def check_reachability(self) -> bool:
        """
        Verificar si el host objetivo es alcanzable mediante Ping.
        """
        import subprocess
        import platform
        
        try:
            # Determinar comando según OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', self.target_ip]
            
            # Ejecutar ping (sin mostrar output)
            return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        except Exception as e:
            logger.error(f"Error en ping check: {e}")
            return False

    def get_status(self) -> dict:
        """
        Obtener estado del cliente.
        """
        # Verificar conectividad real (Ping)
        # NOTA: No sobrescribimos self.connected porque UDP puede funcionar sin Ping (Firewall)
        is_reachable = self.check_reachability()
        
        return {
            'connected': self.connected,
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'reachable': is_reachable
        }


# Ejemplo de uso
if __name__ == "__main__":
    print("=== TidalAI OSC Client - Test ===\n")
    
    # Crear cliente (cambiar IP según tu configuración)
    client = OSCClient(target_ip="127.0.0.1", target_port=6010)
    
    # Test 1: Enviar patrón simple
    print("Test 1: Enviando patrón de drums...")
    pattern = 'sound "bd sn hh sn"'
    client.send_pattern("d1", pattern)
    time.sleep(2)
    
    # Test 2: Enviar parámetro
    print("\nTest 2: Enviando parámetro speed...")
    client.send_param("d1", "speed", 1.5)
    time.sleep(2)
    
    # Test 3: Enviar patrón más complejo
    print("\nTest 3: Enviando patrón complejo...")
    complex_pattern = '''sound "bd*4 sn*2 hh*8"
  # speed 1.2
  # room 0.3'''
    client.send_pattern("d2", complex_pattern)
    time.sleep(2)
    
    # Test 4: Detener canal
    print("\nTest 4: Deteniendo d1...")
    client.stop_channel("d1")
    time.sleep(1)
    
    # Test 5: Detener todos
    print("\nTest 5: Deteniendo todos los canales...")
    client.stop_all()
    
    # Estado
    print(f"\nEstado del cliente: {client.get_status()}")
