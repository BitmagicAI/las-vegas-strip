"""Export original additions only; does not install or bake shared city data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'ess-deck':'d9cdb8','ess-tile':'80bcc2','ess-coping':'e5d9bf','ess_pool':'65bdc5','ess-wall':'c4ac87','ess-band':'6d6455','ess-metal':'9a9e9d','ess-frame':'514336','ess-mesh':'65574a','ess-towel':'f1ede3','ess-parasol':'ded0ae','ess-blue':'3475aa'})
for key in ['embassySpaRefinement']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
