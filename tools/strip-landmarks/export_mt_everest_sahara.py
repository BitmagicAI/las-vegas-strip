"""Original material palette; export separately streamed public room."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
from mt_everest_materials import finishes
E.colors.update({'me-brick': '873e35', 'me-brick-0': '91443b', 'me-brick-1': '84392f', 'me-brick-2': '98483b', 'me-red': '79332f', 'me-cream': 'dbd1b8', 'me-frame': '282626', 'me-glass': '34444b', 'me-blue': '496e91', 'me-snow': 'c9d1cf', 'me-concrete': '8f8b81', 'me-tile-0': '8d5c49', 'me-tile-1': 'a16a52', 'me-tile-2': '775043', 'me-roof': '8a887e', 'me-floor': 'aaa496', 'me-metal': '9d9d95', 'me-carpet': '443a33', 'me-ceiling': 'b8af96', 'me-orange': 'a54b2e', 'me-wood': '74462b', 'me-grid': '8c8678', 'me-blind': '272523', 'me-table': '3b2821', 'me-vinyl': '6d252a', 'me-glassware': 'acb5b3', 'me-food-0': '733925', 'me-food-1': 'b5933c', 'me-food-2': '56613c', 'me-lamp': 'ead2a0'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('mt-everest-sahara-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['me-glass','me-tile','me-bottle']:bs.inputs['Roughness'].default_value=.3
  if key=='me-metal':bs.inputs['Metallic'].default_value=.75;bs.inputs['Roughness'].default_value=.28
  if key=='me-vinyl':bs.inputs['Roughness'].default_value=.47
  if key=='me-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.7
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 finishes()
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('mt-everest-sahara-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('mt-everest-sahara-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED mt-everest-sahara-'+part)
