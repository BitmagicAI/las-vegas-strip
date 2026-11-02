"""Export original additions only; does not install or bake shared city data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'ess-deck':'d9cdb8','ess-tile':'80bcc2','ess-coping':'e5d9bf','ess_pool':'65bdc5','ess-wall':'c4ac87','ess-band':'6d6455','ess-metal':'9a9e9d','ess-frame':'514336','ess-mesh':'65574a','ess-towel':'f1ede3','ess-parasol':'ded0ae','ess-blue':'3475aa'})
E.colors.update({'lvw-terrace-paving':'c4b89e','lvw-terrace-glass':'bdd0d0','lvw-fixture':'34383a'})
for key in ['embassySpaRefinement','lvccWest']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 if key=='lvccWest':
  m=E.materials.get('lvw-terrace-glass')
  if m:
   bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.22;bs.inputs['Roughness'].default_value=.18;m.surface_render_method='DITHERED'
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
