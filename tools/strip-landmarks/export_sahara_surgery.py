import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ssc-stucco': 'bfc1bb', 'ssc-block': 'a9ada8', 'ssc-membrane': 'd9dacf', 'ssc-clear': '90a5a9', 'ssc-glass': '34444a', 'ssc-alloy': '9eaaa9', 'ssc-joint': '90968e', 'ssc-coping': 'd4d7cc', 'ssc-white': 'd7dace', 'ssc-soffit': 'c3c9bd', 'ssc-letter': '4d5750', 'ssc-lamp': 'f2f4e7', 'ssc-paving': 'a9ac9f', 'ssc-curb': 'a2a89c', 'ssc-equipment': 'b9bdb0', 'ssc-dark': '252d2b', 'ssc-service': '8b9488', 'ssc-gravel': 'a87f69', 'ssc-leaf': '526f43', 'ssc-trunk': '73624c', 'ssc-carpet': '83877a', 'ssc-cream': 'c8cbbc', 'ssc-ceiling': 'd8dace', 'ssc-floorjoint': '73796e', 'ssc-seatgray': '6a777b', 'ssc-seatpurple': '6a506e', 'ssc-seatbeige': 'afa79b', 'ssc-table': 'a69d88', 'ssc-pot': 'b6aa94', 'ssc-cabinet': 'b5a68a', 'ssc-red': 'c54d4e'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('sahara-surgery-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['ssc-metal']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='ssc-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='ssc-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='ssc-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('sahara-surgery-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('sahara-surgery-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
