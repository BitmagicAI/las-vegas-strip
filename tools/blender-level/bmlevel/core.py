"""The bpy-free half of bmlevel: coordinates, records, collider math, the JSON writers and the
review cameras — both the standard set (`review_cameras`) and the ad-hoc `--shot` specs
(`resolve_point`, `custom_shot`) review.py aims from a level JSON.

Everything a level script says is in GAME coordinates — metres, Y up, +Z forward, yaw in radians
about +Y so that an entity's forward at yaw θ is (sin θ, 0, cos θ) (engine/agent-docs/
coordinate-system.md). Blender is Z up, so a game point (x, y, z) is placed at Blender
(x, -z, y). That map is a rotation (90° about X, determinant +1), not a reflection, so a yaw
about game +Y is the SAME angle about Blender +Z. glTF export with `export_yup=True` maps
Blender (x, y, z) back to (x, z, -y), which undoes the placement exactly: what the script said
in game coordinates is what the engine reads from the GLB, and the collider records written
here (in game coordinates, untouched) line up with the art without any fixing up.

This module never imports bpy, so `python3 -m unittest` covers it without Blender and a level
script can be dry-run (`bmlevel.NullScene`) to check its counts and JSON before a real build.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from typing import Iterable, Sequence

MESH_LEVEL_FORMAT = 'bitmagic-mesh-level'
MESH_LEVEL_VERSION = 1

Vec3 = tuple[float, float, float]


# ---------------------------------------------------------------- coordinates

def to_blender(p: Sequence[float]) -> Vec3:
    """Game (x, y, z) -> Blender (x, -z, y)."""
    return (float(p[0]), -float(p[2]), float(p[1]))


def from_blender(p: Sequence[float]) -> Vec3:
    """Blender (x, y, z) -> game (x, z, -y)."""
    return (float(p[0]), float(p[2]), -float(p[1]))


def blender_yaw(game_yaw: float) -> float:
    """A yaw about game +Y is the same angle about Blender +Z (the axis map is a proper rotation)."""
    return float(game_yaw)


def rotate_xz(x: float, z: float, yaw: float) -> tuple[float, float]:
    """Rotate a local (x, z) offset by `yaw` about +Y: local +Z lands on (sin yaw, cos yaw)."""
    c, s = math.cos(yaw), math.sin(yaw)
    return (c * x + s * z, -s * x + c * z)


@dataclass(frozen=True)
class Frame:
    """A local frame: `world()` maps a local game point into the parent frame. Frames compose."""
    origin: Vec3 = (0.0, 0.0, 0.0)
    yaw: float = 0.0

    def world(self, p: Sequence[float]) -> Vec3:
        x, z = rotate_xz(float(p[0]), float(p[2]), self.yaw)
        return (self.origin[0] + x, self.origin[1] + float(p[1]), self.origin[2] + z)

    def child(self, origin: Sequence[float], yaw: float) -> 'Frame':
        return Frame(self.world(origin), self.yaw + yaw)


# ---------------------------------------------------------------- records

@dataclass
class BoxCollider:
    name: str
    position: Vec3
    size: Vec3
    yaw: float
    group: str | None = None

    def to_json(self) -> dict:
        d = {'name': self.name, 'shape': 'box', 'position': list(self.position), 'size': list(self.size), 'yaw': self.yaw}
        if self.group:
            d['group'] = self.group
        return d


@dataclass
class HullCollider:
    name: str
    vertices: list[float]  # flat world xyz
    group: str | None = None

    def to_json(self) -> dict:
        d = {'name': self.name, 'shape': 'convexHull', 'vertices': list(self.vertices)}
        if self.group:
            d['group'] = self.group
        return d


@dataclass
class DoorRecord:
    """Exactly the engine's `DoorDefinition` (worldProfileData.doors[]), so sync_world.py copies it."""
    id: str
    position: Vec3
    rotation_y: float
    width: float
    height: float
    thickness: float
    kind: str = 'plain'
    animation: str = 'slide'
    auto_open_radius: float | None = None

    def to_json(self) -> dict:
        d = {
            'id': self.id,
            'position': {'x': self.position[0], 'y': self.position[1], 'z': self.position[2]},
            'rotationY': self.rotation_y,
            'width': self.width,
            'height': self.height,
            'thickness': self.thickness,
            'kind': self.kind,
            'animation': self.animation,
        }
        if self.auto_open_radius is not None:
            d['autoOpenRadius'] = self.auto_open_radius
        return d


