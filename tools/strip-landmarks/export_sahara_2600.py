import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'s26-stucco': 'd2d2c8', 's26-membrane': 'a9aaa3', 's26-clear': '8ba4ab', 's26-glass': '345059', 's26-mullion': '586367', 's26-reveal': 'e0e0d4', 's26-white': 'e2e2d8', 's26-cap': '747d7b', 's26-seam': '939c98', 's26-mint': '7fbbb7', 's26-green': 'b7c6a4', 's26-letter': '858e8c', 's26-dark': '252a29', 's26-lamp': 'ffefd0', 's26-paving': 'aaa99d', 's26-curb': 'b1b3a7', 's26-equipment': 'a9ada3', 's26-alloy': '9ba8a7', 's26-service': '686f6b', 's26-concrete': '9e9f93', 's26-cream': 'ddd9c9', 's26-joint': '74786f', 's26-beam': '343b36', 's26-duct': '373d3a', 's26-wood': '91694c', 's26-seat': '30352f', 's26-chair': 'baa37e', 's26-leaf': '557346', 's26-slat': '535749', 's26-screen': '5c8893', 's26-stem':'65764c', 's26-woodjoint':'70513c'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('sahara-2600-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['s26-metal']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='s26-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='s26-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='s26-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('sahara-2600-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('sahara-2600-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
