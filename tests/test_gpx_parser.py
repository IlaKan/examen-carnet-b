import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.gpx_parser import parse_gpx

FIXTURE = os.path.join(
    os.path.dirname(__file__), '..', 'gpx',
    '22-sept-2026-1301 - zona franca .gpx'
)

def test_parse_real_track_point_count():
    result = parse_gpx(FIXTURE)
    assert len(result["points"]) == 1179

def test_parse_real_track_first_point():
    result = parse_gpx(FIXTURE)
    p = result["points"][0]
    assert abs(p["lat"] - 41.35996274593377) < 1e-9
    assert abs(p["lng"] - 2.13273807812838) < 1e-9
    assert p["time"] == "2026-09-22T10:14:11Z"

def test_parse_real_track_duration():
    result = parse_gpx(FIXTURE)
    assert result["start_time"] == "2026-09-22T10:14:11Z"
    assert result["end_time"] == "2026-09-22T11:01:50Z"
    assert abs(result["duration_min"] - 47.65) < 0.1

def test_parse_real_track_no_waypoints():
    # This particular GPX has zero <wpt> elements (confirmed during design).
    result = parse_gpx(FIXTURE)
    assert result["waypoints"] == []

def test_parse_missing_file_raises():
    import pytest
    with pytest.raises(FileNotFoundError):
        parse_gpx("does/not/exist.gpx")
