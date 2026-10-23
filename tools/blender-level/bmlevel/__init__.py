"""bmlevel — write a low-poly game level as a short Python script, build it in Blender, and get
one GLB plus the collider / door / light JSON the Bitmagic engine's `MeshLevel` loads.

    from bmlevel import *
    mat('stone', (0.5, 0.5, 0.48))
    with context('hut', origin=(0, 0, 0)):
        slab('floor', (0, 0), (8, 6), material='stone')
        wall('north', (-4, -3), (4, -3), height=3, material='stone', opening={'at': 4, 'width': 1.4, 'height': 2.2})
        door('front', (0, 0, -3), yaw=0)
        spawn((0, 0.1, 0))
    export('build/level', 'hut')

Every position is in GAME coordinates (metres, Y up, +Z forward, yaw about +Y) inside the current
`context()`; the Blender axis flip happens once, in the scene backend. Anything built with
`solid=True` (the default) also becomes a collider record; `decor()` is the same call for things
the player must never bump into. See core.py for the coordinate argument and the JSON shapes.
"""
from __future__ import annotations

import contextlib
import math
import os
import sys
from typing import Sequence

from bmlevel.core import (
    BoxCollider, DoorRecord, Frame, HullCollider, Landmark, LevelData, Link, MaterialRecord,
    PointLight, SpotLight, Stairs, Volume, box_corners, hex_color, prism_vertices, ramp_vertices,
    require_convex_outline, rotate_xz,
)

try:  # inside Blender
    import bpy  # noqa: F401
    from bmlevel.scene_bpy import BpyScene as Scene
except ImportError:  # plain python3: record only
    from bmlevel.scene_null import NullScene as Scene

__all__ = [
    'mat', 'context', 'box', 'decor', 'prism', 'slab', 'wall', 'glazing', 'door', 'stairs', 'text',
    'volume', 'link', 'lamp', 'spot', 'landmark', 'spawn', 'export', 'level', 'scene', 'reset', 'DRY_RUN',
]

DRY_RUN = '--dry-run' in sys.argv or not Scene.available

level = LevelData()
scene = Scene()
_frames: list[Frame] = [Frame()]


def reset() -> None:
    """Start over (a script that builds several levels calls this between them)."""
    global level
    level = LevelData()
    scene.reset()
    _frames[:] = [Frame()]


def _frame() -> Frame:
    return _frames[-1]


def _vec3(p: Sequence[float], what: str) -> tuple[float, float, float]:
    if len(p) != 3:
        raise ValueError(f'{what} must be (x, y, z), got {p!r}')
    return (float(p[0]), float(p[1]), float(p[2]))


# ---------------------------------------------------------------- materials

def mat(name: str, rgb: Sequence[float], metal: float = 0.0, roughness: float = 0.5, glow: float = 0.0, alpha: float = 1.0) -> None:
    """Declare a material. Name conventions the engine reads: `glass*` renders as a thin
    transparent pane, `emissive*` is guaranteed to glow (glow > 0 also exports emission)."""
    if len(rgb) != 3:
        raise ValueError(f'mat({name!r}): rgb must be (r, g, b) in 0..1')
    level.materials[name] = MaterialRecord(name, tuple(float(c) for c in rgb), metal, roughness, glow, alpha)
    scene.material(name, rgb, metal, roughness, glow, alpha)


# ---------------------------------------------------------------- frames

@contextlib.contextmanager
def context(name: str, origin: Sequence[float] = (0, 0, 0), yaw: float = 0.0):
    """A named part of the level with its own local frame (a room, a module, a corridor). Objects
    made inside land in a Blender collection of that name. Contexts nest."""
    _frames.append(_frame().child(_vec3(origin, 'context origin'), yaw))
    scene.begin_collection(name)
    try:
        yield
    finally:
        scene.end_collection()
        _frames.pop()


# ---------------------------------------------------------------- solids

def box(name: str, pos: Sequence[float], size: Sequence[float], material: str, solid: bool = True, yaw: float = 0.0, bevel: float = 0.0, group: str | None = None) -> None:
    """An oriented box: `pos` is its centre, `size` its full (width, height, depth) in metres."""
    p = _frame().world(_vec3(pos, f'box {name!r} pos'))
    s = _vec3(size, f'box {name!r} size')
    if min(s) <= 0:
        raise ValueError(f'box {name!r}: every size must be > 0')
    w_yaw = _frame().yaw + yaw
    scene.box(name, p, s, w_yaw, material, bevel)
    if solid:
        level.colliders.append(BoxCollider(name, p, s, w_yaw, group))
    else:
        level.visual_points.extend(box_corners(p, s, w_yaw))


