import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'bb-mortar':'b8b8b0','bb-mirror':'a3b5b7','bb-stucco': 'bbbcb4', 'bb-membrane': 'c9cbc4', 'bb-blue': '234b71', 'bb-charcoal': '393c40', 'bb-letter': 'e0e1d8', 'bb-dark': '202224', 'bb-door': '25292d', 'bb-alloy': '737e82', 'bb-clear': '98adb7', 'bb-glass': '354850', 'bb-concrete': 'a6a79e', 'bb-rope': 'a6a292', 'bb-coping': 'd9dad0', 'bb-equipment': 'afb4ac', 'bb-rubber': '272927', 'bb-cream': 'd5d4c9', 'bb-ceiling': '252724', 'bb-steel': '303431', 'bb-lamp': 'f5edcf', 'bb-apron': '242927', 'bb-mat': '993d39', 'bb-red': 'b8292e', 'bb-wood': '71624b', 'bb-gold': 'bb9d42', 'bb-bag': '33292b'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('barrys-boxing-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['bb-alloy','bb-gold']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='bb-mirror':bs.inputs['Metallic'].default_value=.9;bs.inputs['Roughness'].default_value=.18
  if key=='bb-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='bb-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='bb-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('barrys-boxing-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('barrys-boxing-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
