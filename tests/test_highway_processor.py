"""Unit tests for highway processing utilities."""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.highway_processor import (
    process_xml_ways,
    calculate_logo_position,
    calculate_highway_totals
)


class TestProcessXmlWays:
    """Tests for the process_xml_ways function."""
    
    def test_empty_input(self):
        """Should return empty list for empty input."""
        assert process_xml_ways([], {}) == []
        assert process_xml_ways(None, None) == []
    
    def test_single_way(self):
        """Should return single path for single way."""
        way_ids = ['123']
        ways_data = {
            123: [[45.0, 25.0], [45.1, 25.1], [45.2, 25.2]]
        }
        result = process_xml_ways(way_ids, ways_data)
        assert len(result) == 1
        assert result[0] == [[45.0, 25.0], [45.1, 25.1], [45.2, 25.2]]
    
    def test_connected_ways(self):
        """Should merge connected ways into single path."""
        way_ids = ['1', '2']
        ways_data = {
            1: [[45.0, 25.0], [45.1, 25.1]],
            2: [[45.1, 25.1], [45.2, 25.2]]  # Connects to end of way 1
        }
        result = process_xml_ways(way_ids, ways_data)
        assert len(result) == 1
        assert len(result[0]) == 3  # Should merge without duplicating junction


class TestCalculateLogoPosition:
    """Tests for the calculate_logo_position function."""
    
    def test_empty_coordinates(self):
        """Should return None for empty coordinates."""
        assert calculate_logo_position([], "right") is None
    
    def test_right_position(self):
        """Should offset to the right (positive longitude)."""
        coords = [[45.0, 25.0], [45.0, 26.0]]  # Horizontal line
        result = calculate_logo_position(coords, "right", offset=0.5)
        assert result[1] > 25.5  # Longitude should be offset right
    
    def test_left_position(self):
        """Should offset to the left (negative longitude)."""
        coords = [[45.0, 25.0], [45.0, 26.0]]
        result = calculate_logo_position(coords, "left", offset=0.5)
        assert result[1] < 25.5  # Longitude should be offset left
    
    def test_top_position(self):
        """Should offset to the top (positive latitude)."""
        coords = [[45.0, 25.0], [45.0, 26.0]]
        result = calculate_logo_position(coords, "top", offset=0.5)
        assert result[0] > 45.0  # Latitude should be offset up
    
    def test_center_position(self):
        """Should return center for unknown position."""
        coords = [[45.0, 25.0], [46.0, 26.0]]
        result = calculate_logo_position(coords, "center")
        assert result[0] == 45.5  # Center latitude
        assert result[1] == 25.5  # Center longitude


class TestCalculateHighwayTotals:
    """Tests for the calculate_highway_totals function."""
    
    def test_empty_data(self):
        """Should return zeros for empty data."""
        result = calculate_highway_totals({})
        assert result['total'] == 0
        assert result['finished'] == 0
    
    def test_single_highway(self):
        """Should correctly sum highway sections."""
        data = {
            "A1": {
                "sections": {
                    "Section 1": {"length": "50 km", "status": "finished"},
                    "Section 2": {"length": "30 km", "status": "in_construction"}
                }
            }
        }
        result = calculate_highway_totals(data)
        assert result['finished'] == 50.0
        assert result['in_construction'] == 30.0
        assert result['total'] == 80.0
    
    def test_multiple_highways(self):
        """Should sum across multiple highways."""
        data = {
            "A1": {"sections": {"S1": {"length": "100 km", "status": "finished"}}},
            "A2": {"sections": {"S1": {"length": "50 km", "status": "finished"}}}
        }
        result = calculate_highway_totals(data)
        assert result['finished'] == 150.0
        assert result['total'] == 150.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
