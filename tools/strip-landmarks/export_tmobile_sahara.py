import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'ms-stucco': 'd8d6cd', 'ms-roof': 'bebeb4', 'ms-paving': 'aba59a', 'ms-trim': 'a59d87', 'ms-tan': 'b3aa8b', 'ms-frame': '737978', 'ms-panel': 'e3e1d9', 'ms-sill': 'a49e91', 'ms-magenta': 'ad2f66', 'ms-letter': 'ece9df', 'ms-dark': '454848', 'ms-tile': 'ad7860', 'ms-tile-0': 'ae7b64', 'ms-tile-1': 'b5846d', 'ms-tile-2': '99694f', 'ms-metal': '777e7a', 'ms-gravel': 'a89c84', 'ms-leaf': '626d43', 'ms-trunk': '7b6953'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('tmobile-sahara-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 if key=='ms-panel':bs.inputs['Roughness'].default_value=.24
 if key in ['ms-metal','ms-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'tmobile-sahara-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'tmobile-sahara-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED tmobile-sahara-exterior')
