import shutil
from map_creator import create_highways_map
from build import optimize_resources
import os

def create_htaccess():
    """Create .htaccess for Apache optimization"""
    htaccess_content = """
    # Enable GZIP compression
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/x-javascript application/json
    </IfModule>

    # Set browser caching
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType text/css "access plus 1 year"
        ExpiresByType text/javascript "access plus 1 year"
        ExpiresByType application/javascript "access plus 1 year"
        ExpiresByType application/x-javascript "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
        ExpiresByType image/jpeg "access plus 1 year"
        ExpiresByType image/svg+xml "access plus 1 year"
    </IfModule>
    """
    
    with open('.htaccess', 'w') as f:
        f.write(htaccess_content)

def ensure_directory_structure():
    """Ensure all necessary directories exist"""
    directories = [
        'assets',
        'assets/css',
        'assets/js',
        'assets/vendors'
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    print("Creating directory structure...")
    ensure_directory_structure()
    
    print("Optimizing resources...")
    optimize_resources()
    create_htaccess()
    
    print("Creating map...")
    m = create_highways_map("above")
    m.save('index.html')
    print("Map saved as 'index.html'")

if __name__ == "__main__":
    main()