"""Export only the original amenity additions. Never regenerates existing resort shells."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'ra-paving':'d2c5ac','ra-tile':'69a6ad','ra_pool':'49969d','ra-coping':'e2d7c1','ra-white':'eee8dc','ra-yellow':'e4c253','ra-red':'b44640','ra-teal':'348b91','ra-wood':'806347','ra-screen':'252d32','ra-blue':'36689b','ra-soil':'8c785d','ra-green':'4e7541','ra-bark':'7f694c','pa-paving':'cfc3ad','pa_pool':'4c9da6','pa-white':'e9e5d8','pa-tile':'58a0a4','pa-navy':'273b58','pa-wood':'846b4c'})
for key in ['rioAmenities','palmsAmenities']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
