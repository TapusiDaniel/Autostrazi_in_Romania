# Map configuration settings

# Map center and default zoom level
MAP_CENTER = [45.9432, 24.9668]
MAP_ZOOM = 7
MAP_PREFER_CANVAS = True

# Data paths
DATA_DIR = "data"
CITY_BOUNDARIES_DIR = f"{DATA_DIR}/city_boundaries"
ROMANIA_GEOJSON_FILE = f"{DATA_DIR}/romania.geojson"

# Optional: resolve missing OSM cache entries during build
AUTO_RESOLVE_CACHE = False

# Highway rendering/performance
HIGHWAY_SMOOTH_FACTOR = 2.0
SIMPLIFY_TOLERANCE = 0.001
COORDINATE_PRECISION = 5
HIGH_DETAIL_ZOOM = 9
ENABLE_HIGH_DETAIL_LAYERS = True

# Timeline settings
TIMELINE_START_YEAR = 1970
TIMELINE_END_YEAR = 2035
TIMELINE_PRESENT_YEAR = 2025
TIMELINE_LABELS = [1970, 2000, 2010, 2020, 2025, 2030, 2035]
TIMELINE_LABEL_POSITIONS = [0, 20, 40, 60, 75, 88, 100]
TIMELINE_SLIDER_DEFAULT = 78

# Meta and resource hints
META_TITLE = "Autostrăzi în România - Hartă Interactivă"
META_DESCRIPTION = (
    "Hartă interactivă a autostrăzilor și drumurilor expres din România. "
    "Vizualizați progresul construcției, secțiunile finalizate, în lucru și planificate. "
    "Actualizat regulat cu date oficiale."
)
META_KEYWORDS = (
    "Romania, highways, motorways, autostrăzi, drumuri expres, infrastructure, "
    "harta autostrazilor, retea rutiera"
)
META_AUTHOR = "Daniel Tapusi"
META_ROBOTS = "index, follow"
PRECONNECT_URLS = [
    "https://cdnjs.cloudflare.com",
    "https://unpkg.com",
]
DNS_PREFETCH_URLS = [
    "https://mt1.google.com",
    "https://tile.openstreetmap.org",
]

# Static asset loading
FONT_AWESOME_URL = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
)
STATIC_CSS_FILES = [
    "static/css/controls.css",
    "static/css/totals_table.css",
    "static/css/markers.css",
    "static/css/ux_enhancements.css",
]
STATIC_JS_FILES = [
    "static/js/map_controls.js",
    "static/js/section_filters.js",
    "static/js/resource_loader.js",
    "static/js/dark_mode.js",
    "static/js/ux_enhancements.js",
    "static/js/timeline.js",
    "static/js/highway_layers.js",
    "static/js/loading_overlay.js",
    "static/js/sidebar.js",
]
BUNDLED_CSS_PATH = "assets/css/app.css"
BUNDLED_JS_PATH = "assets/js/app.js"
USE_BUNDLED_ASSETS = True

# Romanian month names
ROMANIAN_MONTHS = {
    1: "ianuarie",
    2: "februarie",
    3: "martie",
    4: "aprilie",
    5: "mai",
    6: "iunie",
    7: "iulie",
    8: "august",
    9: "septembrie",
    10: "octombrie",
    11: "noiembrie",
    12: "decembrie",
}

# Re-export city data for backward compatibility
from data.city_data import CITIES, CITY_LABELS, CITY_BOUNDARIES
