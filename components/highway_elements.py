import folium

from components.highway_processor import calculate_highway_totals
from highway_data import HIGHWAYS
from map_elements import add_all_highways_to_map
from utils.template_loader import render_template


def add_highways_to_map(m):
    """Add highways to the map."""
    add_all_highways_to_map(m)


def add_totals_table(m):
    """Add highway totals table to the map."""
    totals = calculate_highway_totals(HIGHWAYS)

    # Create the HTML for the totals table
    table_html = render_template(
        "totals_table",
        total=f"{totals['total']:.2f}",
        finished=f"{totals['finished']:.2f}",
        in_construction=f"{totals['in_construction']:.2f}",
        tendered=f"{totals['tendered']:.2f}",
        planned=f"{totals['planned']:.2f}",
    )

    # Add HTML to the map
    m.get_root().html.add_child(folium.Element(table_html))

    # Add GitHub button
    github_button = render_template("github_button")
    m.get_root().html.add_child(folium.Element(github_button))
