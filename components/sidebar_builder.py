import re


def _highway_sort_key(highway_key):
    match = re.search(r"\b(A\d+|DEx\d+)\b", highway_key)
    if match:
        code = match.group(1)
        if code.startswith("A"):
            return (0, int(code[1:]), highway_key)
        return (1, int(code[3:]), highway_key)
    return (2, float("inf"), highway_key)


def build_sidebar_items(highways):
    sorted_highways = sorted(
        highways.items(), key=lambda item: _highway_sort_key(item[0])
    )
    items_html = ""

    for highway_key, data in sorted_highways:
        code_match = re.search(r"\b(A\d+|DEx\d+)\b", highway_key)
        display_code = code_match.group(1) if code_match else highway_key
        name = data.get("name", "")
        length = data.get("total_length", "N/A")
        display_label = (
            f"{display_code} - {name}" if code_match else (name or highway_key)
        )

        has_finished = False
        has_construction = False
        for section in data.get("sections", {}).values():
            if section["status"] == "finished":
                has_finished = True
            if section["status"] == "in_construction":
                has_construction = True

        dot_class = "mixed"
        if has_finished and not has_construction:
            dot_class = "finished"
        elif not has_finished and has_construction:
            dot_class = "in-construction"
        elif not has_finished and not has_construction:
            dot_class = "planned"

        items_html += f"""
            <div class="highway-item" onclick="highlightHighway('{highway_key}')">
                <div class="highway-status-dot {dot_class}"></div>
                <div style="display:flex; flex-direction:column;">
                    <span style="font-weight:bold;">{display_label}</span>
                    <span style="font-size:11px; color:#666;">{length}</span>
                </div>
            </div>
        """

    return items_html
