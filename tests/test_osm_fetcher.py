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
                "pasos_peatones", "carril_bici", "carril_bus", "rotondas"]:
        assert key in result

def test_fetch_finds_traffic_signals_near_la_campana():
    result = fetch_osm_infrastructure(LA_CAMPANA_BBOX)
    assert result["disponible"] is True
    assert len(result["semaforos"]) > 0

def test_roundabout_query_succeeds_and_has_valid_shape_if_any_found():
    # No se asume que esta bbox concreta tenga una rotonda etiquetada como
    # tal en OSM (la consulta directa para comprobarlo falló hoy por caída
    # temporal de Overpass, y no se va a afirmar un dato de mapa real sin
    # haberlo verificado). Lo que sí se comprueba: la consulta funciona, y
    # si aparece alguna rotonda, tiene la forma de línea esperada.
    result = fetch_osm_infrastructure(LA_CAMPANA_BBOX)
    assert result["disponible"] is True
    for line in result["rotondas"]:
        assert "points" in line
        assert len(line["points"]) >= 2
        assert "lat" in line["points"][0] and "lng" in line["points"][0]

def test_bus_and_bike_lanes_are_line_geometries():
    result = fetch_osm_infrastructure(LA_CAMPANA_BBOX)
    for key in ("carril_bici", "carril_bus"):
        for line in result[key]:
            assert "points" in line
            assert len(line["points"]) >= 2

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
