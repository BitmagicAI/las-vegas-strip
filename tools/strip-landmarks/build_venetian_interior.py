"""Build the Venetian's public interiors (2026-10-23) without the rest of build.py.

  "$(uv python find 3.12)" tools/strip-landmarks/build_venetian_interior.py [lobby] [casino] [shoppes] [sample]

Modules (each owns one streamed sub-venue; see venetian_interior_plan.py for the layout):
  lobby    venetian_lobby.py    -> key 'venetian' (its interior: Great Hall, Scenic Overlook, Rialto landing, arrivals,
                                   colonnade, rotunda, front desk)
  casino   venetian_casino.py   -> key 'venetianCasino' (casino floor, Restaurant Row)
  shoppes  venetian_shoppes.py  -> key 'grandCanal' (Level 2: canal, streets, St Mark's Square, east terrace link)
  sample   venetian_kit_sample.py -> key 'vikit', written to build/venetian-interiors/kit/ only (a kit test scene)

Each module defines build(B) -> list of venue dicts (key, name, bounds, portals, zones, accessPoints, levelY,
preloadDistance, views, routes); lights come from B.lights. This script writes <key>-interior.json and
<key>-interior-collision.json (and a tiny anchor exterior for new sub-venues), then merges the venue entries into
build/strip-landmarks/venues.json: a new key is inserted after 'venetian'; for 'venetian' itself only the interior-owned
fields are replaced and the exterior's views are kept. Then export with
  blender -b --python tools/strip-landmarks/export.py -- venetian-interior venetianCasino-interior grandCanal-interior
(and the anchors: venetianCasino-exterior grandCanal-exterior), or pass --export here.
"""
import sys, json, subprocess, importlib
from pathlib import Path
sys.path.insert(0, 'tools/strip-landmarks')
from common import Meshes, Frame

MODULES = {'lobby': 'venetian_lobby', 'casino': 'venetian_casino', 'shoppes': 'venetian_shoppes', 'sample': 'venetian_kit_sample'}
OUT = Path('build/strip-landmarks')
# The exterior-owned parts of the 'venetian' venue that this script never replaces
EXTERIOR_PORTAL = 'Venetian Grand Colonnade'


def save(B, out, keys):
    out.mkdir(parents=True, exist_ok=True)
    for key in keys:
        prop = key + '-interior'
        meshes = [g for g in B.groups.values() if g['property'] == prop]
        labels = [g for g in B.labels if g['property'] == prop]
        (out / (prop + '.json')).write_text(json.dumps({'meshes': meshes, 'labels': labels}, separators=(',', ':'), default=float))
        (out / (prop + '-collision.json')).write_text(json.dumps(B.solids[prop], separators=(',', ':'), default=float))
        tris = sum(len(g['faces']) for g in meshes)
        print(f'{prop}: {len(meshes)} batches, {tris:,} triangles, {len(B.solids[prop]["indices"]) // 3:,} collision triangles, {len(labels)} labels')


def anchor(out, key, point):
    """A tiny exterior for a sub-venue that has none of its own (the runtime loads <key>-exterior.glb for every venue)."""
    A = Meshes(); A.property = key + '-exterior'; A.source = 'anchor'
    A.box('vi-iron', point, (.01, .01, .01), True)           # (a 1 cm solid: tools read every collision file as a trimesh)
    (out / (key + '-exterior.json')).write_text(json.dumps({'meshes': list(A.groups.values()), 'labels': []}, separators=(',', ':')))
    (out / (key + '-exterior-collision.json')).write_text(json.dumps(A.solids[key + '-exterior'], separators=(',', ':')))


def lobby_routes(lobby):
    """The 'venetian' venue's routes: [0] in from the palace door, [1] the full Rialto approach (venetian_rialto's
    route_points) continued by the lobby's route that starts at the Rialto gallery door (kept as 'interior' so
    build_venetian_exterior.py can refresh the outdoor part alone), then the lobby's other routes."""
    import math
    from venetian_rialto import route_points
    routes = list(lobby.get('routes') or [])
    rialto = [r for r in routes if math.dist((r['points'][0][0], r['points'][0][2]), (225.85, -644.0)) < 6]
    others = [r for r in routes if r not in rialto]
    inner = rialto[0]['points'] if rialto else [[228.0, 6.32, -644.0]]
    first = others.pop(0) if others else dict(points=[[222.0, .24, -685.2], [237.0, .24, -684.9]])
    return [first, dict(points=[list(p) for p in route_points()] + inner, interior=inner)] + others + rialto[1:]


def merge(venues_path, new):
    """Read-modify-write under a lock directory: several agents build modules at once."""
    import os, time
    lock = Path('build/venetian-interiors/.venues.lock'); lock.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(600):
        try:
            os.mkdir(lock); break
        except FileExistsError:
            time.sleep(.5)
    try:
        _merge(venues_path, new)
    finally:
        os.rmdir(lock)


def _merge(venues_path, new):
    venues = json.loads(venues_path.read_text())
    keys = [v['key'] for v in venues]
    for v in new:
        if v['key'] == 'venetian':
            old = venues[keys.index('venetian')]
            old['portals'] = [p for p in old['portals'] if p['name'] == EXTERIOR_PORTAL] + v.get('portals', [])
            for f in ['zones', 'accessPoints', 'lights']:
                if f in v: old[f] = v[f]
            old['routes'] = lobby_routes(v)
            old['views'] = {k: x for k, x in old['views'].items() if not k.startswith('vi-')}
            old['views'].update(v.get('views', {}))
        elif v['key'] in keys:
            venues[keys.index(v['key'])] = v
        else:
            venues.insert(keys.index('venetian') + 1, v); keys = [x['key'] for x in venues]
    venues_path.write_text(json.dumps(venues, separators=(',', ':')))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    names = args or ['lobby', 'casino', 'shoppes']
    B = Meshes()
    venues = []
    for name in names:
        mod = importlib.import_module(MODULES[name])
        out_venues = mod.build(B)
        for v in out_venues:
            v.setdefault('lights', [l for l in B.lights if l['venue'] == v['key']])
            v.setdefault('hotelSources', [])
            v.setdefault('views', {})
        venues += out_venues
    keys = [v['key'] for v in venues]
    sample = 'sample' in names
    out = Path('build/venetian-interiors/kit') if sample else OUT
    save(B, out, keys)
    for v in venues:
        if v['key'] != 'venetian' and not sample: anchor(out, v['key'], v.pop('anchor'))
    if sample:
        (out / 'venues.json').write_text(json.dumps(venues, separators=(',', ':')))
    else:
        merge(OUT / 'venues.json', venues)
    print('venues:', ', '.join(f"{v['key']} ({len(v['zones'])} zones, {len(v.get('lights', []))} lights)" for v in venues))
    if '--export' in sys.argv:
        files = [k + '-interior' for k in keys] + ([k + '-exterior' for k in keys if k != 'venetian'] if not sample else [])
        cmd = ['blender', '-b', '--python', 'tools/strip-landmarks/export.py', '--'] + files
        if sample: cmd = ['blender', '-b', '--python', 'tools/strip-landmarks/venetian_review.py', '--', 'export', str(out)] + files
        subprocess.run(['tools/strip-landmarks/vi_blender.sh'] + cmd, check=True)


if __name__ == '__main__':
    main()
