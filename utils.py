import httpx
import xml.etree.ElementTree as ET
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union
import time
import json

# Create httpx client with connection pooling
CLIENT = httpx.Client(
    timeout=60.0,
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    http2=True,  # Enable HTTP/2
    verify=True,  # Keep SSL verification
    headers={
        'User-Agent': 'Highway-Fetcher/1.0',
        'Accept-Encoding': 'gzip, deflate',
    }
)

def get_relation_ways_fast(relation_id, timeout=60):
    """
    Fetch all ways from a relation using httpx (faster than requests).
    """
    query = f"""
    [out:json][timeout:{timeout}];
    relation({relation_id});
    (._;>;);
    out body;
    """
    
    endpoints = [
        "https://overpass.private.coffee/api/interpreter",  # This was fastest in curl
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n      Trying {endpoint.split('/')[2]}...", end=" ", flush=True)
            
            t0 = time.time()
            
            response = CLIENT.post(
                endpoint,
                data={"data": query},
                timeout=timeout
            )
            
            t1 = time.time()
            print(f"got {len(response.content)/1024:.0f}KB in {t1-t0:.1f}s...", end=" ", flush=True)
            
            response.raise_for_status()
            
            # Parse JSON
            t2 = time.time()
            data = response.json()
            t3 = time.time()
            print(f"parsed in {t3-t2:.1f}s...", end=" ", flush=True)
            
            # Parse nodes and ways
            nodes = {}
            ways = {}
            
            for element in data['elements']:
                if element['type'] == 'node':
                    nodes[element['id']] = [element['lat'], element['lon']]
                elif element['type'] == 'way' and 'nodes' in element:
                    way_id = element['id']
                    coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
                    if coords:
                        ways[way_id] = coords
            
            t4 = time.time()
            print(f"processed {len(ways)} ways in {t4-t3:.1f}s", end=" ", flush=True)
            
            total_time = t4 - t0
            print(f"\n      ✓ Total: {total_time:.1f}s", end=" ", flush=True)
            
            return ways
            
        except httpx.TimeoutException:
            print(f"[TIMEOUT]", flush=True)
            continue
        except httpx.HTTPStatusError as e:
            print(f"[HTTP {e.response.status_code}]", flush=True)
            continue
        except Exception as e:
            print(f"[ERROR: {str(e)[:50]}]", flush=True)
            continue
    
    print("\n      ✗ All endpoints failed!")
    return {}

def get_all_way_coordinates(way_ids, timeout=60):
    """
    Fetch coordinates for individual ways (slower).
    """
    if not way_ids:
        return {}
    
    ways_str = ','.join(str(w) for w in way_ids)
    
    query = f"""
    [out:json][timeout:{timeout}];
    way(id:{ways_str});
    (._;>;);
    out body;
    """
    
    endpoints = [
        "https://overpass.private.coffee/api/interpreter",
        "https://overpass-api.de/api/interpreter",
    ]
    
    for endpoint in endpoints:
        try:
            t0 = time.time()
            
            response = CLIENT.post(
                endpoint,
                data={"data": query},
                timeout=timeout
            )
            
            t1 = time.time()
            print(f"fetched in {t1-t0:.1f}s...", end=" ", flush=True)
            
            response.raise_for_status()
            data = response.json()
            
            # Parse nodes and ways
            nodes = {}
            ways = {}
            
            for element in data['elements']:
                if element['type'] == 'node':
                    nodes[element['id']] = [element['lat'], element['lon']]
                elif element['type'] == 'way' and 'nodes' in element:
                    way_id = element['id']
                    coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
                    if coords:
                        ways[way_id] = coords
            
            return ways
            
        except Exception as e:
            print(f"[ERROR: {str(e)[:50]}]", flush=True)
            continue
    
    return {}

def get_romania_outline(geojson_data):
    """
    Generate a unified outline of Romania from GeoJSON data containing county polygons.
    """
    polygons = []
    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if isinstance(geom, MultiPolygon):
            polygons.extend(list(geom.geoms))
        else:
            polygons.append(geom)
    
    union = unary_union(polygons)
    
    if isinstance(union, MultiPolygon):
        exterior_coords = [list(union.geoms[0].exterior.coords)]
    else:
        exterior_coords = [list(union.exterior.coords)]
    
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": exterior_coords
        }
    }