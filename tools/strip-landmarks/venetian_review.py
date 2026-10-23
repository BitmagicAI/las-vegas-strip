"""Offline review of the Venetian interiors (2026-10-23).

  blender -b --python tools/strip-landmarks/venetian_review.py -- export <dir> <name> ...
      export <dir>/<name>.json to <dir>/<name>.glb with export.py's materials (no version.json; for test scenes)
  blender -b --python tools/strip-landmarks/venetian_review.py -- render <key> [view ...] [--dir D] [--with name ...]
      render the venue's 'vi-*' views (or the ones named) from D (default build/strip-landmarks) with EEVEE: world
      ambient plus the venue's lights, like the game's interior lighting; --with adds other GLBs (e.g.
      venetian-exterior) for context. Writes build/venetian-interiors/review/<key>-<view>.png

Run it through tools/strip-landmarks/vi_blender.sh when other agents may be using Blender.
"""
import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0, 'tools/strip-landmarks')

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
REVIEW = Path('build/venetian-interiors/review'); REVIEW.mkdir(parents=True, exist_ok=True)


def pt(p): return Vector((p[0], -p[2], p[1]))


def opt(name, default=None, many=False):
    if name not in args: return default
    i = args.index(name)
    if not many: return args[i + 1]
    out = []
    for a in args[i + 1:]:
        if a.startswith('--'): break
        out.append(a)
    return out


if args[0] == 'export':
    import export as E
    d = Path(args[1]); E.OUT = d
    for name in args[2:]:
        bpy.ops.wm.read_factory_settings(use_empty=True); E.materials.clear(); E.add(name)
        bpy.ops.export_scene.gltf(filepath=str((d / (name + '.glb')).resolve()), export_format='GLB', export_yup=True, export_extras=True,
                                  export_lights=False, export_cameras=False)
        print('EXPORTED', name, flush=True)
    sys.exit(0)

key = args[1]
d = Path(opt('--dir', 'build/strip-landmarks'))
views_wanted = [a for a in args[2:] if not a.startswith('--') and a not in (opt('--dir', ''),) and a not in (opt('--with', [], True) or [])]
meta = next(v for v in json.loads((d / 'venues.json').read_text()) if v['key'] == key)
bpy.ops.wm.read_factory_settings(use_empty=True)
for name in [key + '-interior'] + (opt('--with', [], True) or []):
    src = d / (name + '.glb')
    if not src.exists(): src = Path('build/strip-landmarks') / (name + '.glb')
    bpy.ops.import_scene.gltf(filepath=str(src.resolve()))
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
try:
    s.eevee.taa_render_samples = 32
    s.eevee.use_shadows = True
except Exception: pass
s.render.resolution_x = int(opt('--w', 1280)); s.render.resolution_y = int(opt('--h', 720))
s.view_settings.view_transform = 'AgX'
s.world = bpy.data.worlds.new('ambient'); s.world.use_nodes = True
bg = s.world.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (.62, .6, .56, 1); bg.inputs[1].default_value = float(opt('--ambient', .55))
for l in meta.get('lights', []):
    ld = bpy.data.lights.new('pool', 'POINT'); ld.energy = l['power'] * 4; ld.shadow_soft_size = .8
    c = l.get('color', 0xffe8cf); ld.color = (((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255)
    ob = bpy.data.objects.new('pool', ld); s.collection.objects.link(ob); ob.location = pt(l['p'])
cam = bpy.data.objects.new('camera', bpy.data.cameras.new('camera')); s.collection.objects.link(cam); s.camera = cam; cam.data.clip_end = 3000
views = {k: v for k, v in meta['views'].items() if (k in views_wanted if views_wanted else k.startswith('vi-'))}
for name, v in views.items():
    cam.location = pt(v['eye']); cam.rotation_euler = (pt(v['target']) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = v.get('lens', 18)
    s.render.filepath = str((REVIEW / f'{key}-{name}.png').resolve())
    bpy.ops.render.render(write_still=True)
    print('RENDERED', s.render.filepath, flush=True)