def decor(name: str, pos: Sequence[float], size: Sequence[float], material: str, yaw: float = 0.0, bevel: float = 0.0) -> None:
    """A box the player never collides with: cladding, trim, lamps, fasteners, signage plates."""
    box(name, pos, size, material, solid=False, yaw=yaw, bevel=bevel)


def prism(name: str, outline: Sequence[tuple[float, float]], bottom: float, top: float, material: str, solid: bool = True, group: str | None = None) -> None:
    """A polygon in local XZ extruded from `bottom` to `top`. Solid prisms must be convex (a
    concave one raises — split it), because the collider is a convex hull."""
    if top <= bottom:
        raise ValueError(f'prism {name!r}: top must be above bottom')
    if solid:
        require_convex_outline(name, outline)
    verts = prism_vertices(_frame(), outline, bottom, top)
    scene.prism(name, verts, material)
    if solid:
        level.colliders.append(HullCollider(name, verts, group))
    else:
        level.visual_points.extend((verts[i], verts[i + 1], verts[i + 2]) for i in range(0, len(verts), 3))


def slab(name: str, pos_xz: Sequence[float], size_xz: Sequence[float], material: str, y: float = 0.0, thickness: float = 0.5, yaw: float = 0.0) -> None:
    """A floor or ceiling plate whose TOP surface is at `y`."""
    box(name, (pos_xz[0], y - thickness / 2, pos_xz[1]), (size_xz[0], thickness, size_xz[1]), material, yaw=yaw)


def wall(name: str, start: Sequence[float], end: Sequence[float], height: float, material: str, thickness: float = 0.3, base: float = 0.0, opening: dict | None = None) -> None:
    """A wall from local (x, z) `start` to `end`. `opening={'at': m, 'width': w, 'height': h}` cuts
    a doorway centred `at` metres from the start, leaving a lintel above it."""
    (x0, z0), (x1, z1) = (float(start[0]), float(start[1])), (float(end[0]), float(end[1]))
    length = math.hypot(x1 - x0, z1 - z0)
    if length <= 0:
        raise ValueError(f'wall {name!r}: start and end coincide')
    yaw = math.atan2(x1 - x0, z1 - z0)  # local +Z along the wall at yaw 0

    def segment(seg_name: str, t0: float, t1: float, seg_base: float, seg_top: float) -> None:
        if t1 - t0 <= 1e-6 or seg_top - seg_base <= 1e-6:
            return
        tm = (t0 + t1) / 2
        cx, cz = x0 + (x1 - x0) * tm / length, z0 + (z1 - z0) * tm / length
        box(seg_name, (cx, (seg_base + seg_top) / 2, cz), (thickness, seg_top - seg_base, t1 - t0), material, yaw=yaw)

    if opening is None:
        segment(name, 0.0, length, base, base + height)
        return
    unknown = set(opening) - {'at', 'width', 'height'}
    if unknown:
        raise ValueError(f'wall {name!r}: opening keys must be at/width/height, got {sorted(unknown)}')
    at, w, h = float(opening['at']), float(opening['width']), float(opening['height'])
    if not (0 < at - w / 2 and at + w / 2 < length):
        raise ValueError(f'wall {name!r}: opening {at}±{w / 2} falls outside the wall length {length:.2f}')
    if h >= height:
        raise ValueError(f'wall {name!r}: opening height {h} must be below the wall height {height}')
    segment(f'{name} left', 0.0, at - w / 2, base, base + height)
    segment(f'{name} right', at + w / 2, length, base, base + height)
    segment(f'{name} lintel', at - w / 2, at + w / 2, base + h, base + height)


def glazing(name: str, start: Sequence[float], end: Sequence[float], height: float, glass: str, frame: str, sill: float = 0.9, head: float = 0.4, base: float = 0.0, thickness: float = 0.3) -> None:
    """A window wall: solid sill and head bands in `frame`, a thin pane in `glass` between them.
    The pane is not a collider — the sill and head are, which is what stops the player."""
    wall(f'{name} sill', start, end, sill, frame, thickness, base)
    wall(f'{name} head', start, end, head, frame, thickness, base + height - head)
    (x0, z0), (x1, z1) = start, end
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    yaw = math.atan2(x1 - x0, z1 - z0)
    pane_h = height - sill - head
    box(f'{name} pane', (cx, base + sill + pane_h / 2, cz), (0.04, pane_h, math.hypot(x1 - x0, z1 - z0)), glass, solid=False, yaw=yaw)
    # An invisible-to-decor but solid pane keeps the player from walking through the glass.
    level.colliders.append(BoxCollider(f'{name} pane collider', _frame().world((cx, base + sill + pane_h / 2, cz)), (max(0.1, thickness / 2), pane_h, math.hypot(x1 - x0, z1 - z0)), _frame().yaw + yaw))


