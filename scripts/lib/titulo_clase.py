"""Human title for a class: "6 nov · Les Corts · Túnel Esplugues (+2)".

The last part is what that class added: the first critical point crossed there
for the first time ever (stable over time, unlike "least repeated"). Classes
with no new catalog point (e.g. Zona Franca, which has no catalog) fall back to
the street driven for the longest, via OpenStreetMap Nominatim reverse geocoding.

"Crossed" uses the same rule as public/cobertura.html: a track segment within
60 m of the point, ignoring GPS jumps faster than 40 m/s.
"""
import json
import math
import re
import time
import urllib.request
from collections import Counter
from datetime import datetime

TOLERANCIA_M = 60
VEL_MAX_MS = 40
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
ZONA_CORTA = [  # orden en que aparecen en el título
    ("PEDRALBES", "Les Corts"), ("UNIVERSIT", "Les Corts"), ("POBLE SEC", "Poble Sec"),
    ("MONTJ", "Montjuïc"), ("MAQUINISTA", "La Maquinista"), ("ZONA FRANCA", "Zona Franca"),
]
# "Salida desde zona 2 (2)", "Llegada a zona 2"…: dicen poco de la clase, solo si no hay otro
GENERICO = re.compile(r"zona \d", re.I)


def _dist_tramo(p, a, b):
    k = math.cos(math.radians(p["lat"])) * 111320
    ax, ay = (a["lng"] - p["lng"]) * k, (a["lat"] - p["lat"]) * 110540
    bx, by = (b["lng"] - p["lng"]) * k, (b["lat"] - p["lat"]) * 110540
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = max(0, min(1, -(ax * dx + ay * dy) / L)) if L else 0
    return math.hypot(ax + t * dx, ay + t * dy)


def _segundos(a, b):
    f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (f(b["time"]) - f(a["time"])).total_seconds()


def puntos_cruzados(points, catalog):
    """Catalog indices crossed by the track, in route order."""
    vistos = {}
    for j in range(len(points) - 1):
        a, b = points[j], points[j + 1]
        largo = _dist_tramo(a, b, b)
        dt = _segundos(a, b)
        if (largo / dt > VEL_MAX_MS) if dt > 0 else largo > TOLERANCIA_M:
            continue
        for i, p in enumerate(catalog):
            if i not in vistos and abs(a["lat"] - p["lat"]) < 0.003 and _dist_tramo(p, a, b) <= TOLERANCIA_M:
                vistos[i] = j
    return sorted(vistos, key=vistos.get)


def nombre_punto(nombre):
    return re.sub(r"^Z\d+\s*-\s*[\d.]+\s*", "", nombre).strip().rstrip(".")


def zona_corta(zonas):
    out = []
    for clave, corto in ZONA_CORTA:
        if any(clave in z.upper() for z in zonas) and corto not in out:
            out.append(corto)
    return " + ".join(out) or (zonas[0] if zonas else "sin zona")


def fecha_corta(fecha_iso):
    y, m, d = fecha_iso.split("-")
    return f"{int(d)} {MESES[int(m) - 1]}"


def nominatim_calle(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=17&lat={lat}&lon={lng}"
    req = urllib.request.Request(url, headers={"User-Agent": "tupilotob-carnet-b/1.0 (uso personal)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("address", {}).get("road")


def calles_por_tiempo(points, reverse_fn=nominatim_calle, cada_s=60, pausa_s=1.1):
    """Streets ordered by time spent, sampling one point every `cada_s` seconds.
    Nominatim allows 1 request/second, hence the pause."""
    cuenta, ultimo = Counter(), None
    for p in points:
        if ultimo is not None and _segundos(ultimo, p) < cada_s:
            continue
        ultimo = p
        try:
            calle = reverse_fn(p["lat"], p["lng"])
        except Exception:
            calle = None
        if calle:
            cuenta[calle] += 1
        if pausa_s:
            time.sleep(pausa_s)
    return [c for c, _ in cuenta.most_common()]


def titulo(fecha_iso, zonas, nuevos, catalog, calles=(), calles_usadas=()):
    """nuevos: catalog indices crossed for the first time, in route order."""
    base = f"{fecha_corta(fecha_iso)} · {zona_corta(zonas)}"
    if nuevos:
        utiles = [i for i in nuevos if not GENERICO.search(catalog[i]["nombre"])] or nuevos
        extra = f" (+{len(nuevos) - 1})" if len(nuevos) > 1 else ""
        return f"{base} · {nombre_punto(catalog[utiles[0]]['nombre'])}{extra}"
    calle = next((c for c in calles if c not in calles_usadas), None)
    return f"{base} · {calle}" if calle else base


def titular(track, tracks_previos, catalog, titulos_previos=(), reverse_fn=nominatim_calle):
    """Title for `track` given the classes recorded before it (full track dicts)."""
    vistos = {i for t in tracks_previos for i in puntos_cruzados(t["points"], catalog)}
    nuevos = [i for i in puntos_cruzados(track["points"], catalog) if i not in vistos]
    calles = [] if nuevos else calles_por_tiempo(track["points"], reverse_fn)
    usadas = {calle_de_titulo(t) for t in titulos_previos}
    return titulo(track["fecha"], track["zonas"], nuevos, catalog, calles, usadas)


def calle_de_titulo(t):
    """Street part of a fallback title, so later classes don't repeat it."""
    return t.split(" · ")[2] if t.count(" · ") >= 2 else None
