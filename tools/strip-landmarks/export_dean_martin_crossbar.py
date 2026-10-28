"""Original metre-scaled warehouse finishes; no third-party imagery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'dx-stone':'a69d84','dx-joint':'928b77','dx-cap-concrete':'b6ad9b','dx-concrete':'bdb7aa','dx-roof':'b0ada2','dx-metal-paint':'b9b7a5','dx-rib-paint':'d2cebb','dx-trim-paint':'b5b19d','dx-frame-paint':'bcbdb3','dx-glass':'243335','dx-metal':'646763','dx-vent':'414642','dx-sign':'e5debc','dx-yellow':'cec46b','dx-letter':'30362b','dx-red':'a4453a','dx-dark-sign':'262a2a','dx-white':'e8e6db'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('dean-martin-crossbar-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='dx-metal':bs.inputs['Metallic'].default_value=.45
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'dean-martin-crossbar-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'dean-martin-crossbar-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED dean-martin-crossbar-exterior')
