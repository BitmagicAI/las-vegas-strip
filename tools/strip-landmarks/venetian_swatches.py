"""Render every Venetian interior material ('vi-*', venetian_materials.py) on a board, through export.py's own material
and UV code, to check colours, textures and normal maps before a build uses them.

blender -b --python tools/strip-landmarks/venetian_swatches.py   ->  build/venetian-interiors/swatches.png
"""
import sys, math
from pathlib import Path
import bpy
sys.path.insert(0, 'tools/strip-landmarks')
import export as E
import venetian_materials as VM

OUT = Path('build/venetian-interiors/swatch'); OUT.mkdir(parents=True, exist_ok=True)
E.OUT = OUT
names = list(VM.SPEC)
cols = 10
meshes = []


def quad(v, f, pts):
    n = len(v); v.extend(pts); f.extend([[n, n + 1, n + 2], [n, n + 2, n + 3]])


for i, k in enumerate(names):
    cx, cz = (i % cols) * 2.2, -(i // cols) * 2.6          # game X across, Y up; one swatch per material
    v, f = [], []
    # a 1.8 m panel facing the camera (+Z) and a short column in front of it (curved surfaces, smoothing)
    quad(v, f, [(cx - .9, cz + .1, 0), (cx + .9, cz + .1, 0), (cx + .9, cz + 1.9, 0), (cx - .9, cz + 1.9, 0)])
    n = 16
    for j in range(n):
        a0, a1 = j * math.tau / n, (j + 1) * math.tau / n
        p = lambda a, y: (cx + .45 + .22 * math.cos(a), cz + y, .5 + .22 * math.sin(a))
        quad(v, f, [p(a1, .1), p(a0, .1), p(a0, 1.3), p(a1, 1.3)])
    meshes.append(dict(property='swatch', source='swatch', material=k, detail=1, vertices=v, faces=f))
import json
(OUT / 'swatch.json').write_text(json.dumps(dict(meshes=meshes, labels=[])))

bpy.ops.wm.read_factory_settings(use_empty=True); E.materials.clear(); E.add('swatch')
for i, k in enumerate(names):
    cx, cz = (i % cols) * 2.2, -(i // cols) * 2.6
    cu = bpy.data.curves.new(k, 'FONT'); cu.body = k[3:]; cu.size = .2; cu.align_x = 'CENTER'
    o = bpy.data.objects.new(k + ' label', cu); bpy.context.collection.objects.link(o)
    o.location = (cx, 0.05, cz - .12); o.rotation_euler = (math.pi / 2, 0, 0)
w = (cols - 1) * 2.2; rows = math.ceil(len(names) / cols)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); bpy.context.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = w + 2.6
cam.location = (w / 2, -30, -(rows - 1) * 1.3 + 1.0); cam.rotation_euler = (math.pi / 2, 0, 0)
bpy.context.scene.camera = cam
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); bpy.context.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(60), math.radians(-25), math.radians(20))
world = bpy.data.worlds.new('w'); bpy.context.scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.35, .37, .4, 1)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.render.resolution_x = 2000; sc.render.resolution_y = int(2000 * (rows * 2.6 + .6) / (w + 2.6))
sc.view_settings.view_transform = 'AgX'
sc.render.filepath = str(Path('build/venetian-interiors/swatches.png').resolve())
bpy.ops.render.render(write_still=True)
print('SWATCHES', sc.render.filepath)
