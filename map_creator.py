import folium
import json
from config import MAP_CENTER, MAP_ZOOM, ROMANIA_GEOJSON_FILE, CITIES, CITY_BOUNDARIES
from utils import get_romania_outline
from map_elements import (add_cities_to_map, 
                         add_all_highways_to_map, 
                         add_romania_outline_to_map,
                         add_base_layer,
                         add_city_boundaries)
from map_hover import add_hover_effect

def create_highways_map(labels_position="below"):
    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='© OpenStreetMap contributors',  # Adăugat atribuirea
        prefer_canvas=True,
        disable_3d=True
    )
    
    header_content = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <style>
    body {
        margin: 0;
        padding: 0;
    }
    #map {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
    }
    .title {
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999;
        background: white;
        padding: 5px 15px;
        border-radius: 3px;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
    }
    .footer {
        position: absolute;
        bottom: 10px;
        right: 10px;
        z-index: 999;
        background: white;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 12px;
        font-family: Arial, sans-serif;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
    }
    .footer a {
        color: #0066cc;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    """
    m.get_root().header.add_child(folium.Element(header_content))
    
    # Adaugă titlu și footer
    page_elements = """
    <div class="title">Autostrăzi în România</div>
    <div class="footer">
        <a href="https://github.com/TapusiDaniel/Autostrazi_in_Romania" target="_blank">GitHub Repository</a>
    </div>
    """
    m.get_root().html.add_child(folium.Element(page_elements))

    # Add tile layers
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        attr='© OpenStreetMap contributors',  # Adăugat atribuirea
        control=True,
        overlay=False,
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='CartoDB Light',
        attr='© CartoDB',  # Adăugat atribuirea
        control=True,
        overlay=False,
    ).add_to(m)
    
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        name='EGIS',
        attr='© Google',  # Adăugat atribuirea
        overlay=False,
    ).add_to(m)

    white_map = folium.TileLayer(
        tiles='',
        attr='© Highways.ro',  # Adăugat atribuirea
        bgcolor='white',
        name='Hartă Albă',
        overlay=False,
    ).add_to(m)
    
    # Add Romania outline
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
    add_city_boundaries(m)
    
    # Add city labels
    for city, coords in CITIES.items():
        if labels_position == "below":
            icon_anchor = (0, -10)
            padding_top = "8px"
        else:
            icon_anchor = (0, 20)
            padding_top = "-18px"
            
        marker = folium.Marker(
            coords,
            icon=folium.DivIcon(
                html=f'<div class="city-label" style="font-size: 11px; '
                     f'font-weight: bold; color: black; text-align: center; '
                     f'position: absolute; width: 100px; margin-left: -50px; '
                     f'padding-top: {padding_top};">{city}</div>',
                icon_size=(0, 0),
                icon_anchor=icon_anchor,
            )
        )
        marker.add_to(m)
    
    # Add city markers
    for city, coords in CITIES.items():
        if city not in CITY_BOUNDARIES:
            fill_color = "#E0E0E0"
            border_color = "#4A4A4A"
            
            folium.CircleMarker(
                coords,
                radius=3,
                color=border_color,
                fill=True,
                fillColor=fill_color,
                fillOpacity=1,
                weight=1,
                name="_"
            ).add_to(m)

    # Create a FeatureGroup for highways
    highways_group = folium.FeatureGroup(name="Highways")
    add_all_highways_to_map(highways_group)
    highways_group.add_to(m)
    
    # Add hover effect
    add_hover_effect(m, highways_group)
    
    # Add layer control
    folium.LayerControl(position='topright').add_to(m)
    
    # Add loading indicator
    loading_script = """
    <script>
    var loadingControl = L.control({position: 'topright'});
    loadingControl.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'loading-indicator');
        div.innerHTML = 'Se încarcă...';
        div.style.display = 'none';
        div.style.padding = '5px';
        div.style.background = 'white';
        div.style.border = '1px solid #ccc';
        return div;
    };
    loadingControl.addTo(map);
    
    map.on('layeradd', function(e) {
        document.querySelector('.loading-indicator').style.display = 'block';
    });
    map.on('layerremove', function(e) {
        document.querySelector('.loading-indicator').style.display = 'none';
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(loading_script))
    
    # Add visibility control script
    visibility_script = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var overlays = document.querySelector('.leaflet-control-layers-overlays');
        if(overlays) {
            overlays.style.display = 'none';
        }
        
        var labels = document.querySelectorAll('.city-label');
        var outline = document.querySelector('.leaflet-overlay-pane .romania-outline');
        
        function updateVisibility() {
            var activeLayer = document.querySelector('.leaflet-control-layers-base input:checked').parentElement.textContent.trim();
            var isWhiteMap = activeLayer === 'Hartă Albă';
            var isEGIS = activeLayer === 'EGIS';
            var isCartoDB = activeLayer === 'CartoDB Light';
            var isOSM = activeLayer === 'OpenStreetMap';
            
            labels.forEach(function(label) {
                label.style.display = (isWhiteMap || isEGIS) ? 'block' : 'none';
                label.style.color = isEGIS ? 'white' : 'black';
                label.style.textShadow = isEGIS ? '2px 2px 2px black' : 'none';
            });
            
            if (outline) {
                outline.style.display = isWhiteMap ? 'block' : 'none';
            }

            document.querySelectorAll('.city-boundary').forEach(function(element) {
                element.style.display = isWhiteMap ? 'block' : 'none';
                element.style.visibility = isWhiteMap ? 'visible' : 'hidden';
            });

            document.querySelectorAll('.leaflet-circle-marker-pane > *').forEach(function(dot) {
                dot.style.display = (isCartoDB || isWhiteMap || isEGIS) ? 'block' : 'none';
            });
        }
        
        var layerInputs = document.querySelectorAll('.leaflet-control-layers-base input');
        layerInputs.forEach(function(input) {
            input.addEventListener('change', updateVisibility);
        });
        
        var whiteMapRadio = Array.from(layerInputs).find(input => 
            input.parentElement.textContent.trim() === 'Hartă Albă'
        );
        if (whiteMapRadio) {
            whiteMapRadio.click();
        }
        
        updateVisibility();
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(visibility_script))
    
# La final, adaugă script pentru loading screen
    loading_screen = """
    <div id="loading" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: white;
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: Arial, sans-serif;">
        <div>
            <h2>Se încarcă harta...</h2>
            <div style="width: 150px; height: 4px; background: #eee; border-radius: 2px;">
                <div id="progress" style="width: 0%; height: 100%; background: #4CAF50; border-radius: 2px; transition: width 0.3s;"></div>
            </div>
        </div>
    </div>
    <script>
    window.addEventListener('load', function() {
        document.getElementById('loading').style.display = 'none';
    });
    let progress = 0;
    const progressBar = document.getElementById('progress');
    const interval = setInterval(() => {
        progress += 5;
        if (progress > 90) clearInterval(interval);
        progressBar.style.width = progress + '%';
    }, 100);
    </script>
    """
    m.get_root().html.add_child(folium.Element(loading_screen))

    return m