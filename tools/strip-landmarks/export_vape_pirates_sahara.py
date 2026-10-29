import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'vp-stucco': '63696d', 'vp-membrane': 'bcbfbd', 'vp-parapet': '59636d', 'vp-rib': '434c54', 'vp-coping': '9ea7aa', 'vp-dark': '25282b', 'vp-clear': '8da6a9', 'vp-alloy': '9ea9ab', 'vp-bars': '616b70', 'vp-paving': '868988', 'vp-concrete': 'adafac', 'vp-lamp': 'eff3ea', 'vp-white': 'dadfdd', 'vp-service': '858e90', 'vp-wall': 'c7cbc9', 'vp-tile': 'a4a6a0', 'vp-grout': '676e6b', 'vp-ceiling': 'd8dcd9', 'vp-rack': '383c40', 'vp-packred': 'a64c4e', 'vp-packblue': '467ba1', 'vp-packgreen': '6b9067', 'vp-packgold': 'ba9e56', 'vp-screen': '456674'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('vape-pirates-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['vp-alloy','vp-bars']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='vp-clear':bs.inputs['Alpha'].default_value=.08;bs.inputs['Roughness'].default_value=.12;m.diffuse_color=(*m.diffuse_color[:3],.08);m.surface_render_method='BLENDED'
 for obj in bpy.context.scene.objects:
  if obj.type=='FONT':
   obj.data.resolution_u=3;obj.data.bevel_depth=0
   font=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
   if font.exists():obj.data.font=bpy.data.fonts.load(str(font),check_existing=True)
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('vape-pirates-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('vape-pirates-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
