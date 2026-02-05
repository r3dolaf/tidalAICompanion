import sys
import os
import random
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Configuración
# Nota: Rutas relativas asumiendo ejecución desde app.py (en ../web/)
CORPUS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'patterns.txt')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config_evolution.json')

class EvolutionaryTrainer:
    """
    Entrenador evolutivo que usa el generador actual para crear 
    nuevas generaciones de patrones y seleccionar los mejores.
    """
    
    def __init__(self, generator_instance):
        self.generator = generator_instance
        self.config = self._load_config()
        
    def _load_config(self):
        import json
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando config: {e}")
            
        # Fallback defaults
        return {
            "weights": {"density": 1.0, "variety": 1.0, "complexity": 1.0, "euclidean": 1.0},
            "params": {"temperature": 1.2, "batch_size": 50, "top_k": 10, "strictness": 0},
            "filters": {"genre": "all", "instrument": "all"}
        }

    def evaluate(self, pattern):
        """Puntúa un patrón (0-100) basándose en pesos dinámicos."""
        total_score = 0.0
        w = self.config.get("weights", {})
        
        # 1. Sanity Check (Always strict)
        if not pattern or len(pattern) < 5: return -100
        if pattern.count('"') % 2 != 0: return -100
        if "NaN" in pattern: return -100
        
        # 2. Densidad
        score_density = 0
        events = len(re.findall(r'[a-z0-9]+', pattern))
        if events == 0: return -50
        length = len(pattern)
        density_ratio = events / (length / 3.0) 
        
        if 0.3 <= density_ratio <= 0.8: score_density = 20
        else: score_density = -10
        
        total_score += score_density * w.get("density", 1.0)
            
        # 3. Variedad
        score_variety = 0
        tokens = pattern.split()
        unique_tokens = len(set(tokens))
        variety_ratio = unique_tokens / len(tokens) if tokens else 0
        
        if variety_ratio > 0.5: score_variety = 15
        elif variety_ratio < 0.2: score_variety = -20
        
        total_score += score_variety * w.get("variety", 1.0)
            
        # 4. Complejidad
        score_complexity = 0
        advanced_funcs = ['every', 'fast', 'slow', 'jux', 'iter', 'rev', 'palindrome', 'struct']
        for func in advanced_funcs:
            if func in pattern:
                score_complexity += 10
        
        total_score += score_complexity * w.get("complexity", 1.0)
                
        # 5. Euclidiano
        score_euclidean = 0
        if "(" in pattern and "," in pattern:
            score_euclidean = 15
            
        total_score += score_euclidean * w.get("euclidean", 1.0)
            
        return total_score

    def run_evolution(self, batch_size=None, top_k=None):
        """Ejecuta una ronda de evolución usando parámetros de config."""
        p = self.config.get("params", {})
        batch_size = batch_size or p.get("batch_size", 50)
        top_k = top_k or p.get("top_k", 10)
        temp_val = p.get("temperature", 1.2)
        strictness = p.get("strictness", 0)
        
        candidates = []
        logger.info(f"Iniciando evolución dinámica: {batch_size} candidatos, T={temp_val}")
        
        # Filtros de género/instrumento
        f = self.config.get("filters", {})
        p_type_fixed = f.get("instrument") if f.get("instrument") != "all" else None
        style_fixed = f.get("genre") if f.get("genre") != "all" else "experimental"
        
        for i in range(batch_size):
            try:
                p_type = p_type_fixed or random.choice(['drums', 'bass', 'melody', 'percussion', 'fx'])
                
                result = self.generator.generate(
                    pattern_type=p_type,
                    style=style_fixed,
                    temperature=temp_val
                )
                candidates.append(result["pattern"])
            except Exception as e:
                logger.error(f"Error generando candidato: {e}")
                
        scored = []
        for pat in candidates:
            s = self.evaluate(pat)
            scored.append((s, pat))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        survivors = scored[:top_k]
        
        added_count = 0
        valid_survivors = [s for s in survivors if s[0] > strictness]
        
        if valid_survivors:
            try:
                with open(CORPUS_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"\n# --- EVOLUTIONARY RUN {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")
                    for score, pat in valid_survivors:
                        f.write(f"{pat}\n")
                        added_count += 1
                logger.info(f"Guardados {added_count} patrones evolutivos")
            except Exception as e:
                logger.error(f"Error guardando corpus: {e}")
                
        return {
            "generated": batch_size,
            "survivors": len(valid_survivors),
            "top_score": valid_survivors[0][0] if valid_survivors else 0,
            "patterns": [s[1] for s in valid_survivors]
        }
