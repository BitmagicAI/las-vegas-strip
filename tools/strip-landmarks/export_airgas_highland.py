import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ag-cream': 'd8d8cc', 'ag-membrane': 'cecec2', 'ag-blue': '235368', 'ag-clear': '7c989c', 'ag-alloy': 'aab1ad', 'ag-sign': 'd9dccc', 'ag-groove': 'a5a8a0', 'ag-yellow': 'bba14c', 'ag-foot': '7b7b70', 'ag-dark': '333d40', 'ag-lamp': 'ebeee3', 'ag-paving': 'a6a69c', 'ag-coping': 'b4b8b0', 'ag-equipment': '999f98', 'ag-tile': '686e69', 'ag-wall': '8a9390', 'ag-ceiling': 'd6d8ce', 'ag-grid': '969d98', 'ag-grout': '777c75', 'ag-slat': 'a1aba8', 'ag-shelf': 'd4d7c9', 'ag-glove': 'c3c7bb', 'ag-paper': 'e0dfcf', 'ag-label': 'b8b9aa', 'ag-counter': 'aab0a4'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('airgas-highland-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['ag-metal']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='ag-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='ag-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='ag-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('airgas-highland-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('airgas-highland-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
