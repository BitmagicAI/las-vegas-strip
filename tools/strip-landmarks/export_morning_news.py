import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'mn-stucco': 'd8ceb3', 'mn-membrane': 'b7b8ae', 'mn-dark': '454b4c', 'mn-stone': 'a6967d', 'mn-stone0': 'b5a58b', 'mn-stone1': 'a39780', 'mn-stone2': 'b9af98', 'mn-stone3': '9d917b', 'mn-frame': '282b28', 'mn-glass': '283f40', 'mn-clear': 'b2c7c4', 'mn-canvas': 'ebc336', 'mn-yellow': 'cfa52e', 'mn-blue': '264e6e', 'mn-letter': 'f5efdd', 'mn-paving': 'b7afa0', 'mn-equipment': '878b85', 'mn-wall': 'e1d8c3', 'mn-flute': 'd5cbb5', 'mn-wood': '8f7152', 'mn-wood0': '977b5c', 'mn-wood1': 'a68a68', 'mn-wood2': '876d50', 'mn-wood3': '9c8060', 'mn-ceiling': 'dfded2', 'mn-grid': 'b2b4ad', 'mn-brown': '654a34', 'mn-woven': '85877a', 'mn-table': 'd9d7cb', 'mn-counter': 'b4a28a', 'mn-art': 'ddd3b5', 'mn-lamp': 'fff0d4'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('morning-news-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['mn-alloy']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='mn-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='mn-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='mn-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('morning-news-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('morning-news-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
