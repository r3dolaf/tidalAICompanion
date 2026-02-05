"""
TidalAI Companion - Flask Web Server
Servidor web que expone API REST y sirve interfaz de control.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Añadir path del generador
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'generator'))

from pattern_generator import PatternGenerator
from structure_engine import Conductor
from theory_engine import TheoryEngine
from latent_engine import LatentEngine
from oracle_engine import OracleEngine
from osc_client import OSCClient
from database import DatabaseManager

import json
import logging
from datetime import datetime
import threading
import time
import zipfile
import io

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)

def load_config():
    """Cargar configuración desde config.json"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    
    # Configuración por defecto
    default_config = {
        'raspberry_pi': {
            'ip': '192.168.1.100',
            'flask_port': 5000
        },
        'pc': {
            'ip': '192.168.1.50',
            'osc_port': 6010
        }
    }
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Crear config por defecto
        # Asegurarse de que el directorio padre existe
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.warning(f"Configuración no encontrada, creada en {config_path}")
        return default_config

# --- BACKGROUND SCHEDULER ---
def run_nightly_build():
    """Ejecuta una ronda de evolución automáticamente cada 24 horas"""
    while True:
        try:
            # Esperar 24 horas (u 8 horas para pruebas/demo)
            # En un entorno real esto se haría con cron o apscheduler
            time.sleep(60 * 60 * 12) # Cada 12 horas
            
            logger.info("🧵 [Scheduler] Iniciando Ronda Nocturna Automática...")
            
            from evolutionary_trainer import EvolutionaryTrainer
            trainer = EvolutionaryTrainer(state.generator)
            
            # Cargar config si existe
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config_evolution.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                weights = config.get('weights', {})
                params = config.get('params', {})
                
                result = trainer.run_evolution(
                    batch_size=params.get('batch_size', 50),
                    top_k=params.get('top_k', 10),
                    weights=weights
                )
                
                if result['survivors'] > 0:
                    state.generator._init_markov_model()
                    state.log_activity("🧵 [Auto] Cerebro actualizado tras evolución programada.")
            
        except Exception as e:
            logger.error(f"Error en scheduler nocturno: {e}")
        
# Iniciar hilo en segundo plano
scheduler_thread = threading.Thread(target=run_nightly_build, daemon=True)
scheduler_thread.start()

# Estado global de la aplicación
class AppState:
    def __init__(self):
        self.db = DatabaseManager()  # Initialize Database
        self.generator = PatternGenerator(use_ai=True)
        self.conductor = Conductor()
        self.theory = TheoryEngine()
        self.latent = LatentEngine()
        self.oracle = OracleEngine()
        
        # Cargar configuración inicial para el cliente OSC
        config = load_config()
        self.osc_client = OSCClient(
            target_ip=config['pc']['ip'],
            target_port=config['pc']['osc_port']
        )
        
        self.mode = "suggestions"
        self.config = {
            'density': 0.6,
            'complexity': 0.5,
            'tempo': 140,
            'style': 'techno',
            'instruments': ['kick', 'snare', 'hihat']
        }
        self.last_pattern = None
        self.autonomous_running = False
        self.activity_log = []
    
    def log_activity(self, message: str):
        """Añadir entrada al log de actividad"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.activity_log.append(entry)
        if len(self.activity_log) > 50:
            self.activity_log = self.activity_log[-50:]
        logger.info(message)

state = AppState()


@app.route('/')
def index():
    """Servir interfaz web principal"""
    return render_template('index.html')

@app.route('/admin')
def admin_panel():
    """Servir panel de administración"""
    """Servir panel de administración"""
    return render_template('admin.html')

# --- CONDUCTOR API ---
@app.route('/api/conductor/start', methods=['POST'])
def conductor_start():
    data = request.get_json()
    bpm = int(data.get('bpm', 140))
    template = data.get('template', 'standard')
    custom_structure = data.get('structure', None)
    
    state.conductor.start(bpm, template_name=template, custom_structure=custom_structure)
    
    msg = f"Conductor iniciado ({'Custom' if custom_structure else template})"
    return jsonify({"success": True, "message": msg})

@app.route('/api/conductor/stop', methods=['POST'])
def conductor_stop():
    state.conductor.stop()
    return jsonify({"success": True, "message": "Conductor detenido"})

@app.route('/api/conductor/status', methods=['GET'])
def conductor_status():
    status = state.conductor.update()
    if not status:
        return jsonify({"active": False})
    
    return jsonify({
        "active": True, 
        "data": status
    })

@app.route('/api/conductor/templates', methods=['GET'])
def conductor_templates():
    return jsonify({
        "success": True, 
        "templates": list(state.conductor.templates.keys())
    })

# --- THEORY RULES API (Phase 17b) ---

@app.route('/api/theory/rules', methods=['GET'])
def get_theory_rules():
    """Obtiene la configuración actual de reglas de validación"""
    try:
        rules = state.theory.get_rules()
        return jsonify({'success': True, 'rules': rules})
    except Exception as e:
        logger.error(f"Error getting rules: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/osc/status', methods=['GET'])
def get_osc_status():
    """Obtiene el estado de conexión del cliente OSC"""
    return jsonify(state.osc_client.get_status())

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Endpoint general de estado para el frontend"""
    return jsonify({
        "success": True,
        "osc": state.osc_client.get_status()
    })

