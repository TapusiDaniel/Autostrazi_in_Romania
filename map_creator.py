import folium
import json
from config import MAP_CENTER, MAP_ZOOM, ROMANIA_GEOJSON_FILE, CITIES, CITY_BOUNDARIES
from highway_data import HIGHWAYS
from utils import get_romania_outline
from map_elements import (add_cities_to_map, 
                         add_all_highways_to_map, 
                         add_romania_outline_to_map,
                         add_base_layer,
                         add_city_boundaries,
                         calculate_highway_totals)

def add_totals_table(m, highways_data):
    """Add the totals table to the map."""
    totals = calculate_highway_totals(highways_data)
    
    # Create the table HTML
    table_html = f"""
    <div id="totals-table" class="totals-table">
        <table>
            <tr class="total-row">
                <td>Total:</td>
                <td>{totals['total']:.1f} km</td>
            </tr>
            <tr class="status-row finished">
                <td>Finalizat:</td>
                <td>{totals['finished']:.1f} km</td>
            </tr>
            <tr class="status-row in-construction">
                <td>În construcție:</td>
                <td>{totals['in_construction']:.1f} km</td>
            </tr>
            <tr class="status-row planned">
                <td>Planificat:</td>
                <td>{totals['planned']:.1f} km</td>
            </tr>
            <tr class="status-row tendered">
                <td>Licitat:</td>
                <td>{totals['tendered']:.1f} km</td>
            </tr>
        </table>
    </div>
    """
    
    # Add CSS
    css = """
    <style>
    .totals-table {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        z-index: 1000;
        font-family: Arial, sans-serif;
        font-size: 12px;
    }
    
    .totals-table table {
        border-collapse: collapse;
    }
    
    .totals-table td {
        padding: 3px 10px;
        border-bottom: 1px solid #eee;
    }
    
    .totals-table tr:last-child td {
        border-bottom: none;
    }
    
    .total-row {
        font-weight: bold;
    }
    
    .status-row.finished td:first-child {
        color: green;
    }
    
    .status-row.in-construction td:first-child {
        color: orange;
    }
    
    .status-row.planned td:first-child {
        color: grey;
    }
    
    .status-row.tendered td:first-child {
        color: brown;
    }
    </style>
    """
    
    # Add elements to map
    m.get_root().html.add_child(folium.Element(css))
    m.get_root().html.add_child(folium.Element(table_html))

