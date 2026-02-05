import os
import subprocess
import threading
import time
import webbrowser
from flask import Flask, render_template, jsonify, request

# ==============================================================================
# 🔧 EL MOTOR (THE ENGINE)
# ==============================================================================
# Este script actúa como un "puente" seguro entre la interfaz web moderna
# y el sistema operativo Windows.
#
# CÓMO FUNCIONA:
# 1. Levanta un servidor web local en el puerto 8080.
# 2. Expone "endpoints" (botones) que la web puede llamar.
# 3. Cuando recibe una llamada, ejecuta el script .bat correspondiente
#    usando `subprocess`, que es la forma nativa de Python de hablar con Windows.
# ==============================================================================

app = Flask(__name__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@app.route('/')
def home():
    """Sirve la interfaz gráfica del lanzador."""
    return render_template('launcher.html')

@app.route('/api/run/<action>', methods=['POST'])
def run_action(action):
    """
    Endpoint maestro para ejecutar comandos.
    Recibe el nombre de la acción y busca el script correspondiente.
    """
    scripts = {
        'deploy': 'deploy.bat',
        'cleanup': 'cleanup.bat',
        'ssh': 'setup-ssh.bat',
        'extract': 'extract-patterns-interactive.bat',
        'admin_remote': 'admin.bat' # Abre navegador, pero lo incluimos por completitud
    }
    
    if action not in scripts:
        return jsonify({'success': False, 'error': 'Acción desconocida'}), 400
    
    script_name = scripts[action]
    script_path = os.path.join(PROJECT_ROOT, script_name)
    
    if not os.path.exists(script_path):
        return jsonify({'success': False, 'error': f'Script no encontrado: {script_name}'}), 404
    
    try:
        # Ejecutamos el script en una ventana nueva para que el usuario vea el output
        # 'start' es un comando de cmd.exe para abrir ventana nueva
        cmd = f'start cmd /k "{script_path}"'
        subprocess.Popen(cmd, shell=True, cwd=PROJECT_ROOT)
        return jsonify({'success': True, 'message': f'Ejecutando {script_name}...'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/open/folder/<target>', methods=['POST'])
def open_folder(target):
    """Abre carpetas locales en el Explorador de Windows."""
    paths = {
        'root': PROJECT_ROOT,
        'corpus': os.path.join(PROJECT_ROOT, 'examples', 'corpus'),
        'bridge': os.path.join(PROJECT_ROOT, 'pc-side')
    }
    
    if target not in paths:
        return jsonify({'success': False, 'error': 'Carpeta desconocida'}), 400
    
    path = paths[target]
    try:
        os.startfile(path) # Nativo de Windows para abrir explorer
        return jsonify({'success': True, 'message': f'Abriendo {path}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def open_browser():
    """Abre el navegador automáticamente después de arrancar."""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:8080')

if __name__ == '__main__':
    print("🚀 Iniciando TidalAI Local Engine...")
    print(f"📂 Project Root: {PROJECT_ROOT}")
    
    # Lanzar hilo para abrir navegador
    threading.Thread(target=open_browser).start()
    
    # Arrancar servidor (bloqueante)
    app.run(host='127.0.0.1', port=8080)
