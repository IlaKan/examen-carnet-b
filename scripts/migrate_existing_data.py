"""One-off: convert the old data.js/zonas.js into public/data/*.json.

Run once. Safe to re-run — it always overwrites public/data/points.json
and public/data/zones.json from the current data.js/zonas.js.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _extract_js_array(js_path, var_name):
    text = js_path.read_text(encoding="utf-8")
    match = re.search(rf"const {var_name}\s*=\s*(\[.*\]);", text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find `const {var_name} = [...]` in {js_path}")
    return json.loads(match.group(1))


def main():
    points = _extract_js_array(ROOT / "data.js", "DATA")
    zones = _extract_js_array(ROOT / "zonas.js", "ZONAS")

    out_dir = ROOT / "public" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "points.json").write_text(
        json.dumps(points, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "zones.json").write_text(
        json.dumps(zones, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Wrote {len(points)} points to public/data/points.json")
    print(f"Wrote {len(zones)} zones to public/data/zones.json")


if __name__ == "__main__":
    main()
