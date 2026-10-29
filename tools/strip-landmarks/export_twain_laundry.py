"""Original material palette; export separately streamed public room."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'tl-stucco':'b4b0a2','tl-roof':'c4c4b8','tl-concrete':'b0afa6','tl-blue-fascia':'52647b','tl-cream':'dbd6bf','tl-frame':'303337','tl-glass':'3c5054','tl-brick':'7f7771','tl-red':'ab4e4c','tl-gold':'d4b55c','tl-metal':'a4a8a7','tl-lamp':'eeebce','tl-grout':'62584b','tl-tile-0':'ac916b','tl-tile-1':'a88d66','tl-tile-2':'b39771','tl-wall-blue':'5d8cbe','tl-ceiling':'bbbcb7','tl-grid':'999b95','tl-chrome':'bfc6c8','tl-drum':'252e36','tl-display':'7899a2','tl-button':'d3d4c8','tl-table-blue':'3569a4'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('twain-laundry-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['tl-glass','tl-drum']:bs.inputs['Roughness'].default_value=.3
  if key in ['tl-metal','tl-chrome']:bs.inputs['Metallic'].default_value=.6;bs.inputs['Roughness'].default_value=.35
  if key=='tl-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.7
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('twain-laundry-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('twain-laundry-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED twain-laundry-'+part)
