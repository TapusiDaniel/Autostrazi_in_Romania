import folium

def add_hover_effect(m, feature_group):
    """Add hover effect to highways on the map."""
    
    def get_color(feature):
        """Get color based on status"""
        status_colors = {
            "finished": "green",
            "in_construction": "orange",
            "planned": "grey",
            "tendered": "brown"
        }
        properties = feature.get('properties', {})
        status = properties.get('status', '')
        return status_colors.get(status, '#3388ff')
    
    style_function = lambda x: {
        'color': get_color(x),
        'weight': 4,
        'opacity': 1
    }
    
    highlight_function = lambda x: {
        'color': get_color(x),
        'weight': 6,
        'opacity': 1
    }
    
    # Use _children instead of get_children()
    for child in feature_group._children.values():
        if isinstance(child, folium.features.GeoJson):
            child.style_function = style_function
            child.highlight_function = highlight_function
            child.highlight = True
            child.smooth_factor = 0.5
            
            # Add tooltip if it doesn't exist
            if not hasattr(child, 'tooltip'):
                child.tooltip = folium.features.GeoJsonTooltip(
                    fields=['name', 'highway', 'status', 'completion_date', 'length'],
                    aliases=['Tronson:', 'Autostrada:', 'Status:', 'Data finalizării:', 'Lungime:'],
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                )