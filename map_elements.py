import folium
from config import CITIES
from utils import get_all_way_coordinates
from config import CITY_BOUNDARIES
import xml.etree.ElementTree as ET
import math
import json
import requests
import xml.etree.ElementTree as ET

def add_highway_logo(m, coordinates, logo_path, highway_code):
    """Adaugă logo-ul autostrăzii pe hartă."""
    if not coordinates:
        return
        
    # Calculăm centrul aproximativ al autostrăzii
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Adăugăm un marker custom cu logo-ul
    icon_html = f"""
        <div class="highway-logo" style="
            background-image: url('{logo_path}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: white;
            border: 2px solid #666;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
        ">
        </div>
    """
    
    folium.Marker(
        [center_lat, center_lon],
        icon=folium.DivIcon(
            html=icon_html,
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            class_name=f'highway-logo-marker {highway_code.lower()}'
        )
    ).add_to(m)

def add_cities_to_map(m, labels_position="below"):
    """Adaugă orașele pe hartă cu puncte și etichete."""
    from config import CITIES, CITY_BOUNDARIES
    
    # Configurăm poziția etichetelor
    if labels_position == "below":
        icon_anchor = (0, -10)
        padding_top = "8px"
    else:  # "above"
        icon_anchor = (0, 20)
        padding_top = "-18px"

    # Adăugăm orașele cu puncte și nume
    for city, coords in CITIES.items():
        # Folosim culorile din CITY_BOUNDARIES dacă există, altfel folosim culori implicite
        fill_color = "#E0E0E0"  # culoare implicită pentru fill
        border_color = "#4A4A4A"  # culoare implicită pentru border
        
        if city in CITY_BOUNDARIES:
            fill_color = CITY_BOUNDARIES[city].get('fill_color', fill_color)
            border_color = CITY_BOUNDARIES[city].get('border_color', border_color)
            
            # Adăugăm doar textul pentru orașele cu boundary
            folium.Marker(
                coords,
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 11px; font-weight: bold; color: {border_color}; '
                         f'text-align: center; position: absolute; width: 100px; '
                         f'margin-left: -50px; padding-top: {padding_top};">{city}</div>',
                    icon_size=(0, 0),
                    icon_anchor=icon_anchor,
                    class_name="transparent"
                )
            ).add_to(m)
        else:
            # Adăugăm punct și text doar pentru orașele fără boundary
            folium.CircleMarker(
                coords,
                radius=3,
                color=border_color,
                fill=True,
                fillColor=fill_color,
                fillOpacity=1,
                weight=1
            ).add_to(m)

            folium.Marker(
                coords,
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 11px; font-weight: bold; color: {border_color}; '
                         f'text-align: center; position: absolute; width: 100px; '
                         f'margin-left: -50px; padding-top: {padding_top};">{city}</div>',
                    icon_size=(0, 0),
                    icon_anchor=icon_anchor,
                    class_name="transparent"
                )
            ).add_to(m)

def add_city_boundaries(m):
    """Add city boundaries using local JSON files."""
    import json
    from pathlib import Path
    
    for city, config in CITY_BOUNDARIES.items():
        try:
            json_file = Path('data/city_boundaries') / f"{city}.json"
            
            if not json_file.exists():
                print(f"Warning: Missing JSON file for {city}: {json_file}")
                continue
            
            # Citim datele JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                boundary_data = json.load(f)
            
            # Procesăm coordonatele
            all_coords = []
            if boundary_data['type'] == 'Feature':
                if boundary_data['geometry']['type'] == 'Polygon':
                    # Convertim coordonatele din [lon, lat] în [lat, lon]
                    all_coords = [[coord[1], coord[0]] for coord in boundary_data['geometry']['coordinates'][0]]
            
            if all_coords:
                # Verificăm dacă primul și ultimul punct sunt identice
                if all_coords[0] != all_coords[-1]:
                    all_coords.append(all_coords[0])
                
                # Add boundary as GeoJson with specific class
                boundary = folium.GeoJson(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[[coord[1], coord[0]] for coord in all_coords]]
                        }
                    },
                    style_function=lambda x: {
                        'fillColor': config['fill_color'],
                        'color': config['border_color'],
                        'weight': 2,
                        'fillOpacity': 1,
                        'opacity': 1
                    },
                    name="_",  # Important: use the same name as the outline layer
                    class_name='city-boundary'
                )
                boundary.add_to(m)
                
        except Exception as e:
            print(f"Error adding {city} boundary: {str(e)}")

