"""Original material palette; export separately streamed public room."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors['fm-case-glass']='9eb8bd'
E.colors.update({'fm-stucco': 'c4b99b', 'fm-roof': 'c8c8bf', 'fm-concrete': 'adada3', 'fm-blue': '3d526d', 'fm-cream': 'dcd7bf', 'fm-frame': '292c2d', 'fm-glass': '34464a', 'fm-red': 'a53737', 'fm-green': '316c42', 'fm-paper': 'e0decb', 'fm-metal': '9a9f9f', 'fm-lamp': 'eee9d9', 'fm-floor-dark': '323537', 'fm-floor-light': 'c3c5be', 'fm-wall': 'c7c5b6', 'fm-ceiling': 'bfbfb4', 'fm-grid': 'a5a69d', 'fm-display': '4b686f', 'fm-pack-0': 'af4941', 'fm-pack-1': 'ceb640', 'fm-pack-2': '477150', 'fm-pack-3': '465b89', 'fm-pack-4': 'c9914c', 'fm-pack-5': 'bcaf8e'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('favorita-market-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['fm-glass','fm-drum']:bs.inputs['Roughness'].default_value=.3
  if key in ['fm-metal','fm-chrome']:bs.inputs['Metallic'].default_value=.6;bs.inputs['Roughness'].default_value=.35
  if key=='fm-case-glass':
   bs.inputs['Alpha'].default_value=.20;m.diffuse_color=(*m.diffuse_color[:3],.20);m.surface_render_method='DITHERED';bs.inputs['Roughness'].default_value=.18
  if key=='fm-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.7
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('favorita-market-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('favorita-market-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED favorita-market-'+part)
