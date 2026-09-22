import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.lib.track_index import load_index, upsert_track_entry

def test_load_index_missing_file_returns_empty_list():
    assert load_index("/tmp/does-not-exist-index.json") == []

def test_upsert_creates_file_and_adds_entry():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "index.json")
        entry = {"id": "a", "nombre": "Clase A", "fecha": "2026-09-20",
                  "zonas": ["ZONA 2 - PEDRALBES"], "duracion_min": 30}
        upsert_track_entry(path, entry)
        assert load_index(path) == [entry]

def test_upsert_replaces_existing_entry_by_id():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "index.json")
        upsert_track_entry(path, {"id": "a", "nombre": "v1", "fecha": "2026-09-20",
                                    "zonas": [], "duracion_min": 10})
        upsert_track_entry(path, {"id": "a", "nombre": "v2", "fecha": "2026-09-20",
                                    "zonas": [], "duracion_min": 10})
        result = load_index(path)
        assert len(result) == 1
        assert result[0]["nombre"] == "v2"

def test_upsert_sorts_by_fecha_descending():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "index.json")
        upsert_track_entry(path, {"id": "old", "nombre": "old", "fecha": "2026-09-01",
                                    "zonas": [], "duracion_min": 10})
        upsert_track_entry(path, {"id": "new", "nombre": "new", "fecha": "2026-09-22",
                                    "zonas": [], "duracion_min": 10})
        result = load_index(path)
        assert [e["id"] for e in result] == ["new", "old"]
