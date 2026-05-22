import json
from importlib import import_module
from pathlib import Path

MANIFEST_PATH = Path("data/highways_manifest.json")


def _load_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_sections(module_path, var_name):
    module = import_module(module_path)
    return getattr(module, var_name)


def load_highways():
    highways = {}
    for entry in _load_manifest():
        sections = _load_sections(entry["sections_module"], entry["sections_var"])
        highway_data = {
            "name": entry["name"],
            "sections": sections,
            "color": entry.get("color", "green"),
            "total_length": entry.get("total_length", "N/A"),
        }
        if "logo" in entry:
            highway_data["logo"] = entry["logo"]
        highways[entry["key"]] = highway_data
    return highways


HIGHWAYS = load_highways()
