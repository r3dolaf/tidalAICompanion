import re
import os

# Ruta del archivo HTML fuente
SOURCE_HTML = r"C:\Users\alfredo\Desktop\tidal\Documentacion_Completa\HTML\06_generos.html"
# Ruta del corpus destino
DEST_CORPUS = r"C:\Users\alfredo\Desktop\tidalai-companion\examples\corpus\patterns.txt"

def extract_patterns():
    if not os.path.exists(SOURCE_HTML):
        print(f"Error: No encuentro el archivo {SOURCE_HTML}")
        return

    with open(SOURCE_HTML, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Regex para encontrar bloques de código dentro de <pre><code>...</code></pre>
    # Nota: El HTML tiene <p> dentro de <code> a veces, según lo visto.
    code_blocks = re.findall(r'<pre><code>(.*?)</code></pre>', html_content, re.DOTALL)
    
    clean_patterns = []
    
    for block in code_blocks:
        # Limpiar tags HTML internos (<p>, </p>, <br>)
        text = re.sub(r'<[^>]+>', '', block)
        
        # Limpiar entidades HTML
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
        
        # Separar por líneas
        lines = text.split('\n')
        
        current_pattern = []
        
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith('--'): continue # Ignorar comentarios puros
            
            # Si empieza por d1, d2... es un patrón
            if re.match(r'd\d+\s*\$', line):
                # Guardar patrón previo si existe
                if current_pattern:
                    clean_patterns.append(" ".join(current_pattern))
                    current_pattern = []
                
                # Transformar 'd1 $ ...' a algo genérico para el corpus?
                # El corpus actual usa 'sound "..."' directamente o 'note "..."'.
                # Pero 'd1 $ ...' es válido también si el modelo lo aprende.
                # Sin embargo, para mantener consistencia con 'patterns.txt' existente,
                # idealmente extraeríamos solo la parte del pattern.
                # PERO, el modelo es agnóstico. Vamos a limpiar 'd\d+ \$' para dejar solo el sound/note.
                
                # Estrategia: Quitar 'd1 $ ' y dejar el resto.
                content = re.sub(r'^d\d+\s*\$\s*', '', line)
                current_pattern.append(content)
            
            elif line.startswith('#'):
                # Es un efecto añadido al patrón anterior
                if current_pattern:
                    current_pattern.append(line)
        
        # Añadir último del bloque
        if current_pattern:
            clean_patterns.append(" ".join(current_pattern))

    # Guardar en corpus
    print(f"Encontrados {len(clean_patterns)} patrones nuevos.")
    
    with open(DEST_CORPUS, 'a', encoding='utf-8') as f:
        f.write("\n\n# ============================================\n")
        f.write("# IMPORTADO DESDE DOCUMENTACION GENEROS\n")
        f.write("# ============================================\n")
        for p in clean_patterns:
            # Limpieza final de espacios múltiples
            p_clean = re.sub(r'\s+', ' ', p).strip()
            f.write(p_clean + '\n')
            print(f"Importado: {p_clean[:50]}...")

if __name__ == '__main__':
    extract_patterns()
