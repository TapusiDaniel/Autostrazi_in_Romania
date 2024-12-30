import requests
import json

# URL-ul layerului
base_url = "https://services7.arcgis.com/CC3A0nBoLM6gxwLd/arcgis/rest/services/Transparenta_rutier/FeatureServer/2"
query_url = f"{base_url}/query"

# Parametrii pentru query
params = {
    'where': '1=1',  # Selectează toate înregistrările
    'outFields': '*',  # Toate câmpurile
    'returnGeometry': 'true',
    'f': 'geojson',  # Format GeoJSON
    'geometryPrecision': 6,  # Precizia coordonatelor
    'spatialRel': 'esriSpatialRelIntersects',
    'outSR': '4326'  # Sistem de coordonate WGS84 (lat/long)
}

try:
    # Facem request-ul
    response = requests.get(query_url, params=params)
    response.raise_for_status()  # Verifică dacă request-ul a fost cu succes
    
    # Salvăm rezultatul în fișier
    with open('drumuri_romania.geojson', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=2)
    
    print("Datele au fost salvate cu succes în fișierul 'drumuri_romania.geojson'")
    
    # Afișăm câteva statistici
    data = response.json()
    if 'features' in data:
        print(f"\nNumăr total de drumuri: {len(data['features'])}")
        
        # Afișăm tipurile unice de drumuri
        print("\nTipuri de drumuri:")
        types = set(feature['properties']['interv2'] for feature in data['features'] if 'interv2' in feature['properties'])
        for t in sorted(types):
            print(f"- {t}")

except requests.exceptions.RequestException as e:
    print(f"Eroare la descărcarea datelor: {str(e)}")