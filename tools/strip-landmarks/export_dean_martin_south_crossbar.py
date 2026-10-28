"""Original metre-scaled warehouse finishes; no third-party imagery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'dc-stone':'a69d84','dc-joint':'928b77','dc-cap-concrete':'b6ad9b','dc-concrete':'bdb7aa','dc-roof':'b0ada2','dc-metal-paint':'afa68f','dc-rib-paint':'d2cebb','dc-trim-paint':'b5b19d','dc-frame-paint':'bcbdb3','dc-glass':'243335','dc-metal':'646763','dc-vent':'414642','dc-sign':'e5debc','dc-yellow':'cec46b','dc-letter':'30362b','dc-red':'a4453a','dc-dark-sign':'262a2a','dc-white':'e8e6db'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('dean-martin-south-crossbar-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='dc-metal':bs.inputs['Metallic'].default_value=.45
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'dean-martin-south-crossbar-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'dean-martin-south-crossbar-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED dean-martin-south-crossbar-exterior')
