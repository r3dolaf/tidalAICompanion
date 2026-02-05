import re
import os

CORPUS_PATH = r"C:\Users\alfredo\Desktop\tidalai-companion\examples\corpus\patterns.txt"

def sanitize_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return line
        
    # 1. Eliminar HTML accidental
    if line.startswith('<div') or line.startswith('<nav'):
        return None
        
    # 2. Corregir espacio tras dólar (el corazón de la Fase 16)
    # Busca $ seguido de cualquier cosa que NO sea un espacio, y le mete el espacio.
    line = re.sub(r'\$([^\s\)])', r'$ \1', line)
    
    # 3. Detectar "hallucinaciones" de overlapping sounds
    parts = [p.strip() for p in line.split('#') if p.strip()]
    source_keywords = r'^(sound|s|note|n|midinote|drum|kick|snare|hihat|clap|tabla)\b'
    sources = [p for p in parts if re.match(source_keywords, p)]
    
    if len(sources) > 1:
        return None # Eliminar patrones polifónicos mal formados del entrenamiento
        
    return line

def clean():
    if not os.path.exists(CORPUS_PATH):
        print(f"Error: {CORPUS_PATH} no existe")
        return
        
    with open(CORPUS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    original_count = len(lines)
    clean_lines = []
    
    for line in lines:
        sanitized = sanitize_line(line)
        if sanitized is not None:
            clean_lines.append(sanitized + '\n')
    
    with open(CORPUS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
        
    print(f"Limpieza y Alineación completada: {original_count} -> {len(clean_lines)} líneas")
    print(f"Eliminadas/Corregidas {original_count - len(clean_lines)} líneas.")

if __name__ == "__main__":
    clean()
