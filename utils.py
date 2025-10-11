import requests
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union
import time
import json

def get_all_way_coordinates(way_ids):
    """
    Fetch coordinates for a list of OpenStreetMap way IDs using the Overpass API.
    """
    ways_str = ','.join(way_ids)
    overpass_url = "https://overpass.private.coffee/api/interpreter"
    
    query = f"""
    [out:json];
    way(id:{ways_str});
    (._;>;);
    out body;
    """
    
    # Adăugăm retry logic și error handling
    max_retries = 3
    retry_delay = 2  # secunde
    
    for attempt in range(max_retries):
        try:
            response = requests.post(overpass_url, data=query, timeout=30)
            response.raise_for_status()  # Verifică pentru erori HTTP
            
            # Verifică dacă răspunsul este JSON valid
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"Invalid JSON response: {response.text[:200]}...")
                raise
                
            # Procesează datele
            nodes = {}
            ways = {}
            
            for element in data['elements']:
                if element['type'] == 'node':
                    nodes[element['id']] = [element['lat'], element['lon']]
                elif element['type'] == 'way':
                    ways[element['id']] = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
            
            return ways
            
        except requests.exceptions.RequestException as e:
            print(f"Request attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                print(f"Failed after {max_retries} attempts")
                raise
                
        except Exception as e:
            print(f"Error processing data: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                raise

    return {}  # Returnează dict gol dacă totul eșuează

def get_romania_outline(geojson_data):
    """
    Generate a unified outline of Romania from GeoJSON data containing county polygons.

    Args:
        geojson_data (dict): GeoJSON data containing Romania's county polygons.

    Returns:
        dict: A GeoJSON feature representing the unified outline of Romania.
    """
    # Convert all county polygons into Shapely objects
    polygons = []
    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if isinstance(geom, MultiPolygon):
            # If the geometry is a MultiPolygon, extract individual polygons
            polygons.extend(list(geom.geoms))
        else:
            # Otherwise, add the polygon directly
            polygons.append(geom)
    
    # Merge all polygons into a single geometry
    union = unary_union(polygons)
    
    # Convert the unified geometry back to GeoJSON format
    if isinstance(union, MultiPolygon):
        # If the result is a MultiPolygon, use the first polygon's exterior coordinates
        exterior_coords = [list(union.geoms[0].exterior.coords)]
    else:
        # Otherwise, use the exterior coordinates of the single polygon
        exterior_coords = [list(union.exterior.coords)]
    
    # Return the unified outline as a GeoJSON feature
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": exterior_coords
        }
    }