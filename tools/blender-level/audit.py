"""Ray-cast audit of a built level, run inside Blender against the COLLIDERS the engine will get
(not the art — decoration is exactly what must not be solid):

    "$BLENDER" -b --python tools/blender-level/audit.py -- build/level/hut.mesh-level.json [--doors closed] [--json out.json]

Checks, all driven by the level JSON:
  floor_continuity   every volume: a ray down from 1 m above its floor must hit within 1.5 m on a 0.5 m grid
  door_clearance     every door (doors open): nothing solid across the opening at three heights
  link_clearance     every link: a player capsule (r 0.4, h 1.8) marched from A through the door to B never
                     hits a wall and always has a floor under it
  sealed_envelope    (--doors closed only) every roofed volume: rays up and outward from inside hit something —
                     no hole in a roof or wall the player could fall through
  coplanar_overlap   pairs of box colliders with a shared face plane and overlapping extents — z-fighting
                     candidates; a WARNING, not a failure

Exit 1 on any failure. `--json` also writes the full result for a script to read.
"""
import json
import math
import os
import sys

import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmlevel.core import box_corners, flat_to_points, rotate_xz, to_blender  # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
if not argv:
    print(__doc__)
    sys.exit(2)
LEVEL_PATH = argv[0]
DOORS_CLOSED = '--doors' in argv and argv[argv.index('--doors') + 1] == 'closed'
JSON_OUT = argv[argv.index('--json') + 1] if '--json' in argv else None
DOORS_PATH = LEVEL_PATH.replace('.mesh-level.json', '.doors.json')

level = json.load(open(LEVEL_PATH))
doors = json.load(open(DOORS_PATH)) if os.path.exists(DOORS_PATH) else []

# ---------------------------------------------------------------- BVH from colliders

verts: list[Vector] = []
faces: list[tuple] = []
BOX_FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def add_box(center, size, yaw) -> None:
    base = len(verts)
    verts.extend(Vector(to_blender(p)) for p in box_corners(center, size, yaw))
    faces.extend(tuple(base + i for i in f) for f in BOX_FACES)


def add_hull(flat) -> None:
    bm = bmesh.new()
    for p in flat_to_points(flat):
        bm.verts.new(to_blender(p))
    bm.verts.ensure_lookup_table()
    bmesh.ops.convex_hull(bm, input=list(bm.verts))
    base = len(verts)
    index = {v: i for i, v in enumerate(bm.verts)}
    verts.extend(v.co.copy() for v in bm.verts)
    faces.extend(tuple(base + index[v] for v in f.verts) for f in bm.faces)
    bm.free()


boxes = []
for c in level['colliders']:
    if c['shape'] == 'box':
        add_box(c['position'], c['size'], c.get('yaw', 0.0))
        boxes.append(c)
    else:
        add_hull(c['vertices'])
if DOORS_CLOSED:
    for d in doors:
        p = d['position']
        add_box((p['x'], p['y'], p['z']), (d['width'], d['height'], d['thickness']), d.get('rotationY', 0.0))
bvh = BVHTree.FromPolygons(verts, faces) if faces else None


def cast(origin, direction, limit):
    """Ray in GAME coordinates; returns hit distance or None."""
    if bvh is None:
        return None
    o = Vector(to_blender(origin))
    d = Vector(to_blender(direction))
    hit = bvh.ray_cast(o, d, limit)
    return hit[3] if hit[0] is not None else None


# ---------------------------------------------------------------- checks

results: dict[str, dict] = {}


def record(check: str, ok: bool, detail: dict) -> None:
    r = results.setdefault(check, {'checks': 0, 'failures': []})
    r['checks'] += 1
    if not ok:
        r['failures'].append(detail)


def volume_grid(v, step=0.5, inset=0.35):
    px, py, pz = v['position']
    sx, sy, sz = v['size']
    yaw = v.get('yaw', 0.0)
    xs = [x for x in frange(-sx / 2 + inset, sx / 2 - inset, step)]
    zs = [z for z in frange(-sz / 2 + inset, sz / 2 - inset, step)]
    for lx in xs:
        for lz in zs:
            wx, wz = rotate_xz(lx, lz, yaw)
            yield (px + wx, py - sy / 2, pz + wz), (lx, lz)


def frange(a, b, step):
    n = max(1, int(round((b - a) / step)))
    return [a + (b - a) * i / n for i in range(n + 1)] if b > a else [(a + b) / 2]


volumes = {v['name']: v for v in level.get('volumes', [])}
for v in level.get('volumes', []):
    for (x, floor_y, z), local in volume_grid(v):
        hit = cast((x, floor_y + 1.0, z), (0, -1, 0), 2.5)
        record('floor_continuity', hit is not None and hit <= 1.5, {'volume': v['name'], 'at': [round(x, 2), round(z, 2)], 'local': [round(local[0], 2), round(local[1], 2)]})

if DOORS_CLOSED:
    for v in level.get('volumes', []):
        if 'unroofed' in v.get('tags', []):
            continue
        sx, sy, sz = v['size']
        yaw = v.get('yaw', 0.0)
        for (x, floor_y, z), local in volume_grid(v, step=1.0):
            up = cast((x, floor_y + 0.5, z), (0, 1, 0), sy + 1.0)
            record('sealed_envelope', up is not None, {'volume': v['name'], 'kind': 'roof', 'at': [round(x, 2), round(z, 2)]})
            for dx, dz, limit in ((1, 0, sx / 2 - local[0] + 1.0), (-1, 0, sx / 2 + local[0] + 1.0), (0, 1, sz / 2 - local[1] + 1.0), (0, -1, sz / 2 + local[1] + 1.0)):
                wx, wz = rotate_xz(dx, dz, yaw)
                side = cast((x, floor_y + sy / 2, z), (wx, 0, wz), limit)
                record('sealed_envelope', side is not None, {'volume': v['name'], 'kind': 'wall', 'at': [round(x, 2), round(z, 2)], 'dir': [dx, dz]})
