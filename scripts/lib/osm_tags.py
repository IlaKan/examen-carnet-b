"""Which OSM features count as each map layer. Shared by the Overpass fetcher
and the local extract index, so both classify exactly the same way.

Checked against the BBBike Barcelona extract (2026-11-08): bus lanes here are
mostly tagged psv:lanes=...designated / lanes:psv / busway:right=lane, not
busway / lanes:bus; and most «cycleway» keys say there is NO lane (no,
crossing, shared_lane pictogram, asl), so only real lane values count.
"""

NODE_LAYERS = {
    "traffic_signals": "semaforos",
    "stop": "stops",
    "give_way": "cedas",
    "crossing": "pasos_peatones",
}

_BUS_LANE = {"lane", "opposite_lane"}
_BIKE_LANE = {"lane", "track", "opposite_lane", "opposite_track", "share_busway", "shared_busway"}
_SHARED_BUS = {"share_busway", "shared_busway"}  # bus lane that bikes may use
_SIDES = ("", ":left", ":right", ":both")


def node_layer(tags):
    return NODE_LAYERS.get(tags.get("highway"))


def _positive_int(v):
    try:
        return int(v) > 0
    except (TypeError, ValueError):
        return False


def is_bus_lane(tags):
    if tags.get("highway") == "busway":
        return True
    if any(tags.get("cycleway" + s) in _SHARED_BUS for s in _SIDES):
        return True
    for k, v in tags.items():
        if (k == "busway" or k.startswith("busway:")) and v in _BUS_LANE:
            return True
        if (k.startswith("lanes:bus") or k.startswith("lanes:psv")) and _positive_int(v):
            return True
        if (k.startswith("bus:lanes") or k.startswith("psv:lanes")) and "designated" in v.split("|"):
            return True
    return False


def is_bike_lane(tags):
    if tags.get("highway") == "cycleway":
        return True
    return any(tags.get("cycleway" + s) in _BIKE_LANE for s in _SIDES)


def way_layers(tags):
    """A way can be in several layers (e.g. Diagonal: bike lane AND bus lane)."""
    layers = []
    if tags.get("junction") in ("roundabout", "circular"):
        layers.append("rotondas")
    if is_bike_lane(tags):
        layers.append("carril_bici")
    if is_bus_lane(tags):
        layers.append("carril_bus")
    return layers

