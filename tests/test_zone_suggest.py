import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.zone_suggest import collect_known_zones

def test_collect_known_zones_dedupes_and_sorts():
    entries = [
        {"zonas": ["zona franca"]},
        {"zonas": ["ZONA 2 - PEDRALBES"]},
        {"zonas": ["zona franca"]},  # duplicate
    ]
    assert collect_known_zones(entries) == ["ZONA 2 - PEDRALBES", "zona franca"]

def test_collect_known_zones_handles_missing_key():
    entries = [{"id": "a"}, {"zonas": ["zona franca"]}]
    assert collect_known_zones(entries) == ["zona franca"]

def test_collect_known_zones_empty_list():
    assert collect_known_zones([]) == []
