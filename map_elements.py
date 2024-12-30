import folium
from config import CITIES
from utils import get_all_way_coordinates, simplify_geojson
from config import CITY_BOUNDARIES
from map_hover import add_hover_effect
import xml.etree.ElementTree as ET
import math
import json
import requests
import xml.etree.ElementTree as ET
from folium.features import GeoJson, GeoJsonTooltip
import tempfile
import os
import json
from folium import GeoJson, GeoJsonTooltip

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

def sort_boundary_ways(way_refs, nodes_data):
    """Sort way segments to form a continuous boundary."""
    if not way_refs:
        return []
    
    # Create a dictionary of ways with their start and end nodes
    ways = {}
    for way_ref in way_refs:
        if way_ref in nodes_data:
            coords = nodes_data[way_ref]
            if coords:
                ways[way_ref] = {
                    'start': coords[0],
                    'end': coords[-1],
                    'coords': coords
                }
    
    # Find the correct order of ways
    ordered_ways = []
    current_way = way_refs[0]  # Start with the first way
    used_ways = set()
    
    while len(ordered_ways) < len(way_refs) and current_way in ways:
        if current_way in used_ways:
            break
            
        ordered_ways.append(current_way)
        used_ways.add(current_way)
        current_end = ways[current_way]['end']
        
        # Find the next way that starts where this one ends
        next_way = None
        for way_ref, way_data in ways.items():
            if way_ref not in used_ways and way_data['start'] == current_end:
                next_way = way_ref
                break
        
        if not next_way:
            # If no way starts at our end, try finding one whose end connects to our end
            for way_ref, way_data in ways.items():
                if way_ref not in used_ways and way_data['end'] == current_end:
                    next_way = way_ref
                    # Reverse the coordinates of this way
                    ways[way_ref]['coords'].reverse()
                    ways[way_ref]['start'], ways[way_ref]['end'] = ways[way_ref]['end'], ways[way_ref]['start']
                    break
                    
        current_way = next_way
    
    # Get the ordered coordinates
    ordered_coords = []
    for way_ref in ordered_ways:
        if way_ref in ways:
            ordered_coords.extend(ways[way_ref]['coords'])
    
    return ordered_coords

def fill_city_boundary(m, coordinates, fill_color):
    """Fill a city boundary with the specified color."""
    if coordinates and coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])

    folium.Polygon(
        locations=coordinates,
        fill=True,
        color=fill_color,
        fillColor=fill_color,
        fillOpacity=1,
        weight=0
    ).add_to(m)

def add_city_boundaries(m):
    """Add boundaries for all configured cities."""
    for city, config in CITY_BOUNDARIES.items():
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            query = f"""
            [out:xml][timeout:25];
            relation({config['relation_id']});
            way(r:"outer");
            (._;>;);
            out body;
            """
            
            response = requests.get(overpass_url, params={'data': query})
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                nodes = {}
                for node in root.findall('.//node'):
                    node_id = node.get('id')
                    lat = float(node.get('lat'))
                    lon = float(node.get('lon'))
                    nodes[node_id] = [lat, lon]
                
                way_coords = {}
                way_refs = []
                for way in root.findall('.//way'):
                    way_id = way.get('id')
                    coords = []
                    for nd in way.findall('nd'):
                        node_ref = nd.get('ref')
                        if node_ref in nodes:
                            coords.append(nodes[node_ref])
                    if coords:
                        way_coords[way_id] = coords
                        way_refs.append(way_id)
                
                all_coords = sort_boundary_ways(way_refs, way_coords)
                
                if all_coords:
                    if all_coords[0] != all_coords[-1]:
                        all_coords.append(all_coords[0])
                    
                    # Add boundary as GeoJson with specific class
                    folium.GeoJson(
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
                        class_name='city-boundary'
                    ).add_to(m)
                    
        except Exception as e:
            print(f"Error adding {city} boundary: {str(e)}")

