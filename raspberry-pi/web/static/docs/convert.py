import os
import re

# Directorio base
base_dir = r'c:\Users\alfredo\Desktop\tidal\Documentacion_Completa'
html_dir = os.path.join(base_dir, 'HTML')

# Crear directorio HTML si no existe
os.makedirs(html_dir, exist_ok=True)

# Template HTML base
def create_html(title, content):
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - TidalCycles</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #0a0e27; 
            color: #e0e0e0; 
            line-height: 1.8; 
        }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
        header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 40px; 
            border-radius: 15px; 
            margin-bottom: 40px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
        }}
        header h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .back-link {{ 
            display: inline-block; 
            background: rgba(255,255,255,0.2); 
            padding: 10px 20px; 
            border-radius: 5px; 
            color: white; 
            text-decoration: none; 
            margin-top: 20px; 
            transition: all 0.3s;
        }}
        .back-link:hover {{ background: rgba(255,255,255,0.3); }}
        .content {{ 
            background: #1a1f3a; 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 5px 20px rgba(0,0,0,0.3); 
        }}
        .content h1 {{ 
            color: #8b9dff; 
            margin: 30px 0 20px 0; 
            font-size: 2rem; 
        }}
        .content h2 {{ 
            color: #a78bfa; 
            margin: 25px 0 15px 0; 
            font-size: 1.7rem; 
            border-bottom: 2px solid #2d3555; 
            padding-bottom: 10px; 
        }}
        .content h3 {{ 
            color: #8b9dff; 
            margin: 20px 0 10px 0; 
            font-size: 1.4rem; 
        }}
        .content h4 {{ 
            color: #a78bfa; 
            margin: 15px 0 10px 0; 
            font-size: 1.2rem; 
        }}
        .content p {{ margin: 15px 0; color: #d0d0d0; }}
        .content code {{ 
            background: #2d3555; 
            padding: 3px 8px; 
            border-radius: 4px; 
            font-family: 'Courier New', monospace; 
            color: #ff79c6; 
            border: 1px solid #3d4566;
        }}
        .content pre {{ 
            background: #0d1117; 
            color: #f8f8f2; 
            padding: 20px; 
            border-radius: 8px; 
            overflow-x: auto; 
            margin: 20px 0; 
            border: 1px solid #2d3555;
        }}
        .content pre code {{ 
            background: none; 
            color: #f8f8f2; 
            padding: 0; 
            border: none;
        }}
        .content table {{ 
            width: 100%; 
            border-collapse: collapse; 
            margin: 20px 0; 
        }}
        .content th, .content td {{ 
            padding: 12px; 
            text-align: left; 
            border: 1px solid #2d3555; 
        }}
        .content th {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
        }}
        .content tr:nth-child(even) {{ background: #242b4a; }}
        .content tr:nth-child(odd) {{ background: #1a1f3a; }}
        .content strong {{ color: #8b9dff; font-weight: 600; }}
        .content ul, .content ol {{ margin: 15px 0 15px 30px; }}
        .content li {{ margin: 8px 0; color: #d0d0d0; }}
        .content blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            color: #a0a0a0;
            font-style: italic;
            background: #242b4a;
            padding: 15px 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 {title}</h1>
            <p>Documentación Completa de TidalCycles</p>
            <a href="index.html" class="back-link">← Volver al Índice</a>
        </header>
        <div class="content">
            {content}
        </div>
    </div>
</body>
</html>'''

# Función simple de conversión
def convert_md_to_html(md_text):
    html = md_text
    
    # Convertir bloques de código
    html = re.sub(r'```haskell\n(.*?)\n```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```supercollider\n(.*?)\n```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'```.*?\n(.*?)\n```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    # Convertir headers
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convertir inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Convertir bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Convertir listas
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Convertir párrafos
    lines = html.split('\n')
    result = []
    in_para = False
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            if not in_para:
                result.append('<p>')
                in_para = True
            result.append(line)
        else:
            if in_para:
                result.append('</p>')
                in_para = False
            result.append(line)
    
    if in_para:
        result.append('</p>')
    
    return '\n'.join(result)

# Archivos a convertir
files = [
    ('00_Glosario/GLOSARIO_MUSICA_ELECTRONICA.md', '00_glosario.html', 'Glosario de Música Electrónica'),
    ('01_Fundamentos/01_Arquitectura_Y_Conceptos.md', '01_fundamentos.html', 'Fundamentos'),
    ('02_Sintaxis_Avanzada/01_Mini_Notacion_Completa.md', '02_sintaxis.html', 'Sintaxis Avanzada'),
    ('03_Funciones_Completas/01_Funciones_Transformacion.md', '03_funciones.html', 'Funciones Completas'),
    ('04_Efectos_Y_Parametros/01_Efectos_Completos.md', '04_efectos.html', 'Efectos y Parámetros'),
    ('05_Samples_Y_Sintesis/01_Samples_Y_Sintesis.md', '05_samples.html', 'Samples y Síntesis'),
    ('06_Generos_Musicales/01_Generos_Completos.md', '06_generos.html', 'Géneros Musicales'),
    ('07_Tecnicas_Avanzadas/01_Tecnicas_Avanzadas.md', '07_tecnicas.html', 'Técnicas Avanzadas'),
    ('08_SuperCollider_Integration/01_SuperCollider_Integration.md', '08_supercollider.html', 'SuperCollider Integration'),
    ('09_Ejercicios_Practicos/01_Ejercicios_Completos.md', '09_ejercicios.html', 'Ejercicios Prácticos'),
    ('10_Referencia_Completa/01_Referencia_Completa.md', '10_referencia.html', 'Referencia Completa'),
]

print('Convirtiendo archivos markdown a HTML...\n')

for md_file, html_file, title in files:
    md_path = os.path.join(base_dir, md_file)
    html_path = os.path.join(html_dir, html_file)
    
    if os.path.exists(md_path):
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = convert_md_to_html(md_content)
            full_html = create_html(title, html_content)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f'[OK] Convertido: {title} -> {html_file}')
        except Exception as e:
            print(f'[ERROR] Error en {title}: {str(e)}')
    else:
        print(f'[ERROR] No encontrado: {md_file}')

print(f'\n¡Conversión completada!')
print(f'Archivos HTML creados en: {html_dir}')
print(f'\nAbre index.html para empezar a navegar la documentación')
