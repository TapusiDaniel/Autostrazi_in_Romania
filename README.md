# Autostrăzi în România 🛣️

An interactive map visualization of Romania's highway infrastructure, including motorways, expressways, and planned routes.

## Features

- **Interactive Map**: Powered by Folium/Leaflet with multiple map styles (Standard, OSM, Satellite)
- **Comprehensive Coverage**: Displays finished, in-construction, tendered, and planned highway sections
- **City Integration**: Shows major Romanian cities with administrative boundaries
- **Filtering**: Toggle visibility by section status (Finished, In Construction, etc.)
- **Optimized Output**: Generates a single, optimized HTML file for easy deployment

## Requirements

- Python 3.8+
- Dependencies:
  - `folium` - Map generation
  - `requests` - HTTP client for fetching data
  - `shapely` - Geometry operations
  - `cssmin` / `jsmin` - Asset minification

## Installation

```bash
pip install folium requests shapely cssmin jsmin
```

## Usage

Generate the interactive map:

```bash
python main.py
```

This will:
1. Download and cache vendor files (Leaflet, Bootstrap, etc.)
2. Optimize CSS and JavaScript assets
3. Generate `index.html` with the complete map

## Project Structure

```
├── main.py                 # Entry point
├── config.py               # Configuration settings
├── map_creator.py          # Folium map assembly
├── build.py                # Asset optimization pipeline
├── components/             # Map component modules
│   ├── base_map.py         # Base map initialization
│   ├── city_elements.py    # City markers and labels
│   ├── highway_elements.py # Highway rendering
│   └── map_layers.py       # Tile layers and overlays
├── utils/                  # Utility modules
│   ├── geo.py              # GeoJSON and Overpass utilities
│   ├── resource_manager.py # CSS/JS injection
│   └── html_optimizer.py   # HTML post-processing
├── data/                   # GeoJSON files and city data
├── static/                 # Custom CSS and JavaScript
└── assets/                 # Generated/downloaded assets
```

## Data Sources

- Highway data: GeoJSON files with route geometries
- City boundaries: OSM data processed via Overpass API
- Base maps: OpenStreetMap, ESRI Satellite

## License

This project is for educational and informational purposes.
