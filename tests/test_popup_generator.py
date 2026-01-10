"""Unit tests for popup generator."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.popup_generator import create_section_popup


class TestCreateSectionPopup:
    """Tests for the create_section_popup function."""
    
    def test_finished_section(self):
        """Should create popup with completion date for finished sections."""
        section_data = {
            "status": "finished",
            "length": "50 km",
            "completion_date": "2023-06-15"
        }
        result = create_section_popup("A1", "București - Pitești", section_data)
        
        assert "A1" in result
        assert "București - Pitești" in result
        assert "Finalizat" in result
        assert "50 km" in result
        assert "2023-06-15" in result
        assert "green" in result  # Status color
    
    def test_in_construction_section(self):
        """Should include progress for construction sections."""
        section_data = {
            "status": "in_construction",
            "length": "30 km",
            "completion_date": "2025-12-01",
            "progress": "45%"
        }
        result = create_section_popup("A3", "Lot 1", section_data)
        
        assert "În construcție" in result
        assert "45%" in result
        assert "orange" in result
    
    def test_tendered_section(self):
        """Should include SEAP code for tendered sections."""
        section_data = {
            "status": "tendered",
            "length": "25 km",
            "seap_code": "SEAP-12345"
        }
        result = create_section_popup("A7", "Lot 5", section_data)
        
        assert "Lansat spre licitație" in result
        assert "SEAP-12345" in result
        assert "brown" in result
    
    def test_planned_section(self):
        """Should include feasibility date for planned sections."""
        section_data = {
            "status": "planned",
            "length": "80 km",
            "feasibility_study_date": "2024-03-01"
        }
        result = create_section_popup("A13", "Sibiu - Făgăraș", section_data)
        
        assert "Planificat" in result
        assert "grey" in result
    
    def test_optional_fields(self):
        """Should include optional fields when present."""
        section_data = {
            "status": "finished",
            "length": "40 km",
            "constructor": "Strabag",
            "cost": "500M"
        }
        result = create_section_popup("A10", "Sebeș - Turda", section_data)
        
        assert "Strabag" in result
        assert "500M" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
