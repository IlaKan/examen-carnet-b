"""Parse Open GPX Tracker .gpx files into plain dicts."""
import os
import xml.etree.ElementTree as ET
from datetime import datetime

_NS = {"g": "http://www.topografix.com/GPX/1/1"}


def _parse_time(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")


def parse_gpx(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"GPX file not found: {path}")

    tree = ET.parse(path)
    root = tree.getroot()

    points = []
    for trkpt in root.findall(".//g:trkpt", _NS):
        time_el = trkpt.find("g:time", _NS)
        points.append({
            "lat": float(trkpt.get("lat")),
            "lng": float(trkpt.get("lon")),
            "time": time_el.text if time_el is not None else None,
        })

    waypoints = []
    for wpt in root.findall(".//g:wpt", _NS):
        name_el = wpt.find("g:name", _NS)
        time_el = wpt.find("g:time", _NS)
        waypoints.append({
            "lat": float(wpt.get("lat")),
            "lng": float(wpt.get("lon")),
            "name": name_el.text if name_el is not None else "",
            "time": time_el.text if time_el is not None else None,
        })

    start_time = points[0]["time"] if points else None
    end_time = points[-1]["time"] if points else None
    duration_min = None
    if start_time and end_time:
        duration_min = (_parse_time(end_time) - _parse_time(start_time)).total_seconds() / 60

    return {
        "points": points,
        "waypoints": waypoints,
        "start_time": start_time,
        "end_time": end_time,
        "duration_min": duration_min,
    }
