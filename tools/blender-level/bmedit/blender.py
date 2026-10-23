"""The Blender half of bmedit: every builder, edit and the export. See __init__.py."""
from __future__ import annotations

import math
import os
import random
import re
from typing import Callable, Iterable, Optional, Sequence, Union

import bmesh
import bpy
from mathutils import Matrix, Vector

from bmedit.colour import Colour, distance, mix, to_hex, to_linear

__all__ = [
    'load', 'box', 'cylinder', 'cone', 'sphere', 'join', 'copy', 'move', 'remove', 'objects',
    'paint', 'recolor', 'replace_colour', 'palette', 'decimate', 'scatter', 'bounds', 'describe',
    'height_at', 'turn', 'part', 'anchor', 'export', 'mix',
]

MAX_EXPORTS = 8
_ID = re.compile(r'^[a-z0-9][a-z0-9_-]{0,63}$')
_state: dict = {'inputs': os.path.abspath('build/inputs'), 'out': os.path.abspath('build/assets'), 'exports': []}

Objects = Union[bpy.types.Object, Iterable[bpy.types.Object]]
Vec = Sequence[float]


def configure(inputs_dir: str, out_dir: str) -> None:
    """Where load() reads and export() writes. Called by the host before the script runs."""
    _state['inputs'] = os.path.abspath(inputs_dir)
    _state['out'] = os.path.abspath(out_dir)
    _state['exports'] = []


def exports() -> list[dict]:
    """What the script exported, for the host: [{id, file, targetHeight, triangles}]."""
    return list(_state['exports'])


# ---- coordinates ---------------------------------------------------------------------------

def _to_b(p: Vec) -> Vector:
    return Vector((p[0], -p[2], p[1]))


def _to_game(v: Vec) -> tuple[float, float, float]:
    return (v[0], v[2], -v[1])


def _list(objs: Objects) -> list[bpy.types.Object]:
    if isinstance(objs, bpy.types.Object):
        return [objs]
    return [o for o in objs if o.type == 'MESH']


def objects() -> list[bpy.types.Object]:
    """Every mesh object in the scene."""
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


# ---- load ----------------------------------------------------------------------------------

def load(input_id: str) -> list[bpy.types.Object]:
    """Import one of the job's input GLBs (the game asset with that id) and return its meshes.

    Transforms are applied, so every vertex position is where the game draws it."""
    if not _ID.match(input_id):
        raise ValueError(f'bad input id {input_id!r}')
    path = os.path.join(_state['inputs'], f'{input_id}.glb')
    if not os.path.exists(path):
        have = sorted(f[:-4] for f in os.listdir(_state['inputs'])) if os.path.isdir(_state['inputs']) else []
        raise FileNotFoundError(f'no input {input_id!r}; this job has {have}')
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == 'MESH']
    for o in new:
        if o.type != 'MESH':
            continue
        # Bake parent + own transform into the mesh, so positions are world positions.
        world = o.matrix_world.copy()
        o.parent = None
        o.data.transform(world)
        o.matrix_world = Matrix.Identity(4)
    for o in new:
        if o.type != 'MESH':
            bpy.data.objects.remove(o, do_unlink=True)
    for o in meshes:
        _face_up(o)
    return meshes


def _face_up(obj: bpy.types.Object) -> None:
    """Flip a mesh whose faces mostly point DOWN. Some generated grounds are wound inside-out and
    drawn double-sided; left as they are, `n[1] > 0.7` would find no flat ground to paint."""
    mesh = obj.data
    total = sum(p.area * p.normal.z for p in mesh.polygons)
    area = sum(p.area for p in mesh.polygons)
    if area > 0 and total / area < -0.3:
        mesh.flip_normals()
        print(f'[bmedit] {obj.name}: faces pointed down; flipped')


# ---- primitives ----------------------------------------------------------------------------

def _vertex_material() -> bpy.types.Material:
    mat = bpy.data.materials.get('bmedit_vertex')
    if mat is None:
        mat = bpy.data.materials.new('bmedit_vertex')
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes['Principled BSDF']
        bsdf.inputs['Roughness'].default_value = 1.0
        attr = nodes.new('ShaderNodeVertexColor')
        attr.layer_name = 'Col'
        mat.node_tree.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    return mat


