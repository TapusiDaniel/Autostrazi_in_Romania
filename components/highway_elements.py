import folium
from map_elements import add_all_highways_to_map, calculate_highway_totals
from highway_data import HIGHWAYS

def add_highways_to_map(m):
    """Add highways to the map."""
    add_all_highways_to_map(m)

def add_totals_table(m):
    """Add highway totals table to the map."""
    totals = calculate_highway_totals(HIGHWAYS)
    
    # Create the HTML for the totals table
    table_html = f"""
    <div id="totals-table" class="totals-table">
        <table>
            <tr class="total-row">
                <td>Total:</td>
                <td>{totals['total']:.2f} km</td>
            </tr>
            <tr class="status-row finished">
                <td>Finalizat:</td>
                <td>{totals['finished']:.2f} km</td>
            </tr>
            <tr class="status-row in-construction">
                <td>În construcție:</td>
                <td>{totals['in_construction']:.2f} km</td>
            </tr>
            <tr class="status-row planned">
                <td>Planificat:</td>
                <td>{totals['planned']:.2f} km</td>
            </tr>
            <tr class="status-row tendered">
                <td>Licitat:</td>
                <td>{totals['tendered']:.2f} km</td>
            </tr>
        </table>
    </div>
    """
    
    # Add HTML to the map
    m.get_root().html.add_child(folium.Element(table_html))
    
    # Add update text
    update_text = """
    <div style="
        position: fixed;
        bottom: 10px;
        left: 10px;
        background: rgba(255, 255, 255, 0.8);
        padding: 5px;
        border-radius: 3px;
        z-index: 1000;
        font-family: Arial, sans-serif;
        color: #666;
        font-size: 10px;">
        Ultima actualizare: 15 aprilie 2025
    </div>
    """
    m.get_root().html.add_child(folium.Element(update_text))
    
    # Add GitHub button
    github_button = """
    <div style="position: fixed; top: 10px; left: 10px; z-index: 1000;">
        <a href="https://github.com/TapusiDaniel/Autostrazi_in_Romania" target="_blank" style="text-decoration: none;">
            <button style="background-color: #24292e; color: white; padding: 10px 15px; border: none; border-radius: 5px; font-size: 14px; cursor: pointer;">
                <i class="fab fa-github"></i> View on GitHub
            </button>
        </a>
    </div>
    """
    m.get_root().html.add_child(folium.Element(github_button))