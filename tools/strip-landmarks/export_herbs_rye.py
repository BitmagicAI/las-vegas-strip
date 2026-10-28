"""Original material palette; export separately streamed public room."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
from herbs_rye_materials import finishes
E.colors.update({'hr-stucco': '8c4e48', 'hr-trim': '8b7960', 'hr-roof': '777773', 'hr-foundation': '8c8374', 'hr-paving': '724c41', 'hr-joint': '51413a', 'hr-awning': '252629', 'hr-metal': '494444', 'hr-sign': '8d3334', 'hr-board': 'dfdcd0', 'hr-floor': '413023', 'hr-ceiling': '272422', 'hr-wallpaper': '722d33', 'hr-wood': '4b2c1c', 'hr-darkwood': '281b15', 'hr-plate': 'd7d0bb', 'hr-napkin': '292823', 'hr-glass': '777b70', 'hr-brass': '8c6c36', 'hr-bottle-0': '344033', 'hr-bottle-1': '563e22', 'hr-bottle-2': '382d28', 'hr-label': 'baaa8d', 'hr-lamp': 'e4bf7c', 'hr-art': '3b3430', 'hr-plank-0': '5a3823', 'hr-plank-1': '62402b', 'hr-plank-2': '50311f', 'hr-plank-3': '66452e'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('herbs-rye-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['hr-glass','hr-bottle-0','hr-bottle-1','hr-bottle-2']:bs.inputs['Roughness'].default_value=.3
  if key in ['hr-metal','hr-brass']:bs.inputs['Metallic'].default_value=.75;bs.inputs['Roughness'].default_value=.28
  if key=='hr-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.7
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 finishes()
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('herbs-rye-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('herbs-rye-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED herbs-rye-'+part)
