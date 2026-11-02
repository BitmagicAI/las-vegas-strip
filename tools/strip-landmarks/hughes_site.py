"""Existing road/sidewalk keepouts for Hughes amenities, in game X/Z metres."""
import json
from functools import lru_cache
from shapely.geometry import shape, box
from shapely.ops import unary_union

@lru_cache(maxsize=1)
def roads():
    region = box(1100, -400, 1650, 100)
    surfaces = json.load(open('build/geographic-strip/surface-layers.geojson'))
    polygons = []
    for feature in surfaces['features']:
        if feature['properties']['kind'] not in ('road', 'sidewalk'):
            continue
        geometry = shape(feature['geometry'])
        if geometry.intersects(region):
            polygons.append(geometry.intersection(region).buffer(.3))
    return unary_union(polygons)