def _finish(name: str, bm: bmesh.types.BMesh, color: Colour, at: Vec, yaw: float) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = False
    mesh.materials.append(_vertex_material())
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    _colour_layer(obj)
    _fill(obj, to_linear(color))
    # Straight into the vertices: the object keeps an identity transform, so every position a
    # later call reads (bounds, paint, scatter) is already where the game draws it.
    mesh.transform(Matrix.Translation(_to_b(at)) @ Matrix.Rotation(yaw, 4, 'Z'))
    return obj


def box(name: str, size: Vec, at: Vec = (0, 0, 0), color: Colour = '#999999', yaw: float = 0.0) -> bpy.types.Object:
    """A box `size` = (width x, height y, depth z) whose BOTTOM centre sits at `at`."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((size[0], size[2], size[1])), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector((0, 0, size[1] / 2)), verts=bm.verts)
    return _finish(name, bm, color, at, yaw)


def cylinder(name: str, radius: float, height: float, at: Vec = (0, 0, 0), color: Colour = '#999999',
             segments: int = 8, top_radius: Optional[float] = None, yaw: float = 0.0) -> bpy.types.Object:
    """An upright cylinder (or frustum, with top_radius) standing on `at`."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=max(3, segments),
                          radius1=radius, radius2=radius if top_radius is None else top_radius, depth=height)
    bmesh.ops.translate(bm, vec=Vector((0, 0, height / 2)), verts=bm.verts)
    return _finish(name, bm, color, at, yaw)


def cone(name: str, radius: float, height: float, at: Vec = (0, 0, 0), color: Colour = '#999999',
         segments: int = 8, yaw: float = 0.0) -> bpy.types.Object:
    """An upright cone standing on `at` — a pine layer, a roof tip, a spike."""
    return cylinder(name, radius, height, at, color, segments, top_radius=0.0, yaw=yaw)


