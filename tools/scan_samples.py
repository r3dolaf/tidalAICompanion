import os
import json
import requests
import socket

def find_dirt_samples():
    """Intentar localizar la carpeta Dirt-Samples automáticamente"""
    # Rutas comunes en Windows
    common_paths = [
        os.path.expanduser("~\\AppData\\Local\\SuperCollider\\downloaded-quarks\\Dirt-Samples"),
        os.path.expanduser("~\\Dirt-Samples"),
        "C:\\Dirt-Samples"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def scan_folder(base_path):
    """Escanear carpetas y contar archivos de audio"""
    print(f"Escaneando {base_path}...")
    inventory = {}
    
    # Extensiones de audio soportadas por SuperDirt
    audio_exts = ('.wav', '.aif', '.aiff', '.flac', '.ogg')
    
    try:
        # Listar subdirectorios (cada uno es un banco de samples)
        for entry in os.scandir(base_path):
            if entry.is_dir() and not entry.name.startswith('.'):
                sample_name = entry.name
                # Contar archivos de audio dentro
                count = 0
                for f in os.scandir(entry.path):
                    if f.is_file() and f.name.lower().endswith(audio_exts):
                        count += 1
                
                if count > 0:
                    inventory[sample_name] = count
                    # print(f"  Found: {sample_name} ({count})")
                    
    except Exception as e:
        print(f"Error escaneando: {e}")
        return None

    return inventory

def main():
    print("=== TidalAI Sample Scout ===")
    print("Este script escaneará tus samples para enseñárselos a la IA.\n")
    
    # 1. Localizar Dirt-Samples
    path = find_dirt_samples()
    if path:
        print(f"Carpeta detectada: {path}")
        use_auto = input("¿Usar esta carpeta? [S/n]: ").lower() != 'n'
        if not use_auto:
            path = input("Introduce la ruta completa a Dirt-Samples: ").strip()
    else:
        path = input("Introduce la ruta completa a Dirt-Samples: ").strip()
        
    if not os.path.exists(path):
        print("Error: La ruta no existe.")
        return

    # 2. Escanear
    inventory = scan_folder(path)
    if not inventory:
        print("No se encontraron samples.")
        return
    
    print(f"\n¡Escaneo completado! Se encontraron {len(inventory)} bancos de sonido.")
    
    # 3. Enviar a la Pi
    default_ip = "192.168.1.55" # Valor por defecto común, o localhost si es test
    pi_ip = input(f"IP de la Raspberry Pi [{default_ip}]: ").strip() or default_ip
    pi_port = "5000"
    
    url = f"http://{pi_ip}:{pi_port}/api/samples/upload"
    
    try:
        print(f"Enviando datos a {url}...")
        response = requests.post(url, json=inventory, timeout=5)
        
        if response.status_code == 200:
            print("\n✅ ¡Éxito! La IA ha aprendido tus samples.")
        else:
            print(f"\n❌ Error del servidor: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        print("Asegúrate de que la Pi está encendida y conectada a la misma red.")

    input("\nPresiona ENTER para cerrar...")

if __name__ == "__main__":
    main()
