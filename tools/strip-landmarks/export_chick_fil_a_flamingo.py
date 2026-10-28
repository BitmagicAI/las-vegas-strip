import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'cf-stucco':'d6d1bd','cf-roof':'8a8982','cf-foundation':'9a9284','cf-cap':'303333','cf-mortar':'787366','cf-brick-0':'9a8f77','cf-brick-1':'a39880','cf-brick-2':'b3a68c','cf-brick-3':'8e8572','cf-brick-4':'aea38d','cf-glass':'374845','cf-frame':'282d2c','cf-sill':'8c8577','cf-metal':'6b706a','cf-letter':'eee8d7','cf-sign':'ad272c','cf-service':'615d50','cf-paving':'a69e8b','cf-planter':'45463f','cf-shrub':'526144'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('chick-fil-a-flamingo-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.83
 if key=='cf-glass':bs.inputs['Roughness'].default_value=.24
 if key in ['cf-metal','cf-frame']:bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.4
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'chick-fil-a-flamingo-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'chick-fil-a-flamingo-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED chick-fil-a-flamingo-exterior')
