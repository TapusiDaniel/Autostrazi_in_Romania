import gzip
import os
import requests
from cssmin import cssmin
from jsmin import jsmin
import shutil

def download_file(url, local_path):
    """Download a file from URL and save it locally."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def ensure_vendor_files():
    """Download and save vendor files locally."""
    vendor_files = {
        # CSS files
        'leaflet.css': 'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css',
        'leaflet.awesome-markers.css': 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css',
        'bootstrap-glyphicons.css': 'https://netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap-glyphicons.css',
        'fontawesome-all.min.css': 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.2.0/css/all.min.css',
        'bootstrap.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css',
        'leaflet.awesome.rotate.min.css': 'https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/leaflet.awesome.rotate.min.css',
        
        # JavaScript files
        'leaflet.js': 'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js',
        'leaflet.awesome-markers.js': 'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js',
        'jquery.min.js': 'https://code.jquery.com/jquery-3.7.1.min.js',
        'bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js'
    }
    
    vendors_dir = 'static/vendors'
    os.makedirs(vendors_dir, exist_ok=True)
    
    for filename, url in vendor_files.items():
        local_path = os.path.join(vendors_dir, filename)
        if not os.path.exists(local_path):
            print(f"Downloading {filename}...")
            if download_file(url, local_path):
                print(f"Successfully downloaded {filename}")
            else:
                print(f"Failed to download {filename}")

def optimize_resources():
    """Combine and minify CSS and JavaScript files."""
    # First ensure we have all vendor files
    ensure_vendor_files()
    
    # CSS files to combine
    css_files = [
        'leaflet.css',
        'leaflet.awesome-markers.css',
        'bootstrap-glyphicons.css',
        'fontawesome-all.min.css',
        'bootstrap.min.css',
        'leaflet.awesome.rotate.min.css'
    ]
    
    # Combine CSS files
    combined_css = ''
    for css_file in css_files:
        try:
            with open(f'static/vendors/{css_file}', 'r', encoding='utf-8') as f:
                print(f"Processing CSS: {css_file}")
                combined_css += f.read() + '\n'
        except Exception as e:
            print(f"Error processing {css_file}: {str(e)}")
    
    # Minify and save CSS
    try:
        minified_css = cssmin(combined_css)
        with open('static/css/main.css', 'w', encoding='utf-8') as f:
            f.write(minified_css)
        print("CSS optimization complete")
    except Exception as e:
        print(f"Error minifying CSS: {str(e)}")
    
    # JavaScript files to combine
    js_files = [
        'leaflet.js',
        'jquery.min.js',
        'bootstrap.bundle.min.js',
        'leaflet.awesome-markers.js'
    ]
    
    # Combine JavaScript files
    combined_js = ''
    for js_file in js_files:
        try:
            with open(f'static/vendors/{js_file}', 'r', encoding='utf-8') as f:
                print(f"Processing JS: {js_file}")
                combined_js += f.read() + '\n'
        except Exception as e:
            print(f"Error processing {js_file}: {str(e)}")
    
    # Minify and save JavaScript
    try:
        minified_js = jsmin(combined_js)
        with open('static/js/deferred.js', 'w', encoding='utf-8') as f:
            f.write(minified_js)
        print("JavaScript optimization complete")
    except Exception as e:
        print(f"Error minifying JavaScript: {str(e)}")
    
    static_files = {
        'css': ['main.css'],
        'js': ['deferred.js'],
        'vendors': [
            'leaflet.js',
            'leaflet.css',
            'bootstrap.min.css',
            'bootstrap.bundle.min.js'
        ]
    }
    
    for folder, files in static_files.items():
        for file in files:
            input_path = f'static/{folder}/{file}'
            if os.path.exists(input_path):
                with open(input_path, 'rb') as f_in:
                    with gzip.open(f'{input_path}.gz', 'wb', compresslevel=9) as f_out:
                        shutil.copyfileobj(f_in, f_out)

if __name__ == '__main__':
    optimize_resources()