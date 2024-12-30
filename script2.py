import requests
import json
from datetime import datetime

def query_feature_layer(layer_url, layer_name):
    params = {
        'where': '1=1',
        'outFields': '*',
        'returnGeometry': 'true',
        'f': 'geojson',
        'outSR': '4326'  # WGS84
    }
    
    try:
        print(f"\nDescărcare layer: {layer_name}")
        print(f"URL: {layer_url}")
        
        response = requests.get(f"{layer_url}/query", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Salvăm datele
            filename = f"monitorizare_rutier_{layer_name.lower()}_{datetime.now().strftime('%Y%m%d')}.geojson"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            features = data.get('features', [])
            print(f"Features descărcate: {len(features)}")
            
            if features:
                print("Exemplu proprietăți primul feature:")
                properties = features[0].get('properties', {})
                for key, value in properties.items():
                    print(f"- {key}: {value}")
            
            return True
            
        else:
            print(f"Eroare descărcare: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Eroare: {str(e)}")
        return False

# Definim layerele disponibile
base_url = "https://services7.arcgis.com/CC3A0nBoLM6gxwLd/arcgis/rest/services/Monitorizare_rutier/FeatureServer"
layers = [
    {"id": 0, "name": "Localitati"},
    {"id": 1, "name": "VO"},
    {"id": 2, "name": "Autostrazi"},
    {"id": 3, "name": "Drum_expres"},
    {"id": 4, "name": "Primara_Secundara"},
    {"id": 5, "name": "Transregio"},
    {"id": 6, "name": "TENT"}
]

# Descărcăm fiecare layer
successful_downloads = []
failed_downloads = []

for layer in layers:
    layer_url = f"{base_url}/{layer['id']}"
    success = query_feature_layer(layer_url, layer['name'])
    
    if success:
        successful_downloads.append(layer['name'])
    else:
        failed_downloads.append(layer['name'])

# Afișăm sumarul
print("\nRezumat descărcare:")
print(f"\nLayere descărcate cu succes ({len(successful_downloads)}):")
for name in successful_downloads:
    print(f"- {name}")

print(f"\nLayere eșuate ({len(failed_downloads)}):")
for name in failed_downloads:
    print(f"- {name}")

# Salvăm metadata despre setul de date
metadata = {
    "service_name": "Monitorizare_rutier",
    "download_date": datetime.now().isoformat(),
    "layers": layers,
    "successful_downloads": successful_downloads,
    "failed_downloads": failed_downloads
}

with open("monitorizare_rutier_metadata.json", 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("\nProcesul de descărcare s-a încheiat. Verifică fișierele generate.")