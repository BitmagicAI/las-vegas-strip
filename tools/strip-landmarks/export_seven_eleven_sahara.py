import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ss-masonry': '99775f', 'ss-mortar': 'b3a291', 'ss-membrane': 'bebdb4', 'ss-coping': '595c5a', 'ss-dark': '303436', 'ss-black': '171c1c', 'ss-glass': '233639', 'ss-alloy': '8b9090', 'ss-base-tile': '8e4835', 'ss-white': 'ece9dc', 'ss-orange': 'cf7b37', 'ss-green': '23694f', 'ss-red': 'bc3433', 'ss-concrete': 'b3b0a7', 'ss-soffit': 'c8c7be', 'ss-screen': '4b727c', 'ss-yellow': 'b99b47', 'ss-light': 'fff2d9', 'ss-floor': 'c5c1b3', 'ss-cream': 'c2bdac', 'ss-ceiling': 'd8d6ca', 'ss-grout': '6b6a61', 'ss-grid': 'aaa99f', 'ss-pack-red': 'a84e41', 'ss-pack-blue': '416578', 'ss-pack-green': '637955', 'ss-pack-gold': 'bf9c52', 'ss-clear': 'b7c9c8', 'ss-cabinet': 'b9b2a0', 'ss-counter': '92948d'})
E.colors.update({'ss-board0':'78786c','ss-board1':'828277','ss-board2':'706f66'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('seven-eleven-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key=='ss-alloy':bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.4
  if key in ['ss-clear','ss-glass']:
   bs.inputs['Alpha'].default_value=.12;bs.inputs['Roughness'].default_value=.12;m.diffuse_color=(*m.diffuse_color[:3],.12);m.surface_render_method='DITHERED'
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('seven-eleven-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('seven-eleven-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
