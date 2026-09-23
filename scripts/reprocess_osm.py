"""One-off: re-fetch OSM infrastructure for an existing track (e.g. after
Overpass was down when it was first ingested), overwriting its -osm.json.

Usage:
    python3 scripts/reprocess_osm.py <track-id>
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.geo_utils import bbox_with_buffer
from scripts.lib.osm_fetcher import fetch_osm_infrastructure

ROOT = Path(__file__).resolve().parent.parent
TRACKS_DIR = ROOT / "public" / "data" / "tracks"


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 scripts/reprocess_osm.py <track-id>")
        sys.exit(1)

    track_id = sys.argv[1]
    track_path = TRACKS_DIR / f"{track_id}.json"
    if not track_path.exists():
        print(f"No existe {track_path}")
        sys.exit(1)

    track = json.loads(track_path.read_text(encoding="utf-8"))
    latlngs = [(p["lat"], p["lng"]) for p in track["points"]]
    bbox = bbox_with_buffer(latlngs, buffer_m=150)

    print(f"Reprocesando infraestructura OSM para '{track_id}'...")
    osm_data = fetch_osm_infrastructure(bbox)
    if not osm_data["disponible"]:
        print(f"Sigue sin estar disponible: {osm_data['error']}")
        sys.exit(1)

    osm_path = TRACKS_DIR / f"{track_id}-osm.json"
    osm_path.write_text(json.dumps(osm_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Listo: {len(osm_data['semaforos'])} semáforos, {len(osm_data['stops'])} stops, "
        f"{len(osm_data['cedas'])} cedas, {len(osm_data['pasos_peatones'])} pasos, "
        f"{len(osm_data['carril_bici'])} tramos de carril bici, "
        f"{len(osm_data['carril_bus'])} tramos de carril bus, "
        f"{len(osm_data['rotondas'])} rotondas."
    )

    subprocess.run(["git", "add", str(osm_path)], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Reprocess OSM infrastructure for {track_id} (roundabouts/lanes as line geometry)"],
        cwd=ROOT, check=True,
    )
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print("Publicado.")


if __name__ == "__main__":
    main()
