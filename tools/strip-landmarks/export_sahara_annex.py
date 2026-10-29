import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'sa-stucco': 'c7c1b2', 'sa-membrane': 'c8c8c0', 'sa-coping': '92988d', 'sa-stone0': '969b8e', 'sa-stone1': 'a6a996', 'sa-stone2': '858d80', 'sa-stone3': 'a19f8a', 'sa-stone4': '8e9691', 'sa-glass': '273c40', 'sa-mullion': 'adb6b3', 'sa-alloy': '919995', 'sa-threshold': 'ada99c', 'sa-blue': '355c9c', 'sa-red': 'a13837', 'sa-signwhite': 'e2dfcf', 'sa-plywood': 'ae8751', 'sa-woodgrain': '997445', 'sa-purple': '8b6a9d', 'sa-roofjoint': '9c9e93', 'sa-service': 'a3a69e', 'sa-vent': '4f5551', 'sa-plinth': '9f9f91'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('sahara-annex-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['sa-alloy','sa-mullion']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='sa-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
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
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('sahara-annex-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('sahara-annex-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
