import folium

def get_highway_style(status):
    """Get style information based on highway status."""
    status_colors = {
        "finished": "green",
        "in_construction": "orange",
        "planned": "grey",
        "tendered": "brown"
    }
    
    return {
        "color": status_colors.get(status, "#3388ff"),
        "weight": 4,
        "opacity": 1
    }

def create_hover_style(base_style):
    """Create hover style based on base style."""
    hover_style = base_style.copy()
    hover_style["weight"] = 6
    hover_style["opacity"] = 0.8
    return hover_style

def add_highway_hover(m, coordinates, highway_code, section_name, section_data, style_info):
    """Add a highway section with hover effect."""
    
    # Create GeoJSON feature
    geojson_feature = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[coord[1], coord[0]] for coord in coordinates]
        },
        "properties": {
            "name": section_name,
            "highway": highway_code,
            "status": section_data["status"],
            "completion_date": section_data.get("completion_date", "N/A"),
            "length": section_data.get("length", "N/A")
        }
    }
    
    # Create GeoJSON layer with hover effect
    hover_layer = folium.GeoJson(
        geojson_feature,
        style_function=lambda x: {
            'color': style_info["color"],
            'weight': style_info["weight"],
            'opacity': style_info["opacity"],
            'className': f'highway-path status-{section_data["status"]}'
        },
        highlight_function=lambda x: create_hover_style(style_info),
        tooltip=folium.GeoJsonTooltip(
            fields=['name', 'highway', 'status', 'completion_date', 'length'],
            aliases=['Tronson:', 'Autostrada:', 'Status:', 'Data finalizării:', 'Lungime:'],
            style=("background-color: white; color: #333333; "
                  "font-family: arial; font-size: 12px; padding: 10px;")
        ),
        name=section_data["status"]
    )
    
    hover_layer.add_to(m)
    return hover_layer