def door(id: str, pos: Sequence[float], yaw: float = 0.0, width: float = 1.4, height: float = 2.2, thickness: float = 0.1, kind: str = 'plain', animation: str = 'slide', jamb: str | None = None, jamb_depth: float = 0.34, auto_open_radius: float | None = None) -> None:
    """A doorway: `pos` is the floor point at its centre, the leaf spans `width` across local X at
    `yaw`. Writes a `DoorDefinition` for world.json (the engine builds and animates the leaf) and,
    when `jamb` names a material, solid jambs and a header around it."""
    if kind not in ('plain', 'locked') or animation not in ('hinge', 'slide', 'dissolve'):
        raise ValueError(f'door {id!r}: kind is plain|locked, animation is hinge|slide|dissolve')
    p = _vec3(pos, f'door {id!r} pos')
    w_yaw = _frame().yaw + yaw
    centre = _frame().world((p[0], p[1] + height / 2, p[2]))
    level.doors.append(DoorRecord(id, centre, w_yaw, width, height, thickness, kind, animation, auto_open_radius))
    if jamb:
        # No jamb or header face may share a plane with the wall around the opening, or it
        # flickers (z-fighting): the default depth stands 2 cm proud of a 0.3 m wall, the jambs
        # stand 1 cm back from the opening's sides and sink 2 cm into the floor, and the header
        # starts 1 cm above the opening's top.
        for side in (-1, 1):
            ox, oz = rotate_xz(side * (width / 2 + 0.09), 0.0, yaw)  # the jambs sit across the leaf, whatever the door's yaw
            box(f'{id} jamb {"L" if side < 0 else "R"}', (p[0] + ox, p[1] + height / 2 + 0.09, p[2] + oz), (0.16, height + 0.22, jamb_depth), jamb, yaw=yaw)
        # The header is a little deeper and taller than the jambs, so no two faces share a plane.
        box(f'{id} header', (p[0], p[1] + height + 0.16, p[2]), (width + 0.38, 0.3, jamb_depth + 0.04), jamb, yaw=yaw)


