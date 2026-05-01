from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.ops import unary_union
import json
import hashlib
from pathlib import Path

CACHE_DIR = Path("data/cache")


def _cache_key(way_ids):
    """Generate a stable cache filename from way IDs."""
    sorted_ids = sorted(way_ids)
    key = hashlib.md5(','.join(sorted_ids).encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def _load_cache(way_ids):
    """Load cached way coordinates if available."""
    cache_file = _cache_key(way_ids)
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            data = json.load(f)
        # Convert string keys back to int
        return {int(k): v for k, v in data.items()}
    return None


def _save_cache(way_ids, ways):
    """Save way coordinates to local cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_key(way_ids)
    # Convert int keys to string for JSON
    with open(cache_file, 'w') as f:
        json.dump({str(k): v for k, v in ways.items()}, f)


def get_all_way_coordinates(way_ids):
    """
    Load way coordinates from local cache.
    Run 'python resolve_cache.py' to populate the cache from OSM API.
    """
    cached = _load_cache(way_ids)
    if cached is not None:
        print("(cached)", end=" ")
        return cached

    # No cache — tell user to run resolver
    raise RuntimeError(
        f"Cache miss for {len(way_ids)} ways! "
        f"Run 'python resolve_cache.py' to fetch and cache way coordinates."
    )


def get_romania_outline(geojson_data):
    """
    Generate a unified outline of Romania from GeoJSON data containing county polygons.

    Args:
        geojson_data (dict): GeoJSON data containing Romania's county polygons.

    Returns:
        dict: A GeoJSON feature representing the unified outline of Romania.
    """
    # Convert all county polygons into Shapely objects
    polygons = []
    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if isinstance(geom, MultiPolygon):
            # If the geometry is a MultiPolygon, extract individual polygons
            polygons.extend(list(geom.geoms))
        else:
            # Otherwise, add the polygon directly
            polygons.append(geom)
    
    # Merge all polygons into a single geometry
    union = unary_union(polygons)
    
    # Convert the unified geometry back to GeoJSON format
    if isinstance(union, MultiPolygon):
        # If the result is a MultiPolygon, use the first polygon's exterior coordinates
        exterior_coords = [list(union.geoms[0].exterior.coords)]
    else:
        # Otherwise, use the exterior coordinates of the single polygon
        exterior_coords = [list(union.exterior.coords)]
    
    # Return the unified outline as a GeoJSON feature
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": exterior_coords
        }
    }