import sys
import os
import re
import urllib.request
import logging

logger = logging.getLogger(__name__)

class ScavengerTool:
    """
    Herramienta para recolectar patrones de TidalCycles desde URLs externas.
    """
    
    def __init__(self, main_corpus_path=None):
        if main_corpus_path:
            self.main_corpus = main_corpus_path
        else:
            # Ruta asumiendo ejecución desde app.py (en ../web/)
            self.main_corpus = os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'corpus', 'patterns.txt')
            
    def fetch_url(self, url):
        """Descarga el contenido de una URL"""
        try:
            logger.info(f"🕷️ Scavenging: {url}")
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_patterns(self, text):
        """Extrae patrones válidos del texto usando heurísticas y regex."""
        patterns = []
        if not text: return patterns
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'): continue
            
            # Buscamos d1 $ o sound "..."
            if re.search(r'd\d+\s*\$', line) or 'sound "' in line or 'note "' in line:
                # Limpiar d1 $
                clean = re.sub(r'^d\d+\s*\$\s*', '', line)
                # Quitar comentarios
                clean = clean.split('--')[0].strip()
                
                # Validar mínimamente (debe tener comillas y longitud)
                if len(clean) > 5 and '"' in clean:
                    # Evitar duplicados simples
                    if clean not in patterns:
                        patterns.append(clean)
        return patterns

    def run_bulk(self, sources_list):
        """Ejecuta la recolección sobre una lista de URLs"""
        all_new_patterns = []
        results = []
        
        for url in sources_list:
            content = self.fetch_url(url)
            if content:
                pats = self.extract_patterns(content)
                all_new_patterns.extend(pats)
                results.append({"url": url, "count": len(pats), "success": True})
            else:
                results.append({"url": url, "count": 0, "success": False})
                
        # Guardar si encontramos algo
        added_count = 0
        if all_new_patterns:
            # Eliminar duplicados
            unique_new = list(set(all_new_patterns))
            
            try:
                with open(self.main_corpus, 'a', encoding='utf-8') as f:
                    f.write(f"\n# --- BULK SCAVENGE RUN {os.path.getmtime(self.main_corpus)} ---\n")
                    for p in unique_new:
                        f.write(p + '\n')
                added_count = len(unique_new)
                logger.info(f"Inyectados {added_count} patrones desde {len(sources_list)} fuentes.")
            except Exception as e:
                logger.error(f"Error guardando en corpus: {e}")
                
        return {
            "total_urls": len(sources_list),
            "results": results,
            "total_added": added_count
        }
