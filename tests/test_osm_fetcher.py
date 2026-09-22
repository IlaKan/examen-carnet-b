import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.osm_fetcher import fetch_osm_infrastructure

# Small bbox around La Campana / Magòria (Prefectura de Trànsit), where we know
# from the live map (2026-09-22) that there's at least one traffic-signal-heavy
# roundabout with a bus lane feeding it.
LA_CAMPANA_BBOX = (41.3595, 2.1290, 41.3630, 2.1340)


def test_fetch_returns_expected_shape():
    result = fetch_osm_infrastructure(LA_CAMPANA_BBOX)
    for key in ["disponible", "error", "semaforos", "stops", "cedas",
                "pasos_peatones", "carril_bici", "carril_bus"]:
        assert key in result

def test_fetch_finds_traffic_signals_near_la_campana():
    result = fetch_osm_infrastructure(LA_CAMPANA_BBOX)
    assert result["disponible"] is True
    assert len(result["semaforos"]) > 0

def test_fetch_handles_unreachable_host_gracefully(monkeypatch):
    import scripts.lib.osm_fetcher as mod

    def fake_urlopen(*args, **kwargs):
        raise OSError("simulated network failure")

    monkeypatch.setattr(mod, "_urlopen", fake_urlopen)
    monkeypatch.setattr(mod.time, "sleep", lambda seconds: None)  # skip real waiting
    result = fetch_osm_infrastructure(LA_CAMPANA_BBOX)
    assert result["disponible"] is False
    assert result["error"]
    assert result["semaforos"] == []
