"""Original material palette; export separately streamed public room."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'kf-stucco':'d5c4a1','kf-terra':'a65e46','kf-cream':'e2d3ae','kf-frame':'383632','kf-glass':'35494c','kf-stone':'b6ad99','kf-roof':'a49e92','kf-tile':'25596b','kf-tile-rib':'397181','kf-gold':'d9bf65','kf-burgundy':'64352f','kf-brick':'914f3f','kf-soil':'4c4134','kf-leaf':'526337','kf-metal':'898b82','kf-carpet':'76624b','kf-wood':'60362c','kf-vinyl':'743634','kf-table':'d4c8ae','kf-ceiling':'7b4b42','kf-bottle':'465e38','kf-lamp':'f1dfb8'})
for part in ['exterior','interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('kung-fu-plaza-'+part)
 for key,m in E.materials.items():
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
  if key in ['kf-glass','kf-tile','kf-bottle']:bs.inputs['Roughness'].default_value=.3
  if key=='kf-vinyl':bs.inputs['Roughness'].default_value=.47
  if key=='kf-lamp':bs.inputs['Emission Color'].default_value=(1,.8,.5,1);bs.inputs['Emission Strength'].default_value=.7
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.new(name='Metre finish')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
 bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/('kung-fu-plaza-'+part+'.blend')).resolve()))
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/('kung-fu-plaza-'+part+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 print('EXPORTED kung-fu-plaza-'+part)
