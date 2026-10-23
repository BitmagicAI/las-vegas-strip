"""Headless review renders of GLB assets (bmedit exports), run inside Blender:

    "$BLENDER" -b --python tools/blender-level/review_asset.py -- <out dir> <a.glb> [<b.glb> ...] [--engine eevee|cycles]

Renders each asset alone from two three-quarter angles — front-left and back-right, from above,
framed to its size — into the output directory, plus `contact-sheet.png` with all of them (two
columns per asset, in the order given; at most four assets). It is a look at shape and colour:
a flat sky light and a sun, vertex colours as authored. Blender is not three.js — trust "wrong
colour family", "too dark", "floating", not an exact shade.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
ENGINE = argv[argv.index('--engine') + 1].lower() if '--engine' in argv and argv.index('--engine') + 1 < len(argv) else 'eevee'
positional = [a for a in argv if not a.startswith('--') and a != ENGINE]
if len(positional) < 2 or ENGINE not in ('eevee', 'cycles'):
    print(__doc__)
    sys.exit(2)
OUT, GLBS = positional[0], positional[1:5]
WIDTH, HEIGHT = 640, 480
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def use_cycles() -> str:
    """Cycles on the first GPU backend that has a device (OptiX, then CUDA), else the CPU."""
    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    backend = 'CPU'
    for kind in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = kind
        except TypeError:
            continue
        prefs.get_devices()
        if any(d.type == kind for d in prefs.devices):
            for d in prefs.devices:
                d.use = d.type == kind
            backend = kind
            break
    scene.cycles.device = 'CPU' if backend == 'CPU' else 'GPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    return backend


if ENGINE == 'cycles':
    print(f'ENGINE cycles on {use_cycles()}', flush=True)
else:
    engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    if hasattr(scene, 'eevee'):
        scene.eevee.taa_render_samples = 16
scene.render.resolution_x, scene.render.resolution_y = WIDTH, HEIGHT
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.world = bpy.data.worlds.new('review')
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.45, 0.55, 0.7, 1)
bg.inputs[1].default_value = 0.7

cam_data = bpy.data.cameras.new('review')
cam_data.lens = 35
cam = bpy.data.objects.new('review', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
sun_data = bpy.data.lights.new('review-sun', 'SUN')
sun_data.energy = 3.0
sun = bpy.data.objects.new('review-sun', sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(45), math.radians(10), math.radians(35))


def load(path: str) -> list:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def frame(objs: list) -> tuple[Vector, float]:
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == 'MESH' for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2, max((hi - lo).length / 2, 0.1)


paths: list[str] = []
names: list[str] = []
for glb in GLBS:
    stem = os.path.splitext(os.path.basename(glb))[0]
    objs = load(glb)
    centre, radius = frame(objs)
    distance = radius / math.tan(math.radians(20)) * 1.1
    # Blender is Z up; the game's +Z forward is Blender's -Y, so "front" looks from -Y.
    for label, yaw in (('front', math.radians(-35)), ('back', math.radians(145))):
        direction = Vector((math.sin(yaw), -math.cos(yaw), 0.55)).normalized()
        cam.location = centre + direction * distance
        cam.rotation_euler = (centre - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cam_data.clip_end = distance * 4
        path = os.path.join(OUT, f'{stem}-{label}.png')
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        paths.append(path)
        names.append(f'{stem}-{label}')
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)

import numpy as np  # Blender bundles numpy  # noqa: E402

cols = 2
thumb_w, thumb_h = WIDTH // 2, HEIGHT // 2
rows = math.ceil(len(paths) / cols)
sheet = np.zeros((rows * thumb_h, cols * thumb_w, 4), dtype=np.float32)
sheet[..., 3] = 1
for i, p in enumerate(paths):
    img = bpy.data.images.load(p)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
    small = px[::2, ::2][:thumb_h, :thumb_w]
    r, c = divmod(i, cols)
    y0 = (rows - 1 - r) * thumb_h  # Blender image rows run bottom-up
    sheet[y0:y0 + small.shape[0], c * thumb_w:c * thumb_w + small.shape[1]] = small
    bpy.data.images.remove(img)
out_img = bpy.data.images.new('contact', cols * thumb_w, rows * thumb_h, alpha=True)
out_img.pixels = sheet.ravel().tolist()
sheet_path = os.path.join(OUT, 'contact-sheet.png')
out_img.filepath_raw = sheet_path
out_img.file_format = 'PNG'
out_img.save()
order = ', '.join(f'{i + 1}:{n}' for i, n in enumerate(names))
print(f'CONTACT_SHEET {sheet_path} ({cols} per row, left to right, top to bottom: {order})')
