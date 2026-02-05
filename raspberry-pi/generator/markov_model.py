"""
TidalAI Companion - Markov Chain Model
Modelo de cadenas de Markov para generar patrones TidalCycles basados en ejemplos.
"""

import random
import json
import os
from collections import defaultdict
from typing import List, Dict, Tuple
import re


class MarkovModel:
    """
    Modelo de Markov para generar patrones TidalCycles.
    
    Aprende de un corpus de patrones existentes y genera nuevos
    patrones basados en las probabilidades aprendidas.
    """
    
    def __init__(self, order: int = 2):
        """
        Inicializar modelo.
        
        Args:
            order: Orden del modelo Markov (número de tokens de contexto)
        """
        self.order = order
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.starts = []
        self.trained = False
    
    def tokenize(self, pattern: str) -> List[str]:
        """
        Tokenizar patrón TidalCycles.
        
        Args:
            pattern: String con código Tidal
        
        Returns:
            Lista de tokens
        """
        # Remover comentarios
        pattern = re.sub(r'--.*$', '', pattern, flags=re.MULTILINE)
        
        # Tokenizar por espacios y símbolos especiales
        tokens = re.findall(r'\w+|[*+\-/()[\]{}$#"<>~,]', pattern)
        
        return [t for t in tokens if t.strip()]
    
    def train(self, patterns: List[str]):
        """
        Entrenar modelo con corpus de patrones.
        
        Args:
            patterns: Lista de patrones TidalCycles
        """
        for pattern in patterns:
            tokens = self.tokenize(pattern)
            
            if len(tokens) < self.order + 1:
                continue
            
            # Guardar inicio
            self.starts.append(tuple(tokens[:self.order]))
            
            # Construir transiciones
            for i in range(len(tokens) - self.order):
                state = tuple(tokens[i:i + self.order])
                next_token = tokens[i + self.order]
                self.transitions[state][next_token] += 1
        
        self.trained = True
        print(f"Modelo entrenado con {len(patterns)} patrones")
        print(f"Estados únicos: {len(self.transitions)}")
    
    def generate(self, max_tokens: int = 50, temperature: float = 1.0) -> Dict:
        """
        Generar nuevo patrón y devolver el proceso de 'pensamiento'.
        """
        if not self.trained:
            raise ValueError("Modelo no entrenado. Llama a train() primero.")
        
        if not self.starts:
            return {"pattern": "", "thoughts": []}
        
        # Comenzar con un estado inicial aleatorio
        current_state = list(random.choice(self.starts))
        result = list(current_state)
        thoughts = []
        
        # Registrar el inicio
        thoughts.append({
            "token": " ".join(current_state),
            "prob": 1.0,
            "alternatives": []
        })
        
        for _ in range(max_tokens - self.order):
            state_tuple = tuple(current_state[-self.order:])
            
            if state_tuple not in self.transitions:
                break
            
            # Obtener posibles siguientes tokens
            next_tokens = self.transitions[state_tuple]
            
            # Aplicar temperatura y calcular probabilidades
            total = sum(next_tokens.values())
            choices = list(next_tokens.keys())
            
            # Calcular distribución original (para visualización)
            original_probs = {t: (next_tokens[t] / total) for t in choices}
            
            if temperature != 1.0:
                adjusted = {}
                for token, count in next_tokens.items():
                    prob = count / total
                    adjusted[token] = prob ** (1.0 / temperature)
                
                total_adjusted = sum(adjusted.values())
                weights = [adjusted[c] / total_adjusted for c in choices]
            else:
                weights = [next_tokens[c] / total for c in choices]
            
            # Seleccionar siguiente token
            next_token = random.choices(choices, weights=weights)[0]
            
            # Registrar pensamiento
            thoughts.append({
                "token": next_token,
                "prob": weights[choices.index(next_token)],
                "alternatives": sorted(
                    [{"token": c, "prob": w} for c, w in zip(choices, weights)],
                    key=lambda x: x["prob"], reverse=True
                )[:3] # Top 3 alternativas
            })
            
            result.append(next_token)
            current_state.append(next_token)
        
        return {
            "pattern": self._reconstruct(result),
            "thoughts": thoughts
        }
    
    def _reconstruct(self, tokens: List[str]) -> str:
        """
        Reconstruir patrón desde tokens.
        
        Args:
            tokens: Lista de tokens
        
        Returns:
            String con espaciado apropiado
        """
        result = []
        for i, token in enumerate(tokens):
            # Añadir espacios apropiados
            if i > 0:
                prev = tokens[i - 1]
                # No añadir espacio antes de ciertos símbolos
                if token not in [')', ']', '}', ',', '*', '+', '-', '/']:
                    # No añadir espacio después de ciertos símbolos
                    if prev not in ['(', '[', '{', '$', '#', '"']:
                        result.append(' ')
            
            result.append(token)
        
        return ''.join(result)
    
    def save(self, filepath: str):
        """Guardar modelo a archivo JSON"""
        data = {
            'order': self.order,
            'transitions': {
                str(k): dict(v) for k, v in self.transitions.items()
            },
            'starts': [list(s) for s in self.starts]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Modelo guardado en {filepath}")
    
    def load(self, filepath: str):
        """Cargar modelo desde archivo JSON"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.order = data['order']
        self.starts = [tuple(s) for s in data['starts']]
        
        # Reconstruir transitions
        self.transitions = defaultdict(lambda: defaultdict(int))
        for state_str, next_tokens in data['transitions'].items():
            state = eval(state_str)  # Convertir string a tuple
            for token, count in next_tokens.items():
                self.transitions[state][token] = count
        
        self.trained = True
        print(f"Modelo cargado desde {filepath}")

    def to_graph_json(self, limit=100):
        """
        Convierte el modelo en un formato de grafo (nodos y enlaces).
        Simplifica los estados (tuplas) a tokens individuales para visualización.
        """
        nodes_dict = {}
        links_dict = defaultdict(int)
        
        # Procesar transiciones para crear enlaces entre tokens
        for state, next_tokens in self.transitions.items():
            # El último token del estado apunta al siguiente token
            source = state[-1]
            for target, count in next_tokens.items():
                # Crear clave única para el enlace
                link_key = (source, target)
                links_dict[link_key] += count
                
                # Registrar nodos
                nodes_dict[source] = nodes_dict.get(source, 0) + count
                nodes_dict[target] = nodes_dict.get(target, 0) + count
        
        # Ordenar nodos por importancia (frecuencia) y limitar
        sorted_nodes = sorted(nodes_dict.items(), key=lambda x: x[1], reverse=True)[:limit]
        top_tokens = {node[0] for node in sorted_nodes}
        
        nodes = []
        for token, weight in sorted_nodes:
            # Determinar tipo de nodo
            node_type = "function"
            if '"' in token: node_type = "sample"
            elif token.isdigit(): node_type = "number"
            elif token in ['$', '#']: node_type = "operator"
            
            nodes.append({
                "id": token,
                "label": token,
                "weight": weight,
                "type": node_type
            })
            
        links = []
        for (src, tgt), val in links_dict.items():
            if src in top_tokens and tgt in top_tokens:
                links.append({
                    "source": src,
                    "target": tgt,
                    "value": val
                })
                
        return {
            "nodes": nodes,
            "links": links
        }


# Corpus personalizado - Basado en samples REALES del usuario
# Todos estos samples están verificados como instalados
EXAMPLE_CORPUS = [
    # Drums básicos - Kicks (bd, 808bd, clubkick, hardkick)
    'sound "bd sn"',
    'sound "bd sn hh sn"',
    'sound "bd sn cp hh"',
    'sound "bd*4 sn*2"',
    'sound "bd*4 sn*2 hh*8"',
    'sound "808bd*4 sn*2"',
    'sound "808bd(3,8) 808sd(5,8)"',
    'sound "clubkick*4"',
    'sound "hardkick(3,8)"',
    
    # Euclidean rhythms
    'sound "bd(3,8)"',
    'sound "bd(5,8)"',
    'sound "bd(3,8) sn(5,8)"',
    'sound "bd(3,8) sn(5,8) hh*16"',
    'sound "bd(5,8) cp(3,8)"',
    'sound "808bd(7,16) 808sd(5,16)"',
    
    # Snares (sn, 808sd)
    'sound "sn*4"',
    'sound "sn(3,8)"',
    'sound "sn ~ sn ~"',
    'sound "808sd*2"',
    'sound "808sd(5,8)"',
    
    # Hi-hats (hh, hh27, 808hc, 808oh)
    'sound "hh*8"',
    'sound "hh*16"',
    'sound "hh(11,16)"',
    'sound "hh27*16"',
    'sound "808hc*8"',
    'sound "808oh*4"',
    
    # Claps (cp, realclaps)
    'sound "cp*4"',
    'sound "cp(3,8)"',
    'sound "cp ~ cp ~"',
    'sound "realclaps*2"',
    
    # Cymbals
    'sound "808cy*2"',
    
    # Toms (ht, mt, lt, 808ht, 808mt, 808lt)
    'sound "ht mt lt"',
    'sound "808ht 808mt 808lt"',
    
    # Percussion (tabla, tabla2)
    'sound "tabla*8"',
    'sound "tabla*8" # speed 1.5',
    'sound "tabla(7,16)"',
    'sound "tabla2*8"',
    'sound "tabla2(5,8)"',
    
    # Bass synths (bass, bass1, bass2, bass3, jungbass, jvbass)
    'note "0 3 7 5" # sound "bass"',
    'note "0 5 7 12" # sound "bass"',
    'note "0 3 7" # sound "bass1"',
    'note "0 5 7 12" # sound "bass1"',
    'note "0 3 7 10" # sound "bass2"',
    'note "0 4 7" # sound "bass3"',
    'note "0 3 7 5" # sound "jungbass"',
    'note "0 7 12" # sound "jungbass"',
    'note "0 5 7" # sound "jvbass"',
    
    # Melody (arpy, gtr, sitar)
    'note "0 2 4 7" # sound "arpy"',
    'note "0 4 7 12" # sound "arpy"',
    'note "0 3 7 12" # sound "arpy"',
    'note "0 2 4 7" # sound "gtr"',
    'note "0 4 7" # sound "gtr"',
    'note "0 3 7 10" # sound "sitar"',
    
    # Efectos básicos
    'sound "bd sn" # speed 1.2',
    'sound "bd*4 sn*2" # room 0.3',
    'sound "hh*16" # gain 0.8',
    'sound "bd sn cp hh" # speed 1.1',
    'sound "bd*4" # room 0.4',
    'sound "bd sn" # lpf 1000',
    'sound "hh*16" # cutoff 2000',
    'sound "sn*4" # room 0.3 # size 0.8',
    
    # Patterns estructurados
    'sound "[bd sn] [bd cp]"',
    'sound "[bd bd] [sn cp]"',
    'sound "bd [sn sn] hh [cp cp]"',
    'sound "[hh hh] [hh ~]"',
    'sound "[808bd 808bd] [808sd cp]"',
    
    # Combinaciones
    'sound "bd sn hh cp"',
    'sound "bd*4 sn*2 hh*8 cp*2"',
    'sound "bd(3,8) sn(5,8) hh(11,16)"',
    'sound "bd sn ~ cp"',
    'sound "bd*4 [sn cp] hh*8"',
    'sound "808bd*4 808sd*2 808hc*8"',
    
    # Con silencios (~)
    'sound "bd ~ sn ~"',
    'sound "bd ~ ~ sn"',
    'sound "~ bd sn ~"',
    'sound "bd bd ~ sn"',
    'sound "bd ~ sn sn"',
    'sound "~ hh ~ hh"',
    
    # Efectos avanzados
    'sound "bd sn" # speed (range 0.8 1.2 $ slow 4 sine)',
    'sound "hh*16" # pan (range 0 1 $ slow 8 sine)',
    'sound "bd*4" # gain (range 0.8 1 $ slow 2 sine)',
    'sound "bd sn" # lpf (range 200 2000 $ slow 8 sine)',
    'sound "hh*16" # hpf 1000',
    
    # Jungle/Breaks (jungle, amencutup)
    'sound "jungle*4"',
    'sound "jungle(5,8)"',
    'sound "amencutup*8"',
    
    # Techno (techno, tech)
    'sound "techno*4"',
    'sound "tech*8"',
    
    # Glitch (glitch, glitch2)
    'sound "glitch*8"',
    'sound "glitch(7,16)"',
    'sound "glitch2*4"',
    
    # Ambient/FX (wind, space, birds)
    'sound "wind" # gain 0.5',
    'sound "space" # room 0.8',
    'sound "birds" # gain 0.4',
    
    # Vocales (yeah, speech)
    'sound "yeah*4"',
    'sound "speech*2"',
    
    # Números
    'sound "numbers*8"',
]


def create_default_corpus():
    """Crear corpus por defecto en examples/corpus/"""
    corpus_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus')
    os.makedirs(corpus_dir, exist_ok=True)
    
    corpus_file = os.path.join(corpus_dir, 'default_patterns.txt')
    
    with open(corpus_file, 'w') as f:
        for pattern in EXAMPLE_CORPUS:
            f.write(pattern + '\n')
    
    print(f"Corpus por defecto creado en {corpus_file}")
    return corpus_file


# Ejemplo de uso
if __name__ == "__main__":
    print("=== TidalAI Markov Model - Demo ===\n")
    
    # Crear modelo
    model = MarkovModel(order=2)
    
    # Entrenar con corpus de ejemplo
    print("Entrenando modelo...")
    model.train(EXAMPLE_CORPUS)
    
    print("\n=== Patrones Generados ===\n")
    
    # Generar varios patrones con diferentes temperaturas
    print("1. Temperatura baja (conservador):")
    pattern = model.generate(max_tokens=30, temperature=0.5)
    print(f"   {pattern}\n")
    
    print("2. Temperatura media (balanceado):")
    pattern = model.generate(max_tokens=30, temperature=1.0)
    print(f"   {pattern}\n")
    
    print("3. Temperatura alta (creativo):")
    pattern = model.generate(max_tokens=30, temperature=1.5)
    print(f"   {pattern}\n")
    
    # Guardar modelo
    model_path = os.path.join(os.path.dirname(__file__), 'markov_model.json')
    model.save(model_path)
    
    # Crear corpus por defecto
    create_default_corpus()
