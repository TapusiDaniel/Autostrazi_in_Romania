import requests
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union
from shapely.geometry import shape, mapping
from shapely import simplify

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

# utils.py
def simplify_geojson(geojson_data, tolerance=0.001):  # Increased tolerance
    """Simplify GeoJSON coordinates to reduce file size."""
    from shapely.geometry import shape, mapping
    from shapely import simplify
    
    def round_coordinates(coords, decimal_places=5):
        """Round coordinates to reduce precision."""
        if isinstance(coords, (int, float)):
            return round(coords, decimal_places)
        elif isinstance(coords, (list, tuple)):
            return [round_coordinates(c, decimal_places) for c in coords]
        return coords

    def process_geometry(geometry):
        """Process and simplify a geometry."""
        if geometry['type'] == 'LineString':
            geom = shape(geometry)
            simplified_geom = simplify(geom, tolerance=tolerance, preserve_topology=True)
            new_geometry = mapping(simplified_geom)
            # Round coordinates to 5 decimal places
            new_geometry['coordinates'] = round_coordinates(new_geometry['coordinates'])
            return new_geometry
        return geometry

    # Remove unnecessary properties
    def clean_properties(properties):
        essential_props = ['name', 'highway', 'status', 'completion_date', 'length']
        return {k: v for k, v in properties.items() if k in essential_props}

    if isinstance(geojson_data, dict):
        if geojson_data['type'] == 'Feature':
            geojson_data['geometry'] = process_geometry(geojson_data['geometry'])
            if 'properties' in geojson_data:
                geojson_data['properties'] = clean_properties(geojson_data['properties'])
        elif geojson_data['type'] == 'FeatureCollection':
            simplified_features = []
            for feature in geojson_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    feature['geometry'] = process_geometry(feature['geometry'])
                    if 'properties' in feature:
                        feature['properties'] = clean_properties(feature['properties'])
                    simplified_features.append(feature)
            geojson_data['features'] = simplified_features

    return geojson_data