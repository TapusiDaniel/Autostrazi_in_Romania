import folium
import json
from config import ROMANIA_GEOJSON_FILE
from utils.geo import get_romania_outline

def add_tile_layers(m):
    """Add tile layers to the map."""
    # Add OpenStreetMap tile layer
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        control=True,
        overlay=False,
    ).add_to(m)
    
    # Add satellite tile layer
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        name='Satellite',
        attr='Google Satellite',
        overlay=False,
    ).add_to(m)

    # Add white map as the base tile layer
    folium.TileLayer(
        tiles='',
        attr='Highways.ro',
        bgcolor='white',
        name='White Map',
        overlay=False,
    ).add_to(m)
    
    # Add Romania outline (visible only on the white map)
    add_romania_outline(m)

def add_romania_outline(m):
    """Add Romania outline to the map."""
    with open(ROMANIA_GEOJSON_FILE, 'r', encoding='utf-8') as f:
        romania_geojson = json.load(f)
    romania_outline = get_romania_outline(romania_geojson)
    
    outline = folium.GeoJson(
        romania_outline,
        name="_",
        style_function=lambda x: {
            'fillColor': 'white',
            'color': 'gray',
            'weight': 1.5,
            'fillOpacity': 1,
            'opacity': 1
        },
        class_name='romania-outline',
    )
    outline.add_to(m)