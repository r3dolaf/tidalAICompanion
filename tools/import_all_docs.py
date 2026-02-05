import re
import os
import glob

# Ruta base de documentación
DOCS_DIR = r"C:\Users\alfredo\Desktop\tidal\Documentacion_Completa\HTML"
# Ruta del corpus destino
DEST_CORPUS = r"C:\Users\alfredo\Desktop\tidalai-companion\examples\corpus\patterns.txt"

def extract_patterns_from_file(filepath):
    """Extrae bloques de código <pre><code> de un archivo HTML."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return []

    # Regex para encontrar bloques de código
    code_blocks = re.findall(r'<pre><code>(.*?)</code></pre>', html_content, re.DOTALL)
    
    clean_patterns = []
    
    for block in code_blocks:
        # Limpiar tags HTML
        text = re.sub(r'<[^>]+>', '', block)
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        
        lines = text.split('\n')
        current_pattern = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('--'): continue # Ignorar comentarios
            
            # Detectar líneas de código Tidal
            # Aceptamos 'd1 $', 's "..."', 'note "..."', o transformaciones directas
            if re.match(r'd\d+\s*\$', line) or re.match(r's\s+"', line) or re.match(r'note\s+"', line):
                 # Limpiar 'd1 $ ' para dejar solo el patrón puro (mejor para el modelo)
                content = re.sub(r'^d\d+\s*\$\s*', '', line)
                if content:
                    clean_patterns.append(content)
            
            # Detectar efectos encadenados (# lpf 100)
            elif line.startswith('#'):
                 # Si la línea anterior era un patrón, podemos "fusionarla" o tratarla como continuación
                 # Para el corpus simple, vamos a ignorar líneas sueltas de efectos por ahora
                 # a menos que podamos pegarlas al anterior.
                 # SIMPLE FIX: Si la lista no está vacía, pegamos al último
                 if clean_patterns:
                     clean_patterns[-1] += " " + line

    return clean_patterns

def main():
    if not os.path.exists(DOCS_DIR):
        print(f"Error: Directorio no encontrado {DOCS_DIR}")
        return

    all_patterns = []
    
    # Archivos a procesar (Priorizamos los que tienen código útil)
    target_files = [
        "01_fundamentos.html",
        "03_funciones.html",
        "04_efectos.html",
        "04_efectos.html",
        "06_generos.html",
        "07_tecnicas.html",
        "09_ejercicios.html",
        "10_referencia.html"
    ]
    
    print(f"Analizando documentación en {DOCS_DIR}...")
    
    for filename in target_files:
        filepath = os.path.join(DOCS_DIR, filename)
        if os.path.exists(filepath):
            pats = extract_patterns_from_file(filepath)
            print(f"  - {filename}: {len(pats)} patrones extraídos.")
            all_patterns.extend(pats)
            
    # Guardar en corpus
    print(f"\nTotal nuevos patrones: {len(all_patterns)}")
    
    # Leer corpus existente para evitar duplicados exactos
    existing = set()
    if os.path.exists(DEST_CORPUS):
        with open(DEST_CORPUS, 'r', encoding='utf-8') as f:
            for line in f:
                existing.add(line.strip())
    
    added_count = 0
    with open(DEST_CORPUS, 'a', encoding='utf-8') as f:
        f.write("\n\n# ============================================\n")
        f.write("# IMPORTADO DESDE DOCUMENTACION COMPLETA\n")
        f.write("# ============================================\n")
        for p in all_patterns:
            # Limpieza final
            p_clean = re.sub(r'\s+', ' ', p).strip()
            
            # Filtrar patrones demasiado cortos o sintaxis definición de tipos
            if len(p_clean) < 5 or "::" in p_clean: 
                continue
                
            if p_clean not in existing:
                f.write(p_clean + '\n')
                existing.add(p_clean)
                added_count += 1

    print(f"Patrones únicos añadidos: {added_count}")

if __name__ == '__main__':
    main()
