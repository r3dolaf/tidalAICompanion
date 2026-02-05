#!/usr/bin/env python3
"""
Extractor de Patrones TidalCycles - Versión Interactiva
Extrae patrones y permite mejorar la clasificación interactivamente
"""

import os
import re
import json
import argparse
from pathlib import Path

def extract_patterns_from_file(filepath):
    """Extrae patrones de un archivo .tidal"""
    patterns = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern_regex = r'd[1-9]\s*\$\s*(.+?)(?:\n|$)'
        matches = re.finditer(pattern_regex, content, re.MULTILINE)
        
        for match in matches:
            pattern = match.group(1).strip()
            pattern = re.sub(r'--.*$', '', pattern).strip()
            
            if len(pattern) > 5 and not pattern.startswith('silence'):
                patterns.append(pattern)
        
        return patterns
        
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return []

def categorize_pattern(pattern):
    """Categoriza el patrón con heurísticas mejoradas"""
    pattern_lower = pattern.lower()
    
    sound_match = re.search(r's\s+"([^"]+)"', pattern_lower)
    sound_source = sound_match.group(1) if sound_match else ""
    has_note = 'note' in pattern_lower or re.search(r'n\s+"', pattern_lower)
    
    drum_sounds = ['bd', 'kick', 'sn', 'snare', 'hh', 'hat', 'hihat', 'cp', 'clap',
                   'clubkick', 'sd', 'rim', 'tom', 'cymbal', 'crash', 'ride', 'hh27', 'ch', 'oh']
    bass_sounds = ['bass', 'sub', 'jungbass', 'reese', 'wobble', 'superfm', 'bassdm', 'bassdrums']
    melody_sounds = ['arpy', 'arp', 'piano', 'superpiano', 'rhodes', 'keys', 'supersquare', 
                     'supersaw', 'superpwm', 'pluck', 'bell', 'gong', 'supergong', 'supervibe', 
                     'vibe', 'marimba', 'synth', 'lead', 'pad', 'string']
    perc_sounds = ['tabla', 'bongo', 'conga', 'perc', 'shaker', 'tamb', 'cowbell', 'wood', 
                   'metal', 'click', 'tick']
    fx_sounds = ['noise', 'wind', 'breath', 'bev', 'birds', 'space', 'pad', 'drone', 
                 'texture', 'grain', 'glitch', 'acid']
    
    for drum in drum_sounds:
        if drum in sound_source or f'sound "{drum}' in pattern_lower:
            return 'drums'
    
    for bass in bass_sounds:
        if bass in sound_source:
            return 'bass'
    
    for perc in perc_sounds:
        if perc in sound_source:
            return 'percussion'
    
    for fx in fx_sounds:
        if fx in sound_source:
            return 'fx'
    
    if has_note:
        if any(x in pattern_lower for x in ['scale', 'chord', 'arpeggio', 'arpeggiate']):
            return 'melody'
        
        note_numbers = re.findall(r'\b(\d+)\b', pattern)
        if note_numbers:
            notes = [int(n) for n in note_numbers if int(n) < 128]
            if notes:
                avg_note = sum(notes) / len(notes)
                if avg_note < 48:
                    return 'bass'
                elif avg_note >= 48:
                    return 'melody'
    
    for melody in melody_sounds:
        if melody in sound_source or melody in pattern_lower:
            return 'melody'
    
    if any(x in pattern_lower for x in ['lpf 200', 'lpf 150', 'lpf 120', 'lpf 100']):
        return 'bass'
    
    if any(x in pattern_lower for x in ['striate', 'grain', 'chop']):
        return 'fx'
    
    return 'unknown'

def ask_user_classification(pattern, auto_type):
    """Pregunta al usuario si la clasificación automática es correcta"""
    print("\n" + "="*80)
    print("PATRON ENCONTRADO:")
    print("-"*80)
    
    # Mostrar patrón con mejor formato
    if len(pattern) > 70:
        # Dividir en líneas si es muy largo
        words = pattern.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 70:
                print(f"  {line}")
                line = word
            else:
                line += (" " + word) if line else word
        if line:
            print(f"  {line}")
    else:
        print(f"  {pattern}")
    
    print("-"*80)
    print(f"Clasificacion automatica: [{auto_type.upper()}]")
    print("="*80)
    
    response = input("\nEs correcta? (s/n/tipo): ").strip().lower()
    
    if response == 's' or response == '':
        return auto_type
    elif response == 'n':
        print("\nTipos disponibles:")
        print("  - drums      (bateria)")
        print("  - bass       (bajo)")
        print("  - melody     (melodia)")
        print("  - percussion (percusion)")
        print("  - fx         (efectos)")
        print("  - unknown    (desconocido)")
        new_type = input("\nTipo correcto: ").strip().lower()
        return new_type if new_type else auto_type
    elif response in ['drums', 'bass', 'melody', 'percussion', 'fx', 'unknown']:
        return response
    else:
        return auto_type