def optimize_template(html_content):
    """Optimize the Folium-generated HTML template."""
    
    # Curățăm title-ul întâi
    html_content = html_content.replace(
        '/* Essential styles for initial render */ .map-container { height: 100vh; width: 100%; } .loading { position: fixed; /* etc */ }',
        'Harta autostrăzilor din România'  # sau alt titlu dorit
    )
    
    # Split the content to insert our optimizations
    head_end = html_content.find('</head>')
    body_end = html_content.find('</body>')
    
    if head_end == -1 or body_end == -1:
        return html_content
        
    # Critical CSS that should be inlined
    critical_css = """
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            font-family: Arial, sans-serif;
        }
        #map { 
            position: absolute; 
            top: 0; 
            bottom: 0; 
            width: 100%; 
            height: 100vh;
            z-index: 1;
        }
        .leaflet-container { 
            height: 100vh; 
            width: 100%; 
            background: white;
        }
        .map-controls {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.4);
            z-index: 1000;
        }
        .totals-table {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }
    </style>
    """
    
    # Preload directives
    preload_tags = """
    <link rel="preload" href="/static/vendors/leaflet.js" as="script">
    <link rel="preload" href="/static/css/main.css" as="style">
    """
    
    # Async CSS loading
    async_css = """
    <link rel="stylesheet" href="/static/css/main.css" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="/static/css/main.css"></noscript>
    <link rel="stylesheet" href="/static/css/async.css" media="print" onload="this.media='all'">
    """
    
    # Resource loader script
    resource_loader = """
    <script>
        function loadDeferred() {
            const resources = {
                css: [
                    '/static/vendors/leaflet.awesome-markers.css',
                    '/static/vendors/bootstrap-glyphicons.css',
                    '/static/vendors/fontawesome-all.min.css',
                    '/static/vendors/bootstrap.min.css',
                    '/static/vendors/leaflet.css',
                    '/static/vendors/leaflet.awesome.rotate.min.css'
                ],
                js: [
                    '/static/vendors/leaflet.awesome-markers.js',
                    '/static/vendors/jquery.min.js',
                    '/static/vendors/bootstrap.bundle.min.js',
                    '/static/vendors/leaflet.js'
                ]
            };

            // Load CSS files
            resources.css.forEach(file => {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = file;
                document.head.appendChild(link);
            });

            // Load JS files
            let loadedScripts = 0;
            resources.js.forEach(file => {
                const script = document.createElement('script');
                script.src = file;
                script.async = true;
                script.onload = () => {
                    loadedScripts++;
                    if (loadedScripts === resources.js.length) {
                        // Initialize any deferred functionality
                        if (window.initMap) window.initMap();
                    }
                };
                document.body.appendChild(script);
            });
        }

        // Load deferred resources after initial render
        if (document.readyState === 'complete') {
            loadDeferred();
        } else {
            window.addEventListener('load', loadDeferred);
        }
    </script>
    """
    
    # Inject our optimizations
    optimized_html = (
        html_content[:head_end] +
        critical_css +
        preload_tags +
        async_css +
        html_content[head_end:body_end] +
        resource_loader +
        html_content[body_end:]
    )
    
    # Remove any blocking scripts and CSS from the original template
    blocking_resources = [
        'leaflet.awesome-markers.js',
        'jquery-3.7.1.min.js',
        'bootstrap.bundle.min.js',
        'leaflet.js',
        'leaflet.awesome-markers.css',
        'bootstrap-glyphicons.css',
        'fontawesome-free',
        'bootstrap.min.css',
        'leaflet.css',
        'leaflet.awesome.rotate.min.css'
    ]
    
    for resource in blocking_resources:
        optimized_html = optimized_html.replace(
            f'<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/{resource}"',
            f'<!-- Deferred: {resource} -->'
        )
        optimized_html = optimized_html.replace(
            f'<script src="https://cdn.jsdelivr.net/npm/{resource}"',
            f'<!-- Deferred: {resource} -->'
        )
    
    return optimized_html

