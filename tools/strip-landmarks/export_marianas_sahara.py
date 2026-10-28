import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ms-stucco': 'c9c3ae', 'ms-cream': 'e0dcc7', 'ms-roof': '90918a', 'ms-brown': '716252', 'ms-frame': '282c2a', 'ms-glass': '344b4d', 'ms-joint': '99927e', 'ms-metal': '4d5556', 'ms-lamp': 'ded8b3', 'ms-green': '226b44', 'ms-red': 'a83d37', 'ms-yellow': 'c9a136', 'ms-paving': 'aaa99b', 'ms-tile-0': '64554c', 'ms-tile-1': '786556', 'ms-tile-2': '574e48'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('marianas-sahara-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='ms-glass':bs.inputs['Roughness'].default_value=.32
 if key in ['wh-metal','wh-blue','wh-seam']:bs.inputs['Roughness'].default_value=.48
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'marianas-sahara-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'marianas-sahara-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED marianas-sahara')
