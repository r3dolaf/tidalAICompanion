"""
TidalAI Companion - Pattern Generator
Generador de patrones TidalCycles con soporte para diferentes estilos y parámetros.
Incluye generación basada en reglas y modelo de IA (Markov Chains).
"""

import random
import os
import json
from typing import List, Dict, Optional
from enum import Enum
from collections import defaultdict

# Intentar importar modelo Markov (opcional)
try:
    from markov_model import MarkovModel
    MARKOV_AVAILABLE = True
except ImportError:
    MARKOV_AVAILABLE = False
    print("Markov model no disponible. Usando solo generación basada en reglas.")


class PatternType(Enum):
    """Tipos de patrones soportados"""
    DRUMS = "drums"
    BASS = "bass"
    MELODY = "melody"
    PERCUSSION = "percussion"
    FX = "fx"


class PatternGenerator:
    """
    Generador de patrones TidalCycles.
    
    Soporta dos modos:
    - Basado en reglas: Usa biblioteca de patrones predefinidos
    - Basado en IA: Usa modelo Markov entrenado con ejemplos
    """
    
    def __init__(self, model=None, use_ai: bool = False):
        """
        Inicializar generador.
        
        Args:
            model: Modelo de IA opcional (MarkovModel)
            use_ai: Si True, usa modelo de IA cuando esté disponible
        """
        self.model = model
        self.use_ai = use_ai and MARKOV_AVAILABLE
        self._init_pattern_library()
        
        # Fase 36: Memoria Musical
        self.pattern_history = []
        self.max_history = 10
        
        # Cargar o crear modelo Markov si está disponible
        self.markov_model = None
        self.rule_thoughts = [] # Para logging de lógica en tiempo real
        if MARKOV_AVAILABLE and use_ai:
            self._init_markov_model()
    
    def reload_library(self):
        """Recarga la librería de samples e index extendido"""
        self._init_pattern_library()
        
    def _init_pattern_library(self):
        """Inicializar biblioteca de patrones base desde JSON o defaults"""
        
        # Intentar cargar desde JSON
        samples_path = os.path.join(os.path.dirname(__file__), '..', 'samples.json')
        loaded_json = False
        
        if os.path.exists(samples_path):
            try:
                import json
                with open(samples_path, 'r') as f:
                    data = json.load(f)
                    
                self.drum_samples = data.get('drums', {
                    'kick': ['bd', 'bass'], 'snare': ['sn'], 'hihat': ['hh']
                })
                self.bass_samples = data.get('bass', ['bass', 'bass1'])
                self.melody_samples = data.get('melody', ['superpiano'])
                self.perc_samples = data.get('percussion', ['tabla'])
                self.fx_samples = data.get('fx', ['wind', 'noise'])
                
                # Fusionar synths en melody_samples si existen
                synths = data.get('synths', [])
                if synths:
                    # Evitar duplicados
                    self.melody_samples = list(set(self.melody_samples + synths))
                
                loaded_json = True
                print(f"Librería de samples cargada desde {samples_path}")
            except Exception as e:
                print(f"Error cargando samples.json: {e}")
        
        # Cargar index extendido (Fase 18: AI Sample Scout)
        self.extended_samples = {}
        extended_path = os.path.join(os.path.dirname(__file__), 'samples_v2.json')
        if os.path.exists(extended_path):
            try:
                with open(extended_path, 'r') as f:
                    self.extended_samples = json.load(f)
                print(f"Index extendido de samples cargado ({len(self.extended_samples)} categorías)")
            except Exception as e:
                print(f"Error cargando samples_v2.json: {e}")

        # Cargar samples personalizados del usuario (Smart Scout)
        custom_path = os.path.join(os.path.dirname(__file__), 'custom_samples.json')
        if os.path.exists(custom_path):
            try:
                with open(custom_path, 'r') as f:
                    custom_data = json.load(f)
                
                print(f"Cargando {len(custom_data)} bancos de usuario...")
                
                # Heurística simple para clasificar
                for name in custom_data.keys():
                    name_lower = name.lower()
                    
                    # Drums
                    if name_lower.startswith('bd') or 'kick' in name_lower:
                        if 'kick' not in self.drum_samples: self.drum_samples['kick'] = []
                        if name not in self.drum_samples['kick']: self.drum_samples['kick'].append(name)
                    elif name_lower.startswith('sn') or 'snare' in name_lower or 'sd' in name_lower:
                        if 'snare' not in self.drum_samples: self.drum_samples['snare'] = []
                        if name not in self.drum_samples['snare']: self.drum_samples['snare'].append(name)
                    elif name_lower.startswith('hh') or 'hat' in name_lower:
                        if 'hihat' not in self.drum_samples: self.drum_samples['hihat'] = []
                        if name not in self.drum_samples['hihat']: self.drum_samples['hihat'].append(name)
                    elif 'clap' in name_lower or 'cp' in name_lower:
                         if 'clap' not in self.drum_samples: self.drum_samples['clap'] = []
                         if name not in self.drum_samples['clap']: self.drum_samples['clap'].append(name)
                         
                    # Bass
                    elif 'bass' in name_lower or 'moog' in name_lower or '808' in name_lower:
                        if name not in self.bass_samples: self.bass_samples.append(name)
                        
                    # Percussion
                    elif 'perc' in name_lower or 'tabla' in name_lower or 'glitch' in name_lower:
                        if name not in self.perc_samples: self.perc_samples.append(name)
                    
                    # Si no encaja, lo metemos en 'fx' o 'melody' por defecto para que la IA tenga variedad
                    # (Mejor estrategia: pool genérico de 'custom')
                    else:
                        if name not in self.fx_samples: self.fx_samples.append(name)
                        
                loaded_json = True # Marcar como cargado para no usar defaults si el json falló pero este no
                
            except Exception as e:
                print(f"Error cargando custom_samples.json: {e}")
        
        if not loaded_json:
            print("Usando librería de samples por defecto")
            # Samples de drums
            self.drum_samples = {
                'kick': ['bd', 'bass', 'bass3'],
                'snare': ['sn', 'snare', 'sd'],
                'hihat': ['hh', 'hat', 'hc'],
                'clap': ['cp', 'clap'],
                'tom': ['lt', 'mt', 'ht'],
                'cymbal': ['cy', 'crash']
            }
            
            # Samples de bass
            self.bass_samples = ['bass', 'bass1', 'bass2', 'bass3', 'jungbass']
            
            # Samples de melodía (SAMPLES + SYNTHS COMPLETOS)
            self.melody_samples = [
                'arpy', 'tink', 'metal', 'kurt',     # Samples
                'superpiano', 'supersaw', 'superpwm', 'superchip', # Synths Clásicos
                'supermandolin', 'supergong', 'supervibe', 'superhex' # Synths Exóticos
            ]
            
            # Samples de percusión
            self.perc_samples = ['tabla', 'tabla2', 'bongo', 'conga', 'tok']
            
            # Samples de FX (SOLO SAMPLES)
            self.fx_samples = ['glitch', 'h', 'insect', 'procshort', 'voodoo']
        
        # Notas musicales (constantes)
        self.notes = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
        self.octaves = [2, 3, 4, 5]
        
        # Escalas musicales (constantes)
        self.scales = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'pentatonic': [0, 2, 4, 7, 9],
            'blues': [0, 3, 5, 6, 7, 10]
        }
    
    def _init_markov_model(self):
        """Inicializar modelo Markov"""
        model_path = os.path.join(os.path.dirname(__file__), 'markov_model.json')
        
        if os.path.exists(model_path):
            # Cargar modelo existente
            self.markov = MarkovModel()
            self.markov.load(model_path)
            print(f"Modelo Markov cargado desde {model_path}")
        else:
            # Crear y entrenar modelo nuevo con corpus por defecto
            from markov_model import EXAMPLE_CORPUS
            self.markov = MarkovModel(order=2)
            self.markov.train(EXAMPLE_CORPUS)
            self.markov.save(model_path)
            print(f"Modelo Markov creado y guardado en {model_path}")
    
    def generate(self,
                 pattern_type: str = "drums",
                 density: float = 0.6,
                 complexity: float = 0.5,
                 tempo: int = 140,
                 style: str = "techno",
                 use_ai: bool = None,
                 temperature: float = 1.0,
                 musical_friction: float = 0.2,
                 intent_modifiers: Dict = None) -> Dict:
        """
        Generar patrón TidalCycles. Devuelve dict con {"pattern": str, "thoughts": list}
        """
        
        # Aplicar modificadores de intención si existen
        if intent_modifiers:
            density = max(0.0, min(1.0, density + intent_modifiers.get("density_offset", 0.0)))
            complexity = max(0.0, min(1.0, complexity + intent_modifiers.get("complexity_offset", 0.0)))
            tempo += intent_modifiers.get("tempo_mod", 0)
            if intent_modifiers.get("style_pref"):
                style = intent_modifiers["style_pref"]

        # Determinar si usar IA
        should_use_ai = use_ai if use_ai is not None else self.use_ai
        
        # Si IA está disponible y habilitada, usarla (el generador IA podría recibir tokens extra)
        if should_use_ai and MARKOV_AVAILABLE and hasattr(self, 'markov'):
            # Inyectar tokens extra en el pensamiento si existen
            result = self._generate_with_ai(temperature)
            
            # --- FASE 36: CONTEXTUAL FRICTION ---
            # Si el patrón es idéntico o muy similar al anterior, forzar mutación
            if self.pattern_history:
                similarity = self._calculate_similarity(result["pattern"], self.pattern_history[-1])
                if similarity > 0.8:
                    mutation = self.mutate(result["pattern"], strength=0.6)
                    result["pattern"] = mutation["pattern"]
                    result["thoughts"].append({
                        "token": "HIST_FRICTION", 
                        "prob": similarity, 
                        "alts": ["Patrón muy similar al anterior detectado. Mutación forzada para evitar estancamiento."]
                    })

            if intent_modifiers and intent_modifiers.get("extra_tokens"):
                for t in intent_modifiers["extra_tokens"]:
                    result["pattern"] += f" {t}"
                result["thoughts"].append({"token": "MODS", "prob": 1.0, "alts": intent_modifiers["extra_tokens"]})
            
            # --- FASE 36: HUMANIZER ---
            result["pattern"] = self._humanize_pattern(result["pattern"])
            
            # Guardar en historial
            self._update_history(result["pattern"])
            
            # Post-procesar sintaxis (Fase 16: Asegurar espacio tras $)
            result["pattern"] = self._post_process_syntax(result["pattern"])
            return result
        
        # Sino, usar generación basada en reglas
        self.rule_thoughts = [] # Limpiar para nueva generación
        density = max(0.0, min(1.0, density))
        complexity = max(0.0, min(1.0, complexity))
        
        pattern = ""
        if pattern_type == "drums":
            pattern = self._generate_drums(density, complexity, style, musical_friction)
        elif pattern_type == "bass":
            pattern = self._generate_bass(density, complexity, style, musical_friction)
        elif pattern_type == "melody":
            pattern = self._generate_melody(density, complexity, style, musical_friction)
        elif pattern_type == "percussion":
            pattern = self._generate_percussion(density, complexity, style, musical_friction)
        elif pattern_type == "fx":
            pattern = self._generate_fx(density, complexity, style, musical_friction)
        else:
            raise ValueError(f"Tipo de patrón no soportado: {pattern_type}")
            
        thoughts = self.rule_thoughts
        if intent_modifiers and intent_modifiers.get("extra_tokens"):
            for t in intent_modifiers["extra_tokens"]:
                pattern += f" {t}"
            thoughts.append({"token": "ORACLE", "prob": 1.0, "alts": intent_modifiers["extra_tokens"]})

        # Post-procesar sintaxis (Fase 16: Asegurar espacio tras $)
        pattern = self._post_process_syntax(pattern)

        return {"pattern": pattern, "thoughts": thoughts}
    
    def _generate_drums(self, density: float, complexity: float, style: str, friction: float = 0.2) -> str:
        """Generar patrón de drums"""
        
        # Seleccionar samples según estilo
        if style == "techno":
            kick = random.choice(self.drum_samples['kick'])
            snare = random.choice(self.drum_samples['snare'])
            hihat = random.choice(self.drum_samples['hihat'])
        elif style == "ambient":
            kick = random.choice(self.drum_samples['kick'])
            snare = random.choice(self.drum_samples['snare'])
            hihat = random.choice(self.drum_samples['hihat'])
        else:  # default
            kick = 'bd'
            snare = 'sn'
            hihat = 'hh'
        
        # Fricción Musical: Posibilidad de swap de samples fuera de estilo
        if random.random() < friction:
            # Aplanar todas las listas de samples disponibles para elegir uno al azar
            all_samples = []
            for s_list in self.drum_samples.values():
                if isinstance(s_list, list):
                    all_samples.extend(s_list)
            
            if all_samples:
                swapped = random.choice(all_samples)
                target = random.choice(['kick', 'snare', 'hihat'])
                
                if target == 'kick': kick = swapped
                elif target == 'snare': snare = swapped
                else: hihat = swapped
                
                self.rule_thoughts.append({
                    "token": "FRICCIÓN", 
                    "prob": friction, 
                    "alternatives": [{"token": f"Swap {target} -> {swapped}", "prob": 1.0}]
                })
        
        # Calcular repeticiones basadas en densidad
        kick_density = int(2 + density * 6)  # 2-8 kicks
        snare_density = int(1 + density * 3)  # 1-4 snares
        hihat_density = int(4 + density * 12)  # 4-16 hihats

        self.rule_thoughts.append({
            "token": "REGLAS: DRUMS",
            "prob": 0.9,
            "alternatives": [
                {"token": f"Estilo: {style}", "prob": 1.0},
                {"token": f"Kicks: {kick_density}", "prob": density},
                {"token": f"Snares: {snare_density}", "prob": density},
                {"token": f"Hihats: {hihat_density}", "prob": density}
            ]
        })
        
        # Construir patrón básico
        if complexity < 0.3:
            # Patrón simple
            pattern = f'sound "{kick}*{kick_density} {snare}*{snare_density}"'
            self.rule_thoughts.append({"token": "MODO", "prob": 1.0, "alternatives": [{"token": "Estructura Simple", "prob": 1.0}]})
        elif complexity < 0.7:
            # Patrón medio
            pattern = f'sound "{kick}*{kick_density} {snare}*{snare_density} {hihat}*{hihat_density}"'
            self.rule_thoughts.append({"token": "MODO", "prob": 1.0, "alternatives": [{"token": "Estructura Estándar", "prob": 1.0}]})
        else:
            # Patrón complejo con euclidean rhythms
            pattern = f'sound "{kick}({kick_density},{int(16*density)}) {snare}({snare_density},8) {hihat}*{hihat_density}"'
            self.rule_thoughts.append({"token": "MODO", "prob": 1.0, "alternatives": [{"token": "Estructura Euclídea", "prob": 1.0}]})
        
        # Añadir efectos según complejidad
        effects = []
        if complexity > 0.4:
            effects.append(f"# speed {0.8 + random.random() * 0.4:.2f}")
            self.rule_thoughts.append({"token": "FX", "prob": 0.5, "alternatives": [{"token": "Variación Speed", "prob": complexity}]})
        if complexity > 0.6:
            effects.append(f"# room {random.random() * 0.3:.2f}")
            self.rule_thoughts.append({"token": "FX", "prob": 0.5, "alternatives": [{"token": "Reverb/Room", "prob": complexity}]})
        if complexity > 0.8:
            effects.append(f"# gain {0.9 + random.random() * 0.2:.2f}")
            self.rule_thoughts.append({"token": "FX", "prob": 0.5, "alternatives": [{"token": "Compress/Gain", "prob": complexity}]})
        
        if effects:
            pattern += "\n  " + "\n  ".join(effects)
        
        return pattern
    
    def _generate_bass(self, density: float, complexity: float, style: str, friction: float = 0.2) -> str:
        """Generar patrón de bass"""
        
        sample = random.choice(self.bass_samples)
        
        # FRICCIÓN: Posibilidad de cambiar a un sample aleatorio de cualquier tipo
        if random.random() < friction:
            sample = random.choice(self.bass_samples + self.melody_samples)
            self.rule_thoughts.append({"token": "FRICCIÓN", "prob": friction, "alternatives": [{"token": f"Swap bass -> {sample}", "prob": 1.0}]})

        # Generar secuencia de notas (MODIFICADO PARA SAMPLES: 0-15)
        # scale = self.scales['minor'] if style in ['techno', 'ambient'] else self.scales['major']
        # Usamos índices directos de samples
        
        # Número de notas según densidad
        num_notes = int(2 + density * 6)  # 2-8 notas
        notes = []
        for _ in range(num_notes):
            note_index = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8]) 
            notes.append(f"{note_index}")
        
        self.rule_thoughts.append({
            "token": "REGLAS: BASS",
            "prob": 0.85,
            "alternatives": [
                {"token": f"Sample: {sample}", "prob": 1.0},
                {"token": f"Notas: {num_notes}", "prob": density}
            ]
        })
        
        notes_str = " ".join(notes)
        
        # Construir patrón
        if complexity < 0.5:
            pattern = f'note "{notes_str}"\n  # sound "{sample}"'
        else:
            # Añadir variación con euclidean
            pattern = f'note "{notes_str}"\n  # sound "{sample}"\n  # speed (range 0.8 1.2 $ slow 4 sine)'
        
        return pattern
    
    def _generate_melody(self, density: float, complexity: float, style: str, friction: float = 0.2) -> str:
        """Generar patrón melódico"""
        
        sample = random.choice(self.melody_samples)

        # FRICCIÓN: Posibilidad de cambiar sample
        if random.random() < friction:
            sample = random.choice(self.melody_samples + self.fx_samples)
            self.rule_thoughts.append({"token": "FRICCIÓN", "prob": friction, "alternatives": [{"token": f"Swap melody -> {sample}", "prob": 1.0}]})
        
        # Detectar si es Synth (necesita notas MIDI) o Sample (necesita indices 0-11)
        # Lista ampliada con todos los super* detectados
        is_synth = sample.startswith("super")
        
        # Generar secuencia melódica
        num_notes = int(4 + density * 8)  # 4-12 notas
        notes = []
        
        # Escala musical
        scale = self.scales['minor'] if style in ['techno', 'ambient'] else self.scales['major']
        octave = 5 # Octava central
        
        for _ in range(num_notes):
            if is_synth:
                # Generar nota MIDI (ej: 60, 64...)
                note_val = random.choice(scale) + (octave * 12)
                notes.append(f"{note_val}")
            else:
                # Generar índice de sample (0-11)
                note_index = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8]) 
                notes.append(f"{note_index}")
        
        notes_str = " ".join(notes)
        
        # Construir patrón
        pattern = f'note "{notes_str}"\n  # sound "{sample}"'
        
        # Efectos según complejidad
        if complexity > 0.5:
            pattern += f'\n  # room {0.3 + complexity * 0.4:.2f}'
        if complexity > 0.7:
            pattern += f'\n  # lpf (range 500 5000 $ slow 8 sine)'
        
        return pattern
    
    def _generate_percussion(self, density: float, complexity: float, style: str, friction: float = 0.2) -> str:
        """Generar patrón de percusión"""
        
        sample = random.choice(self.perc_samples)
        repetitions = int(4 + density * 12)  # 4-16 hits
        
        self.rule_thoughts.append({
            "token": "REGLAS: PERC",
            "prob": 0.75,
            "alternatives": [
                {"token": f"Pasos: {repetitions}", "prob": density}
            ]
        })

        if complexity < 0.5:
            pattern = f'sound "{sample}*{repetitions}"'
        else:
            # Euclidean rhythm
            pattern = f'sound "{sample}({repetitions},{int(16*density)})"'
            
            # FRICCIÓN: Acelerar/Frenar aleatoriamente
            speed_var = 1.0
            if random.random() < friction:
                 speed_var = random.choice([0.5, 2.0, 1.5, 0.75])
                 self.rule_thoughts.append({"token": "FRICCIÓN", "prob": friction, "alternatives": [{"token": f"Speed x{speed_var}", "prob": 1.0}]})

            pattern += f'\n  # speed (range 0.8 {1.5 * speed_var} $ slow 4 sine)'
        
        return pattern
    
    def _generate_fx(self, density: float, complexity: float, style: str, friction: float = 0.2) -> str:
        """Generar patrón de efectos/ambiente"""
        
        sample = random.choice(self.fx_samples)
        
        self.rule_thoughts.append({
            "token": "REGLAS: FX",
            "prob": 0.7,
            "alternatives": [
                {"token": f"Estilo: {style}", "prob": 1.0},
                {"token": f"Complejidad: {complexity}", "prob": complexity}
            ]
        })

        pattern = f'sound "{sample}"'
        pattern += f'\n  # gain {0.3 + density * 0.3:.2f}'
        pattern += f'\n  # room {0.5 + complexity * 0.4:.2f}'
        
        # FRICCIÓN: Chopped FX (striate)
        if random.random() < friction:
            cuts = random.choice([4, 8, 16, 32])
            pattern += f'\n  # striate {cuts}'
            self.rule_thoughts.append({"token": "FRICCIÓN", "prob": friction, "alternatives": [{"token": f"Striate {cuts}", "prob": 1.0}]})

        pattern += f'\n  # size {0.7 + complexity * 0.3:.2f}'
        
        return pattern
    
    def _generate_with_ai(self, temperature: float = 1.0) -> Dict:
        """
        Generar patrón usando modelo Markov.
        
        Args:
            temperature: Controla creatividad (0.5=conservador, 2.0=creativo)
        
        Returns:
            Dict con {"pattern": str, "thoughts": list}
        """
        if not hasattr(self, 'markov'):
            raise ValueError("Modelo Markov no inicializado")
        
        # Generar patrón
        max_tokens = int(20 + temperature * 30)
        result = self.markov.generate(max_tokens=max_tokens, temperature=temperature)
        
        # Validar y retornar
        if self.validate(result["pattern"]):
            return result
        else:
            # Si no es válido, intentar de nuevo
            for _ in range(2):
                result = self.markov.generate(max_tokens=max_tokens, temperature=temperature)
                if self.validate(result["pattern"]):
                    return result
            
            # Si falla, fallback
            return {"pattern": self._generate_drums(0.6, 0.5, "techno"), "thoughts": []}
    
    def validate(self, pattern: str) -> bool:
        """
        Validar sintaxis básica de patrón Tidal.
        
        Args:
            pattern: String con código Tidal
        
        Returns:
            True si parece válido, False si no
        """
        
        # Validaciones básicas
        if not pattern or not isinstance(pattern, str):
            return False
        
        # Debe contener al menos 'sound' o 'note'
        if 'sound' not in pattern and 'note' not in pattern:
            return False
        
        # Comillas balanceadas
        if pattern.count('"') % 2 != 0:
            return False
        
        # Paréntesis balanceados
        if pattern.count('(') != pattern.count(')'):
            return False
        
        # Corchetes balanceados
        if pattern.count('[') != pattern.count(']'):
            return False
        
        # Llaves balanceadas
        if pattern.count('{') != pattern.count('}'):
            return False
        
        # Debe tener al menos un sample o nota entre comillas
        import re
        if not re.search(r'"[^"]+?"', pattern):
            return False
        
        # No debe tener caracteres extraños
        invalid_chars = ['@', '&', '|', ';', '\\']
        if any(char in pattern for char in invalid_chars):
            return False
        
        # Longitud razonable
        if len(pattern) < 10 or len(pattern) > 500:
            return False
        
        return True
    
    def _cleanup_pattern(self, pattern: str) -> str:
        """
        Limpia el patrón de redundancias técnicas que TidalCycles sobreescribiría.
        Si hay múltiples '# sound' o '# note', mantiene solo el primero (la intención principal).
        """
        if not pattern or not isinstance(pattern, str):
            return pattern
            
        import re
        
        # 1. Separar por el operador de unión '#'
        parts = pattern.split('#')
        if len(parts) <= 1:
            return pattern
            
        seen_params = set()
        clean_parts = []
        
        # La primera parte es el cuerpo principal (ej: sound "..." o note "...")
        first_part = parts[0].strip()
        clean_parts.append(first_part)
        
        # Identificar qué parámetro define la primera parte
        if first_part.startswith('sound') or first_part.startswith('s '):
            seen_params.add('sound')
        elif first_part.startswith('note') or first_part.startswith('n '):
            seen_params.add('note')
            
        # Procesar el resto de parámetros (después de cada #)
        for part in parts[1:]:
            part = part.strip()
            if not part: continue
            
            # Extraer el nombre del parámetro (primera palabra)
            param_match = re.match(r'^(\w+)', part)
            if param_match:
                param_name = param_match.group(1)
                
                # REGLA TIDAL: Si el parámetro ya existe, el segundo lo sobreescribiría.
                # Lo eliminamos para evitar confusión y ruido técnico.
                if param_name not in seen_params:
                    clean_parts.append(part)
                    seen_params.add(param_name)
            else:
                clean_parts.append(part)
                
        return " # ".join(clean_parts)
    
    def _post_process_syntax(self, pattern: str) -> str:
        """
        Corrige problemas comunes de sintaxis y errores de formato.
        Fase 16: Asegura que siempre haya un espacio tras el símbolo $
        Fase 11: Corrige formato de floats rotos (ej: '1 00' -> '1.00')
        """
        if not pattern:
            return pattern
            
        import re
        
        # 1. Fix broken floats (digit space digit digit) -> digit.digit digit
        # Catch "1 00" -> "1.00", "0 5" -> "0.5"
        pattern = re.sub(r'(\d+)\s+(\d{1,2})(?!\d)', r'\1.\2', pattern)
        
        # 2. Fix $ operator spacing
        pattern = re.sub(r'\$([^\s\)])', r'$ \1', pattern)
        
        # 3. Validar speed y gain rango
        # Si speed es 0, Tidal explota o no suena. Clamp a 0.1
        pattern = re.sub(r'#\s*speed\s+0(\.0+)?(?!\d)', '# speed 0.1', pattern)
        
        return pattern
    
    def is_hallucination(self, pattern: str) -> bool:
        """
        Detecta si el patrón tiene colisiones técnicas (múltiples sonidos/notas 
        sin estar en un bloque orquestado válido).
        """
        if not pattern or not isinstance(pattern, str):
            return False
            
        import re
        # Limpiar prefijos antes de validar
        clean_pattern = re.sub(r'^d\d+\s*\$\s*', '', pattern.strip())
        parts = [p.strip() for p in clean_pattern.split('#') if p.strip()]
        
        source_keywords = r'^(sound|s|note|n|midinote|drum|kick|snare|hihat|clap|tabla)\b'
        sources = [p for p in parts if re.match(source_keywords, p)]
        
        # Si hay más de una fuente en un solo string, es una "alucinación" técnica
        # (A menos que el usuario esté usando deliberadamente una sintaxis compleja)
        return len(sources) > 1

    def get_layers(self, pattern: str) -> List[Dict]:
        """
        Divide un patrón complejo en capas independientes.
        Versión 2.7: Detecta si la división es necesaria por 'alucinación'.
        """
        if not pattern or not isinstance(pattern, str):
            return [{'offset': 0, 'code': pattern, 'is_hallucination': False}]
            
        import re
        
        is_hallucinating = self.is_hallucination(pattern)
        
        # 1. Normalizar espacios y separar por '#'
        pattern = re.sub(r'^d\d+\s*\$\s*', '', pattern.strip())
        
        parts = []
        for p in pattern.split('#'):
            p = p.strip()
            if not p: continue
            p = re.sub(r'^d\d+\s*\$\s*', '', p)
            parts.append(p)
            
        if not parts:
            return [{'offset': 0, 'code': pattern, 'is_hallucination': False}]
            
        # 2. Identificar "fuentes" y "modificadores"
        sources = []
        modifiers = []
        source_keywords = r'^(sound|s|note|n|midinote|drum|kick|snare|hihat|clap|tabla)\b'
        
        for part in parts:
            if re.match(source_keywords, part):
                sources.append(part)
            else:
                modifiers.append(part)
                
        # 3. Caso especial: primera parte como fuente
        if not sources and parts:
            first_part = parts[0]
            common_mods = r'^(lpf|hpf|room|size|delay|gain|pan|orbit|crush|shape|speed|accelerate|vowel|cutoff|resonance)\b'
            if not re.match(common_mods, first_part):
                sources = [first_part]
                modifiers = parts[1:]
            
        # 4. Construcción de capas
        if len(sources) <= 1:
            final_code = " # ".join(parts)
            return [{'offset': 0, 'code': final_code, 'is_hallucination': is_hallucinating}]
            
        layers = []
        for i, source in enumerate(sources):
            layer_parts = [source] + modifiers
            layer_code = " # ".join(layer_parts)
            layers.append({
                'offset': i,
                'code': layer_code,
                'is_hallucination': is_hallucinating
            })
            
        return layers

    def mutate(self, pattern: str, strength: float = 0.5) -> Dict:
        """
        Toma un patrón existente y aplica mutaciones rítmicas y sintácticas.
        strength: 0.1 (sutil) a 1.0 (radical)
        """
        if not pattern:
            return {"pattern": "", "thoughts": [{"token": "ERROR", "prob": 0, "alts": ["Patrón vacío"]}]}
            
        import re
        thoughts = []
        
        # 1. Limpiar prefijos para trabajar sobre el core
        core = re.sub(r'^d\d+\s*\$\s*', '', pattern.strip())
        
        # 2. Tokenización básica para mutación
        # Separamos por espacios y caracteres especiales pero mantenemos bloques "..."
        tokens = re.findall(r'\"[^\"]*\"|\w+|[*+\-/()[\]{}$#"<>~,]', core)
        
        mutated_tokens = []
        for token in tokens:
            mutation_seed = random.random()
            
            # Estrategia A: Mutar valores numéricos (probabilidad proporcional a strength)
            if re.match(r'^\d+(\.\d+)?$', token) and mutation_seed < (strength * 0.4):
                val = float(token)
                factor = 0.5 if random.random() < 0.5 else 2.0
                new_val = val * factor if val > 0 else 1
                # Limitar valores razonables
                if new_val > 32: new_val = 32
                token = str(int(new_val)) if new_val.is_integer() else f"{new_val:.2f}"
                thoughts.append({"token": "NUM_MUT", "prob": strength, "alts": [f"{val} -> {token}"]})
            
            # Estrategia B: Mutar Samples dentro de comillas
            elif token.startswith('"') and token.endswith('"') and mutation_seed < (strength * 0.3):
                content = token[1:-1]
                # Si es un solo sample (ej: "bd"), intentar cambiarlo por uno similar
                if re.match(r'^\w+$', content):
                    category = None
                    if content in ['bd', 'kick', 'bass']: category = 'kick'
                    elif content in ['sn', 'sd', 'snare']: category = 'snare'
                    elif content in ['hh', 'hat', 'hc']: category = 'hihat'
                    
                    if category and category in self.drum_samples:
                        new_sample = random.choice(self.drum_samples[category])
                        token = f'"{new_sample}"'
                        thoughts.append({"token": "SMP_MUT", "prob": strength, "alts": [f"{content} -> {new_sample}"]})
                
                # Si es una secuencia (ej: "bd sn"), intentar rotarla rítmicamente
                elif ' ' in content:
                    parts = content.split()
                    if len(parts) > 1:
                        # Rota el array 1 posición
                        parts = parts[1:] + [parts[0]]
                        token = f'"{ " ".join(parts) }"'
                        thoughts.append({"token": "ROT_MUT", "prob": strength, "alts": ["Rhythmic Rotation"]})
            
            # Estrategia C: Mutar Operadores (ej: cambiar # por | esporádicamente)
            elif token == '#' and mutation_seed < (strength * 0.1):
                token = '|'
                thoughts.append({"token": "OP_MUT", "prob": strength, "alts": ["# -> |"]})
            
            mutated_tokens.append(token)
            
        # 3. Añadir o quitar efectos según strength
        mutated_pattern = " ".join(mutated_tokens)
        
        # --- GUARANTEED MUTATION CHECK (V3.1 FIX) ---
        # Si la mutación probabilística no hizo nada, forzar un cambio visible
        if mutated_pattern == core and strength > 0.1:
            # Opción 1: Añadir un efecto obvio
            forced_fx = random.choice(["# speed 1.5", "# lpf 1000", "# vowel \"a\"", "# crush 3"])
            mutated_pattern += f" {forced_fx}"
            thoughts.append({"token": "FORCE_MUT", "prob": 1.0, "alts": ["Forced Change"]})
        
        if strength > 0.6 and "#" not in mutated_pattern:
            extra_fx = random.choice(["# lpf 2000", "# crush 4", "# room 0.3", "# speed 1.2"])
            mutated_pattern += f" {extra_fx}"
            thoughts.append({"token": "FX_ADD", "prob": strength, "alts": [extra_fx]})
            
        # 4. Limpieza final de sintaxis
        mutated_pattern = self._post_process_syntax(mutated_pattern)
        mutated_pattern = self._cleanup_pattern(mutated_pattern)
        
        return {"pattern": mutated_pattern, "thoughts": thoughts}

    def suggest_samples(self, current_pattern: str, count: int = 4) -> List[str]:
        """
        Analiza el patrón actual y sugiere samples similares de la librería extendida.
        """
        if not self.extended_samples:
            return []
            
        import re
        # Extraer el sample principal (habitualmente el primer string entre comillas)
        match = re.search(r'\"(\w+)', current_pattern)
        if not match:
            return []
            
        current_sample = match.group(1)
        
        # Encontrar a qué categoría pertenece el sample actual
        target_cat = "uncategorized"
        for cat, samples in self.extended_samples.items():
            if current_sample in samples:
                target_cat = cat
                break
        
        # Obtener sugerencias de la misma categoría
        candidates = self.extended_samples.get(target_cat, [])
        if not candidates:
            # Si no hay, usar percusión o algo genérico
            candidates = self.extended_samples.get("perc", []) + self.extended_samples.get("kick", [])
            
        if not candidates:
            return []
            
        # Filtrar el actual y elegir N aleatorios
        candidates = [s for s in candidates if s != current_sample]
        if len(candidates) > count:
            return random.sample(candidates, count)
        return candidates

    def replace_sample(self, pattern: str, old_sample: str, new_sample: str) -> str:
        """
        Reemplaza un sample por otro en el patrón, manteniendo la estructura.
        """
        if not pattern: return pattern
        import re
        # Reemplazar old_sample como palabra completa en todo el patrón
        # Esto funciona para 'sound "bd sn"', 'bd*4', etc.
        return re.sub(rf'\b{old_sample}\b', new_sample, pattern)

    def morph(self, pattern_a: str, pattern_b: str, ratio: float = 0.5) -> Dict:
        """
        Interpolar entre dos patrones usando mezcla de matrices de transición.
        
        Args:
            pattern_a: Patrón inicial (ratio = 0.0)
            pattern_b: Patrón final (ratio = 1.0)
            ratio: Parámetro de mezcla (0.0 a 1.0)
        """
        # Tokenizar ambos
        tokens_a = self.markov.tokenize(pattern_a) if hasattr(self, 'markov') else pattern_a.split()
        tokens_b = self.markov.tokenize(pattern_b) if hasattr(self, 'markov') else pattern_b.split()
        
        order = 1 # Usamos orden 1 para micro-modelos para mayor flexibilidad
        
        # Construir micro-modelo A
        trans_a = defaultdict(lambda: defaultdict(int))
        for i in range(len(tokens_a) - order):
            state = tuple(tokens_a[i:i + order])
            next_t = tokens_a[i + order]
            trans_a[state][next_t] += 1
            
        # Construir micro-modelo B
        trans_b = defaultdict(lambda: defaultdict(int))
        for i in range(len(tokens_b) - order):
            state = tuple(tokens_b[i:i + order])
            next_t = tokens_b[i + order]
            trans_b[state][next_t] += 1
            
        # Mezclar estados iniciales (basado en ratio)
        starts_a = tokens_a[:order]
        starts_b = tokens_b[:order]
        current_state = starts_a if random.random() > ratio else starts_b
        result = list(current_state)
        
        # Generar híbrido
        max_len = int(len(tokens_a) * (1-ratio) + len(tokens_b) * ratio)
        thoughts = []
        
        for _ in range(max_len):
            state_tuple = tuple(current_state[-order:])
            
            # Obtener opciones de ambos modelos
            opts_a = trans_a.get(state_tuple, {})
            opts_b = trans_b.get(state_tuple, {})
            
            if not opts_a and not opts_b:
                break
                
            # Combinar opciones con pesos
            combined = defaultdict(float)
            
            # Normalizar y añadir pesos de A
            if opts_a:
                total_a = sum(opts_a.values())
                for t, c in opts_a.items():
                    combined[t] += (c / total_a) * (1 - ratio)
                    
            # Normalizar y añadir pesos de B
            if opts_b:
                total_b = sum(opts_b.values())
                for t, c in opts_b.items():
                    combined[t] += (c / total_b) * ratio
            
            # Seleccionar siguiente token
            tokens = list(combined.keys())
            weights = list(combined.values())
            
            # Normalizar pesos finales
            sum_w = sum(weights)
            weights = [w / sum_w for w in weights]
            
            next_token = random.choices(tokens, weights=weights)[0]
            
            # Registrar "pensamiento" del morfado
            thoughts.append({
                "token": next_token,
                "prob": weights[tokens.index(next_token)],
                "alternatives": sorted(
                    [{"token": t, "prob": w} for t, w in zip(tokens, weights)],
                    key=lambda x: x["prob"], reverse=True
                )[:2]
            })
            
            result.append(next_token)
            current_state = result[-order:]
            
        pattern_str = self._reconstruct(result) if hasattr(self, 'markov') else " ".join(result)
        
        return {
            "pattern": pattern_str,
            "thoughts": thoughts,
            "ratio": ratio
        }

    def get_random_style(self) -> str:
        """Obtener estilo aleatorio"""
        styles = ['techno', 'ambient', 'breakbeat', 'house', 'experimental']
        return random.choice(styles)

    def generate_fill(self, style: str = "techno") -> Dict:
        """
        Genera un 'Fill' (redoble/transición) corto y de alta energía.
        Enfocado en percusión rápida y variaciones de velocidad.
        """
        # Un fill siempre tiene alta densidad y complejidad por definición
        density = 0.9
        complexity = 0.8
        
        # Usamos percusión o drums para el fill
        p_type = random.choice(["drums", "percussion"])
        
        # Generar patrón base
        res = self.generate(
            pattern_type=p_type, 
            density=density, 
            complexity=complexity, 
            style=style, 
            use_ai=True # Preferimos IA para fills por imprevisibilidad
        )
        
        # Inyectar "Fricción" agresiva (chopped logic)
        pattern = res["pattern"]
        
        # Asegurar que sea corto (fast)
        pattern += "\n  # fast 2"
        
        # Añadir un filtro resonante que se abre (barrido de frecuencia)
        pattern += "\n  # hpf (line 100 2000 1)"
        pattern += "\n  # resonance 0.2"
        
        res["pattern"] = pattern
        res["thoughts"].append({"token": "FILL_ENGINE", "prob": 1.0, "alts": ["High Energy Transition"]})
        
        return res


    # --- FASE 36: UTILITIES DE CONTEXTO ---

    def _calculate_similarity(self, p1: str, p2: str) -> float:
        """Calcula similitud basada en tokens únicos compartidos."""
        set1 = set(p1.split())
        set2 = set(p2.split())
        if not set1 or not set2: return 0.0
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        return len(intersection) / len(union)

    def _update_history(self, pattern: str):
        """Añade patrón al historial y mantiene tamaño máximo."""
        self.pattern_history.append(pattern)
        if len(self.pattern_history) > self.max_history:
            self.pattern_history.pop(0)

    def _humanize_pattern(self, pattern: str) -> str:
        """Añade sutiles desviaciones a los valores numéricos para sonar menos robótico."""
        import re
        
        def hum(match):
            val = float(match.group(2))
            # Desviación de +/- 2% máximo
            deviation = (random.random() * 0.04) - 0.02
            new_val = val + (val * deviation)
            return f"{match.group(1)} {new_val:.3f}"

        # Humanizar gain, speed, pan, room, size
        params = "(gain|speed|pan|room|size|resonance|cutoff|lpf|hpf)"
        # Regex que busca el parámetro seguido de un espacio y un número
        pattern = re.sub(rf'(#\s+{params})\s+(\d+\.?\d*)', hum, pattern)
        return pattern