def create_section_popup(highway_code, section_name, section_data):
    """Creează popup-ul pentru un tronson de autostradă."""
    status_colors = {
        "finished": "green",
        "in_construction": "orange",
        "planned": "grey",
        "tendered": "brown"
    }
    
    status_text = {
        "finished": "Finalizat",
        "in_construction": "În construcție",
        "planned": "Planificat",
        "tendered": "Lansat spre licitație"
    }
    
    # Partea comună a popup-ului
    popup_content = f"""
    <div style='font-family: Arial; font-size: 12px; padding: 5px;'>
        <b>Autostrada {highway_code}</b><br>
        <b>Tronson: {section_name}</b>
        <hr style='margin: 5px 0;'>
        Status: <span style='color: {status_colors[section_data["status"]]};'>
            {status_text[section_data["status"]]}</span><br>
        Lungime: {section_data["length"]}"""

    # Adăugăm informații specifice în funcție de status
    if section_data["status"] == "finished":
        popup_content += f"""<br>Data finalizării: {section_data.get("completion_date", "N/A")}"""
    
    elif section_data["status"] == "in_construction":
        popup_content += f"""
        <br>Finalizare: {section_data.get("completion_date", "N/A")}
        <br>Progres: {section_data.get("progress", "N/A")}"""
    
    elif section_data["status"] == "tendered":
        popup_content += f"""
        <br>Finalizare licitație: {section_data.get("tender_end_date", "N/A")}
        <br>Codul SEAP: {section_data.get("seap_code", "N/A")}
        <br>Stadiul curent: {section_data.get("current_stage", "N/A")}
        <br>Durata construcției: {section_data.get("construction_duration", "N/A")}"""
    
    elif section_data["status"] == "planned":
        popup_content += f"""
        <br>Finalizare studiu de fezabilitate: {section_data.get("feasibility_study_date", "N/A")}
        <br>Data aproximativă a finalizării: {section_data.get("projected_completion_date", "N/A")}"""

    # Adăugăm constructor dacă există
    if "constructor" in section_data:
        popup_content += f"<br>Constructor: {section_data['constructor']}"
    if "designer" in section_data:
        popup_content += f"<br>Proiectant: {section_data['designer']}"

    # Adăugăm cost sau cost estimat
    if section_data["status"] in ["finished", "in_construction"]:
        if "cost" in section_data:
            popup_content += f"<br>Cost: {section_data['cost']} €"
    else:
        if "estimated_cost" in section_data:
            popup_content += f"<br>Cost estimat: {section_data['estimated_cost']} €"

    # Adăugăm sursa finanțării dacă există
    if "financing" in section_data:
        popup_content += f"<br>Finanțare: {section_data['financing']}"
    
    if "current_stage" in section_data:
        popup_content += f"<br>Stadiul curent: {section_data['current_stage']}"

    popup_content += "</div>"
    
    return popup_content

