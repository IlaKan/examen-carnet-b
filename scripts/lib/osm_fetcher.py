"""Fetch traffic infrastructure from OpenStreetMap via the Overpass API.

Free, no token required. One request per track, cached to a file by the
caller — never fetched live while reviewing a route.
"""
import json
import ssl
import time
import urllib.request
import urllib.parse

import certifi

from scripts.lib.osm_tags import node_layer, way_layers
from scripts.lib.osm_local import infra_from_index

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# semaforos/stops/cedas/pasos_peatones son puntos (nodos OSM). carril_bici/
# carril_bus/rotondas son LÍNEAS/formas (vías OSM) — un carril bus no es un
# punto, es un tramo entero que hay que ver dibujado para saber por dónde
# no meterse, así que se guardan como geometría completa, no un centro.
_POINT_LAYERS = ("semaforos", "stops", "cedas", "pasos_peatones")
_LINE_LAYERS = ("carril_bici", "carril_bus", "rotondas")
_EMPTY_LAYERS = {k: [] for k in _POINT_LAYERS + _LINE_LAYERS}

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _urlopen(request, timeout):
    return urllib.request.urlopen(request, timeout=timeout, context=_SSL_CONTEXT)


def _build_query(bbox):
    south, west, north, east = bbox
    bbox_str = f"{south},{west},{north},{east}"
    return f"""
[out:json][timeout:25];
(
  node["highway"="traffic_signals"]({bbox_str});
  node["highway"="stop"]({bbox_str});
  node["highway"="give_way"]({bbox_str});
  node["highway"="crossing"]({bbox_str});
  way["highway"~"^(cycleway|busway)$"]({bbox_str});
  way[~"^cycleway(:left|:right|:both)?$"~"^(lane|track|opposite_lane|opposite_track|share_busway|shared_busway)$"]({bbox_str});
  way[~"^(busway|busway:.*|lanes:bus.*|lanes:psv.*|bus:lanes.*|psv:lanes.*)$"~"."]({bbox_str});
  way["junction"~"^(roundabout|circular)$"]({bbox_str});
);
out geom;
"""


def fetch_osm_infrastructure(bbox, retries=3, retry_wait_s=5, use_local=True):
    # Local extract first (scripts/lib/osm_local.py): no dependency on the
    # public Overpass servers, which were down most of Nov 2026.
    if use_local:
        local = infra_from_index(bbox)
        if local is not None:
            return local
    query = _build_query(bbox)
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")

    payload = None
    last_error = None
    for attempt in range(retries):
        request = urllib.request.Request(OVERPASS_URL, data=data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "examen-carnet-b/1.0 (personal driving-practice route mapper)",
        })
        try:
            with _urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except Exception as exc:  # network error, timeout, 504 (server busy), etc.
            last_error = exc
            if attempt < retries - 1:
                time.sleep(retry_wait_s)

    if payload is None:
        return {"disponible": False, "error": str(last_error), **_EMPTY_LAYERS}

    result = {"disponible": True, "error": None, **{k: [] for k in _EMPTY_LAYERS}}

    for el in payload.get("elements", []):
        tags = el.get("tags", {})

        if el["type"] == "node":
            layer = node_layer(tags)
            if layer:
                result[layer].append({"lat": el["lat"], "lng": el["lon"]})
            continue

        # way: geometría completa (lista de puntos), no solo el centro —
        # para carril_bici/carril_bus/rotondas necesitamos la forma real.
        geometry = el.get("geometry")
        if not geometry:
            continue
        line = {"points": [{"lat": g["lat"], "lng": g["lon"]} for g in geometry]}
        for layer in way_layers(tags):
            result[layer].append(line)

    return result