def create_highways_map(labels_position="below"):
    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles='',  # Începem cu tiles gol pentru harta albă
        bgcolor='white',  # Fundal alb implicit
        title = 'Harta autostrăzilor din România'
    )
    
     # Adăugăm meta tags pentru optimizare
    meta_tags = """
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Hartă interactivă a autostrăzilor din România">
        <title>Autostrăzi în România</title>
    """
    m.get_root().header.add_child(folium.Element(meta_tags))
    
    # CSS critic optimizat
    critical_css = """
    <style>
        body{margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif}
        #map{position:absolute;top:0;bottom:0;width:100%;height:100vh;z-index:1}
        .leaflet-container{height:100vh;width:100%;background:#fff}
        .controls{position:absolute;top:10px;right:10px;background:#fff;padding:8px;border-radius:4px;box-shadow:0 2px 4px rgba(0,0,0,.1);z-index:1000}
        .stats{position:fixed;bottom:20px;right:20px;background:#fff;padding:10px;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,.1);z-index:1000;font-size:14px}
        .btn{margin:2px 0;padding:6px 12px;border:1px solid #ddd;background:#fff;border-radius:3px;cursor:pointer}
        .btn:hover{background:#f8f8f8}
        select{padding:6px;border:1px solid #ddd;border-radius:3px;background:#fff}
    </style>
    """
    m.get_root().header.add_child(folium.Element(critical_css))

    script_loader = """
        <script>
            // Defer non-critical resource loading
            function loadDeferred() {
                // Load non-critical CSS
                const cssFiles = [
                    '/static/vendors/leaflet.awesome-markers.css',
                    '/static/vendors/bootstrap-glyphicons.css',
                    // etc
                ];
                
                cssFiles.forEach(file => {
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = file;
                    document.head.appendChild(link);
                });
                
                // Load non-critical JS
                const jsFiles = [
                    '/static/vendors/leaflet.awesome-markers.js',
                    '/static/vendors/jquery.min.js',
                    // etc
                ];
                
                jsFiles.forEach(file => {
                    const script = document.createElement('script');
                    script.src = file;
                    script.async = true;
                    document.body.appendChild(script);
                });
            }
            
            // Load deferred resources after initial render
            if (document.readyState === 'complete') {
                loadDeferred();
            } else {
                window.addEventListener('load', loadDeferred);
            }
        </script>
    """
    
    m.get_root().html.add_child(folium.Element(script_loader))

    # Resource hints pentru optimizare
    preload_hints = """
    <link rel="preconnect" href="https://unpkg.com">
    <link rel="preconnect" href="https://cdn.jsdelivr.net">
    <link rel="dns-prefetch" href="https://unpkg.com">
    <link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
    """
    m.get_root().header.add_child(folium.Element(preload_hints))
    
    # Script de încărcare lazy pentru resurse non-critice
    lazy_load = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        function loadStyle(src) {
            let link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = src;
            link.media = 'print';
            link.onload = function() {this.media='all'};
            document.head.appendChild(link);
        }
        
        // Încărcăm stilurile non-critice după ce pagina s-a încărcat
        setTimeout(function() {
            [
                'https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css',
                'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css'
            ].forEach(loadStyle);
        }, 100);
    });
    </script>
    """
    m.get_root().header.add_child(folium.Element(lazy_load))

    # Adăugăm OpenStreetMap
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        control=True,
        overlay=False,
    ).add_to(m)
    
    # Adăugăm EGIS (satellite)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        name='EGIS',
        attr='Google Satellite',
        overlay=False,
    ).add_to(m)

    # Adăugăm harta albă ca tile layer de bază
    white_map = folium.TileLayer(
        tiles='',
        attr='Highways.ro',
        bgcolor='white',
        name='Hartă Albă',
        overlay=False,
    ).add_to(m)
    
    # Adăugăm conturul României (vizibil doar pe harta albă)
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
    
    # Adăugăm numele orașelor (pentru harta albă și EGIS)
    for city, coords in CITIES.items():
        if labels_position == "below":
            icon_anchor = (0, -10)
            padding_top = "8px"
        else:  # "above"
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
    
    # Adăugăm punctele roșii pentru orașe (vizibile pe toate hărțile)
    for city, coords in CITIES.items():
        if city not in CITY_BOUNDARIES:  # Adăugăm puncte doar pentru orașele fără boundary
            fill_color = "#E0E0E0"  # culoare implicită pentru fill
            border_color = "#4A4A4A"  # culoare implicită pentru border
            
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
    
    # Adăugăm autostrăzile (vizibile pe toate hărțile)
    add_all_highways_to_map(m)
    
    # Adăugăm JavaScript pentru a gestiona elementele hărții albe
    script = """
    <style>
    .minimize-button {
        position: absolute;
        top: 5px;
        right: 5px;
        width: 20px;
        height: 20px;
        background: #fff;
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        z-index: 1001;
    }

    .minimize-button:hover {
        background: #f0f0f0;
    }

    .map-controls.minimized .map-button-group {
        display: none;
    }

    .map-controls.minimized {
        background: transparent;  /* Make background transparent */
        box-shadow: none;  /* Remove shadow */
        width: 20px;  /* Match button width */
        height: 20px;  /* Match button height */
        padding: 0;  /* Remove padding */
    }

    .map-controls {
        position: absolute;
        top: 10px;
        right: 10px;
        background: white;
        padding: 10px;
        border-radius: 4px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.4);
        z-index: 1000;
    }

    .map-button {
        display: block;
        margin: 5px 0;
        padding: 8px 15px;
        border: none;
        border-radius: 4px;
        background: #fff;
        color: #333;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 150px;
        text-align: left;
    }

    .map-button:hover {
        background: #f0f0f0;
    }

    .map-button.active {
        background: #4a90e2;
        color: white;
    }

    .map-button-group {
        margin-bottom: 15px;
    }

    .map-button-group-title {
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
        color: #666;
    }

    .section-button {
        display: flex;
        align-items: center;
        margin: 5px 0;
        padding: 8px 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: #fff;
        color: #333;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 150px;
    }

    .section-button.active {
        border-color: #4a90e2;
        background: #f5f9ff;
    }

    .section-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
    }

    .section-all .section-indicator {
        background: linear-gradient(45deg, green 25%, orange 25% 50%, brown 50% 75%, grey 75%);
    }

    .section-finished .section-indicator {
        background-color: green;
    }

    .section-in-construction .section-indicator {
        background-color: orange;
    }

    .section-tendered .section-indicator {
        background-color: brown;
    }

    .section-planned .section-indicator {
        background-color: grey;
    }

    .highway-path {
        transition: all 0.3s ease;
    }

    .highway-path:hover {
        cursor: pointer;
        filter: brightness(1.2);
    }

    .status-finished:hover {
        stroke: #00ff00;
    }

    .status-in_construction:hover {
        stroke: #ffa500;
    }

    .status-planned:hover {
        stroke: #808080;
    }

    .status-tendered:hover {
        stroke: #a52a2a;
    }

    .leaflet-control-layers-base {
        display: none !important;
    }
    .leaflet-control-layers-overlays label:first-child {
        display: none !important;
    }
    .leaflet-control-layers-toggle {
        display: none !important;
    }
    .leaflet-control-layers {
        display: none !important;
    }
    .leaflet-control {
        display: none !important;
    }

    .year-button {
        display: flex;
        align-items: center;
        margin: 5px 0;
        padding: 8px 15px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: #fff;
        color: #333;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 150px;
    }

    .year-button.active {
        border-color: #4a90e2;
        background: #f5f9ff;
    }

    .highway-logo {
        transition: all 0.3s ease;
    }

    .highway-logo:hover {
        transform: scale(1.2);
        box-shadow: 0 3px 7px rgba(0,0,0,0.3);
    }

    /* Asigură-te că logo-urile sunt mereu deasupra altor elemente */
    .highway-logo-marker {
        z-index: 1000 !important;
    }

    </style>

    <div class="map-controls">
        <button class="minimize-button">−</button>
        <div class="map-button-group">
            <div class="map-button-group-title">Stil hartă</div>
            <button class="map-button active" data-map="white">Hartă Albă</button>
            <button class="map-button" data-map="osm">OpenStreetMap</button>
            <button class="map-button" data-map="satellite">Satelit</button>
        </div>

        <div class="map-button-group">
            <div class="map-button-group-title">Secțiuni</div>
            <button class="section-button section-all active" data-section="all">
                <span class="section-indicator"></span>
                Toate secțiunile
            </button>
            <button class="section-button section-finished" data-section="Finished">
                <span class="section-indicator"></span>
                Doar finalizate
            </button>
            <button class="section-button section-in-construction" data-section="In Construction">
                <span class="section-indicator"></span>
                Doar în construcție
            </button>
            <button class="section-button section-tendered" data-section="Tendered">
                <span class="section-indicator"></span>
                Doar în licitație
            </button>
            <button class="section-button section-planned" data-section="Planned">
                <span class="section-indicator"></span>
                Doar planificate
            </button>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        var mapButtons = document.querySelectorAll('.map-button[data-map]');
        var sectionButtons = document.querySelectorAll('.section-button');
        var overlays = document.querySelector('.leaflet-control-layers-overlays');
        var minimizeButton = document.querySelector('.minimize-button');
        var mapControls = document.querySelector('.map-controls');
        if(overlays) {
            overlays.style.display = 'none';
        }
        
        if (minimizeButton && mapControls) {
                minimizeButton.addEventListener('click', function() {
                    mapControls.classList.toggle('minimized');
                    minimizeButton.textContent = mapControls.classList.contains('minimized') ? '+' : '−';
                });
            }

        var labels = document.querySelectorAll('.city-label');
        var outline = document.querySelector('.leaflet-overlay-pane .romania-outline');
        
        function updateMapStyle(activeButton, skipButtonUpdate = false) {
            if (!skipButtonUpdate) {
                mapButtons.forEach(button => button.classList.remove('active'));
                activeButton.classList.add('active');
            }
            
            var mapStyle = activeButton.getAttribute('data-map');
            
            // Handle the white background and outline specifically
            if (outline) {
                outline.style.display = mapStyle === 'white' ? 'block' : 'none';
            }
            
            // Only hide the white background element, not all overlay paths
            document.querySelectorAll('.leaflet-overlay-pane .romania-outline, .leaflet-overlay-pane .white-background').forEach(function(element) {
                element.style.display = mapStyle === 'white' ? 'block' : 'none';
            });
            
            if (!skipButtonUpdate) {
                // Find and click the correct base layer radio button
                var baseLayerName = {
                    'white': 'Hartă Albă',
                    'osm': 'OpenStreetMap',
                    'satellite': 'EGIS'
                }[mapStyle];
                
                var baseInput = Array.from(document.querySelectorAll('.leaflet-control-layers-base input'))
                    .find(input => input.nextElementSibling.textContent.trim() === baseLayerName);
                if (baseInput) baseInput.click();
            }
            
            var isWhiteMap = mapStyle === 'white';
            var isEGIS = mapStyle === 'satellite';
            
            // Update labels
            labels.forEach(function(label) {
                label.style.display = (isWhiteMap || isEGIS) ? 'block' : 'none';
                label.style.color = isEGIS ? 'white' : 'black';
                label.style.textShadow = isEGIS ? '2px 2px 2px black' : 'none';
            });
            
            // Update city boundaries
            document.querySelectorAll('.city-boundary').forEach(function(element) {
                element.style.display = isWhiteMap ? 'block' : 'none';
                element.style.visibility = isWhiteMap ? 'visible' : 'hidden';
            });
            
            // Update city dots
            document.querySelectorAll('.leaflet-circle-marker-pane > *').forEach(function(dot) {
                dot.style.display = (isWhiteMap || isEGIS) ? 'block' : 'none';
            });

            // Ensure proper z-index for background elements
            if (outline) {
                outline.parentElement.style.zIndex = isWhiteMap ? '1' : '-1';
            }
        }

        function selectSection(button) {
            sectionButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            var sectionName = button.getAttribute('data-section');
            var activeMapButton = document.querySelector('.map-button.active');
            var isWhiteMap = activeMapButton && activeMapButton.getAttribute('data-map') === 'white';
            
            // Update section visibility while preserving city boundaries and outline
            var overlayInputs = document.querySelectorAll('.leaflet-control-layers-overlays input[type="checkbox"]');
            overlayInputs.forEach(function(input) {
                var label = input.nextElementSibling.textContent.trim();
                
                // Skip processing for elements we want to preserve
                if (label === '_') {
                    return;  // Skip the outline layer
                }

                // Handle highway sections
                if (sectionName === 'all') {
                    if (!input.checked) input.click();
                } else {
                    if (label === sectionName && !input.checked) input.click();
                    else if (label !== sectionName && input.checked) input.click();
                }
            });

            // For white map, ensure all elements remain visible
            if (isWhiteMap) {
                // Ensure outline is visible
                if (outline) {
                    outline.style.display = 'block';
                    outline.parentElement.style.zIndex = '1';
                }
                
                // Ensure Romania outline and white background are visible
                document.querySelectorAll('.leaflet-overlay-pane .romania-outline, .leaflet-overlay-pane .white-background').forEach(function(element) {
                    element.style.display = 'block';
                });
                
                // Explicitly ensure city boundaries are visible
                document.querySelectorAll('.city-boundary').forEach(function(element) {
                    element.style.display = 'block';
                    element.style.visibility = 'visible';
                    // Force a repaint
                    element.style.opacity = 0.99;
                    setTimeout(() => {
                        element.style.opacity = 1;
                    }, 10);
                });
                
                // Ensure labels are visible
                document.querySelectorAll('.city-label').forEach(function(label) {
                    label.style.display = 'block';
                    label.style.color = 'black';
                    label.style.textShadow = 'none';
                });
                
                // Ensure city dots are visible
                document.querySelectorAll('.leaflet-circle-marker-pane > *').forEach(function(dot) {
                    dot.style.display = 'block';
                });
            }
        }
        
        // Event listeners
        mapButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                updateMapStyle(this);
            });
        });

        sectionButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                selectSection(this);
            });
        });
        
        // Initial setup
        var whiteMapButton = document.querySelector('.map-button[data-map="white"]');
        if (whiteMapButton) {
            updateMapStyle(whiteMapButton);
        }

        // Show all sections initially
        var allButton = document.querySelector('.section-button[data-section="all"]');
        if (allButton) {
            selectSection(allButton);
        }
    });
    </script>
    """

    # Add the layer control and script
    m.get_root().html.add_child(folium.Element(script))
    folium.LayerControl(position='topright').add_to(m)

    add_totals_table(m, HIGHWAYS)
    
    original_save = m.save
    
    def optimized_save(path, **kwargs):
        original_save(path, **kwargs)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        optimized_content = optimize_template(content)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
    
    m.save = optimized_save
    
    return m