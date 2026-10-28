import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'df-plaster':'ded9c8','df-white':'eeebe3','df-roof':'8a8982','df-base':'a19b8e','df-tan':'aa9980','df-cap':'b9b3a3','df-red':'a7342d','df-slat':'c46959','df-glass':'303c3c','df-frame':'48463c','df-blind':'999d86','df-letter':'f3d799','df-paving':'a99f8c','df-metal':'6f716b','df-stone-0':'9b9586','df-stone-1':'b0a78e','df-stone-2':'d0c4a6','df-stone-3':'817f72'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('dennys-flamingo-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 if key=='df-glass':bs.inputs['Roughness'].default_value=.24
 if key in ['df-metal','df-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'dennys-flamingo-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'dennys-flamingo-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED dennys-flamingo-exterior')