@dataclass
class Volume:
    name: str
    position: Vec3
    size: Vec3
    yaw: float
    tags: list[str]

    def to_json(self) -> dict:
        return {'name': self.name, 'position': list(self.position), 'size': list(self.size), 'yaw': self.yaw, 'tags': list(self.tags)}


@dataclass
class Landmark:
    name: str
    position: Vec3
    yaw: float
    tags: list[str]

    def to_json(self) -> dict:
        return {'name': self.name, 'position': list(self.position), 'yaw': self.yaw, 'tags': list(self.tags)}


@dataclass
class PointLight:
    name: str
    position: Vec3
    color: str
    intensity: float
    distance: float
    decay: float

    def to_json(self) -> dict:
        return {'name': self.name, 'type': 'point', 'position': list(self.position), 'color': self.color,
                'intensity': self.intensity, 'distance': self.distance, 'decay': self.decay}


@dataclass
class SpotLight:
    name: str
    position: Vec3
    target: Vec3
    color: str
    intensity: float
    angle: float
    penumbra: float
    cast_shadow: bool

    def to_json(self) -> dict:
        return {'name': self.name, 'type': 'spot', 'position': list(self.position), 'target': list(self.target),
                'color': self.color, 'intensity': self.intensity, 'angle': self.angle, 'penumbra': self.penumbra,
                'castShadow': self.cast_shadow}


@dataclass
class Link:
    """A walkable connection the audit marches: from volume `a` to volume `b`, through `door` if named."""
    a: str
    b: str
    door: str | None = None

    def to_json(self) -> dict:
        d = {'from': self.a, 'to': self.b}
        if self.door:
            d['door'] = self.door
        return d


@dataclass
class Stairs:
    """Review-camera hint: where a staircase starts and ends (game coordinates)."""
    name: str
    foot: Vec3
    top: Vec3

    def to_json(self) -> dict:
        return {'name': self.name, 'foot': list(self.foot), 'top': list(self.top)}


@dataclass
class MaterialRecord:
    name: str
    rgb: tuple[float, float, float]
    metal: float
    roughness: float
    glow: float
    alpha: float


# ---------------------------------------------------------------- colours

def hex_color(color) -> str:
    """Accept '#rrggbb' or an (r, g, b) tuple in 0..1 and return '#rrggbb'."""
    if isinstance(color, str):
        if len(color) == 7 and color[0] == '#':
            int(color[1:], 16)
            return color.lower()
        raise ValueError(f'colour {color!r} must be #rrggbb or an (r, g, b) tuple in 0..1')
    r, g, b = (max(0.0, min(1.0, float(c))) for c in color)
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))


# ---------------------------------------------------------------- geometry

def box_corners(center: Sequence[float], size: Sequence[float], yaw: float) -> list[Vec3]:
    """The eight world corners of an oriented box (game coordinates)."""
    hx, hy, hz = (float(s) / 2 for s in size)
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                x, z = rotate_xz(sx * hx, sz * hz, yaw)
                out.append((center[0] + x, center[1] + sy * hy, center[2] + z))
    return out