def scan_directory(directory, interactive=False, review_unknown=False):
    """Escanea directorio buscando archivos .tidal"""
    all_patterns = []
    
    tidal_files = list(Path(directory).rglob('*.tidal'))
    
    print(f"Encontrados {len(tidal_files)} archivos .tidal")
    
    for filepath in tidal_files:
        print(f"Procesando: {filepath.name}")
        patterns = extract_patterns_from_file(filepath)
        
        for pattern in patterns:
            pattern_type = categorize_pattern(pattern)
            
            # Modo interactivo: preguntar por patrones unknown
            if interactive and (review_unknown and pattern_type == 'unknown'):
                pattern_type = ask_user_classification(pattern, pattern_type)
            
            all_patterns.append({
                'pattern': pattern,
                'type': pattern_type,
                'source': str(filepath.name)
            })
    
    return all_patterns

def save_to_corpus(patterns, output_file):
    """Guarda patrones en archivo de corpus"""
    txt_file = output_file.replace('.json', '.txt')
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("# Patrones extraídos de proyecto personal\n")
        f.write(f"# Total: {len(patterns)} patrones\n\n")
        
        for item in patterns:
            f.write(f"# {item['type']} - {item['source']}\n")
            f.write(f"{item['pattern']}\n\n")
    
    print(f"[OK] Guardado en {txt_file}")

def save_to_favorites(patterns, output_file):
    """Guarda patrones en formato de favoritos (JSON)"""
    favorites = []
    
    for item in patterns:
        favorites.append({
            'pattern': item['pattern'],
            'type': item['type'],
            'timestamp': 0,
            'source': item['source']
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Guardado en {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Extrae patrones de archivos TidalCycles')
    parser.add_argument('directory', help='Directorio con archivos .tidal')
    parser.add_argument('--output', '-o', default='extracted_patterns.txt', help='Archivo de salida')
    parser.add_argument('--format', '-f', choices=['corpus', 'favorites'], default='corpus',
                        help='Formato de salida')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Modo interactivo: revisar clasificaciones unknown')
    parser.add_argument('--add-to-corpus', '-a', action='store_true',
                        help='Añadir automáticamente al corpus base')
    parser.add_argument('--auto-train', '-t', action='store_true',
                        help='Re-entrenar modelo automáticamente después de extraer')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"Error: Directorio {args.directory} no existe")
        return
    
    print(f"Escaneando {args.directory}...")
    patterns = scan_directory(args.directory, 
                              interactive=args.interactive, 
                              review_unknown=args.interactive)
    
    if not patterns:
        print("No se encontraron patrones")
        return
    
    print(f"\n{'='*60}")
    print(f"  EXTRACCION COMPLETADA")
    print(f"{'='*60}")
    print(f"\n  Total de patrones encontrados: {len(patterns)}")
    
    # Estadísticas
    by_type = {}
    for p in patterns:
        ptype = p['type']
        by_type[ptype] = by_type.get(ptype, 0) + 1
    
    print(f"\n  Distribucion por tipo:")
    print(f"  {'-'*40}")
    
    # Iconos para cada tipo
    icons = {
        'drums': '[DRUMS]     ',
        'bass': '[BASS]      ',
        'melody': '[MELODY]    ',
        'percussion': '[PERCUSSION]',
        'fx': '[FX]        ',
        'unknown': '[UNKNOWN]   '
    }
    
    for ptype in sorted(by_type.keys()):
        count = by_type[ptype]
        percentage = (count / len(patterns)) * 100
        icon = icons.get(ptype, f'[{ptype.upper()}]')
        bar = '#' * int(percentage / 2)
        print(f"  {icon} {count:3d} ({percentage:5.1f}%) {bar}")
    
    print(f"  {'-'*40}")
    print(f"{'='*60}\n")
    
    # Guardar
    if args.format == 'corpus':
        save_to_corpus(patterns, args.output)
    else:
        save_to_favorites(patterns, args.output)
    
    # Añadir al corpus automáticamente
    if args.add_to_corpus:
        print("\n[?] ¿Añadir estos patrones al corpus base?")
        response = input("(s/n): ").strip().lower()
        if response == 's':
            corpus_file = 'examples/corpus/patterns.txt'
            if os.path.exists(corpus_file):
                with open(args.output, 'r', encoding='utf-8') as src:
                    content = src.read()
                with open(corpus_file, 'a', encoding='utf-8') as dst:
                    dst.write('\n' + content)
                print(f"[OK] Añadido a {corpus_file}")
    
    # Re-entrenar modelo
    if args.auto_train:
        print("\n[?] ¿Re-entrenar el modelo ahora?")
        response = input("(s/n): ").strip().lower()
        if response == 's':
            print("[INFO] Debes re-entrenar desde la interfaz web:")
            print("  1. Abre http://192.168.1.147:5000")
            print("  2. Click '🔄 Re-entrenar Modelo'")
    
    print(f"\n[OK] Proceso completado")
    print(f"\nPara usar estos patrones:")
    if args.format == 'corpus':
        print(f"1. Copia {args.output} a examples/corpus/")
        print(f"2. Añade el contenido a patterns.txt")
    else:
        print(f"1. Copia {args.output} a examples/corpus/favorites.json")
    print(f"3. Re-entrena el modelo desde la interfaz web")

if __name__ == '__main__':
    main()
