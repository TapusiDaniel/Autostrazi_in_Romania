import requests
import json

# URL of the ArcGIS layer
base_url = "https://services7.arcgis.com/CC3A0nBoLM6gxwLd/arcgis/rest/services/Transparenta_rutier/FeatureServer/2"
query_url = f"{base_url}/query"

# Parameters for the query
params = {
    'where': '1=1',  # Select all records
    'outFields': '*',  # Include all fields
    'returnGeometry': 'true',  # Include geometry in the response
    'f': 'geojson',  # Response format as GeoJSON
    'geometryPrecision': 6,  # Coordinate precision
    'spatialRel': 'esriSpatialRelIntersects',  # Spatial relationship
    'outSR': '4326'  # Coordinate system (WGS84 lat/long)
}

try:
    # Make the request to the ArcGIS server
    response = requests.get(query_url, params=params)
    response.raise_for_status()  # Check if the request was successful
    
    # Save the result to a GeoJSON file
    with open('roads_romania.geojson', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=2)
    
    print("Data successfully saved to 'roads_romania.geojson'")
    
    # Display some statistics
    data = response.json()
    if 'features' in data:
        print(f"\nTotal number of roads: {len(data['features'])}")
        
        # Display unique road types
        print("\nRoad types:")
        types = set(feature['properties']['interv2'] for feature in data['features'] if 'interv2' in feature['properties'])
        for t in sorted(types):
            print(f"- {t}")

except requests.exceptions.RequestException as e:
    print(f"Error downloading data: {str(e)}")