def sphere(name: str, radius: float, at: Vec = (0, 0, 0), color: Colour = '#999999', detail: int = 1) -> bpy.types.Object:
    """A faceted ball centred on `at` (detail 1 = 80 faces, 2 = 320)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=max(1, min(3, detail)), radius=radius)
    return _finish(name, bm, color, at, 0.0)


# ---- object edits --------------------------------------------------------------------------

def join(objs: Objects, name: str) -> bpy.types.Object:
    """Merge meshes into one object (one draw call in the game)."""
    items = _list(objs)
    if not items:
        raise ValueError('join() needs at least one mesh')
    for o in items:
        _colour_layer(o)
    with bpy.context.temp_override(active_object=items[0], selected_editable_objects=items, selected_objects=items):
        bpy.ops.object.join()
    items[0].name = name
    items[0].data.name = name
    return items[0]


def copy(obj: bpy.types.Object, at: Optional[Vec] = None, yaw: float = 0.0, scale: float = 1.0,
         name: Optional[str] = None) -> bpy.types.Object:
    """A copy of `obj`, rotated by `yaw` and scaled about its bottom centre, then moved so that
    bottom centre sits at `at` (default: where it was)."""
    dup = obj.copy()
    dup.data = obj.data.copy()
    dup.name = name or f'{obj.name}.copy'
    bpy.context.scene.collection.objects.link(dup)
    move(dup, at=at, yaw=yaw, scale=scale)
    return dup


def move(obj: bpy.types.Object, at: Optional[Vec] = None, yaw: float = 0.0, scale: float = 1.0) -> None:
    """Rotate/scale `obj` about its bottom centre, then put that point at `at` (game coords)."""
    lo, hi = bounds(obj)
    base = Vector(_to_b(((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)))
    target = _to_b(at) if at is not None else base
    m = Matrix.Translation(target) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Scale(scale, 4) @ Matrix.Translation(-base)
    obj.data.transform(m)


def turn(objs: Objects, angle: float, axis: Vec = (0, 1, 0), about: Optional[Vec] = None) -> None:
    """Rotate by `angle` radians about `axis` (game coords, right-handed: about +Z, +Y turns toward
    -X) through the point `about` (default: the objects' box centre). A spoke is a box standing on
    the hub turned about the hub; a leaning leg is turned about its foot."""
    items = _list(objs)
    if about is None:
        lo, hi = bounds(items)
        about = tuple((lo[k] + hi[k]) / 2 for k in range(3))
    pivot = _to_b(about)
    a = _to_b(axis)
    m = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, Vector(a).normalized()) @ Matrix.Translation(-pivot)
    for o in items:
        o.data.transform(m)
        for child in o.children:
            child.location = m @ child.location


def remove(objs: Objects) -> None:
    for o in _list(objs):
        bpy.data.objects.remove(o, do_unlink=True)


def decimate(objs: Objects, ratio: float) -> None:
    """Keep about `ratio` (0..1) of each mesh's triangles — cheaper, chunkier."""
    for o in _list(objs):
        mod = o.modifiers.new('decimate', 'DECIMATE')
        mod.ratio = max(0.01, min(1.0, ratio))
        with bpy.context.temp_override(object=o, active_object=o):
            bpy.ops.object.modifier_apply(modifier=mod.name)


# ---- colour --------------------------------------------------------------------------------

def _colour_layer(obj: bpy.types.Object):
    """The object's face-corner colour attribute — an imported GLB's own COLOR_0 (byte or float:
    both read and write linear `.color`), else a new one filled from its materials' colours, with
    the materials switched to show it (white base, colour from the attribute)."""
    mesh = obj.data
    attrs = mesh.color_attributes
    layer = attrs.active_color
    if layer is not None and layer.domain == 'CORNER':
        return layer
    old = layer
    new = attrs.new('Col', 'FLOAT_COLOR', 'CORNER')
    base = [_material_colour(m) for m in mesh.materials] or [(0.8, 0.8, 0.8, 1.0)]
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            if old is not None:  # a POINT-domain layer: each corner takes its vertex's colour
                new.data[li].color = old.data[mesh.loops[li].vertex_index].color
            else:
                new.data[li].color = base[min(poly.material_index, len(base) - 1)]
    attrs.active_color = new
    # The glTF exporter's 'ACTIVE' mode writes the RENDER colour attribute.
    attrs.default_color_name = new.name
    for mat in mesh.materials:
        _show_vertex_colour(mat, new.name)
    return new


def _material_colour(mat) -> tuple[float, float, float, float]:
    if mat is None:
        return (0.8, 0.8, 0.8, 1.0)
    if mat.use_nodes and 'Principled BSDF' in mat.node_tree.nodes:
        c = mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
        return (c[0], c[1], c[2], 1.0)
    c = mat.diffuse_color
    return (c[0], c[1], c[2], 1.0)


def _show_vertex_colour(mat, layer_name: str) -> None:
    """Base colour from the attribute, unless an image texture drives it (then the attribute tints)."""
    if mat is None or not mat.use_nodes or 'Principled BSDF' not in mat.node_tree.nodes:
        return
    for node in mat.node_tree.nodes:
        if node.bl_idname == 'ShaderNodeVertexColor':
            node.layer_name = layer_name
            return
    bsdf = mat.node_tree.nodes['Principled BSDF']
    base = bsdf.inputs['Base Color']
    if base.is_linked:
        return
    base.default_value = (1.0, 1.0, 1.0, 1.0)
    attr = mat.node_tree.nodes.new('ShaderNodeVertexColor')
    attr.layer_name = layer_name
    mat.node_tree.links.new(attr.outputs['Color'], base)


def _fill(obj: bpy.types.Object, rgba) -> None:
    layer = _colour_layer(obj)
    for d in layer.data:
        d.color = rgba


def _faces(obj: bpy.types.Object):
    """(polygon, game centre, game normal, current sRGB hex) per face."""
    layer = _colour_layer(obj)
    mesh = obj.data
    # The shading normals (an imported GLB's own NORMAL data), not the winding: generated grounds
    # are often wound the other way and drawn double-sided, so poly.normal can point down.
    corners = mesh.corner_normals
    for poly in mesh.polygons:
        c = layer.data[poly.loop_indices[0]].color
        n = Vector((0.0, 0.0, 0.0))
        for li in poly.loop_indices:
            n += corners[li].vector
        n = n.normalized() if n.length > 1e-9 else poly.normal
        yield poly, _to_game(poly.center), _to_game(n), to_hex(c), layer


def paint(objs: Objects, fn: Callable[[tuple, tuple, str], Optional[Colour]]) -> int:
    """Call fn(position, normal, current_hex) for every face; a colour it returns repaints that
    face, None keeps it. Position and normal are game coords (normal[1] > 0.7: roughly flat
    ground; < 0.3: steep or a wall). Returns the number of faces repainted."""
    changed = 0
    for o in _list(objs):
        for poly, pos, normal, current, layer in _faces(o):
            out = fn(pos, normal, current)
            if out is None:
                continue
            rgba = to_linear(out)
            for li in poly.loop_indices:
                layer.data[li].color = rgba
            changed += 1
    return changed


def recolor(objs: Objects, colour: Colour, where: Optional[Callable[[tuple, tuple, str], bool]] = None) -> int:
    """Paint every face (or those `where(position, normal, current_hex)` accepts) one colour."""
    return paint(objs, lambda p, n, c: colour if where is None or where(p, n, c) else None)


def replace_colour(objs: Objects, mapping: dict, tolerance: float = 0.08) -> int:
    """Swap colours: {'#3f8f3a': '#eef3f7', ...}. A face within `tolerance` of a key takes its
    value — the way to turn 'the green of the leaves' white without touching the bark."""
    keys = list(mapping.items())

    def swap(_p, _n, current):
        best = min(keys, key=lambda kv: distance(kv[0], current))
        return best[1] if distance(best[0], current) <= tolerance else None
    return paint(objs, swap)


def palette(objs: Objects, top: int = 12) -> list[tuple[str, int]]:
    """The face colours in use, most common first, as [(hex, faces)] — printed too, so the build
    log shows what an edit has to work with. Near-identical colours are merged."""
    counts: dict[str, int] = {}
    for o in _list(objs):
        for _poly, _p, _n, current, _l in _faces(o):
            for known in counts:
                if distance(known, current) < 0.03:
                    counts[known] += 1
                    break
            else:
                counts[current] = 1
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])[:top]
    print('[bmedit] palette: ' + ', '.join(f'{h} x{n}' for h, n in ranked))
    return ranked


