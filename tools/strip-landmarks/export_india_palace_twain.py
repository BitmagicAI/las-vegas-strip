import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ip-ochre': '987655', 'ip-roof': 'c2bdae', 'ip-paving': 'bcb3a1', 'ip-red': '8e4c42', 'ip-stone-base': '635e4f', 'ip-glass': '283b3e', 'ip-frame': '7d817c', 'ip-steel': 'a0a39b', 'ip-cream': 'ded5b8', 'ip-dark': '272c28', 'ip-cap': '70483d', 'ip-joint': '6f4239', 'ip-lamp': 'e8c992', 'ip-stone-0': '6c6a55', 'ip-stone-1': '87785c', 'ip-stone-2': '5d5f50', 'ip-stone-3': '75634c', 'ip-stone-4': '94856e'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('india-palace-twain-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 if key=='ip-glass':bs.inputs['Roughness'].default_value=.24
 if key in ['ip-steel','ip-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'india-palace-twain-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'india-palace-twain-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED india-palace-twain-exterior')