def add_section_delimiter(m, coordinates, way_coords):
    """Adaugă un marcaj de delimitare perpendicular pe autostradă."""
    if not way_coords or len(way_coords) < 2:
        return
        
    lat, lon = coordinates
    
    # Găsim cel mai apropiat segment de drum
    min_dist = float('inf')
    best_idx = 0
    
    for i in range(len(way_coords)-1):
        p1 = way_coords[i]
        p2 = way_coords[i+1]
        
        if p1 == p2:
            continue
            
        dx = p2[1] - p1[1]
        dy = p2[0] - p1[0]
        
        if dx == 0 and dy == 0:
            continue
            
        try:
            d = abs((dx)*(p1[0]-lat) - (p1[1]-lon)*(dy)) / math.sqrt(dx*dx + dy*dy)
            if d < min_dist:
                min_dist = d
                best_idx = i
        except ZeroDivisionError:
            continue
    
    if best_idx >= len(way_coords)-1:
        return
        
    p1 = way_coords[best_idx]
    p2 = way_coords[best_idx + 1]
    
    dx = p2[1] - p1[1]
    dy = p2[0] - p1[0]
    
    if dx == 0 and dy == 0:
        return
    
    angle = math.atan2(dy, dx)
    perpendicular_angle = angle + math.pi/2
    
    road_width = 0.0008  # lățime fixă pentru vizibilitate mai bună
    delimiter_length = road_width * 1.2
    delimiter_weight = 5  # subțiem linia pentru claritate mai bună
    
    x1 = lon + delimiter_length * math.cos(perpendicular_angle)
    y1 = lat + delimiter_length * math.sin(perpendicular_angle)
    x2 = lon - delimiter_length * math.cos(perpendicular_angle)
    y2 = lat - delimiter_length * math.sin(perpendicular_angle)
    
    # Adăugăm linia delimitatorului
    folium.PolyLine(
        locations=[[y1, x1], [y2, x2]],
        weight=delimiter_weight,
        color='black',
        dash_array=None,  # eliminăm dash_array pentru o linie solidă
        opacity=1
    ).add_to(m)

def process_xml_ways(way_ids, ways_data):
    """Helper function to process and combine XML ways properly"""
    if not way_ids or not ways_data:
        return []

    # Convert IDs to int for consistency
    way_ids = [int(wid) for wid in way_ids if int(wid) in ways_data]
    
    # Create a graph of connected ways
    connections = {}
    for wid in way_ids:
        coords = ways_data[wid]
        if len(coords) < 2:
            continue
        start = tuple(coords[0])
        end = tuple(coords[-1])
        connections[wid] = {'coords': coords, 'start': start, 'end': end}

    # Find connected segments and merge them
    merged_paths = []
    used_ways = set()
    
    def find_connected_ways(current_way, current_path):
        used_ways.add(current_way)
        current_end = connections[current_way]['end']
        
        # Look for ways that connect to our end point
        for wid, data in connections.items():
            if wid not in used_ways:
                if data['start'] == current_end:
                    return wid
                elif data['end'] == current_end:
                    # Reverse the coordinates if needed
                    connections[wid]['coords'].reverse()
                    connections[wid]['start'], connections[wid]['end'] = connections[wid]['end'], connections[wid]['start']
                    return wid
        return None

    # Process each unused way as a potential start of a path
    for start_way in way_ids:
        if start_way in used_ways:
            continue
            
        current_path = connections[start_way]['coords'][:]
        current_way = start_way
        
        while True:
            next_way = find_connected_ways(current_way, current_path)
            if not next_way:
                break
                
            # Add coordinates without duplicating the connecting point
            next_coords = connections[next_way]['coords']
            if current_path[-1] == next_coords[0]:
                current_path.extend(next_coords[1:])
            else:
                current_path.extend(next_coords)
                
            current_way = next_way
            
        if current_path:  # Adăugăm path-ul doar dacă nu e gol
            merged_paths.append(current_path)

    return merged_paths  # Returnăm toate path-urile

