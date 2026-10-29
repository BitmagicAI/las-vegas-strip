"""Original metre-scaled warehouse finishes; no third-party imagery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'sc-masonry':'b3a18a','sc-joint':'9f907b','sc-cap-concrete':'b6ad9b','sc-concrete':'bdb7aa','sc-roof-paint':'ada99d','sc-roof-tile':'ad7965','sc-trim-paint':'b5a38e','sc-post-paint':'b2ac9d','sc-window-frame-paint':'c0bbae','sc-glass':'283c3f','sc-metal':'646763','sc-vent':'414642','sc-sign-paint':'e0d6bd','sc-letter':'353735'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('shooting-center-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='sc-metal':bs.inputs['Metallic'].default_value=.45
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'shooting-center-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'shooting-center-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED shooting-center-exterior')
