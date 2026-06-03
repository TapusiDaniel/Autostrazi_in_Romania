"""Unit tests for timeline payload generation."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.timeline_builder import build_timeline_payload
from config import TIMELINE_PRESENT_YEAR


def test_current_state_total_uses_finished_status():
    highways = {
        "A0": {
            "sections": {
                "Old section": {
                    "status": "finished",
                    "completion_date": "2025",
                    "length": "10 km",
                },
                "Current section": {
                    "status": "finished",
                    "completion_date": str(TIMELINE_PRESENT_YEAR),
                    "length": "4.47 km",
                },
                "Projected section": {
                    "status": "in_construction",
                    "completion_date": str(TIMELINE_PRESENT_YEAR),
                    "length": "17.5 km",
                },
            }
        }
    }

    payload, current_state_total = build_timeline_payload(highways)

    assert payload["presentYear"] == TIMELINE_PRESENT_YEAR
    assert current_state_total == 14.47
    assert payload["timelineData"][TIMELINE_PRESENT_YEAR] == 31.97