def stairs(name: str, foot: Sequence[float], rise: float, run: float, material: str, width: float = 2.0, yaw: float = 0.0, steps: int | None = None, rail: str | None = None, treads_solid: bool = False) -> None:
    """A straight flight climbing `rise` over `run` along local +Z from `foot` (the bottom edge's
    centre, at floor level). Visual treads, one smooth ramp collider (so walking up is not a
    stutter), optional rails in `rail`. `treads_solid=True` makes every tread a collider too."""
    f = _vec3(foot, f'stairs {name!r} foot')
    n = steps or max(2, math.ceil(rise / 0.18))
    tread, riser = run / n, rise / n
    for i in range(n):
        top = f[1] + (i + 1) * riser
        box(f'{name} tread {i:02d}', (f[0], (f[1] + top) / 2, f[2] + (i + 0.5) * tread), (width, top - f[1], tread), material, solid=treads_solid, yaw=yaw)
    frame = _frame().child((0, 0, 0), yaw) if yaw else _frame()
    level.colliders.append(HullCollider(f'{name} ramp', ramp_vertices(frame, f, width, rise, run)))
    if rail:
        for side in (-1, 1):
            x = f[0] + side * (width / 2 + 0.05)
            pts = []
            for z, y in ((f[2], f[1]), (f[2] + run, f[1] + rise)):
                for dy in (0.85, 0.95):
                    for dx in (-0.03, 0.03):
                        pts.extend(frame.world((x + dx, y + dy, z)))
            level.colliders.append(HullCollider(f'{name} rail {"L" if side < 0 else "R"}', pts))
            scene.hull(f'{name} rail {"L" if side < 0 else "R"}', pts, rail)
            for i in range(0, n, max(1, n // 3)):
                box(f'{name} post {"L" if side < 0 else "R"} {i}', (x, f[1] + (i + 1) * riser + 0.45, f[2] + (i + 0.5) * tread), (0.06, 0.9, 0.06), rail, solid=False, yaw=yaw)
    level.stairs.append(Stairs(name, _frame().world(f), frame.world((f[0], f[1] + rise, f[2] + run))))


def text(name: str, string: str, pos: Sequence[float], material: str, yaw: float = 0.0, size: float = 0.5, extrude: float = 0.01, both_faces: bool = False) -> None:
    """3D signage, readable from local -Z at yaw 0 (facing an approaching player). Blender's
    bundled font, no font file. `both_faces` adds a mirrored copy for the other approach."""
    p = _frame().world(_vec3(pos, f'text {name!r} pos'))
    scene.text(name, string, p, _frame().yaw + yaw, size, material, extrude, both_faces)
    level.visual_points.append(p)


# ---------------------------------------------------------------- data only

def volume(name: str, pos: Sequence[float], size: Sequence[float], yaw: float = 0.0, tags: Sequence[str] = (), roofed: bool = True) -> None:
    """A named region (a room, an airlock, a trigger area): `pos` is its centre. The audit checks
    floor continuity inside it and, when `roofed`, a sealed envelope. Tags reach the game."""
    p = _frame().world(_vec3(pos, f'volume {name!r} pos'))
    t = [str(x) for x in tags]
    if not roofed:
        t.append('unroofed')
    level.volumes.append(Volume(name, p, _vec3(size, f'volume {name!r} size'), _frame().yaw + yaw, t))


def link(a: str, b: str, door: str | None = None) -> None:
    """Declare that a player can walk from volume `a` to volume `b` (through `door`, if named).
    The audit marches the route with a player-sized capsule."""
    level.links.append(Link(a, b, door))


def lamp(name: str, pos: Sequence[float], color, intensity: float = 8.0, distance: float = 20.0, decay: float = 2.0) -> None:
    """A point light. Point lights share a small pool in the engine — place them where it matters."""
    level.lights.append(PointLight(name, _frame().world(_vec3(pos, f'lamp {name!r} pos')), hex_color(color), intensity, distance, decay))


def spot(name: str, pos: Sequence[float], target: Sequence[float], color, intensity: float = 20.0, angle: float = math.pi / 4, penumbra: float = 0.3, cast_shadow: bool = True) -> None:
    """A spot light; the first two with `cast_shadow` bake shadows from the static level."""
    level.lights.append(SpotLight(name, _frame().world(_vec3(pos, f'spot {name!r} pos')), _frame().world(_vec3(target, f'spot {name!r} target')), hex_color(color), intensity, angle, penumbra, cast_shadow))


def landmark(name: str, pos: Sequence[float], yaw: float = 0.0, tags: Sequence[str] = ()) -> None:
    """A named point the game asks for by name (`level.landmark('exit')`, `landmarksTagged('guard')`)."""
    level.landmarks.append(Landmark(name, _frame().world(_vec3(pos, f'landmark {name!r} pos')), _frame().yaw + yaw, [str(t) for t in tags]))


def spawn(pos: Sequence[float], yaw: float = 0.0) -> None:
    """Where the player starts: the `spawn` landmark, which sync_world.py also writes into world.json."""
    landmark('spawn', pos, yaw)


# ---------------------------------------------------------------- output

def export(out_dir: str, name: str) -> dict:
    """Write `<name>.mesh-level.json`, `<name>.doors.json`, `<name>.blend` (named parts, editable)
    and `<name>.glb` (joined per material) into `out_dir`, and print the summary — including the
    exact `bitmagic assets add` line, whose `--height` must be the level's native height."""
    for l in level.links:
        names = {v.name for v in level.volumes}
        for end in (l.a, l.b):
            if end not in names:
                raise ValueError(f'link({l.a!r}, {l.b!r}): no volume named {end!r}')
        if l.door and l.door not in {d.id for d in level.doors}:
            raise ValueError(f'link({l.a!r}, {l.b!r}, door={l.door!r}): no door with that id')
    level_path, doors_path = level.write(out_dir, name)
    glb_path = os.path.join(out_dir, f'{name}.glb')
    blend_path = os.path.join(out_dir, f'{name}.blend')
    size = 0
    if not DRY_RUN:
        scene.save_blend(blend_path)
        size = scene.export_glb(glb_path)
    print(level.summary(name, glb_path), flush=True)
    overlaps, where = scene.coplanar_overlaps()
    if overlaps:
        # The same warning bmedit's export() prints for props: a still render cannot show the flicker.
        print(f'[bmlevel] WARNING {name}: {overlaps} overlapping coplanar face pair(s) will FLICKER in the game '
              f'(z-fighting), e.g. at {"; ".join(where)}. Offset the trim or panel 5 cm off the surface '
              f'(or inset it), or give the layers different depths. Fix before going on.', flush=True)
    print(f'WROTE {level_path} {doors_path}' + ('' if DRY_RUN else f' {blend_path} {glb_path} ({size} bytes)'), flush=True)
    return {'level': level_path, 'doors': doors_path, 'glb': glb_path, 'blend': blend_path, 'dry_run': DRY_RUN}
