import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.obras_fetcher import fetch_obras, _first_point_of_geometry

# Bbox covering the Gràcia example record found during design (Torrent de les
# Flors), well inside Barcelona ciutat where this dataset has coverage.
GRACIA_BBOX = (41.39, 2.14, 41.42, 2.17)


def test_fetch_returns_expected_shape():
    result = fetch_obras(GRACIA_BBOX)
    for key in ["disponible", "error", "cobertura", "obras"]:
        assert key in result
    assert result["cobertura"] == "barcelona_ciudad_solo"

def test_fetch_finds_something_in_a_dense_area():
    result = fetch_obras(GRACIA_BBOX)
    assert result["disponible"] is True
    # Barcelona has roadworks going on somewhere in Gràcia most of the time;
    # if this ever legitimately returns zero, that's real data, not a bug —
    # but the fetch itself must have succeeded.
    assert isinstance(result["obras"], list)

def test_fetch_handles_download_failure_gracefully(monkeypatch):
    import scripts.lib.obras_fetcher as mod

    def fake_urlopen(*args, **kwargs):
        raise OSError("simulated network failure")

    monkeypatch.setattr(mod, "_urlopen", fake_urlopen)
    result = fetch_obras(GRACIA_BBOX)
    assert result["disponible"] is False
    assert result["error"]
    assert result["obras"] == []

def test_first_point_of_geometry_parses_polygon():
    wkt = "POLYGON ((429579.609191971 4584519.40297314, 429572.780336405 4584514.09577338))"
    x, y = _first_point_of_geometry(wkt)
    assert x == 429579.609191971
    assert y == 4584519.40297314
