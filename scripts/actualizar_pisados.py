"""Write public/data/pisados.json: for each critical point crossed, the dates
of the classes that crossed it ({"<nombre>": ["2026-10-30", ...]}).

Usage:
    python3 scripts/actualizar_pisados.py

Same rule as public/cobertura.html (60 m, GPS jumps ignored). nueva_clase.py
calls it, so it stays current with every new class. Lets puntos.html know
what's missing without downloading every track to the phone.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.titulo_clase import puntos_cruzados

DATA = Path(__file__).resolve().parent.parent / "public" / "data"


def actualizar():
    catalog = json.loads((DATA / "points.json").read_text(encoding="utf-8"))
    index = json.loads((DATA / "tracks" / "index.json").read_text(encoding="utf-8"))
    pisados = {}
    for e in sorted(index, key=lambda e: e["fecha"]):
        t = json.loads((DATA / "tracks" / f"{e['id']}.json").read_text(encoding="utf-8"))
        for i in puntos_cruzados(t["points"], catalog):
            pisados.setdefault(catalog[i]["nombre"], []).append(e["fecha"])
    (DATA / "pisados.json").write_text(json.dumps(pisados, ensure_ascii=False, indent=2), encoding="utf-8")
    return pisados


if __name__ == "__main__":
    print(f"{len(actualizar())} puntos pisados")
