from map_creator import create_highways_map
from build import optimize_resources
import os

def ensure_static_structure():
    """Ensure static directory structure exists."""
    directories = [
        'static/css',
        'static/js',
        'static/vendors'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    print("Ensuring static structure...")
    ensure_static_structure()
    
    print("Optimizing resources...")
    optimize_resources()
    
    print("Creating map...")
    m = create_highways_map("above")
    m.save('autostrada_a1_detailed1.html')
    print("Map saved as 'autostrada_a1_detailed1.html'")

if __name__ == "__main__":
    main()