"""Original metre-scaled warehouse finishes; no third-party imagery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'dn-stone':'c6c5bb','dn-joint':'aaa99f','dn-cap-concrete':'b6ad9b','dn-concrete':'bdb7aa','dn-roof':'b0ada2','dn-metal-paint':'b9b7a5','dn-rib-paint':'d2cebb','dn-trim-paint':'b5b19d','dn-frame-paint':'bcbdb3','dn-glass':'243335','dn-metal':'646763','dn-vent':'414642','dn-sign':'e5debc','dn-yellow':'cec46b','dn-letter':'30362b','dn-red':'a4453a','dn-dark-sign':'262a2a','dn-white':'e8e6db'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('dean-martin-north-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='dn-metal':bs.inputs['Metallic'].default_value=.45
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'dean-martin-north-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'dean-martin-north-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED dean-martin-north-exterior')
