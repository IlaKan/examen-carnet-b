"""Fetch active/recent roadworks from Open Data Barcelona.

Dataset: "Obres a l'espai públic de la ciutat de Barcelona" — free, no
token, updated daily. Coverage is Barcelona city only (confirmed during
design, 2026-09-22); l'Hospitalet de Llobregat and other municipalities
are NOT covered by this dataset.
"""
import json
import re
import ssl
import urllib.request

import certifi

from .geo_utils import etrs89_31n_to_wgs84

OBRAS_JSON_URL = (
    "https://opendata-ajuntament.barcelona.cat/data/dataset/"
    "fd9f355f-2160-4f89-96a1-6ece3924e3bd/resource/"
    "089bcf9e-140e-4ea3-bf93-03c6260ba0f5/download"
)

_POINT_RE = re.compile(r"(-?\d+\.?\d*)\s+(-?\d+\.?\d*)")
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _urlopen(request, timeout):
    return urllib.request.urlopen(request, timeout=timeout, context=_SSL_CONTEXT)


def _first_point_of_geometry(wkt):
    """Extract the first (x, y) pair from a WKT POLYGON/LINESTRING string."""
    match = _POINT_RE.search(wkt)
    if not match:
        raise ValueError(f"No coordinate pair found in geometry: {wkt!r}")
    return float(match.group(1)), float(match.group(2))


def fetch_obras(bbox):
    south, west, north, east = bbox
    request = urllib.request.Request(OBRAS_JSON_URL, headers={
        "User-Agent": "examen-carnet-b/1.0 (personal driving-practice route mapper)",
    })

    try:
        with _urlopen(request, timeout=60) as response:
            records = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        return {
            "disponible": False, "error": str(exc),
            "cobertura": "barcelona_ciudad_solo", "obras": [],
        }

    obras = []
    for rec in records:
        geom = rec.get("geometria_etrs89")
        if not geom:
            continue
        try:
            x, y = _first_point_of_geometry(geom)
            lat, lng = etrs89_31n_to_wgs84(x, y)
        except (ValueError, Exception):
            continue
        if south <= lat <= north and west <= lng <= east:
            obras.append({
                "lat": lat, "lng": lng,
                "titol": rec.get("titol", ""),
                "estat": rec.get("estat", ""),
                "data_inici": rec.get("data_inici"),
                "data_fi": rec.get("data_fi"),
            })

    return {
        "disponible": True, "error": None,
        "cobertura": "barcelona_ciudad_solo", "obras": obras,
    }
