"""Read/write public/data/tracks/index.json — the lightweight list lista.html loads."""
import json
import os


def load_index(index_path):
    if not os.path.exists(index_path):
        return []
    with open(index_path, encoding="utf-8") as f:
        return json.load(f)


def upsert_track_entry(index_path, entry):
    entries = load_index(index_path)
    entries = [e for e in entries if e["id"] != entry["id"]]
    entries.append(entry)
    entries.sort(key=lambda e: e["fecha"], reverse=True)

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