def create_lot_polygon(m, coordinates, lot_info, style=None):
    """Creează un polygon pentru un lot cu hover effect."""
    if style is None:
        style = {
            'fillColor': '#3388ff',
            'color': '#3388ff',
            'weight': 2,
            'fillOpacity': 0.2
        }
    
    polygon = folium.Polygon(
        locations=coordinates,
        popup=folium.Popup(lot_info, max_width=300),
        **style
    )
    
    polygon.add_to(m)
    return polygon

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
    
    # Construim conținutul de bază al popup-ului
    popup_content = f"""
    <div style='font-family: Arial; font-size: 12px; padding: 5px;'>
        <b>Autostrada {highway_code}</b><br>
        <b>Tronson: {section_name}</b>
        <hr style='margin: 5px 0;'>
        Status: <span style='color: {status_colors[section_data["status"]]};'>
            {status_text[section_data["status"]]}</span><br>
        Data finalizării: {section_data["completion_date"]}<br>
        Lungime: {section_data["length"]}"""

    # Adăugăm constructor doar dacă există
    if "constructor" in section_data:
        popup_content += f"<br>Constructor: {section_data['constructor']}"

    # Adăugăm cost doar dacă există
    if "cost" in section_data:
        popup_content += f"<br>Cost: {section_data['cost']} €"

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

def add_geojson_section_to_map(m, highway_code, section_name, section_data, default_color):
    """Adaugă un tronson de autostradă din GeoJSON pe hartă."""
    try:
        with open(f"data/highways/{section_data['geojson_file']}", 'r') as f:
            geojson_data = json.load(f)
        
        # Extrage coordonatele din GeoJSON
        coordinates = geojson_data['geometry']['coordinates']
        
        status_colors = {
            "finished": "green",
            "in_construction": "orange",
            "planned": "grey",
            "tendered": "brown"
        }

        line_color = status_colors.get(section_data["status"], default_color)
        
        # Convertim coordonatele în formatul [lat, lon]
        formatted_coords = [[coord[1], coord[0]] for coord in coordinates]
        
        folium.PolyLine(
            formatted_coords,
            weight=4,
            color=line_color,
            opacity=1,
            popup=folium.Popup(
                html=create_section_popup(highway_code, section_name, section_data),
                max_width=250
            )
        ).add_to(m)
        
        # Adaugă delimitator la sfârșitul secțiunii dacă există coordonate
        if 'end_point' in section_data and formatted_coords:
            add_section_delimiter(m, section_data['end_point'], formatted_coords)
            
    except Exception as e:
        print(f"Eroare la procesarea tronsonului {section_name}: {str(e)}")

