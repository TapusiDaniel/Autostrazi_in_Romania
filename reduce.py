import re
import os
from pathlib import Path

def fast_minify_html(input_file):
    """
    Fast HTML minification focusing on size reduction with minimal CPU usage.
    """
    if not input_file.endswith('.html'):
        input_file += '.html'
    
    input_path = Path(input_file)
    output_path = input_path.with_stem(input_path.stem + '.min')
    
    print(f"Processing: {input_path}")
    
    try:
        # Citește fișierul în chunks pentru a reduce folosirea memoriei
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Minificare rapidă folosind doar operații simple
        minified = content
        
        # Elimină comentariile HTML (operație relativ rapidă)
        minified = re.sub(r'<!--[\s\S]*?-->', '', minified)
        
        # Elimină spațiile multiple și newline-urile (operație simplă)
        minified = re.sub(r'[\n\r\t]+', ' ', minified)
        minified = re.sub(r'\s{2,}', ' ', minified)
        
        # Elimină spațiile între tag-uri (operație simplă)
        minified = re.sub(r'>\s+<', '><', minified)
        
        # Elimină spațiile la început și sfârșit
        minified = minified.strip()
        
        # Salvează rezultatul
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified)
        
        # Calculează statisticile
        original_size = os.path.getsize(input_path)
        minified_size = os.path.getsize(output_path)
        saved = original_size - minified_size
        saved_percent = (saved / original_size) * 100
        
        print("\nResults:")
        print(f"Original size: {original_size:,} bytes")
        print(f"Minified size: {minified_size:,} bytes")
        print(f"Saved: {saved:,} bytes ({saved_percent:.1f}%)")
        
        # Sugestii pentru optimizare ulterioară
        print("\nSugestii pentru optimizare ulterioară:")
        print("1. Verifică și comprimă imaginile mari")
        print("2. Mută CSS și JavaScript în fișiere externe")
        print("3. Folosește un CDN pentru resursele statice")
        print("4. Activează compresia GZIP pe server")
        
    except Exception as e:
        print(f"Error: {e}")

# Folosire
fast_minify_html('autostrada_a1_detailed1')