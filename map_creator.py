import json

import folium

from components.base_map import create_base_map
from components.city_elements import add_cities_to_map
from components.highway_elements import add_highways_to_map, add_totals_table
from components.map_layers import add_tile_layers
from components.sidebar_builder import build_sidebar_items
from components.timeline_builder import build_timeline_payload
from components.ui_builder import (
    build_dark_mode_toggle,
    build_loading_overlay,
    build_map_controls,
    build_meta_tags,
    build_sidebar,
    build_skip_link,
    build_timeline,
    build_update_footer,
    build_ux_enhancements,
)
from config import (
    BUNDLED_CSS_PATH,
    BUNDLED_JS_PATH,
    FONT_AWESOME_URL,
    STATIC_CSS_FILES,
    STATIC_JS_FILES,
    USE_BUNDLED_ASSETS,
)
from highway_data import HIGHWAYS
from utils.html_optimizer import optimize_template
from utils.resource_manager import add_css_file, add_external_js, add_preload_css


def create_highways_map(labels_position="below"):
    """Create a Folium map displaying highways in Romania."""
    # Create base map
    m = create_base_map()

    # Add HTML lang attribute for accessibility and SEO
    html_lang = """
    <script>
        document.documentElement.setAttribute('lang', 'ro');
    </script>
    """
    m.get_root().html.add_child(folium.Element(html_lang))

    # Add meta tags for SEO and responsiveness
    m.get_root().header.add_child(folium.Element(build_meta_tags()))

    # Add Font Awesome for icons (non-blocking)
    add_preload_css(m, FONT_AWESOME_URL)

    # Add CSS files
    add_css_file(m, "static/css/critical.css")
    if USE_BUNDLED_ASSETS:
        add_preload_css(m, BUNDLED_CSS_PATH)
    else:
        for css_path in STATIC_CSS_FILES:
            add_preload_css(m, css_path)

    # Add tile layers and Romania outline
    add_tile_layers(m)

    # Add cities and boundaries
    add_cities_to_map(m, labels_position)

    # Add highways
    add_highways_to_map(m)

    # Add skip link for keyboard navigation
    m.get_root().html.add_child(folium.Element(build_skip_link()))

    # Add map controls HTML
    m.get_root().html.add_child(folium.Element(build_map_controls()))

    # Add dark mode toggle button
    m.get_root().html.add_child(folium.Element(build_dark_mode_toggle()))

    # Add JavaScript files (deferred)
    if USE_BUNDLED_ASSETS:
        add_external_js(m, BUNDLED_JS_PATH, {"defer": "defer"})
    else:
        for js_path in STATIC_JS_FILES:
            add_external_js(m, js_path, {"defer": "defer"})

    # Add highway totals table
    add_totals_table(m)

    # Add loading overlay
    m.get_root().html.add_child(folium.Element(build_loading_overlay()))

    # Add sidebar
    sidebar_items_html = build_sidebar_items(HIGHWAYS)
    m.get_root().html.add_child(folium.Element(build_sidebar(sidebar_items_html)))

    # Add UX Enhancements
    m.get_root().html.add_child(folium.Element(build_ux_enhancements()))

    # Add Timeline Slider
    timeline_payload, current_state_total = build_timeline_payload(HIGHWAYS)
    timeline_payload_json = json.dumps(timeline_payload)
    m.get_root().html.add_child(
        folium.Element(build_timeline(timeline_payload_json, current_state_total))
    )

    # Add update date footer
    m.get_root().html.add_child(folium.Element(build_update_footer()))

    # Add layer control
    folium.LayerControl(position="topright").add_to(m)

    # Override save method to optimize HTML
    original_save = m.save

    def optimized_save(path, **kwargs):
        original_save(path, **kwargs)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        optimized_content = optimize_template(content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(optimized_content)

    m.save = optimized_save

    return m


if __name__ == "__main__":
    # Create the map
    m = create_highways_map()

    # Save the map to an HTML file
    m.save("index.html")
