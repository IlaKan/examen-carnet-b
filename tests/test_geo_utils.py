import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.geo_utils import haversine_m, bbox_with_buffer, etrs89_31n_to_wgs84

def test_haversine_known_distance():
    # La Campana (Prefectura) vs a point ~1km south, approx values
    a = (41.3874, 2.1330)
    b = (41.3784, 2.1330)
    d = haversine_m(a, b)
    assert 950 < d < 1050

def test_haversine_zero_distance():
    a = (41.3874, 2.1330)
    assert haversine_m(a, a) == 0

def test_bbox_with_buffer_single_point():
    south, west, north, east = bbox_with_buffer([(41.36, 2.13)], 100)
    assert south < 41.36 < north
    assert west < 2.13 < east
    # 100m buffer should be small in degrees (~0.0009 lat)
    assert (north - south) < 0.01

def test_bbox_with_buffer_multiple_points():
    pts = [(41.35, 2.10), (41.40, 2.15)]
    south, west, north, east = bbox_with_buffer(pts, 50)
    assert south < 41.35 and north > 41.40
    assert west < 2.10 and east > 2.15

def test_etrs89_to_wgs84_known_point():
    # Sample point from the real Open Data Barcelona obras dataset
    # (first record downloaded during design, 2026-09-22): x=429579.609191971, y=4584519.40297314
    # Known to sit in Barcelona's Gràcia district (c. Torrent de les Flors).
    lat, lng = etrs89_31n_to_wgs84(429579.609191971, 4584519.40297314)
    assert 41.39 < lat < 41.42   # Gràcia is north of the city center
    assert 2.14 < lng < 2.17
