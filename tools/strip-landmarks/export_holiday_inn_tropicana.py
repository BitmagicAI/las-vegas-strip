import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'hi-gray': '92938b', 'hi-white': 'e9e8e1', 'hi-membrane': 'c4c5be', 'hi-orange': 'a75b3a', 'hi-navy': '3c565e', 'hi-joint': '8b8a80', 'hi-frame': 'aab6b3', 'hi-glass': '698f97', 'hi-vent': '4d585a', 'hi-dark': '3a3d3c', 'hi-wood': '9c7652', 'hi-stone': 'c3b8a0', 'hi-lamp': 'fff1d6', 'hi-clear': 'a4b8bd', 'hi-paving': 'b9b5a9', 'hi-sign': 'e7e8dc', 'hi-equipment': '959a91', 'hi-wall': 'e2dfd5', 'hi-floor': 'c9c3b4', 'hi-ceiling': 'e9e7dd', 'hi-blue': '398dac', 'hi-steel': 'a0a5a4', 'hi-counter': '454c4a', 'hi-leather': '956547', 'hi-copper': 'a57c52', 'hi-seatback': 'b6a887'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('holiday-inn-tropicana-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['hi-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='hi-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='hi-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='hi-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  if part=='interior' and any(m and m.name.endswith(('hi-leather','hi-counter')) for m in obj.data.materials):
   bpy.context.view_layer.objects.active=obj
   mod=obj.modifiers.new('Soft manufactured edges','BEVEL');mod.width=.035;mod.segments=3
   bpy.ops.object.modifier_apply(modifier=mod.name)
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('holiday-inn-tropicana-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('holiday-inn-tropicana-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
