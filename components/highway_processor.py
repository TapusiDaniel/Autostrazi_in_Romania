"""Highway data processing utilities for XML and GeoJSON parsing."""

import math
from typing import List, Dict, Tuple, Optional, Any
import folium


def process_xml_ways(way_ids: List[str], ways_data: Dict[int, List[List[float]]]) -> List[List[List[float]]]:
    """Process and combine XML ways into continuous paths.
    
    Args:
        way_ids: List of OSM way IDs as strings
        ways_data: Dictionary mapping way IDs to their coordinate lists
    
    Returns:
        List of merged coordinate paths
    """
    if not way_ids or not ways_data:
        return []

    # Convert IDs to int for consistency
    way_ids = [int(wid) for wid in way_ids if int(wid) in ways_data]
    
    # Create a graph of connected ways
    connections: Dict[int, Dict[str, Any]] = {}
    for wid in way_ids:
        coords = ways_data[wid]
        if len(coords) < 2:
            continue
        start = tuple(coords[0])
        end = tuple(coords[-1])
        connections[wid] = {'coords': coords, 'start': start, 'end': end}

    # Find connected segments and merge them
    merged_paths: List[List[List[float]]] = []
    used_ways: set = set()
    
    def find_connected_ways(current_way: int) -> Optional[int]:
        """Find ways that connect to the current way's endpoint."""
        used_ways.add(current_way)
        current_end = connections[current_way]['end']
        
        for wid, data in connections.items():
            if wid not in used_ways:
                if data['start'] == current_end:
                    return wid
                elif data['end'] == current_end:
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
            next_way = find_connected_ways(current_way)
            if not next_way:
                break
                
            next_coords = connections[next_way]['coords']
            if current_path[-1] == next_coords[0]:
                current_path.extend(next_coords[1:])
            else:
                current_path.extend(next_coords)
                
            current_way = next_way
            
        if current_path:
            merged_paths.append(current_path)

    return merged_paths


def add_section_delimiter(m: folium.Map, coordinates: Tuple[float, float], way_coords: List[List[float]]) -> None:
    """Adds a perpendicular delimiter marker on the highway at specified coordinates.
    
    Args:
        m: Folium map object
        coordinates: Tuple of (lat, lon) for delimiter placement
        way_coords: List of coordinate pairs for the highway path
    """
    if not way_coords or len(way_coords) < 2:
        return
        
    lat, lon = coordinates
    
    # Find the closest road segment
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
    
    # Calculate perpendicular line
    angle = math.atan2(dy, dx)
    perpendicular_angle = angle + math.pi/2
    
    road_width = 0.0008
    delimiter_length = road_width * 1.2
    delimiter_weight = 5
    
    # Calculate delimiter endpoints
    x1 = lon + delimiter_length * math.cos(perpendicular_angle)
    y1 = lat + delimiter_length * math.sin(perpendicular_angle)
    x2 = lon - delimiter_length * math.cos(perpendicular_angle)
    y2 = lat - delimiter_length * math.sin(perpendicular_angle)
    
    folium.PolyLine(
        locations=[[y1, x1], [y2, x2]],
        weight=delimiter_weight,
        color='black',
        dash_array=None,
        opacity=1
    ).add_to(m)


def calculate_logo_position(coordinates: List[List[float]], logo_position: str, offset: float = 0.1) -> Optional[List[float]]:
    """Calculate logo position based on section coordinates and desired position.
    
    Args:
        coordinates: List of coordinate pairs for the highway section
        logo_position: Position relative to section ("right", "left", "top", "bottom")
        offset: Distance offset from center
    
    Returns:
        [lat, lon] coordinates for logo placement, or None if coordinates are empty
    """
    if not coordinates:
        return None
        
    lats = [coord[0] for coord in coordinates]
    lons = [coord[1] for coord in coordinates]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
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


def add_section_logo(m: folium.Map, coordinates: List[List[float]], logo_data: Dict[str, str], 
                     logo_group: folium.FeatureGroup, highway_code: str) -> None:
    """Add a logo marker for a specific highway section.
    
    Args:
        m: Folium map object
        coordinates: List of coordinate pairs for the highway section
        logo_data: Dictionary with "position" and "path" keys
        logo_group: Feature group to add the logo marker to
        highway_code: Highway identifier for CSS classes
    """
    if not logo_data or not coordinates:
        return
        
    logo_position = logo_data.get("position", "right")
    logo_path = logo_data.get("path")
    
    if not logo_path:
        return
        
    logo_coords = calculate_logo_position(coordinates, logo_position)
    
    if not logo_coords:
        return
        
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


def calculate_highway_totals(highways_data: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """Calculate total lengths for each highway status and overall total.
    
    Args:
        highways_data: Dictionary of highways with their sections
    
    Returns:
        Dictionary with totals for each status and overall total
    """
    totals: Dict[str, float] = {
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
