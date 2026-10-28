"""Original metre-scaled warehouse finishes; no third-party imagery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'de-panel-paint':'aaa18c','de-panel-rib-paint':'b8ad96','de-stone':'a69d84','de-joint':'928b77','de-cap-concrete':'b6ad9b','de-concrete':'bdb7aa','de-roof':'b0ada2','de-metal-paint':'b9b7a5','de-rib-paint':'d2cebb','de-trim-paint':'b5b19d','de-frame-paint':'bcbdb3','de-glass':'243335','de-metal':'646763','de-vent':'414642','de-sign':'e5debc','de-yellow':'cec46b','de-letter':'30362b','de-red':'a4453a','de-dark-sign':'262a2a','de-white':'e8e6db'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('dean-martin-east-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='de-metal':bs.inputs['Metallic'].default_value=.45
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'dean-martin-east-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'dean-martin-east-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED dean-martin-east-exterior')
