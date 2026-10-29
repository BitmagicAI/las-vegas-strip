import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'hw-ivory': 'e0ded5', 'hw-panel': 'bdbdc0', 'hw-coping': 'd9d8d1', 'hw-brown': '524c49', 'hw-base': '96938b', 'hw-joint': '8f8e86', 'hw-trim': '464b4b', 'hw-glass': '6a8985', 'hw-curtain': '9caaa0', 'hw-stone': 'aaa18b', 'hw-soffit': 'dad9d2', 'hw-lamp': 'fff1d6', 'hw-clear': 'a4b9b7', 'hw-paving': 'b9b4a8', 'hw-sign': '315b59', 'hw-equipment': '999d98', 'hw-vent': '454b4a', 'hw-wall': 'dddcd6', 'hw-floor': '99988e', 'hw-darkwood': '665044', 'hw-lightwood': 'bda992', 'hw-counter': 'ecebe3', 'hw-teal': '325e67', 'hw-membrane': 'c7c7be'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('homewood-city-center-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['hw-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='hw-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='hw-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='hw-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('homewood-city-center-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('homewood-city-center-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