def add_xml_section_to_map(m, highway_code, section_name, section_data, default_color):
    """Adaugă un tronson de autostradă din XML pe hartă."""
    try:
        tree = ET.parse(f"data/highways/{section_data['xml_file']}")
        root = tree.getroot()
        way_ids = [member.get('ref') for member in root.findall(".//member[@type='way']")]
        ways_data = get_all_way_coordinates(way_ids)
        
        status_colors = {
            "finished": "green",
            "in_construction": "orange",
            "planned": "grey",
            "tendered": "brown"
        }

        line_color = status_colors.get(section_data["status"], default_color)
        
        style_function = lambda x: {
            'color': line_color,
            'weight': 4,
            'opacity': 1
        }
        
        highlight_function = lambda x: {
            'color': line_color,
            'weight': 6,
            'opacity': 1
        }

        for way_id in way_ids:
            if int(way_id) in ways_data:
                geojson_data = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[coord[1], coord[0]] for coord in ways_data[int(way_id)]]
                    },
                    "properties": {
                        'name': section_name,
                        'highway': highway_code,
                        'status': section_data["status"],
                        'completion_date': section_data.get("completion_date", "N/A"),
                        'length': section_data.get("length", "N/A")
                    }
                }
                
                gjson = GeoJson(
                    geojson_data,
                    style_function=style_function,
                    highlight_function=highlight_function,
                    tooltip=GeoJsonTooltip(
                        fields=['name', 'highway', 'status', 'completion_date', 'length'],
                        aliases=['Tronson:', 'Autostrada:', 'Status:', 'Data finalizării:', 'Lungime:'],
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                )
                gjson.add_to(m)
        
        # Adaugă delimitator la sfârșitul secțiunii dacă există coordonate
        all_coords = []
        for way_id in way_ids:
            if int(way_id) in ways_data:
                all_coords.extend(ways_data[int(way_id)])
                
        if 'end_point' in section_data and all_coords:
            add_section_delimiter(m, section_data['end_point'], all_coords)
            
    except Exception as e:
        print(f"Eroare la procesarea tronsonului {section_name}: {str(e)}")

def add_highway_section_to_map(m, highway_code, section_name, section_data, default_color):
    """Adaugă un tronson de autostradă pe hartă."""
    try:
        # Definește base_url la începutul funcției
        base_url = "https://raw.githubusercontent.com/TapusiDaniel/Autostrazi_in_Romania/main"
        
        if 'geojson_file' in section_data:
            print(f"\nProcesez tronsonul {section_name}")
            
            geojson_path = f"{base_url}/data/highways/{section_data['geojson_file']}"
            print(f"Încercăm să citim fișierul: {geojson_path}")
            
            # Folosește requests pentru a prelua datele
            response = requests.get(geojson_path)
            if response.status_code != 200:
                raise ValueError(f"Nu s-a putut accesa fișierul: {geojson_path}")
            geojson_data = response.json()
            
            # Apply more aggressive simplification
            simplified_data = simplify_geojson(geojson_data, tolerance=0.001)
            
            if not 'features' in simplified_data:
                raise ValueError("Nu există features în GeoJSON")
            
            status_colors = {
                "finished": "green",
                "in_construction": "orange",
                "planned": "grey",
                "tendered": "brown"
            }

            line_color = status_colors.get(section_data["status"], default_color)
            
            # Create a single GeoJSON object for all features
            combined_features = {
                'type': 'FeatureCollection',
                'features': []
            }

            for feature in simplified_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    feature['properties'] = {
                        'name': section_name,
                        'highway': highway_code,
                        'status': section_data["status"],
                        'completion_date': section_data.get("completion_date", "N/A"),
                        'length': section_data.get("length", "N/A")
                    }
                    combined_features['features'].append(feature)

            if combined_features['features']:
                gjson = GeoJson(
                    combined_features,
                    style_function=lambda x: {
                        'color': line_color,
                        'weight': 4,
                        'opacity': 1
                    },
                    highlight_function=lambda x: {
                        'color': line_color,
                        'weight': 6,
                        'opacity': 1
                    },
                    tooltip=GeoJsonTooltip(
                        fields=['name', 'highway', 'status', 'completion_date', 'length'],
                        aliases=['Tronson:', 'Autostrada:', 'Status:', 'Data finalizării:', 'Lungime:'],
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    ),
                    embed=False,
                    overlay=True
                )
                gjson.add_to(m)
                print(f"GeoJson adăugat cu succes pentru {section_name}")
            
            if 'end_point' in section_data and combined_features['features']:
                coordinates = [coord for feature in combined_features['features'] 
                             for coord in feature['geometry']['coordinates']]
                formatted_coords = [[coord[1], coord[0]] for coord in coordinates]
                if formatted_coords:
                    add_section_delimiter(m, section_data['end_point'], formatted_coords)
                
        elif 'xml_file' in section_data:
            xml_file_path = section_data['xml_file']
            if not xml_file_path.startswith('A0/'):
                xml_file_path = f"A0/{xml_file_path}"
            xml_url = f"{base_url}/data/highways/{xml_file_path}"
            print(f"Încercăm să citim fișierul XML: {xml_url}")
            
            response = requests.get(xml_url)
            if response.status_code == 200:
                # Creăm directorul temporar dacă nu există
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Salvăm fișierul temporar în directorul temp
                temp_path = os.path.join(temp_dir, f"temp_{os.path.basename(xml_file_path)}")
                with open(temp_path, 'w', encoding='utf-8') as temp_file:
                    temp_file.write(response.text)
                
                try:
                    add_xml_section_to_map(m, highway_code, section_name, {'xml_file': temp_path}, default_color)
                finally:
                    # Ștergem fișierul temporar după ce am terminat
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                raise ValueError(f"Nu s-a putut accesa fișierul XML: {xml_url} (Status code: {response.status_code})")
            
    except Exception as e:
        print(f"Eroare la procesarea tronsonului {section_name}: {str(e)}")
        import traceback
        traceback.print_exc()

def add_highway_to_map(m, highway_code, highway_data):
    """Adaugă o autostradă completă pe hartă."""
    print(f"\nAdaug autostrada {highway_code} pe hartă")
    sections = highway_data["sections"]
    
    # Pentru a păstra coordonatele între secțiuni
    all_coords = []
    added_delimiters = set()  # Set pentru a ține evidența delimiterilor adăugate
    
    for i, (section_name, section_data) in enumerate(sections.items()):
        print(f"\nProcesez secțiunea {section_name} din {highway_code}")
        if 'geojson_file' in section_data:
            print(f"Procesez fișier GeoJSON: {section_data['geojson_file']}")
        elif 'xml_file' in section_data:
            print(f"Procesez fișier XML: {section_data['xml_file']}")
            try:
                tree = ET.parse(f"data/highways/{section_data['xml_file']}")
                root = tree.getroot()
                way_ids = [member.get('ref') for member in root.findall(".//member[@type='way']")]
                ways_data = get_all_way_coordinates(way_ids)
                
                # Adăugăm coordonatele secțiunii curente
                for way_id in way_ids:
                    if int(way_id) in ways_data:
                        all_coords.extend(ways_data[int(way_id)])
            except Exception as e:
                print(f"Eroare la procesarea XML: {str(e)}")
                continue
                
        add_highway_section_to_map(m, 
                                highway_code, 
                                section_name, 
                                section_data, 
                                highway_data["color"])
        
        # Adaugă delimitări între secțiuni consecutive
        if i < len(sections) - 1:
            current_section = section_data
            next_section = list(sections.values())[i + 1]
            
            if ('end_point' in current_section and 
                'start_point' in next_section and 
                current_section['end_point'] != next_section['start_point'] and 
                all_coords):
                    # Creăm o cheie unică pentru acest delimiter
                    delimiter_key = f"{current_section['end_point'][0]},{current_section['end_point'][1]}"
                    if delimiter_key not in added_delimiters:
                        add_section_delimiter(m, current_section['end_point'], all_coords)
                        added_delimiters.add(delimiter_key)

def add_all_highways_to_map(feature_group):
    """Adaugă toate autostrăzile pe hartă."""
    from highway_data import HIGHWAYS
    print("\nÎncep adăugarea autostrăzilor...")
    
    # Process highways in chunks
    chunk_size = 5
    highways_items = list(HIGHWAYS.items())
    
    for i in range(0, len(highways_items), chunk_size):
        chunk = highways_items[i:i + chunk_size]
        for highway_code, highway_data in chunk:
            print(f"\nProcesez autostrada {highway_code}")
            print(f"Secțiuni găsite: {list(highway_data['sections'].keys())}")
            for section_name, section_data in highway_data['sections'].items():
                print(f"\nProcesez secțiunea {section_name}")
                print(f"Date secțiune: {section_data}")
                if 'geojson_file' in section_data:
                    print(f"Găsit fișier GeoJSON: {section_data['geojson_file']}")
            add_highway_to_map(feature_group, highway_code, highway_data)

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