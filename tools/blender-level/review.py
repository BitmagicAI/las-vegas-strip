"""Headless review renders of a built level, run inside Blender:

    "$BLENDER" -b --python tools/blender-level/review.py -- build/level/hut.blend build/level/hut.mesh-level.json build/level/review/
        [--lighting review|game] [--shot 'FROM -> TO']... [--only] [--fov <degrees>] [--engine eevee|cycles]

Opens the .blend (named parts intact) and renders a deterministic set of shots from the level
JSON — `overview` (top-down), `door-<id>-a/b` (both approaches of every door), `stairs-<name>`
(from the foot), `volume-<name>` (inside every room) — into the output directory, plus
`contact-sheet.png` with all of them. Read the sheet, then the shots that look wrong.

`--shot` adds a frame you aim yourself: both ends are `landmark:<name>`, `volume:<name>`,
`door:<id>` or a raw `x,y,z` in game coordinates, and `'FROM'` alone looks at the level's centre.
Repeat it; `--only` renders just those and skips the standard set and the sheet, which is the
one-render look at the thing you just changed.

`--lighting review` (the default) mounts a camera fill and a sun so nothing hides in shadow: this
is a look at the GEOMETRY. `--lighting game` instead runs the engine's `interior` preset and the
`lamp()`s and `spot()`s the level JSON declares, so the lighting pass can be judged here rather
than through a `bitmagic verify`. EEVEE is not three.js — trust "too dark" and "too bright", not
an exact colour.

`--engine cycles` renders with Cycles instead of EEVEE, on the GPU through OptiX or CUDA when
there is one, else on the CPU. EEVEE needs an OpenGL context, which a headless Linux server with
only the CUDA driver (no EGL) cannot give it; Cycles in background mode needs none.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmlevel.core import custom_shot, review_cameras, to_blender  # noqa: E402

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
positional = [a for a in argv if not a.startswith('--')]


def flag_value(name: str, default: str | None = None) -> str | None:
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def flag_values(name: str) -> list[str]:
    return [argv[i + 1] for i, a in enumerate(argv) if a == name and i + 1 < len(argv)]


# `--shot`, `--lighting` and `--fov` each consume the token after them, which would otherwise read
# as a positional path.
consumed = {argv[i + 1] for i, a in enumerate(argv) if a in ('--shot', '--lighting', '--fov', '--engine') and i + 1 < len(argv)}
positional = [a for a in positional if a not in consumed]
if len(positional) < 3:
    print(__doc__)
    sys.exit(2)
BLEND, LEVEL_PATH, OUT = positional[0], positional[1], positional[2]
LIGHTING = (flag_value('--lighting', 'review') or 'review').lower()
if LIGHTING not in ('review', 'game'):
    print(f"--lighting takes 'review' or 'game', not {LIGHTING!r}")
    sys.exit(2)
SHOT_SPECS = flag_values('--shot')
ONLY = '--only' in argv
FOV = float(flag_value('--fov')) if flag_value('--fov') else None
ENGINE = (flag_value('--engine', 'eevee') or 'eevee').lower()
if ENGINE not in ('eevee', 'cycles'):
    print(f"--engine takes 'eevee' or 'cycles', not {ENGINE!r}")
    sys.exit(2)
if ONLY and not SHOT_SPECS:
    print('--only needs at least one --shot')
    sys.exit(2)
WIDTH, HEIGHT = 960, 540
DEFAULT_LENS = 24.0

level = json.load(open(LEVEL_PATH))
doors_path = LEVEL_PATH.replace('.mesh-level.json', '.doors.json')
doors = json.load(open(doors_path)) if os.path.exists(doors_path) else []
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=os.path.abspath(BLEND))
scene = bpy.context.scene


def use_cycles() -> str:
    """Cycles on the first GPU backend that has a device (OptiX, then CUDA), else the CPU. Low
    samples plus the denoiser: this is a look at geometry, not a beauty render."""
    scene.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    backend = 'CPU'
    for kind in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = kind
        except TypeError:  # this Blender build lacks the backend
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
if scene.world is None:
    scene.world = bpy.data.worlds.new('review')
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.35, 0.4, 0.5, 1)
# The engine's `interior` preset holds environment at 0.22 and the skybox at 0.3 against an
# ambient floor of 0.8 (engine/agent-docs/mesh-level.md); a world background is EEVEE's nearest
# equivalent to that plus the retargeted HemisphereLight. `review` lights it flat instead.
bg.inputs[1].default_value = 0.6 if LIGHTING == 'review' else 0.35

cam_data = bpy.data.cameras.new('review')
cam = bpy.data.objects.new('review', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
fill_data = bpy.data.lights.new('review-fill', 'POINT')
fill_data.energy = 400
fill_data.shadow_soft_size = 2
fill = bpy.data.objects.new('review-fill', fill_data)
scene.collection.objects.link(fill)
sun_data = bpy.data.lights.new('review-sun', 'SUN')
# The engine dims its sun to 8% indoors; `review` keeps a full one so geometry reads everywhere.
sun_data.energy = 2.5 if LIGHTING == 'review' else 2.5 * 0.08
sun = bpy.data.objects.new('review-sun', sun_data)
scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))
if LIGHTING == 'game':
    fill.hide_render = True


def hex_rgb(value) -> tuple[float, float, float]:
    """`#rrggbb` (or a three.js colour number) to linear-ish rgb. The level JSON writes hex."""
    if isinstance(value, str):
        h = value.lstrip('#')
        n = int(h, 16) if h else 0xFFFFFF
    else:
        n = int(value)
    return (((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255)


def add_level_lights() -> int:
    """The JSON's own lamps and spots as real EEVEE lights. three.js intensities are unitless and
    Blender's are watts; 30 W per unit puts a default `lamp(intensity=8)` where the eye expects a
    room light. The engine pools point lights (a room with eight lamps gets four in game) — this
    lights all of them, so read brightness, not count."""
    for light in level.get('lights', []):
        color = hex_rgb(light.get('color', '#ffffff'))
        if light['type'] == 'point':
            data = bpy.data.lights.new(light['name'], 'POINT')
            data.energy = light.get('intensity', 8.0) * 30
            data.shadow_soft_size = 0.25
            obj = bpy.data.objects.new(light['name'], data)
            obj.location = to_blender(light['position'])
        else:
            data = bpy.data.lights.new(light['name'], 'SPOT')
            data.energy = light.get('intensity', 20.0) * 30
            # three.js `angle` is the half-cone; Blender's `spot_size` is the full one.
            data.spot_size = min(light.get('angle', math.pi / 4) * 2, math.pi)
            data.spot_blend = light.get('penumbra', 0.3)
            data.shadow_soft_size = 0.1
            data.use_shadow = bool(light.get('castShadow', True))
            obj = bpy.data.objects.new(light['name'], data)
            pos = Vector(to_blender(light['position']))
            obj.location = pos
            obj.rotation_euler = (Vector(to_blender(light['target'])) - pos).to_track_quat('-Z', 'Y').to_euler()
        data.color = color
        scene.collection.objects.link(obj)
    return len(level.get('lights', []))


if LIGHTING == 'game':
    print(f'LIGHTING game — interior preset, {add_level_lights()} level lights, emissive materials as authored')


def render(shot: dict) -> str:
    pos = Vector(to_blender(shot['position']))
    target = Vector(to_blender(shot['target']))
    cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    if shot['kind'] == 'ortho':
        cam_data.type = 'ORTHO'
        sx, sz = shot['extent']
        cam_data.ortho_scale = max(sx, sz * WIDTH / HEIGHT) * 1.15  # fit both axes into a 16:9 frame
        fill.hide_render = True
    else:
        cam_data.type = 'PERSP'
        fov = shot.get('fov', FOV)
        if fov:
            cam_data.lens_unit = 'FOV'
            cam_data.angle = math.radians(fov)
        else:
            cam_data.lens_unit = 'MILLIMETERS'
            cam_data.lens = DEFAULT_LENS
        fill.hide_render = LIGHTING == 'game'
        fill.location = pos + Vector((0, 0, 0.6))
    path = os.path.join(OUT, f"{shot['name']}.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


shots = [] if ONLY else review_cameras(level, doors)
shots += [custom_shot(spec, i + 1, level, doors, FOV) for i, spec in enumerate(SHOT_SPECS)]
paths = [render(s) for s in shots]
for s, p in zip(shots, paths):
    print(f"SHOT {s['name']} -> {p}" + (f"  ({s['spec']})" if 'spec' in s else ''))

if ONLY:
    sys.exit(0)

# Contact sheet: every shot at half size, four per row, labelled by file name in the log.
import numpy as np  # Blender bundles numpy  # noqa: E402

cols = 4
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
order = ', '.join(f'{i + 1}:{s["name"]}' for i, s in enumerate(shots))
print(f'CONTACT_SHEET {sheet_path} ({cols} per row, left to right, top to bottom: {order})')