# Ejemplo de uso
if __name__ == "__main__":
    generator = PatternGenerator()
    
    print("=== TidalAI Pattern Generator - Ejemplos ===\n")
    
    # Ejemplo 1: Drums techno
    print("1. Drums Techno (densidad: 0.7, complejidad: 0.6)")
    pattern = generator.generate("drums", density=0.7, complexity=0.6, style="techno")
    print(f"d1 $ {pattern}\n")
    
    # Ejemplo 2: Bass ambient
    print("2. Bass Ambient (densidad: 0.4, complejidad: 0.3)")
    pattern = generator.generate("bass", density=0.4, complexity=0.3, style="ambient")
    print(f"d2 $ {pattern}\n")
    
    # Ejemplo 3: Melody compleja
    print("3. Melody (densidad: 0.8, complejidad: 0.9)")
    pattern = generator.generate("melody", density=0.8, complexity=0.9, style="techno")
    print(f"d3 $ {pattern}\n")
    
    # Validación
    print("4. Validación de patrones:")
    valid_pattern = 'sound "bd sn"'
    invalid_pattern = 'sound "bd sn'
    print(f"  '{valid_pattern}' -> {generator.validate(valid_pattern)}")
    print(f"  '{invalid_pattern}' -> {generator.validate(invalid_pattern)}")
