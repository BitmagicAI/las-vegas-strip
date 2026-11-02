"""Export scoped original west-resort geometry; never installs or bakes shared data."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'gca-column':'e5dfcf','gca-wood':'654631','gca-frame':'484b49','gca-strap':'e8e7dd'})
E.colors.update({'wpa-deck':'c4bda8','wpa-tile':'83b3b8','wpa-coping':'b1a18f','wpa_pool':'62b4cd','wpa-frame':'b8bdbb','wpa-mesh':'dadbd7','wpa-blue':'24599a'})
key=next(a.split('=',1)[1] for a in sys.argv if a.startswith('--only='))
assert key in ['goldCoastExterior','wyndhamDesertBlue']
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
