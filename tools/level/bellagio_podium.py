"""Shared Bellagio podium portals and doorway-aware wall finishes."""
import math

PODIUM_DOORS = [
    ('south_entrance', (-155, 0, -76), 0, 6, 4.5),
    ('north_gallery_exit', (-131, 0, 34), math.pi / 2, 5, 4.5),
    ('lobby_service', (-191, 0, -58), math.pi / 2, 3.4, 3.2),
    ('casino_service', (-191, 0, 12), math.pi / 2, 3.4, 3.2),
]


def wall_moulding_spans(x, height, start=-75.5, end=41.5):
    """Z spans for the side-wall trim; leave 10 cm beyond each door jamb."""
    spans = [(start, end)]
    for _, position, yaw, width, top in PODIUM_DOORS:
        if abs(x-position[0]) > 1 or abs(math.sin(yaw)) < .9 or height-.08 >= top:
            continue
        lo, hi = position[2]-width/2-.10, position[2]+width/2+.10
        spans = [(a, b) for left, right in spans
                 for a, b in [(left, min(right, lo)), (max(left, hi), right)] if b-a > .001]
    return spans
