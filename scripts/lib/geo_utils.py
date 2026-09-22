"""Geo helpers: distance, bounding boxes, and one coordinate system conversion."""
import math
from pyproj import Transformer

_ETRS89_31N_TO_WGS84 = Transformer.from_crs("EPSG:25831", "EPSG:4326", always_xy=True)


def haversine_m(a, b):
    """Great-circle distance in meters between (lat, lng) tuples a and b."""
    lat1, lng1 = a
    lat2, lng2 = b
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def bbox_with_buffer(points, buffer_m):
    """Bounding box (south, west, north, east) around `points`, expanded by buffer_m meters."""
    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]
    south, north = min(lats), max(lats)
    west, east = min(lngs), max(lngs)
    # Rough meters-per-degree at this latitude; good enough for a padding buffer.
    mid_lat = (south + north) / 2
    m_per_deg_lat = 111320
    m_per_deg_lng = 111320 * math.cos(math.radians(mid_lat))
    dlat = buffer_m / m_per_deg_lat
    dlng = buffer_m / m_per_deg_lng if m_per_deg_lng > 0 else buffer_m / 111320
    return (south - dlat, west - dlng, north + dlat, east + dlng)


def etrs89_31n_to_wgs84(x, y):
    """Convert ETRS89 / UTM zone 31N (EPSG:25831) coordinates, as used by Open Data
    Barcelona's `geometria_etrs89` fields, to (lat, lng) in WGS84."""
    lng, lat = _ETRS89_31N_TO_WGS84.transform(x, y)
    return (lat, lng)
