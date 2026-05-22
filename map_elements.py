import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import folium
from folium.utilities import JsCode
from shapely.geometry import LineString

from components.highway_processor import (
    add_section_delimiter,
    add_section_logo,
    process_xml_ways,
)
from components.popup_generator import create_section_popup
from config import (
    AUTO_RESOLVE_CACHE,
    CITY_BOUNDARIES,
    COORDINATE_PRECISION,
    ENABLE_HIGH_DETAIL_LAYERS,
    HIGH_DETAIL_ZOOM,
    HIGHWAY_SMOOTH_FACTOR,
    SIMPLIFY_TOLERANCE,
)
from utils.geo import get_all_way_coordinates

SIMPLIFIED_CACHE_DIR = Path("data/cache/simplified")


def _simplified_cache_path(cache_key):
    return SIMPLIFIED_CACHE_DIR / f"{cache_key}.json"


def _load_simplified(cache_key):
    cache_path = _simplified_cache_path(cache_key)
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_simplified(cache_key, coords):
    SIMPLIFIED_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _simplified_cache_path(cache_key)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(coords, f)


def _round_coordinates(coords):
    return [
        [round(coord[0], COORDINATE_PRECISION), round(coord[1], COORDINATE_PRECISION)]
        for coord in coords
    ]


def simplify_coordinates(coords, cache_key=None):
    if not coords or len(coords) < 3:
        return _round_coordinates(coords) if coords else coords

    if cache_key:
        cached = _load_simplified(cache_key)
        if cached is not None:
            return _round_coordinates(cached)

    line = LineString(coords)
    simplified = line.simplify(SIMPLIFY_TOLERANCE, preserve_topology=False)
    simplified_coords = list(simplified.coords)
    if len(simplified_coords) < 2:
        simplified_coords = coords
    simplified_coords = _round_coordinates(simplified_coords)

    if cache_key:
        _save_simplified(cache_key, simplified_coords)

    return simplified_coords


def _line_geometry(lines):
    if len(lines) == 1:
        return {"type": "LineString", "coordinates": lines[0]}
    return {"type": "MultiLineString", "coordinates": lines}


def _write_feature_collection(path, features):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"type": "FeatureCollection", "features": features},
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )


def add_city_boundaries(m):
    """Add city boundaries using local JSON files."""
    import json
    from pathlib import Path

    for city, config in CITY_BOUNDARIES.items():
        try:
            json_file = Path("data/city_boundaries") / f"{city}.json"

            if not json_file.exists():
                print(f"Warning: Missing JSON file for {city}: {json_file}")
                continue

            # Load JSON data
            with open(json_file, "r", encoding="utf-8") as f:
                boundary_data = json.load(f)

            # Process coordinates
            all_coords = []
            if boundary_data["type"] == "Feature":
                if boundary_data["geometry"]["type"] == "Polygon":
                    # Convert coordinates from [lon, lat] to [lat, lon]
                    all_coords = [
                        [coord[1], coord[0]]
                        for coord in boundary_data["geometry"]["coordinates"][0]
                    ]

            if all_coords:
                # Ensure first and last points are identical for closed polygon
                if all_coords[0] != all_coords[-1]:
                    all_coords.append(all_coords[0])

                # Add boundary as GeoJson with specific class
                boundary = folium.GeoJson(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [[coord[1], coord[0]] for coord in all_coords]
                            ],
                        },
                    },
                    style_function=lambda x: {
                        "fillColor": config["fill_color"],
                        "color": config["border_color"],
                        "weight": 2,
                        "fillOpacity": 1,
                        "opacity": 1,
                    },
                    name="_",
                    class_name="city-boundary",
                )
                boundary.add_to(m)

        except Exception as e:
            print(f"Error adding {city} boundary: {str(e)}")