# ---- placement -----------------------------------------------------------------------------

def bounds(objs: Objects) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """(min, max) corners in game coords over every vertex."""
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for o in _list(objs):
        for v in o.data.vertices:
            g = _to_game(o.matrix_world @ v.co)
            for i in range(3):
                lo[i] = min(lo[i], g[i])
                hi[i] = max(hi[i], g[i])
    if lo[0] == math.inf:
        return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
    return (lo[0], lo[1], lo[2]), (hi[0], hi[1], hi[2])


def height_at(objs: Objects, x: float, z: float) -> Optional[float]:
    """The top surface's height at game (x, z), or None off the mesh."""
    best = None
    for o in _list(objs):
        origin = _to_b((x, 1e4, z))
        hit, loc, _n, _i = o.ray_cast(o.matrix_world.inverted() @ origin, Vector((0, 0, -1)))
        if hit:
            y = _to_game(o.matrix_world @ loc)[1]
            best = y if best is None else max(best, y)
    return best


def scatter(proto: bpy.types.Object, count: int, on: Optional[Objects] = None,
            area: Sequence[float] = (0.0, 0.0, 20.0), seed: int = 1, min_spacing: float = 2.0,
            scale: Sequence[float] = (0.8, 1.2), avoid: Sequence[Sequence[float]] = (),
            max_slope: float = 0.5) -> list[bpy.types.Object]:
    """Place up to `count` copies of `proto` at random inside the circle `area` = (x, z, radius),
    random yaw and scale, standing on `on`'s surface (flat enough: normal-y >= 1 - max_slope).
    `avoid` = [(x, z, radius), ...] keeps spots clear (the spawn, a path). Returns the copies."""
    rng = random.Random(seed)
    placed: list[tuple[float, float]] = []
    out = []
    ground = _list(on) if on is not None else []
    for _ in range(count * 30):
        if len(out) >= count:
            break
        a = rng.uniform(0, math.tau)
        r = area[2] * math.sqrt(rng.random())
        x, z = area[0] + r * math.cos(a), area[1] + r * math.sin(a)
        if any((x - px) ** 2 + (z - pz) ** 2 < min_spacing ** 2 for px, pz in placed):
            continue
        if any((x - ax) ** 2 + (z - az) ** 2 < ar ** 2 for ax, az, ar in avoid):
            continue
        y = 0.0
        if ground:
            hit = _surface(ground, x, z)
            if hit is None or hit[1] < 1.0 - max_slope:
                continue
            y = hit[0]
        out.append(copy(proto, at=(x, y, z), yaw=rng.uniform(0, math.tau), scale=rng.uniform(*scale),
                        name=f'{proto.name}.{len(out)}'))
        placed.append((x, z))
    return out


