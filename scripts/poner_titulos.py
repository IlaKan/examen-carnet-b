"""Give a title to every class in index.json that doesn't have one yet.

Usage:
    python3 scripts/poner_titulos.py            # only classes without "titulo"
    python3 scripts/poner_titulos.py --rehacer  # recompute all (overwrites hand edits)

To fix a title by hand, edit its "titulo" in public/data/tracks/index.json.
Does not commit or push.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lib.titulo_clase import titular

ROOT = Path(__file__).resolve().parent.parent
TRACKS_DIR = ROOT / "public" / "data" / "tracks"
INDEX_PATH = TRACKS_DIR / "index.json"


def main():
    rehacer = "--rehacer" in sys.argv
    catalog = json.loads((ROOT / "public" / "data" / "points.json").read_text(encoding="utf-8"))
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    tracks = {e["id"]: json.loads((TRACKS_DIR / f"{e['id']}.json").read_text(encoding="utf-8")) for e in index}

    orden = sorted(index, key=lambda e: tracks[e["id"]]["hora_inicio"] or e["fecha"])
    for n, e in enumerate(orden):
        if e.get("titulo") and not rehacer:
            continue
        previos = [tracks[x["id"]] for x in orden[:n]]
        titulos_previos = [x["titulo"] for x in orden[:n] if x.get("titulo")]
        e["titulo"] = titular(tracks[e["id"]], previos, catalog, titulos_previos)
        print(e["titulo"])

    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
