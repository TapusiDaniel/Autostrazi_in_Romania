import requests
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union

def get_all_way_coordinates(way_ids):
    ways_str = ','.join(way_ids)
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    way(id:{ways_str});
    (._;>;);
    out body;
    """
    
    response = requests.post(overpass_url, data=query)
    data = response.json()
    
    nodes = {}
    ways = {}
    
    for element in data['elements']:
        if element['type'] == 'node':
            nodes[element['id']] = [element['lat'], element['lon']]
        elif element['type'] == 'way':
            ways[element['id']] = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
    
    return ways

def get_romania_outline(geojson_data):
    # Convertim toate poligoanele județelor în obiecte Shapely
    polygons = []
    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if isinstance(geom, MultiPolygon):
            polygons.extend(list(geom.geoms))
        else:
            polygons.append(geom)
    
    # Unim toate poligoanele
    union = unary_union(polygons)
    
    # Convertim înapoi în format GeoJSON
    if isinstance(union, MultiPolygon):
        exterior_coords = [list(union.geoms[0].exterior.coords)]
    else:
        exterior_coords = [list(union.exterior.coords)]
    
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": exterior_coords
        }
    }