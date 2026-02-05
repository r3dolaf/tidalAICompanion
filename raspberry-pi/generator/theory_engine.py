"""
Theory Engine (Fase 17b)
Motor de validación lógica-musical con soporte para reglas dinámicas JSON.
"""
import re
import json
import os
import logging

logger = logging.getLogger(__name__)

class TheoryEngine:
    def __init__(self, rules_file='theory_rules.json'):
        self.rules_file = os.path.join(os.path.dirname(__file__), rules_file)
        self.rules_config = self._load_rules_config()
        
        # Mapa de métodos hardcoded (legacy support + complex logic)
        self.method_map = {
            # General rules
            "no_empty_pattern": self._rule_no_empty_pattern,
            "balanced_parens": self._rule_balanced_parens,
            "no_excessive_silence": self._rule_no_excessive_silence,
            "valid_euclidean": self._rule_valid_euclidean,
            "valid_speed_range": self._rule_valid_speed_range,
            "valid_filter_range": self._rule_valid_filter_range,
            "no_extreme_density_jumps": self._rule_no_extreme_density_jumps,
            "valid_sample_syntax": self._rule_valid_sample_syntax,
            "no_orphan_effects": self._rule_no_orphan_effects,
            "no_multiple_decimal_points": self._rule_no_multiple_decimal_points,
            # Genre-specific rules
            "kick_on_one": self._rule_kick_on_one,
            "steady_pulse": self._rule_steady_pulse,
            "backbeat": self._rule_snare_on_two_four,
            "high_density": self._rule_high_tempo_density,
            "no_heavy_kicks": self._rule_no_heavy_kicks,
            # Improved genre rules
            "techno_kick_pattern": self._rule_techno_kick_pattern,
            "techno_no_swing": self._rule_techno_no_swing,
            "house_four_on_floor": self._rule_house_four_on_floor,
            "house_offbeat_hats": self._rule_house_offbeat_hats,
            "dnb_fast_tempo": self._rule_dnb_fast_tempo,
            "dnb_breakbeat_structure": self._rule_dnb_breakbeat_structure,
            "ambient_low_density": self._rule_ambient_low_density,
            "ambient_texture_focus": self._rule_ambient_texture_focus,
            "breakbeat_syncopation": self._rule_breakbeat_syncopation,
            "dub_space_and_delay": self._rule_dub_space_and_delay,
            "experimental_unconventional": self._rule_experimental_unconventional,
            "trap_hihat_rolls": self._rule_trap_hihat_rolls,
            "trap_808_bass": self._rule_trap_808_bass,
            # Additional genre rules
            "breakbeat_varied_rhythm": self._rule_breakbeat_varied_rhythm,
            "dub_bass_focus": self._rule_dub_bass_focus,
            "experimental_complexity": self._rule_experimental_complexity,
            "cyberpunk_digital_sounds": self._rule_cyberpunk_digital_sounds,
            "cyberpunk_aggressive": self._rule_cyberpunk_aggressive,
            "industrial_harsh_sounds": self._rule_industrial_harsh_sounds,
            "industrial_distortion": self._rule_industrial_distortion,
            "deepsea_atmospheric": self._rule_deepsea_atmospheric,
            "deepsea_low_tempo": self._rule_deepsea_low_tempo,
            "glitch_fragmented": self._rule_glitch_fragmented,
            "glitch_digital_artifacts": self._rule_glitch_digital_artifacts,
            "organic_natural_sounds": self._rule_organic_natural_sounds,
            "organic_irregular_rhythm": self._rule_organic_irregular_rhythm
        }

    def _load_rules_config(self):
        """Carga reglas desde JSON o crea defaults si no existe."""
        defaults = {
            "general": [
                {"id": "no_empty_pattern", "type": "method", "active": True, "desc": "No Empty Patterns"},
                {"id": "balanced_parens", "type": "method", "active": True, "desc": "Balanced Parentheses"},
                {"id": "no_excessive_silence", "type": "method", "active": True, "desc": "Max 50% Silence"},
                {"id": "valid_euclidean", "type": "method", "active": True, "desc": "Valid Euclidean (k<=n)"},
                {"id": "no_consecutive_silences", "type": "regex", "pattern": "~ ~", "active": True, "desc": "No Consecutive Silences"},
                {"id": "no_multiple_decimal_points", "type": "method", "active": True, "desc": "No Multiple Decimals (e.g. 0.1.2)"},
                {"id": "valid_speed_range", "type": "method", "active": True, "desc": "Valid Speed (0.25-4.0)"},
                {"id": "valid_filter_range", "type": "method", "active": True, "desc": "Valid Filters (20-20kHz)"},
                {"id": "no_extreme_density_jumps", "type": "method", "active": True, "desc": "No Extreme Density Jumps"},
                {"id": "valid_sample_syntax", "type": "method", "active": True, "desc": "Valid Sample Syntax"},
                {"id": "no_orphan_effects", "type": "method", "active": True, "desc": "No Effects Without Sound"}
            ],
            "techno": [
                {"id": "techno_kick_pattern", "type": "method", "active": True, "desc": "Kick Pattern (4/4)"},
                {"id": "techno_no_swing", "type": "method", "active": True, "desc": "No Heavy Swing"}
            ],
            "house": [
                {"id": "house_four_on_floor", "type": "method", "active": True, "desc": "Four-on-Floor Kick"},
                {"id": "house_offbeat_hats", "type": "method", "active": True, "desc": "Offbeat Hi-Hats"}
            ],
            "drum_and_bass": [
                {"id": "dnb_fast_tempo", "type": "method", "active": True, "desc": "High Density (*8+)"},
                {"id": "dnb_breakbeat_structure", "type": "method", "active": True, "desc": "Breakbeat Structure"}
            ],
            "ambient": [
                {"id": "ambient_low_density", "type": "method", "active": True, "desc": "Low Density"},
                {"id": "ambient_texture_focus", "type": "method", "active": True, "desc": "Texture Focus"}
            ],
            "breakbeat": [
                {"id": "breakbeat_syncopation", "type": "method", "active": True, "desc": "Syncopation Required"},
                {"id": "breakbeat_varied_rhythm", "type": "method", "active": True, "desc": "Varied Rhythm"}
            ],
            "dub": [
                {"id": "dub_space_and_delay", "type": "method", "active": True, "desc": "Space & Delay"},
                {"id": "dub_bass_focus", "type": "method", "active": True, "desc": "Bass Focus"}
            ],
            "experimental": [
                {"id": "experimental_unconventional", "type": "method", "active": True, "desc": "Unconventional Patterns"},
                {"id": "experimental_complexity", "type": "method", "active": True, "desc": "Complex Structures"}
            ],
            "trap": [
                {"id": "trap_hihat_rolls", "type": "method", "active": True, "desc": "Hi-Hat Rolls (*12+)"},
                {"id": "trap_808_bass", "type": "method", "active": True, "desc": "808 Bass Elements"}
            ],
            "cyberpunk": [
                {"id": "cyberpunk_digital_sounds", "type": "method", "active": True, "desc": "Digital/Synth Sounds"},
                {"id": "cyberpunk_aggressive", "type": "method", "active": True, "desc": "Aggressive Rhythm"}
            ],
            "industrial": [
                {"id": "industrial_harsh_sounds", "type": "method", "active": True, "desc": "Harsh/Metallic Sounds"},
                {"id": "industrial_distortion", "type": "method", "active": True, "desc": "Distortion/Noise"}
            ],
            "deepsea": [
                {"id": "deepsea_atmospheric", "type": "method", "active": True, "desc": "Atmospheric/Fluid"},
                {"id": "deepsea_low_tempo", "type": "method", "active": True, "desc": "Low Tempo/Sparse"}
            ],
            "glitch": [
                {"id": "glitch_fragmented", "type": "method", "active": True, "desc": "Fragmented Patterns"},
                {"id": "glitch_digital_artifacts", "type": "method", "active": True, "desc": "Digital Artifacts"}
            ],
            "organic": [
                {"id": "organic_natural_sounds", "type": "method", "active": True, "desc": "Natural/Field Sounds"},
                {"id": "organic_irregular_rhythm", "type": "method", "active": True, "desc": "Irregular Rhythm"}
            ]
        }
        
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r') as f:
                    config = json.load(f)
                
                # MIGRACIÓN: Asegurarse de que las reglas críticas existan
                if "general" in config:
                    existing_ids = [r['id'] for r in config["general"]]
                    for mandatory_rule in defaults["general"]:
                        if mandatory_rule['id'] not in existing_ids:
                            config["general"].append(mandatory_rule)
                            logger.info(f"Migración: Regla {mandatory_rule['id']} añadida al config existente.")
                    
                    # Guardar si hubo cambios
                    if len(config["general"]) > len(existing_ids):
                        self._save_rules_config(config)
                
                return config
            except Exception as e:
                logger.error(f"Error loading rules JSON: {e}")
                return defaults
        else:
            self._save_rules_config(defaults)
            return defaults

    def _save_rules_config(self, config=None):
        """Guarda la configuración actual en JSON."""
        if config:
            self.rules_config = config
        try:
            with open(self.rules_file, 'w') as f:
                json.dump(self.rules_config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving rules JSON: {e}")

    def get_rules(self):
        """Devuelve la configuración completa de reglas."""
        return self.rules_config

    def toggle_rule(self, genre, rule_id, active):
        """Activa o desactiva una regla."""
        if genre in self.rules_config:
            for rule in self.rules_config[genre]:
                if rule['id'] == rule_id:
                    rule['active'] = active
                    self._save_rules_config()
                    return True
        return False

    def add_regex_rule(self, genre, rule_id, regex_pattern, message):
        """Añade una regla personalizada basada en Regex."""
        if genre not in self.rules_config:
            self.rules_config[genre] = []
            
        new_rule = {
            "id": rule_id,
            "type": "regex",
            "regex": regex_pattern,
            "message": message,
            "active": True,
            "desc": f"Custom: {rule_id}"
        }
        self.rules_config[genre].append(new_rule)
        self._save_rules_config()
        return True

    def validate(self, pattern, genre):
        """
        Valida usando reglas dinámicas.
        Aplica reglas GENERALES primero, luego reglas del género.
        """
        issues = []
        
        # 1. Aplicar reglas GENERALES (siempre)
        if "general" in self.rules_config:
            for rule_def in self.rules_config["general"]:
                if not rule_def.get('active', True):
                    continue
                    
                # Ejecutar según tipo
                if rule_def['type'] == 'method':
                    method = self.method_map.get(rule_def['id'])
                    if method:
                        valid, msg = method(pattern)
                        if not valid: issues.append(f"[GENERAL] {msg}")
                
                elif rule_def['type'] == 'regex':
                    if re.search(rule_def['pattern'], pattern, re.IGNORECASE):
                        issues.append(f"[GENERAL] {rule_def.get('message', 'Regex violation')}")
        
        # 2. Aplicar reglas del GÉNERO (si existe)
        if not genre or genre not in self.rules_config:
            return len(issues) == 0, issues
        
        for rule_def in self.rules_config[genre]:
            if not rule_def.get('active', True):
                continue
                
            # Ejecutar según tipo
            if rule_def['type'] == 'method':
                method = self.method_map.get(rule_def['id'])
                if method:
                    valid, msg = method(pattern)
                    if not valid: issues.append(f"[{genre.upper()}] {msg}")
            
            elif rule_def['type'] == 'regex':
                # Regla Regex: El patrón DEBE cumplir el regex
                if not re.search(rule_def['regex'], pattern, re.IGNORECASE):
                    issues.append(f"[{genre.upper()}] {rule_def['message']}")
                    
        return len(issues) == 0, issues

    def sanitize_pattern(self, pattern):
        """Limpia errores críticos antes de que el patrón llegue al usuario."""
        import re
        
        # 1. Corregir múltiples decimales (ej: 0.1.86 -> 0.186)
        # Buscamos números con más de un punto
        def fix_decimals(match):
            text = match.group(0)
            parts = text.split('.')
            return parts[0] + "." + "".join(parts[1:])
        
        sanitized = re.sub(r'\d+\.\d+(\.\d+)+', fix_decimals, pattern)
        
        if sanitized != pattern:
            logger.info(f"✨ Auto-Sanitizer: Corregidos decimales en {pattern} -> {sanitized}")
            
        return sanitized

    def get_musical_insight(self, pattern, genre):
        """Analiza el patrón y devuelve una explicación musical."""
        insights = []
        p_lower = pattern.lower()
        
        # 1. Análisis de Estructura Rítmica
        sync_score = self.analyze_syncopation(pattern)
        variety_score = self.analyze_variety(pattern)
        
        if sync_score > 0.6:
            insights.append(f"He detectado una síncopa elevada ({int(sync_score*100)}%), lo que añade un groove agresivo y dinámico.")
        elif sync_score < 0.2 and "bd" in p_lower:
            insights.append("La rítmica es altamente estable y centrada, ideal para mantener el pulso en pista.")

        if variety_score > 0.7:
            insights.append("La variedad de tokens es alta, creando un patrón rico en matices y poco repetitivo.")

        # 2. Análisis de Estructura Clásica
        if "bd*4" in p_lower or 'bd * 4' in p_lower:
            insights.append("He reforzado el 'Four-on-the-floor' para asegurar una base rítmica inamovible.")
        elif "bd" in p_lower and "(" in p_lower:
            insights.append("El uso de algoritmos euclidianos aporta una complejidad matemática natural al ritmo.")
        
        # 3. Análisis de Síncopa & Swing
        if "sn" in p_lower or "cp" in p_lower:
            if "every" in p_lower:
                insights.append("Las variaciones condicionales en la caja inyectan un 'swing' orgánico que respira.")
            else:
                insights.append("El 'backbeat' está alineado para maximizar el impacto rítmico.")

        # 4. Análisis de Complejidad (FX)
        fx_keywords = ["gain", "delay", "room", "size", "cutoff", "hpf", "lpf", "crush"]
        detected_fx = [fx for fx in fx_keywords if fx in p_lower]
        if len(detected_fx) > 2:
            insights.append(f"La cadena de efectos ({', '.join(detected_fx[:2])}) añade una dimensión espacial profunda.")
        
        # 5. Análisis Específico de Género
        genre_map = {
            "glitch": "He fragmentado la señal para generar micro-artefactos digitales característicos del género.",
            "ambient": "Me he centrado en el espacio negativo y las texturas etéreas, minimizando la percusión directa.",
            "trap": "He configurado hi-hat rolls de alta frecuencia para dar esa sensación de urgencia urbana.",
            "drum_and_bass": "La base es un breakbeat deconstruido con síncopa extrema, rindiendo homenaje al jungle clásico.",
            "cyberpunk": "He priorizado una estética industrial y agresiva con énfasis en el procesamiento digital.",
            "industrial": "La saturación y el ruido metálico son los protagonistas de este diseño sonoro."
        }
        if genre in genre_map:
            insights.append(genre_map[genre])

        # Fallback
        if not insights:
            insights.append("He equilibrado todos los parámetros para lograr una coherencia musical absoluta.")

        return " ".join(insights)

    # --- HARDCODED LOGIC METHODS (Las mismas de antes) ---
    
    def _rule_kick_on_one(self, pattern):
        if "bd" in pattern.lower(): return True, ""
        return False, "Missing Kick (bd) foundation"

    def _rule_steady_pulse(self, pattern):
        if "*4" in pattern or "*8" in pattern: return True, ""
        return True, "" 

    def _rule_snare_on_two_four(self, pattern):
        if "sn" in pattern or "cp" in pattern: return True, ""
        return False, "Missing Backbeat (sn/cp)"

    def _rule_high_tempo_density(self, pattern):
        if "*" in pattern or "[" in pattern: return True, ""
        return False, "Too simple for DnB"

    def _rule_no_heavy_kicks(self, pattern):
        if "bd*4" in pattern: return False, "Too rhythmic for Ambient (bd*4 detected)"
        return True, ""
    
    # --- GENERAL MUSIC THEORY RULES ---
    
    def _rule_no_empty_pattern(self, pattern):
        """No patrones vacíos o solo espacios."""
        clean = pattern.strip()
        if not clean or clean == "~":
            return False, "Pattern cannot be empty"
        return True, ""
    
    def _rule_balanced_parens(self, pattern):
        """Verifica que paréntesis, corchetes y llaves estén balanceados."""
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        for char in pattern:
            if char in pairs.keys():
                stack.append(char)
            elif char in pairs.values():
                if not stack or pairs[stack.pop()] != char:
                    return False, "Unbalanced parentheses/brackets"
        if stack:
            return False, "Unbalanced parentheses/brackets"
        return True, ""
    
    def _rule_no_excessive_silence(self, pattern):
        """Máximo 50% de silencios en el patrón."""
        tokens = pattern.split()
        if not tokens:
            return True, ""
        silence_count = sum(1 for t in tokens if t == '~')
        silence_ratio = silence_count / len(tokens)
        if silence_ratio > 0.5:
            return False, f"Too much silence ({int(silence_ratio*100)}% > 50%)"
        return True, ""
    
    def _rule_valid_euclidean(self, pattern):
        """Verifica que en notación euclidiana (k,n), k <= n."""
        import re
        euclidean_matches = re.findall(r'\((\d+),(\d+)\)', pattern)
        for k, n in euclidean_matches:
            if int(k) > int(n):
                return False, f"Invalid Euclidean: ({k},{n}) - k must be <= n"
        return True, ""
    
    def _rule_no_multiple_decimal_points(self, pattern):
        """Verifica que no haya números con más de un punto decimal."""
        import re
        # Busca cualquier cadena que parezca un número con múltiples puntos
        bad_numbers = re.findall(r'\d*\.\d*\.\d+', pattern)
        if bad_numbers:
            return False, f"Invalid numeric syntax: {bad_numbers[0]}"
        return True, ""
    
    # --- ADDITIONAL GENERAL RULES ---
    
    def _rule_valid_speed_range(self, pattern):
        """Speed debe estar entre 0.25 y 4.0"""
        import re
        speeds = re.findall(r'speed\s+(\d+\.?\d*)', pattern)
        for speed in speeds:
            if float(speed) < 0.25 or float(speed) > 4.0:
                return False, f"Invalid speed: {speed} (must be 0.25-4.0)"
        return True, ""
    
    def _rule_valid_filter_range(self, pattern):
        """lpf/hpf entre 20Hz y 20000Hz"""
        import re
        filters = re.findall(r'(?:lpf|hpf)\s+(\d+)', pattern)
        for freq in filters:
            if int(freq) < 20 or int(freq) > 20000:
                return False, f"Invalid filter: {freq}Hz (must be 20-20000)"
        return True, ""
    
    def _rule_no_extreme_density_jumps(self, pattern):
        """No mezclar *16 con *0.25 en el mismo patrón"""
        import re
        has_very_fast = bool(re.search(r'\*1[2-6]', pattern))
        has_very_slow = bool(re.search(r'\*0\.[1-5]', pattern))
        if has_very_fast and has_very_slow:
            return False, "Extreme density jump (*16 + *0.25 in same pattern)"
        return True, ""
    
    def _rule_valid_sample_syntax(self, pattern):
        """Verifica que 's' o 'sound' tengan comillas"""
        import re
        if re.search(r'\bs\s+[a-z]+(?!["\'])', pattern):
            return False, "Sample name must be quoted: s \"bd\" not s bd"
        return True, ""
    
    def _rule_no_orphan_effects(self, pattern):
        """No puede haber solo efectos sin 's' o 'sound'"""
        import re
        has_sound = bool(re.search(r'\b(?:s|sound)\b', pattern))
        has_effects = bool(re.search(r'#\s*(?:lpf|hpf|room|delay|gain)', pattern))
        if has_effects and not has_sound:
            return False, "Effects without sound source"
        return True, ""
    
    # --- IMPROVED GENRE-SPECIFIC RULES ---
    
    # TECHNO
    def _rule_techno_kick_pattern(self, pattern):
        """Techno requiere kick en patrón regular (4/4)"""
        import re
        if 'bd' not in pattern.lower():
            return False, "Techno requires kick drum (bd)"
        # Verificar que no esté muy sincopado
        if re.search(r'bd.*~.*~.*~', pattern):
            return False, "Techno kick too sparse (4/4 pulse required)"
        return True, ""
    
    def _rule_techno_no_swing(self, pattern):
        """Techno evita swing excesivo"""
        import re
        if re.search(r'bd.*\[.*~.*\]', pattern):
            return False, "Techno should avoid heavy swing patterns"
        return True, ""
    
    # HOUSE
    def _rule_house_four_on_floor(self, pattern):
        """House requiere bombo constante (four-on-floor)"""
        import re
        if not re.search(r'bd\*[4-8]', pattern):
            return False, "House requires four-on-floor kick (bd*4 or bd*8)"
        return True, ""
    
    def _rule_house_offbeat_hats(self, pattern):
        """House típicamente tiene hats en offbeat"""
        import re
        if 'hh' in pattern and not re.search(r'hh.*\*[8-9]|hh.*\*1[0-6]', pattern):
            return False, "House hats should be fast (*8 or higher)"
        return True, ""
    
    # DRUM & BASS
    def _rule_dnb_fast_tempo(self, pattern):
        """DnB requiere alta densidad rítmica"""
        import re
        density_markers = len(re.findall(r'\*[8-9]|\*1[0-6]|\[', pattern))
        if density_markers < 2:
            return False, "DnB requires high rhythmic density (*8+, brackets)"
        return True, ""
    
    def _rule_dnb_breakbeat_structure(self, pattern):
        """DnB debe tener estructura de breakbeat"""
        has_kick = 'bd' in pattern
        has_snare = 'sn' in pattern or 'cp' in pattern
        if not (has_kick and has_snare):
            return False, "DnB requires both kick and snare"
        return True, ""
    
    # AMBIENT
    def _rule_ambient_low_density(self, pattern):
        """Ambient requiere baja densidad"""
        import re
        if re.search(r'\*[8-9]|\*1[0-6]', pattern):
            return False, "Ambient should avoid high density (*8+)"
        return True, ""
    
    def _rule_ambient_texture_focus(self, pattern):
        """Ambient prioriza texturas sobre ritmo"""
        import re
        percussive = len(re.findall(r'\b(?:bd|sn|cp|hh)\b', pattern))
        textural = len(re.findall(r'\b(?:pad|texture|drone|field)\b', pattern))
        if percussive > textural and percussive > 2:
            return False, "Ambient should focus on textures, not percussion"
        return True, ""
    
    # BREAKBEAT
    def _rule_breakbeat_syncopation(self, pattern):
        """Breakbeat requiere sincopación"""
        import re
        if not re.search(r'~|\[.*~.*\]', pattern):
            return False, "Breakbeat requires syncopation (~ or brackets)"
        return True, ""
    
    # DUB
    def _rule_dub_space_and_delay(self, pattern):
        """Dub requiere espacio y delay"""
        import re
        has_space = bool(re.search(r'~', pattern))
        has_delay = bool(re.search(r'delay|room', pattern))
        if not (has_space or has_delay):
            return False, "Dub requires space (silence ~) or delay effects"
        return True, ""
    
    # EXPERIMENTAL
    def _rule_experimental_unconventional(self, pattern):
        """Experimental debe romper convenciones"""
        import re
        conventional_markers = len(re.findall(r'bd\*4|sn.*cp|hh\*8', pattern))
        if conventional_markers > 1:
            return False, "Too conventional for Experimental"
        return True, ""
    
    # TRAP
    def _rule_trap_hihat_rolls(self, pattern):
        """Trap requiere hi-hat rolls rápidos"""
        import re
        if 'hh' in pattern and not re.search(r'hh.*\*1[2-6]', pattern):
            return False, "Trap requires fast hi-hat rolls (*12+)"
        return True, ""
    
    def _rule_trap_808_bass(self, pattern):
        """Trap típicamente usa 808 bass"""
        import re
        if not re.search(r'808|bass|sub', pattern):
            return False, "Trap should include 808/bass elements"
        return True, ""
    
    # --- ADDITIONAL GENRE RULES ---
    
    # BREAKBEAT (additional)
    def _rule_breakbeat_varied_rhythm(self, pattern):
        """Breakbeat debe tener ritmo variado"""
        import re
        if re.search(r'(\w+\*\d+)\s+\1\s+\1', pattern):
            return False, "Breakbeat should have varied rhythm (too repetitive)"
        return True, ""
    
    # DUB (additional)
    def _rule_dub_bass_focus(self, pattern):
        """Dub debe enfocarse en el bajo"""
        import re
        has_bass = bool(re.search(r'bass|sub|808', pattern))
        if not has_bass:
            return False, "Dub requires bass focus"
        return True, ""
    
    # EXPERIMENTAL (additional)
    def _rule_experimental_complexity(self, pattern):
        """Experimental debe tener estructuras complejas"""
        import re
        complexity_markers = len(re.findall(r'\[|\(|\{|<', pattern))
        if complexity_markers < 2:
            return False, "Experimental should have complex structures"
        return True, ""
    
    # CYBERPUNK
    def _rule_cyberpunk_digital_sounds(self, pattern):
        """Cyberpunk requiere sonidos digitales"""
        import re
        digital_sounds = bool(re.search(r'synth|digital|cyber|glitch|chip', pattern))
        if not digital_sounds:
            return False, "Cyberpunk requires digital sounds"
        return True, ""
    
    def _rule_cyberpunk_aggressive(self, pattern):
        """Cyberpunk requiere ritmo agresivo"""
        import re
        has_aggression = bool(re.search(r'\*[6-9]|\*1[0-6]|bd.*sn', pattern))
        if not has_aggression:
            return False, "Cyberpunk requires aggressive rhythm"
        return True, ""
    
    # INDUSTRIAL
    def _rule_industrial_harsh_sounds(self, pattern):
        """Industrial requiere sonidos duros"""
        import re
        harsh_sounds = bool(re.search(r'metal|industrial|harsh|noise|clank', pattern))
        if not harsh_sounds:
            return False, "Industrial requires harsh sounds"
        return True, ""
    
    def _rule_industrial_distortion(self, pattern):
        """Industrial usa distorsión"""
        import re
        has_distortion = bool(re.search(r'distort|crush|noise|gain\s+[2-9]', pattern))
        if not has_distortion:
            return False, "Industrial should include distortion"
        return True, ""
    
    # DEEPSEA
    def _rule_deepsea_atmospheric(self, pattern):
        """DeepSea requiere atmósfera fluida"""
        import re
        atmospheric = bool(re.search(r'pad|reverb|room|ocean|water|wave', pattern))
        if not atmospheric:
            return False, "DeepSea requires atmospheric sounds"
        return True, ""
    
    def _rule_deepsea_low_tempo(self, pattern):
        """DeepSea debe ser lento"""
        import re
        if re.search(r'\*[8-9]|\*1[0-6]', pattern):
            return False, "DeepSea should be slow"
        if '~' not in pattern:
            return False, "DeepSea requires space"
        return True, ""
    
    # GLITCH
    def _rule_glitch_fragmented(self, pattern):
        """Glitch requiere fragmentación"""
        import re
        fragments = len(re.findall(r'~|\[.*~.*\]', pattern))
        if fragments < 2:
            return False, "Glitch requires fragmented patterns"
        return True, ""
    
    def _rule_glitch_digital_artifacts(self, pattern):
        """Glitch debe tener artefactos digitales"""
        import re
        artifacts = bool(re.search(r'glitch|stutter|chop|cut|bit', pattern))
        if not artifacts:
            return False, "Glitch requires digital artifacts"
        return True, ""
    
    # ORGANIC
    def _rule_organic_natural_sounds(self, pattern):
        """Organic requiere sonidos naturales"""
        import re
        natural = bool(re.search(r'field|nature|wood|bird|wind|rain|organic', pattern))
        if not natural:
            return False, "Organic requires natural sounds"
        return True, ""
    
    def _rule_organic_irregular_rhythm(self, pattern):
        """Organic debe tener ritmo irregular"""
        import re
        regular_patterns = len(re.findall(r'bd\*4|sn\*4|hh\*8', pattern))
        if regular_patterns > 1:
            return False, "Organic should have irregular rhythm"
        return True, ""

    # --- FASE 36: DIAGNÓSTICOS AVANZADOS ---

    def analyze_syncopation(self, pattern: str) -> float:
        """Mide el nivel de síncopa (desplazamiento rítmico)."""
        score = 0.0
        # Marcadores de síncopa: silencios iniciales, corchetes, tildes
        if re.search(r'\"~\s+', pattern): score += 0.3
        if "[" in pattern: score += 0.2
        if "(" in pattern: score += 0.2 # Euclidean is often syncopated
        if "~" in pattern: score += 0.1
        # Bonus por irregularidad
        if pattern.count("~") > 2: score += 0.2
        return min(1.0, score)

    def analyze_variety(self, pattern: str) -> float:
        """Mide la diversidad de tokens (no repetitividad)."""
        tokens = pattern.split()
        if not tokens: return 0.0
        unique_tokens = set(tokens)
        ratio = len(unique_tokens) / len(tokens)
        return min(1.0, ratio)
