import bpy,sys,numpy as np,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'cg-stucco': '8b8980', 'cg-membrane': 'c9c7b9', 'cg-glass': '1c3339', 'cg-alloy': 'b0b1a7', 'cg-threshold': '8e8b7e', 'cg-charcoal': '292b2b', 'cg-soffit': '50504a', 'cg-coping': '72736a', 'cg-red': 'b72629', 'cg-sign': 'e1dfcd', 'cg-gold': 'c9a856', 'cg-yellow': 'd9bb38', 'cg-blue': '376d9b', 'cg-teal': '459d91', 'cg-pink': 'ab5175', 'cg-lamp': 'eadfc3', 'cg-curb': '999b92', 'cg-equipment': 'b1b5ab', 'cg-service': '686f69', 'cg-paving': '98988e'})
for part in ['exterior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('chrome-gypsy-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
  if key in ['cg-metal']:bs.inputs['Metallic'].default_value=.35;bs.inputs['Roughness'].default_value=.42
  if key=='cg-glass':bs.inputs['Alpha'].default_value=1;bs.inputs['Roughness'].default_value=.3;m.surface_render_method='BLENDED'
  if key=='cg-clear':bs.inputs['Alpha'].default_value=.17;bs.inputs['Roughness'].default_value=.22;m.surface_render_method='BLENDED'
  if key=='cg-lamp':bs.inputs['Emission Color'].default_value=(.9,.95,1,1);bs.inputs['Emission Strength'].default_value=.15
 for obj in bpy.context.scene.objects:
  if obj.type!='MESH':continue
  obj.data.validate();uv=obj.data.uv_layers.new(name='Metre finishes')
  for poly in obj.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]))
   for li in poly.loop_indices:
    p=obj.data.vertices[obj.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y/2,p.z/2) if axis==0 else (p.x/2,p.z/2) if axis==1 else (p.x/2,p.y/2)
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('chrome-gypsy-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('chrome-gypsy-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
h=hashlib.sha256()
for f in sorted(E.OUT.glob('*.glb')):h.update(f.read_bytes())
for f in sorted(E.OUT.glob('*-collision.json')):h.update(f.read_bytes())
h.update((E.OUT/'venues.json').read_bytes());(E.OUT/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