def add_all_highways_to_map(m):
    """Add all highways to map with proper styling, popups, and interactive features."""
    from highway_data import HIGHWAYS

    print(f"\n  → Processing {len(HIGHWAYS)} highways...")

    # Initialize feature groups for different highway statuses
    status_groups = {
        "finished": folium.FeatureGroup(name="Finished"),
        "in_construction": folium.FeatureGroup(name="In Construction"),
        "tendered": folium.FeatureGroup(name="Tendered"),
        "planned": folium.FeatureGroup(name="Planned"),
    }

    detail_groups = {}
    if ENABLE_HIGH_DETAIL_LAYERS:
        detail_groups = {
            key: folium.FeatureGroup(name=f"_detail_{key}", show=False)
            for key in status_groups
        }

    # Initialize delimiter groups
    delimiter_groups = {
        "finished": folium.FeatureGroup(name="_delimiters_finished", show=False),
        "in_construction": folium.FeatureGroup(
            name="_delimiters_in_construction", show=False
        ),
        "tendered": folium.FeatureGroup(name="_delimiters_tendered", show=False),
        "planned": folium.FeatureGroup(name="_delimiters_planned", show=False),
    }

    # Create logo group
    logo_group = folium.FeatureGroup(name="_logos", show=True)
    logo_group.add_to(m)

    # Add groups to map
    for group in status_groups.values():
        group.add_to(m)
    for group in detail_groups.values():
        group.add_to(m)
    for group in delimiter_groups.values():
        group.add_to(m)

    # Define status colors
    status_colors = {
        "finished": "green",
        "in_construction": "orange",
        "planned": "grey",
        "tendered": "brown",
    }
    low_features_by_status = {key: [] for key in status_groups}
    high_features_by_status = {key: [] for key in status_groups}
    bind_feature_popup = JsCode(
        """
        function(feature, layer) {
            if (feature.properties.popup_html) {
                layer.bindPopup(feature.properties.popup_html, {maxWidth: 250});
            }
            if (feature.properties.tooltip) {
                layer.bindTooltip(feature.properties.tooltip, {sticky: true});
            }
        }
        """
    )

    def get_section_year(section_data):
        """Calculate completion year for any section status."""
        status = section_data.get("status")
        # Check if there's an explicit projected completion date first
        projected_date = section_data.get("projected_completion_date")
        if projected_date:
            # Data is already clean, just take the year
            return str(projected_date)[:4]

        if status in ["finished", "in_construction"]:
            completion_date = section_data.get("completion_date", "")
            if not completion_date:
                return "unknown"
            return str(completion_date)[:4]

        elif status == "tendered":
            try:
                tender_year = int(section_data.get("tender_end_date", "2026"))
                duration_str = section_data.get("construction_duration", "0 de luni")
                months = int(duration_str.split()[0])
                years = months / 12
                return str(int(tender_year + years))
            except (TypeError, ValueError, AttributeError):
                return "2035"

        elif status == "planned":
            return "2035"

        return "unknown"

    def style_function(feature):
        """Define highway styling based on status"""
        status = feature["properties"]["status"]
        return {
            "color": status_colors.get(status, "grey"),
            "weight": 4,
            "opacity": 1,
            "className": feature["properties"]["className"],
        }

    def highlight_function(feature):
        """Define highway highlight styling"""
        status = feature["properties"]["status"]
        return {"color": status_colors.get(status, "grey"), "weight": 6, "opacity": 0.8}

    def add_feature_collection(features, group, use_highlight):
        if not features:
            return

        kwargs = {
            "style_function": style_function,
            "smooth_factor": HIGHWAY_SMOOTH_FACTOR,
            "on_each_feature": bind_feature_popup,
            "class_name": "highway-sections",
        }
        if use_highlight:
            kwargs["highlight_function"] = highlight_function

        folium.GeoJson(
            {"type": "FeatureCollection", "features": features},
            **kwargs,
        ).add_to(group)

    # Process each highway section
    total_highways = len(HIGHWAYS)
    highway_counter = 0

    for highway_code, highway_data in HIGHWAYS.items():
        highway_counter += 1
        total_sections = len(highway_data["sections"])
        print(
            f"\n  [{highway_counter}/{total_highways}] Processing {highway_code} ({total_sections} sections)..."
        )

        section_counter = 0
        for section_name, section_data in highway_data["sections"].items():
            section_counter += 1
            print(
                f"    [{section_counter}/{total_sections}] {section_name}...", end=" "
            )

            try:
                status = section_data["status"]
                if status not in status_groups:
                    print("✗ Invalid status, skipping")
                    continue

                # Handle GeoJSON data
                if "geojson_file" in section_data:
                    print("(GeoJSON)", end=" ")
                    with open(
                        f"data/highways/{section_data['geojson_file']}", "r"
                    ) as f:
                        geojson_data = json.load(f)

                    coordinates = []
                    if "features" in geojson_data:
                        for feature in geojson_data["features"]:
                            if feature["geometry"]["type"] == "LineString":
                                coordinates.extend(feature["geometry"]["coordinates"])
                    elif "geometry" in geojson_data:
                        if geojson_data["geometry"]["type"] == "LineString":
                            coordinates.extend(geojson_data["geometry"]["coordinates"])
                        elif geojson_data["geometry"]["type"] == "MultiLineString":
                            for line in geojson_data["geometry"]["coordinates"]:
                                coordinates.extend(line)

                    if coordinates:
                        geojson_path = (
                            Path("data/highways") / section_data["geojson_file"]
                        )
                        cache_key = hashlib.md5(
                            f"{geojson_path}:{geojson_path.stat().st_mtime}:{SIMPLIFY_TOLERANCE}".encode()
                        ).hexdigest()
                        low_coordinates = simplify_coordinates(
                            coordinates, cache_key=cache_key
                        )

                        # Create and add highway feature
                        feature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": coordinates,
                            },
                            "properties": {
                                "name": section_name,
                                "highway": highway_code,
                                "status": status,
                                "completion_date": section_data.get(
                                    "completion_date", "N/A"
                                ),
                                "length": section_data.get("length", "N/A"),
                                "constructor": section_data.get("constructor", "N/A"),
                                "cost": section_data.get("cost", "N/A"),
                            },
                        }

                        class_base = (
                            f'highway-section highway-section-{highway_code.lower().replace(" ", "-")} '
                            f"section-year-{get_section_year(section_data)} section-status-{status}"
                        )
                        popup_html = create_section_popup(
                            highway_code, section_name, section_data
                        )
                        feature_properties = {
                            **feature["properties"],
                            "className": f"{class_base} low-detail",
                            "popup_html": popup_html,
                            "tooltip": (
                                f"{highway_code} - {section_name}"
                                if not ENABLE_HIGH_DETAIL_LAYERS
                                else ""
                            ),
                        }

                        low_feature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": low_coordinates,
                            },
                            "properties": feature_properties,
                        }
                        low_features_by_status[status].append(low_feature)

                        if ENABLE_HIGH_DETAIL_LAYERS:
                            high_feature = {
                                **feature,
                                "properties": {
                                    **feature["properties"],
                                    "className": f"{class_base} high-detail",
                                    "popup_html": popup_html,
                                    "tooltip": f"{highway_code} - {section_name}",
                                },
                            }
                            high_features_by_status[status].append(high_feature)

                        # Add delimiter and logo if specified
                        if "end_point" in section_data:
                            formatted_coords = [
                                [coord[1], coord[0]] for coord in coordinates
                            ]
                            add_section_delimiter(
                                delimiter_groups[status],
                                section_data["end_point"],
                                formatted_coords,
                            )

                        if "logo" in section_data:
                            add_section_logo(
                                m,
                                [[coord[1], coord[0]] for coord in coordinates],
                                section_data["logo"],
                                logo_group,
                                highway_code,
                                status,
                            )

                    print("✓")

                # Handle XML data
                elif "xml_file" in section_data:
                    print("(XML)", end=" ")
                    tree = ET.parse(f"data/highways/{section_data['xml_file']}")
                    root = tree.getroot()
                    way_ids = [
                        member.get("ref")
                        for member in root.findall(".//member[@type='way']")
                    ]

                    print(f"[{len(way_ids)} ways]", end=" ")
                    print("fetching...", end=" ", flush=True)

                    xml_path = Path("data/highways") / section_data["xml_file"]
                    ways_data = get_all_way_coordinates(
                        way_ids, xml_path=xml_path, auto_resolve=AUTO_RESOLVE_CACHE
                    )

                    if ways_data:
                        print("processing...", end=" ", flush=True)
                        paths = process_xml_ways(way_ids, ways_data)

                        base_cache_key = hashlib.md5(
                            (
                                f"{xml_path}:{xml_path.stat().st_mtime}:"
                                f"{','.join(way_ids)}:{SIMPLIFY_TOLERANCE}"
                            ).encode()
                        ).hexdigest()

                        full_lines = []
                        low_lines = []
                        for path_index, path in enumerate(paths):
                            if not path:
                                continue

                            full_coords = [[coord[1], coord[0]] for coord in path]
                            if len(full_coords) < 2:
                                continue

                            low_coords = simplify_coordinates(
                                full_coords,
                                cache_key=f"{base_cache_key}-{path_index}",
                            )
                            full_lines.append(full_coords)
                            low_lines.append(low_coords)

                        if full_lines:
                            class_base = (
                                f'highway-section highway-section-{highway_code.lower().replace(" ", "-")} '
                                f"section-year-{get_section_year(section_data)} section-status-{status}"
                            )
                            popup_html = create_section_popup(
                                highway_code, section_name, section_data
                            )
                            properties = {
                                "name": section_name,
                                "highway": highway_code,
                                "status": status,
                                "completion_date": section_data.get(
                                    "completion_date", "N/A"
                                ),
                                "length": section_data.get("length", "N/A"),
                                "constructor": section_data.get("constructor", "N/A"),
                                "cost": section_data.get("cost", "N/A"),
                            }

                            low_feature = {
                                "type": "Feature",
                                "geometry": _line_geometry(low_lines),
                                "properties": {
                                    **properties,
                                    "className": f"{class_base} low-detail",
                                    "popup_html": popup_html,
                                    "tooltip": (
                                        f"{highway_code} - {section_name}"
                                        if not ENABLE_HIGH_DETAIL_LAYERS
                                        else ""
                                    ),
                                },
                            }
                            low_features_by_status[status].append(low_feature)

                            if ENABLE_HIGH_DETAIL_LAYERS:
                                feature = {
                                    "type": "Feature",
                                    "geometry": _line_geometry(full_lines),
                                    "properties": {
                                        **properties,
                                        "className": f"{class_base} high-detail",
                                        "popup_html": popup_html,
                                        "tooltip": f"{highway_code} - {section_name}",
                                    },
                                }
                                high_features_by_status[status].append(feature)

                        # Add delimiter and logo if specified
                        if paths and "end_point" in section_data:
                            add_section_delimiter(
                                delimiter_groups[status],
                                section_data["end_point"],
                                paths[-1],
                            )

                        if paths and "logo" in section_data:
                            add_section_logo(
                                m,
                                paths[-1],
                                section_data["logo"],
                                logo_group,
                                highway_code,
                                status,
                            )

                    print("✓")
                else:
                    print("✗ No data source")

            except Exception as e:
                print(f"✗ Error: {str(e)}")
                continue

    print("\n  ✓ Finished processing all highways\n")

    for status, features in low_features_by_status.items():
        add_feature_collection(
            features,
            status_groups[status],
            use_highlight=True,
        )

    if ENABLE_HIGH_DETAIL_LAYERS:
        for status, features in high_features_by_status.items():
            add_feature_collection(
                features,
                detail_groups[status],
                use_highlight=True,
            )

    status_layer_names = {key: group.get_name() for key, group in status_groups.items()}
    detail_layer_names = {key: group.get_name() for key, group in detail_groups.items()}

    layer_payload = {
        "statusLayers": {
            key: {
                "low": status_layer_names[key],
                "high": detail_layer_names[key],
            }
            for key in status_layer_names
            if key in detail_layer_names
        },
        "highDetailZoom": HIGH_DETAIL_ZOOM,
        "smoothFactor": HIGHWAY_SMOOTH_FACTOR,
    }
    layer_payload_json = json.dumps(layer_payload)
    m.get_root().html.add_child(
        folium.Element(
            f'<script id="highway-layer-data" type="application/json">{layer_payload_json}</script>'
        )
    )

    print("Finished adding highways to map")
