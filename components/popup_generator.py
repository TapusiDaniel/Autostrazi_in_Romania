"""Popup generation utilities for highway sections."""

from typing import Dict, Any


def create_section_popup(highway_code: str, section_name: str, section_data: Dict[str, Any]) -> str:
    """Creates an HTML popup for a highway section with relevant information based on its status.
    
    Args:
        highway_code: The highway identifier (e.g., "Autostrada A1")
        section_name: The name of the highway section
        section_data: Dictionary containing section metadata (status, length, dates, etc.)
    
    Returns:
        HTML string for the popup content
    """
    status_colors = {
        "finished": "green",
        "in_construction": "orange",
        "planned": "grey",
        "tendered": "brown"
    }
    
    status_text = {
        "finished": "Finalizat",
        "in_construction": "În construcție",
        "planned": "Planificat",
        "tendered": "Lansat spre licitație"
    }
    
    # Create base popup content
    popup_content = f"""
    <div style='font-family: Arial; font-size: 12px; padding: 5px;'>
        <b>{highway_code}</b><br>
        <b>Tronson: {section_name}</b>
        <hr style='margin: 5px 0;'>
        Status: <span style='color: {status_colors[section_data["status"]]};'>
            {status_text[section_data["status"]]}</span><br>
        Lungime: {section_data["length"]}"""

    # Add status-specific information
    if section_data["status"] == "finished":
        popup_content += f"""<br>Data finalizării: {section_data.get("completion_date", "N/A")}"""
    
    elif section_data["status"] == "in_construction":
        popup_content += f"""
        <br>Finalizare: {section_data.get("completion_date", "N/A")}
        <br>Progres: {section_data.get("progress", "N/A")}"""
    
    elif section_data["status"] == "tendered":
        popup_content += f"""
        <br>Finalizare licitație: {section_data.get("tender_end_date", "N/A")}
        <br>Codul SEAP: {section_data.get("seap_code", "N/A")}
        <br>Stadiul curent: {section_data.get("current_stage", "N/A")}
        <br>Durata construcției: {section_data.get("construction_duration", "N/A")}"""
    
    elif section_data["status"] == "planned":
        popup_content += f"""
        <br>Finalizare studiu de fezabilitate: {section_data.get("feasibility_study_date", "N/A")}
        <br>Data aproximativă a finalizării: {section_data.get("projected_completion_date", "N/A")}"""

    # Add optional information if available
    if "constructor" in section_data:
        popup_content += f"<br>Constructor: {section_data['constructor']}"
    if "designer" in section_data:
        popup_content += f"<br>Proiectant: {section_data['designer']}"

    # Add cost information
    if section_data["status"] in ["finished", "in_construction"]:
        if "cost" in section_data:
            popup_content += f"<br>Cost: {section_data['cost']} €"
    else:
        if "estimated_cost" in section_data:
            popup_content += f"<br>Cost estimat: {section_data['estimated_cost']} €"

    # Add financing and current stage if available
    if "financing" in section_data:
        popup_content += f"<br>Finanțare: {section_data['financing']}"
    
    if "current_stage" in section_data and section_data["status"] != "tendered":
        popup_content += f"<br>Stadiul curent: {section_data['current_stage']}"

    popup_content += "</div>"
    
    return popup_content
