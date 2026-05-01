#!/usr/bin/env python3
"""
Resolve way coordinates from OpenStreetMap and save to local cache.

Run this script when XML files are added or updated.
The main build (main.py) reads only from cache — zero API calls at build time.

Usage:
    python resolve_cache.py              # Resolve only uncached files
    python resolve_cache.py --force      # Re-resolve everything
    python resolve_cache.py --file PATH  # Resolve a single XML file
"""
import xml.etree.ElementTree as ET
import requests
import json
import hashlib
import time
import sys
from pathlib import Path

CACHE_DIR = Path("data/cache")
HIGHWAYS_DIR = Path("data/highways")

# OSM main API — different from Overpass, much more reliable
OSM_API_BASE = "https://api.openstreetmap.org/api/0.6"

HEADERS = {
    'User-Agent': 'AutostraziRomania/1.0 (educational highway map project)',
    'Accept': 'application/json',
}

# Rate limiting for OSM API (be polite)
REQUEST_DELAY = 0.5  # seconds between requests


def _cache_key(way_ids):
    """Generate cache filename — same algorithm as utils/geo.py."""
    sorted_ids = sorted(way_ids)
    key = hashlib.md5(','.join(sorted_ids).encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"


def _cache_exists(way_ids):
    return _cache_key(way_ids).exists()


def _save_cache(way_ids, ways_data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_key(way_ids)
    with open(cache_file, 'w') as f:
        json.dump({str(k): v for k, v in ways_data.items()}, f)
    return cache_file


def extract_way_ids(xml_path):
    """Extract way IDs from an OSM XML file (relation or direct ways)."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Try relation members first (most common format)
    way_ids = [m.get('ref') for m in root.findall(".//member[@type='way']")]

    # Fallback: direct way elements
    if not way_ids:
        way_ids = [w.get('id') for w in root.findall(".//way") if w.get('id')]

    return [wid for wid in way_ids if wid]


def fetch_ways_batch(way_ids, batch_size=50):
    """Fetch ways from OSM API and return {way_id_int: [node_id_int, ...]}."""
    way_nodes = {}

    for i in range(0, len(way_ids), batch_size):
        batch = way_ids[i:i + batch_size]
        ids_str = ','.join(batch)
        url = f"{OSM_API_BASE}/ways.json?ways={ids_str}"

        r = requests.get(url, timeout=30, headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        for el in data.get('elements', []):
            if el['type'] == 'way':
                way_nodes[el['id']] = el.get('nodes', [])

        if i + batch_size < len(way_ids):
            time.sleep(REQUEST_DELAY)

    return way_nodes


def fetch_nodes_batch(node_ids, batch_size=200):
    """Fetch node coordinates from OSM API and return {node_id_int: [lat, lon]}."""
    nodes = {}
    unique_ids = list(set(node_ids))

    for i in range(0, len(unique_ids), batch_size):
        batch = unique_ids[i:i + batch_size]
        ids_str = ','.join(str(nid) for nid in batch)
        url = f"{OSM_API_BASE}/nodes.json?nodes={ids_str}"

        r = requests.get(url, timeout=30, headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        for el in data.get('elements', []):
            if el['type'] == 'node':
                nodes[el['id']] = [el['lat'], el['lon']]

        if i + batch_size < len(unique_ids):
            time.sleep(REQUEST_DELAY)

    return nodes


def resolve_xml_file(xml_path, force=False):
    """Resolve coordinates for a single XML file. Returns (way_ids, status_str)."""
    way_ids = extract_way_ids(xml_path)

    if not way_ids:
        return None, "no way IDs found"

    if not force and _cache_exists(way_ids):
        return way_ids, "already cached ✓"

    # Step 1: Fetch ways → get node references
    print("ways...", end=" ", flush=True)
    way_node_refs = fetch_ways_batch(way_ids)

    # Step 2: Collect all unique node IDs
    all_node_ids = []
    for node_list in way_node_refs.values():
        all_node_ids.extend(node_list)

    # Step 3: Fetch all node coordinates
    print(f"nodes({len(set(all_node_ids))})...", end=" ", flush=True)
    node_coords = fetch_nodes_batch(all_node_ids)

    # Step 4: Build way → coordinates mapping
    ways_data = {}
    for way_id, node_list in way_node_refs.items():
        coords = [node_coords[nid] for nid in node_list if nid in node_coords]
        if coords:
            ways_data[way_id] = coords

    # Step 5: Save to cache
    if ways_data:
        cache_file = _save_cache(way_ids, ways_data)
        return way_ids, f"resolved ✓ ({len(ways_data)} ways → {cache_file.name})"

    return way_ids, "no data returned"


def main():
    """Resolve all XML highway files."""
    force = '--force' in sys.argv

    # Single file mode
    if '--file' in sys.argv:
        idx = sys.argv.index('--file')
        if idx + 1 < len(sys.argv):
            xml_path = Path(sys.argv[idx + 1])
            print(f"Resolving {xml_path}...", end=" ", flush=True)
            way_ids, status = resolve_xml_file(xml_path, force=True)
            print(status)
            return
        else:
            print("Error: --file requires a path argument")
            sys.exit(1)

    # Batch mode: resolve all XML files
    xml_files = sorted(HIGHWAYS_DIR.rglob("*.xml"))

    print(f"Found {len(xml_files)} XML files in {HIGHWAYS_DIR}/")
    print(f"Cache directory: {CACHE_DIR}/")
    if force:
        print("Mode: FORCE (re-resolving everything)")
    print()

    resolved = 0
    cached = 0
    failed = 0

    for i, xml_path in enumerate(xml_files, 1):
        rel_path = xml_path.relative_to(HIGHWAYS_DIR)
        print(f"  [{i}/{len(xml_files)}] {rel_path}... ", end="", flush=True)

        try:
            way_ids, status = resolve_xml_file(xml_path, force=force)
            print(status)

            if "already cached" in status:
                cached += 1
            elif "resolved" in status:
                resolved += 1
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            break
        except Exception as e:
            print(f"FAILED: {e}")
            failed += 1

    print(f"\nDone! Resolved: {resolved}, Already cached: {cached}, Failed: {failed}")


if __name__ == "__main__":
    main()
