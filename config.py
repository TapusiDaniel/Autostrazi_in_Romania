# Map configuration settings

# Map center and default zoom level
MAP_CENTER = [45.9432, 24.9668]
MAP_ZOOM = 7

# Data paths
DATA_DIR = 'data'
CITY_BOUNDARIES_DIR = 'data/city_boundaries'
ROMANIA_GEOJSON_FILE = 'data/romania.geojson'

# Re-export city data for backward compatibility
from data.city_data import CITIES, CITY_LABELS, CITY_BOUNDARIES