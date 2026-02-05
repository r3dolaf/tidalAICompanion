"""
Latent Space Engine (Fase 18)
Motor de interpolación vectorial entre géneros musicales.
Permite crear híbridos únicos mezclando parámetros de múltiples estilos.
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

class LatentEngine:
    def __init__(self, rules_file='theory_rules.json'):
        self.rules_file = os.path.join(os.path.dirname(__file__), rules_file)
        self.available_genres = self._load_genres()
        self.genre_vectors = self._init_vectors()
        logger.info(f"Latent Engine initialized with {len(self.available_genres)} genres")
    
    def _load_genres(self):
        """Lee los géneros disponibles desde theory_rules.json"""
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r') as f:
                    rules = json.load(f)
                    return list(rules.keys())
            except Exception as e:
                logger.error(f"Error loading genres from rules: {e}")
                return []
        return []
    
    def _init_vectors(self):
        """
        Define vectores de parámetros para cada género conocido.
        Estos son los "embeddings" que se interpolarán.
        """
        # Parámetros base por género (ajustables)
        base_vectors = {
            "techno": {
                "density_base": 0.8,
                "complexity_base": 0.6,
                "tempo_preference": 140,
                "preferred_samples": ["bd", "hh", "sn", "cp", "clap"],
                "rhythmic_weight": 0.9  # Qué tan rítmico es (0-1)
            },
            "house": {
                "density_base": 0.7,
                "complexity_base": 0.5,
                "tempo_preference": 125,
                "preferred_samples": ["bd", "sn", "cp", "oh", "ch"],
                "rhythmic_weight": 0.8
            },
            "drum_and_bass": {
                "density_base": 0.9,
                "complexity_base": 0.8,
                "tempo_preference": 174,
                "preferred_samples": ["bd", "sn", "hh", "reese"],
                "rhythmic_weight": 0.95
            },
            "ambient": {
                "density_base": 0.3,
                "complexity_base": 0.4,
                "tempo_preference": 90,
                "preferred_samples": ["pad", "texture", "wind", "space"],
                "rhythmic_weight": 0.2
            },
            "breakbeat": {
                "density_base": 0.75,
                "complexity_base": 0.7,
                "tempo_preference": 135,
                "preferred_samples": ["bd", "sn", "hh", "break"],
                "rhythmic_weight": 0.85
            },
            "dub": {
                "density_base": 0.5,
                "complexity_base": 0.4,
                "tempo_preference": 110,
                "preferred_samples": ["bd", "sn", "delay", "echo"],
                "rhythmic_weight": 0.6
            },
            "experimental": {
                "density_base": 0.6,
                "complexity_base": 0.9,
                "tempo_preference": 120,
                "preferred_samples": ["noise", "glitch", "fx"],
                "rhythmic_weight": 0.5
            }
        }
        
        # Crear vectores solo para géneros que existen en theory_rules.json
        vectors = {}
        for genre in self.available_genres:
            if genre in base_vectors:
                vectors[genre] = base_vectors[genre]
            else:
                # Género custom: usar valores neutros
                vectors[genre] = {
                    "density_base": 0.5,
                    "complexity_base": 0.5,
                    "tempo_preference": 120,
                    "preferred_samples": [],
                    "rhythmic_weight": 0.5
                }
                logger.warning(f"Genre '{genre}' not in base vectors, using defaults")
        
        return vectors
    
    def get_available_genres(self):
        """Retorna lista de géneros disponibles para mezclar"""
        return self.available_genres
    
    def interpolate(self, genre_a, genre_b, weight_b):
        """
        Interpola entre dos géneros.
        weight_b: 0.0 = 100% A, 1.0 = 100% B
        """
        if genre_a not in self.genre_vectors or genre_b not in self.genre_vectors:
            logger.error(f"Invalid genres for interpolation: {genre_a}, {genre_b}")
            return None
        
        vec_a = self.genre_vectors[genre_a]
        vec_b = self.genre_vectors[genre_b]
        weight_a = 1.0 - weight_b
        
        # Interpolación lineal de parámetros numéricos
        result = {
            "density_base": (vec_a["density_base"] * weight_a) + (vec_b["density_base"] * weight_b),
            "complexity_base": (vec_a["complexity_base"] * weight_a) + (vec_b["complexity_base"] * weight_b),
            "tempo_preference": int((vec_a["tempo_preference"] * weight_a) + (vec_b["tempo_preference"] * weight_b)),
            "rhythmic_weight": (vec_a["rhythmic_weight"] * weight_a) + (vec_b["rhythmic_weight"] * weight_b),
            "blend_info": {
                "genre_a": genre_a,
                "genre_b": genre_b,
                "weight_a": weight_a,
                "weight_b": weight_b
            }
        }
        
        # Mezclar samples (unión ponderada)
        # Si weight_b > 0.5, priorizar samples de B
        if weight_b > 0.5:
            result["preferred_samples"] = vec_b["preferred_samples"] + vec_a["preferred_samples"][:2]
        else:
            result["preferred_samples"] = vec_a["preferred_samples"] + vec_b["preferred_samples"][:2]
        
        return result
    
    def blend_multiple(self, blend_config):
        """
        Mezcla múltiples géneros con pesos arbitrarios.
        blend_config: {"techno": 0.5, "ambient": 0.3, "house": 0.2}
        """
        # Normalizar pesos para que sumen 1.0
        total = sum(blend_config.values())
        if total == 0:
            return None
        
        normalized = {k: v/total for k, v in blend_config.items()}
        
        # Inicializar resultado
        result = {
            "density_base": 0.0,
            "complexity_base": 0.0,
            "tempo_preference": 0,
            "rhythmic_weight": 0.0,
            "preferred_samples": [],
            "blend_info": normalized
        }
        
        # Sumar contribuciones ponderadas
        for genre, weight in normalized.items():
            if genre not in self.genre_vectors:
                continue
            vec = self.genre_vectors[genre]
            result["density_base"] += vec["density_base"] * weight
            result["complexity_base"] += vec["complexity_base"] * weight
            result["tempo_preference"] += int(vec["tempo_preference"] * weight)
            result["rhythmic_weight"] += vec["rhythmic_weight"] * weight
            
            # Añadir samples según peso (más peso = más samples)
            sample_count = max(1, int(len(vec["preferred_samples"]) * weight * 2))
            result["preferred_samples"].extend(vec["preferred_samples"][:sample_count])
        
        # Eliminar duplicados de samples manteniendo orden
        seen = set()
        unique_samples = []
        for s in result["preferred_samples"]:
            if s not in seen:
                seen.add(s)
                unique_samples.append(s)
        result["preferred_samples"] = unique_samples
        
        return result
    
    def get_hybrid_params(self, blend_config):
        """
        Retorna parámetros finales para el generador basados en la mezcla.
        Alias de blend_multiple para compatibilidad con API.
        """
        return self.blend_multiple(blend_config)
