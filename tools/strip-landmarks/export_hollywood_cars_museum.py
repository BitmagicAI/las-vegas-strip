"""Original metre-scaled warehouse finishes; no third-party imagery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'hcm-metal-paint':'ada58d','hcm-rib-paint':'a49d88','hcm-roof-paint':'b7b6a9','hcm-trim-paint':'c1baa4','hcm-stone':'bcb9a9','hcm-sign-paint':'d5d0bb','hcm-letter':'393a34','hcm-frame-paint':'9da2a0','hcm-glass':'263b3d','hcm-metal':'4c5050','hcm-concrete':'aea797','hcm-soil':'655d45','hcm-hedge':'445535','hcm-vent':'515952','steel':'4c5050'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('hollywood-cars-museum-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='hcm-metal':bs.inputs['Metallic'].default_value=.45
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]],q[axes[1]])
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'hollywood-cars-museum-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'hollywood-cars-museum-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED hollywood-cars-museum-exterior')
