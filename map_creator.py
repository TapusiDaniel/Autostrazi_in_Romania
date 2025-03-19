import folium
from components.base_map import create_base_map
from components.map_layers import add_tile_layers
from components.city_elements import add_cities_to_map
from components.highway_elements import add_highways_to_map, add_totals_table
from utils_folder.resource_manager import add_css_file, add_js_file, add_external_css
from utils_folder.html_optimizer import optimize_template

def create_highways_map(labels_position="below"):
    """Create a Folium map displaying highways in Romania."""
    # Create base map
    m = create_base_map()
    
    # Add meta tags for SEO and responsiveness
    meta_tags = """
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Interactive map of highways in Romania">
        <title>Autostrăzi în România</title>
    """
    m.get_root().header.add_child(folium.Element(meta_tags))
    
    # Add Font Awesome for icons
    add_external_css(m, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css")
    
    # Add CSS files
    add_css_file(m, "static/css/critical.css")
    add_css_file(m, "static/css/controls.css")
    add_css_file(m, "static/css/totals_table.css")
    add_css_file(m, "static/css/markers.css")
    
    # Add tile layers and Romania outline
    add_tile_layers(m)
    
    # Add cities and boundaries
    add_cities_to_map(m, labels_position)
    
    # Add highways
    add_highways_to_map(m)
    
    # Add map controls HTML
    controls_html = """
    <div class="map-controls">
        <button class="minimize-button">−</button>
        <div class="map-button-group">
            <div class="map-button-group-title">Stil hartă</div>
            <button class="map-button active" data-map="white">Hartă Albă</button>
            <button class="map-button" data-map="osm">OpenStreetMap</button>
            <button class="map-button" data-map="satellite">Satelit</button>
        </div>

        <div class="map-button-group">
            <div class="map-button-group-title">Secțiuni</div>
            <button class="section-button section-all active" data-section="all">
                <span class="section-indicator"></span>
                Toate secțiunile
            </button>
            <button class="section-button section-finished" data-section="Finished">
                <span class="section-indicator"></span>
                Finalizate
            </button>
            <button class="section-button section-in-construction" data-section="In Construction">
                <span class="section-indicator"></span>
                În construcție
            </button>
            <button class="section-button section-tendered" data-section="Tendered">
                <span class="section-indicator"></span>
                În licitație
            </button>
            <button class="section-button section-planned" data-section="Planned">
                <span class="section-indicator"></span>
                Planificate
            </button>
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(controls_html))
    
    # Add JavaScript files
    add_js_file(m, "static/js/map_controls.js")
    add_js_file(m, "static/js/section_filters.js")
    add_js_file(m, "static/js/resource_loader.js")
    
    # Add highway totals table
    add_totals_table(m)
    
    # Add layer control
    folium.LayerControl(position='topright').add_to(m)
    
    # Override save method to optimize HTML
    original_save = m.save
    
    def optimized_save(path, **kwargs):
        original_save(path, **kwargs)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        optimized_content = optimize_template(content)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
    
    m.save = optimized_save
    
    return m

if __name__ == "__main__":
    # Create the map
    m = create_highways_map()
    
    # Save the map to an HTML file
    m.save('index.html')