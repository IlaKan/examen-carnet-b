"""Ingest a new GPX class recording into the site.

Usage:
    python3 scripts/nueva_clase.py "gpx/mi-clase.gpx"
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.gpx_parser import parse_gpx
from scripts.lib.zone_matcher import match_zones
from scripts.lib.geo_utils import bbox_with_buffer
from scripts.lib.osm_fetcher import fetch_osm_infrastructure
from scripts.lib.obras_fetcher import fetch_obras
from scripts.lib.track_index import upsert_track_entry

ROOT = Path(__file__).resolve().parent.parent
TRACKS_DIR = ROOT / "public" / "data" / "tracks"
POINTS_PATH = ROOT / "public" / "data" / "points.json"
INDEX_PATH = TRACKS_DIR / "index.json"


def slugify(gpx_path, date_str):
    base = Path(gpx_path).stem
    base = base.strip().lower().replace(" ", "-").replace("--", "-")
    return f"{date_str}-{base}"[:80]


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 scripts/nueva_clase.py <ruta-al-gpx>")
        sys.exit(1)

    gpx_path = sys.argv[1]
    parsed = parse_gpx(gpx_path)
    date_str = parsed["start_time"][:10] if parsed["start_time"] else "sin-fecha"

    track_id = slugify(gpx_path, date_str)
    print(f"Procesando {gpx_path} como '{track_id}'...")

    catalog = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    zonas = match_zones(parsed["points"], catalog)
    if not zonas:
        nombre_manual = input(
            "Esta clase no coincide con ninguna zona del catálogo (60m). "
            "¿Cómo la llamas? (ej. 'zona franca'): "
        ).strip()
        zonas = [nombre_manual] if nombre_manual else ["sin clasificar"]
        print(f"Zona registrada manualmente: {zonas}")
    else:
        print(f"Zona(s) detectada(s) automáticamente: {zonas}")

    latlngs = [(p["lat"], p["lng"]) for p in parsed["points"]]
    bbox = bbox_with_buffer(latlngs, buffer_m=150)

    print("Consultando OpenStreetMap (semáforos, stops, cedas, pasos, carriles)...")
    osm_data = fetch_osm_infrastructure(bbox)
    if not osm_data["disponible"]:
        print(f"  Aviso: no se pudo obtener infraestructura OSM ({osm_data['error']}). "
              "Se guarda la clase igual, marcada como no disponible.")

    print("Consultando Open Data Barcelona (obras)...")
    obras_data = fetch_obras(bbox)
    if not obras_data["disponible"]:
        print(f"  Aviso: no se pudo obtener el dataset de obras ({obras_data['error']}). "
              "Se guarda la clase igual, marcada como no disponible.")

    TRACKS_DIR.mkdir(parents=True, exist_ok=True)

    track_data = {
        "id": track_id,
        "nombre": Path(gpx_path).stem,
        "conductor": "Ilaria",
        "fecha": date_str,
        "hora_inicio": parsed["start_time"],
        "hora_fin": parsed["end_time"],
        "duracion_min": round(parsed["duration_min"], 2) if parsed["duration_min"] else None,
        "zonas": zonas,
        "fuente": "Open GPX Tracker (iOS), export propio",
        "points": parsed["points"],
        "waypoints_manuales": parsed["waypoints"],
    }
    (TRACKS_DIR / f"{track_id}.json").write_text(
        json.dumps(track_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (TRACKS_DIR / f"{track_id}-osm.json").write_text(
        json.dumps(osm_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (TRACKS_DIR / f"{track_id}-obras.json").write_text(
        json.dumps(obras_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    upsert_track_entry(str(INDEX_PATH), {
        "id": track_id,
        "nombre": track_data["nombre"],
        "fecha": date_str,
        "zonas": zonas,
        "duracion_min": track_data["duracion_min"],
    })

    print("Archivos escritos. Publicando (git add + commit + push)...")
    subprocess.run(["git", "add", "public/data"], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Add class {track_id}"], cwd=ROOT, check=True
    )
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print(f"Listo. '{track_id}' publicado.")


if __name__ == "__main__":
    main()
