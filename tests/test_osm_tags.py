import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.osm_tags import way_layers, node_layer


def test_barcelona_bus_lane_tags():
    assert way_layers({"highway": "primary", "psv:lanes": "yes|yes|designated"}) == ["carril_bus"]
    assert way_layers({"highway": "primary", "busway:right": "lane"}) == ["carril_bus"]
    assert way_layers({"highway": "primary", "lanes:psv": "1"}) == ["carril_bus"]
    assert way_layers({"highway": "primary", "busway": "lane"}) == ["carril_bus"]
    assert way_layers({"highway": "primary", "cycleway:right": "share_busway"}) == ["carril_bici", "carril_bus"]
    assert way_layers({"highway": "primary", "cycleway": "lane", "psv:lanes": "designated|yes"}) == ["carril_bici", "carril_bus"]


def test_tags_that_mean_no_bike_lane():
    assert way_layers({"highway": "residential", "cycleway": "no"}) == []
    assert way_layers({"highway": "footway", "cycleway": "crossing"}) == []
    assert way_layers({"highway": "residential", "cycleway": "shared_lane"}) == []
    assert way_layers({"highway": "primary", "cycleway:both": "no", "lanes:psv": "0"}) == []


def test_other_layers():
    assert way_layers({"highway": "cycleway"}) == ["carril_bici"]
    assert way_layers({"highway": "primary", "junction": "roundabout"}) == ["rotondas"]
    assert node_layer({"highway": "traffic_signals"}) == "semaforos"