@app.route('/api/osc/send', methods=['POST'])
def send_osc_message():
    """Envía un mensaje OSC arbitrario"""
    try:
        data = request.json
        address = data.get('address')
        args = data.get('args', [])
        
        if not address:
            return jsonify({'success': False, 'message': 'Address required'}), 400
            
        if state.osc_client.send_custom(address, *args):
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Failed to send'}), 500
    except Exception as e:
        logger.error(f"Error sending OSC: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/theory/toggle', methods=['POST'])
def toggle_theory_rule():
    """Activa o desactiva una regla específica"""
    try:
        data = request.json
        genre = data.get('genre')
        rule_id = data.get('rule_id')
        active = data.get('active')
        
        if state.theory.toggle_rule(genre, rule_id, active):
            logger.info(f"Regla {rule_id} ({genre}) -> {'Activa' if active else 'Inactiva'}")
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Rule/Genre not found'}), 404
    except Exception as e:
        logger.error(f"Error toggling rule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/theory/add', methods=['POST'])
def add_theory_rule():
    """Añade una regla custom Regex"""
    try:
        data = request.json
        genre = data.get('genre')
        rule_id = data.get('rule_id')
        regex = data.get('regex')
        message = data.get('message', 'Custom Rule Violation')
        
        if state.theory.add_regex_rule(genre, rule_id, regex, message):
            logger.info(f"Nueva Regla Custom añadida a {genre}: {rule_id}")
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"Error adding rule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# --- LATENT SPACE API (Phase 18) ---

@app.route('/api/latent/genres', methods=['GET'])
def get_latent_genres():
    """Obtiene géneros disponibles y sus vectores"""
    try:
        genres = state.latent.get_available_genres()
        vectors = state.latent.genre_vectors
        return jsonify({'success': True, 'genres': genres, 'vectors': vectors})
    except Exception as e:
        logger.error(f"Error getting latent genres: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/latent/blend', methods=['POST'])
def blend_genres():
    """Calcula parámetros interpolados para una mezcla de géneros"""
    try:
        data = request.json
        blend_config = data.get('blend')  # {"techno": 0.7, "ambient": 0.3}
        
        if not blend_config:
            return jsonify({'success': False, 'message': 'Missing blend config'}), 400
        
        result = state.latent.blend_multiple(blend_config)
        if result:
            return jsonify({'success': True, 'params': result})
        return jsonify({'success': False, 'message': 'Invalid blend'}), 400
    except Exception as e:
        logger.error(f"Error blending genres: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/samples/upload', methods=['POST'])
def upload_samples():
    """
    Endpoint para recibir el inventario de samples del usuario.
    Guarda en custom_samples.json y recarga el generador.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400
            
        custom_samples_path = os.path.join(os.path.dirname(__file__), '..', 'generator', 'custom_samples.json')
        
        # Guardar archivo
        with open(custom_samples_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Recargar generador
        state.generator.reload_library()
        
        logger.info(f"Custom samples uploaded: {len(data)} items")
        state.log_activity(f"Librería actualizada: {len(data)} bancos de usuario")
        
        return jsonify({'success': True, 'count': len(data)})
        
    except Exception as e:
        logger.error(f"Error uploading samples: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_pattern():
    """
    Generar nuevo patrón con parámetros especificados.
    """
    try:
        data = request.get_json()
        
        # Extraer parámetros con valores por defecto
        pattern_type = data.get('pattern_type', 'drums')
        density = float(data.get('density', 0.6))
        complexity = float(data.get('complexity', 0.5))
        tempo = int(data.get('tempo', 140))
        style = data.get('style', 'techno')
        blend = data.get('blend', None)  # NEW: {"techno": 0.7, "ambient": 0.3}
        use_ai = data.get('use_ai', state.generator.use_ai)
        temperature = float(data.get('temperature', 1.0))
        musical_friction = float(data.get('musical_friction', 0.2))
        
        # --- LATENT SPACE OVERRIDE (Phase 18) ---
        # Si se proporciona un blend, calcular parámetros interpolados
        if blend:
            latent_params = state.latent.blend_multiple(blend)
            if latent_params:
                # Sobrescribir density/complexity con valores interpolados
                density = latent_params["density_base"]
                complexity = latent_params["complexity_base"]
                tempo = latent_params["tempo_preference"]
                # El estilo se usa para validación (género dominante)
                dominant_genre = max(blend.items(), key=lambda x: x[1])[0]
                style = dominant_genre
                logger.info(f"🌀 Latent Blend: {blend} -> D:{density:.2f}, C:{complexity:.2f}")
        
        # --- CONDUCTOR OVERRIDE ---
        # Si el "Director de Orquesta" está activo, sus parámetros tienen prioridad
        conductor_status = state.conductor.update()
        if conductor_status and conductor_status["status"] == "playing":
            # Mezclar valores del conductor (bias del 80%) con los del usuario (20%)
            # Esto permite "guiar" la canción pero obedece al plan maestro
            c_dens = conductor_status["target_density"]
            c_comp = conductor_status["target_complexity"]
            
            density = (c_dens * 0.8) + (density * 0.2)
            complexity = (c_comp * 0.8) + (complexity * 0.2)
            
            # Loggear intervención del conductor
            logger.info(f"🎻 Conductor Override: {conductor_status['section']} (D:{density:.2f}, C:{complexity:.2f})")

        # Si se proporciona una intención, procesarla con el Oráculo
        intent = data.get('intent')
        intent_mods = None
        if intent:
            intent_mods = state.oracle.interpret(intent)
            # Mezclar offsets del oráculo con los parámetros base
            density = max(0.0, min(1.0, density + intent_mods.get("density_offset", 0.0)))
            complexity = max(0.0, min(1.0, complexity + intent_mods.get("complexity_offset", 0.0)))
            tempo += intent_mods.get("tempo_mod", 0)
            if intent_mods.get("style_pref"):
                style = intent_mods["style_pref"]

        # Generar patrón (ahora devuelve dict con pattern y thoughts)
        result = state.generator.generate(
            pattern_type=pattern_type,
            density=density,
            complexity=complexity,
            tempo=tempo,
            style=style,
            use_ai=use_ai,
            temperature=temperature,
            musical_friction=musical_friction,
            intent_modifiers=intent_mods
        )
        
        # --- THEORY VALIDATION LOOP (Phase 17) ---
        pattern = state.theory.sanitize_pattern(result["pattern"])
        thoughts = result["thoughts"]
        validation_info = {"valid": True, "issues": []}
        
        # Solo validar si se solicita y el motor tiene reglas para este estilo
        # Por defecto validamos 'techno', 'house', etc.
        if use_ai:
            attempts = 0
            max_attempts = 3
            is_valid = False
            
            while attempts < max_attempts:
                # Validar patrón actual
                is_valid, issues = state.theory.validate(pattern, style)
                
                if is_valid:
                    validation_info = {"valid": True, "issues": []}
                    break # Éxito
                else:
                    # Fallo: Reintentar
                    attempts += 1
                    logger.warning(f"⚠️ Theory Violation ({style}): {issues}. Retrying {attempts}/{max_attempts}...")
                    
                    # Regenerar (quizás variando temp o seed)
                    result = state.generator.generate(
                        pattern_type=pattern_type,
                        density=density,
                        complexity=complexity,
                        tempo=tempo,
                        style=style,
                        use_ai=use_ai,
                        temperature=temperature + (attempts * 0.1), # Aumentar caos ligeramente
                        musical_friction=musical_friction,
                        intent_modifiers=intent_mods
                    )
                    pattern = state.theory.sanitize_pattern(result["pattern"])
                    thoughts = result["thoughts"]
            
            # Si tras 3 intentos sigue fallando, marcamos como inválido pero enviamos igual (fallback)
            if not is_valid:
                validation_info = {"valid": False, "issues": issues}
                thoughts.append(f"⚠️ Theory Breaker: {', '.join(issues)}")
        
        # Obtener capas y detectar alucinaciones
        layers = state.generator.get_layers(pattern)
        is_hallucination = any(l.get('is_hallucination', False) for l in layers)
        
        # --- MUSICAL INSIGHT (Theorist Insight) ---
        musical_insight = state.theory.get_musical_insight(pattern, style)
        
        # Guardar último patrón
        state.last_pattern = pattern
        mode_str = "IA" if use_ai else "Reglas"
        temp_str = f" (T={temperature})" if use_ai else ""
        
        # Save to Database History
        state.db.add_history_entry(
            pattern=pattern,
            style=style,
            density=density,
            complexity=complexity,
            tempo=tempo,
            thoughts=thoughts
        )
        
        state.log_activity(f"Patrón generado con {mode_str}{temp_str}: {pattern_type} (densidad={density:.2f}, complejidad={complexity:.2f})")
        
        return jsonify({
            'success': True,
            'pattern': pattern,
            'thoughts': thoughts,
            'insight': musical_insight,
            'mode': mode_str,
            'temperature': temperature if use_ai else None,
            'layers': layers,
            'is_hallucination': is_hallucination,
            'validation': validation_info,
            'timestamp': int(datetime.now().timestamp())
        })
        
    except Exception as e:
        logger.error(f"Error generando patrón: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate/macro', methods=['POST'])
def generate_macro_wave():
    """
    Macro-Generación: Crea un conjunto completo de instrumentos (Drums, Bass, Keys)
    con cohesión musical garantizada.
    """
    try:
        data = request.get_json()
        style = data.get('style', 'techno')
        density = float(data.get('density', 0.6))
        complexity = float(data.get('complexity', 0.5))
        tempo = int(data.get('tempo', 140))
        use_ai = data.get('use_ai', True)
        
        instruments = [
            {"type": "drums", "d": density, "c": complexity},
            {"type": "bass", "d": max(0.2, density - 0.2), "c": complexity},
            {"type": "melody", "d": max(0.1, density - 0.3), "c": min(1.0, complexity + 0.2)}
        ]
        
        macro_results = []
        full_pattern_lines = []
        all_thoughts = ["Macro-Wave Engine: Generando ecosistema musical..."]
        
        for inst in instruments:
            # Generar cada parte
            res = state.generator.generate(
                pattern_type=inst["type"],
                density=inst["d"],
                complexity=inst["c"],
                tempo=tempo,
                style=style,
                use_ai=use_ai
            )
            
            # Sanitizar
            clean_pattern = state.theory.sanitize_pattern(res["pattern"])
            
            # Formatear para el ensamble (d1, d2, d3)
            layer_id = len(macro_results) + 1
            full_pattern_lines.append(f"d{layer_id} $ {clean_pattern}")
            
            macro_results.append({
                "type": inst["type"],
                "pattern": clean_pattern,
                "thoughts": res["thoughts"]
            })
            all_thoughts.extend(res["thoughts"][:1]) # Agregar el pensamiento principal de cada uno
            
        full_ensemble = "\n\n".join(full_pattern_lines)
        state.last_pattern = full_ensemble
        
        # Generar Insight Maestro
        master_insight = f"Ensamble {style.upper()} completo. He equilibrado el bombo con una línea de bajo complementaria y texturas armónicas en el registro superior."
        
        state.log_activity(f"Macro-Wave Generada: {style} (Ensamble de 3 pistas)")

        return jsonify({
            'success': True,
            'pattern': full_ensemble,
            'parts': macro_results,
            'thoughts': all_thoughts,
            'insight': master_insight,
            'timestamp': int(datetime.now().timestamp())
        })
    except Exception as e:
        logger.error(f"Error in macro-generation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/fill', methods=['POST'])
def generate_fill():
    """Genera un patrón de transición (Fill) de alta energía"""
    try:
        data = request.get_json() or {}
        style = data.get('style', 'techno')
        
        result = state.generator.generate_fill(style=style)
        state.log_activity(f"🥁 Fill de transición generado ({style})")
        
        return jsonify({
            'success': True,
            'pattern': result["pattern"],
            'thoughts': result["thoughts"],
            'timestamp': int(datetime.now().timestamp())
        })
    except Exception as e:
        logger.error(f"Error generando fill: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mutate', methods=['POST'])
def mutate_pattern():
    """Muta un patrón existente"""
    try:
        data = request.json
        if not data or 'pattern' not in data:
            return jsonify({'success': False, 'message': 'Falta el patrón actual'}), 400
            
        current_pattern = data.get('pattern')
        strength = data.get('strength', 0.5)
        
        # Mutar usando el generador
        result = state.generator.mutate(current_pattern, strength)
        
        pattern = result["pattern"]
        thoughts = result["thoughts"]
        
        # Obtener capas
        layers = state.generator.get_layers(pattern)
        is_hallucination = any(l.get('is_hallucination', False) for l in layers)
        
        # Guardar como último patrón
        state.last_pattern = pattern
        state.log_activity(f"Patrón mutado (fuerza={strength:.2f}): {pattern}")
        
        return jsonify({
            'success': True,
            'pattern': pattern,
            'thoughts': thoughts,
            'layers': layers,
            'is_hallucination': is_hallucination,
            'timestamp': int(datetime.now().timestamp())
        })
        
    except Exception as e:
        logger.error(f"Error mutando patrón: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/oracle/interpret', methods=['POST'])
def oracle_interpret():
    """Interpretar intención en parámetros técnicos"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        result = state.oracle.interpret(text)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"Error en oráculo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send', methods=['POST'])
def send_pattern():
    """
    Enviar patrón a TidalCycles vía OSC.
    
    Request JSON:
    {
        "channel": "d1",
        "pattern": "sound \"bd sn\""
    }
    
    Response JSON:
    {
        "success": true,
        "message": "Patrón enviado a d1"
    }
    """
    try:
        data = request.get_json()
        
        channel = data.get('channel', 'd1')
        pattern = data.get('pattern', state.last_pattern)
        morph_mode = data.get('morph', False)
        
        # --- MORPH / XFADE LOGIC ---
        # Si morph está activo, sustituir el canal estándar (d1) por la función de transición (xfade 1)
        # Esto asume que el receptor concatena: channel + " $ " + pattern
        if morph_mode:
            import re
            match = re.search(r'd(\d+)', channel)
            if match:
                idx = match.group(1)
                channel = f"xfade {idx}"
                logger.info(f"🌀 Morph Mode: Aplicando transición {channel}")

        if not pattern:
            return jsonify({'success': False, 'error': 'No hay patrón para enviar'}), 400
            
        # Determinar destino (prioridad: request > config > default)
        target_ip = data.get('target_ip')
        target_port = data.get('target_port')
        
        if target_ip and target_port:
             # Si los parámetros son diferentes a los actuales, recrear cliente
             if not state.osc_client or state.osc_client.target_ip != target_ip or state.osc_client.target_port != int(target_port):
                state.osc_client = OSCClient(target_ip=target_ip, target_port=int(target_port))
                logger.info(f"OSC Client actualizado a target específico: {target_ip}:{target_port}")
             client_to_use = state.osc_client
        else:
            # Fallback al cliente global
            if state.osc_client is None:
                config = load_config()
                state.osc_client = OSCClient(
                    target_ip=config['pc']['ip'],
                    target_port=config['pc']['osc_port']
                )
            client_to_use = state.osc_client

        # 1. DETECTAR SI ES UN PATRÓN MULTI-CANAL (MACRO)
        import re
        if re.search(r'd\d+\s+\$', pattern):
            # Es un bloque macro. Dividirlo por dX $
            tracks = []
            # Dividir el bloque manteniendo el identificador (el paréntesis captura el separador)
            raw_tracks = re.split(r'(d\d+\s+\$)', pattern)
            
            # Re-ensamblar: raw_tracks[i] es "d1 $", raw_tracks[i+1] es el código
            for i in range(1, len(raw_tracks), 2):
                if i+1 < len(raw_tracks):
                    ch_id = raw_tracks[i].replace('$', '').strip() # "d1"
                    code = raw_tracks[i+1].strip()
                    # Limpiar posibles restos de otros canales si el split falló por algo
                    code = re.split(r'd\d+\s+\$', code)[0].strip()
                    tracks.append({'channel': ch_id, 'code': code})
            
            # Enviar cada track directamente bypassando get_layers
            sent_count = 0
            for track in tracks:
                success = client_to_use.send_pattern(track['channel'], track['code'])
                if success:
                    sent_count += 1
                    state.log_activity(f"Macro-Pista enviada a {track['channel']}")
            
            return jsonify({
                'success': True,
                'message': f'Macro-Ensamble enviado: {sent_count} pistas activas',
                'macro': True
            })

        # 2. PROCESAR PATRÓN SIMPLE (con orquestación de capas automática)
        layers = state.generator.get_layers(pattern)
        
        # Obtener índice base del canal (ej: d1 -> 1)
        base_match = re.search(r'd(\d+)', channel)
        base_idx = int(base_match.group(1)) if base_match else 1
        
        # Morph check (Phase 34)
        do_morph = data.get('morph', False)
        transition_func = "xfade 4" if do_morph else ""

        # Enviar cada capa
        sent_count = 0
        for layer in layers:
            target_channel = f"d{base_idx + layer['offset']}"
            code = layer['code']
            
            # Aplicar Morph si no es macro (los macro ya tienen dX $ internos)
            if transition_func:
                code = f"{transition_func} $ {code}"

            success = client_to_use.send_pattern(target_channel, code)
            if success:
                sent_count += 1
                state.log_activity(f"Capa [{layer['offset']}] enviada a {target_channel}" + (" (MORPH)" if do_morph else ""))
        
        return jsonify({
            'success': True,
            'message': f'Orquestación Exitosa: {sent_count} pistas activas' if sent_count > 1 else f'Patrón enviado a {target_channel}',
            'layers': [l['code'] for l in layers] if sent_count > 1 else None
        })
            
    except Exception as e:
        logger.error(f"Error enviando patrón: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """
    GET: Obtener configuración actual
    POST: Actualizar configuración
    """
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'config': state.config
        })
    
    else:  # POST
        try:
            data = request.get_json()
            
            # Actualizar configuración
            if 'density' in data:
                state.config['density'] = float(data['density'])
            if 'complexity' in data:
                state.config['complexity'] = float(data['complexity'])
            if 'tempo' in data:
                state.config['tempo'] = int(data['tempo'])
            if 'style' in data:
                state.config['style'] = data['style']
            if 'instruments' in data:
                state.config['instruments'] = data['instruments']
            
            state.log_activity("Configuración actualizada")
            
            return jsonify({
                'success': True,
                'config': state.config
            })
            
        except Exception as e:
            logger.error(f"Error actualizando configuración: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/mode', methods=['GET', 'POST'])
def mode():
    """
    GET: Obtener modo actual
    POST: Cambiar modo de operación
    """
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'mode': state.mode,
            'autonomous_running': state.autonomous_running
        })
    
    else:  # POST
        try:
            data = request.get_json()
            new_mode = data.get('mode')
            
            if new_mode not in ['suggestions', 'autonomous', 'hybrid']:
                return jsonify({
                    'success': False,
                    'error': 'Modo inválido'
                }), 400
            
            state.mode = new_mode
            state.log_activity(f"Modo cambiado a: {new_mode}")
            
            return jsonify({
                'success': True,
                'mode': state.mode
            })
            
        except Exception as e:
            logger.error(f"Error cambiando modo: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Obtener estado completo de la aplicación"""
    osc_status = state.osc_client.get_status() if state.osc_client else {'connected': False}
    
    return jsonify({
        'success': True,
        'mode': state.mode,
        'config': state.config,
        'osc': osc_status,
        'last_pattern': state.last_pattern,
        'autonomous_running': state.autonomous_running,
        'activity_log': state.activity_log[-10:]  # Últimas 10 entradas
    })


@app.route('/api/favorites', methods=['GET', 'POST', 'DELETE'])
def favorites():
    """
    GET: Obtener lista de patrones favoritos (desde DB)
    POST: Añadir patrón a favoritos (guardar en DB)
    DELETE: Eliminar patrón de favoritos
    """
    if request.method == 'GET':
        try:
            favs = state.db.get_favorites()
            return jsonify({
                'success': True,
                'favorites': favs
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            pattern = data.get('pattern')
            name = data.get('name', f"Favorite {datetime.now().strftime('%H:%M')}")
            style = data.get('style', 'unknown')
            tags = data.get('tags', '')
            metadata = data.get('metadata', {})
            
            # Support legacy 'type'
            if 'type' in data and style == 'unknown':
                style = data['type']
            
            if not pattern:
                return jsonify({'success': False, 'message': 'Missing pattern'}), 400
            
            new_id = state.db.add_favorite(pattern, name, style, tags, metadata)
            
            if new_id:
                state.log_activity(f"Favorito guardado: {name}")
                return jsonify({'success': True, 'id': new_id})
            else:
                return jsonify({'success': False, 'message': 'Failed to save'}), 500
                
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
            
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            fav_id = data.get('id')
            
            # Legacy fallback: Delete by pattern string if ID not provided
            if not fav_id and 'pattern' in data:
                 # We would need to search, but for now let's enforce ID usage or return 400?
                 # Actually, let's just log a warning and return error. Frontend must use ID.
                 # Wait, if I break FE, I must fix FE.
                 return jsonify({'success': False, 'message': 'Please provide ID for deletion'}), 400
            
            if state.db.delete_favorite(fav_id):
                state.log_activity(f"Favorito eliminado: {fav_id}")
                return jsonify({'success': True})
            return jsonify({'success': False, 'message': 'Not found'}), 404
        except Exception as e:
             return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Obtener historial desde la base de datos"""
    try:
        limit = int(request.args.get('limit', 50))
        history = state.db.get_history(limit)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/data/import', methods=['POST'])
def import_data():
    """Importar datos masivos desde localStorage (Migración)"""
    try:
        data = request.get_json()
        history = data.get('history', [])
        favorites = data.get('favorites', [])
        
        h_count, f_count = state.db.import_client_data(history, favorites)
        
        state.log_activity(f"📦 Migración de datos: {h_count} historial, {f_count} favoritos.")
        
        return jsonify({
            'success': True,
            'imported': {
                'history': h_count,
                'favorites': f_count
            }
        })
    except Exception as e:
        logger.error(f"Error import data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/retrain', methods=['POST'])
def retrain_model():
    """
    Re-entrenar modelo de IA con corpus actualizado (incluyendo favoritos)
    """
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'generator'))
        from markov_model import MarkovModel
        
        # Rutas
        corpus_file = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'patterns.txt')
        favorites_file = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'favorites.json')
        model_file = os.path.join(os.path.dirname(__file__), '..', 'generator', 'markov_model.json')
        
        # Cargar corpus base
        patterns = []
        if os.path.exists(corpus_file):
            with open(corpus_file, 'r') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Añadir favoritos (extraer solo los patrones)
        if os.path.exists(favorites_file):
            with open(favorites_file, 'r') as f:
                favorites_data = json.load(f)
                # Extraer patrones de objetos JSON
                favorite_patterns = [fav['pattern'] for fav in favorites_data if 'pattern' in fav]
                patterns.extend(favorite_patterns)
        
        if not patterns:
            return jsonify({
                'success': False,
                'error': 'No hay patrones para entrenar'
            }), 400
        
        # Entrenar modelo
        state.log_activity(f"Re-entrenando modelo con {len(patterns)} patrones...")
        
        model = MarkovModel(order=2)
        model.train(patterns)
        model.save(model_file)
        
        # Recargar modelo en el generador
        state.generator._init_markov_model()
        
        state.log_activity(f"✓ Modelo re-entrenado exitosamente")
        
        return jsonify({
            'success': True,
            'message': f'Modelo re-entrenado con {len(patterns)} patrones',
            'pattern_count': len(patterns)
        })
        
    except Exception as e:
        logger.error(f"Error re-entrenando modelo: {e}")
        state.log_activity(f"✗ Error re-entrenando modelo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/train/evolve', methods=['POST'])
def train_evolve():
    """
    Ejecutar una ronda de entrenamiento evolutivo (Nightly Build)
    """
    try:
        from evolutionary_trainer import EvolutionaryTrainer
        
        # Usar generador existente en el estado
        trainer = EvolutionaryTrainer(state.generator)
        
        # Leer parametros opcionales
        data = request.get_json() or {}
        batch = data.get('batch_size', 50)
        top_k = data.get('top_k', 10)
        
        state.log_activity(f"🧬 Iniciando evolución: {batch} candidatos...")
        
        result = trainer.run_evolution(batch_size=batch, top_k=top_k)
        
        # Si hubo éxito, re-inicializar el generador para que aprenda lo nuevo inmediatamente
        if result['survivors'] > 0:
            state.generator._init_markov_model()
            state.log_activity("Cerebro actualizado con nuevos patrones.")
            
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error en evolución: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/train/scavenge', methods=['POST'])
def train_scavenge():
    """
    Recolectar patrones desde fuentes externas (Web Scraping)
    """
    try:
        from scavenger_tool import ScavengerTool
        
        # Nueva ruta dentro de raspberry-pi/
        sources_file = os.path.join(os.path.dirname(__file__), '..', 'sources.txt')
        
        if not os.path.exists(sources_file):
            return jsonify({'success': False, 'error': f'Archivo de fuentes no encontrado en {sources_file}'}), 404
            
        with open(sources_file, 'r') as f:
            sources = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        if not sources:
            return jsonify({'success': False, 'error': 'No hay URLs en sources.txt'}), 400
            
        state.log_activity(f"🕷️ Iniciando recolección desde {len(sources)} fuentes...")
        
        scavenger = ScavengerTool()
        result = scavenger.run_bulk(sources)
        
        if result['total_added'] > 0:
            state.generator._init_markov_model()
            state.log_activity(f"Cerebro ampliado con {result['total_added']} patrones externos.")
            
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error en Scavenge: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/evolution', methods=['GET', 'POST'])
def config_evolution():
    """
    Gestionar la configuración del entrenamiento evolutivo
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config_evolution.json')
    
    if request.method == 'GET':
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return jsonify(json.load(f))
            else:
                return jsonify({
                    "weights": {"density": 1.0, "variety": 1.0, "complexity": 1.0, "euclidean": 1.0},
                    "params": {"temperature": 1.2, "batch_size": 50, "top_k": 10, "strictness": 0},
                    "filters": {"genre": "all", "instrument": "all"}
                })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
            
    elif request.method == 'POST':
        try:
            new_config = request.get_json()
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=4)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/brain/graph', methods=['GET'])
def brain_graph():
    """
    Exportar el modelo Markov como un grafo (nodos y enlaces) para visualización
    """
    try:
        # Intentar obtener el grafo del modelo Markov
        if hasattr(state.generator.markov, 'to_graph_json'):
            graph_data = state.generator.markov.to_graph_json()
        else:
            # Fallback si el método no existe aún
            graph_data = {
                "nodes": [{"id": "root", "label": "Brain"}],
                "links": []
            }
        return jsonify(graph_data)
    except Exception as e:
        logger.error(f"Error exportando grafo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/presets', methods=['GET', 'POST', 'DELETE'])
def presets():
    """
    GET: Obtener lista de presets
    POST: Guardar nuevo preset
    DELETE: Eliminar preset
    """
    presets_file = os.path.join(os.path.dirname(__file__), '..', 'presets.json')
    
    if request.method == 'GET':
        try:
            if os.path.exists(presets_file):
                with open(presets_file, 'r') as f:
                    presets_data = json.load(f)
            else:
                presets_data = []
            
            return jsonify({
                'success': True,
                'presets': presets_data
            })
        except Exception as e:
            logger.error(f"Error leyendo presets: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            name = data.get('name', '').strip()
            
            if not name:
                return jsonify({'success': False, 'error': 'Nombre vacío'}), 400
            
            # Leer presets existentes
            presets_data = []
            if os.path.exists(presets_file):
                with open(presets_file, 'r') as f:
                    presets_data = json.load(f)
            
            # Verificar si ya existe
            if any(p['name'] == name for p in presets_data):
                return jsonify({'success': False, 'error': 'Preset ya existe'}), 400
            
            # Crear nuevo preset
            new_preset = {
                'name': name,
                'genMode': data.get('genMode', 'rules'),
                'patternType': data.get('patternType', 'drums'),
                'density': data.get('density', 0.6),
                'complexity': data.get('complexity', 0.5),
                'tempo': data.get('tempo', 140),
                'style': data.get('style', 'techno'),
                'temperature': data.get('temperature', 1.0),
                'timestamp': int(datetime.now().timestamp())
            }
            presets_data.append(new_preset)
            
            # Guardar
            with open(presets_file, 'w') as f:
                json.dump(presets_data, f, indent=2)
            
            state.log_activity(f"Preset '{name}' guardado")
            
            return jsonify({'success': True, 'message': 'Preset guardado'})
            
        except Exception as e:
            logger.error(f"Error guardando preset: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            name = data.get('name', '').strip()
            
            if not name:
                return jsonify({'success': False, 'error': 'Nombre vacío'}), 400
            
            if not os.path.exists(presets_file):
                return jsonify({'success': False, 'error': 'No hay presets'}), 404
            
            with open(presets_file, 'r') as f:
                presets_data = json.load(f)
            
            original_count = len(presets_data)
            presets_data = [p for p in presets_data if p['name'] != name]
            
            if len(presets_data) == original_count:
                return jsonify({'success': False, 'error': 'Preset no encontrado'}), 404
            
            with open(presets_file, 'w') as f:
                json.dump(presets_data, f, indent=2)
            
            state.log_activity(f"Preset '{name}' eliminado")
            
            return jsonify({'success': True, 'message': 'Preset eliminado'})
            
        except Exception as e:
            logger.error(f"Error eliminando preset: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history', methods=['GET', 'POST', 'DELETE'])
def history():
    """
    GET: Obtener historial de patrones
    POST: Añadir patrón al historial
    DELETE: Limpiar historial
    """
    history_file = os.path.join(os.path.dirname(__file__), '..', 'history.json')
    MAX_HISTORY = 100
    
    if request.method == 'GET':
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
            else:
                history_data = []
            
            return jsonify({
                'success': True,
                'history': history_data
            })
        except Exception as e:
            logger.error(f"Error leyendo historial: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            pattern = data.get('pattern', '').strip()
            
            if not pattern:
                return jsonify({'success': False, 'error': 'Patrón vacío'}), 400
            
            # Leer historial existente
            history_data = []
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
            
            # Añadir nuevo patrón
            new_entry = {
                'pattern': pattern,
                'type': data.get('type', 'unknown'),
                'mode': data.get('mode', 'rules'),
                'temperature': data.get('temperature'),
                'timestamp': int(datetime.now().timestamp())
            }
            history_data.insert(0, new_entry)  # Añadir al principio
            
            # Mantener solo últimos MAX_HISTORY
            history_data = history_data[:MAX_HISTORY]
            
            # Guardar
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
            return jsonify({'success': True, 'message': 'Añadido al historial'})
            
        except Exception as e:
            logger.error(f"Error añadiendo al historial: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            # Limpiar historial
            if os.path.exists(history_file):
                with open(history_file, 'w') as f:
                    json.dump([], f)
            
            state.log_activity("Historial limpiado")
            
            return jsonify({'success': True, 'message': 'Historial limpiado'})
            
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-batch', methods=['POST'])
def generate_batch():
    """
    Generar múltiples patrones de una vez
    
    Request JSON:
    {
        "count": 10,
        "type": "drums",
        "density": 0.7,
        ...
    }
    """
    try:
        data = request.get_json()
        count = data.get('count', 10)
        
        if count < 1 or count > 50:
            return jsonify({'success': False, 'error': 'Count debe estar entre 1 y 50'}), 400
        
        # Extraer parámetros
        pattern_type = data.get('type', 'drums')
        density = data.get('density', state.config['density'])
        complexity = data.get('complexity', state.config['complexity'])
        tempo = data.get('tempo', state.config['tempo'])
        style = data.get('style', state.config['style'])
        use_ai = data.get('use_ai', False)
        temperature = data.get('temperature', 1.0)
        
        # Generar múltiples patrones
        patterns = []
        for i in range(count):
            result = state.generator.generate(
                pattern_type=pattern_type,
                density=density,
                complexity=complexity,
                tempo=tempo,
                style=style,
                use_ai=use_ai,
                temperature=temperature
            )
            patterns.append({
                'pattern': result["pattern"],
                'index': i + 1
            })
        
        mode_str = "IA" if use_ai else "Reglas"
        state.log_activity(f"Generados {count} patrones en lote ({mode_str})")
        
        return jsonify({
            'success': True,
            'patterns': patterns,
            'count': len(patterns),
            'mode': mode_str
        })
        
    except Exception as e:
        logger.error(f"Error generando lote: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate/morph', methods=['POST'])
def generate_morph():
    """
    Interpolar entre dos patrones
    """
    try:
        data = request.get_json()
        pattern_a = data.get('pattern_a')
        pattern_b = data.get('pattern_b')
        ratio = float(data.get('ratio', 0.5))

        if not pattern_a or not pattern_b:
            return jsonify({'success': False, 'error': 'Se requieren dos patrones'}), 400

        # Simple morphing: interpolate between patterns
        # If ratio is 0, use pattern_a; if 1, use pattern_b; if 0.5, mix both
        if ratio <= 0.2:
            morphed_pattern = pattern_a
        elif ratio >= 0.8:
            morphed_pattern = pattern_b
        else:
            # Mix patterns by alternating lines
            lines_a = pattern_a.strip().split('\n')
            lines_b = pattern_b.strip().split('\n')
            
            # Determine which pattern to favor based on ratio
            if ratio < 0.5:
                # Favor pattern A
                base = lines_a
                alt = lines_b
                mix_ratio = ratio * 2  # Scale 0.2-0.5 to 0.4-1.0
            else:
                # Favor pattern B
                base = lines_b
                alt = lines_a
                mix_ratio = (1 - ratio) * 2  # Scale 0.5-0.8 to 0.6-0.4
            
            # Interleave lines based on ratio
            morphed_lines = []
            for i, line in enumerate(base):
                morphed_lines.append(line)
                # Add alt line probabilistically
                if i < len(alt) and (i % 2 == 0 if mix_ratio > 0.5 else i % 3 == 0):
                    morphed_lines.append(alt[i])
            
            morphed_pattern = '\n'.join(morphed_lines)
        
        state.log_activity(f"Morfado rítmico aplicado (ratio={ratio:.2f})")
        
        return jsonify({
            'success': True,
            'pattern': morphed_pattern,
            'thoughts': [],
            'ratio': ratio
        })
    except Exception as e:
        logger.error(f"Error en morfado: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop():
    """Detener canal(es) específico(s)"""
    try:
        data = request.get_json()
        channel = data.get('channel', 'all')
        
        if state.osc_client is None:
            return jsonify({
                'success': False,
                'error': 'OSC client no inicializado'
            }), 400
        
        if channel == 'all':
            success = state.osc_client.stop_all()
            state.log_activity("Todos los canales detenidos")
        else:
            success = state.osc_client.stop_channel(channel)
            state.log_activity(f"Canal {channel} detenido")
        
        return jsonify({
            'success': success
        })
        
    except Exception as e:
        logger.error(f"Error deteniendo canal: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/corpus-stats', methods=['GET'])
def corpus_stats():
    """
    Analizar corpus y retornar estadísticas
    """
    try:
        import sys
        from collections import Counter
        import re
        
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'generator'))
        
        # Rutas
        corpus_file = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'patterns.txt')
        favorites_file = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'favorites.json')
        
        # Cargar patrones
        patterns = []
        if os.path.exists(corpus_file):
            with open(corpus_file, 'r') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Añadir favoritos
        if os.path.exists(favorites_file):
            with open(favorites_file, 'r') as f:
                favorites_data = json.load(f)
                favorite_patterns = [fav['pattern'] for fav in favorites_data if 'pattern' in fav]
                patterns.extend(favorite_patterns)
        
        if not patterns:
            return jsonify({
                'success': False,
                'error': 'No hay patrones en el corpus'
            }), 400
        
        # Análisis
        total_patterns = len(patterns)
        
        # Contar samples más usados
        samples = []
        for pattern in patterns:
            # Buscar sound "..."
            sound_matches = re.findall(r'sound\s+"([^"]+)"', pattern)
            samples.extend(sound_matches)
        
        sample_counter = Counter(samples)
        top_samples = sample_counter.most_common(10)
        
        # Contar efectos más usados
        effects = []
        effect_keywords = ['lpf', 'hpf', 'delay', 'reverb', 'crush', 'distort', 'gain', 'pan', 'speed', 'slow', 'fast']
        for pattern in patterns:
            for effect in effect_keywords:
                if effect in pattern:
                    effects.append(effect)
        
        effect_counter = Counter(effects)
        top_effects = effect_counter.most_common(10)
        
        # Longitud promedio
        avg_length = sum(len(p) for p in patterns) / len(patterns)
        
        # Distribución por tipo (si están categorizados en favoritos)
        type_distribution = {}
        if os.path.exists(favorites_file):
            with open(favorites_file, 'r') as f:
                favorites_data = json.load(f)
                for fav in favorites_data:
                    fav_type = fav.get('type', 'unknown')
                    type_distribution[fav_type] = type_distribution.get(fav_type, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_patterns': total_patterns,
                'avg_length': round(avg_length, 1),
                'top_samples': [{'name': s, 'count': c} for s, c in top_samples],
                'top_effects': [{'name': e, 'count': c} for e, c in top_effects],
                'type_distribution': type_distribution
            }
        })
        
    except Exception as e:
        logger.error(f"Error analizando corpus: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# ADMIN ROUTES
# ==========================================

@app.route('/api/system/stats', methods=['GET'])
def system_stats():
    """Retornar estadísticas del sistema (CPU, RAM, Temp, Disk)"""
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # RAM
        ram = psutil.virtual_memory()
        ram_percent = ram.percent
        ram_used = round(ram.used / (1024**2), 1) # MB
        ram_total = round(ram.total / (1024**2), 1) # MB
        
        # Temperatura (Raspberry Pi specific)
        temp = "N/A"
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                temp = temps['cpu_thermal'][0].current
            elif 'coretemp' in temps: # PC Fallback
                temp = temps['coretemp'][0].current
        except:
            pass
            
        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = str(datetime.now() - boot_time).split('.')[0]
        
        return jsonify({
            'success': True,
            'stats': {
                'cpu': cpu_percent,
                'ram_percent': ram_percent,
                'ram_used': ram_used,
                'ram_total': ram_total,
                'temp': temp,
                'disk': disk_percent,
                'uptime': uptime
            }
        })
        
    except ImportError:
        return jsonify({'success': False, 'error': 'psutil no instalado'}), 500
    except Exception as e:
        logger.error(f"Error leyendo sys stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/system/logs', methods=['GET'])
def system_logs():
    """Retornar log de actividad interno"""
    return jsonify({
        'success': True,
        'logs': state.activity_log
    })

@app.route('/api/system/restart', methods=['POST'])
def system_restart():
    """Reiniciar servicio (hacky method)"""
    try:
        state.log_activity("REINICIANDO SERVIDOR...")
        
        # En un servicio systemd, si el proceso muere, systemd lo reinicia.
        # Así que matar el proceso es una forma efectiva de reiniciar.
        def kill_later():
            import time
            time.sleep(1)
            os._exit(1)
            
        import threading
        threading.Thread(target=kill_later).start()
        
        return jsonify({'success': True, 'message': 'Reiniciando...'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/system-config', methods=['GET', 'POST'])
def system_config():
    """
    Gestionar configuración del sistema (IP destino, puerto, etc)
    """
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    
    if request.method == 'GET':
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {'pc': {'ip': '127.0.0.1', 'osc_port': 6010}}
            
            return jsonify({'success': True, 'config': config})
        except Exception as e:
            logger.error(f"Error leyendo system config: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            target_ip = data.get('ip')
            target_port = data.get('port')
            
            if not target_ip:
                return jsonify({'success': False, 'error': 'IP requerida'}), 400
            
            # Cargar config actual
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {'pc': {'ip': '127.0.0.1', 'osc_port': 6010}}
            
            # Actualizar
            config['pc']['ip'] = target_ip
            if target_port:
                config['pc']['osc_port'] = int(target_port)
            
            # Guardar
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Reiniciar cliente OSC con nueva IP
            state.osc_client = OSCClient(
                target_ip=config['pc']['ip'],
                target_port=config['pc']['osc_port']
            )
            
            state.log_activity(f"Configuración actualizada: IP PC = {target_ip}")
            
            return jsonify({'success': True, 'message': 'Configuración guardada'})
            
        except Exception as e:
            logger.error(f"Error guardando system config: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jam-session', methods=['POST'])
def jam_session():
    """
    Iniciar sesión de jam (generación continua)
    
    Request JSON:
    {
        "duration": 10,  # minutos
        "interval": 8,   # segundos entre patrones
        "channels": ["d1", "d2"],
        "types": ["drums", "bass"]
    }
    """
    try:
        data = request.get_json()
        
        duration = data.get('duration', 5)  # minutos
        interval = data.get('interval', 8)  # segundos
        channels = data.get('channels', ['d1'])
        pattern_types = data.get('types', ['drums', 'bass', 'melody'])
        
        # Validar
        if duration < 1 or duration > 60:
            return jsonify({'success': False, 'error': 'Duración debe estar entre 1 y 60 minutos'}), 400
        
        if interval < 2 or interval > 60:
            return jsonify({'success': False, 'error': 'Intervalo debe estar entre 2 y 60 segundos'}), 400
        
        # Calcular cuántos patrones generar
        total_seconds = duration * 60
        pattern_count = total_seconds // interval
        
        state.log_activity(f"Jam session iniciada: {duration}min, {interval}s intervalo, {len(channels)} canales")
        
        # Nota: La generación continua se haría con threading o async
        # Por ahora retornamos la configuración
        return jsonify({
            'success': True,
            'message': 'Jam session configurada',
            'config': {
                'duration': duration,
                'interval': interval,
                'channels': channels,
                'types': pattern_types,
                'estimated_patterns': pattern_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error en jam session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/backup', methods=['GET'])
def create_backup():
    """
    Crear backup de todos los datos
    """
    try:
        import zipfile
        from datetime import datetime
        
        # Crear directorio de backups si no existe
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nombre del backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'tidalai_backup_{timestamp}.zip'
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Archivos a incluir
        files_to_backup = [
            ('favorites.json', os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'favorites.json')),
            ('presets.json', os.path.join(os.path.dirname(__file__), '..', 'presets.json')),
            ('history.json', os.path.join(os.path.dirname(__file__), '..', 'history.json')),
            ('markov_model.json', os.path.join(os.path.dirname(__file__), '..', 'generator', 'markov_model.json'))
        ]
        
        # Crear ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, filepath in files_to_backup:
                if os.path.exists(filepath):
                    zipf.write(filepath, filename)
        
        state.log_activity(f"Backup creado: {backup_name}")
        
        return jsonify({
            'success': True,
            'message': 'Backup creado',
            'filename': backup_name,
            'path': backup_path,
            'size': os.path.getsize(backup_path)
        })
        
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/restore', methods=['POST'])
def restore_backup():
    """
    Restaurar desde backup
    
    Request: multipart/form-data con archivo ZIP
    """
    try:
        import zipfile
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        if not file.filename.endswith('.zip'):
            return jsonify({'success': False, 'error': 'El archivo debe ser ZIP'}), 400
        
        # Guardar temporalmente
        temp_path = os.path.join(os.path.dirname(__file__), '..', 'temp_backup.zip')
        file.save(temp_path)
        
        # Extraer y restaurar
        files_restored = []
        with zipfile.ZipFile(temp_path, 'r') as zipf:
            for filename in zipf.namelist():
                if filename == 'favorites.json':
                    target = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'favorites.json')
                elif filename == 'presets.json':
                    target = os.path.join(os.path.dirname(__file__), '..', 'presets.json')
                elif filename == 'history.json':
                    target = os.path.join(os.path.dirname(__file__), '..', 'history.json')
                elif filename == 'markov_model.json':
                    target = os.path.join(os.path.dirname(__file__), '..', 'generator', 'markov_model.json')
                else:
                    continue
                
                # Extraer
                with zipf.open(filename) as source, open(target, 'wb') as dest:
                    dest.write(source.read())
                
                files_restored.append(filename)
        
        # Eliminar temporal
        os.remove(temp_path)
        
        # Recargar modelo si fue restaurado
        if 'markov_model.json' in files_restored:
            state.generator._init_markov_model()
        
        state.log_activity(f"Backup restaurado: {len(files_restored)} archivos")
        
        return jsonify({
            'success': True,
            'message': 'Backup restaurado',
            'files_restored': files_restored
        })
        
    except Exception as e:
        logger.error(f"Error restaurando backup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export-tidal', methods=['POST'])
def export_tidal():
    """
    Exportar patrones a archivo .tidal
    
    Request JSON:
    {
        "source": "history" | "favorites" | "session",
        "include_comments": true,
        "group_by_type": true
    }
    """
    try:
        from datetime import datetime
        
        data = request.get_json()
        source = data.get('source', 'history')
        include_comments = data.get('include_comments', True)
        group_by_type = data.get('group_by_type', True)
        
        patterns = []
        
        # Cargar patrones según fuente
        if source == 'history':
            history_file = os.path.join(os.path.dirname(__file__), '..', 'history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                    patterns = [{'pattern': h['pattern'], 'type': h.get('type', 'unknown'), 'mode': h.get('mode', 'unknown')} for h in history_data]
        
        elif source == 'favorites':
            favorites_file = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'favorites.json')
            if os.path.exists(favorites_file):
                with open(favorites_file, 'r') as f:
                    favorites_data = json.load(f)
                    patterns = [{'pattern': fav['pattern'], 'type': fav.get('type', 'unknown'), 'mode': 'Favorito'} for fav in favorites_data]
        
        if not patterns:
            return jsonify({'success': False, 'error': 'No hay patrones para exportar'}), 400
        
        # Generar contenido .tidal
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"-- TidalAI Companion Export\n"
        content += f"-- Generated: {timestamp}\n"
        content += f"-- Source: {source}\n"
        content += f"-- Total patterns: {len(patterns)}\n\n"
        
        if group_by_type:
            # Agrupar por tipo
            by_type = {}
            for p in patterns:
                ptype = p['type']
                if ptype not in by_type:
                    by_type[ptype] = []
                by_type[ptype].append(p)
            
            for ptype, plist in sorted(by_type.items()):
                content += f"-- {'='*40}\n"
                content += f"-- {ptype.upper()} PATTERNS\n"
                content += f"-- {'='*40}\n\n"
                
                for i, p in enumerate(plist, 1):
                    if include_comments:
                        content += f"-- Pattern {i} ({p['type']}, {p['mode']})\n"
                    content += f"{p['pattern']}\n\n"
        else:
            # Sin agrupar
            for i, p in enumerate(patterns, 1):
                if include_comments:
                    content += f"-- Pattern {i} ({p['type']}, {p['mode']})\n"
                content += f"{p['pattern']}\n\n"
        
        state.log_activity(f"Exportados {len(patterns)} patrones a .tidal")
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': f'tidalai_export_{source}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tidal',
            'pattern_count': len(patterns)
        })
        
    except Exception as e:
        logger.error(f"Error exportando a .tidal: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/song-templates', methods=['GET'])
def get_song_templates():
    """
    Obtener lista de templates de canciones
    """
    try:
        templates_file = os.path.join(os.path.dirname(__file__), '..', 'song_templates.json')
        
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            # Templates por defecto si no existe el archivo
            templates = []
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Error cargando templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/generate-song', methods=['POST'])
def generate_song():
    """
    Generar canción completa desde template
    
    Request JSON:
    {
        "template_name": "Techno Track",
        "use_ai": true,
        "temperature": 1.0
    }
    """
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        use_ai = data.get('use_ai', True)
        temperature = data.get('temperature', 1.0)
        
        # Cargar template
        templates_file = os.path.join(os.path.dirname(__file__), '..', 'song_templates.json')
        
        if not os.path.exists(templates_file):
            return jsonify({'success': False, 'error': 'No hay templates disponibles'}), 400
        
        with open(templates_file, 'r') as f:
            templates = json.load(f)
        
        template = next((t for t in templates if t['name'] == template_name), None)
        
        if not template:
            return jsonify({'success': False, 'error': 'Template no encontrado'}), 404
        
        # Generar patrones para cada sección
        song_content = f"-- {template['name']}\n"
        song_content += f"-- Generated by TidalAI Companion\n\n"
        
        all_patterns = []
        
        for section in template['sections']:
            song_content += f"-- {section['name']} ({section['duration']} bars)\n"
            song_content += f"-- {'='*40}\n\n"
            
            for channel, config in section['channels'].items():
                # Generar patrón
                pattern = state.generator.generate(
                    pattern_type=config['type'],
                    density=config['density'],
                    complexity=state.config['complexity'],
                    tempo=state.config['tempo'],
                    style=state.config['style'],
                    use_ai=use_ai,
                    temperature=temperature
                )
                
                song_content += f"{channel} $ {pattern}\n"
                all_patterns.append({
                    'section': section['name'],
                    'channel': channel,
                    'pattern': pattern,
                    'type': config['type']
                })
            
            song_content += f"\n"
        
        state.log_activity(f"Canción generada: {template_name} ({len(all_patterns)} patrones)")
        
        return jsonify({
            'success': True,
            'song_content': song_content,
            'template_name': template_name,
            'patterns': all_patterns,
            'sections': len(template['sections'])
        })
        
    except Exception as e:
        logger.error(f"Error generando canción: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/download-kit', methods=['GET'])
def download_kit():
    """
    Descargar Kit de Instalación Universal
    Empaqueta: osc_receiver.scd + scripts de instalación
    """
    try:
        # Rutas relativas
        pc_side_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'pc-side')
        
        files_to_pack = [
            ('start_listening.scd', os.path.join(pc_side_dir, 'osc_receiver.scd')), # Rename for clarity
            ('install_windows.ps1', os.path.join(pc_side_dir, 'install_companion_win.ps1')),
            ('install_mac.sh', os.path.join(pc_side_dir, 'install_companion_mac.sh'))
        ]
        
        # Crear ZIP en memoria
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for zip_name, disk_path in files_to_pack:
                if os.path.exists(disk_path):
                    # Forzar EOL universales o binarios? Text es fine.
                    zf.write(disk_path, zip_name)
                    
            # Añadir README rápido
            readme_content = """
            TidalAI Companion Client Kit
            ============================
            
            1. Windows: Ejecuta 'install_windows.ps1' (Click derecho -> Ejecutar con PowerShell)
            2. Mac: Abre terminal y ejecuta 'sh install_mac.sh'
            3. Manual: Copia 'start_listening.scd' a tu carpeta de inicio de SuperCollider.
            
            ACCESO WEB:
            -----------
            Una vez conectado a la misma red, usa los accesos directos incluidos
            o navega a: http://tidal.local:5000
            """
            zf.writestr('README_INSTALL.txt', readme_content)
            
            # Añadir Accesos Directos Web (.url)
            # Esto permite "abrir" la Pi desde el PC sin instalar nada
            shortcut_dashboard = "[InternetShortcut]\nURL=http://tidal.local:5000"
            shortcut_admin = "[InternetShortcut]\nURL=http://tidal.local:5000/admin"
            
            zf.writestr('TidalAI Dashboard.url', shortcut_dashboard)
            zf.writestr('TidalAI Admin.url', shortcut_admin)
            
        memory_file.seek(0)
        
        from flask import send_file
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='tidalai_client_setup.zip'
        )
            
    except Exception as e:
        logger.error(f"Error generando kit: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/samples', methods=['GET', 'POST'])
def handle_samples():
    """
    GET: Obtener librería de samples
    POST: Actualizar librería de samples
    """
    samples_file = os.path.join(os.path.dirname(__file__), '..', 'samples.json')
    
    if request.method == 'GET':
        try:
            if os.path.exists(samples_file):
                with open(samples_file, 'r') as f:
                    samples = json.load(f)
            else:
                # Si no existe, devolver valores actuales del generador
                # Esto es un fallback, pero idealmente samples.json debería existir
                samples = {
                    "drums": state.generator.drum_samples,
                    "bass": state.generator.bass_samples,
                    "melody": state.generator.melody_samples,
                    "percussion": state.generator.perc_samples,
                    "fx": state.generator.fx_samples
                }
            return jsonify({'success': True, 'samples': samples})
        except Exception as e:
            logger.error(f"Error leyendo samples: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
            
    elif request.method == 'POST':
        try:
            new_samples = request.get_json()
            if not new_samples:
                return jsonify({'success': False, 'error': 'Datos inválidos'}), 400
            
            # Guardar en archivo
            with open(samples_file, 'w') as f:
                json.dump(new_samples, f, indent=2)
            
            # Recargar generador
            state.generator._init_pattern_library()
            state.log_activity("Librería de samples actualizada")
            
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error guardando samples: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/samples/suggest', methods=['POST'])
def suggest_samples():
    """Analizar patrón y sugerir samples similares"""
    try:
        data = request.get_json()
        pattern = data.get('pattern')
        count = int(data.get('count', 4))
        
        if not pattern:
            return jsonify({'success': False, 'error': 'Patrón no proporcionado'}), 400
            
        suggestions = state.generator.suggest_samples(pattern, count=count)
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    except Exception as e:
        logger.error(f"Error sugiriendo samples: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/samples/replace', methods=['POST'])
def replace_sample():
    """Reemplazar sample en patrón"""
    try:
        data = request.get_json()
        pattern = data.get('pattern')
        old_sample = data.get('old_sample')
        new_sample = data.get('new_sample')
        
        if not all([pattern, old_sample, new_sample]):
            return jsonify({'success': False, 'error': 'Faltan parámetros'}), 400
            
        new_pattern = state.generator.replace_sample(pattern, old_sample, new_sample)
        return jsonify({
            'success': True,
            'pattern': new_pattern
        })
    except Exception as e:
        logger.error(f"Error reemplazando sample: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/samples/index', methods=['POST'])
def reindex_samples():
    """Forzar re-indexación de la librería"""
    try:
        # Ejecutar el scanner
        scanner_path = os.path.join(os.path.dirname(__file__), '..', 'generator', 'sample_scanner.py')
        import subprocess
        result = subprocess.run([sys.executable, scanner_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Recargar en el generador
            state.generator.reload_library()
            state.log_activity("Librería de samples re-indexada")
            return jsonify({
                'success': True, 
                'message': 'Re-indexación completada',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False, 
                'error': result.stderr
            }), 500
    except Exception as e:
        logger.error(f"Error re-indexando samples: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/evolution/run', methods=['POST'])
def run_evolution_manual():
    """Trigger manual para el proceso de evolución"""
    try:
        from evolutionary_trainer import EvolutionaryTrainer
        trainer = EvolutionaryTrainer(state.generator)
        
        # Cargar config si existe
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config_evolution.json')
        weights = {}
        if os.path.exists(config_path):
             with open(config_path, 'r') as f:
                 config = json.load(f)
                 weights = config.get('weights', {})

        result = trainer.run_evolution(weights=weights)
        
        if result['survivors'] > 0:
            state.generator._init_markov_model()
            state.log_activity("🧬 [Manual] Cerebro actualizado tras evolución.")
            
        return jsonify({'success': True, 'survivors': result['survivors']})
        
    except Exception as e:
        logger.error(f"Error manual evolution: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Cargar configuración
    config = load_config()
    
    # Iniciar servidor
    host = '0.0.0.0'  # Accesible desde red local
    port = config['raspberry_pi']['flask_port']
    
    logger.info(f"=== TidalAI Companion Server ===")
    logger.info(f"Iniciando en http://{host}:{port}")
    logger.info(f"OSC target: {config['pc']['ip']}:{config['pc']['osc_port']}")
    
    app.run(host=host, port=port, debug=True)