def _surface(objs: list, x: float, z: float) -> Optional[tuple[float, float]]:
    best = None
    for o in objs:
        origin = o.matrix_world.inverted() @ _to_b((x, 1e4, z))
        hit, loc, normal, _i = o.ray_cast(origin, Vector((0, 0, -1)))
        if hit:
            y = _to_game(o.matrix_world @ loc)[1]
            if best is None or y > best[0]:
                best = (y, _to_game(normal)[1])
    return best


def describe(objs: Objects) -> None:
    """Print name, triangle count and size of each mesh — cheap orientation for an edit."""
    for o in _list(objs):
        lo, hi = bounds(o)
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        size = tuple(round(hi[i] - lo[i], 2) for i in range(3))
        print(f'[bmedit] {o.name}: {tris} tris, size {size}, min {tuple(round(v, 2) for v in lo)}')


# ---- export --------------------------------------------------------------------------------

def _coplanar_overlaps(items: list, limit: int = 5) -> tuple[int, list[str]]:
    """Faces that lie in the same plane, facing the same way, and overlap: they z-fight (flicker
    between their colours) in the game. Typical cause: trim laid flush on a surface — a rim whose
    top cap sits at the platform's height, a stripe on a wall. Returns (count, examples)."""
    faces = []
    for o in items:
        layer = o.data.color_attributes.active_color
        for poly in o.data.polygons:
            n = poly.normal
            if n.length < 1e-6:
                continue
            pts = [o.data.vertices[v].co.copy() for v in poly.vertices]
            colour = to_hex(layer.data[poly.loop_indices[0]].color) if layer and layer.domain == 'CORNER' else '?'
            faces.append((n.normalized(), n.normalized().dot(pts[0]), pts, poly.center.copy(), poly.area, colour))
    buckets: dict = {}
    for i, (n, d, _p, _c, _a, _col) in enumerate(faces):
        key = (round(n.x, 2), round(n.y, 2), round(n.z, 2), round(d * 200))   # same direction, within ~5 mm
        buckets.setdefault(key, []).append(i)

    def inside(point, pts, n) -> bool:
        # Convex polygon test in its own plane: the point is on the inner side of every edge.
        sign = 0
        for k in range(len(pts)):
            edge = pts[(k + 1) % len(pts)] - pts[k]
            side = n.dot(edge.cross(point - pts[k]))
            if abs(side) < 1e-7:
                continue
            if sign == 0:
                sign = 1 if side > 0 else -1
            elif (side > 0) != (sign > 0):
                return False
        return True

    count, examples = 0, []
    for group in buckets.values():
        if len(group) < 2:
            continue
        for x in range(len(group)):
            for y in range(x + 1, len(group)):
                fa, fb = faces[group[x]], faces[group[y]]
                small, big = (fa, fb) if fa[4] <= fb[4] else (fb, fa)
                # Two faces of one colour flicker between identical pixels: invisible, not reported.
                if small[5] == big[5] or not inside(small[3], big[2], big[0]):
                    continue
                count += 1
                if len(examples) < limit:
                    g = _to_game(small[3])
                    examples.append(f'({g[0]:.2f}, {g[1]:.2f}, {g[2]:.2f}) {small[5]} vs {big[5]}')
    return count, examples


