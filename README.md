# 🛣️ Autostrăzi în România

An interactive visualization of Romania's highway network, showing current status, construction progress, and historical development of motorways (Autostrăzi) and expressways (Drumuri Expres).

## ✨ Features

### 🗺️ Interactive Map
- **Multiple View Modes**: Switch between White Map, OpenStreetMap, and Satellite views
- **Highway Status Visualization**: Color-coded highways by status (Finished, In Construction, Tendered, Planned)
- **Detailed Information**: Click any highway section for completion dates, length, and status details
- **City Markers**: Major Romanian cities with labels and administrative boundaries

### ⏱️ Timeline Mode
- **Historical Playback**: See how Romania's highway network evolved year by year
- **Cumulative Progress**: Track total kilometers built over time
- **Animated Transitions**: Smooth visualization of network growth

### 🌓 Dark Mode
- **Auto-Detection**: Automatically matches your system theme preference
- **Manual Toggle**: Switch between light and dark themes with 🌙/☀️ button
- **Comprehensive Styling**: Dark mode applies to map background, UI elements, and city markers

### 📊 Statistics
- **Real-time Totals**: View total kilometers by status (Finished, In Construction, etc.)
- **Detailed Breakdown**: See statistics for each individual highway
- **Always Visible**: Stats table accessible from any view

### 🔗 Sharing
- **Direct Links**: Share the map with others
- **Social Media**: Quick share to Facebook, Twitter, WhatsApp
- **Copy Link**: One-click copy to clipboard

### 🎯 Additional Features
- **Highway Logos**: Visual identification for each motorway
- **Section Delimiters**: Clear boundaries between highway segments
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Fullscreen Mode**: Distraction-free viewing experience

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TapusiDaniel/Licenta.git
   cd Autostrazi_in_Romania_v2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate the map**
   ```bash
   python main.py
   ```

4. **Open the map**
   - Open `index.html` in your web browser
   - Or use a local server:
     ```bash
     python -m http.server 8000
     ```
   - Navigate to `http://localhost:8000`

## 🛠️ Technology Stack

### Backend
- **Python 3.10+**: Core application logic
- **Folium**: Interactive map generation
- **Requests**: API calls to OpenStreetMap
- **Shapely**: Geometry operations

### Frontend
- **Leaflet.js**: Interactive mapping library
- **Vanilla JavaScript**: UI interactions and dynamic features
- **CSS3**: Styling and animations

### Data Sources
- **OpenStreetMap**: Highway geometry and geographic data
- **Overpass API**: Real-time OSM data queries
- **Manual Curation**: Highway status, completion dates, and metadata

## 🧰 Development

### Formatting & Linting
```bash
black .
ruff check .
```

### Optional: Auto-resolve OSM cache
Set `AUTO_RESOLVE_CACHE = True` in `config.py` to resolve missing OSM cache entries during a build.

### Build bundled assets
```bash
python build.py
```

## 📁 Project Structure

```
Autostrazi_in_Romania_v2/
├── main.py                 # Entry point
├── map_creator.py          # Map generation logic
├── map_elements.py         # Highway rendering
├── highway_data.py         # Highway manifest loader
├── config.py               # Configuration settings
├── components/             # Modular components
│   ├── base_map.py         # Base map initialization
│   ├── city_elements.py    # City markers and labels
│   ├── highway_elements.py # Highway rendering
│   └── map_layers.py       # Tile layers and overlays
├── data/                   # Data files
│   ├── city_data.py
│   ├── highways/           # GeoJSON and XML files
│   ├── highways_manifest.json # Highway metadata (manifest)
│   └── sections/           # Highway section definitions
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
└── utils/                  # Utility functions
    ├── geo.py              # GeoJSON and Overpass utilities
    ├── resource_manager.py # CSS/JS injection
    └── html_optimizer.py   # HTML post-processing
```

## 📊 Data Attribution

This project uses data from:
- **[OpenStreetMap](https://www.openstreetmap.org/)** contributors - Licensed under [ODbL](https://opendatacommons.org/licenses/odbl/)
- **[Overpass API](https://overpass-api.de/)** - For real-time OSM data queries
- Highway status and completion data manually curated from official sources

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue describing the problem
2. **Suggest Features**: Share your ideas for improvements
3. **Update Data**: Submit corrections for highway statuses or completion dates
4. **Code Contributions**: Fork the repo and submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Daniel Tapusi**
- GitHub: [@TapusiDaniel](https://github.com/TapusiDaniel)

## 🙏 Acknowledgments

- OpenStreetMap contributors for geographic data
- The Folium and Leaflet.js communities
- Romanian highway enthusiasts and data contributors

---

**Note**: Highway data is updated periodically. For the most current information, please refer to official sources such as [CNAIR](https://www.cnair.ro/) (Romanian National Company of Motorways and National Roads).
