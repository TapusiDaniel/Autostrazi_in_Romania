import folium
from config import MAP_CENTER, MAP_ZOOM

def create_base_map():
    """Create the base Folium map."""
    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles='',  # Start with no tiles for a white background
        bgcolor='white',  # Default white background
        title='Romania Highways Map'
    )
    return m