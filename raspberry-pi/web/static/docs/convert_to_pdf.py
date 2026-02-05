#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertidor HTML a PDF usando navegador (Chrome/Edge)
Alternativa simple sin dependencias complejas
"""

import os
import subprocess
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR.parent / "PDF"
PDF_DIR.mkdir(exist_ok=True)

# Archivos HTML a convertir
html_files = [
    ('index.html', '00_INDICE.pdf'),
    ('00_glosario.html', '00_glosario.pdf'),
    ('01_fundamentos.html', '01_fundamentos.pdf'),
    ('02_sintaxis.html', '02_sintaxis.pdf'),
    ('03_funciones.html', '03_funciones.pdf'),
    ('04_efectos.html', '04_efectos.pdf'),
    ('05_samples.html', '05_samples.pdf'),
    ('06_generos.html', '06_generos.pdf'),
    ('07_tecnicas.html', '07_tecnicas.pdf'),
    ('08_supercollider.html', '08_supercollider.pdf'),
    ('09_ejercicios.html', '09_ejercicios.pdf'),
    ('10_referencia.html', '10_referencia.pdf'),
]

def find_chrome():
    """Encuentra la ruta de Chrome o Edge"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def convert_html_to_pdf_chrome(html_file, pdf_file):
    """Convierte HTML a PDF usando Chrome/Edge"""
    chrome_path = find_chrome()
    
    if not chrome_path:
        print("[ERROR] No se encontró Chrome o Edge")
        return False
    
    try:
        html_path = (BASE_DIR / html_file).absolute()
        pdf_path = (PDF_DIR / pdf_file).absolute()
        
        # Comando para Chrome headless
        cmd = [
            chrome_path,
            '--headless',
            '--disable-gpu',
            '--print-to-pdf=' + str(pdf_path),
            '--no-margins',
            'file:///' + str(html_path).replace('\\', '/')
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if pdf_path.exists():
            print(f"[OK] Convertido: {html_file} -> {pdf_file}")
            return True
        else:
            print(f"[ERROR] {html_file}: No se generó el PDF")
            return False
            
    except Exception as e:
        print(f"[ERROR] {html_file}: {str(e)}")
        return False

def create_readme():
    """Crea un README en la carpeta PDF"""
    readme_content = """# DOCUMENTACIÓN TIDALCYCLES - PDFs

Esta carpeta contiene toda la documentación de TidalCycles en formato PDF.

## Archivos Disponibles:

- **00_INDICE.pdf** - Índice general de toda la documentación
- **00_glosario.pdf** - Glosario de Música Electrónica (80+ términos)
- **01_fundamentos.pdf** - Fundamentos de TidalCycles
- **02_sintaxis.pdf** - Sintaxis Avanzada y Mini-notación
- **03_funciones.pdf** - Funciones Completas (200+ funciones)
- **04_efectos.pdf** - Efectos y Parámetros
- **05_samples.pdf** - Samples y Síntesis
- **06_generos.pdf** - Géneros Musicales
- **07_tecnicas.pdf** - Técnicas Avanzadas
- **08_supercollider.pdf** - Integración con SuperCollider
- **09_ejercicios.pdf** - Ejercicios Prácticos
- **10_referencia.pdf** - Referencia Completa

## Cómo Usar:

1. Abre **00_INDICE.pdf** para ver el índice general
2. Navega a los PDFs específicos según tus necesidades
3. Todos los PDFs mantienen el formato y diseño de la versión HTML

## Notas:

- Los PDFs están optimizados para impresión en A4
- Conservan el tema oscuro de la versión HTML
- Incluyen todos los ejemplos de código
- Mantienen la navegación interna (enlaces)

**Total:** 12 documentos PDF
**Contenido:** 6000+ líneas de documentación técnica
"""
    
    readme_path = PDF_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("[OK] Creado README.md")

def main():
    print("Convirtiendo archivos HTML a PDF usando Chrome/Edge...")
    print()
    
    # Verificar que Chrome/Edge está disponible
    chrome_path = find_chrome()
    if not chrome_path:
        print("[ERROR] No se encontró Chrome o Edge instalado")
        print("Por favor instala Google Chrome o Microsoft Edge")
        return
    
    print(f"Usando: {chrome_path}")
    print()
    
    # Convertir archivos
    success_count = 0
    for html_file, pdf_file in html_files:
        if convert_html_to_pdf_chrome(html_file, pdf_file):
            success_count += 1
    
    # Crear README
    create_readme()
    
    print()
    print(f"Conversión completada!")
    print(f"Archivos convertidos: {success_count}/{len(html_files)}")
    print(f"PDFs creados en: {PDF_DIR}")
    print()
    print("Abre 00_INDICE.pdf para empezar a navegar la documentación")

if __name__ == "__main__":
    main()
