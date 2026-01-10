import requests
import json
from datetime import datetime

def query_feature_layer(layer_url, layer_name):
    """
    Query an ArcGIS feature layer and save the data as a GeoJSON file.

    Args:
        layer_url (str): The URL of the ArcGIS feature layer.
        layer_name (str): The name of the layer for identification.

    Returns:
        bool: True if the download and save were successful, False otherwise.
    """
    params = {
        'where': '1=1',  # Select all records
        'outFields': '*',  # Include all fields
        'returnGeometry': 'true',  # Include geometry in the response
        'f': 'geojson',  # Response format as GeoJSON
        'outSR': '4326'  # Coordinate system (WGS84 lat/long)
    }
    
    try:
        print(f"\nDownloading layer: {layer_name}")
        print(f"URL: {layer_url}")
        
        # Make the request to the ArcGIS server
        response = requests.get(f"{layer_url}/query", params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save the data to a GeoJSON file
            filename = f"road_monitoring_{layer_name.lower()}_{datetime.now().strftime('%Y%m%d')}.geojson"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Display statistics about the downloaded features
            features = data.get('features', [])
            print(f"Features downloaded: {len(features)}")
            
            if features:
                print("Example properties of the first feature:")
                properties = features[0].get('properties', {})
                for key, value in properties.items():
                    print(f"- {key}: {value}")
            
            return True
            
        else:
            print(f"Download error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Define the available layers
base_url = "https://services7.arcgis.com/CC3A0nBoLM6gxwLd/arcgis/rest/services/Monitorizare_rutier/FeatureServer"
layers = [
    {"id": 0, "name": "Localities"},
    {"id": 1, "name": "VO"},
    {"id": 2, "name": "Highways"},
    {"id": 3, "name": "Express_Roads"},
    {"id": 4, "name": "Primary_Secondary"},
    {"id": 5, "name": "Transregional"},
    {"id": 6, "name": "TENT"}
]

# Download each layer
successful_downloads = []
failed_downloads = []

for layer in layers:
    layer_url = f"{base_url}/{layer['id']}"
    success = query_feature_layer(layer_url, layer['name'])
    
    if success:
        successful_downloads.append(layer['name'])
    else:
        failed_downloads.append(layer['name'])

# Display a summary of the download process
print("\nDownload summary:")
print(f"\nSuccessfully downloaded layers ({len(successful_downloads)}):")
for name in successful_downloads:
    print(f"- {name}")

print(f"\nFailed layers ({len(failed_downloads)}):")
for name in failed_downloads:
    print(f"- {name}")

# Save metadata about the dataset
metadata = [
    {"id": 0, "name": "Localitati"},
    {"id": 1, "name": "VO"},
    {"id": 2, "name": "Autostrazi"},
    {"id": 3, "name": "Drum_expres"},
    {"id": 4, "name": "Primara_Secundara"},
    {"id": 5, "name": "Transregio"},
    {"id": 6, "name": "TENT"}
]

with open("road_monitoring_metadata.json", 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("\nDownload process completed. Check the generated files.")