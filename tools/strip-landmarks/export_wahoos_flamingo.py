import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
E.colors.update({'wh-stucco':'89968d','wh-roof':'9e9d94','wh-cream':'dbd8bf','wh-stone-0':'8c8980','wh-stone-1':'afaca0','wh-stone-2':'777c79','wh-stone-3':'b2b2a8','wh-frame':'262d31','wh-glass':'34474b','wh-menu':'ccb459','wh-blue':'284f80','wh-seam':'3a6392','wh-red':'b54f4d','wh-metal':'a5aba7','wh-lens':'dedab4','wh-paving':'aaa79a','wh-joint':'77766d'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('wahoos-flamingo-exterior')
for key,m in E.materials.items():
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85
 if key=='wh-glass':bs.inputs['Roughness'].default_value=.32
 if key in ['wh-metal','wh-blue','wh-seam']:bs.inputs['Roughness'].default_value=.48
bpy.ops.wm.save_as_mainfile(filepath=str((E.OUT/'wahoos-flamingo-exterior.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'wahoos-flamingo-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
print('EXPORTED wahoos-flamingo')
