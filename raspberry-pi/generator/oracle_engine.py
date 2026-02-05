"""
TidalAI Companion - Oracle Engine
Mapeador semántico que traduce intenciones en parámetros técnicos de TidalCycles.
Optimizado para ejecución ligera en Raspberry Pi.
"""

import re

class OracleEngine:
    def __init__(self):
        # Diccionario maestro de intenciones
        # Cada entrada contiene descriptores y sus efectos en los parámetros
        self.lexicon = {
            # --- ATMÓSFERA ---
            "oscuro": {"complexity": +0.2, "tokens": ["# lpf 800", "# crush 3"], "style_pref": "industrial"},
            "brillante": {"complexity": +0.1, "tokens": ["# hpf 2000"], "style_pref": "experimental"},
            "espacial": {"density": -0.2, "complexity": +0.2, "tokens": ["# delay 0.7 # delayfb 0.5"], "style_pref": "ambient"},
            "sucio": {"complexity": +0.3, "tokens": ["# crush 2", "# dist 0.4"], "style_pref": "industrial"},
            "limpio": {"complexity": -0.2, "tokens": ["# gain 1"], "style_pref": "house"},
            
            # --- ENERGÍA ---
            "agresivo": {"density": +0.3, "complexity": +0.3, "tokens": ["*2", "# speed 1.2"]},
            "relajado": {"density": -0.3, "complexity": -0.2, "tokens": ["/2"], "style_pref": "ambient"},
            "minimal": {"density": -0.4, "complexity": -0.4, "tokens": [], "style_pref": "techno"},
            "caótico": {"complexity": +0.5, "tokens": ["jux(rev)", "iter 4"], "style_pref": "experimental"},
            "denso": {"density": +0.4, "tokens": ["*4"]},
            
            # --- ESTILO ---
            "tribal": {"style_pref": "ethnic", "density": +0.1},
            "acid": {"style_pref": "experimental", "tokens": ["# resonance 0.4 # cutoff 0.2"]},
            "dub": {"style_pref": "ambient", "tokens": ["# delay 0.8 # lock 1"], "tempo_mod": -20},
            "hard": {"style_pref": "industrial", "density": +0.2, "tempo_mod": +10},
            
            # --- DINÁMICA (Modificadores relativos) ---
            "más": {"multiplier": 1.2},
            "menos": {"multiplier": 0.8},
            "sube": {"multiplier": 1.1},
            "baja": {"multiplier": 0.9}
        }
        
        # Mapeo de sinónimos para mayor flexibilidad
        self.synonyms = {
            "dark": "oscuro", "bright": "brillante", "space": "espacial", "dirty": "sucio", "clean": "limpio",
            "aggressive": "agresivo", "chill": "relajado", "soft": "relajado", "chaos": "caótico", "dense": "denso",
            "fast": "agresivo", "slow": "relajado", "deep": "dub", "industrial": "industrial",
            "hazlo": None, "pone": None, "quiero": None, "algo": None, "sonido": None
        }

    def interpret(self, text):
        """Traduce un texto en un objeto de parámetros técnicos"""
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        
        result = {
            "density_offset": 0.0,
            "complexity_offset": 0.0,
            "extra_tokens": [],
            "style_pref": None,
            "tempo_mod": 0,
            "detected_keywords": []
        }
        
        multiplier = 1.0
        
        # Primero procesamos multiplicadores de dinámica
        for word in words:
            intent = self.lexicon.get(word) or self.lexicon.get(self.synonyms.get(word))
            if intent and "multiplier" in intent:
                multiplier *= intent["multiplier"]
                result["detected_keywords"].append(word)

        # Luego procesamos el resto de palabras
        for word in words:
            key = self.synonyms.get(word, word)
            intent = self.lexicon.get(key)
            
            if intent:
                if "multiplier" in intent: continue # Ya procesado
                
                result["detected_keywords"].append(word)
                if "density" in intent: result["density_offset"] += intent["density"] * multiplier
                if "complexity" in intent: result["complexity_offset"] += intent["complexity"] * multiplier
                if "tokens" in intent: result["extra_tokens"].extend(intent["tokens"])
                if "style_pref" in intent: result["style_pref"] = intent["style_pref"]
                if "tempo_mod" in intent: result["tempo_mod"] += intent["tempo_mod"]

        # Limitar offsets para no romper los sliders (0.0 a 1.0 suele ser el rango)
        # Aquí permitimos que el generador maneje los límites finales
        
        return result

# Singleton para uso global
oracle = OracleEngine()