def calculate_logo_position(coordinates, logo_position, offset=0.1):
    """
    Calculează poziția logo-ului în funcție de coordonatele secțiunii și poziția dorită
    """
    if not coordinates:
        return None
        
    # Calculăm centrul secțiunii
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Ajustăm poziția în funcție de preferință
    if logo_position == "right":
        return [center_lat, center_lon + offset]
    elif logo_position == "left":
        return [center_lat, center_lon - offset]
    elif logo_position == "top":
        return [center_lat + offset, center_lon]
    elif logo_position == "bottom":
        return [center_lat - offset, center_lon]
    else:
        return [center_lat, center_lon]

def add_section_logo(m, coordinates, logo_data, logo_group, highway_code):
    """Adaugă logo-ul pentru o secțiune specifică"""
    if not logo_data or not coordinates:
        return
        
    logo_position = logo_data.get("position", "right")
    logo_path = logo_data.get("path")
    
    if not logo_path:
        return
        
    # Calculăm poziția logo-ului
    logo_coords = calculate_logo_position(coordinates, logo_position)
    
    if not logo_coords:
        return
        
    # Adăugăm logo-ul cu dimensiuni mai mici
    icon_html = f"""
        <div class="highway-logo highway-{highway_code.lower()}" 
             data-highway="{highway_code}"
             style="
                background-image: url('{logo_path}');
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                width: 25px;
                height: 25px;
                border-radius: 50%;
                background-color: white;
                border: 2px solid #666;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
        "
        onclick="highlightHighway('{highway_code}')">
        </div>
    """
    
    folium.Marker(
        logo_coords,
        icon=folium.DivIcon(
            html=icon_html,
            icon_size=(25, 25),
            icon_anchor=(12.5, 12.5),
            class_name=f'highway-logo-marker {highway_code.lower()}'
        )
    ).add_to(logo_group)

