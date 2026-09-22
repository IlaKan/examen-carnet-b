import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.zone_matcher import match_zones

CATALOG = [
    {"lat": 41.387829, "lng": 2.12181, "zona": "ZONA 2 - PEDRALBES"},
    {"lat": 41.382773, "lng": 2.119321, "zona": "ZONA 3 - Z. UNIVERSIT."},
]

def test_match_exact_coincidence():
    track = [{"lat": 41.387829, "lng": 2.12181}]
    assert match_zones(track, CATALOG) == ["ZONA 2 - PEDRALBES"]

def test_match_within_tolerance():
    # ~30m north of the Zona 2 catalog point
    track = [{"lat": 41.388100, "lng": 2.12181}]
    assert match_zones(track, CATALOG, tolerance_m=60) == ["ZONA 2 - PEDRALBES"]

def test_no_match_far_away():
    # The real "zona franca" track's start point, ~2km from either catalog point
    track = [{"lat": 41.35996274593377, "lng": 2.13273807812838}]
    assert match_zones(track, CATALOG, tolerance_m=60) == []

def test_match_multiple_zones_sorted_unique():
    track = [
        {"lat": 41.387829, "lng": 2.12181},
        {"lat": 41.382773, "lng": 2.119321},
        {"lat": 41.387829, "lng": 2.12181},  # duplicate, must not duplicate output
    ]
    assert match_zones(track, CATALOG) == ["ZONA 2 - PEDRALBES", "ZONA 3 - Z. UNIVERSIT."]

def test_empty_track_returns_empty():
    assert match_zones([], CATALOG) == []
