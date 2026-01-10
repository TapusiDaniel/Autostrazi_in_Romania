import folium

def add_css_file(m, file_path):
    """Add a CSS file to the map."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            m.get_root().header.add_child(folium.Element(f"<style>{css_content}</style>"))
        return True
    except Exception as e:
        print(f"Error loading CSS file {file_path}: {str(e)}")
        return False

def add_js_file(m, file_path):
    """Add a JavaScript file to the map."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
            m.get_root().html.add_child(folium.Element(f"<script>{js_content}</script>"))
        return True
    except Exception as e:
        print(f"Error loading JS file {file_path}: {str(e)}")
        return False

def add_external_css(m, url, attributes=None):
    """Add an external CSS file to the map."""
    link_tag = f'<link rel="stylesheet" href="{url}"'
    if attributes:
        for attr, value in attributes.items():
            link_tag += f' {attr}="{value}"'
    link_tag += '>'
    m.get_root().header.add_child(folium.Element(link_tag))

def add_external_js(m, url, attributes=None):
    """Add an external JavaScript file to the map."""
    script_tag = f'<script src="{url}"'
    if attributes:
        for attr, value in attributes.items():
            script_tag += f' {attr}="{value}"'
    script_tag += '></script>'
    m.get_root().html.add_child(folium.Element(script_tag))