def add_all_highways_to_map(m):
    """Optimized version with correct section rendering and hover effects"""
    from highway_data import HIGHWAYS
    
    # Create feature groups for each status
    status_groups = {
        "finished": folium.FeatureGroup(name="Finished"),
        "in_construction": folium.FeatureGroup(name="In Construction"),
        "tendered": folium.FeatureGroup(name="Tendered"),
        "planned": folium.FeatureGroup(name="Planned")
    }
    
    # Create corresponding delimiter groups for each status
    delimiter_groups = {
        "finished": folium.FeatureGroup(name="_delimiters_finished", show=False),
        "in_construction": folium.FeatureGroup(name="_delimiters_in_construction", show=False),
        "tendered": folium.FeatureGroup(name="_delimiters_tendered", show=False),
        "planned": folium.FeatureGroup(name="_delimiters_planned", show=False)
    }
    
    # Create a feature group for logos
    logo_group = folium.FeatureGroup(name="_logos", show=True)
    logo_group.add_to(m)
    
    for group in status_groups.values():
        group.add_to(m)
    for group in delimiter_groups.values():
        group.add_to(m)
    
    status_colors = {
        "finished": "green",
        "in_construction": "orange",
        "planned": "grey",
        "tendered": "brown"
    }
    
    def style_function(feature):
        """Style function that uses the status from feature properties"""
        status = feature['properties']['status']
        return {
            'color': status_colors.get(status, "grey"),
            'weight': 4,
            'opacity': 1
        }

    def highlight_function(feature):
        """Highlight function that uses the status from feature properties"""
        status = feature['properties']['status']
        return {
            'color': status_colors.get(status, "grey"),
            'weight': 6,
            'opacity': 0.8
        }
    
    for highway_code, highway_data in HIGHWAYS.items():
        for section_name, section_data in highway_data["sections"].items():
            try:
                status = section_data["status"]
                if status not in status_groups:
                    continue
                
                if 'geojson_file' in section_data:
                    with open(f"data/highways/{section_data['geojson_file']}", 'r') as f:
                        geojson_data = json.load(f)
                    
                    coordinates = []
                    if 'features' in geojson_data:
                        for feature in geojson_data['features']:
                            if feature['geometry']['type'] == 'LineString':
                                coordinates.extend(feature['geometry']['coordinates'])
                    elif 'geometry' in geojson_data:
                        if geojson_data['geometry']['type'] == 'LineString':
                            coordinates.extend(geojson_data['geometry']['coordinates'])
                        elif geojson_data['geometry']['type'] == 'MultiLineString':
                            for line in geojson_data['geometry']['coordinates']:
                                coordinates.extend(line)
                    
                    if coordinates:
                        feature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": coordinates
                            },
                            "properties": {
                                "name": section_name,
                                "highway": highway_code,
                                "status": status,
                                "completion_date": section_data.get("completion_date", "N/A"),
                                "length": section_data.get("length", "N/A"),
                                "constructor": section_data.get("constructor", "N/A"),
                                "cost": section_data.get("cost", "N/A")
                            }
                        }
                        
                        folium.GeoJson(
                            feature,
                            style_function=style_function,
                            highlight_function=highlight_function,
                            popup=folium.Popup(
                                html=create_section_popup(highway_code, section_name, section_data),
                                max_width=250
                            ),
                            tooltip=f"{highway_code} - {section_name}",
                            name=section_name,
                            overlay=True,
                            class_name=f'highway-section-{highway_code.lower()}'
                        ).add_to(status_groups[status])
                        
                        if 'end_point' in section_data:
                            formatted_coords = [[coord[1], coord[0]] for coord in coordinates]
                            add_section_delimiter(delimiter_groups[status], section_data['end_point'], formatted_coords)
                            
                        if "logo" in section_data:
                            add_section_logo(m, [[coord[1], coord[0]] for coord in coordinates], 
                                           section_data["logo"], logo_group, highway_code)
                
                elif 'xml_file' in section_data:
                    tree = ET.parse(f"data/highways/{section_data['xml_file']}")
                    root = tree.getroot()
                    way_ids = [member.get('ref') for member in root.findall(".//member[@type='way']")]
                    ways_data = get_all_way_coordinates(way_ids)
                    
                    if ways_data:
                        paths = process_xml_ways(way_ids, ways_data)
                        
                        for path in paths:
                            if path:
                                feature = {
                                    "type": "Feature",
                                    "geometry": {
                                        "type": "LineString",
                                        "coordinates": [[coord[1], coord[0]] for coord in path]
                                    },
                                    "properties": {
                                        "name": section_name,
                                        "highway": highway_code,
                                        "status": status,
                                        "completion_date": section_data.get("completion_date", "N/A"),
                                        "length": section_data.get("length", "N/A"),
                                        "constructor": section_data.get("constructor", "N/A"),
                                        "cost": section_data.get("cost", "N/A")
                                    }
                                }
                                
                                folium.GeoJson(
                                    feature,
                                    style_function=style_function,
                                    highlight_function=highlight_function,
                                    popup=folium.Popup(
                                        html=create_section_popup(highway_code, section_name, section_data),
                                        max_width=250
                                    ),
                                    tooltip=f"{highway_code} - {section_name}",
                                    name=section_name,
                                    overlay=True,
                                    class_name=f'highway-section-{highway_code.lower()}'
                                ).add_to(status_groups[status])
                        
                        if paths and 'end_point' in section_data:
                            add_section_delimiter(delimiter_groups[status], section_data['end_point'], paths[-1])
                            
                        if paths and "logo" in section_data:
                            add_section_logo(m, paths[-1], section_data["logo"], logo_group, highway_code)
                            
            except Exception as e:
                print(f"Error processing {highway_code} - {section_name}: {str(e)}")
                continue

    folium.LayerControl(collapsed=False).add_to(m)

    # Add JavaScript to sync delimiter visibility with section visibility
    m.get_root().html.add_child(folium.Element("""
        <style>
            .leaflet-interactive {
                stroke-linecap: round;
                stroke-linejoin: round;
            }
            
            .highway-logo {
                transition: all 0.3s ease;
            }

            .highway-logo:hover {
                transform: scale(1.2);
                box-shadow: 0 3px 7px rgba(0,0,0,0.3);
            }

            .highway-logo-marker {
                z-index: 1000 !important;
            }
            
            .leaflet-pane .leaflet-overlay-pane div[class*="highway-logo"] {
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
            }
            
            .highlighted-path {
                animation: pulse 1.5s infinite;
                stroke-width: 6px !important;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.6; }
                100% { opacity: 1; }
            }
        </style>
        <script>
        let activeHighway = null;
        
        function highlightHighway(highwayCode) {
            console.log('Highlighting highway:', highwayCode);  // Pentru debugging
            
            // Resetăm highlight-ul anterior
            document.querySelectorAll('.highlighted-path').forEach(path => {
                path.classList.remove('highlighted-path');
            });
            
            // Dacă apăsăm pe același logo, doar eliminăm highlight-ul
            if (activeHighway === highwayCode) {
                activeHighway = null;
                return;
            }
            
            // Setăm noul highway activ și adăugăm highlight
            activeHighway = highwayCode;
            
            // Selectăm toate path-urile pentru această autostradă
            document.querySelectorAll('.leaflet-pane path').forEach(path => {
                const parentElement = path.closest('.leaflet-interactive');
                if (parentElement && parentElement.classList.contains(`highway-section-${highwayCode.toLowerCase()}`)) {
                    path.classList.add('highlighted-path');
                }
            });
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            // Function to sync delimiter visibility with section visibility
            function syncDelimiterVisibility() {
                const layerControls = document.querySelectorAll('.leaflet-control-layers-overlays input[type="checkbox"]');
                layerControls.forEach(control => {
                    const labelText = control.nextElementSibling.textContent.trim();
                    if (labelText === '_logos') {
                        control.checked = true;
                        if (control.onchange) control.onchange();
                        control.parentElement.style.display = 'none';
                    }
                    const delimiterControl = Array.from(layerControls).find(c => 
                        c.nextElementSibling.textContent.trim() === `_delimiters_${labelText.toLowerCase().replace(' ', '_')}`
                    );
                    if (delimiterControl) {
                        delimiterControl.checked = control.checked;
                        if (delimiterControl.onchange) delimiterControl.onchange();
                    }
                });
            }

            const sectionControls = document.querySelectorAll('.leaflet-control-layers-overlays input[type="checkbox"]');
            sectionControls.forEach(control => {
                control.addEventListener('change', syncDelimiterVisibility);
            });

            syncDelimiterVisibility();
            
            const logoControl = Array.from(sectionControls).find(c => 
                c.nextElementSibling.textContent.trim() === '_logos'
            );
            if (logoControl) {
                logoControl.parentElement.style.display = 'none';
            }
        });
        </script>
    """))

    print("Finished adding highways to map")

def add_romania_outline_to_map(feature_group, romania_outline):
    """Adaugă conturul României pe hartă."""
    
    folium.GeoJson(
        romania_outline,
        style_function=lambda x: {
            'fillColor': 'white',
            'color': 'gray',
            'weight': 1.5,
            'fillOpacity': 1,
            'opacity': 1
        }
    ).add_to(feature_group)

def add_base_layer(m):
    """Adaugă stratul de bază alb pe hartă."""
    
    folium.TileLayer(
        tiles='',
        attr='Map data',
        bgcolor='white',
        overlay=True,
        control=False,
    ).add_to(m)

def calculate_highway_totals(highways_data):
    """Calculate totals for each status."""
    totals = {
        "finished": 0,
        "in_construction": 0,
        "planned": 0,
        "tendered": 0,
        "total": 0
    }
    
    for highway in highways_data.values():
        for section in highway['sections'].values():
            if 'length' in section:
                try:
                    length = float(section['length'].replace(' km', ''))
                    status = section['status']
                    totals[status] += length
                    totals['total'] += length
                except (ValueError, KeyError):
                    continue
    
    return totals