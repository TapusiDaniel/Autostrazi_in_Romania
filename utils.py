import requests
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union

def get_all_way_coordinates(way_ids):
    """
    Fetch coordinates for a list of OpenStreetMap way IDs using the Overpass API.

    Args:
        way_ids (list): A list of OpenStreetMap way IDs.

    Returns:
        dict: A dictionary mapping way IDs to their respective coordinates.
    """
    # Convert the list of way IDs into a comma-separated string
    ways_str = ','.join(way_ids)
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Define the Overpass query to fetch way and node data
    query = f"""
    [out:json];
    way(id:{ways_str});
    (._;>;);
    out body;
    """
    
    # Send the request to the Overpass API
    response = requests.post(overpass_url, data=query)
    data = response.json()
    
    # Extract nodes and ways from the response
    nodes = {}
    ways = {}
    
    for element in data['elements']:
        if element['type'] == 'node':
            # Store node coordinates
            nodes[element['id']] = [element['lat'], element['lon']]
        elif element['type'] == 'way':
            # Store way coordinates by referencing node IDs
            ways[element['id']] = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
    
    return ways

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