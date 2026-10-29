import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'mb-mirror':'a3b5b7','mb-stucco': 'bbbcb4', 'mb-membrane': 'c9cbc4', 'mb-blue': '76aebc', 'mb-charcoal': '393c40', 'mb-letter': 'e0e1d8', 'mb-dark': '202224', 'mb-door': '25292d', 'mb-alloy': '737e82', 'mb-clear': '98adb7', 'mb-glass': '354850', 'mb-concrete': 'a6a79e', 'mb-rope': 'a6a292', 'mb-coping': 'd9dad0', 'mb-equipment': 'afb4ac', 'mb-rubber': '272927', 'mb-cream': 'b9b5a5', 'mb-ceiling': '252724', 'mb-steel': '303431', 'mb-lamp': 'f5edcf', 'mb-apron': '242927', 'mb-mat': '353b39', 'mb-red': 'b8292e', 'mb-wood': '71624b', 'mb-gold': 'bb9d42', 'mb-bag': '33292b'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('martinez-boxing-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['mb-alloy','mb-gold']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='mb-mirror':bs.inputs['Metallic'].default_value=.9;bs.inputs['Roughness'].default_value=.18
  if key=='mb-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='mb-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='mb-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('martinez-boxing-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('martinez-boxing-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