PART_PREFIX = 'BM_part_'
_PART_NAME = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')
MOTIONS = ('spin', 'upright', 'pendulum', 'none')


def part(obj: bpy.types.Object, name: str) -> bpy.types.Object:
    """Mark `obj` as the moving part `name` of a smart prop (export it with `smart=`). A part
    is one object: join its pieces first. Names: letters, digits and _, starting with a letter."""
    if not _PART_NAME.match(name):
        raise ValueError(f'part name {name!r}: letters, digits and _, starting with a letter')
    obj.name = f'{PART_PREFIX}{name}'
    obj.data.name = obj.name
    return obj


ANCHOR_PREFIX = 'BM_anchor_'


def anchor(obj: bpy.types.Object, name: str, at: Vec) -> bpy.types.Object:
    """A named point game code will want: a door, an entrance, a seat, a cabin floor. `at` is in
    game coordinates at rest. On a part (after part()) it rides with the part and code finds it as
    `smart.pivotOf(id, 'cabin_3').getObjectByName('BM_anchor_floor')` — every part may reuse the
    same names. On any other exported object it stays put, found on the placed object:
    `getObjectIdService().getObjectById(id).getObjectByName('BM_anchor_door')` — so those names
    must be unique within the prop."""
    if not _PART_NAME.match(name):
        raise ValueError(f'anchor name {name!r}: letters, digits and _, starting with a letter')
    owner = obj.name[len(PART_PREFIX):] if obj.name.startswith(PART_PREFIX) else re.sub(r'[^A-Za-z0-9_]', '_', obj.name)
    empty = bpy.data.objects.new(f'{ANCHOR_PREFIX}{owner}__{name}', None)
    bpy.context.scene.collection.objects.link(empty)
    empty.parent = obj  # the part keeps an identity transform, so `at` is also its local position
    empty.location = _to_b(at)
    return empty


def _vec(value, what: str) -> dict:
    if not (isinstance(value, (list, tuple)) and len(value) == 3):
        raise ValueError(f'{what} must be (x, y, z)')
    return {'x': float(value[0]), 'y': float(value[1]), 'z': float(value[2])}


def _smart_declaration(smart: dict, items: list, lo, hi) -> tuple[dict, list[dict]]:
    """Validate `smart` against the exported objects; return the GLB's bmSmartObject extras and
    the asset-record light emitters (offsets in the asset frame: bottom-centre origin)."""
    names = {o.name[len(PART_PREFIX):]: o for o in items if o.name.startswith(PART_PREFIX)}
    parts = []
    for p in smart.get('parts', []):
        name = p.get('name')
        if name not in names:
            raise ValueError(f'smart part {name!r} has no object: call part(obj, {name!r}) on one of the exported objects')
        motion = dict(p.get('motion') or {})
        if motion.get('kind') not in MOTIONS:
            raise ValueError(f'smart part {name!r}: motion kind must be one of {MOTIONS}')
        if 'axis' in motion:
            motion['axis'] = [float(v) for v in motion['axis']]
        entry = {'name': name, 'motion': motion}
        if p.get('parent'):
            if p['parent'] not in names:
                raise ValueError(f'smart part {name!r}: parent {p["parent"]!r} is not a part')
            entry['parent'] = p['parent']
        if p.get('pivot') is not None:
            entry['pivot'] = _vec(p['pivot'], f'smart part {name!r} pivot')
        parts.append(entry)
    origin = ((lo[0] + hi[0]) / 2, lo[1], (lo[2] + hi[2]) / 2)
    lights = []
    for i, l in enumerate(smart.get('lights', [])):
        if 'color' not in l:
            raise ValueError('a smart light needs a color')
        where = l.get('position')
        if where is None:
            if l.get('part') not in names:
                raise ValueError('a smart light needs a position, or a part to sit at the centre of')
            plo, phi = bounds(names[l['part']])
            where = tuple((plo[k] + phi[k]) / 2 for k in range(3))
        offset = {'x': where[0] - origin[0], 'y': where[1] - origin[1], 'z': where[2] - origin[2]}
        emitter = {'color': to_hex(to_linear(l['color'])), 'offset': offset}
        for key in ('intensity', 'distance'):
            if key in l:
                emitter[key] = float(l[key])
        if l.get('part'):
            if l['part'] not in names:
                raise ValueError(f'smart light: part {l["part"]!r} is not a part')
            emitter['part'] = l['part']
        lights.append(emitter)
    return {'parts': parts}, lights


