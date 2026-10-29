import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'hg-ivory': 'deded4', 'hg-gray': '8d9294', 'hg-coping': 'e3e3dc', 'hg-membrane': 'c5c7c2', 'hg-frame': '414a48', 'hg-glass': '668e80', 'hg-sill': '6c7470', 'hg-joint': '777d79', 'hg-dark': '363d3a', 'hg-brick': '99978b', 'hg-mortar': 'b5b1a5', 'hg-stone': 'b9b7a8', 'hg-clear': '9db7ad', 'hg-paving': 'b9b5a9', 'hg-sign': '992d3b', 'hg-equipment': '999e96', 'hg-wall': 'dedcd3', 'hg-floor': 'a7a59a', 'hg-ceiling': 'eeece2', 'hg-wood': '66513d', 'hg-counter': 'ece9dc', 'hg-relief': 'dddcd4', 'hg-art': 'a6b7a8', 'hg-teal': '527e7c', 'hg-seat': '8b8f8a', 'hg-orange': 'bc6d3d', 'hg-lamp': 'fff1d6'})
E.colors['hg-floor-joint']='8b8b81'
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('hilton-garden-city-center-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['hg-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='hg-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='hg-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='hg-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  if part=='interior' and any(m and m.name.endswith(('hg-seat','hg-orange','hg-counter')) for m in obj.data.materials):
   bpy.context.view_layer.objects.active=obj
   mod=obj.modifiers.new('Soft manufactured edges','BEVEL');mod.width=.035;mod.segments=3
   bpy.ops.object.modifier_apply(modifier=mod.name)
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('hilton-garden-city-center-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('hilton-garden-city-center-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
