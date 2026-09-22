"""Collect zone names already used across recorded classes, to suggest instead
of re-typing a colloquial zone name (e.g. "zona franca") slightly differently
each time, which would otherwise fragment the zone filter in lista.html.
"""


def collect_known_zones(index_entries):
    zonas = set()
    for entry in index_entries:
        zonas.update(entry.get("zonas", []))
    return sorted(zonas)
