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

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

_EMPTY_LAYERS = {
    "semaforos": [], "stops": [], "cedas": [],
    "pasos_peatones": [], "carril_bici": [], "carril_bus": [],
}

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
  way["highway"="cycleway"]({bbox_str});
  way["cycleway"]({bbox_str});
  way["busway"]({bbox_str});
  way["lanes:bus"]({bbox_str});
);
out center;
"""


def fetch_osm_infrastructure(bbox, retries=3, retry_wait_s=5):
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
            point = {"lat": el["lat"], "lng": el["lon"]}
        else:  # way -> use its computed center
            center = el.get("center")
            if not center:
                continue
            point = {"lat": center["lat"], "lng": center["lon"]}

        if tags.get("highway") == "traffic_signals":
            result["semaforos"].append(point)
        elif tags.get("highway") == "stop":
            result["stops"].append(point)
        elif tags.get("highway") == "give_way":
            result["cedas"].append(point)
        elif tags.get("highway") == "crossing":
            result["pasos_peatones"].append(point)
        elif tags.get("highway") == "cycleway" or "cycleway" in tags:
            result["carril_bici"].append(point)
        elif "busway" in tags or "lanes:bus" in tags:
            result["carril_bus"].append(point)

    return result
