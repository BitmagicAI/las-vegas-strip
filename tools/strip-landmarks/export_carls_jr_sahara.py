import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'cj-stucco': 'bcb49a', 'cj-roof': 'c5c4b8', 'cj-paving': 'b0aa9d', 'cj-trim': 'dbd4bd', 'cj-frame': '5b5550', 'cj-glass': '2f4145', 'cj-sill': 'd9d3c1', 'cj-red': '9f4545', 'cj-red-dark': '773438', 'cj-letter': 'e7dfc8', 'cj-dark': '4e4840', 'cj-tile': 'b86f51', 'cj-tile-0': 'ba7357', 'cj-tile-1': 'ad6048', 'cj-tile-2': 'bd7e61', 'cj-metal': '7e8078', 'cj-gravel': 'b5a38a', 'cj-leaf': '6d7049', 'cj-handle': 'adb2b0'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('carls-jr-sahara-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 if key=='cj-glass':bs.inputs['Roughness'].default_value=.24
 if key in ['cj-metal','cj-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'carls-jr-sahara-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'carls-jr-sahara-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED carls-jr-sahara-exterior')
