import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ds-cream': 'b9b5a1', 'ds-membrane': 'babbb0', 'ds-metal': '454e4c', 'ds-seam': '596461', 'ds-silver': '9ba5a0', 'ds-service': '666b64', 'ds-stone': '6f6a5e', 'ds-stone0': '8a8170', 'ds-stone1': '625f53', 'ds-stone2': '9b907b', 'ds-glass': '627d7d', 'ds-alloy': 'adb6af', 'ds-red': '9e292c', 'ds-letter': 'f1dfb2', 'ds-paving': 'a29e8d', 'ds-rail': '3d4240', 'ds-equipment': '8d948a'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('dennys-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['ds-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='ds-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('dennys-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('dennys-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