else:
    for d in doors:
        p = d['position']
        yaw = d.get('rotationY', 0.0)
        fx, fz = rotate_xz(0.0, 1.0, yaw)
        rx, rz = rotate_xz(1.0, 0.0, yaw)
        base_y = p['y'] - d['height'] / 2
        span = d['thickness'] + 1.2
        for lateral in frange(-d['width'] / 2 + 0.12, d['width'] / 2 - 0.12, 0.25):
            for h in (0.3, 1.0, d['height'] - 0.25):
                origin = (p['x'] + rx * lateral - fx * span / 2, base_y + h, p['z'] + rz * lateral - fz * span / 2)
                hit = cast(origin, (fx, 0, fz), span)
                record('door_clearance', hit is None, {'door': d['id'], 'lateral': round(lateral, 2), 'height': round(h, 2)})

    door_by_id = {d['id']: d for d in doors}
    for l in level.get('extras', {}).get('links', []):
        a, b = volumes.get(l['from']), volumes.get(l['to'])
        if not a or not b:
            record('link_clearance', False, {'link': l, 'reason': 'unknown volume'})
            continue
        waypoints = [tuple(a['position'])]
        if l.get('door'):
            d = door_by_id.get(l['door'])
            if not d:
                record('link_clearance', False, {'link': l, 'reason': 'unknown door'})
                continue
            waypoints.append((d['position']['x'], d['position']['y'] - d['height'] / 2 + 0.9, d['position']['z']))
        waypoints.append(tuple(b['position']))
        for i in range(len(waypoints) - 1):
            (x0, y0, z0), (x1, y1, z1) = waypoints[i], waypoints[i + 1]
            n = max(1, int(math.hypot(x1 - x0, z1 - z0) / 0.5))
            for k in range(n + 1):
                t = k / n
                x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
                # Probe for the floor from just above waist height: a door waypoint sits under its
                # header, and a ray from higher up would start inside the lintel.
                probe_y = y0 + (y1 - y0) * t + 0.5
                floor = cast((x, probe_y, z), (0, -1, 0), 3.0)
                record('link_clearance', floor is not None, {'link': [l['from'], l['to']], 'at': [round(x, 2), round(z, 2)], 'reason': 'no floor'})
                if floor is None:
                    continue
                fy = probe_y - floor
                for h in (0.5, 1.5):
                    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        # Rays run along the march direction's perpendiculars and along it; a wall
                        # within capsule radius means the route squeezes through something.
                        blocked = cast((x, fy + h, z), (dx, 0, dz), 0.4)
                        record('link_clearance', blocked is None, {'link': [l['from'], l['to']], 'at': [round(x, 2), round(z, 2)], 'height': h, 'dir': [dx, dz], 'reason': 'wall within 0.4 m'})

# Z-fighting candidates: two boxes sharing a face plane with overlapping extents (axis-aligned only).
warnings = []
def faces_of(b):
    if abs(b.get('yaw', 0.0)) > 1e-6:
        return []
    px, py, pz = b['position']
    sx, sy, sz = b['size']
    out = []
    rect = [(px - sx / 2, px + sx / 2), (py - sy / 2, py + sy / 2), (pz - sz / 2, pz + sz / 2)]
    for axis in range(3):
        for sign, plane in ((-1, rect[axis][0]), (1, rect[axis][1])):
            out.append((axis, sign, plane, rect))
    return out
for i in range(len(boxes)):
    for j in range(i + 1, len(boxes)):
        for axis, sign, plane, rect in faces_of(boxes[i]):
            for axis2, sign2, plane2, rect2 in faces_of(boxes[j]):
                # Same plane AND same facing: two visible faces fighting. A wall standing on a floor
                # (floor top against wall bottom) is a contact, not a fight.
                if axis != axis2 or sign != sign2 or abs(plane - plane2) > 0.001:
                    continue
                overlap = all(min(rect[k][1], rect2[k][1]) - max(rect[k][0], rect2[k][0]) > 0.01 for k in range(3) if k != axis)
                if overlap:
                    warnings.append({'a': boxes[i]['name'], 'b': boxes[j]['name'], 'axis': 'xyz'[axis], 'plane': round(plane, 3)})
                    break

# ---------------------------------------------------------------- report

failed = 0
mode = 'doors closed' if DOORS_CLOSED else 'doors open'
print(f'AUDIT {os.path.basename(LEVEL_PATH)} ({mode}): {len(level["colliders"])} colliders, {len(doors)} doors')
for check, r in results.items():
    n = len(r['failures'])
    failed += n
    print(f'  {check:18s} {r["checks"]:6d} rays  {n:4d} failed' + ('' if n == 0 else '   e.g. ' + json.dumps(r['failures'][0])))
if not results:
    print('  (no volumes, doors or links to audit — declare volume()/link() in the level script)')
if warnings:
    print(f'  coplanar_overlap   {len(warnings):4d} warning(s) — shared face planes, likely z-fighting: ' + ', '.join(f"{w['a']} / {w['b']}" for w in warnings[:6]))
if JSON_OUT:
    json.dump({'mode': mode, 'results': results, 'coplanar_warnings': warnings}, open(JSON_OUT, 'w'), indent=1)
    print(f'  wrote {JSON_OUT}')
print('AUDIT_RESULT ' + ('PASS' if failed == 0 else f'FAIL {failed}'))
sys.exit(0 if failed == 0 else 1)
