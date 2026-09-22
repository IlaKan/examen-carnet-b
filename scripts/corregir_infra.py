"""Add a manual correction (missing/wrong infrastructure) to a track.

Usage:
    python3 scripts/corregir_infra.py
Interactive — asks which track, what kind of element, where, and why.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.track_index import load_index

ROOT = Path(__file__).resolve().parent.parent
TRACKS_DIR = ROOT / "public" / "data" / "tracks"
INDEX_PATH = TRACKS_DIR / "index.json"

TIPOS = ["semaforo", "stop", "ceda", "paso_peatones", "carril_bici", "carril_bus", "obra"]

_MAPS_LATLNG_RE = re.compile(r"[@?]?(-?\d+\.\d+),\s*(-?\d+\.\d+)")


def parse_location(raw):
    """Accepts either 'lat,lng' or a Google Maps URL containing lat,lng."""
    match = _MAPS_LATLNG_RE.search(raw)
    if not match:
        raise ValueError(
            f"No pude leer unas coordenadas de: {raw!r}. "
            "Pega 'lat,lng' o un link de Google Maps que las contenga."
        )
    return float(match.group(1)), float(match.group(2))


def main():
    tracks = load_index(str(INDEX_PATH))
    if not tracks:
        print("No hay ninguna clase todavía. Procesa una con nueva_clase.py primero.")
        sys.exit(1)

    print("Clases disponibles:")
    for t in tracks:
        print(f"  {t['id']}  ({t['fecha']}, {', '.join(t['zonas']) or 'sin zona'})")
    track_id = input("¿Qué clase quieres corregir? (id): ").strip()
    if track_id not in {t["id"] for t in tracks}:
        print("Ese id no está en la lista.")
        sys.exit(1)

    print(f"Tipos válidos: {', '.join(TIPOS)}")
    tipo = input("¿Qué tipo de elemento? ").strip()
    if tipo not in TIPOS:
        print("Tipo no reconocido.")
        sys.exit(1)

    accion = input("¿Lo añades (falta) o lo quitas (está mal en OSM)? [añadir/quitar]: ").strip()
    raw_location = input("Coordenadas ('lat,lng') o link de Google Maps: ").strip()
    lat, lng = parse_location(raw_location)
    nota = input("Nota (opcional): ").strip()

    overrides_path = TRACKS_DIR / f"{track_id}-overrides.json"
    overrides = {"added": [], "removed": []}
    if overrides_path.exists():
        overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

    entry = {"tipo": tipo, "lat": lat, "lng": lng, "nota": nota}
    if accion.startswith("añ") or accion.startswith("a"):
        overrides["added"].append(entry)
    else:
        overrides["removed"].append(entry)

    overrides_path.write_text(json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Guardado. Publicando (git add + commit + push)...")
    subprocess.run(["git", "add", str(overrides_path)], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Correct infra for {track_id}: {accion} {tipo}"],
        cwd=ROOT, check=True,
    )
    subprocess.run(["git", "push"], cwd=ROOT, check=True)
    print("Listo.")


if __name__ == "__main__":
    main()