def convex_hull_2d(points: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    """Andrew's monotone chain; returns the hull counter-clockwise without collinear points."""
    pts = sorted(set((float(x), float(z)) for x, z in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def require_convex_outline(name: str, outline: Sequence[tuple[float, float]]) -> None:
    """A prism collider is a convex hull; a concave outline would silently become its hull."""
    if len(outline) < 3:
        raise ValueError(f'{name}: an outline needs at least 3 points')
    hull = convex_hull_2d(outline)
    if len(hull) != len(set((float(x), float(z)) for x, z in outline)):
        raise ValueError(f'{name}: outline is not convex — split it into convex parts (its hull would drop {len(outline) - len(hull)} point(s))')


def prism_vertices(frame: Frame, outline: Sequence[tuple[float, float]], bottom: float, top: float) -> list[float]:
    """Flat world xyz list for an extruded polygon given in the frame's local XZ."""
    out: list[float] = []
    for y in (bottom, top):
        for x, z in outline:
            out.extend(frame.world((x, y, z)))
    return out


def ramp_vertices(frame: Frame, foot: Sequence[float], width: float, rise: float, run: float) -> list[float]:
    """A wedge from the foot (local, at the bottom edge centre) rising `rise` over `run` along local +Z."""
    fx, fy, fz = (float(v) for v in foot)
    hw = width / 2
    pts = [(fx - hw, fy, fz), (fx + hw, fy, fz), (fx - hw, fy, fz + run), (fx + hw, fy, fz + run),
           (fx - hw, fy + rise, fz + run), (fx + hw, fy + rise, fz + run)]
    out: list[float] = []
    for p in pts:
        out.extend(frame.world(p))
    return out


def aabb(points: Iterable[Sequence[float]]) -> tuple[Vec3, Vec3] | None:
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    any_point = False
    for p in points:
        any_point = True
        for i in range(3):
            lo[i] = min(lo[i], float(p[i]))
            hi[i] = max(hi[i], float(p[i]))
    return ((lo[0], lo[1], lo[2]), (hi[0], hi[1], hi[2])) if any_point else None


def flat_to_points(flat: Sequence[float]) -> list[Vec3]:
    return [(float(flat[i]), float(flat[i + 1]), float(flat[i + 2])) for i in range(0, len(flat) - 2, 3)]


def coplanar_overlaps(faces: Iterable[tuple[Sequence[Sequence[float]], str]], limit: int = 5) -> tuple[int, list[str]]:
    """Faces that lie in one plane, face the same way and overlap: they z-fight (flicker between
    their materials) in the game. `faces` is (points in game space, material) per polygon — every
    mesh, decor and text included, because trim laid flush on a wall is the usual culprit and it is
    never a collider. Two faces of one material flicker between identical pixels, so they are not
    reported. Returns (count, up to `limit` examples). Same rule as bmedit's export() check."""
    prepared = []
    for pts, material in faces:
        p = [(float(v[0]), float(v[1]), float(v[2])) for v in pts]
        if len(p) < 3:
            continue
        # Newell's normal: robust for any planar polygon, its length is twice the area.
        nx = ny = nz = 0.0
        for i, (x0, y0, z0) in enumerate(p):
            x1, y1, z1 = p[(i + 1) % len(p)]
            nx += (y0 - y1) * (z0 + z1)
            ny += (z0 - z1) * (x0 + x1)
            nz += (x0 - x1) * (y0 + y1)
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length < 1e-9:
            continue
        n = (nx / length, ny / length, nz / length)
        centre = tuple(sum(v[i] for v in p) / len(p) for i in range(3))
        prepared.append((n, n[0] * p[0][0] + n[1] * p[0][1] + n[2] * p[0][2], p, centre, length / 2, material))
    buckets: dict = {}
    for i, (n, d, _p, _c, _a, _m) in enumerate(prepared):
        key = (round(n[0], 2), round(n[1], 2), round(n[2], 2), round(d * 200))   # same direction, within ~5 mm
        buckets.setdefault(key, []).append(i)

    def inside(point, pts, n) -> bool:
        # Convex polygon test in its own plane: the point is on the inner side of every edge.
        sign = 0
        for k in range(len(pts)):
            a, b = pts[k], pts[(k + 1) % len(pts)]
            e = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
            q = (point[0] - a[0], point[1] - a[1], point[2] - a[2])
            side = n[0] * (e[1] * q[2] - e[2] * q[1]) + n[1] * (e[2] * q[0] - e[0] * q[2]) + n[2] * (e[0] * q[1] - e[1] * q[0])
            if abs(side) < 1e-7:
                continue
            if sign == 0:
                sign = 1 if side > 0 else -1
            elif (side > 0) != (sign > 0):
                return False
        return True

    count, examples = 0, []
    for group in buckets.values():
        for x in range(len(group)):
            for y in range(x + 1, len(group)):
                fa, fb = prepared[group[x]], prepared[group[y]]
                if fa[5] == fb[5]:
                    continue
                small, big = (fa, fb) if fa[4] <= fb[4] else (fb, fa)
                if not inside(small[3], big[2], big[0]):
                    continue
                count += 1
                if len(examples) < limit:
                    c = small[3]
                    examples.append(f'({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}) {small[5]} vs {big[5]}')
    return count, examples


# ---------------------------------------------------------------- the level

@dataclass
class LevelData:
    colliders: list = field(default_factory=list)
    doors: list[DoorRecord] = field(default_factory=list)
    volumes: list[Volume] = field(default_factory=list)
    landmarks: list[Landmark] = field(default_factory=list)
    lights: list = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    stairs: list[Stairs] = field(default_factory=list)
    materials: dict[str, MaterialRecord] = field(default_factory=dict)
    visual_points: list[Vec3] = field(default_factory=list)  # decoration corners, for the extent

    def require_unique(self, kind: str, items: Sequence, key: str) -> None:
        seen: set = set()
        for item in items:
            k = getattr(item, key)
            if k in seen:
                raise ValueError(f'duplicate {kind} {key} {k!r} — every {kind} needs its own name')
            seen.add(k)

    def bounds(self) -> tuple[Vec3, Vec3] | None:
        pts: list[Vec3] = list(self.visual_points)
        for c in self.colliders:
            if isinstance(c, BoxCollider):
                pts.extend(box_corners(c.position, c.size, c.yaw))
            else:
                pts.extend(flat_to_points(c.vertices))
        return aabb(pts)

    def native_height(self) -> float:
        b = self.bounds()
        return round(b[1][1] - b[0][1], 3) if b else 0.0

    def mesh_level_json(self) -> dict:
        self.require_unique('collider', self.colliders, 'name')
        self.require_unique('volume', self.volumes, 'name')
        self.require_unique('landmark', self.landmarks, 'name')
        self.require_unique('light', self.lights, 'name')
        self.require_unique('door', self.doors, 'id')
        return {
            'format': MESH_LEVEL_FORMAT,
            'version': MESH_LEVEL_VERSION,
            'units': 'meters',
            'colliders': [c.to_json() for c in self.colliders],
            'volumes': [v.to_json() for v in self.volumes],
            'landmarks': [l.to_json() for l in self.landmarks],
            'lights': [l.to_json() for l in self.lights],
            'extras': {
                'links': [l.to_json() for l in self.links],
                'stairs': [s.to_json() for s in self.stairs],
                'doors': [d.id for d in self.doors],
            },
        }

    def doors_json(self) -> list[dict]:
        return [d.to_json() for d in self.doors]

    def write(self, out_dir: str, name: str) -> tuple[str, str]:
        os.makedirs(out_dir, exist_ok=True)
        level_path = os.path.join(out_dir, f'{name}.mesh-level.json')
        doors_path = os.path.join(out_dir, f'{name}.doors.json')
        with open(level_path, 'w') as f:
            json.dump(self.mesh_level_json(), f, indent=1)
        with open(doors_path, 'w') as f:
            json.dump(self.doors_json(), f, indent=1)
        return level_path, doors_path

    def summary(self, name: str, glb_path: str) -> str:
        boxes = sum(1 for c in self.colliders if isinstance(c, BoxCollider))
        hulls = len(self.colliders) - boxes
        b = self.bounds()
        extent = 'no geometry' if not b else 'x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f' % (b[0][0], b[1][0], b[0][1], b[1][1], b[0][2], b[1][2])
        has_spawn = any(l.name == 'spawn' for l in self.landmarks)
        lines = [
            f'LEVEL {name}: {len(self.colliders)} colliders ({boxes} box, {hulls} hull), {len(self.doors)} doors, '
            f'{len(self.volumes)} volumes, {len(self.landmarks)} landmarks, {len(self.lights)} lights, {len(self.links)} links',
            f'BOUNDS {extent}   native height {self.native_height()} m',
            'REGISTER bitmagic assets add %s --name %s --keep-glb --asset-id level-%s --height %s' % (glb_path, name, name, self.native_height()),
        ]
        if not has_spawn:
            lines.append('WARNING no spawn(): the player spawn stays whatever world.json says')
        if not self.colliders:
            lines.append('WARNING no solid geometry: nothing in this level can be stood on')
        return '\n'.join(lines)


# ---------------------------------------------------------------- review cameras

def review_cameras(level: dict, doors: Sequence[dict] = ()) -> list[dict]:
    """Deterministic review shots (game coordinates): overview, both sides of every door, every
    staircase from its foot, every volume from inside. `level` is the mesh-level JSON dict."""
    shots: list[dict] = []
    pts: list[Vec3] = []
    for c in level.get('colliders', []):
        if c['shape'] == 'box':
            pts.extend(box_corners(c['position'], c['size'], c.get('yaw', 0.0)))
        else:
            pts.extend(flat_to_points(c['vertices']))
    b = aabb(pts)
    if b:
        cx, cz = (b[0][0] + b[1][0]) / 2, (b[0][2] + b[1][2]) / 2
        sx, sz = max(b[1][0] - b[0][0], 1.0), max(b[1][2] - b[0][2], 1.0)
        span = max(sx, sz)
        # `scale` fits the wider axis into the frame's WIDTH; a renderer with a 16:9 frame fits the
        # taller axis with `extent` (see review.py).
        shots.append({'name': 'overview', 'kind': 'ortho', 'position': (cx, b[1][1] + span, cz), 'target': (cx, b[0][1], cz), 'scale': span * 1.15, 'extent': (sx, sz)})
    for d in doors:
        p = d['position']
        px, py, pz = (p['x'], p['y'], p['z']) if isinstance(p, dict) else tuple(p)
        yaw = d.get('rotationY', 0.0)
        eye_y = py - d['height'] / 2 + 1.6
        for side, sign in (('a', 1), ('b', -1)):
            ox, oz = rotate_xz(0.0, sign * 4.0, yaw)
            shots.append({'name': f"door-{d['id']}-{side}", 'kind': 'persp', 'position': (px + ox, eye_y, pz + oz), 'target': (px, eye_y - 0.2, pz)})
    for s in level.get('extras', {}).get('stairs', []):
        foot, top = tuple(s['foot']), tuple(s['top'])
        dx, dz = top[0] - foot[0], top[2] - foot[2]
        n = math.hypot(dx, dz) or 1.0
        shots.append({'name': f"stairs-{s['name']}", 'kind': 'persp', 'position': (foot[0] - dx / n * 4, foot[1] + 1.7, foot[2] - dz / n * 4), 'target': (top[0], top[1] + 0.5, top[2])})
    for v in level.get('volumes', []):
        p, size, yaw = v['position'], v['size'], v.get('yaw', 0.0)
        long_axis_z = size[2] >= size[0]
        back = (0.0, -size[2] / 2 + 0.8) if long_axis_z else (-size[0] / 2 + 0.8, 0.0)
        ox, oz = rotate_xz(back[0], back[1], yaw)
        eye_y = p[1] - size[1] / 2 + 1.6
        fx, fz = rotate_xz(0.0, 1.0, yaw) if long_axis_z else rotate_xz(1.0, 0.0, yaw)
        shots.append({'name': f"volume-{v['name']}", 'kind': 'persp', 'position': (p[0] + ox, eye_y, p[2] + oz), 'target': (p[0] + ox + fx * 4, eye_y - 0.3, p[2] + oz + fz * 4)})
    return shots


# ---------------------------------------------------------------- ad-hoc shots

EYE_HEIGHT = 1.6
"""Where a standing player's camera is above the floor — the height every review shot uses."""


def level_center(level: dict) -> Vec3:
    """The centre of the collider bounds, at eye height above their floor: what a shot with no
    target looks at."""
    pts: list[Vec3] = []
    for c in level.get('colliders', []):
        if c['shape'] == 'box':
            pts.extend(box_corners(c['position'], c['size'], c.get('yaw', 0.0)))
        else:
            pts.extend(flat_to_points(c['vertices']))
    b = aabb(pts)
    if not b:
        return (0.0, EYE_HEIGHT, 0.0)
    return ((b[0][0] + b[1][0]) / 2, b[0][1] + EYE_HEIGHT, (b[0][2] + b[1][2]) / 2)


def resolve_point(spec: str, level: dict, doors: Sequence[dict] = (), *, as_eye: bool = False) -> Vec3:
    """A game-space point from one end of a `--shot` spec.

    `landmark:<name>`, `volume:<name>`, `door:<id>` or a raw `x,y,z`. Landmarks, doors and volumes
    are recorded at the floor, the door's centre and the room's centre respectively, so `as_eye`
    (the FROM end) lifts each to a standing camera and the TO end aims at the thing itself. Raw
    coordinates are used exactly as written, either end — they are the escape hatch.
    """
    spec = spec.strip()
    kind, _, rest = spec.partition(':')
    kind, rest = kind.strip().lower(), rest.strip()
    if kind == 'landmark':
        for l in level.get('landmarks', []):
            if l['name'] == rest:
                x, y, z = l['position']
                return (x, y + (EYE_HEIGHT if as_eye else 1.0), z)
        known = ', '.join(sorted(l['name'] for l in level.get('landmarks', []))) or '(none)'
        raise ValueError(f'no landmark named {rest!r} — the level has: {known}')
    if kind == 'volume':
        for v in level.get('volumes', []):
            if v['name'] == rest:
                x, y, z = v['position']
                return (x, y - v['size'][1] / 2 + EYE_HEIGHT, z) if as_eye else (x, y, z)
        known = ', '.join(sorted(v['name'] for v in level.get('volumes', []))) or '(none)'
        raise ValueError(f'no volume named {rest!r} — the level has: {known}')
    if kind == 'door':
        for d in doors:
            if d['id'] == rest:
                p = d['position']
                x, y, z = (p['x'], p['y'], p['z']) if isinstance(p, dict) else tuple(p)
                return (x, y - d['height'] / 2 + EYE_HEIGHT, z) if as_eye else (x, y, z)
        known = ', '.join(sorted(d['id'] for d in doors)) or '(none)'
        raise ValueError(f'no door with id {rest!r} — the level has: {known}')
    parts = [p for p in spec.replace(' ', '').split(',') if p]
    if len(parts) == 3:
        try:
            return (float(parts[0]), float(parts[1]), float(parts[2]))
        except ValueError:
            pass
    raise ValueError(f'cannot read shot point {spec!r} — use landmark:<name>, volume:<name>, door:<id> or x,y,z')


def custom_shot(spec: str, index: int, level: dict, doors: Sequence[dict] = (), fov: float | None = None) -> dict:
    """One `--shot` argument as a review shot. `'FROM -> TO'`, or `'FROM'` to look at the level's
    centre. `index` numbers the frame (`shot-1`, `shot-2`, …)."""
    frm, arrow, to = spec.partition('->')
    position = resolve_point(frm, level, doors, as_eye=True)
    target = resolve_point(to, level, doors) if arrow else level_center(level)
    shot = {'name': f'shot-{index}', 'kind': 'persp', 'position': position, 'target': target, 'spec': spec.strip()}
    if fov is not None:
        shot['fov'] = fov
    return shot
