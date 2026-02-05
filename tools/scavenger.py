import sys
import os
import re
import urllib.request
import argparse

# Configuración
CORPUS_FILE = os.path.join(os.path.dirname(__file__), '..', 'examples', 'corpus', 'scavenged.txt')
MAIN_CORPUS = os.path.join(os.path.dirname(__file__), '..', 'examples', 'corpus', 'patterns.txt')

def fetch_url(url):
    print(f"🕷️ Scavenging: {url}")
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def extract_patterns(text):
    """Extrae líneas que parecen ser código TidalCycles."""
    patterns = []
    lines = text.split('\n')
    
    # Regex basicos para detectar Tidal
    # d1 $ ...
    # sound "..."
    # note "..."
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('--'): continue
        
        # Heurística: Si contiene d1 $ o sound "..." es probable que sea código
        if re.search(r'd\d+\s*\$', line) or 'sound "' in line or 'note "' in line:
            # Limpieza: quitar d1 $ inicial para el corpus
            clean = re.sub(r'^d\d+\s*\$\s*', '', line)
            
            # Quitar comentarios inline
            clean = clean.split('--')[0].strip()
            
            if len(clean) > 5 and '"' in clean:
                patterns.append(clean)
                
    return patterns

def save_patterns(patterns, append_to_main=True):
    # Guardar en scavenged.txt
    visited = set()
    with open(CORPUS_FILE, 'a', encoding='utf-8') as f:
        for p in patterns:
            if p not in visited:
                f.write(p + '\n')
                visited.add(p)
                
    count = len(visited)
    print(f"✅ {count} patrones guardados en {CORPUS_FILE}")
    
    if append_to_main:
        with open(MAIN_CORPUS, 'a', encoding='utf-8') as f:
            f.write(f"\n# --- SCAVENGED BATCH ---\n")
            for p in visited:
                f.write(p + '\n')
        print(f"📚 {count} patrones inyectados al cerebro principal.")

def main():
    # Argumentos
    urls = []
    
    if len(sys.argv) >= 2:
        # Modo URL única
        urls.append(sys.argv[1])
    else:
        # Modo Bulk (sources.txt)
        sources_file = os.path.join(os.path.dirname(__file__), 'sources.txt')
        if os.path.exists(sources_file):
            print(f"📂 Cargando fuentes desde {sources_file}...")
            with open(sources_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
        else:
            # Fallback
            print("No URL provided and sources.txt not found.")
            urls.append("https://tidalcycles.org/")

    print(f"🎯 Objetivo: {len(urls)} fuentes.")
    
    total_found = 0
    all_patterns = []
    
    for url in urls:
        content = fetch_url(url)
        if content:
            pats = extract_patterns(content)
            if pats:
                print(f"  -> {len(pats)} patrones.")
                all_patterns.extend(pats)
            else:
                print("  -> 0 patrones.")
                
    if all_patterns:
        print(f"\n✨ Total recolectado: {len(all_patterns)} patrones.")
        save_patterns(all_patterns)
    else:
        print("\n❌ No se encontró nada comestible.")


if __name__ == '__main__':
    # Fix encoding
    sys.stdout.reconfigure(encoding='utf-8')
    main()
