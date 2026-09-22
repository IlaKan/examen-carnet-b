"""Match a GPX track against the critical-points catalog to guess its zone(s)."""
from .geo_utils import haversine_m


def match_zones(track_points, catalog_points, tolerance_m=60):
    matched = set()
    for tp in track_points:
        t = (tp["lat"], tp["lng"])
        for cp in catalog_points:
            c = (cp["lat"], cp["lng"])
            if haversine_m(t, c) <= tolerance_m:
                matched.add(cp["zona"])
    return sorted(matched)
