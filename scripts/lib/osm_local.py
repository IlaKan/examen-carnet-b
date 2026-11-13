"""Traffic infrastructure from a local OpenStreetMap extract, so ingesting a
class doesn't depend on the public Overpass servers (down most of Nov 2026).

Extract: BBBike «Barcelona» (https://download.bbbike.org/osm/bbbike/Barcelona/),
OSM XML gzipped, saved as osm_local/Barcelona.osm.gz (gitignored). Rebuild the
index after downloading a newer extract:
    python3 scripts/lib/osm_local.py
"""
import gzip
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.lib.osm_tags import node_layer, way_layers

ROOT = Path(__file__).resolve().parent.parent.parent
EXTRACT = ROOT / "osm_local" / "Barcelona.osm.gz"
INDEX = ROOT / "osm_local" / "index.json"
LAYERS = ("semaforos", "stops", "cedas", "pasos_peatones", "carril_bici", "carril_bus", "rotondas")
# Every class and the 68 catalog points fall well inside this box.
REGION = (41.30, 1.95, 41.47, 2.25)


def _tags(el):
    return {t.get("k"): t.get("v") for t in el.iter("tag")}


def build_index(extract=EXTRACT, out=INDEX, region=REGION):
    s, w, n, e = region
    layers = {k: [] for k in LAYERS}
    wanted_ways = []  # (layers, node refs)
    needed = set()
    timestamp = None

    # Pass 1: point features (nodes come first) and the ways we want.
    with gzip.open(extract, "rb") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            ts = el.get("timestamp")
            if ts and (timestamp is None or ts > timestamp):
                timestamp = ts  # newest edit = how fresh the extract is
            if el.tag == "node":
                if len(el):
                    layer = node_layer(_tags(el))
                    if layer:
                        lat, lng = float(el.get("lat")), float(el.get("lon"))
                        if s <= lat <= n and w <= lng <= e:
                            layers[layer].append({"lat": lat, "lng": lng})
                el.clear()
            elif el.tag == "way":
                ls = way_layers(_tags(el))
                if ls:
                    refs = [int(nd.get("ref")) for nd in el.iter("nd")]
                    wanted_ways.append((ls, refs))
                    needed.update(refs)
                el.clear()
            elif el.tag == "relation":
                el.clear()

    # Pass 2: coordinates of the nodes those ways use.
    coords = {}
    with gzip.open(extract, "rb") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == "node":
                i = int(el.get("id"))
                if i in needed:
                    coords[i] = (float(el.get("lat")), float(el.get("lon")))
                el.clear()
            elif el.tag == "way":
                break  # all nodes are before the ways in OSM XML

    for ls, refs in wanted_ways:
        pts = [{"lat": coords[r][0], "lng": coords[r][1]} for r in refs if r in coords]
        if len(pts) < 2 or not any(s <= p["lat"] <= n and w <= p["lng"] <= e for p in pts):
            continue
        for layer in ls:
            layers[layer].append({"points": pts})

    data = {"fuente": f"OpenStreetMap, extracto BBBike Barcelona ({extract.name})",
            "fecha_extracto": timestamp, "region": region, **layers}
    out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def _inside(feature, bbox):
    s, w, n, e = bbox
    pts = [feature] if "lat" in feature else feature["points"]
    return any(s <= p["lat"] <= n and w <= p["lng"] <= e for p in pts)


def infra_from_index(bbox, index_path=INDEX):
    """Same shape as osm_fetcher.fetch_osm_infrastructure. None if there's no
    index or the bbox isn't fully inside its region (caller falls back)."""
    if not Path(index_path).exists():
        return None
    data = json.loads(Path(index_path).read_text(encoding="utf-8"))
    rs, rw, rn, re_ = data["region"]
    s, w, n, e = bbox
    if not (rs <= s and rw <= w and rn >= n and re_ >= e):
        return None
    fecha = (data.get("fecha_extracto") or "")[:10]
    return {"disponible": True, "error": None,
            "fuente": f"{data['fuente']}, datos del {fecha}" if fecha else data["fuente"],
            **{k: [f for f in data[k] if _inside(f, bbox)] for k in LAYERS}}


if __name__ == "__main__":
    d = build_index()
    print({k: len(d[k]) for k in LAYERS}, d["fecha_extracto"])