def export(asset_id: str, objs: Optional[Objects] = None, smart: Optional[dict] = None) -> dict:
    """Write `objs` (default: every mesh in the scene) as the game asset `asset_id`. An id the game
    already has REPLACES that asset everywhere it is placed; a new id adds one, sized to the
    meshes' real height. Returns {id, targetHeight, triangles}.

    `smart` makes it a SMART OBJECT the engine animates with no game code:
        {'parts': [{'name': 'wheel', 'motion': {'kind': 'spin', 'axis': (0, 0, 1), 'rpm': 3}},
                   {'name': 'cabin_1', 'parent': 'wheel', 'motion': {'kind': 'upright'}}],
         'lights': [{'color': '#ffd27a', 'part': 'cabin_1', 'intensity': 4}]}
    Every part is an exported object marked with part(obj, name). Pivots default to the part's
    box centre (the top centre for upright / pendulum); give 'pivot': (x, y, z) to override."""
    if not _ID.match(asset_id):
        raise ValueError(f'asset id {asset_id!r}: use lowercase letters, digits, - and _')
    if any(e['id'] == asset_id for e in _state['exports']):
        raise ValueError(f'{asset_id!r} was already exported in this script')
    if len(_state['exports']) >= MAX_EXPORTS:
        raise ValueError(f'at most {MAX_EXPORTS} exports per script')
    items = _list(objs) if objs is not None else objects()
    if not items:
        raise ValueError('nothing to export')
    for o in items:
        _colour_layer(o)
    lo, hi = bounds(items)
    overlaps, where = _coplanar_overlaps(items)
    if overlaps:
        print(f'[bmedit] WARNING {asset_id}: {overlaps} overlapping coplanar face pair(s) will FLICKER in the game '
              f'(z-fighting), e.g. at {"; ".join(where)}. Lift the upper surface by at least 1 cm, or make '
              f'the trim not cover the surface under it.')
    extras, lights = _smart_declaration(smart, items, lo, hi) if smart else (None, [])
    scene = bpy.context.scene
    if extras is not None:
        scene['bmSmartObject'] = extras  # scene custom properties are the GLB's scene extras
    os.makedirs(_state['out'], exist_ok=True)
    path = os.path.join(_state['out'], f'{asset_id}.glb')
    try:
        anchors = [c for o in items for c in o.children if c.name.startswith(ANCHOR_PREFIX)]
        chosen = items + anchors
        with bpy.context.temp_override(selected_objects=chosen, selected_editable_objects=chosen):
            bpy.ops.object.select_all(action='DESELECT')
            for o in chosen:
                o.select_set(True)
            bpy.ops.export_scene.gltf(
                filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                export_normals=True, export_vertex_color='ACTIVE', export_lights=False, export_cameras=False,
                export_extras=extras is not None,
            )
    finally:
        if 'bmSmartObject' in scene:
            del scene['bmSmartObject']
    record = {
        'id': asset_id,
        'file': f'{asset_id}.glb',
        'targetHeight': round(max(0.01, hi[1] - lo[1]), 3),
        'triangles': sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in items),
    }
    if extras is not None:
        record['smartParts'] = [p['name'] for p in extras['parts']]
    if lights:
        record['lights'] = lights
    _state['exports'].append(record)
    moving = f', smart: {", ".join(record["smartParts"])}' if extras else ''
    print(f'[bmedit] exported {asset_id}: {record["triangles"]} tris, {record["targetHeight"]} m tall{moving}')
    return record
