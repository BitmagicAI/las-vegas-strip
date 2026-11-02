"""Export scoped original Allegiant geometry; never installs or bakes shared data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'anc-roof':'a6afb3','anc-soffit':'737d82','anc-edge':'8b959b','anc-frame':'3a4145'})
key=next(a.split('=',1)[1] for a in sys.argv if a.startswith('--only='))
assert key == 'allegiantStadium'
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
