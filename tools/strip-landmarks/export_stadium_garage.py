"""Export original garage geometry with metre-scale UVs and rough concrete."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'sg-deck':'92958e','sg-soffit':'9da299','sg-concrete':'bbbcb4','sg-gray':'a4a69e','sg-white':'dedfd8','sg-ochre':'98724b','sg-line':'d9d7bc','sg-green':'485b40','sg-yellow':'c9ad50','sg-red':'b63e3b'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('stadium-garage-exterior')
for m in E.materials.values():m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 uv=o.data.uv_layers.new(name='Metre finish')
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]]*.5,q[axes[1]]*.5)
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'stadium-garage-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'stadium-garage-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED stadium-garage-exterior')
