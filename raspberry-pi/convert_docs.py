"""
TidalAI Companion - Documentation Converter
Convierte documentación Markdown a HTML y PDF.
"""

import markdown
import os
from pathlib import Path
import subprocess
import sys


def convert_md_to_html(md_file: str, output_file: str = None):
    """
    Convertir archivo Markdown a HTML.
    
    Args:
        md_file: Ruta al archivo .md
        output_file: Ruta de salida (opcional, usa mismo nombre con .html)
    """
    if output_file is None:
        output_file = md_file.replace('.md', '.html')
    
    # Leer markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir a HTML con extensiones
    html = markdown.markdown(
        md_content,
        extensions=[
            'extra',
            'codehilite',
            'toc',
            'tables',
            'fenced_code'
        ]
    )
    
    # Template HTML completo
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Path(md_file).stem}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .content {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: transparent;
            color: #ecf0f1;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #555;
            font-style: italic;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="content">
        {html}
    </div>
</body>
</html>
"""
    
    # Guardar HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"[OK] HTML generado: {output_file}")


def convert_html_to_pdf(html_file: str, output_file: str = None):
    """
    Convertir archivo HTML a PDF usando WeasyPrint.
    
    Args:
        html_file: Ruta al archivo .html
        output_file: Ruta de salida (opcional, usa mismo nombre con .pdf)
    """
    try:
        from weasyprint import HTML
        
        if output_file is None:
            output_file = html_file.replace('.html', '.pdf')
        
        # Convertir
        HTML(html_file).write_pdf(output_file)
        print(f"[OK] PDF generado: {output_file}")
        
    except ImportError:
        print("[!] WeasyPrint no esta instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
        print("[OK] WeasyPrint instalado. Reintenta la conversion.")


def convert_md_to_pdf(md_file: str, output_file: str = None):
    """
    Convertir Markdown directamente a PDF (vía HTML).
    
    Args:
        md_file: Ruta al archivo .md
        output_file: Ruta de salida PDF (opcional)
    """
    if output_file is None:
        output_file = md_file.replace('.md', '.pdf')
    
    # Crear HTML temporal
    temp_html = md_file.replace('.md', '_temp.html')
    
    # MD -> HTML
    convert_md_to_html(md_file, temp_html)
    
    # HTML -> PDF
    convert_html_to_pdf(temp_html, output_file)
    
    # Limpiar temporal
    if os.path.exists(temp_html):
        os.remove(temp_html)


def convert_all_docs(docs_dir: str = "../docs"):
    """
    Convertir toda la documentación del proyecto.
    
    Args:
        docs_dir: Directorio con archivos .md
    """
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"Error: Directorio {docs_dir} no existe")
        return
    
    # Buscar todos los .md
    md_files = list(docs_path.glob("*.md"))
    
    if not md_files:
        print(f"No se encontraron archivos .md en {docs_dir}")
        return
    
    print(f"\n=== Convirtiendo {len(md_files)} archivos ===\n")
    
    # Crear subdirectorios para salida
    html_dir = docs_path / "html"
    pdf_dir = docs_path / "pdf"
    html_dir.mkdir(exist_ok=True)
    pdf_dir.mkdir(exist_ok=True)
    
    for md_file in md_files:
        print(f"\nProcesando: {md_file.name}")
        
        # Rutas de salida
        html_out = html_dir / md_file.name.replace('.md', '.html')
        pdf_out = pdf_dir / md_file.name.replace('.md', '.pdf')
        
        # Convertir
        try:
            convert_md_to_html(str(md_file), str(html_out))
            convert_html_to_pdf(str(html_out), str(pdf_out))
        except Exception as e:
            print(f"[ERROR] Error procesando {md_file.name}: {e}")
    
    print(f"\n=== Conversión completada ===")
    print(f"HTML: {html_dir}")
    print(f"PDF: {pdf_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Convertir documentación Markdown')
    parser.add_argument('--docs-dir', default='../docs', help='Directorio con archivos .md')
    parser.add_argument('--file', help='Convertir un archivo específico')
    parser.add_argument('--format', choices=['html', 'pdf', 'both'], default='both',
                       help='Formato de salida')
    
    args = parser.parse_args()
    
    if args.file:
        # Convertir archivo específico
        if args.format in ['html', 'both']:
            convert_md_to_html(args.file)
        if args.format in ['pdf', 'both']:
            convert_md_to_pdf(args.file)
    else:
        # Convertir todo el directorio
        convert_all_docs(args.docs_dir)
