"""Shared street heights and constrained polygon tessellation (metres, X/Z)."""
import math
import numpy as np
import mapbox_earcut
from shapely.geometry import Polygon, box

ROAD_Y = .135  # Previous .035 m surface, raised by exactly 10 cm.
WALK_Y = .280
BED_Y = .240
SLAB_BOTTOM = -.080  # Buried below the -.020 m terrain plane.


def street_y(height):
    # Preserve all elevated bridge/door landings; fade the ground lift out over
    # the first half metre of an approach's rise instead of adding a seam.
    return .035 + height + .1 * max(0, 1 - max(0, height) / .5)


def polygons(geometry):
    if geometry.is_empty:
        return
    if geometry.geom_type == 'Polygon':
        yield geometry
    else:
        for child in getattr(geometry, 'geoms', []):
            yield from polygons(child)


def triangles(polygon):
    """Earcut respects concave boundaries and holes. Filtering unconstrained
    Delaunay triangles by containment leaves large missing pavement wedges.
    Do not simplify individual tiles: that opens cracks along shared edges.
    """
    rings = [list(r.coords)[:-1] for r in [polygon.exterior, *polygon.interiors]]
    vertices = np.array([v for ring in rings for v in ring], dtype=np.float64)
    ends = np.cumsum([len(r) for r in rings], dtype=np.uint32)
    indices = mapbox_earcut.triangulate_float64(vertices, ends)
    for i in range(0, len(indices), 3):
        points = vertices[indices[i:i+3]]
        a, b = points[1] - points[0], points[2] - points[0]
        if a[0]*b[1] - a[1]*b[0] < 0:
            points = points[::-1]
        yield Polygon(points)


def tiles(geometry, size=160):
    for p in polygons(geometry):
        x0, z0, x1, z1 = p.bounds
        for x in range(math.floor(x0/size), math.floor(x1/size)+1):
            for z in range(math.floor(z0/size), math.floor(z1/size)+1):
                yield from polygons(p.intersection(box(x*size, z*size, (x+1)*size, (z+1)*size)))
