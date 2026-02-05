import sys
import os
import random
import re
from datetime import datetime

# Añadir path del generador para poder importarlo
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'raspberry-pi', 'generator'))

try:
    from pattern_generator import PatternGenerator
except ImportError:
    print("Error: No se pudo importar PatternGenerator. Verifica la ruta.")
    sys.exit(1)

# Configurar encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

# Configuración
CORPUS_FILE = os.path.join(os.path.dirname(__file__), '..', 'examples', 'corpus', 'evolution.txt')
GEN_BATCH_SIZE = 50  # Cuántos generar por ronda
TOP_K = 10           # Cuántos guardar

class PatternCritic:
    """Crítico artificial que puntúa patrones basado en 'estética matemática'."""
    
    @staticmethod
    def score(pattern):
        score = 0.0
        
        # 1. Test de Sanidad (0 o 100)
        if not pattern or len(pattern) < 5: return -100
        if pattern.count('"') % 2 != 0: return -100 # Comillas desbalanceadas
        if "NaN" in pattern: return -100
        
        # 2. Densidad (Preferimos 30% - 80%)
        # Calculamos densidad aprox contando eventos vs silencios/espacios
        # Esto es muy heurístico
        events = len(re.findall(r'[a-z0-9]+', pattern))
        if events == 0: return -50
        
        # Longitud visual
        length = len(pattern)
        density_ratio = events / (length / 3.0) # Ajuste a ojo
        
        if 0.3 <= density_ratio <= 0.8:
            score += 20
        elif density_ratio > 0.9: # Demasiado denso
            score -= 10
        else: # Demasiado vacío
            score -= 10
            
        # 3. Variedad (Penalizar repetición excesiva)
        tokens = pattern.split()
        unique_tokens = len(set(tokens))
        variety_ratio = unique_tokens / len(tokens) if tokens else 0
        
        if variety_ratio > 0.5: # Buena variedad
            score += 15
        elif variety_ratio < 0.2: # Muy repetitivo (ej: bd bd bd bd)
            score -= 20
            
        # 4. Complejidad Sintáctica (Bonificación por uso de funciones)
        advanced_funcs = ['every', 'fast', 'slow', 'jux', 'iter', 'rev', 'palindrome']
        for func in advanced_funcs:
            if func in pattern:
                score += 10
        
        # 5. Estructura Euclidiana (Bonificación)
        if "(" in pattern and "," in pattern:
            score += 15
            
        return score

def main():
    print(f"🧬 Iniciando Entrenador Evolutivo...")
    print(f"Batch: {GEN_BATCH_SIZE} | Selección: Top {TOP_K}")
    
    # Inicializar generador
    generator = PatternGenerator(use_ai=True)
    
    candidates = []
    
    # Fase 1: Generación
    print("Generando candidatos...")
    for i in range(GEN_BATCH_SIZE):
        # Aleatorizar parámetros para explorar
        p_type = random.choice(['drums', 'bass', 'melody', 'percussion', 'fx'])
        dens = random.uniform(0.3, 0.9)
        comp = random.uniform(0.3, 0.9)
        temp = random.uniform(0.8, 1.5) # Temperatura alta para innovación
        
        try:
            pat = generator.generate(
                pattern_type=p_type,
                density=dens,
                complexity=comp,
                style='experimental',
                temperature=temp
            )
            candidates.append(pat)
            if i % 10 == 0: print(f".", end="", flush=True)
        except Exception as e:
            pass # Ignorar fallos de generación
            
    print("\nEvaluando...")
    
    # Fase 2: Evaluación
    scored_candidates = []
    for pat in candidates:
        s = PatternCritic.score(pat)
        scored_candidates.append((s, pat))
        
    # Ordenar por puntuación descendente
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Fase 3: Selección
    survivors = scored_candidates[:TOP_K]
    
    print("\n🏆 Top Supervivientes:")
    print("-" * 40)
    for score, pat in survivors:
        print(f"[{score:.1f}] {pat}")
        
    # Fase 4: Reproducción (Guardar en corpus)
    # Guardamos en un archivo separado 'evolution.txt' para no ensuciar el principal todavía
    # O podríamos añadirlo a favorites.json
    
    # Vamos a añadirlo al corpus principal directamente pero con un comentario
    TARGET_CORPUS = os.path.join(os.path.dirname(__file__), '..', 'examples', 'corpus', 'patterns.txt')
    
    new_count = 0
    with open(TARGET_CORPUS, 'a', encoding='utf-8') as f:
        f.write(f"\n# --- EVOLUTIONARY BATCH {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n")
        for score, pat in survivors:
            if score > 0: # Solo si pasó el corte de calidad mínima
                f.write(f"{pat}\n")
                new_count += 1
                
    print(f"\n💾 {new_count} patrones añadidos al Corpus Principal.")
    print("El cerebro ha crecido.")

if __name__ == '__main__':
    main()
