import folium
from config import CITIES, CITY_BOUNDARIES, CITY_LABELS
from map_elements import add_city_boundaries

def add_cities_to_map(m, labels_position="below"):
    """Add cities, boundaries, labels and markers to the map."""
    # Add city boundaries
    add_city_boundaries(m)
    
    # Add city labels and markers
    add_city_labels(m, labels_position)
    add_city_markers(m)

def add_city_labels(m, labels_position="below"):
    """Add city labels to the map."""
    # Configure label positions
    position_config = {
        "bottom": {
            "icon_anchor": (0, 0),
            "html_style": "text-align: center; position: absolute; left: -50px; top: 3px; width: 100px;"
        },
        "top": {
            "icon_anchor": (0, 0), 
            "html_style": "text-align: center; position: absolute; left: -50px; top: -20px; width: 100px;"
        },
        "left": {
            "icon_anchor": (0, 0),
            "html_style": "text-align: right; position: absolute; right: 3px; top: -3px; width: 100px;"
        },
        "right": {
            "icon_anchor": (0, 0),
            "html_style": "text-align: left; position: absolute; left: 3px; top: -3px; width: 100px;"
        }
    }

    # Add city labels (visible on white map and satellite)
    for city, coords in CITIES.items():
        label_position = CITY_LABELS.get(city, "right")
        config = position_config[label_position]
        
        marker = folium.Marker(
            coords,
            icon=folium.DivIcon(
                html=f'<div class="city-label" style="{config["html_style"]}; '
                    f'font-size: 11px; font-weight: bold;">{city}</div>',
                icon_size=(0, 0),
                icon_anchor=config["icon_anchor"],
            )
        )
        marker.add_to(m)

def add_city_markers(m):
    """Add city markers (dots) to the map."""
    # Add dots for cities (visible on all maps)
    for city, coords in CITIES.items():
        if city not in CITY_BOUNDARIES:  # Add dots only for cities without boundaries
            fill_color = "#E0E0E0"  # Default fill color
            border_color = "#4A4A4A"  # Default border color
            
            folium.CircleMarker(
                coords,
                radius=3,
                color=border_color,
                fill=True,
                fillColor=fill_color,
                fillOpacity=1,
                weight=1,
                name="_",
                class_name="city-dot"
            ).add_to(m)