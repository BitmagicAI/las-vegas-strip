"""Export original grouped source additions, without installation or shared bake."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'rcr-terracotta':'b77e60','rcr-frame':'59483c','rcr-sand':'d5c4a1','rcr-rust':'ab6748','rcr-blue':'647b8b','rcr-towel':'e8e3d8','rcr-parasol':'c9552a','rgr-housing':'757774','rgr-diffuser':'dedbc8','rgr-metal':'777b78','ccr-purple':'654275','ccr-metal':'8e9595','ccr-dark':'333738','ccr-panel':'92918b'})
for key in ['royaleCourtyardRefinement','royaleGarageRefinement','carnavalRefinement']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
